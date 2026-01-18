# Floor Monitoring - Quick Start Guide

## What This Does
The Live Floor Monitoring service **automatically detects employees on each floor** by analyzing camera feeds in real-time. It identifies registered employees and displays their names on the Floor Monitoring dashboard page.

## Key Features
✅ **Live Detection** - Monitors camera feeds continuously  
✅ **Privacy First** - Shows only names, no face photos on dashboard  
✅ **Auto-Update** - Refreshes every 3 seconds  
✅ **Floor-Based** - Tracks which floor each person is on  
✅ **Smart Timeout** - Removes people after 60 seconds if not seen  

## How To Use

### Step 1: Start All Services
```bash
# Run the main startup script
START-ALL.bat
```

This starts:
- Laravel Backend (port 8000)
- Face Registration (port 8001)
- Fire Detection (port 8002)
- **Live Floor Monitoring (port 8003)** ← New!
- Dashboard (port 5173)

### Step 2: Start Camera Monitoring
Once services are running, activate the cameras:

```bash
# Option A: Start all cameras at once
curl -X POST http://localhost:8003/start-all-cameras

# Option B: Start specific camera
curl -X POST http://localhost:8003/start-camera/1
```

### Step 3: View Floor Monitoring Dashboard
1. Open dashboard: `http://localhost:5173`
2. Navigate to **Floor Monitoring** page
3. Select a floor (e.g., "Ground Floor")
4. See detected employees appear in real-time!

## What You'll See

### On The Dashboard
When employees are detected, you'll see cards showing:

```
┌─────────────────────────────┐
│  👤  John Doe               │
│  📍  Engineering            │
│  ✓ Last seen: 5s ago        │
└─────────────────────────────┘
```

**Note**: Face photos are NOT shown on this page (privacy)

### When No One Is Detected
```
No one detected on this floor
People will appear here when detected by cameras
```

## Camera Setup Requirements

Each camera MUST have:
1. **Stream URL** - Valid RTSP or HTTP stream
   - Example: `rtsp://admin:pass@192.168.1.100:554/stream`
   - Or webcam: `0` (device ID)

2. **Floor Assignment** - Camera must be assigned to a floor
   - Set via Cameras page in dashboard
   - Example: Camera 1 → Ground Floor

3. **Active Status** - Camera must be enabled

## Testing The System

### Check Service Health
```bash
curl http://localhost:8003/health
```

Expected response:
```json
{
  "status": "healthy",
  "monitoring_cameras": 2,
  "employees_cached": 5,
  "insightface_available": true
}
```

### Check Current Floor Presence
```bash
curl http://localhost:8003/floor-presence/1
```

Example response:
```json
{
  "floor_id": 1,
  "people": [
    {
      "employee_id": 1,
      "name": "John Doe",
      "employee_number": "EMP001",
      "department": "Engineering",
      "last_seen": "2026-01-16T14:30:45"
    }
  ],
  "count": 1,
  "last_updated": "2026-01-16T14:30:50"
}
```

## Troubleshooting

### "No one detected" But People Are Present

**Possible Causes:**
1. ❌ Employees not registered with faces
   - **Fix**: Register via Employee Registration app (port 5174)

2. ❌ Cameras not started
   - **Fix**: Run `curl -X POST http://localhost:8003/start-all-cameras`

3. ❌ Camera can't see faces clearly
   - **Fix**: Adjust camera angle/position

4. ❌ Service not running
   - **Fix**: Check if Live Floor Monitoring window is open

### Camera Not Starting

**Error**: "Cannot open camera X"

**Solutions:**
- Check camera stream URL is correct
- Verify camera is on same network
- Test stream manually: `ffplay rtsp://your-camera-url`

### High CPU Usage

**Solution**: Reduce detection frequency
```python
# Edit live_floor_monitoring.py
DETECTION_INTERVAL = 5  # Increase from 3 to 5 seconds
```

## System Architecture

```
┌─────────────┐
│   Camera    │ ←─── Continuous Video Feed
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│ Live Monitoring Service │ ←─── Detects & Identifies Faces
│      (Port 8003)        │
└──────┬──────────────────┘
       │
       ▼
┌─────────────┐
│  Dashboard  │ ←─── Displays Employee Names
│ (Port 5173) │
└─────────────┘
```

## Privacy & Security

🔒 **Privacy Features:**
- Face photos NOT displayed on floor monitoring page
- Only employee names and departments shown
- Service runs on local network only (not internet-exposed)

⚠️ **Security Notes:**
- Service has no authentication (internal use only)
- Keep on private network
- Don't expose port 8003 to internet

## Performance Expectations

| Metric | Value |
|--------|-------|
| Detection Speed | 3 seconds per camera |
| Face Recognition | ~100ms per face |
| Max Cameras | 10-20 (depends on CPU) |
| RAM Usage | ~500MB per camera |

## Service Ports Reference

| Service | Port | Purpose |
|---------|------|---------|
| Dashboard | 5173 | Web interface |
| Employee Registration | 5174 | Register new employees |
| Laravel Backend | 8000 | API & database |
| Face Registration API | 8001 | Face enrollment |
| Fire Detection | 8002 | Fire alerts |
| **Floor Monitoring** | **8003** | **Live employee detection** |

## Next Steps

After setup:
1. ✅ Register employees with faces (port 5174)
2. ✅ Assign cameras to floors (Cameras page)
3. ✅ Start camera monitoring (see Step 2 above)
4. ✅ Monitor Floor Monitoring page for live updates
5. 🎉 Enjoy automated floor occupancy tracking!

## Support

**Check logs**: Look at the "Floor Monitoring Service" PowerShell window

**Common log messages:**
- ✅ `Started monitoring Camera X on Floor Y` - Success
- 👤 `Floor X - Detected: John Doe` - Person identified
- ⚠️ `Cannot open camera X` - Camera connection issue
- 🔄 `Cache loaded: 5 employees` - Employee data refreshed

For issues, see [LIVE_MONITORING_README.md](LIVE_MONITORING_README.md) for detailed troubleshooting.
