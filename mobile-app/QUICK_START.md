# Quick Start Guide - Aegis Ignis Mobile App

## Prerequisites Check

### Android
- [ ] Node.js 18+ installed
- [ ] Android Studio installed
- [ ] Android SDK installed (API 23+)
- [ ] Android Emulator or physical device connected

### iOS (macOS only)
- [ ] Node.js 18+ installed
- [ ] Xcode 14+ installed
- [ ] CocoaPods installed (`sudo gem install cocoapods`)
- [ ] iOS Simulator or physical device

## Installation Steps

### 1. Install Dependencies

```bash
cd mobile-app
npm install
```

### 2. iOS Setup (macOS only)

```bash
cd ios
pod install
cd ..
```

### 3. Configure API Endpoints

Edit `src/config/api.ts` and update the `HOST` variable:

- **Android Emulator**: `10.0.2.2`
- **iOS Simulator**: `localhost`
- **Physical Device**: Your computer's IP (e.g., `192.168.1.100`)

## Running the App

### Option 1: Quick Scripts (Easiest)

**Windows - Android:**
```bash
# Double-click or run:
RUN-ANDROID.bat
```

**macOS - iOS:**
```bash
chmod +x RUN-IOS.sh
./RUN-IOS.sh
```

### Option 2: Manual Steps

**IMPORTANT:** You need TWO terminal windows!

**Terminal 1 - Metro Bundler:**
```bash
cd mobile-app
npm start
```
Wait until you see: `info Dev server ready`

**Terminal 2 - Run App (NEW WINDOW):**
```bash
cd mobile-app
npm run android    # For Android
# OR
npm run ios        # For iOS (macOS only)
```

**Note:** If Metro terminal doesn't accept input, that's normal! Just open a NEW terminal window for step 2.

## First Run Checklist

1. ✅ Metro bundler starts successfully
2. ✅ App builds without errors
3. ✅ App launches on emulator/device
4. ✅ Login screen appears
5. ✅ Can connect to backend API

## Common Issues & Solutions

### "Cannot connect to Metro bundler"
- **Solution**: Make sure Metro is running (`npm start`)
- Check port 8081 is not blocked

### "Cannot connect to backend API"
- **Android Emulator**: Change `localhost` to `10.0.2.2` in `src/config/api.ts`
- **Physical Device**: Use your computer's IP address
- Check backend is running on correct port

### "Build failed" (Android)
```bash
cd android
./gradlew clean
cd ..
npm run android
```

### "Pod install failed" (iOS)
```bash
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
```

### "Module not found"
```bash
rm -rf node_modules
npm install
```

## Testing the Connection

1. Make sure your Laravel backend is running on `http://localhost:8000`
2. Open the app
3. Try to login (or check if health endpoint works)
4. Check Metro bundler console for API errors

## Next Steps

- Customize the UI in `src/screens/`
- Add new API endpoints in `src/services/api.ts`
- Configure push notifications
- Add authentication flow
- Set up app icons and splash screens

## Need Help?

- Check `README.md` for detailed documentation
- Review React Native docs: https://reactnative.dev/docs/getting-started
- Check backend API is accessible from your device/emulator
