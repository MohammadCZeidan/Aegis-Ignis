# Next Steps: After Downloading Android Studio

## You've Downloaded Android Studio - Now What?

### Step 1: Install Android Studio

1. **Run the installer** (the .exe file you downloaded)
2. Click **Next** through the installation wizard
3. **IMPORTANT:** Make sure these are checked:
   - ✅ Android SDK
   - ✅ Android SDK Platform
   - ✅ Android Virtual Device (AVD)
   - ✅ Performance (Intel HAXM) - if you have Intel CPU
4. Click **Install**
5. Wait 5-10 minutes for installation
6. Click **Finish**

### Step 2: First Launch Setup

1. **Open Android Studio** (from Start menu or desktop)
2. Choose **"Standard"** installation type
3. Let it download SDK components (10-15 minutes first time)
   - This downloads Android SDK, build tools, etc.
4. Click **Finish** when done

### Step 3: Create Android Emulator

1. In Android Studio: **Tools → Device Manager**
   - (If you don't see Device Manager, click **View → Tool Windows → Device Manager**)
2. Click **Create Device** (or **+ Create Device** button)
3. Select category: **Phone**
4. Select device: **Pixel 5** (or Pixel 6, Pixel 7 - any phone works)
5. Click **Next**
6. Select system image:
   - Choose **API 33** (Android 13) or **API 34** (Android 14)
   - If it says "Download" next to it, click **Download**
   - Wait for download (5-10 minutes)
7. Click **Next**
8. Review settings (name it "Pixel_5_API_33" or similar)
9. Click **Finish**

### Step 4: Start the Emulator

1. In Device Manager, find your emulator (the one you just created)
2. Click the **Play** button (▶️) next to it
3. Wait 1-2 minutes for first boot
4. You'll see the Android home screen appear

**Keep the emulator running!** Don't close it.

### Step 5: Add Android SDK to PATH

This lets you use `adb` and `emulator` commands from terminal.

1. **Find SDK Location:**
   - In Android Studio: **File → Settings** (or **Android Studio → Preferences** on Mac)
   - **Appearance & Behavior → System Settings → Android SDK**
   - Copy the "Android SDK Location" path
   - Usually: `C:\Users\user\AppData\Local\Android\Sdk`

2. **Add to System PATH:**
   - Press `Win + X` → Click **System**
   - Click **Advanced system settings**
   - Click **Environment Variables** button
   - Under **System variables**, find **Path**
   - Click **Edit**
   - Click **New**
   - Add: `C:\Users\user\AppData\Local\Android\Sdk\platform-tools`
   - Click **New** again
   - Add: `C:\Users\user\AppData\Local\Android\Sdk\emulator`
   - Click **OK** on all dialogs

3. **Restart Terminal:**
   - **Close ALL terminal/command prompt windows**
   - Open a **NEW** terminal
   - Test: Type `adb devices`
   - Should show your emulator!

### Step 6: Run Your Mobile App!

Now everything should work:

1. **Make sure Metro bundler is running** (in one terminal):
   ```bash
   cd mobile-app
   npm start
   ```
   Wait for: `info Dev server ready`

2. **In a NEW terminal, run:**
   ```bash
   cd mobile-app
   npm run android
   ```

3. **The app will:**
   - Build (takes 2-5 minutes first time)
   - Install on your emulator
   - Launch automatically!

## Quick Test

After adding to PATH and restarting terminal:

```bash
# Should show your emulator
adb devices

# Should list your emulator
emulator -list-avds

# Should show Java version
java -version
```

All should work!

## Troubleshooting

**"Device Manager not showing"**
- Click **View → Tool Windows → Device Manager**
- Or **Tools → Device Manager**

**"Can't find SDK location"**
- In Android Studio: **File → Settings → Android SDK**
- The path is shown at the top

**"adb still not found" after adding to PATH**
- Restart your computer
- Or close ALL terminals and open new ones
- Make sure you added the correct paths

**"Emulator won't start"**
- Make sure virtualization is enabled in BIOS
- Try creating a new emulator
- Check if HAXM is installed (for Intel CPUs)

## You're Almost There!

Once you:
- ✅ Install Android Studio
- ✅ Create emulator
- ✅ Start emulator
- ✅ Add SDK to PATH
- ✅ Restart terminal

Then run: `npm run android` and your app will launch!
