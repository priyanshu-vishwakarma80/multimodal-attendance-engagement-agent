# PowerShell Startup Script for Multimodal Attendance & Engagement Agent
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Launching Multimodal Attendance & Engagement Agent" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

if (Get-Command py -ErrorAction SilentlyContinue) {
    py app.py
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    python app.py
} else {
    Write-Host "[ERROR] Python not found in PATH." -ForegroundColor Red
}
