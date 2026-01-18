@echo off
echo ============================================
echo   Camera Detection Service
echo   Fire + Face Detection with 5-Min Tracking
echo ============================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Creating from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env with your camera settings, then run again.
    pause
    exit /b
)

echo Starting Camera Detection Service...
echo.
echo Service will:
echo   - Capture frames from camera
echo   - Detect fire (sends to port 8002)
echo   - Recognize faces (sends to port 8001)
echo   - Track presence for 5 minutes
echo   - Reset timer when person seen again
echo.

REM Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install dependencies if needed
if not exist "venv\" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Start service
echo.
echo === STARTING CAMERA SERVICE ===
echo Press Ctrl+C to stop
echo.
python main.py

pause
