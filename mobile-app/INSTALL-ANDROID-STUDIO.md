# Install Android Studio - Step by Step

## Why You Need This

Your errors show:
- `adb` not found → Need Android SDK
- `gradlew.bat` not found → Need Gradle (comes with Android Studio)
- No emulators → Need Android Studio to create them

**Android Studio includes EVERYTHING you need!**

## Installation Steps

### 1. Download Android Studio
- Go to: https://developer.android.com/studio
- Click "Download Android Studio"
- File size: ~1 GB
- Download time: 5-10 minutes

### 2. Install Android Studio
1. Run the installer
2. Click **Next** through the wizard
3. **Important:** Make sure these are checked:
   - ✅ Android SDK
   - ✅ Android SDK Platform
   - ✅ Android Virtual Device (AVD)
   - ✅ Performance (Intel HAXM) - if on Intel CPU
4. Click **Install**
5. Wait 5-10 minutes for installation
6. Click **Finish**

### 3. First Launch Setup
1. Open Android Studio
2. Choose "Standard" installation
3. Let it download SDK components (10-15 minutes first time)
4. Click **Finish** when done

### 4. Create Android Emulator
1. In Android Studio: **Tools → Device Manager**
2. Click **Create Device** (or **+ Create Device** button)
3. Select category: **Phone**
4. Select device: **Pixel 5** (or Pixel 6, Pixel 7)
5. Click **Next**
6. Select system image:
   - Choose **API 33** (Android 13) or **API 34** (Android 14)
   - If not downloaded, click **Download** next to it
   - Wait for download (5-10 minutes)
7. Click **Next**
8. Review settings, click **Finish**

### 5. Start Emulator
1. In Device Manager, find your emulator
2. Click the **Play** button (▶️) next to it
3. Wait 1-2 minutes for first boot
4. You'll see Android home screen

### 6. Add Android SDK to PATH

**Find SDK Location:**
1. In Android Studio: **File → Settings**
2. **Appearance & Behavior → System Settings → Android SDK**
3. Copy the "Android SDK Location" path
4. Usually: `C:\Users\YourName\AppData\Local\Android\Sdk`

**Add to PATH:**
1. Press `Win + X` → **System**
2. Click **Advanced system settings**
3. Click **Environment Variables**
4. Under **System variables**, find **Path**
5. Click **Edit**
6. Click **New**
7. Add: `C:\Users\YourName\AppData\Local\Android\Sdk\platform-tools`
8. Click **New** again
9. Add: `C:\Users\YourName\AppData\Local\Android\Sdk\emulator`
10. Replace `YourName` with your actual username
11. Click **OK** on all dialogs

### 7. Restart Terminal
- **Close ALL terminal windows**
- Open a **NEW** terminal/command prompt
- Test: Type `adb devices` - should work now!

### 8. Run Your App

```bash
cd mobile-app
npm run android
```

The app should build and launch on your emulator!

## Time Estimate

- Download: 5-10 minutes
- Installation: 5-10 minutes
- First launch setup: 10-15 minutes
- Create emulator: 5 minutes
- First emulator boot: 1-2 minutes

**Total: ~30-45 minutes** (one-time setup)

## After Installation

Test everything works:

```bash
# Should show your emulator
adb devices

# Should list your emulator
emulator -list-avds

# Should show Java version
java -version
```

## Troubleshooting

**"SDK location not found"**
- Make sure Android Studio is fully installed
- Check SDK location in Android Studio settings

**"adb still not found" after adding to PATH**
- Restart your computer
- Close and reopen terminal
- Check PATH was saved correctly

**"Emulator won't start"**
- Make sure virtualization is enabled in BIOS
- Check HAXM is installed (for Intel CPUs)
- Try creating a new emulator

## You're Done!

Once Android Studio is installed and emulator is running:
- ✅ ADB will work
- ✅ Gradle will work
- ✅ Emulator will be available
- ✅ Your app will build and run

Just run: `npm run android` and it should work!
