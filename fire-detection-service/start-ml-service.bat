@echo off
title ML Fire Detection Service - Port 8002
color 0C

echo.
echo ===============================================================
echo        ML FIRE DETECTION SERVICE WITH N8N ALERTS
echo ===============================================================
echo.
echo   Starting ML-powered fire detection on PORT 8004...
echo   - YOLOv8 ML detection with color fallback
echo   - N8N WhatsApp/Voice alerts
echo   - EC2 Laravel backend integration
echo   - Auto screenshot capture
echo.
echo   Note: Your existing service runs on port 8002
echo         This ML service runs on port 8004
echo.
echo ===============================================================
echo.

cd /d "%~dp0"

REM Use the correct Python path
C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe main_ml.py

pause
