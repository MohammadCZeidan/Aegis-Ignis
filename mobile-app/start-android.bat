@echo off
echo Starting Aegis Ignis Mobile App for Android...
echo.

cd /d "%~dp0"

echo [1/2] Starting Metro bundler...
start "Metro Bundler" cmd /k "npm start"

timeout /t 5 /nobreak >nul

echo [2/2] Building and launching Android app...
call npm run android

echo.
echo App should launch on Android emulator or connected device.
echo.
pause
