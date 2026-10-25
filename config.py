"""
Configuration module for Multimodal Attendance & Engagement Agent.
Handles environment variables, default paths, algorithm weights, and thresholds.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables if .env file exists
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

# Storage Paths
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
AUDIO_DIR = STORAGE_DIR / "audio"
REPORTS_DIR = STORAGE_DIR / "reports"
DB_PATH = STORAGE_DIR / "classroom_intelligence.db"

# Ensure required directories exist
for folder in [STORAGE_DIR, UPLOAD_DIR, AUDIO_DIR, REPORTS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "multimodal-attendance-secret-key-2026")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1")
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")

    # GenAI / Gemini Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    # Attendance Logic Configuration
    # Minimum sustained presence (in seconds) required to mark a student as Present
    MIN_SUSTAINED_SECONDS = int(os.getenv("MIN_SUSTAINED_SECONDS", 15))
    # Threshold percentage of session presence required for full attendance
    ATTENDANCE_PRESENCE_RATIO_THRESHOLD = float(os.getenv("ATTENDANCE_PRESENCE_RATIO_THRESHOLD", 0.40))
    # Absence grace period before declaring student absent or left early (seconds)
    ABSENCE_GRACE_PERIOD_SECONDS = int(os.getenv("ABSENCE_GRACE_PERIOD_SECONDS", 25))

    # Multimodal Engagement Fusion Weights
    # E_total = W_pose * S_pose + W_movement * S_movement + W_audio * S_audio
    WEIGHT_HEAD_POSE = float(os.getenv("WEIGHT_HEAD_POSE", 0.40))
    WEIGHT_MOVEMENT = float(os.getenv("WEIGHT_MOVEMENT", 0.35))
    WEIGHT_AUDIO = float(os.getenv("WEIGHT_AUDIO", 0.25))

    # Engagement Anomaly Thresholds
    ATTENTION_DROP_THRESHOLD = float(os.getenv("ATTENTION_DROP_THRESHOLD", 40.0))
    HIGH_ENGAGEMENT_THRESHOLD = float(os.getenv("HIGH_ENGAGEMENT_THRESHOLD", 75.0))
    INACTIVITY_ALERT_SECONDS = int(os.getenv("INACTIVITY_ALERT_SECONDS", 30))

    # Privacy & Local Operation
    PRIVACY_OFFLINE_MODE = os.getenv("PRIVACY_OFFLINE_MODE", "False").lower() in ("true", "1")
    ANONYMIZE_FACES_IN_REPORTS = os.getenv("ANONYMIZE_FACES_IN_REPORTS", "False").lower() in ("true", "1")
