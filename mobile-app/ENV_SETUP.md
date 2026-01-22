# Environment Variables Setup

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **The `.env` file is already configured with:**
   - EC2 Backend API: `http://35.180.117.85/api/v1` (Production)

3. **The `.env` file is git-ignored** - your API URLs will NOT be committed to git

## Configuration

### Production (EC2) - Default

The `.env` file is pre-configured to use the EC2 backend:

```env
BACKEND_API_URL=http://35.180.117.85/api/v1
```

### Local Development

To use your local backend instead, edit `.env` and uncomment:

```env
# For Android Emulator
BACKEND_API_URL=http://10.0.2.2:8000/api/v1

# For iOS Simulator
BACKEND_API_URL=http://localhost:8000/api/v1

# For Physical Device (replace with your computer's IP)
BACKEND_API_URL=http://192.168.1.100:8000/api/v1
```

## Available Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BACKEND_API_URL` | Laravel backend API URL | `http://35.180.117.85/api/v1` |
| `FACE_SERVICE_URL` | Face recognition service | `http://10.0.2.2:8001` |
| `FIRE_SERVICE_URL` | Fire detection service | `http://10.0.2.2:8002` |
| `FLOOR_SERVICE_URL` | Floor monitoring service | `http://10.0.2.2:8003` |
| `CAMERA_SERVICE_URL` | Camera streaming service | `http://10.0.2.2:5000` |

## Platform-Specific Notes

### Android Emulator
- Use `10.0.2.2` to access your host machine's localhost
- Example: `http://10.0.2.2:8000/api/v1`

### iOS Simulator
- Use `localhost` directly
- Example: `http://localhost:8000/api/v1`

### Physical Device
- Use your computer's local IP address
- Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- Example: `http://192.168.1.100:8000/api/v1`

## After Changing .env

1. Stop Metro bundler (Ctrl+C)
2. Clear Metro cache:
   ```bash
   npm start -- --reset-cache
   ```
3. Rebuild the app:
   ```bash
   npm run android  # or npm run ios
   ```

## Security

- ✅ `.env` is in `.gitignore` - will NOT be committed
- ✅ `.env.example` is committed - safe template
- ✅ Never commit `.env` with real API keys or URLs
- ✅ Use different `.env` files for different environments if needed

## Troubleshooting

**Environment variables not loading:**
- Make sure `.env` file exists in `mobile-app/` directory
- Restart Metro bundler after changing `.env`
- Clear cache: `npm start -- --reset-cache`
- Rebuild the app completely

**Wrong API URL being used:**
- Check `.env` file has correct values
- Verify no typos in variable names
- Make sure you're using the right platform (Android vs iOS)
