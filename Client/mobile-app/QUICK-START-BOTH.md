# Quick Start - Android & iOS

## 🚀 Get Both Platforms Running

### Step 1: Fix Android Setup (Do This First!)

**Windows Users:**

1. **Run the diagnostic:**
   ```bash
   cd mobile-app
   npm run fix-android
   # Or: FIX-ANDROID-NOW.bat
   ```

2. **Fix PATH automatically (Recommended):**
   - Right-click PowerShell → **Run as Administrator**
   - Navigate to mobile-app folder
   - Run: `.\SETUP-PATH.ps1`
   - **Close ALL terminals**
   - Open a NEW terminal

3. **Or fix PATH manually:**
   - See `SETUP-COMPLETE.md` for manual instructions

4. **Create Android Emulator:**
   - Open Android Studio
   - **Tools → Device Manager**
   - **Create Device → Pixel 5 → API 33**
   - Start the emulator (click Play ▶️)

5. **Verify setup:**
   ```bash
   cd mobile-app
   npm run verify
   # Or: VERIFY-SETUP.bat
   ```

### Step 2: Run Android App

```bash
cd mobile-app
npm run android
```

**That's it!** The app should launch on your Android emulator.

---

## 🍎 iOS Setup (macOS Only)

**Note:** iOS development requires macOS. If you're on Windows, skip this section.

### Step 1: Install Xcode

1. Open **App Store**
2. Search "Xcode"
3. Click **Install** (takes 10-15 minutes, ~10GB)

### Step 2: Install CocoaPods

```bash
sudo gem install cocoapods
```

### Step 3: Install iOS Dependencies

```bash
cd mobile-app/ios
pod install
cd ..
```

### Step 4: Open iOS Simulator

```bash
# Option 1: From command line
open -a Simulator

# Option 2: From Xcode
# Xcode → Open Developer Tool → Simulator
```

### Step 5: Run iOS App

```bash
cd mobile-app
npm run ios
```

**That's it!** The app should launch on your iOS simulator.

---

## 🎯 Running Both Platforms

### Option 1: Sequential (One at a Time)

**Terminal 1:**
```bash
cd mobile-app
npm start
```

**Terminal 2 (Android):**
```bash
cd mobile-app
npm run android
```

**Terminal 3 (iOS - macOS only):**
```bash
cd mobile-app
npm run ios
```

### Option 2: Use Helper Scripts

**Windows:**
```bash
RUN-BOTH.bat
```

**macOS:**
```bash
./RUN-BOTH.sh  # (if created)
```

---

## ✅ Verification Checklist

### Android (Windows/macOS/Linux)

- [ ] Android Studio installed
- [ ] Android SDK in PATH (`adb devices` works)
- [ ] Java in PATH (`java -version` works)
- [ ] JAVA_HOME set (check with `echo %JAVA_HOME%`)
- [ ] Emulator created and running
- [ ] `npm run android` works

### iOS (macOS Only)

- [ ] macOS operating system
- [ ] Xcode installed from App Store
- [ ] CocoaPods installed (`pod --version`)
- [ ] iOS dependencies installed (`pod install` in `ios/` folder)
- [ ] Simulator available (`xcrun simctl list`)
- [ ] `npm run ios` works

---

## 🔧 Troubleshooting

### Android Issues

**"adb not recognized"**
- Run `npm run fix-android` to diagnose
- Run `SETUP-PATH.ps1` as Administrator
- Restart terminal

**"java not found"**
- Same as above - PATH issue
- Java is included with Android Studio

**"No emulators found"**
- Create emulator in Android Studio Device Manager
- Start the emulator before running app

**"JAVA_HOME not set"**
- Run `SETUP-PATH.ps1` as Administrator
- Or set manually: `C:\Program Files\Android\Android Studio\jbr`

### iOS Issues (macOS)

**"pod install fails"**
- Update CocoaPods: `sudo gem install cocoapods`
- Try: `cd ios && pod deintegrate && pod install`

**"No simulators found"**
- Open Xcode → Preferences → Components
- Download iOS simulators

**"Build fails"**
- Clean: `cd ios && xcodebuild clean`
- Reinstall pods: `pod install`

---

## 📚 More Help

- **Complete Setup Guide:** `SETUP-COMPLETE.md`
- **Android Setup:** `INSTALL-ANDROID-STUDIO.md`
- **iOS Setup:** See `SETUP-COMPLETE.md` iOS section
- **Verify Setup:** `npm run verify` or `VERIFY-SETUP.bat`
- **React Native Doctor:** `npm run doctor`

---

## 🎉 Success!

Once both platforms are set up:

- **Android:** `npm run android`
- **iOS:** `npm run ios`

Both apps connect to the same backend API (configured in `.env` file).
