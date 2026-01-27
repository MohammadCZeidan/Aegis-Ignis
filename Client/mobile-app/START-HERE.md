# 🚀 START HERE - Android & iOS Setup

## Current Status

You're seeing these errors:
- ❌ `adb` not recognized → Need to add Android SDK to PATH
- ❌ `java` not recognized → Need to add Java to PATH
- ❌ `JAVA_HOME` not set → Need to set environment variable
- ❌ No emulators found → Need to create emulator

## ⚡ Quick Fix (5 Minutes)

### Step 1: Fix PATH Automatically

1. **Right-click PowerShell → Run as Administrator**
2. Navigate to mobile-app:
   ```powershell
   cd "C:\Users\user\OneDrive\Desktop\Aegis-IgnisGit\Client\mobile-app"
   ```
3. Run the setup script:
   ```powershell
   .\SETUP-PATH.ps1
   ```
4. **Close ALL terminal windows**
5. Open a NEW terminal

### Step 2: Create Android Emulator

1. Open **Android Studio**
2. **Tools → Device Manager**
3. Click **Create Device** (or **+ Create Device**)
4. Select: **Phone → Pixel 5**
5. Click **Next**
6. Download **API 33** (click Download if needed)
7. Click **Next → Finish**
8. **Start the emulator** (click Play button ▶️)

### Step 3: Run Android App

```bash
cd mobile-app
npm run android
```

**Done!** Your Android app should launch! 🎉

---

## 🍎 iOS Setup (macOS Only)

**Note:** iOS development requires macOS. If you're on Windows, you can only develop for Android.

### Quick iOS Setup

1. **Install Xcode** from App Store (10-15 minutes)
2. **Install CocoaPods:**
   ```bash
   sudo gem install cocoapods
   ```
3. **Install iOS dependencies:**
   ```bash
   cd mobile-app/ios
   pod install
   cd ..
   ```
4. **Open Simulator:**
   ```bash
   open -a Simulator
   ```
5. **Run iOS app:**
   ```bash
   cd mobile-app
   npm run ios
   ```

**Done!** Your iOS app should launch! 🎉

---

## 📋 What I Created For You

### Setup Scripts

1. **`SETUP-PATH.ps1`** - Automatically fixes PATH (run as Administrator)
2. **`FIX-ANDROID-NOW.bat`** - Diagnoses Android setup issues
3. **`VERIFY-SETUP.bat`** - Verifies your setup is correct
4. **`RUN-BOTH.bat`** - Helper to run both platforms

### Documentation

1. **`SETUP-COMPLETE.md`** - Complete setup guide for both platforms
2. **`QUICK-START-BOTH.md`** - Quick reference for running both
3. **`INSTALL-ANDROID-STUDIO.md`** - Detailed Android Studio setup
4. **`START-HERE.md`** - This file (quick start)

---

## 🎯 Next Steps

### For Android (Windows)

1. ✅ Run `SETUP-PATH.ps1` as Administrator
2. ✅ Create emulator in Android Studio
3. ✅ Restart terminal
4. ✅ Run `npm run android`

### For iOS (macOS)

1. ✅ Install Xcode from App Store
2. ✅ Install CocoaPods
3. ✅ Run `pod install` in `ios/` folder
4. ✅ Open Simulator
5. ✅ Run `npm run ios`

---

## 🔍 Verify Everything Works

### Android

```bash
# Check ADB
adb devices

# Check Java
java -version

# Check emulators
emulator -list-avds

# Run verification script
npm run verify
```

### iOS (macOS)

```bash
# Check simulators
xcrun simctl list

# Check CocoaPods
pod --version

# Run React Native doctor
npm run doctor
```

---

## ❓ Still Having Issues?

1. **Run diagnostics:**
   ```bash
   npm run fix-android    # Diagnose Android issues
   npm run verify         # Verify setup
   npm run doctor         # React Native doctor
   ```

2. **Check documentation:**
   - `SETUP-COMPLETE.md` - Complete guide
   - `QUICK-START-BOTH.md` - Quick reference
   - `INSTALL-ANDROID-STUDIO.md` - Android Studio setup

3. **Common fixes:**
   - Restart computer after PATH changes
   - Close ALL terminals and reopen
   - Make sure emulator/simulator is running before `npm run android/ios`

---

## 🎉 Success Checklist

- [ ] Android SDK in PATH (`adb devices` works)
- [ ] Java in PATH (`java -version` works)
- [ ] JAVA_HOME set
- [ ] Android emulator created and running
- [ ] `npm run android` works
- [ ] (macOS only) Xcode installed
- [ ] (macOS only) CocoaPods installed
- [ ] (macOS only) `npm run ios` works

Once all checked, you're ready to develop for both platforms! 🚀
