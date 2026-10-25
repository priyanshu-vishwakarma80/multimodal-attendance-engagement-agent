"""
GenAI module for Google Gemini 2.0 Flash integration and offline pedagogical agent.
Generates real-time teaching suggestions, lesson pacing interventions,
interactive classroom activities, and session analytics debriefs.
"""

import json
import logging
import requests
from config import Config

logger = logging.getLogger(__name__)

OFFLINE_SUGGESTIONS_BANK = {
    "ATTENTION_DROP": [
        {
            "category": "Interactive Engagement",
            "suggestion": "Attention dropped below 40%. Execute a 90-second 'Think-Pair-Share' prompt to re-engage passive listeners.",
            "severity": "warning"
        },
        {
            "category": "Active Retrieval",
            "suggestion": "Audience attention dip detected. Pause and present a quick 1-question pulse poll to check concept retention.",
            "severity": "warning"
        },
        {
            "category": "Pacing Adjustment",
            "suggestion": "Prolonged screen/downward focus detected. Invite a student volunteer to summarize the key takeaway before advancing slides.",
            "severity": "info"
        }
    ],
    "MONOLOGUE_FATIGUE": [
        {
            "category": "Instructional Pacing",
            "suggestion": "Continuous teacher monologue with low physical activity. Open the floor for clarifying questions or cold-call a discussion prompt.",
            "severity": "warning"
        },
        {
            "category": "Collaborative Learning",
            "suggestion": "High acoustic lecture duration. Break into 2-minute peer discussion circles on the current example.",
            "severity": "info"
        }
    ],
    "STUDENT_INACTIVE": [
        {
            "category": "Individual Support",
            "suggestion": "Multiple students showing prolonged visual inactivity. Walk around the room or ask students to write down 1 lingering question.",
            "severity": "info"
        }
    ],
    "HIGH_ENGAGEMENT": [
        {
            "category": "Positive Reinforcement",
            "suggestion": "High classroom engagement (>80%). Excellent pacing and interaction. Ideal moment to introduce higher-order problem solving.",
            "severity": "info"
        }
    ]
}

class GeminiTeachingAgent:
    """Provides AI-driven pedagogical feedback using Gemini 2.0 Flash or local heuristic agent."""
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model = Config.GEMINI_MODEL
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    def is_configured(self):
        """Returns True if Gemini API key is provided and offline mode is not forced."""
        return bool(self.api_key and not Config.PRIVACY_OFFLINE_MODE)

    def generate_suggestion(self, trigger_type, telemetry_context):
        """
        Generates targeted teaching suggestion based on real-time classroom telemetry.
        Falls back seamlessly to local heuristic expert system when offline.
        """
        if self.is_configured():
            try:
                prompt = f"""You are an expert AI Pedagogical Assistant observing a live classroom session.
A real-time telemetry alert was triggered: '{trigger_type}'.
Classroom Telemetry:
- Composite Engagement: {telemetry_context.get('composite_score', 'N/A')}%
- Head Pose / Visual Attention Score: {telemetry_context.get('avg_pose', 'N/A')}%
- Student Movement Score: {telemetry_context.get('avg_movement', 'N/A')}%
- Audio Level & Mode: {telemetry_context.get('interaction_mode', 'N/A')}
- Students Detected: {telemetry_context.get('students_detected', 0)}

Provide an immediate, actionable, highly practical teaching intervention in 1-2 concise sentences.
Focus on actionable techniques: Think-Pair-Share, Quick Poll, Cold Calling, Stretching, Concept Check, or Pacing shifts.
Format your output as valid JSON with keys:
"category" (string: e.g. 'Pacing', 'Active Learning', 'Intervention'),
"suggestion" (string: 1-2 sentences),
"severity" (string: 'info' or 'warning')
"""
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.4, "maxOutputTokens": 200}
                }
                headers = {"Content-Type": "application/json"}
                response = requests.post(f"{self.api_url}?key={self.api_key}", headers=headers, json=payload, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    # Clean markdown code block wraps if returned
                    if raw_text.startswith("```json"):
                        raw_text = raw_text.strip("```json").strip("```").strip()
                    elif raw_text.startswith("```"):
                        raw_text = raw_text.strip("```").strip()
                    parsed = json.loads(raw_text)
                    return {
                        "category": parsed.get("category", "Active Learning"),
                        "suggestion": parsed.get("suggestion", raw_text),
                        "severity": parsed.get("severity", "info"),
                        "source": "Gemini 2.0 Flash"
                    }
            except Exception as e:
                logger.warning(f"Gemini API request failed, falling back to offline engine: {e}")

        # Local Offline Heuristic Pedagogical Engine
        import random
        pool = OFFLINE_SUGGESTIONS_BANK.get(trigger_type, OFFLINE_SUGGESTIONS_BANK["ATTENTION_DROP"])
        picked = random.choice(pool)
        return {
            "category": picked["category"],
            "suggestion": picked["suggestion"],
            "severity": picked["severity"],
            "source": "Local Privacy-Preserving Agent"
        }

    def generate_session_summary(self, session_title, duration_minutes, avg_engagement, attendance_count, peak_time, drop_time):
        """Generates comprehensive post-session pedagogical debrief."""
        if self.is_configured():
            try:
                prompt = f"""You are a master educator evaluating a completed classroom session.
Session Details:
- Title: {session_title}
- Duration: {duration_minutes} minutes
- Students Present: {attendance_count}
- Average Engagement Index: {avg_engagement}%
- Peak Engagement Window: Minute {peak_time}
- Attention Drop Window: Minute {drop_time}

Generate a concise 3-paragraph executive teaching report:
1. Overall Session Effectiveness & Pacing.
2. Multimodal Engagement & Interaction Dynamics Analysis.
3. 2 Concrete Recommendations for the Next Lecture.
Write directly in professional, encouraging tone."""
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.6, "maxOutputTokens": 450}
                }
                headers = {"Content-Type": "application/json"}
                res = requests.post(f"{self.api_url}?key={self.api_key}", headers=headers, json=payload, timeout=8)
                if res.status_code == 200:
                    data = res.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception as e:
                logger.warning(f"Gemini summary generation failed: {e}")

        # High-quality offline debrief template
        return f"""### Session Executive Summary: {session_title}

**1. Overall Session Effectiveness & Pacing:**
The session sustained an average engagement score of **{avg_engagement:.1f}%** across **{attendance_count} participating students** over **{duration_minutes:.1f} minutes**. The instructional flow exhibited steady pacing, with strong student presence verified through continuous spatial and facial tracking.

**2. Multimodal Interaction Dynamics:**
Visual focus and head pose alignment reached a peak around minute **{peak_time:.1f}**, coinciding with active concept introduction. Acoustic monitoring identified periods of collaborative interaction balanced with instructional explanation. A transient attention drop occurred near minute **{drop_time:.1f}**, highlighting a transition point where pacing adjustments benefited learner retention.

**3. Actionable Recommendations for Next Session:**
- Implement short 2-minute active retrieval exercises immediately following the 20-minute mark to preempt natural cognitive fatigue.
- Increase student verbal participation during mid-session transitions by incorporating structured peer checks."""

    def generate_interactive_quiz(self, topic="Classroom Concepts"):
        """Generates a 3-question quick pulse quiz to restore classroom attention."""
        if self.is_configured():
            try:
                prompt = f"Create a 3-question multiple choice quick check quiz on the topic '{topic}' to re-engage students. Include correct answers and brief explanations. Return formatted markdown."
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.5, "maxOutputTokens": 400}
                }
                res = requests.post(f"{self.api_url}?key={self.api_key}", headers={"Content-Type": "application/json"}, json=payload, timeout=6)
                if res.status_code == 200:
                    return res.json()["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                pass

        # Offline fallback quiz generator
        return f"""### 🎯 Quick Pulse Check: {topic}

**Question 1:** What is the primary indicator of sustained visual focus in classroom interaction?
- A) Blinking rate exclusively
- B) Head pose alignment and continuous gaze toward instructional board *(Correct)*
- C) Total head stillness for over 2 minutes
- D) Screen brightness

**Question 2:** When multimodal audio indicates continuous lecture monologue with low movement, what is the recommended intervention?
- A) Speak louder
- B) Initiate a 90-second Think-Pair-Share or quick concept poll *(Correct)*
- C) End the lecture immediately
- D) Dim classroom lighting

**Question 3:** Why is sustained presence logic essential for accurate attendance?
- A) It prevents false positives from momentary passersby or doorway appearances *(Correct)*
- B) It replaces student IDs with biometric locks
- C) It requires students to stand still
- D) It only works on single video frames"""
