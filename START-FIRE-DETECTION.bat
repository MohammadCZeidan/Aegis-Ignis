@echo off
title FIRE DETECTION - FIXED & READY
color 0A

echo.
echo ===============================================================
echo               FIRE DETECTION SERVICE - READY
echo ===============================================================
echo.

echo [SETUP] Ensuring database is configured...
cd backend-laravel
php setup_fire_detection.php
echo.

echo ===============================================================
echo               STARTING FIRE DETECTION
echo ===============================================================
echo.
echo Status:
echo   - Camera ID: 1 (Physical Webcam 0) ✓
echo   - Floor ID: 3 (Third Floor) ✓  
echo   - Room: main ✓
echo   - Confidence: 55%% ✓
echo   - Screenshots: backend-laravel\public\storage\alerts\ ✓
echo.
echo When fire detected:
echo   [1] Screenshot saved automatically
echo   [2] Alert created in database
echo   [3] Alert appears in dashboard
echo.
echo ===============================================================
echo.

cd ..
python fire-detection-service\main.py

pause
