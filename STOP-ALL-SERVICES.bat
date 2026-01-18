@echo off
title Stop All Services - Kill Runaway Processes
color 0C

echo.
echo ===============================================================
echo          STOPPING ALL AEGIS-IGNIS SERVICES
echo          Killing runaway Python processes...
echo ===============================================================
echo.

echo [1/3] Killing all Python processes...
taskkill /F /IM python.exe /T >nul 2>&1
if %errorlevel%==0 (
    echo [OK] All Python processes terminated
) else (
    echo [INFO] No Python processes found
)
timeout /t 2 /nobreak >nul

echo.
echo [2/3] Killing PHP/Laravel processes...
taskkill /F /IM php.exe /T >nul 2>&1
if %errorlevel%==0 (
    echo [OK] PHP processes terminated
) else (
    echo [INFO] No PHP processes found
)
timeout /t 1 /nobreak >nul

echo.
echo [3/3] Stopping Docker containers...
docker-compose -f docker/docker-compose.yml down >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Docker containers stopped
) else (
    echo [INFO] Docker containers already stopped or not running
)

echo.
echo ===============================================================
echo               ALL SERVICES STOPPED
echo ===============================================================
echo.
echo Memory cleanup complete. Safe to restart services.
echo.
pause
