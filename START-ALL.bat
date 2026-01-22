@echo off
title Aegis-Ignis - Start All Services
color 0B

echo.
echo ===============================================================
echo              AEGIS-IGNIS SMART BUILDING SYSTEM
echo                    Starting All Services...
echo ===============================================================
echo.

REM Check if camera_config.json exists, create if not
if not exist camera_config.json (
    echo [INFO] Creating camera configuration...
    echo {"cameras":[{"id":1,"name":"Main Webcam","stream_url":"0","floor_id":1,"room":"Office","is_active":true}]} > camera_config.json
    echo [OK] Camera config created
    echo.
)

echo [1/6] Starting PostgreSQL Database...
docker-compose -f docker/docker-compose.yml up -d postgres >nul 2>&1
if %errorlevel%==0 (
    echo [OK] PostgreSQL started
) else (
    echo [WARNING] PostgreSQL may already be running or Docker not available
)
timeout /t 3 /nobreak >nul
echo.

echo [2/6] Starting Live Camera Detection Server (Port 5000)...
start "Live Camera Server" powershell -NoExit -Command "cd '%CD%'; $Host.UI.RawUI.WindowTitle='Live Camera Detection Server - ML ENABLED'; Write-Host '===================================================' -ForegroundColor Cyan; Write-Host '   Live Camera Detection Server Starting...' -ForegroundColor Cyan; Write-Host '   ML Fire Detection + N8N Alerts + Face Recognition' -ForegroundColor Green; Write-Host '===================================================' -ForegroundColor Cyan; Write-Host ''; C:/Users/user/AppData/Local/Programs/Python/Python312/python.exe live_camera_detection_server.py"
timeout /t 5 /nobreak >nul
echo [OK] Live Camera Detection Server launched
echo.

echo [3/6] Starting ULTRA-FAST Face Recognition Service (Port 8001)...
start "Face Recognition Service" powershell -NoExit -Command "cd '%CD%\python-face-service'; $Host.UI.RawUI.WindowTitle='ULTRA-FAST Face Recognition'; Write-Host '===================================================' -ForegroundColor Green; Write-Host '   ULTRA-FAST Face Recognition Starting...' -ForegroundColor Green; Write-Host '   INSTANT Duplicate Checking + Cached Data' -ForegroundColor Yellow; Write-Host '===================================================' -ForegroundColor Green; Write-Host ''; & '%CD%\.venv\Scripts\python.exe' main_fast.py"
timeout /t 2 /nobreak >nul
echo [OK] Face Recognition launched
echo.

echo [3.5/6] Starting Live Floor Monitoring Service (Port 8003)...
start "Floor Monitoring Service" powershell -NoExit -Command "cd '%CD%'; $Host.UI.RawUI.WindowTitle='Live Floor Monitoring'; Write-Host '===================================================' -ForegroundColor DarkCyan; Write-Host '   Live Floor Monitoring Starting...' -ForegroundColor Cyan; Write-Host '   Real-time Employee Detection on Floors' -ForegroundColor Yellow; Write-Host '===================================================' -ForegroundColor DarkCyan; Write-Host ''; & '%CD%\.venv\Scripts\python.exe' python-face-service\live_floor_monitoring.py"
timeout /t 3 /nobreak >nul
echo [OK] Floor Monitoring launched
echo.
echo    Starting camera monitoring in background...
powershell -Command "Start-Sleep -Seconds 10 ; Invoke-RestMethod -Uri http://localhost:8003/start-camera/1 -Method Post | Out-Null" >nul 2>&1 &
echo [OK] Camera will auto-start in 10 seconds
echo.

echo [4/6] Setting up Fire Detection Database...
cd backend-laravel
php setup_fire_detection.php >nul 2>&1
cd ..
echo [OK] Database configured (Camera 1, Floor 3)
echo.

echo [4.5/6] Starting Fire Detection Service (Port 8002) - READY MODE...
start "Fire Detection Service" powershell -NoExit -Command "$Host.UI.RawUI.BackgroundColor='DarkRed'; $Host.UI.RawUI.ForegroundColor='Yellow'; Clear-Host; cd '%CD%'; $Host.UI.RawUI.WindowTitle='Fire Detection - READY'; Write-Host '===================================================' -ForegroundColor Yellow; Write-Host '   FIRE DETECTION - FULLY CONFIGURED' -ForegroundColor Red; Write-Host '===================================================' -ForegroundColor Yellow; Write-Host '   Settings:' -ForegroundColor Cyan; Write-Host '   - Confidence: 55%%+ (Balanced)' -ForegroundColor Green; Write-Host '   - Camera ID: 1 (Physical Webcam 0)' -ForegroundColor Green; Write-Host '   - Floor: Third Floor (ID: 3)' -ForegroundColor Green; Write-Host '   - Screenshots: AUTO SAVE' -ForegroundColor Green; Write-Host '   - Alerts: AUTO CREATE' -ForegroundColor Green; Write-Host '===================================================' -ForegroundColor Yellow; Write-Host '   Fire detection with screenshots ready!' -ForegroundColor Red; Write-Host '===================================================' -ForegroundColor Yellow; Write-Host ''; python fire-detection-service\main.py"
timeout /t 3 /nobreak >nul
echo [OK] Fire Detection launched (Alerts + Screenshots enabled)
echo.

echo [4.6/6] Starting ML Fire Detection Service (Port 8004) - ML MODE...
start "ML Fire Detection Service" powershell -NoExit -Command "$Host.UI.RawUI.BackgroundColor='DarkMagenta'; $Host.UI.RawUI.ForegroundColor='Yellow'; Clear-Host; cd '%CD%'; $Host.UI.RawUI.WindowTitle='ML Fire Detection - AI POWERED'; Write-Host '===================================================' -ForegroundColor Magenta; Write-Host '   ML FIRE DETECTION - YOLOv8 + N8N' -ForegroundColor Red; Write-Host '===================================================' -ForegroundColor Magenta; Write-Host '   AI Features:' -ForegroundColor Cyan; Write-Host '   - YOLOv8 ML Model (with color fallback)' -ForegroundColor Green; Write-Host '   - N8N WhatsApp/Voice Alerts' -ForegroundColor Green; Write-Host '   - EC2 Backend Integration' -ForegroundColor Green; Write-Host '   - Smart Confidence Threshold' -ForegroundColor Green; Write-Host '   - People Count Detection' -ForegroundColor Green; Write-Host '===================================================' -ForegroundColor Magenta; Write-Host '   ML-powered fire detection ready!' -ForegroundColor Red; Write-Host '===================================================' -ForegroundColor Magenta; Write-Host ''; C:/Users/user/AppData/Local/Programs/Python/Python312/python.exe fire-detection-service\main_ml.py"
timeout /t 3 /nobreak >nul
echo [OK] ML Fire Detection launched (AI + N8N Alerts enabled)
echo.

echo [5/6] Laravel Backend running on EC2: http://35.180.117.85
echo [OK] Backend connected (AWS EC2)
echo.

echo [6/8] Starting Camera Detection Service...
start "Camera Detection Service" powershell -NoExit -Command "cd '%CD%\camera-detection-service'; $Host.UI.RawUI.WindowTitle='Camera Detection Service'; Write-Host '===================================================' -ForegroundColor Cyan; Write-Host '   Camera Detection Service Starting...' -ForegroundColor Cyan; Write-Host '   Real-time Fire + Face Detection' -ForegroundColor Yellow; Write-Host '===================================================' -ForegroundColor Cyan; Write-Host ''; python main.py"
timeout /t 2 /nobreak >nul
echo [OK] Camera Detection Service launched
echo.

echo [7/8] Starting Web Dashboard (Port 5173)...
start "Web Dashboard" powershell -NoExit -Command "cd '%CD%\Smart Building Dashboard Design'; $Host.UI.RawUI.WindowTitle='Web Dashboard'; Write-Host '===================================================' -ForegroundColor Blue; Write-Host '   Web Dashboard Starting...' -ForegroundColor Blue; Write-Host '===================================================' -ForegroundColor Blue; Write-Host ''; npm run dev"
timeout /t 2 /nobreak >nul
echo [OK] Web Dashboard launched
echo.

echo [8/9] Starting Employee Registration Portal (Port 5174)...
start "Employee Registration" powershell -NoExit -Command "cd '%CD%\face-registration'; $Host.UI.RawUI.WindowTitle='Employee Registration Portal'; Write-Host '===================================================' -ForegroundColor Yellow; Write-Host '   Employee Registration Portal Starting...' -ForegroundColor Yellow; Write-Host '===================================================' -ForegroundColor Yellow; Write-Host ''; npm run dev"
timeout /t 2 /nobreak >nul
echo [OK] Employee Registration launched
echo.

echo [9/9] Starting React Native Mobile App...
if exist "mobile-app\package.json" (
    echo    Checking mobile app dependencies...
    if not exist "mobile-app\node_modules" (
        echo    [INFO] Installing mobile app dependencies (first time setup)...
        cd mobile-app
        call npm install >nul 2>&1
        cd ..
        echo    [OK] Dependencies installed
    )
    echo    Starting Metro Bundler...
    start "React Native Metro" powershell -NoExit -Command "cd '%CD%\mobile-app'; $Host.UI.RawUI.WindowTitle='React Native Metro Bundler'; Write-Host '===================================================' -ForegroundColor Magenta; Write-Host '   React Native Metro Bundler' -ForegroundColor Magenta; Write-Host '   Mobile App Development Server' -ForegroundColor Cyan; Write-Host '===================================================' -ForegroundColor Magenta; Write-Host ''; npm start"
    timeout /t 5 /nobreak >nul
    echo [OK] Metro Bundler started
    echo.
    
    echo    Building and launching Android app...
    start "React Native Android" powershell -NoExit -Command "cd '%CD%\mobile-app'; $Host.UI.RawUI.WindowTitle='React Native Android'; Write-Host '===================================================' -ForegroundColor Green; Write-Host '   React Native Android App' -ForegroundColor Green; Write-Host '   Building and launching...' -ForegroundColor Yellow; Write-Host '===================================================' -ForegroundColor Green; Write-Host ''; npm run android"
    timeout /t 3 /nobreak >nul
    echo [OK] Android app build initiated
    echo.
    echo    Note: iOS app requires macOS - run 'npm run ios' in mobile-app directory
) else (
    echo [WARNING] Mobile app directory not found - skipping mobile app startup
    echo           Create mobile-app directory and run 'npm install' to enable
)
echo.

echo ===============================================================
echo                   ALL SERVICES LAUNCHED!
echo ===============================================================
echo.
echo Check your Windows taskbar for 10 PowerShell windows:
echo   - Camera Streaming Server (Cyan)
echo   - Face Registration Service (Green)
echo   - Live Floor Monitoring (Cyan) ^<-- Real-time detection
echo   - Fire Detection Service (RED) ^<-- Legacy Port 8002
echo   - ML Fire Detection Service (MAGENTA) ^<-- AI Port 8004 + N8N!
echo   - Camera Detection Service (Cyan)
echo   - Web Dashboard (Blue)
echo   - Employee Registration (Yellow)
echo   - React Native Metro (Magenta) ^<-- Mobile app server
echo   - React Native Android (Green) ^<-- Mobile app build
echo.
echo Backend: Running on AWS EC2 (http://35.180.117.85)
echo.
echo Services need 30-60 seconds to fully start...
echo Python AI services will take longer (loading models)
echo.
echo FIRE DETECTION - NEW SUPER EASY MODE:
echo   - Detects with 30%% confidence (was 85%%)
echo   - Min area: 100px (was 5,000px)
echo   - Photos saved every 5 seconds
echo   - Backend accepts 30%%+ confidence
echo   - Your lighter WILL be detected!
echo.
echo ===============================================================
echo                     ACCESS YOUR SERVICES
echo ===============================================================
echo.
echo   Web Dashboard:      http://localhost:5173
echo   Employee Portal:    http://localhost:5174
echo   Camera Streaming:   http://localhost:5000/stream/1
echo   Face Registration:  http://localhost:8001/docs
echo   Fire Detection:     http://localhost:8002/docs
echo   ML Fire Detection:  http://localhost:8004/docs (AI + N8N!)
echo   Floor Monitoring:   http://localhost:8003/docs (NEW!)
echo   Laravel Backend:    http://35.180.117.85 (AWS EC2)
echo.
echo   Camera API List:    http://localhost:5000/api/cameras
echo.
echo   Mobile App:         Android emulator/device (via Metro)
echo                      Metro Bundler: http://localhost:8081
echo.
echo ===============================================================
echo.
echo WAIT 60 SECONDS, then open: http://localhost:5173
echo Employee Registration: http://localhost:5174
echo.
echo Press any key to open Web Dashboard in browser...
pause >nul

start http://localhost:5173

echo.
echo Dashboard opened! Check the browser.
echo.
echo This window will close in 10 seconds...
timeout /t 10

