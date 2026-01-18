@echo off
echo ========================================
echo  LIVE FLOOR MONITORING SERVICE
echo ========================================
echo.
echo Starting live face detection for floor monitoring...
echo Service will run on http://localhost:8002
echo.

cd python-face-service

echo Activating Python environment...
call venv\Scripts\activate.bat

echo.
echo Starting live monitoring service...
python live_floor_monitoring.py

pause
