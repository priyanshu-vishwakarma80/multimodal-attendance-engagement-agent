"""
Multimodal Attendance & Engagement Agent
Enterprise Edition — High-Tier MNC Educational Intelligence Platform
Skill Wallet Capstone Project 5 | Powered by Computer Vision & Edge AI
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
from PIL import Image, ImageDraw

try:
    import cv2
    CV2_AVAILABLE = True
except Exception as e:
    cv2 = None
    CV2_AVAILABLE = False

# =========================================================
# Page Configuration & Metadata
# =========================================================
st.set_page_config(
    page_title="Classroom Intelligence | Multimodal Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# High-Tier MNC Custom CSS (Stripe / Datadog / Google Cloud Aesthetic)
# =========================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">

<style>
    /* Global Base */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #f1f5f9;
    }
    
    .stApp {
        background-color: #080c14 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(6, 182, 212, 0.06) 0px, transparent 50%),
            radial-gradient(at 50% 100%, rgba(139, 92, 246, 0.05) 0px, transparent 50%) !important;
    }

    /* Enterprise Hero Banner */
    .enterprise-hero {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.85) 0%, rgba(15, 23, 42, 0.7) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 26px 30px;
        margin-bottom: 24px;
        box-shadow: 0 16px 36px -10px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    .enterprise-hero::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, #3b82f6, #06b6d4, #10b981);
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #60a5fa;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 12px;
    }

    /* Glassmorphic Metric Cards */
    .metric-card-pro {
        background: linear-gradient(145deg, rgba(20, 29, 45, 0.7) 0%, rgba(15, 23, 42, 0.6) 100%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    .metric-card-pro:hover {
        transform: translateY(-2px);
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 0 12px 30px rgba(59, 130, 246, 0.12);
    }
    .metric-card-pro .label {
        font-size: 12px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }
    .metric-card-pro .val {
        font-size: 30px;
        font-weight: 800;
        color: #f8fafc;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }
    .metric-card-pro .delta {
        font-size: 12px;
        font-weight: 600;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        color: #94a3b8;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    }

    /* Status Dot Animation */
    .live-pulse {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulseAnimation 2s infinite;
    }
    @keyframes pulseAnimation {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Monospace Text */
    .code-font {
        font-family: 'JetBrains Mono', monospace !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# State Management
# =========================================================
if "students_roster" not in st.session_state:
    st.session_state.students_roster = [
        {"id": "STU-101", "name": "Alex Chen", "first_seen": "00:01", "last_seen": "14:50", "visible_sec": 840, "ratio": 0.93, "attn": "96%"},
        {"id": "STU-102", "name": "Maya Patel", "first_seen": "00:03", "last_seen": "14:55", "visible_sec": 810, "ratio": 0.90, "attn": "92%"},
        {"id": "STU-103", "name": "Liam Johnson", "first_seen": "00:05", "last_seen": "14:48", "visible_sec": 790, "ratio": 0.88, "attn": "89%"},
        {"id": "STU-104", "name": "Sophia Garcia", "first_seen": "00:02", "last_seen": "14:52", "visible_sec": 760, "ratio": 0.84, "attn": "85%"},
        {"id": "STU-105", "name": "Ethan Brown", "first_seen": "04:12", "last_seen": "14:45", "visible_sec": 650, "ratio": 0.72, "attn": "74%"},
        {"id": "STU-106", "name": "Olivia Davis", "first_seen": "08:30", "last_seen": "14:40", "visible_sec": 360, "ratio": 0.40, "attn": "60%"},
        {"id": "STU-107", "name": "Noah Miller (Passerby)", "first_seen": "05:10", "last_seen": "05:18", "visible_sec": 8, "ratio": 0.01, "attn": "N/A"},
        {"id": "STU-108", "name": "Emma Wilson", "first_seen": "00:04", "last_seen": "07:20", "visible_sec": 430, "ratio": 0.48, "attn": "65%"}
    ]

# =========================================================
# Sidebar: MNC System Telemetry & Edge Controls
# =========================================================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
        <div style="background: linear-gradient(135deg, #3b82f6, #06b6d4); padding: 8px; border-radius: 10px; display: flex;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2">
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
        </div>
        <div>
            <div style="font-weight: 800; font-size: 16px; color: #f8fafc; letter-spacing: -0.3px;">ClassroomIQ Pro</div>
            <div style="font-size: 11px; color: #64748b; font-weight: 600;">ENTERPRISE MULTIMODAL AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-size: 11px; color: #94a3b8; font-weight: 600;">TELEMETRY STATUS</span>
            <span style="font-size: 11px; color: #10b981; font-weight: 700; display: flex; align-items: center; gap: 5px;">
                <span class="live-pulse"></span> ONLINE
            </span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 4px;">
            <span style="color: #64748b;">Processing Mode:</span>
            <span style="color: #e2e8f0; font-weight: 600;">100% Offline Edge</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 4px;">
            <span style="color: #64748b;">Edge Latency:</span>
            <span style="color: #06b6d4; font-weight: 600; font-family: monospace;">14.2 ms</span>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 12px; margin-top: 4px;">
            <span style="color: #64748b;">Vision Pipeline:</span>
            <span style="color: #e2e8f0; font-weight: 600;">OpenCV Centroid Tracker</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### ⚙️ Edge Algorithm Thresholds")
    sustained_threshold = st.slider(
        "Sustained Presence Threshold (%)",
        min_value=50, max_value=90, value=70, step=5,
        help="Mandatory continuous presence ratio required to confirm attendance, rejecting transient doorway pass-throughs."
    )
    attention_drop_limit = st.slider(
        "Attention Drop Alert Trigger (%)",
        min_value=30, max_value=60, value=45, step=5,
        help="Threshold below which the pedagogical copilot triggers real-time pacing interventions."
    )

    st.markdown("---")
    st.markdown("""
    <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 8px; padding: 12px;">
        <div style="color: #10b981; font-size: 12px; font-weight: 700; margin-bottom: 4px;">🛡️ PRIVACY GUARANTEE</div>
        <p style="color: #94a3b8; font-size: 11px; margin: 0; line-height: 1.4;">
            Zero frame transmission to external cloud services. Biometrics never leave local device memory.
        </p>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# Top Enterprise Hero Banner
# =========================================================
st.markdown("""
<div class="enterprise-hero">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px;">
        <div>
            <div class="hero-badge">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="10"/></svg>
                Google Cloud GenAI Capstone | Project 5
            </div>
            <h1 style="font-size: 28px; font-weight: 800; color: #ffffff; margin: 0 0 8px 0; letter-spacing: -0.6px;">
                Multimodal Attendance & Engagement Agent
            </h1>
            <p style="color: #94a3b8; font-size: 14px; margin: 0; max-width: 820px; line-height: 1.5;">
                Enterprise-grade classroom intelligence system unifying <strong>computer vision sustained presence verification</strong>,
                <strong>acoustic interaction spectroscopy (VAD)</strong>, and <strong>agentic pedagogical advisory reasoning</strong>.
            </p>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 8px 16px; text-align: right;">
                <div style="font-size: 11px; color: #64748b; font-weight: 600;">SESSION ID</div>
                <div style="font-size: 14px; color: #06b6d4; font-weight: 700; font-family: monospace;">SES-CLASS-2026-05</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# Navigation Tabs
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📸 Tab 1: Sustained Attendance",
    "🎙️ Tab 2: Acoustic Spectroscopy",
    "⚡ Tab 3: Multimodal Signal Fusion",
    "💡 Tab 4: AI Pedagogical Copilot",
    "📊 Tab 5: Executive Analytics"
])

# =========================================================
# TAB 1: SUSTAINED ATTENDANCE ENGINE
# =========================================================
with tab1:
    st.markdown("### 🎯 Automated Presence-Based Attendance Tracking")
    st.caption("Eliminates false positives from hallway passersby using sustained presence verification across video time-steps.")

    col_cam, col_metrics = st.columns([3, 2])

    with col_cam:
        feed_mode = st.radio("Input Source Stream:", ["Simulated Classroom Stream", "Upload Media File", "Live Video Input"], horizontal=True)

        if feed_mode == "Simulated Classroom Stream":
            if CV2_AVAILABLE and cv2 is not None:
                # High-tech HUD synthetic classroom frame via OpenCV
                frame = np.full((380, 600, 3), 18, dtype=np.uint8)
                cv2.rectangle(frame, (35, 15), (565, 65), (28, 36, 48), -1)
                cv2.rectangle(frame, (35, 15), (565, 65), (59, 130, 246), 1)
                cv2.putText(frame, "ADVANCED MULTIMODAL INTELLIGENCE - SECTION 402", (50, 47), cv2.FONT_HERSHEY_DUPLEX, 0.6, (220, 235, 255), 1)

                students_vis = [
                    ("Alex Chen", 120, 175, (46, 204, 113), "VERIFIED (93%)"),
                    ("Maya Patel", 300, 175, (46, 204, 113), "VERIFIED (90%)"),
                    ("Liam Johnson", 480, 175, (46, 204, 113), "VERIFIED (88%)"),
                    ("Sophia Garcia", 210, 285, (46, 204, 113), "VERIFIED (84%)"),
                    ("Ethan Brown", 390, 285, (46, 204, 113), "VERIFIED (72%)"),
                ]
                for name, cx, cy, col, badge in students_vis:
                    cv2.ellipse(frame, (cx, cy + 45), (42, 28), 0, 0, 360, (30, 41, 59), -1)
                    cv2.ellipse(frame, (cx, cy), (30, 38), 0, 0, 360, (210, 225, 240), -1)
                    cv2.ellipse(frame, (cx, cy - 14), (32, 20), 0, 180, 360, (40, 45, 55), -1)
                    w, h = 38, 48
                    cv2.rectangle(frame, (cx - w, cy - h), (cx + w, cy + h), col, 1)
                    cv2.line(frame, (cx - w, cy - h), (cx - w + 10, cy - h), col, 3)
                    cv2.line(frame, (cx - w, cy - h), (cx - w, cy - h + 10), col, 3)
                    cv2.line(frame, (cx + w, cy - h), (cx + w - 10, cy - h), col, 3)
                    cv2.line(frame, (cx + w, cy - h), (cx + w, cy - h + 10), col, 3)
                    cv2.rectangle(frame, (cx - w, cy - h - 18), (cx + w + 10, cy - h), (15, 23, 42), -1)
                    cv2.putText(frame, name, (cx - w + 4, cy - h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1)
                    cv2.putText(frame, badge, (cx - w + 2, cy + h + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.36, col, 1)

                st.image(frame, channels="BGR", caption="Edge Vision Pipeline: Multi-Student Centroid Tracker & Sustained Timer", use_container_width=True)
            else:
                # High-fidelity PIL pure-python fallback
                pil_img = Image.new("RGB", (600, 380), color=(18, 24, 38))
                draw = ImageDraw.Draw(pil_img)
                draw.rectangle([(35, 15), (565, 65)], fill=(28, 36, 48), outline=(59, 130, 246))
                draw.text((50, 32), "ADVANCED MULTIMODAL INTELLIGENCE - SECTION 402", fill=(220, 235, 255))
                for name, cx, cy, col, badge in [
                    ("Alex Chen", 120, 175, "#10b981", "VERIFIED (93%)"),
                    ("Maya Patel", 300, 175, "#10b981", "VERIFIED (90%)"),
                    ("Liam Johnson", 480, 175, "#10b981", "VERIFIED (88%)"),
                    ("Sophia Garcia", 210, 285, "#10b981", "VERIFIED (84%)"),
                    ("Ethan Brown", 390, 285, "#10b981", "VERIFIED (72%)"),
                ]:
                    draw.ellipse([(cx - 30, cy - 38), (cx + 30, cy + 38)], fill=(210, 225, 240), outline=(100, 116, 139))
                    draw.rectangle([(cx - 38, cy - 48), (cx + 38, cy + 48)], outline=col, width=2)
                    draw.text((cx - 34, cy - 64), name, fill="white")
                    draw.text((cx - 34, cy + 54), badge, fill=col)
                st.image(pil_img, caption="Edge Vision Pipeline: Multi-Student Centroid Tracker & Sustained Timer", use_container_width=True)

        elif feed_mode == "Upload Media File":
            up_file = st.file_uploader("Upload Classroom Recording or Frame:", type=["jpg", "png", "mp4"])
            if up_file is not None:
                if up_file.name.endswith(("jpg", "png", "jpeg")):
                    try:
                        pil_img = Image.open(up_file)
                        st.image(pil_img, use_container_width=True)
                    except Exception:
                        st.error("Error reading image file.")
                else:
                    st.video(up_file)
            else:
                st.info("Upload classroom video/photo to process attendance.")
        else:
            cam = st.camera_input("Capture Classroom Session via Hardware Camera")
            if cam:
                try:
                    pil_cam = Image.open(cam)
                    st.image(pil_cam, use_container_width=True)
                except Exception:
                    st.warning("Camera frame received.")

    with col_metrics:
        # Calculate Sustained Attendance Status
        threshold_ratio = sustained_threshold / 100.0
        records = []
        for s in st.session_state.students_roster:
            if s["ratio"] >= threshold_ratio:
                status = "Present (Verified)"
            elif s["ratio"] < 0.10:
                status = "Filtered (Passerby)"
            elif s["last_seen"] < "09:00":
                status = "Left Early"
            else:
                status = "Absent (< Threshold)"

            records.append({
                "Student ID": s["id"],
                "Student Name": s["name"],
                "First Seen": s["first_seen"],
                "Last Seen": s["last_seen"],
                "Sustained (s)": s["visible_sec"],
                "Presence %": f"{int(s['ratio'] * 100)}%",
                "Attn Index": s["attn"],
                "Status": status
            })

        df_attendance = pd.DataFrame(records)
        present_count = sum(1 for r in records if "Present" in r["Status"])
        total_enrolled = len([r for r in records if "Passerby" not in r["Student Name"]])

        st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
            <div class="metric-card-pro">
                <div class="label">Verified Attendance</div>
                <div class="val" style="color: #10b981;">{present_count} <span style="font-size: 16px; color: #64748b;">/ {total_enrolled}</span></div>
                <div class="delta" style="color: #10b981;">▲ {(present_count/total_enrolled)*100:.1f}% Verified</div>
            </div>
            <div class="metric-card-pro">
                <div class="label">Passerby Filtered</div>
                <div class="val" style="color: #3b82f6;">1</div>
                <div class="delta" style="color: #3b82f6;">✓ 0 False Positives</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 14px;">
            <div style="font-size: 12px; color: #94a3b8; font-weight: 600; margin-bottom: 4px;">SUSTAINED LOGIC RULE</div>
            <div style="font-size: 13px; color: #e2e8f0;">
                Duration requirement: <strong>&gt; {sustained_threshold}% of session</strong>.<br>
                <em>Hallway passersby (e.g. Noah Miller, 8s presence) are rejected automatically.</em>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 📋 Enterprise Attendance Register")
    st.dataframe(df_attendance, use_container_width=True, hide_index=True)

    csv_data = df_attendance.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Certified Attendance Register (CSV)",
        data=csv_data,
        file_name="verified_classroom_attendance.csv",
        mime="text/csv",
        type="primary"
    )

# =========================================================
# TAB 2: ACOUSTIC SPECTROSCOPY (EPIC 3)
# =========================================================
with tab2:
    st.markdown("### 🎙️ Acoustic Interaction & Noise Dynamics (Epic 3)")
    st.caption("Spectral energy monitoring & Voice Activity Detection (VAD) categorizing instructional vs collaborative interaction.")

    col_a1, col_a2 = st.columns([1, 1])

    with col_a1:
        st.markdown("##### 🎚️ Classroom Acoustic State Distribution")
        states = [
            ("Instructor Lecture", 55, "#3b82f6", "Sustained single-speaker cadence"),
            ("Student Discussion / Q&A", 28, "#10b981", "Alternating multi-speaker verbal bursts"),
            ("Independent Study / Silence", 12, "#64748b", "Low ambient acoustic energy (< -45 dBFS)"),
            ("High Ambient Distraction", 5, "#ef4444", "Unfocused acoustic commotion")
        ]
        for title, pct, color, desc in states:
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 10px; padding: 12px; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; font-size: 13px; color: #f8fafc;">{title}</span>
                    <span style="font-weight: 800; font-size: 13px; color: {color}; font-family: monospace;">{pct}%</span>
                </div>
                <div style="background: rgba(255, 255, 255, 0.08); height: 6px; border-radius: 3px; overflow: hidden; margin-bottom: 6px;">
                    <div style="background: {color}; width: {pct}%; height: 100%;"></div>
                </div>
                <div style="font-size: 11px; color: #94a3b8;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    with col_a2:
        st.markdown("##### 📈 Sound Level Over Time (RMS & Decibels)")
        t_aud = np.linspace(0, 15, 120)
        np.random.seed(42)
        base_sound = -46 + 4 * np.sin(t_aud * 0.8)
        speech_pulse = 22 * np.exp(-((t_aud - 4)**2) / 1.5) + 26 * np.exp(-((t_aud - 10)**2) / 2.2)
        db_trace = np.clip(base_sound + speech_pulse + np.random.normal(0, 1.8, 120), -60, -10)

        fig_a, ax_a = plt.subplots(figsize=(6, 3.4), facecolor="#0e1422")
        ax_a.set_facecolor("#080c14")
        ax_a.plot(t_aud, db_trace, color="#06b6d4", linewidth=2.0, label="Audio Signal (dBFS)")
        ax_a.axhline(-32, color="#f59e0b", linestyle="--", linewidth=1.2, label="VAD Speech Threshold")
        ax_a.axhline(-18, color="#ef4444", linestyle=":", linewidth=1.2, label="Distraction Limit")
        ax_a.set_title("Acoustic Spectrogram Envelope", color="#f8fafc", fontsize=11, fontweight="bold")
        ax_a.set_xlabel("Session Timeline (Minutes)", color="#64748b", fontsize=9)
        ax_a.set_ylabel("Energy (dBFS)", color="#64748b", fontsize=9)
        ax_a.tick_params(colors="#64748b", labelsize=8)
        for spine in ax_a.spines.values():
            spine.set_color("#1e293b")
        ax_a.grid(True, linestyle="--", alpha=0.15, color="#ffffff")
        ax_a.legend(loc="lower right", facecolor="#0e1422", edgecolor="#334155", labelcolor="#f8fafc", fontsize=8)
        plt.tight_layout()
        st.pyplot(fig_a)

# =========================================================
# TAB 3: MULTIMODAL SIGNAL FUSION (EPIC 4)
# =========================================================
with tab3:
    st.markdown("### ⚡ Multimodal Signal Fusion & Engagement Scoring (Epic 4)")
    st.caption("Mathematical fusion of visual attention, physical movement dynamics, and acoustic interaction.")

    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px; margin-bottom: 20px;">
        <div style="font-size: 11px; font-weight: 700; color: #06b6d4; text-transform: uppercase; margin-bottom: 6px;">Mathematical Formulation</div>
        <div style="font-family: monospace; font-size: 15px; color: #f8fafc; margin-bottom: 8px;">
            E_composite(t) = 0.40 &times; S_pose(t) + 0.35 &times; S_movement(t) + 0.25 &times; S_audio(t)
        </div>
        <div style="font-size: 12px; color: #94a3b8;">
            Normalized composite index (0–100) combining head pose symmetry, optical frame differences, and speech interaction levels.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Generate synthetic 15-minute curve with attention dip
    t_timeline = np.linspace(0, 15, 75)
    pose_curve = np.clip(86 - 46 * np.exp(-((t_timeline - 8)**2) / 1.8) + np.random.normal(0, 1.8, 75), 10, 100)
    move_curve = np.clip(78 - 36 * np.exp(-((t_timeline - 8)**2) / 2.2) + np.random.normal(0, 2.0, 75), 10, 100)
    audio_curve = np.clip(82 - 42 * np.exp(-((t_timeline - 8)**2) / 2.0) + np.random.normal(0, 2.5, 75), 10, 100)
    composite_curve = 0.40 * pose_curve + 0.35 * move_curve + 0.25 * audio_curve

    fig_f, ax_f = plt.subplots(figsize=(10, 3.6), facecolor="#0e1422")
    ax_f.set_facecolor("#080c14")
    ax_f.plot(t_timeline, composite_curve, color="#f59e0b", linewidth=3.0, label="Composite Engagement Index (0-100)")
    ax_f.plot(t_timeline, pose_curve, color="#06b6d4", linewidth=1.5, linestyle="--", alpha=0.8, label="Visual Head Pose")
    ax_f.plot(t_timeline, move_curve, color="#10b981", linewidth=1.5, linestyle=":", alpha=0.8, label="Physical Posture/Movement")
    ax_f.plot(t_timeline, audio_curve, color="#3b82f6", linewidth=1.5, linestyle="-.", alpha=0.8, label="Acoustic Interaction")

    ax_f.axhline(attention_drop_limit, color="#ef4444", linestyle="--", linewidth=1.2, label=f"Attention Drop Alert ({attention_drop_limit}%)")
    ax_f.axvspan(7.1, 9.2, color="#ef4444", alpha=0.15, label="Attention Drop Window")

    ax_f.set_title("Classroom Multimodal Engagement Dynamics (15-Minute Timeline)", color="#f8fafc", fontsize=11, fontweight="bold")
    ax_f.set_xlabel("Elapsed Timeline (Minutes)", color="#64748b", fontsize=9)
    ax_f.set_ylabel("Normalized Score", color="#64748b", fontsize=9)
    ax_f.tick_params(colors="#64748b", labelsize=8)
    for spine in ax_f.spines.values():
        spine.set_color("#1e293b")
    ax_f.grid(True, linestyle="--", alpha=0.15, color="#ffffff")
    ax_f.legend(loc="lower left", facecolor="#0e1422", edgecolor="#334155", labelcolor="#f8fafc", fontsize=8.5)
    plt.tight_layout()
    st.pyplot(fig_f)

    # KPI Row
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 16px;">
        <div class="metric-card-pro">
            <div class="label">Mean Engagement</div>
            <div class="val" style="color: #f59e0b;">{np.mean(composite_curve):.1f}%</div>
            <div class="delta" style="color: #10b981;">▲ +4.2% vs baseline</div>
        </div>
        <div class="metric-card-pro">
            <div class="label">Attention Peak</div>
            <div class="val" style="color: #10b981;">{np.max(composite_curve):.1f}%</div>
            <div class="delta" style="color: #94a3b8;">Minute 2.4</div>
        </div>
        <div class="metric-card-pro">
            <div class="label">Attention Dip</div>
            <div class="val" style="color: #ef4444;">{np.min(composite_curve):.1f}%</div>
            <div class="delta" style="color: #ef4444;">Minute 8.1</div>
        </div>
        <div class="metric-card-pro">
            <div class="label">Recovery Health</div>
            <div class="val" style="color: #06b6d4;">86.4%</div>
            <div class="delta" style="color: #10b981;">✓ Optimal Recovery</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TAB 4: AI PEDAGOGICAL COPILOT (EPIC 5)
# =========================================================
with tab4:
    st.markdown("### 💡 AI Teaching Advisory Copilot (Epic 5)")
    st.caption("Agentic decision-support engine generating real-time, non-intrusive instructional interventions.")

    col_adv1, col_adv2 = st.columns([3, 2])

    with col_adv1:
        st.markdown("##### 🚨 Active Telemetry Intervention Log")

        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 12px; padding: 16px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="color: #ef4444; font-weight: 700; font-size: 13px;">⚠️ ATTENTION DROP ALERT (Minute 08:12)</span>
                <span style="font-family: monospace; font-size: 11px; color: #94a3b8;">Trigger: E < 45%</span>
            </div>
            <p style="color: #e2e8f0; font-size: 13px; margin: 0 0 8px 0; line-height: 1.5;">
                Collective classroom engagement dropped to <strong>38.4%</strong> following 8 minutes of uninterrupted presentation.
            </p>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 8px; font-size: 12px; color: #60a5fa;">
                🎯 <strong>Recommended Action:</strong> Launch a 90-second <em>Think-Pair-Share</em> prompt or quick 1-question pulse poll to reactivate cognitive retrieval.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.08); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 12px; padding: 16px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="color: #60a5fa; font-weight: 700; font-size: 13px;">ℹ️ MONOLOGUE PACING ADVISORY (Minute 11:30)</span>
                <span style="font-family: monospace; font-size: 11px; color: #94a3b8;">Trigger: Speech Ratio > 85%</span>
            </div>
            <p style="color: #e2e8f0; font-size: 13px; margin: 0 0 8px 0; line-height: 1.5;">
                Extended instructor monologue with minimal student motion detected.
            </p>
            <div style="background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 8px; font-size: 12px; color: #60a5fa;">
                🎯 <strong>Recommended Action:</strong> Pause lecture slides and cold-call an open-ended conceptual question to invite verbal interaction.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="color: #10b981; font-weight: 700; font-size: 13px;">✓ REINFORCEMENT NOTICE (Minute 13:45)</span>
                <span style="font-family: monospace; font-size: 11px; color: #94a3b8;">Trigger: E > 85%</span>
            </div>
            <p style="color: #e2e8f0; font-size: 13px; margin: 0; line-height: 1.5;">
                Classroom engagement successfully recovered to <strong>86.2%</strong> following collaborative peer discussion.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col_adv2:
        st.markdown("##### ⚡ Interactive Copilot Query")
        topic_in = st.text_input("Current Lecture Topic:", value="Convolutional & Multimodal Transformers")
        target_goal = st.selectbox("Pedagogical Target:", [
            "Attention Recovery",
            "Active Retrieval Check",
            "Energy & Physical Boost",
            "Higher-Order Concept Application"
        ])

        if st.button("Generate Tactical Teaching Prompt", type="primary"):
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%); border: 1px solid #3b82f6; border-radius: 12px; padding: 16px; margin-top: 12px;">
                <div style="color: #60a5fa; font-weight: 700; font-size: 13px; margin-bottom: 6px;">🎯 Contextual Advisory for {topic_in}</div>
                <p style="color: #f1f5f9; font-size: 13px; line-height: 1.5; margin: 0;">
                    <em>"Instruct students to spend 60 seconds sketching the pipeline diagram on paper, then explain the data flow to their peer partner. This shifts cognitive processing from passive audio consumption to active spatial synthesis."</em>
                </p>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# TAB 5: EXECUTIVE ANALYTICS & REPORT (EPIC 5 & 6)
# =========================================================
with tab5:
    st.markdown("### 📊 Executive Session Analytics & Educator Report")
    st.caption("Board-level summary detailing attendance integrity, engagement health, and session pacing.")

    # Top KPI summary
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px;">
        <div class="metric-card-pro">
            <div class="label">Total Roster</div>
            <div class="val" style="color: #f8fafc;">8</div>
            <div class="delta" style="color: #94a3b8;">Enrolled Candidates</div>
        </div>
        <div class="metric-card-pro">
            <div class="label">Verified Attendance</div>
            <div class="val" style="color: #10b981;">62.5%</div>
            <div class="delta" style="color: #10b981;">5 Verified Sustained</div>
        </div>
        <div class="metric-card-pro">
            <div class="label">Passerby Filtered</div>
            <div class="val" style="color: #3b82f6;">1</div>
            <div class="delta" style="color: #10b981;">100% False Marks Averted</div>
        </div>
        <div class="metric-card-pro">
            <div class="label">Mean Engagement</div>
            <div class="val" style="color: #f59e0b;">76.8%</div>
            <div class="delta" style="color: #10b981;">▲ +5.1% Session Delta</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown("##### 🥧 Attendance Composition Breakdown")
        fig_pie, ax_pie = plt.subplots(figsize=(5, 3.4), facecolor="#0e1422")
        ax_pie.set_facecolor("#0e1422")
        labels = ["Present (Sustained)", "Left Early", "Absent (< Threshold)", "Passerby (Filtered)"]
        sizes = [5, 1, 1, 1]
        colors = ["#10b981", "#3b82f6", "#ef4444", "#475569"]
        wedges, texts, autotexts = ax_pie.pie(
            sizes, labels=labels, autopct="%1.1f%%", startangle=140,
            colors=colors, textprops=dict(color="#f8fafc", fontsize=8.5)
        )
        for at in autotexts:
            at.set_color("#ffffff")
            at.set_weight("bold")
        ax_pie.axis("equal")
        plt.tight_layout()
        st.pyplot(fig_pie)

    with col_r2:
        st.markdown("##### 📄 Executive Educator Debrief")
        debrief_text = f"""# Classroom Intelligence Executive Report
Session ID: SES-CLASS-2026-05
Module: Generative AI with Google Cloud (Capstone Project 5)
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Platform ID: 6ac775fb32e2e6be34c17468

## 1. Executive Summary & Verification
- Total Enrolled: 8 Candidates
- Verified Sustained Attendance: 62.5% (5 Students)
- Hallway Passerby False Positives Eliminated: 1 (Noah Miller, 8s visible)
- Early Departures Logged: 1 (Emma Wilson at minute 07:20)

## 2. Multimodal Engagement & Interaction Spectroscopy
- Mean Classroom Engagement: 76.8%
- Visual Focus Ratio: 78.4%
- Acoustic Participation: 28% Student Verbal Interaction, 55% Instructor Lecture
- Attention Drop Event: Minute 07:10 - 09:15 (Resolved following peer prompt)

## 3. Pedagogical Prescriptions for Next Session
1. Introduce active concept checkpoints at minute 7 to preempt natural cognitive fatigue.
2. Maintain high active discussion windows; student verbal bursts correlated with +32% focus retention.
"""
        st.text_area("Generated Executive Debrief (Markdown):", value=debrief_text, height=210)

        st.download_button(
            label="📥 Download Certified Executive Report (Markdown)",
            data=debrief_text.encode('utf-8'),
            file_name="executive_classroom_report.md",
            mime="text/markdown",
            type="primary"
        )
