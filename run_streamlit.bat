@echo off
echo ========================================================
echo  Launching Streamlit Multimodal Attendance & Engagement Agent
echo ========================================================
echo.

start "" "http://localhost:8501"
py -m streamlit run streamlit_app.py --server.headless true --server.port 8501

pause
