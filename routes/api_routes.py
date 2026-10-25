"""
API Routes Blueprint.
Provides RESTful endpoints for video streaming, frame processing, acoustic telemetry,
multimodal fusion, Gemini 2.0 Flash teaching suggestions, and attendance exports.
"""

import time
import base64
import cv2
import numpy as np
from flask import Blueprint, jsonify, request, Response, send_file
from config import Config
from utils.storage_utils import (
    create_session,
    get_session,
    get_all_students,
    save_attendance_record,
    get_session_attendance,
    save_telemetry,
    get_session_telemetry,
    save_teaching_suggestion,
    get_session_suggestions,
    export_attendance_csv
)
from utils.vision_utils import VisionAnalyticsEngine
from utils.audio_utils import AudioAnalyticsEngine
from utils.fusion_utils import MultimodalFusionEngine
from utils.genai_utils import GeminiTeachingAgent
from utils.simulation_utils import ClassroomSimulator
from utils.tts_utils import TextToSpeechEngine

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Singleton state engines
vision_engine = VisionAnalyticsEngine()
audio_engine = AudioAnalyticsEngine()
fusion_engine = MultimodalFusionEngine()
genai_agent = GeminiTeachingAgent()
simulator = ClassroomSimulator()
tts_engine = TextToSpeechEngine()

# Session tracking state
active_session_state = {
    "session_id": "SES-ACTIVE-01",
    "title": "AI & Multimodal Intelligence Lecture",
    "start_time": time.time(),
    "is_simulated": True,
    "last_alert_time": 0
}

@api_bp.route("/session/active", methods=["GET"])
def get_active_session_info():
    """Returns active session status and elapsed duration."""
    elapsed = time.time() - active_session_state["start_time"]
    return jsonify({
        "session_id": active_session_state["session_id"],
        "title": active_session_state["title"],
        "elapsed_seconds": round(elapsed, 1),
        "is_simulated": active_session_state["is_simulated"]
    })

@api_bp.route("/session/start", methods=["POST"])
def start_session():
    """Initializes or resets a classroom session."""
    data = request.get_json() or {}
    session_id = data.get("session_id", f"SES-{int(time.time())}")
    title = data.get("title", "Classroom Session")
    is_simulated = data.get("is_simulated", True)

    active_session_state["session_id"] = session_id
    active_session_state["title"] = title
    active_session_state["start_time"] = time.time()
    active_session_state["is_simulated"] = is_simulated
    active_session_state["last_alert_time"] = 0

    create_session(session_id, title)
    return jsonify({"success": True, "session_id": session_id, "message": "Session started successfully."})

@api_bp.route("/video_feed")
def video_feed():
    """
    MJPEG streaming generator. Streams either synthetic simulated classroom feed
    or camera frame loop directly to browser <img> elements.
    """
    def generate():
        while True:
            elapsed = time.time() - active_session_state["start_time"]
            roster = get_all_students()

            if active_session_state["is_simulated"]:
                frame = simulator.generate_frame(elapsed)
            else:
                # Blank frame placeholder if external stream isn't pushed yet
                frame = np.full((480, 640, 3), 40, dtype=np.uint8)
                cv2.putText(frame, "Waiting for Live Camera Stream...", (80, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Process frame through vision engine
            annotated_frame, students_info = vision_engine.process_frame(
                frame,
                active_session_state["start_time"],
                roster
            )

            # Persist updated attendance records to DB
            for s in students_info:
                save_attendance_record(
                    active_session_state["session_id"],
                    s["student_id"],
                    first_seen=s.get("first_seen", None),
                    last_seen=s.get("last_seen", None),
                    sustained_duration=s.get("presence_seconds", 0.0),
                    presence_ratio=s.get("presence_ratio", 0.0),
                    status=s.get("status", "Absent")
                )

            ret, buffer = cv2.imencode('.jpg', annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if not ret:
                continue
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.08) # ~12-15 FPS for smooth lightweight streaming

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@api_bp.route("/telemetry/live", methods=["GET"])
def get_live_telemetry():
    """Returns combined real-time multimodal telemetry, active alerts, and student states."""
    elapsed = time.time() - active_session_state["start_time"]
    roster = get_all_students()

    # Get student info
    students_info = []
    for s_id, tracker in vision_engine.student_trackers.items():
        avg_move = np.mean(tracker.recent_movements) if tracker.recent_movements else 5.0
        students_info.append({
            "student_id": tracker.student_id,
            "name": tracker.name,
            "status": tracker.status,
            "presence_seconds": round(tracker.total_visible_seconds, 1),
            "presence_ratio": round(tracker.presence_ratio, 2),
            "pose_score": 85.0 if tracker.status == "Present" else 60.0,
            "movement_score": 75.0 if avg_move > 3 else 45.0,
            "inactivity_seconds": round(tracker.inactivity_duration, 1)
        })

    # Audio metrics
    if active_session_state["is_simulated"]:
        audio_metrics = simulator.generate_audio_signal(elapsed)
    else:
        audio_metrics = audio_engine.analyze_audio_chunk(np.zeros(512, dtype=np.float32))

    # Multimodal evaluation
    evaluation = fusion_engine.evaluate_classroom(students_info, audio_metrics, elapsed)

    # Persist aggregate telemetry slice
    save_telemetry(
        active_session_state["session_id"],
        timestamp=elapsed,
        student_id="aggregate",
        pose_score=evaluation["avg_pose"],
        movement_score=evaluation["avg_movement"],
        audio_score=evaluation["audio_score"],
        composite_score=evaluation["composite_score"],
        state_label=evaluation["engagement_level"],
        inactivity_seconds=0.0
    )

    # Check if AI suggestion should be auto-triggered
    auto_suggestion = None
    now = time.time()
    if evaluation["alerts"] and (now - active_session_state["last_alert_time"] > 25.0):
        active_session_state["last_alert_time"] = now
        top_alert = evaluation["alerts"][0]
        suggestion_res = genai_agent.generate_suggestion(top_alert["type"], evaluation)
        s_id = save_teaching_suggestion(
            active_session_state["session_id"],
            trigger_reason=top_alert["message"],
            suggestion_text=suggestion_res["suggestion"],
            pedagogical_category=suggestion_res.get("category", "Pacing"),
            severity=suggestion_res.get("severity", "info")
        )
        auto_suggestion = {
            "id": s_id,
            "category": suggestion_res.get("category", "Intervention"),
            "text": suggestion_res["suggestion"],
            "severity": suggestion_res.get("severity", "info"),
            "source": suggestion_res.get("source", "Agent")
        }

    return jsonify({
        "elapsed_seconds": round(elapsed, 1),
        "evaluation": evaluation,
        "audio_metrics": audio_metrics,
        "students": students_info,
        "auto_suggestion": auto_suggestion
    })

@api_bp.route("/suggestions/history", methods=["GET"])
def get_suggestions_history():
    """Retrieves all teaching suggestions recorded for active session."""
    session_id = request.args.get("session_id", active_session_state["session_id"])
    records = get_session_suggestions(session_id)
    return jsonify({"suggestions": records})

@api_bp.route("/suggestions/generate_manual", methods=["POST"])
def generate_manual_suggestion():
    """Generates an on-demand teaching intervention based on current telemetry."""
    data = request.get_json() or {}
    category = data.get("category", "ATTENTION_DROP")
    elapsed = time.time() - active_session_state["start_time"]

    context = {
        "composite_score": data.get("composite_score", 65.0),
        "avg_pose": 70.0,
        "avg_movement": 60.0,
        "interaction_mode": "Guided Instruction",
        "students_detected": len(vision_engine.student_trackers)
    }

    result = genai_agent.generate_suggestion(category, context)
    s_id = save_teaching_suggestion(
        active_session_state["session_id"],
        trigger_reason=f"Instructor On-Demand Request ({category})",
        suggestion_text=result["suggestion"],
        pedagogical_category=result.get("category", "Teaching Intervention"),
        severity=result.get("severity", "info")
    )
    tts_metadata = tts_engine.synthesize_suggestion_notice(result["suggestion"], s_id)

    return jsonify({
        "success": True,
        "id": s_id,
        "suggestion": result["suggestion"],
        "category": result.get("category", "Teaching Intervention"),
        "source": result.get("source", "Agent"),
        "tts": tts_metadata
    })

@api_bp.route("/ai/ask", methods=["POST"])
def ask_gemini():
    """Allows educator to converse with Gemini 2.0 Flash regarding classroom dynamics."""
    data = request.get_json() or {}
    question = data.get("question", "How can I improve student participation right now?")
    elapsed = time.time() - active_session_state["start_time"]

    if genai_agent.is_configured():
        try:
            prompt = f"""You are the Multimodal Classroom Intelligence Assistant powered by Google Gemini 2.0 Flash.
Session: {active_session_state['title']} (Elapsed: {int(elapsed // 60)} min {int(elapsed % 60)} sec)
Teacher Question: {question}

Provide a concise, practical, expert answer formatted in clean Markdown."""
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.5, "maxOutputTokens": 350}
            }
            res = requests.post(f"{genai_agent.api_url}?key={genai_agent.api_key}", headers={"Content-Type": "application/json"}, json=payload, timeout=6)
            if res.status_code == 200:
                answer = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                return jsonify({"answer": answer, "source": "Google Gemini 2.0 Flash"})
        except Exception as e:
            pass

    # High-quality offline pedagogical response
    answer = f"""**Pedagogical Insight:**
Regarding: *"{question}"*

1. **Immediate Pacing Action:** Transition from passive presentation to an active check-in (e.g. give students 60 seconds to summarize the core principle to their neighbor).
2. **Multimodal Calibration:** If head pose indicates downward focus, integrate a collaborative digital whiteboard or quick visual question on the screen to draw upward focus.
3. **Inclusive Participation:** Use warm-calling (noticing an interesting written thought) rather than cold-calling to encourage quieter learners."""
    return jsonify({"answer": answer, "source": "Local Pedagogical Assistant (Offline)"})

@api_bp.route("/ai/quiz", methods=["POST"])
def generate_quiz():
    """Generates an instant 3-question pulse quiz to re-engage the classroom."""
    data = request.get_json() or {}
    topic = data.get("topic", "Classroom Engagement & AI Concepts")
    quiz_markdown = genai_agent.generate_interactive_quiz(topic)
    return jsonify({"quiz": quiz_markdown})

@api_bp.route("/attendance/export", methods=["GET"])
def export_attendance():
    """Exports attendance records as a downloadable CSV file."""
    session_id = request.args.get("session_id", active_session_state["session_id"])
    csv_data = export_attendance_csv(session_id)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=attendance_{session_id}.csv"}
    )

@api_bp.route("/settings/update", methods=["POST"])
def update_settings():
    """Updates runtime configuration settings and Gemini API key."""
    data = request.get_json() or {}

    if "min_sustained_seconds" in data:
        Config.MIN_SUSTAINED_SECONDS = int(data["min_sustained_seconds"])
    if "gemini_api_key" in data:
        Config.GEMINI_API_KEY = data["gemini_api_key"].strip()
        genai_agent.api_key = Config.GEMINI_API_KEY
    if "privacy_offline_mode" in data:
        Config.PRIVACY_OFFLINE_MODE = bool(data["privacy_offline_mode"])
    if "weight_head_pose" in data:
        Config.WEIGHT_HEAD_POSE = float(data["weight_head_pose"])
    if "weight_movement" in data:
        Config.WEIGHT_MOVEMENT = float(data["weight_movement"])
    if "weight_audio" in data:
        Config.WEIGHT_AUDIO = float(data["weight_audio"])

    return jsonify({"success": True, "message": "Settings updated successfully."})
