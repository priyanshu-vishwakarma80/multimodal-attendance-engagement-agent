/**
 * Chart.js controller for Session Analytics & Engagement Dynamics.
 */

document.addEventListener("DOMContentLoaded", function() {
    initAnalyticsCharts();
});

function initAnalyticsCharts() {
    // 1. Timeline Chart
    const ctxTimeline = document.getElementById("timelineChart");
    if (ctxTimeline) {
        // Sample timeline points representing session evolution
        const timeLabels = ["00:00", "02:00", "04:00", "06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"];
        const compositeData = [85, 88, 84, 82, 79, 75, 42, 68, 86, 89, 84]; // Notice attention drop at 12:00 recovered to 86
        const poseData = [88, 90, 85, 84, 78, 72, 38, 70, 88, 92, 85];
        const movementData = [80, 82, 80, 78, 76, 74, 45, 65, 82, 84, 80];
        const audioData = [84, 88, 86, 82, 84, 80, 48, 72, 88, 88, 86];

        new Chart(ctxTimeline, {
            type: "line",
            data: {
                labels: timeLabels,
                datasets: [
                    {
                        label: "Composite Engagement",
                        data: compositeData,
                        borderColor: "#f59e0b",
                        backgroundColor: "rgba(245, 158, 11, 0.15)",
                        borderWidth: 3,
                        fill: true,
                        tension: 0.35,
                        pointRadius: 4
                    },
                    {
                        label: "Head Pose Score",
                        data: poseData,
                        borderColor: "#06b6d4",
                        borderWidth: 2,
                        borderDash: [4, 4],
                        tension: 0.3,
                        pointRadius: 2
                    },
                    {
                        label: "Movement Activity",
                        data: movementData,
                        borderColor: "#10b981",
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 2
                    },
                    {
                        label: "Audio Interaction",
                        data: audioData,
                        borderColor: "#3b82f6",
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "top",
                        labels: { color: "#94a3b8", boxWidth: 14 }
                    },
                    tooltip: {
                        mode: "index",
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#64748b" }
                    },
                    y: {
                        min: 0,
                        max: 100,
                        grid: { color: "rgba(255, 255, 255, 0.05)" },
                        ticks: { color: "#64748b" }
                    }
                }
            }
        });
    }

    // 2. Interaction Mode Doughnut Chart
    const ctxMode = document.getElementById("modeDoughnutChart");
    if (ctxMode) {
        new Chart(ctxMode, {
            type: "doughnut",
            data: {
                labels: ["Guided Instruction (55%)", "Active Discussion (30%)", "Independent Silence (15%)"],
                datasets: [{
                    data: [55, 30, 15],
                    backgroundColor: ["#3b82f6", "#10b981", "#64748b"],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: "#94a3b8", boxWidth: 12, padding: 15 }
                    }
                },
                cutout: "65%"
            }
        });
    }
}
