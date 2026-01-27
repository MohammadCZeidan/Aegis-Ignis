@echo off
echo ================================================================
echo     Verifying Android Development Setup
echo ================================================================
echo.

echo [1] Checking Gradle Wrapper...
cd /d "%~dp0\android"
if exist "gradle\wrapper\gradle-wrapper.jar" (
    echo [OK] gradle-wrapper.jar exists
) else (
    echo [ERROR] gradle-wrapper.jar missing
    echo Location: android\gradle\wrapper\gradle-wrapper.jar
)

if exist "gradlew.bat" (
    echo [OK] gradlew.bat exists
) else (
    echo [ERROR] gradlew.bat missing
)
echo.

echo [2] Checking Java...
where java >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Java found in PATH
    java -version
) else (
    echo [WARNING] Java not found in PATH
    echo.
    echo SOLUTION: Install Android Studio
    echo Android Studio includes Java JDK
    echo After installation, Java will be available
)
echo.

echo [3] Checking Android SDK (ADB)...
where adb >nul 2>&1
if %errorlevel%==0 (
    echo [OK] ADB found in PATH
    adb --version
) else (
    echo [WARNING] ADB not found in PATH
    echo.
    echo SOLUTION: Install Android Studio
    echo After installation, add Android SDK to PATH:
    echo   C:\Users\%USERNAME%\AppData\Local\Android\Sdk\platform-tools
)
echo.

echo [4] Checking for Android Emulators...
where emulator >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Emulator command found
    emulator -list-avds
) else (
    echo [WARNING] Emulator command not found
    echo.
    echo SOLUTION: Install Android Studio and create an emulator
)
echo.

echo ================================================================
echo                      Summary
echo ================================================================
echo.
echo Current Status:
echo   Gradle Wrapper: Checked above
echo   Java: Will be available after Android Studio installation
echo   Android SDK: Will be available after Android Studio installation
echo   Emulator: Create in Android Studio Device Manager
echo.
echo Next Steps:
echo   1. Install Android Studio (if not installed)
echo   2. Open Android Studio
echo   3. Create an emulator (Tools ^> Device Manager)
echo   4. Start the emulator
echo   5. Add Android SDK to PATH (see INSTALL-ANDROID-STUDIO.md)
echo   6. Restart terminal
echo   7. Run: npm run android
echo.
pause
