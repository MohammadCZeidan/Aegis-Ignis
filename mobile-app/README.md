# Aegis Ignis Mobile App

React Native mobile application for the Aegis Ignis smart building security system.

## Prerequisites

### For Android Development
- Node.js 18+
- Java Development Kit (JDK) 17
- Android Studio
- Android SDK (API level 23+)
- Android Emulator or physical device

### For iOS Development
- macOS (required for iOS development)
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

### Android

1. **Start Metro bundler:**
```bash
npm start
```

2. **In a new terminal, run Android:**
```bash
npm run android
```

Or use Android Studio:
- Open `android/` folder in Android Studio
- Wait for Gradle sync
- Click Run button

### iOS

1. **Start Metro bundler:**
```bash
npm start
```

2. **In a new terminal, run iOS:**
```bash
npm run ios
```

Or use Xcode:
- Open `ios/AegisIgnis.xcworkspace` in Xcode
- Select a simulator or device
- Click Run button

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

**Metro bundler not connecting:**
- Check that port 8081 is not in use
- Run `adb reverse tcp:8081 tcp:8081`

**Build errors:**
- Clean build: `cd android && ./gradlew clean`
- Delete `node_modules` and reinstall

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
