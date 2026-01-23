@echo off
echo ================================================================
echo     Setting up Android Project Structure
echo ================================================================
echo.

cd /d "%~dp0\android"

echo [1] Downloading Gradle Wrapper JAR...
if not exist "gradle\wrapper\gradle-wrapper.jar" (
    echo Downloading gradle-wrapper.jar...
    powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/gradle/gradle/v8.3.0/gradle/wrapper/gradle-wrapper.jar' -OutFile 'gradle\wrapper\gradle-wrapper.jar'"
    if %errorlevel%==0 (
        echo [OK] Gradle wrapper JAR downloaded
    ) else (
        echo [WARNING] Could not download automatically
        echo Please download manually from:
        echo https://raw.githubusercontent.com/gradle/gradle/v8.3.0/gradle/wrapper/gradle-wrapper.jar
        echo Save to: gradle\wrapper\gradle-wrapper.jar
    )
) else (
    echo [OK] Gradle wrapper JAR already exists
)
echo.

echo [2] Checking gradlew.bat...
if exist "gradlew.bat" (
    echo [OK] gradlew.bat exists
) else (
    echo [ERROR] gradlew.bat missing - should have been created
)
echo.

echo [3] Checking Android SDK setup...
where adb >nul 2>&1
if %errorlevel%==0 (
    echo [OK] ADB found in PATH
    adb --version
) else (
    echo [ERROR] ADB not found
    echo.
    echo SOLUTION: Install Android Studio
    echo 1. Download: https://developer.android.com/studio
    echo 2. Install Android Studio
    echo 3. Add Android SDK to PATH:
    echo    C:\Users\%USERNAME%\AppData\Local\Android\Sdk\platform-tools
    echo.
)
echo.

echo [4] Checking for Java...
where java >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Java found
    java -version
) else (
    echo [WARNING] Java not found in PATH
    echo Android Studio includes Java, or install JDK 17+
)
echo.

echo ================================================================
echo                      Next Steps
echo ================================================================
echo.
echo 1. Install Android Studio (if not installed)
echo 2. Create an emulator in Android Studio Device Manager
echo 3. Start the emulator
echo 4. Run: npm run android
echo.
echo OR connect a physical Android device with USB debugging enabled
echo.
pause
