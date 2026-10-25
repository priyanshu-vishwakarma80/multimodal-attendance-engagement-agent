@echo off
echo ========================================================
echo   Push to GitHub - Multimodal Attendance & Engagement Agent
echo ========================================================
echo.

set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/multimodal-agent.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL provided. Exiting.
    pause
    exit /b 1
)

echo.
echo [1/3] Setting remote origin...
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%

echo [2/3] Renaming branch to main...
git branch -M main

echo [3/3] Pushing commits to GitHub...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo  SUCCESS! Your code has been pushed to GitHub.
    echo  Now you can copy this repository link into SkillWallet!
    echo ========================================================
) else (
    echo.
    echo [ERROR] Push failed. Please check your credentials or repo permissions.
)

pause
