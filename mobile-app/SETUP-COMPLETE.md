# Complete Setup Guide - Android & iOS

## Current Issues to Fix

Your errors show:
- ❌ `adb` not recognized → Android SDK not in PATH
- ❌ `java` not recognized → Java not in PATH  
- ❌ No emulators found → Need to create emulator
- ❌ `JAVA_HOME` not set → Need to set environment variable

## Quick Fix: Automated Setup (Recommended)

### Option 1: Automatic PATH Setup (Easiest)

1. **Right-click PowerShell → Run as Administrator**
2. Navigate to mobile-app folder:
   ```powershell
   cd "C:\Users\user\OneDrive\Desktop\Aegis-IgnisGit\mobile-app"
   ```
3. Run the setup script:
   ```powershell
   .\SETUP-PATH.ps1
   ```
4. **Close ALL terminal windows**
5. Open a NEW terminal
6. Test:
   ```bash
   adb devices
   java -version
   ```

### Option 2: Manual PATH Setup

If automatic setup doesn't work, do it manually:

1. **Press `Win + X` → System**
2. **Advanced system settings → Environment Variables**
3. Under **System variables**, find **Path** → **Edit**
4. Click **New** and add these paths (one at a time):
   ```
   C:\Users\user\AppData\Local\Android\Sdk\platform-tools
   C:\Users\user\AppData\Local\Android\Sdk\emulator
   C:\Program Files\Android\Android Studio\jbr\bin
   ```
5. Click **New** under **System variables** (not Path) to create:
   - Variable name: `JAVA_HOME`
   - Variable value: `C:\Program Files\Android\Android Studio\jbr`
6. Click **OK** on all dialogs
7. **Close ALL terminals and reopen**

## Step 2: Create Android Emulator

1. **Open Android Studio**
2. **Tools → Device Manager**
3. Click **Create Device** (or **+ Create Device**)
4. Select: **Phone → Pixel 5** (or Pixel 6, Pixel 7)
5. Click **Next**
6. Download **API 33** or **API 34** (click Download if needed)
7. Click **Next → Finish**
8. **Start the emulator** (click Play button ▶️)
9. Wait 1-2 minutes for it to boot

## Step 3: Verify Setup

Run the verification script:
```bash
cd mobile-app
VERIFY-SETUP.bat
```

Or test manually:
```bash
# Should show your emulator
adb devices

# Should list emulators
emulator -list-avds

# Should show Java version
java -version

# Should show Gradle version
cd android
.\gradlew.bat --version
```

## Step 4: Run Android App

```bash
cd mobile-app
npm run android
```

The app should build and launch on your emulator!

---

## iOS Setup (macOS Only)

**Note:** iOS development requires macOS. If you're on Windows, you can only develop for Android.

### Prerequisites for iOS

1. **macOS** (required - iOS development doesn't work on Windows)
2. **Xcode 14+** (download from App Store)
3. **CocoaPods** (install with: `sudo gem install cocoapods`)

### iOS Setup Steps

1. **Install Xcode:**
   - Open App Store
   - Search "Xcode"
   - Install (takes 10-15 minutes, ~10GB)

2. **Install CocoaPods:**
   ```bash
   sudo gem install cocoapods
   ```

3. **Install iOS Dependencies:**
   ```bash
   cd mobile-app/ios
   pod install
   cd ..
   ```

4. **Open iOS Simulator:**
   - Open Xcode
   - **Xcode → Open Developer Tool → Simulator**
   - Or run: `open -a Simulator`

5. **Run iOS App:**
   ```bash
   cd mobile-app
   npm run ios
   ```

### iOS Troubleshooting

**"pod install fails"**
- Make sure CocoaPods is installed: `pod --version`
- Try: `cd ios && pod deintegrate && pod install`

**"No simulators found"**
- Open Xcode → Preferences → Components
- Download iOS simulators

**"Build fails"**
- Clean build: `cd ios && xcodebuild clean`
- Reinstall pods: `pod install`

---

## Running Both Versions

### Android (Windows/macOS/Linux)

```bash
cd mobile-app
npm run android
```

### iOS (macOS Only)

```bash
cd mobile-app
npm run ios
```

### Both at Once (macOS)

Open two terminals:

**Terminal 1:**
```bash
cd mobile-app
npm start
```

**Terminal 2:**
```bash
cd mobile-app
npm run android  # In one terminal
npm run ios      # In another terminal (or same terminal after Android)
```

---

## Quick Reference

### Android Commands
```bash
npm run android          # Build and run Android app
npm run start           # Start Metro bundler
adb devices              # List connected devices
emulator -list-avds     # List emulators
```

### iOS Commands (macOS)
```bash
npm run ios              # Build and run iOS app
npm run start           # Start Metro bundler
xcrun simctl list       # List simulators
```

### Verification
```bash
npx react-native doctor # Check React Native setup
VERIFY-SETUP.bat        # Check Android setup (Windows)
```

---

## Summary

**For Android (Windows):**
1. ✅ Run `SETUP-PATH.ps1` as Administrator
2. ✅ Create emulator in Android Studio
3. ✅ Restart terminal
4. ✅ Run `npm run android`

**For iOS (macOS):**
1. ✅ Install Xcode from App Store
2. ✅ Install CocoaPods
3. ✅ Run `pod install` in `ios/` folder
4. ✅ Open Simulator
5. ✅ Run `npm run ios`

---

## Still Having Issues?

1. **Restart your computer** after adding to PATH
2. **Close ALL terminals** and open new ones
3. Run: `npx react-native doctor` to diagnose issues
4. Check: `VERIFY-SETUP.bat` for Android setup status
