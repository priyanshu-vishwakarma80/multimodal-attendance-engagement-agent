@echo off
echo ========================================================
echo   Pushing code to:
echo   https://github.com/priyanshu-vishwakarma80/multimodal-attendance-engagement-agent.git
echo ========================================================
echo.

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================================
    echo  SUCCESS! Your project is pushed to GitHub!
    echo ========================================================
) else (
    echo.
    echo If prompted, please click 'Sign in with your browser' to authorize GitHub.
)

pause
