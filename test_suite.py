"""
Automated Test Suite for Multimodal Attendance & Engagement Agent.
Verifies database operations, vision tracking, sustained presence logic,
audio analysis, multimodal fusion, and Flask web endpoints.
"""

import unittest
import time
import numpy as np
from app import create_app
from config import Config
from utils.storage_utils import (
    init_db,
    get_all_students,
    create_session,
    save_attendance_record,
    get_session_attendance,
    export_attendance_csv
)
from utils.vision_utils import StudentPresenceTracker, VisionAnalyticsEngine
from utils.audio_utils import AudioAnalyticsEngine
from utils.fusion_utils import MultimodalFusionEngine
from utils.genai_utils import GeminiTeachingAgent

class TestMultimodalAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_01_database_and_roster(self):
        """Verifies database initialization and student roster seeding."""
        students = get_all_students()
        self.assertGreaterEqual(len(students), 5, "Database must seed at least 5 default students.")
        self.assertEqual(students[0]["student_id"], "STU-101")

    def test_02_sustained_presence_logic(self):
        """
        Verifies that single-frame/transient appearances (<15s) are NOT marked Present,
        while sustained presence (>=15s) correctly transitions to Present.
        """
        tracker = StudentPresenceTracker("STU-TEST", "Test Student")
        start_time = time.time() - 30

        # Simulate 2 seconds of quick walk-by detection
        tracker.update_presence(start_time + 1.0, start_time)
        tracker.update_presence(start_time + 2.0, start_time)
        self.assertEqual(tracker.status, "Pending (Transient)", "Short appearance must not mark student Present.")

        # Simulate sustained detection exceeding threshold (>15s)
        for t_offset in range(3, 20):
            tracker.update_presence(start_time + t_offset, start_time)

        self.assertIn(tracker.status, ("Present", "Present (Partial)"), "Sustained presence must mark student Present.")

    def test_03_audio_analytics(self):
        """Verifies acoustic RMS energy calculation and interaction mode detection."""
        audio_engine = AudioAnalyticsEngine()
        # Synthetic speech signal (sine wave burst)
        t = np.linspace(0, 1, 16000)
        signal = (np.sin(2 * np.pi * 440 * t) * 16000).astype(np.int16)

        metrics = audio_engine.analyze_audio_chunk(signal)
        self.assertGreater(metrics["rms"], 0.0, "RMS must be positive for non-zero audio.")
        self.assertGreater(metrics["db"], -40.0, "Active audio must be above silence threshold.")

    def test_04_multimodal_fusion(self):
        """Verifies weighted fusion formula E = 0.40*Pose + 0.35*Move + 0.25*Audio."""
        fusion = MultimodalFusionEngine()
        score = fusion.fuse(pose_score=80.0, movement_score=70.0, audio_score=60.0)
        # 0.40*80 + 0.35*70 + 0.25*60 = 32 + 24.5 + 15 = 71.5
        self.assertAlmostEqual(score, 71.5, delta=0.5)

    def test_05_genai_offline_fallback(self):
        """Verifies that the pedagogical agent provides valid suggestions even without an external API key."""
        agent = GeminiTeachingAgent()
        context = {
            "composite_score": 38.0,
            "avg_pose": 40.0,
            "avg_movement": 35.0,
            "interaction_mode": "Guided Instruction",
            "students_detected": 5
        }
        suggestion = agent.generate_suggestion("ATTENTION_DROP", context)
        self.assertIn("suggestion", suggestion)
        self.assertTrue(len(suggestion["suggestion"]) > 10)

    def test_06_flask_endpoints(self):
        """Verifies key HTTP view and REST endpoints."""
        res_index = self.client.get("/")
        self.assertEqual(res_index.status_code, 200)

        res_monitor = self.client.get("/monitor")
        self.assertEqual(res_monitor.status_code, 200)

        res_telemetry = self.client.get("/api/telemetry/live")
        self.assertEqual(res_telemetry.status_code, 200)
        json_data = res_telemetry.get_json()
        self.assertIn("evaluation", json_data)

        res_export = self.client.get("/api/attendance/export?session_id=SES-ACTIVE-01")
        self.assertEqual(res_export.status_code, 200)
        self.assertIn("text/csv", res_export.content_type)

if __name__ == "__main__":
    unittest.main()
