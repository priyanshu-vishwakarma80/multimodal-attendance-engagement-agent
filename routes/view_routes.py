"""
View Routes Blueprint.
Renders HTML templates for Dashboard, Live Monitor, Attendance, Analytics, AI Suggestions, and Settings.
"""

from flask import Blueprint, render_template, request, redirect, url_for
from config import Config
from utils.storage_utils import (
    get_recent_sessions,
    get_all_students,
    get_session,
    get_session_attendance,
    get_session_telemetry,
    get_session_suggestions
)

view_bp = Blueprint("views", __name__)

@view_bp.route("/")
def index():
    """Main dashboard overview."""
    recent_sessions = get_recent_sessions(limit=5)
    students = get_all_students()
    active_session = recent_sessions[0] if recent_sessions else None
    return render_template(
        "index.html",
        recent_sessions=recent_sessions,
        students=students,
        active_session=active_session,
        config=Config
    )

@view_bp.route("/monitor")
def monitor():
    """Live classroom monitoring interface."""
    session_id = request.args.get("session_id", "SES-ACTIVE-01")
    students = get_all_students()
    return render_template(
        "live_monitor.html",
        session_id=session_id,
        students=students,
        config=Config
    )

@view_bp.route("/attendance")
def attendance():
    """Attendance log and student sustained presence management."""
    session_id = request.args.get("session_id", "SES-ACTIVE-01")
    sessions = get_recent_sessions(limit=10)
    attendance_records = get_session_attendance(session_id)
    return render_template(
        "attendance.html",
        selected_session=session_id,
        sessions=sessions,
        records=attendance_records,
        config=Config
    )

@view_bp.route("/analytics")
def analytics():
    """Engagement dynamics, time-series charts, and multimodal fusion breakdown."""
    session_id = request.args.get("session_id", "SES-ACTIVE-01")
    sessions = get_recent_sessions(limit=10)
    telemetry = get_session_telemetry(session_id, limit=100)
    return render_template(
        "analytics.html",
        selected_session=session_id,
        sessions=sessions,
        telemetry=telemetry,
        config=Config
    )

@view_bp.route("/suggestions")
def suggestions():
    """AI Teaching Assistant & Gemini 2.0 Flash pedagogical suggestions."""
    session_id = request.args.get("session_id", "SES-ACTIVE-01")
    sessions = get_recent_sessions(limit=10)
    past_suggestions = get_session_suggestions(session_id)
    return render_template(
        "suggestions.html",
        selected_session=session_id,
        sessions=sessions,
        suggestions=past_suggestions,
        config=Config
    )

@view_bp.route("/settings")
def settings():
    """System configuration, sustained presence thresholds, and Gemini API setup."""
    return render_template("settings.html", config=Config)
