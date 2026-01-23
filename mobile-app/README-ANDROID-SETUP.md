# Android Setup - Complete Guide

## Current Problem

You're seeing these errors:
- ❌ `'adb' is not recognized` - Android SDK not in PATH
- ❌ `'gradlew.bat' is not recognized` - Gradle wrapper missing
- ❌ `No emulators found` - No Android emulator configured

## Solution: Install Android Studio (Recommended)

**This fixes ALL issues at once!**

### Step 1: Install Android Studio
1. Download: https://developer.android.com/studio
2. Run installer
3. Follow installation wizard
4. **Important:** Make sure "Android SDK" and "Android Emulator" are selected

### Step 2: Create Emulator
1. Open Android Studio
2. **Tools → Device Manager**
3. Click **Create Device** (or **+ Create Device**)
4. Select: **Phone → Pixel 5** (or Pixel 6, etc.)
5. Click **Next**
6. Download **API 33** or **API 34** (click Download if needed)
7. Click **Next → Finish**

### Step 3: Start Emulator
1. In Device Manager, find your emulator
2. Click **Play** button (▶️)
3. Wait 1-2 minutes for first boot
4. You'll see Android home screen

### Step 4: Add to PATH (Important!)

1. **Find SDK Location:**
   - Open Android Studio
   - **File → Settings → Appearance & Behavior → System Settings → Android SDK**
   - Copy the "Android SDK Location" path
   - Usually: `C:\Users\YourName\AppData\Local\Android\Sdk`

2. **Add to System PATH:**
   - Press `Win + X` → **System**
   - Click **Advanced system settings**
   - Click **Environment Variables**
   - Under **System variables**, find **Path**, click **Edit**
   - Click **New** and add:
     ```
     C:\Users\YourName\AppData\Local\Android\Sdk\platform-tools
     C:\Users\YourName\AppData\Local\Android\Sdk\emulator
     ```
   - Replace `YourName` with your actual username
   - Click **OK** on all dialogs

3. **Restart Terminal:**
   - Close ALL terminal windows
   - Open a NEW terminal
   - Test: `adb devices` should work now

### Step 5: Run Your App

```bash
cd mobile-app
npm run android
```

## Alternative: Use Physical Device

If you have an Android phone:

1. **Enable USB Debugging:**
   - Settings → About Phone
   - Tap "Build Number" 7 times
   - Go back → Developer Options
   - Enable "USB Debugging"

2. **Connect Phone:**
   - Connect via USB cable
   - Accept "Allow USB Debugging" on phone

3. **Verify:**
   ```bash
   adb devices
   ```
   Should show your device

4. **Run App:**
   ```bash
   cd mobile-app
   npm run android
   ```

## Fix Gradle Wrapper

I've created `gradlew.bat`, but you also need `gradle-wrapper.jar`:

**Option 1: Download manually**
1. Download: https://raw.githubusercontent.com/gradle/gradle/v8.3.0/gradle/wrapper/gradle-wrapper.jar
2. Save to: `mobile-app/android/gradle/wrapper/gradle-wrapper.jar`

**Option 2: Use setup script**
```bash
cd mobile-app
setup-android-project.bat
```

## Verify Everything Works

After setup, test:

```bash
# Check ADB
adb devices

# Check emulators
emulator -list-avds

# Check Java
java -version

# Check Gradle
cd mobile-app/android
.\gradlew.bat --version
```

All should work if Android Studio is properly installed!

## Quick Checklist

- [ ] Android Studio installed
- [ ] Android SDK installed (comes with Android Studio)
- [ ] Emulator created in Device Manager
- [ ] Emulator started and running
- [ ] Android SDK added to PATH
- [ ] Terminal restarted after PATH change
- [ ] `adb devices` works
- [ ] `gradlew.bat` exists in `android/` folder
- [ ] `gradle-wrapper.jar` exists in `android/gradle/wrapper/`

## Still Having Issues?

1. **Restart your computer** after installing Android Studio
2. **Close and reopen** all terminals
3. Make sure Android Studio is fully installed
4. Try creating a new emulator
5. Run: `npx react-native doctor` to check setup

## What Android Studio Provides

- ✅ Android SDK (includes ADB)
- ✅ Android Emulator
- ✅ Gradle build tools
- ✅ Java JDK
- ✅ All React Native Android requirements

**Bottom line:** Install Android Studio - it's the easiest solution!
