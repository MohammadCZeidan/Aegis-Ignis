# Live Floor Monitoring Service

## Overview
This service provides **real-time employee detection** on each floor by monitoring camera feeds continuously. It identifies employees and reports their presence to the dashboard.

## Features
- 🎥 **Live Camera Monitoring** - Continuously processes camera streams
- 👤 **Face Recognition** - Identifies registered employees in real-time
- 📍 **Floor Tracking** - Maps detected people to their current floor
- ⚡ **Fast Detection** - Optimized for speed with cached embeddings
- 🔄 **Auto-refresh** - Updates every 3 seconds per camera
- 📊 **Dashboard Integration** - Sends data to floor monitoring page

## How It Works

### 1. Service Architecture
```
Camera Streams → Face Detection → Face Recognition → Floor Presence API → Dashboard
```

### 2. Detection Flow
1. **Camera Feed**: Reads frames from camera RTSP/HTTP streams
2. **Face Detection**: Uses InsightFace to detect faces in frames
3. **Face Matching**: Compares detected faces against registered employee embeddings
4. **Presence Update**: Updates floor presence data in real-time
5. **Dashboard Display**: Floor monitoring page shows detected employees

### 3. Key Components
- **Port**: 8003 (Face Registration: 8001, Fire Detection: 8002)
- **Detection Threshold**: 50% similarity (stricter than registration)
- **Frame Processing**: Every 3 seconds per camera
- **Presence Timeout**: 60 seconds (person removed if not seen)

## API Endpoints

### Health Check
```
GET /health
Returns service status and monitoring info
```

### Start Monitoring Single Camera
```
POST /start-camera/{camera_id}
Starts monitoring a specific camera
```

### Start All Cameras
```
POST /start-all-cameras
Starts monitoring all cameras from backend
```

### Stop Camera
```
POST /stop-camera/{camera_id}
Stops monitoring a specific camera
```

### Get Floor Presence
```
GET /floor-presence/{floor_id}
Returns list of people currently on a floor
```

### Get All Floors
```
GET /all-floors-presence
Returns people on all floors
```

## Setup Instructions

### 1. Install Dependencies
```bash
cd python-face-service
pip install -r requirements-live-monitoring.txt
```

### 2. Start the Service
```bash
# Windows
START-FLOOR-MONITORING.bat

# Or manually
python live_floor_monitoring.py
```

### 3. Start Monitoring Cameras
```bash
# Start all cameras
curl -X POST http://localhost:8003/start-all-cameras

# Or start specific camera
curl -X POST http://localhost:8003/start-camera/1
```

## Configuration

### Edit Service Settings
Edit `live_floor_monitoring.py`:

```python
# Detection settings
FACE_MATCH_THRESHOLD = 0.50  # 50% threshold for recognition
DETECTION_INTERVAL = 3  # Process frames every 3 seconds
PRESENCE_TIMEOUT = 60  # Remove person after 60 seconds

# Cache settings
CACHE_REFRESH_SECONDS = 30  # Refresh employee data every 30 seconds
```

### Camera Requirements
Each camera needs:
- Valid `stream_url` or `rtsp_url`
- Assigned to a `floor_id`
- Example: `rtsp://admin:password@192.168.1.100:554/stream`

## Dashboard Integration

### Floor Monitoring Page
The dashboard's Floor Monitoring page automatically connects to this service:

```typescript
// Fetches live presence data
const response = await fetch(
  `http://localhost:8003/floor-presence/${selectedFloor}`
);
```

### Display Format
Shows detected employees without their photos (privacy):
- ✅ Employee Name
- ✅ Department
- ✅ Last Seen Time
- ❌ No Face Photo (privacy protection)

## Performance

### Optimization Features
- **Cached Embeddings**: Pre-computed matrix for instant comparisons
- **Frame Skipping**: Processes frames every 3 seconds (not every frame)
- **Vectorized Math**: NumPy operations for speed
- **Async Processing**: Non-blocking camera monitoring

### Expected Performance
- Detection: ~100-200ms per frame
- Recognition: ~50-100ms for comparison
- Total: ~3 seconds per camera cycle

## Troubleshooting

### Camera Not Starting
```
Error: Cannot open camera X
```
**Solution**: Check camera stream URL and network connectivity

### No Employees Detected
```
Warning: NO REGISTERED FACES IN CACHE
```
**Solution**: Ensure employees are registered via face-registration app

### High CPU Usage
**Solution**: Reduce detection frequency in config:
```python
DETECTION_INTERVAL = 5  # Increase to 5 seconds
```

### Service Port Conflict
```
Error: Port 8002 already in use
```
**Solution**: Stop existing service or change port

## Service vs Registration Comparison

| Feature | Registration Service (8001) | Live Monitoring (8002) |
|---------|---------------------------|----------------------|
| Purpose | Employee face registration | Real-time floor monitoring |
| Input | Single photo upload | Continuous camera streams |
| Output | Registration confirmation | Live presence data |
| Threshold | 40% (catch duplicates) | 50% (accurate recognition) |
| Speed | Sub-second | 3 second intervals |

## Integration with Other Services

### Required Services
1. **Laravel Backend** (port 8000) - Employee data & camera info
2. **Face Registration Service** (port 8001) - For registering employees
3. **Fire Detection Service** (port 8002) - Fire alerts
4. **Live Monitoring Service** (port 8003) - This service

### Data Flow
```
Face Registration → Employee Database → Live Monitoring → Dashboard
     (8001)              (8000)              (8003)          (3000)
```

## Security Notes

- ⚠️ Service runs without authentication (internal network only)
- ✅ Does not expose face photos to dashboard
- ✅ Only shows employee names and metadata
- 🔒 Keep service on private network

## Logs

### Success Logs
```
✅ Started monitoring Camera 1 on Floor 2
👤 Floor 2 - Camera 1: Detected John Doe, Jane Smith
```

### Error Logs
```
❌ Cannot open camera 3: Connection timeout
⚠️ Failed to identify face (similarity 45%)
```

## Future Enhancements

- [ ] Multi-camera fusion (same person across cameras)
- [ ] Heatmap visualization
- [ ] Dwell time analytics
- [ ] Crowd density alerts
- [ ] Historical presence reports
- [ ] GPU acceleration support

## Support

For issues:
1. Check service logs
2. Verify camera streams are accessible
3. Ensure employees are registered with faces
4. Test with: `GET http://localhost:8003/health`
