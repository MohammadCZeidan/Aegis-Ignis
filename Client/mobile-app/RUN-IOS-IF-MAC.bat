@echo off
echo ================================================================
echo     Running iOS App (macOS Detection)
echo ================================================================
echo.

REM Check if macOS is available
powershell -Command "if (Test-Path '/usr/bin/sw_vers' -or (Get-Command 'xcodebuild' -ErrorAction SilentlyContinue)) { exit 0 } else { exit 1 }" >nul 2>&1
if %errorlevel%==0 (
    echo [OK] macOS detected - Starting iOS app...
    echo.
    cd mobile-app
    call npm run ios
) else (
    echo [ERROR] macOS not detected!
    echo.
    echo iOS development requires macOS.
    echo.
    echo You are currently on Windows.
    echo.
    echo To run iOS app:
    echo   1. Use a Mac computer
    echo   2. Install Xcode from App Store
    echo   3. Install CocoaPods: sudo gem install cocoapods
    echo   4. Run: cd mobile-app/ios && pod install
    echo   5. Run: npm run ios
    echo.
    echo For more details, see: SETUP-COMPLETE.md
    echo.
)
pause
