@echo off
echo ========================================================
echo  Launching Multimodal Attendance & Engagement Agent
echo ========================================================
echo.

REM Verify Python Launcher
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python Launcher detected.
    py app.py
) else (
    echo [INFO] Falling back to python command...
    python app.py
)

pause
