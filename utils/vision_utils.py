"""
Computer Vision module for Face Detection, Multi-Student Tracking,
Sustained Presence Attendance Logic, Head Pose Estimation, and Inactivity Detection.
"""

import cv2
import numpy as np
import time
from datetime import datetime
from config import Config

# Load OpenCV Cascades
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
EYE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

class StudentPresenceTracker:
    """Tracks a single student's sustained presence and visual behavior over time."""
    def __init__(self, student_id, name="Student"):
        self.student_id = student_id
        self.name = name
        self.first_seen = None
        self.last_seen = None
        self.total_visible_seconds = 0.0
        self.continuous_presence_seconds = 0.0
        self.last_frame_time = None
        self.last_active_time = time.time()
        self.inactivity_duration = 0.0
        self.prev_crop_gray = None
        self.recent_movements = []
        self.recent_poses = []
        self.status = "Absent"
        self.presence_ratio = 0.0

    def update_presence(self, current_time, session_start_time, bounding_box=None, frame_gray=None):
        """Updates timestamps, sustained presence counters, and movement metrics."""
        now = current_time
        if self.first_seen is None:
            self.first_seen = datetime.fromtimestamp(now).isoformat()

        if self.last_frame_time is not None:
            dt = now - self.last_frame_time
            # If detected within reasonable consecutive frame window (< 2.5s)
            if dt < 2.5:
                self.total_visible_seconds += dt
                self.continuous_presence_seconds += dt
            else:
                self.continuous_presence_seconds = 0.0
        else:
            self.continuous_presence_seconds = 0.5
            self.total_visible_seconds = 0.5

        self.last_frame_time = now
        self.last_seen = datetime.fromtimestamp(now).isoformat()

        # Compute movement if box and frame are provided
        movement_level = 0.0
        if bounding_box is not None and frame_gray is not None:
            x, y, w, h = bounding_box
            crop = frame_gray[max(0, y):min(frame_gray.shape[0], y+h), max(0, x):min(frame_gray.shape[1], x+w)]
            if crop.size > 0:
                crop_resized = cv2.resize(crop, (64, 64))
                if self.prev_crop_gray is not None:
                    diff = cv2.absdiff(crop_resized, self.prev_crop_gray)
                    movement_level = float(np.mean(diff))
                    if movement_level > 3.0:
                        self.last_active_time = now
                        self.inactivity_duration = 0.0
                    else:
                        self.inactivity_duration = now - self.last_active_time
                self.prev_crop_gray = crop_resized

        self.recent_movements.append(movement_level)
        if len(self.recent_movements) > 20:
            self.recent_movements.pop(0)

        # Calculate presence ratio against elapsed session duration
        session_elapsed = max(now - session_start_time, 1.0)
        self.presence_ratio = min(1.0, self.total_visible_seconds / session_elapsed)

        # Sustained Presence Attendance Decision Logic
        # Eliminates false positives from quick walk-bys or transient detections
        if self.total_visible_seconds >= Config.MIN_SUSTAINED_SECONDS:
            arrived_offset = (datetime.fromisoformat(self.first_seen).timestamp() - session_start_time)
            # Arrived after 25% of elapsed session: Tardy
            if arrived_offset > 0.25 * session_elapsed and session_elapsed > 40:
                self.status = "Tardy"
            elif self.presence_ratio >= Config.ATTENDANCE_PRESENCE_RATIO_THRESHOLD:
                self.status = "Present"
            else:
                self.status = "Present (Partial)"
        else:
            self.status = "Pending (Transient)"

    def check_departure(self, current_time, session_start_time):
        """Checks if a previously sustained student has left early."""
        if self.last_frame_time is None:
            return
        time_since_seen = current_time - self.last_frame_time
        if time_since_seen > Config.ABSENCE_GRACE_PERIOD_SECONDS:
            if self.total_visible_seconds >= Config.MIN_SUSTAINED_SECONDS and self.status in ("Present", "Present (Partial)"):
                self.status = "Left Early"


class VisionAnalyticsEngine:
    """Performs real-time face detection, tracking, head pose estimation, and presence logging."""
    def __init__(self):
        self.student_trackers = {}
        self.next_unassigned_id = 101

    def assign_or_get_tracker(self, centroid, roster):
        """Matches centroid to existing tracker or assigns to available registered student."""
        cx, cy = centroid
        closest_id = None
        min_dist = 120.0  # pixel distance threshold for tracking match

        for s_id, tracker in self.student_trackers.items():
            if hasattr(tracker, 'last_centroid'):
                dist = np.hypot(cx - tracker.last_centroid[0], cy - tracker.last_centroid[1])
                if dist < min_dist:
                    min_dist = dist
                    closest_id = s_id

        if closest_id is not None:
            tracker = self.student_trackers[closest_id]
            tracker.last_centroid = (cx, cy)
            return tracker

        # Assign new student from roster if available
        existing_ids = set(self.student_trackers.keys())
        assigned_student = None
        for r in roster:
            if r["student_id"] not in existing_ids:
                assigned_student = r
                break

        if assigned_student:
            s_id = assigned_student["student_id"]
            name = assigned_student["name"]
        else:
            s_id = f"STU-{self.next_unassigned_id}"
            name = f"Participant {self.next_unassigned_id}"
            self.next_unassigned_id += 1

        tracker = StudentPresenceTracker(s_id, name)
        tracker.last_centroid = (cx, cy)
        self.student_trackers[s_id] = tracker
        return tracker

    def estimate_head_pose(self, face_crop, eyes):
        """
        Estimates yaw/pitch attention scores based on face and eye spatial symmetry.
        Returns:
            pose_score (0.0 to 100.0)
            state_label ('Attentive', 'Note-Taking/Screen', 'Distracted')
            yaw_deg, pitch_deg
        """
        fh, fw = face_crop.shape[:2]
        if fw == 0 or fh == 0:
            return 70.0, "Attentive", 0.0, 0.0

        if len(eyes) >= 2:
            # Sort eyes horizontally
            eyes_sorted = sorted(eyes, key=lambda e: e[0])
            e1, e2 = eyes_sorted[0], eyes_sorted[1]
            eye_center_x = (e1[0] + e1[2] / 2 + e2[0] + e2[2] / 2) / 2
            eye_center_y = (e1[1] + e1[3] / 2 + e2[1] + e2[3] / 2) / 2

            # Normalized offset from face center
            dx = (eye_center_x - fw / 2) / (fw / 2)
            dy = (eye_center_y - fh * 0.35) / (fh * 0.35)

            yaw_deg = float(dx * 45.0)
            pitch_deg = float(dy * 35.0)

            # Classification
            if abs(yaw_deg) > 26.0:
                return 35.0, "Distracted (Looking Away)", yaw_deg, pitch_deg
            elif pitch_deg > 18.0:
                return 80.0, "Note-Taking / Screen", yaw_deg, pitch_deg
            elif abs(yaw_deg) < 16.0 and abs(pitch_deg) < 18.0:
                return 95.0, "Attentive (Front Focus)", yaw_deg, pitch_deg
            else:
                return 75.0, "Attentive", yaw_deg, pitch_deg
        elif len(eyes) == 1:
            # Only one eye visible -> turning sideways
            return 45.0, "Partially Distracted", 28.0, 5.0
        else:
            # Eyes obscured or tilted down sharply
            return 60.0, "Focused Down / Obscured", 5.0, 25.0

    def process_frame(self, frame_bgr, session_start_time, roster):
        """
        Processes a single camera/video frame.
        Detects faces, updates sustained presence, calculates attention metrics,
        and returns annotated frame with metrics summary.
        """
        current_time = time.time()
        h, w = frame_bgr.shape[:2]
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)

        # Detect frontal faces
        faces = FACE_CASCADE.detectMultiScale(
            gray,
            scaleFactor=1.15,
            minNeighbors=5,
            minSize=(50, 50)
        )

        detected_students_info = []

        for (x, y, fw, fh) in faces:
            cx = int(x + fw / 2)
            cy = int(y + fh / 2)
            centroid = (cx, cy)

            tracker = self.assign_or_get_tracker(centroid, roster)
            tracker.update_presence(current_time, session_start_time, (x, y, fw, fh), gray)

            # Analyze head pose & eyes inside face region
            face_crop = gray[y:y+fh, x:x+fw]
            eyes = EYE_CASCADE.detectMultiScale(face_crop, scaleFactor=1.1, minNeighbors=3, minSize=(15, 15))
            pose_score, pose_label, yaw, pitch = self.estimate_head_pose(face_crop, eyes)

            # Calculate movement score from tracker history
            avg_movement = np.mean(tracker.recent_movements) if tracker.recent_movements else 5.0
            if tracker.inactivity_duration > Config.INACTIVITY_ALERT_SECONDS:
                movement_score = max(10.0, 40.0 - (tracker.inactivity_duration - Config.INACTIVITY_ALERT_SECONDS))
                activity_label = f"Inactive ({int(tracker.inactivity_duration)}s)"
            elif avg_movement < 2.0:
                movement_score = 65.0
                activity_label = "Low Movement"
            else:
                movement_score = min(100.0, 70.0 + avg_movement * 2.5)
                activity_label = "Active Interaction"

            student_data = {
                "student_id": tracker.student_id,
                "name": tracker.name,
                "box": [int(x), int(y), int(fw), int(fh)],
                "centroid": [cx, cy],
                "status": tracker.status,
                "presence_seconds": round(tracker.total_visible_seconds, 1),
                "continuous_seconds": round(tracker.continuous_presence_seconds, 1),
                "presence_ratio": round(tracker.presence_ratio, 2),
                "pose_score": round(pose_score, 1),
                "pose_label": pose_label,
                "movement_score": round(movement_score, 1),
                "activity_label": activity_label,
                "inactivity_seconds": round(tracker.inactivity_duration, 1),
                "yaw": round(yaw, 1),
                "pitch": round(pitch, 1)
            }
            detected_students_info.append(student_data)

            # Draw UI Overlays on Frame
            # Color code based on sustained presence & attention
            if tracker.status in ("Present", "Present (Partial)"):
                color = (46, 204, 113)  # Green
            elif tracker.status == "Tardy":
                color = (241, 196, 15)  # Yellow
            elif tracker.status == "Pending (Transient)":
                color = (52, 152, 219)  # Blue
            else:
                color = (231, 76, 60)   # Red

            # Modern HUD Bounding box with corner accents
            cv2.rectangle(frame_bgr, (x, y), (x + fw, y + fh), color, 2)
            corner_len = int(min(fw, fh) * 0.2)
            cv2.line(frame_bgr, (x, y), (x + corner_len, y), color, 4)
            cv2.line(frame_bgr, (x, y), (x, y + corner_len), color, 4)
            cv2.line(frame_bgr, (x + fw, y), (x + fw - corner_len, y), color, 4)
            cv2.line(frame_bgr, (x + fw, y), (x + fw, y + corner_len), color, 4)

            # Name badge background
            badge_text = f"{tracker.name} [{tracker.status}]"
            metric_text = f"Attn: {int(pose_score)}% | Seen: {int(tracker.total_visible_seconds)}s"
            cv2.rectangle(frame_bgr, (x, max(0, y - 40)), (x + max(len(badge_text)*10, 180), y), (20, 24, 30), -1)
            cv2.putText(frame_bgr, badge_text, (x + 5, max(15, y - 22)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.putText(frame_bgr, metric_text, (x + 5, max(30, y - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)

        # Check for departures in non-detected students
        for s_id, tracker in self.student_trackers.items():
            tracker.check_departure(current_time, session_start_time)

        return frame_bgr, detected_students_info
