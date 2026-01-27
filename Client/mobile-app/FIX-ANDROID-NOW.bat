@echo off
echo ================================================================
echo     Quick Fix: Android Development Environment
echo ================================================================
echo.

echo [1] Checking current setup...
echo.

where adb >nul 2>&1
if %errorlevel%==0 (
    echo [OK] ADB found in PATH
    adb --version
) else (
    echo [ERROR] ADB not found in PATH
    echo.
    echo SOLUTION: Add Android SDK to PATH
    echo.
    echo Option 1: Automatic (Recommended)
    echo   1. Right-click PowerShell
    echo   2. Run as Administrator
    echo   3. Run: .\SETUP-PATH.ps1
    echo.
    echo Option 2: Manual
    echo   1. Press Win + X -^> System
    echo   2. Advanced system settings -^> Environment Variables
    echo   3. Add to Path:
    echo      C:\Users\user\AppData\Local\Android\Sdk\platform-tools
    echo      C:\Users\user\AppData\Local\Android\Sdk\emulator
    echo   4. Add JAVA_HOME:
    echo      C:\Program Files\Android\Android Studio\jbr
    echo   5. Restart terminal
    echo.
)

echo.
where java >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Java found in PATH
    java -version
) else (
    echo [ERROR] Java not found in PATH
    echo.
    echo SOLUTION: Add Java to PATH
    echo   Add to Path: C:\Program Files\Android\Android Studio\jbr\bin
    echo   Set JAVA_HOME: C:\Program Files\Android\Android Studio\jbr
    echo.
)

echo.
where emulator >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Emulator command found
    echo.
    echo Available emulators:
    emulator -list-avds
    echo.
    if %errorlevel% neq 0 (
        echo [WARNING] No emulators found
        echo.
        echo SOLUTION: Create emulator in Android Studio
        echo   1. Open Android Studio
        echo   2. Tools -^> Device Manager
        echo   3. Create Device -^> Pixel 5 -^> API 33
        echo   4. Start emulator
        echo.
    )
) else (
    echo [ERROR] Emulator command not found
    echo.
    echo SOLUTION: Add Android SDK emulator to PATH
    echo   Add to Path: C:\Users\user\AppData\Local\Android\Sdk\emulator
    echo.
)

echo.
echo ================================================================
echo     Next Steps
echo ================================================================
echo.
echo 1. Fix PATH issues (see solutions above)
echo 2. Create emulator in Android Studio (if none exist)
echo 3. Restart terminal
echo 4. Run: npm run android
echo.
echo For detailed setup, see: SETUP-COMPLETE.md
echo.
pause
