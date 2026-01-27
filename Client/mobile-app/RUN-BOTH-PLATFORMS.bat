@echo off
echo ================================================================
echo     Aegis Ignis - Run Both Android and iOS
echo ================================================================
echo.

cd mobile-app

echo [1/2] Starting Android app...
start "React Native Android" powershell -NoExit -Command "cd '%CD%'; $Host.UI.RawUI.WindowTitle='React Native Android'; Write-Host '===================================================' -ForegroundColor Green; Write-Host '   React Native Android App' -ForegroundColor Green; Write-Host '===================================================' -ForegroundColor Green; Write-Host ''; npm run android"
timeout /t 3 /nobreak >nul
echo [OK] Android app starting...
echo.

REM Check if macOS is available for iOS
powershell -Command "if (Test-Path '/usr/bin/sw_vers' -or (Get-Command 'xcodebuild' -ErrorAction SilentlyContinue)) { exit 0 } else { exit 1 }" >nul 2>&1
if %errorlevel%==0 (
    echo [2/2] Starting iOS app (macOS detected)...
    start "React Native iOS" powershell -NoExit -Command "cd '%CD%'; $Host.UI.RawUI.WindowTitle='React Native iOS'; Write-Host '===================================================' -ForegroundColor Blue; Write-Host '   React Native iOS App' -ForegroundColor Blue; Write-Host '===================================================' -ForegroundColor Blue; Write-Host ''; npm run ios"
    timeout /t 3 /nobreak >nul
    echo [OK] iOS app starting...
    echo.
    echo Both Android and iOS apps are launching!
) else (
    echo [2/2] iOS app skipped (macOS required)
    echo.
    echo [INFO] You are on Windows - iOS development requires macOS
    echo        Android app is running. For iOS, use a Mac computer.
    echo.
    echo        See SETUP-COMPLETE.md for iOS setup instructions.
)
echo.
echo ================================================================
echo     Apps Launching
echo ================================================================
echo.
echo Android: Check the Android emulator window
if %errorlevel%==0 (
    echo iOS: Check the iOS Simulator window
)
echo.
pause
