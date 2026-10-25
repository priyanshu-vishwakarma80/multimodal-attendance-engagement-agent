"""
Simulation and Synthetic Classroom Generator module.
Generates synthetic multi-student classroom feeds with realistic visual behaviors,
head poses, attention drops, and audio signals for seamless testing and demonstration.
"""

import cv2
import numpy as np
import time
import math

class ClassroomSimulator:
    """Generates synthetic video frames and audio levels depicting a multi-student classroom."""
    def __init__(self, width=800, height=500):
        self.width = width
        self.height = height
        self.start_time = time.time()

        # Simulated students in a classroom grid
        self.students = [
            {"id": "STU-101", "name": "Alex Chen", "x": 160, "y": 180, "base_focus": 0.92, "state": "Attentive"},
            {"id": "STU-102", "name": "Maya Patel", "x": 400, "y": 180, "base_focus": 0.88, "state": "Attentive"},
            {"id": "STU-103", "name": "Liam Johnson", "x": 640, "y": 180, "base_focus": 0.85, "state": "Attentive"},
            {"id": "STU-104", "name": "Sophia Garcia", "x": 280, "y": 360, "base_focus": 0.78, "state": "Note-Taking"},
            {"id": "STU-105", "name": "Ethan Brown", "x": 520, "y": 360, "base_focus": 0.65, "state": "Distracted"}
        ]

    def render_student_avatar(self, img, s, t):
        """Draws a stylized student portrait with dynamic gaze and head pose."""
        cx, cy = s["x"], s["y"]
        state = s["state"]

        # Dynamic head movement oscillation
        speed = 1.2
        if state == "Attentive":
            dx = math.sin(t * speed + cx) * 4
            dy = math.cos(t * speed * 0.7 + cy) * 3
            eye_off_x, eye_off_y = dx * 0.8, dy * 0.6
            head_color = (225, 230, 235)
        elif state == "Note-Taking":
            dx = math.sin(t * 0.6) * 3
            dy = 12 + math.sin(t * 1.5) * 2  # tilted down
            eye_off_x, eye_off_y = 0, 7
            head_color = (210, 220, 230)
        else: # Distracted
            dx = 18 + math.sin(t * 0.8) * 8 # looking sideways
            dy = math.sin(t * 0.5) * 5
            eye_off_x, eye_off_y = 10, 0
            head_color = (195, 205, 220)

        # Draw torso / shoulders
        torso_y = cy + 50
        cv2.ellipse(img, (int(cx + dx * 0.3), int(torso_y + 40)), (55, 35), 0, 0, 360, (70, 80, 95), -1)

        # Draw Head / Face (Oval)
        face_cx = int(cx + dx)
        face_cy = int(cy + dy)
        face_w = 42
        face_h = 52
        cv2.ellipse(img, (face_cx, face_cy), (face_w, face_h), 0, 0, 360, head_color, -1)
        cv2.ellipse(img, (face_cx, face_cy), (face_w, face_h), 0, 0, 360, (140, 150, 165), 2)

        # Hair
        cv2.ellipse(img, (face_cx, face_cy - 20), (face_w + 2, 28), 0, 180, 360, (40, 40, 50), -1)

        # Eyes
        eye_y = int(face_cy - 6 + eye_off_y)
        left_eye_x = int(face_cx - 16 + eye_off_x)
        right_eye_x = int(face_cx + 16 + eye_off_x)

        cv2.circle(img, (left_eye_x, eye_y), 6, (255, 255, 255), -1)
        cv2.circle(img, (right_eye_x, eye_y), 6, (255, 255, 255), -1)
        cv2.circle(img, (left_eye_x, eye_y), 3, (40, 30, 20), -1)
        cv2.circle(img, (right_eye_x, eye_y), 3, (40, 30, 20), -1)

        # Mouth
        mouth_y = int(face_cy + 24 + dy * 0.3)
        cv2.line(img, (face_cx - 10, mouth_y), (face_cx + 10, mouth_y), (100, 70, 70), 2)

        # Simulated bounding box return format
        box_x = face_cx - face_w
        box_y = face_cy - face_h - 10
        box_w = face_w * 2
        box_h = face_h * 2 + 15
        return (box_x, box_y, box_w, box_h)

    def generate_frame(self, elapsed_seconds):
        """Creates a realistic classroom scene frame with animated students."""
        t = elapsed_seconds
        # Classroom background: subtle slate gradient with board border
        frame = np.full((self.height, self.width, 3), 32, dtype=np.uint8)

        # Draw classroom blackboard / projector border
        cv2.rectangle(frame, (60, 20), (self.width - 60, 90), (45, 52, 58), -1)
        cv2.rectangle(frame, (60, 20), (self.width - 60, 90), (70, 80, 90), 2)
        cv2.putText(frame, "AI & Multimodal Intelligence Class - Section A", (85, 60), cv2.FONT_HERSHEY_DUPLEX, 0.75, (220, 230, 240), 1, cv2.LINE_AA)

        # Introduce cyclical attention drop event every 50 seconds for 12 seconds
        cycle = t % 60
        is_drop_phase = 35 <= cycle <= 48

        for i, s in enumerate(self.students):
            if is_drop_phase and i >= 2:
                s["state"] = "Distracted"
            elif i == 3:
                s["state"] = "Note-Taking"
            elif i == 4 and (t % 30 > 15):
                s["state"] = "Distracted"
            else:
                s["state"] = "Attentive"

            self.render_student_avatar(frame, s, t)

        return frame

    def generate_audio_signal(self, elapsed_seconds):
        """Generates realistic classroom acoustic metrics matching the current phase."""
        cycle = elapsed_seconds % 60
        if 35 <= cycle <= 48:
            # Silence / low engagement phase
            rms = 0.015 + 0.005 * math.sin(elapsed_seconds)
            speech = False
            interaction_mode = "Independent Study / Silence"
            audio_score = 48.0
        elif 20 <= cycle < 35:
            # Active student discussion
            rms = 0.085 + 0.02 * math.sin(elapsed_seconds * 3)
            speech = True
            interaction_mode = "Active Discussion / Student Q&A"
            audio_score = 90.0
        else:
            # Guided instruction / lecture
            rms = 0.055 + 0.01 * math.sin(elapsed_seconds * 2)
            speech = True
            interaction_mode = "Guided Instruction"
            audio_score = 75.0

        db = float(20.0 * math.log10(max(rms, 1e-6)))
        return {
            "rms": round(rms, 4),
            "db": round(db, 1),
            "is_speech": speech,
            "interaction_mode": interaction_mode,
            "audio_score": audio_score
        }
