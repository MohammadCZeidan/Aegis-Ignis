@echo off
echo ================================================================
echo     Aegis Ignis Mobile App - Run Both Platforms
echo ================================================================
echo.

echo [INFO] Checking platform...
if "%OS%"=="Windows_NT" (
    echo [OK] Windows detected - Android development supported
    echo [WARNING] iOS development requires macOS
    echo.
    echo Starting Android app...
    echo.
    call npm run android
) else (
    echo [OK] macOS/Linux detected
    echo.
    echo Choose platform:
    echo   1. Android
    echo   2. iOS
    echo   3. Both (requires two emulators/simulators)
    echo.
    set /p choice="Enter choice (1-3): "
    
    if "%choice%"=="1" (
        call npm run android
    ) else if "%choice%"=="2" (
        call npm run ios
    ) else if "%choice%"=="3" (
        echo Starting Android...
        start "Android" cmd /k "npm run android"
        timeout /t 3 /nobreak >nul
        echo Starting iOS...
        call npm run ios
    ) else (
        echo Invalid choice. Starting Android by default...
        call npm run android
    )
)

pause
