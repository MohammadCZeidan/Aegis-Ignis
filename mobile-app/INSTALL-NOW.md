# Install Android Studio Now - Quick Guide

## You Downloaded It - Install It!

### Installation (5 minutes)

1. **Run the installer** (.exe file)
2. Click **Next** → **Next** → **Next**
3. **Check these boxes:**
   - ✅ Android SDK
   - ✅ Android Virtual Device
4. Click **Install**
5. Wait 5-10 minutes
6. Click **Finish**

### First Launch (10 minutes)

1. Open Android Studio
2. Choose **"Standard"**
3. Wait for SDK download (10-15 min)
4. Click **Finish**

### Create Emulator (5 minutes)

1. **Tools → Device Manager**
2. Click **Create Device**
3. Select **Pixel 5**
4. Click **Next**
5. Download **API 33** (click Download if needed)
6. Click **Next → Finish**

### Start Emulator

1. Click **Play** button (▶️) next to emulator
2. Wait 1-2 minutes
3. Android home screen appears

### Add to PATH (2 minutes)

1. Find SDK: `C:\Users\user\AppData\Local\Android\Sdk`
2. Add to PATH:
   - `C:\Users\user\AppData\Local\Android\Sdk\platform-tools`
   - `C:\Users\user\AppData\Local\Android\Sdk\emulator`
3. Restart terminal
4. Test: `adb devices`

### Run App

```bash
cd mobile-app
npm run android
```

**Done!** App launches on emulator.

See `NEXT-STEPS-AFTER-DOWNLOAD.md` for detailed instructions.
