# Aegis Ignis Mobile App

React Native mobile application for the Aegis Ignis smart building security system.

## Quick Setup

**Having issues?** See **[SETUP-COMPLETE.md](SETUP-COMPLETE.md)** for complete setup instructions.

**Quick Fix for Android:**
1. Run `FIX-ANDROID-NOW.bat` to diagnose issues
2. Run `SETUP-PATH.ps1` as Administrator to fix PATH
3. Create emulator in Android Studio
4. Run `npm run android`

## Prerequisites

### For Android Development
- Node.js 18+
- Java Development Kit (JDK) 17 (included with Android Studio)
- Android Studio
- Android SDK (API level 23+)
- Android Emulator or physical device

### For iOS Development
- **macOS** (required - iOS development doesn't work on Windows)
- Xcode 14+
- CocoaPods
- iOS Simulator or physical device

## Installation

1. **Install dependencies:**
```bash
cd mobile-app
npm install
```

2. **For iOS, install CocoaPods:**
```bash
cd ios
pod install
cd ..
```

3. **Configure API endpoints:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - The `.env` file is already configured with EC2 backend: `http://35.180.117.85/api/v1`
   - To use local backend instead, edit `.env` and uncomment the local URLs
   - **Note**: The `.env` file is git-ignored and will NOT be committed

## Running the App

### Quick Start (Easiest)

**Windows - Android:**
```bash
# Double-click or run:
npm run android
# Or use the batch file:
RUN-ANDROID.bat
```

**macOS - iOS:**
```bash
npm run ios
# Or use the shell script:
./RUN-IOS.sh
```

**Run Both Platforms (macOS only):**
```bash
# Option 1: Run both sequentially
npm run android
npm run ios

# Option 2: Use the helper script
RUN-BOTH.bat  # or ./RUN-BOTH.sh on macOS
```

### Manual Steps

#### Step 1: Start Metro Bundler (Terminal 1)

```bash
cd mobile-app
npm start
```

Wait until you see: `info Dev server ready`

#### Step 2: Run on Device (Terminal 2 - NEW WINDOW)

**For Android:**
```bash
cd mobile-app
npm run android
```

**For iOS (macOS only):**
```bash
cd mobile-app
npm run ios
```

### Alternative: Using IDEs

**Android Studio:**
- Open `mobile-app/android/` folder in Android Studio
- Wait for Gradle sync
- Click Run button (green play icon)

**Xcode (iOS):**
- Open `mobile-app/ios/AegisIgnis.xcworkspace` in Xcode
- Select a simulator or device
- Click Run button (play icon)

## Project Structure

```
mobile-app/
├── android/          # Android native code
├── ios/              # iOS native code
├── src/
│   ├── config/       # API configuration
│   ├── services/     # API services
│   └── screens/      # App screens
├── App.tsx           # Main app component
├── index.js          # Entry point
└── package.json      # Dependencies
```

## Features

- **Dashboard**: Overview of floors, alerts, and system status
- **Alerts**: View and manage fire detection alerts
- **Floors**: Monitor floor occupancy in real-time
- **Cameras**: Manage and view camera feeds
- **Settings**: App configuration and logout

## Troubleshooting

### Android Issues

**"adb not recognized" or "java not found":**
- Run `FIX-ANDROID-NOW.bat` to diagnose
- Run `SETUP-PATH.ps1` as Administrator to fix PATH automatically
- Or manually add to PATH (see `SETUP-COMPLETE.md`)

**"No emulators found":**
- Open Android Studio → Tools → Device Manager
- Create Device → Pixel 5 → API 33
- Start the emulator

**"JAVA_HOME not set":**
- Run `SETUP-PATH.ps1` as Administrator
- Or set JAVA_HOME manually: `C:\Program Files\Android\Android Studio\jbr`

**Metro bundler not connecting:**
- Check that port 8081 is not in use
- Run `adb reverse tcp:8081 tcp:8081`

**Build errors:**
- Clean build: `cd android && .\gradlew.bat clean`
- Delete `node_modules` and reinstall
- Run `VERIFY-SETUP.bat` to check setup

### iOS Issues

**Pod install errors:**
- Update CocoaPods: `sudo gem install cocoapods`
- Clean pods: `cd ios && rm -rf Pods Podfile.lock && pod install`

**Build errors:**
- Clean build folder in Xcode: Product → Clean Build Folder
- Delete DerivedData

### API Connection Issues

**Cannot connect to backend:**
- Default: Uses EC2 backend (`http://35.180.117.85/api/v1`) from `.env` file
- To use local backend: Edit `.env` file and uncomment local URLs
- Android Emulator: Use `10.0.2.2` instead of `localhost` in `.env`
- iOS Simulator: Use `localhost` in `.env`
- Physical device: Use your computer's IP address in `.env` (e.g., `192.168.1.100`)

**Environment Variables:**
- All API URLs are configured in `.env` file
- The `.env` file is git-ignored for security
- Copy `.env.example` to `.env` if missing
- After changing `.env`, restart Metro bundler and rebuild the app

## Development

### Adding New Screens

1. Create screen component in `src/screens/`
2. Add route in `App.tsx`
3. Add navigation button in appropriate screen

### API Integration

All API calls are handled through `src/services/api.ts`. Add new endpoints as needed.

## Building for Production

### Android

```bash
cd android
./gradlew assembleRelease
```

APK will be in `android/app/build/outputs/apk/release/`

### iOS

1. Open `ios/AegisIgnis.xcworkspace` in Xcode
2. Select "Any iOS Device" or specific device
3. Product → Archive
4. Distribute through App Store or TestFlight

## License

MIT License - see LICENSE file for details
