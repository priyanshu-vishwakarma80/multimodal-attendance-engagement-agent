"""
Database and Local Storage Utilities.
Handles SQLite operations, student rosters, session records, attendance logging,
and multimodal telemetry persistence.
"""

import sqlite3
import json
import csv
import io
from datetime import datetime
from pathlib import Path
from config import Config, DB_PATH

def get_db_connection():
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables in the SQLite database and seeds default student roster."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT,
        status TEXT DEFAULT 'active',
        duration_seconds REAL DEFAULT 0.0,
        total_students INTEGER DEFAULT 0,
        average_engagement REAL DEFAULT 0.0,
        summary TEXT
    )
    """)

    # Students table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        registered_at TEXT NOT NULL
    )
    """)

    # Attendance records table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        student_id TEXT NOT NULL,
        first_seen TEXT,
        last_seen TEXT,
        sustained_duration_seconds REAL DEFAULT 0.0,
        presence_ratio REAL DEFAULT 0.0,
        status TEXT DEFAULT 'Absent',
        updated_at TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(session_id),
        FOREIGN KEY(student_id) REFERENCES students(student_id),
        UNIQUE(session_id, student_id)
    )
    """)

    # Engagement telemetry table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS engagement_telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        timestamp REAL NOT NULL,
        student_id TEXT DEFAULT 'aggregate',
        pose_score REAL DEFAULT 0.0,
        movement_score REAL DEFAULT 0.0,
        audio_score REAL DEFAULT 0.0,
        composite_score REAL DEFAULT 0.0,
        state_label TEXT DEFAULT 'Attentive',
        inactivity_seconds REAL DEFAULT 0.0,
        FOREIGN KEY(session_id) REFERENCES sessions(session_id)
    )
    """)

    # AI Teaching suggestions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teaching_suggestions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        trigger_reason TEXT NOT NULL,
        suggestion_text TEXT NOT NULL,
        pedagogical_category TEXT DEFAULT 'Pacing',
        severity TEXT DEFAULT 'info',
        applied INTEGER DEFAULT 0,
        FOREIGN KEY(session_id) REFERENCES sessions(session_id)
    )
    """)

    conn.commit()
    conn.close()
    seed_default_students()

def seed_default_students():
    """Populates standard student roster if not already present."""
    default_roster = [
        ("STU-101", "Alex Chen", "alex.chen@classroom.edu"),
        ("STU-102", "Maya Patel", "maya.patel@classroom.edu"),
        ("STU-103", "Liam Johnson", "liam.j@classroom.edu"),
        ("STU-104", "Sophia Garcia", "sophia.g@classroom.edu"),
        ("STU-105", "Ethan Brown", "ethan.b@classroom.edu"),
        ("STU-106", "Olivia Davis", "olivia.d@classroom.edu"),
        ("STU-107", "Noah Miller", "noah.m@classroom.edu"),
        ("STU-108", "Emma Wilson", "emma.w@classroom.edu")
    ]
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().isoformat()
    for student_id, name, email in default_roster:
        cursor.execute("""
        INSERT OR IGNORE INTO students (student_id, name, email, registered_at)
        VALUES (?, ?, ?, ?)
        """, (student_id, name, email, now_iso))
    conn.commit()
    conn.close()

def get_all_students():
    """Fetches all registered students."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM students ORDER BY student_id ASC").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_student_by_id(student_id):
    """Fetches single student record."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def create_session(session_id, title):
    """Creates a new classroom session and initializes attendance for all students."""
    conn = get_db_connection()
    now_iso = datetime.now().isoformat()
    conn.execute("""
    INSERT OR REPLACE INTO sessions (session_id, title, start_time, status)
    VALUES (?, ?, ?, 'active')
    """, (session_id, title, now_iso))

    # Initialize attendance rows for registered students
    students = conn.execute("SELECT student_id FROM students").fetchall()
    for s in students:
        conn.execute("""
        INSERT OR IGNORE INTO attendance_records (session_id, student_id, status, updated_at)
        VALUES (?, ?, 'Absent', ?)
        """, (session_id, s["student_id"], now_iso))

    conn.commit()
    conn.close()

def update_session(session_id, **kwargs):
    """Updates fields of an existing session."""
    conn = get_db_connection()
    fields = []
    values = []
    for k, v in kwargs.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(session_id)
    query = f"UPDATE sessions SET {', '.join(fields)} WHERE session_id = ?"
    conn.execute(query, values)
    conn.commit()
    conn.close()

def get_session(session_id):
    """Retrieves session details by session_id."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def get_recent_sessions(limit=10):
    """Retrieves most recent sessions."""
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM sessions ORDER BY start_time DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_attendance_record(session_id, student_id, first_seen, last_seen, sustained_duration, presence_ratio, status):
    """Inserts or updates an attendance record."""
    conn = get_db_connection()
    now_iso = datetime.now().isoformat()
    conn.execute("""
    INSERT INTO attendance_records (session_id, student_id, first_seen, last_seen, sustained_duration_seconds, presence_ratio, status, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(session_id, student_id) DO UPDATE SET
        first_seen = excluded.first_seen,
        last_seen = excluded.last_seen,
        sustained_duration_seconds = excluded.sustained_duration_seconds,
        presence_ratio = excluded.presence_ratio,
        status = excluded.status,
        updated_at = excluded.updated_at
    """, (session_id, student_id, first_seen, last_seen, sustained_duration, presence_ratio, status, now_iso))
    conn.commit()
    conn.close()

def get_session_attendance(session_id):
    """Returns joined attendance records for a session with student metadata."""
    conn = get_db_connection()
    query = """
    SELECT ar.*, s.name, s.email
    FROM attendance_records ar
    JOIN students s ON ar.student_id = s.student_id
    WHERE ar.session_id = ?
    ORDER BY ar.status DESC, s.name ASC
    """
    rows = conn.execute(query, (session_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_telemetry(session_id, timestamp, student_id, pose_score, movement_score, audio_score, composite_score, state_label, inactivity_seconds):
    """Records real-time engagement telemetry slice."""
    conn = get_db_connection()
    conn.execute("""
    INSERT INTO engagement_telemetry (session_id, timestamp, student_id, pose_score, movement_score, audio_score, composite_score, state_label, inactivity_seconds)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (session_id, timestamp, student_id, pose_score, movement_score, audio_score, composite_score, state_label, inactivity_seconds))
    conn.commit()
    conn.close()

def get_session_telemetry(session_id, limit=200):
    """Retrieves chronological engagement telemetry for a session."""
    conn = get_db_connection()
    rows = conn.execute("""
    SELECT * FROM engagement_telemetry
    WHERE session_id = ?
    ORDER BY timestamp ASC
    LIMIT ?
    """, (session_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_teaching_suggestion(session_id, trigger_reason, suggestion_text, pedagogical_category='Pacing', severity='info'):
    """Records an AI teaching suggestion."""
    conn = get_db_connection()
    now_iso = datetime.now().isoformat()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO teaching_suggestions (session_id, timestamp, trigger_reason, suggestion_text, pedagogical_category, severity)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, now_iso, trigger_reason, suggestion_text, pedagogical_category, severity))
    conn.commit()
    suggestion_id = cursor.lastrowid
    conn.close()
    return suggestion_id

def get_session_suggestions(session_id):
    """Retrieves all teaching suggestions for a session."""
    conn = get_db_connection()
    rows = conn.execute("""
    SELECT * FROM teaching_suggestions
    WHERE session_id = ?
    ORDER BY id DESC
    """, (session_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def export_attendance_csv(session_id):
    """Generates CSV string of attendance records for a session."""
    records = get_session_attendance(session_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student ID", "Name", "Email", "Status", "First Seen", "Last Seen", "Sustained Presence (s)", "Presence %"])
    for r in records:
        writer.writerow([
            r.get("student_id", ""),
            r.get("name", ""),
            r.get("email", ""),
            r.get("status", "Absent"),
            r.get("first_seen", "N/A"),
            r.get("last_seen", "N/A"),
            f"{r.get('sustained_duration_seconds', 0.0):.1f}",
            f"{(r.get('presence_ratio', 0.0) * 100):.1f}%"
        ])
    return output.getvalue()
