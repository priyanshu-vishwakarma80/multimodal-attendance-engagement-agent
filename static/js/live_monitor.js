/**
 * Live Classroom Monitor JavaScript Controller.
 * Handles telemetry polling, sustained presence table updates,
 * AI suggestion alerts, and Web Speech API Text-to-Speech.
 */

let audioAlertsEnabled = true;
let currentSuggestionText = "";

document.addEventListener("DOMContentLoaded", function() {
    initLiveTelemetryPolling();
    initControls();
});

function initControls() {
    // Audio notice toggle
    const toggleBtn = document.getElementById("toggleAudioNoticeBtn");
    const statusText = document.getElementById("audioNoticeStatus");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", function() {
            audioAlertsEnabled = !audioAlertsEnabled;
            statusText.textContent = audioAlertsEnabled ? "ON" : "OFF";
            toggleBtn.classList.toggle("btn-outline-info", audioAlertsEnabled);
            toggleBtn.classList.toggle("btn-outline-secondary", !audioAlertsEnabled);
        });
    }

    // Play/Speak Suggestion button
    const speakBtn = document.getElementById("speakSuggestionBtn");
    if (speakBtn) {
        speakBtn.addEventListener("click", function() {
            if (currentSuggestionText) {
                speakText(currentSuggestionText);
            }
        });
    }

    // Manual Tip Request button
    const tipBtn = document.getElementById("manualTipBtn");
    if (tipBtn) {
        tipBtn.addEventListener("click", async function() {
            tipBtn.disabled = true;
            tipBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> Formulating...';
            try {
                const res = await fetch("/api/suggestions/generate_manual", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({category: "ATTENTION_DROP"})
                });
                const data = await res.json();
                if (data.success) {
                    updateAiSuggestionCard(data.category, data.suggestion, data.source);
                    if (audioAlertsEnabled) {
                        speakText(data.suggestion);
                    }
                }
            } catch (e) {
                console.error("Manual tip request failed", e);
            } finally {
                tipBtn.disabled = false;
                tipBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles me-1"></i> Request AI Teaching Tip';
            }
        });
    }
}

function initLiveTelemetryPolling() {
    setInterval(fetchLiveTelemetry, 1500);
    fetchLiveTelemetry();
}

async function fetchLiveTelemetry() {
    try {
        const response = await fetch("/api/telemetry/live");
        if (!response.ok) return;
        const data = await response.json();

        // 1. Update Timer
        const sessionTimer = document.getElementById("sessionTimer");
        if (sessionTimer && data.elapsed_seconds !== undefined) {
            const mins = Math.floor(data.elapsed_seconds / 60).toString().padStart(2, '0');
            const secs = Math.floor(data.elapsed_seconds % 60).toString().padStart(2, '0');
            sessionTimer.textContent = `${mins}:${secs}`;
        }

        // 2. Update Composite Gauge
        if (data.evaluation) {
            const evalData = data.evaluation;
            const scoreDisplay = document.getElementById("compositeScoreDisplay");
            const progressBar = document.getElementById("compositeProgressBar");
            const badge = document.getElementById("engagementBadge");

            if (scoreDisplay) scoreDisplay.textContent = `${evalData.composite_score}%`;
            if (progressBar) {
                progressBar.style.width = `${evalData.composite_score}%`;
                progressBar.className = `progress-bar progress-bar-striped progress-bar-animated bg-${evalData.badge_color}`;
            }
            if (badge) {
                badge.textContent = evalData.engagement_level;
                badge.className = `badge bg-${evalData.badge_color}`;
            }

            // Signal Breakdown
            const poseEl = document.getElementById("metricPose");
            const moveEl = document.getElementById("metricMovement");
            const audioEl = document.getElementById("metricAudio");
            const modeEl = document.getElementById("metricInteractionMode");

            if (poseEl) poseEl.textContent = `${evalData.avg_pose}%`;
            if (moveEl) moveEl.textContent = `${evalData.avg_movement}%`;
            if (audioEl) audioEl.textContent = `${evalData.audio_score}%`;
            if (modeEl) modeEl.textContent = evalData.interaction_mode;

            // Tracked Count
            const trackedBadge = document.getElementById("activeTrackedCount");
            if (trackedBadge) {
                trackedBadge.textContent = `${evalData.students_detected} Detected (${evalData.students_present} Present)`;
            }
        }

        // 3. Update Student Sustained Presence Table
        if (data.students && data.students.length > 0) {
            const tbody = document.getElementById("studentPresenceTbody");
            if (tbody) {
                let html = "";
                data.students.forEach(s => {
                    let statusBadgeClass = "bg-secondary";
                    if (s.status.includes("Present")) statusBadgeClass = "bg-success";
                    else if (s.status === "Tardy") statusBadgeClass = "bg-warning";
                    else if (s.status.includes("Pending")) statusBadgeClass = "bg-primary";

                    html += `
                    <tr>
                        <td class="fw-semibold">
                            <div class="d-flex align-items-center gap-1">
                                <span class="small">${s.name}</span>
                            </div>
                        </td>
                        <td><span class="badge ${statusBadgeClass}">${s.status}</span></td>
                        <td class="font-monospace text-info">${s.presence_seconds}s</td>
                    </tr>
                    `;
                });
                tbody.innerHTML = html;
            }
        }

        // 4. Handle Auto AI Suggestions
        if (data.auto_suggestion) {
            const sug = data.auto_suggestion;
            updateAiSuggestionCard(sug.category, sug.text, sug.source);
            if (audioAlertsEnabled) {
                speakText(sug.text);
            }
        }

    } catch (err) {
        console.warn("Telemetry fetch error:", err);
    }
}

function updateAiSuggestionCard(category, text, source) {
    currentSuggestionText = text;
    const catEl = document.getElementById("suggestionCategory");
    const textEl = document.getElementById("suggestionText");
    const sourceEl = document.getElementById("suggestionSource");
    const timeEl = document.getElementById("suggestionTimestamp");

    if (catEl) catEl.textContent = category || "Instructional Intervention";
    if (textEl) textEl.textContent = text;
    if (sourceEl) sourceEl.textContent = source || "Agent";
    if (timeEl) timeEl.textContent = `Triggered at ${new Date().toLocaleTimeString()}`;

    // Visual highlight pulse on the card
    const box = document.getElementById("aiSuggestionBox");
    if (box) {
        box.classList.add("border-warning");
        setTimeout(() => box.classList.remove("border-warning"), 2000);
    }
}

function speakText(text) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel(); // Stop prior audio
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.05;
    window.speechSynthesis.speak(utterance);
}
