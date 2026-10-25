/**
 * Main application client script.
 * Handles top navigation clock, UI enhancements, and shared utilities.
 */

document.addEventListener("DOMContentLoaded", function() {
    // Live Clock in Navbar
    function updateLiveClock() {
        const clockEl = document.getElementById("liveClock");
        if (clockEl) {
            const now = new Date();
            clockEl.textContent = now.toLocaleTimeString();
        }
    }
    updateLiveClock();
    setInterval(updateLiveClock, 1000);
});
