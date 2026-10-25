"""
Multimodal Fusion Engine.
Fuses computer vision features (head pose, movement, inactivity) and acoustic signals
into a unified Engagement Index and detects classroom attention drops and pacing anomalies.
"""

from collections import deque
from config import Config

class MultimodalFusionEngine:
    """Combines visual and audio metrics into composite engagement scores and flags anomalies."""
    def __init__(self):
        self.history = deque(maxlen=300)  # ~5-10 minutes of chronological telemetry
        self.anomaly_log = []

    def fuse(self, pose_score, movement_score, audio_score):
        """
        Calculates weighted composite engagement score.
        Formula: E = W_pose * S_pose + W_move * S_move + W_audio * S_audio
        """
        w_pose = Config.WEIGHT_HEAD_POSE
        w_move = Config.WEIGHT_MOVEMENT
        w_audio = Config.WEIGHT_AUDIO

        # Normalize weights in case user modified them in config
        total_w = w_pose + w_move + w_audio
        if total_w <= 0:
            total_w = 1.0

        composite = (w_pose * pose_score + w_move * movement_score + w_audio * audio_score) / total_w
        return max(0.0, min(100.0, round(composite, 1)))

    def evaluate_classroom(self, student_detections, audio_metrics, session_elapsed_seconds):
        """
        Evaluates full classroom state across all detected students and acoustic stream.
        Returns:
            summary dict with classroom_engagement, student_count, alerts, and trend status.
        """
        if student_detections:
            avg_pose = sum(s["pose_score"] for s in student_detections) / len(student_detections)
            avg_movement = sum(s["movement_score"] for s in student_detections) / len(student_detections)
            total_active_students = sum(1 for s in student_detections if s["status"] in ("Present", "Present (Partial)", "Tardy"))
        else:
            avg_pose = 70.0
            avg_movement = 65.0
            total_active_students = 0

        audio_score = audio_metrics.get("audio_score", 70.0)
        interaction_mode = audio_metrics.get("interaction_mode", "Guided Instruction")

        composite_score = self.fuse(avg_pose, avg_movement, audio_score)

        # Categorize overall engagement level
        if composite_score >= Config.HIGH_ENGAGEMENT_THRESHOLD:
            engagement_level = "High Engagement"
            badge_color = "success"
        elif composite_score >= Config.ATTENTION_DROP_THRESHOLD:
            engagement_level = "Moderate Engagement"
            badge_color = "warning"
        else:
            engagement_level = "Low Engagement (Attention Drop)"
            badge_color = "danger"

        # Record telemetry history point
        point = {
            "elapsed_seconds": round(session_elapsed_seconds, 1),
            "composite": composite_score,
            "pose": round(avg_pose, 1),
            "movement": round(avg_movement, 1),
            "audio": round(audio_score, 1),
            "students_present": total_active_students
        }
        self.history.append(point)

        # Check for anomalies and triggers
        alerts = []

        # 1. Attention Drop Alert
        if composite_score < Config.ATTENTION_DROP_THRESHOLD and session_elapsed_seconds > 20:
            alerts.append({
                "type": "ATTENTION_DROP",
                "severity": "warning",
                "message": f"Classroom engagement dropped to {composite_score}%. Attention deficit detected.",
                "timestamp": round(session_elapsed_seconds, 1)
            })

        # 2. Monologue Alert
        if interaction_mode == "Teacher Monologue" and avg_movement < 45.0:
            alerts.append({
                "type": "MONOLOGUE_FATIGUE",
                "severity": "info",
                "message": "Continuous monologue detected with minimal learner movement. High passive fatigue risk.",
                "timestamp": round(session_elapsed_seconds, 1)
            })

        # 3. Individual Student Inactivity Alerts
        for s in student_detections:
            if s.get("inactivity_seconds", 0) >= Config.INACTIVITY_ALERT_SECONDS:
                alerts.append({
                    "type": "STUDENT_INACTIVE",
                    "severity": "warning",
                    "message": f"{s['name']} has been inactive for {int(s['inactivity_seconds'])} seconds.",
                    "timestamp": round(session_elapsed_seconds, 1),
                    "student_id": s["student_id"]
                })

        return {
            "composite_score": composite_score,
            "engagement_level": engagement_level,
            "badge_color": badge_color,
            "avg_pose": round(avg_pose, 1),
            "avg_movement": round(avg_movement, 1),
            "audio_score": round(audio_score, 1),
            "interaction_mode": interaction_mode,
            "students_detected": len(student_detections),
            "students_present": total_active_students,
            "alerts": alerts
        }
