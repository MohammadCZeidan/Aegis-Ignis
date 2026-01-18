# Camera Detection Service

Integrated service that captures camera frames and runs both fire and face detection with presence tracking.

## Features

- 🎥 **Real-time Camera Capture** - Captures frames from webcam/IP camera
- 🔥 **Fire Detection** - Sends frames to fire detection service
- 👤 **Face Recognition** - Identifies employees in camera feed
- ⏱️ **5-Minute Presence Tracking** - Tracks people on floors with auto-expiry
- 🔄 **Timer Reset** - Seeing someone again resets their 5-minute timer
- 📊 **Auto Cleanup** - Removes expired presence entries

## How It Works

### Presence Tracking Logic

1. **First Detection**: When camera sees a person → Start 5-minute timer
2. **Re-detection**: If camera sees them again → Reset timer to 5 minutes
3. **Expiration**: After 5 minutes without detection → Remove from floor tracking
4. **Multiple Cameras**: Each camera can track people on its assigned floor

### Detection Flow

```
Camera Frame Capture
    ↓
    ├─→ Fire Detection Service → Report to Backend (if fire > 30%)
    └─→ Face Detection Service → Identify Person → Update Presence
                                                    ↓
                                            Reset 5-min Timer
```

## Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Make Sure Services Are Running**:
```bash
# Fire Detection Service (Port 8002)
cd ../fire-detection-service
python main_v2.py

# Face Recognition Service (Port 8001)
cd ../python-face-service
python main_v2.py

# Laravel Backend (Port 8000)
cd ../backend-laravel
php artisan serve
```

4. **Run Camera Service**:
```bash
python main.py
```

## Configuration

### `.env` Variables

- `CAMERA_ID`: Camera device ID (0 for default webcam, or RTSP URL for IP camera)
- `FLOOR_ID`: Which floor this camera monitors
- `ROOM_LOCATION`: Room name (e.g., "Main Hall", "Entrance")
- `DETECTION_INTERVAL`: Seconds between detections (default: 2.0)
- `FIRE_CONFIDENCE_THRESHOLD`: Minimum fire confidence to report (default: 0.3)
- `FACE_CONFIDENCE_THRESHOLD`: Minimum face match confidence (default: 0.6)
- `PRESENCE_TIMEOUT`: Seconds until presence expires (default: 300 = 5 minutes)

## API Endpoints Used

### Backend API
- `POST /api/v1/fire-detections/report` - Report fire detection
- `POST /api/v1/presence/log` - Log employee presence
- `POST /api/v1/employees/identify-face` - Identify person by face embedding

### Fire Service
- `POST /detect-fire` - Analyze frame for fire

### Face Service
- `POST /detect-faces` - Detect faces and extract embeddings

## Example Output

```
🎥 Camera Detection Service STARTED
   Camera: 0
   Floor: 1 (Main Hall)
   Presence Timeout: 300s (5 minutes)
   
🆕 Employee 42 detected on floor 1 - starting 5min timer
✓ Presence logged: John Doe on floor 1

👤 Detected: John Doe (confidence: 87%)
👁️ Employee 42 seen again on floor 1 - resetting 5min timer

🔥 Fire detected! Confidence: 85%
🔥 FIRE REPORTED! Event ID: 123

📊 Status: 100 frames | 3 people on floor 1

⏱️ Employee 42 expired from floor 1 (>5min)
```

## Multi-Camera Setup

To monitor multiple cameras/floors, run multiple instances:

```bash
# Camera 1 - Ground Floor
CAMERA_ID=0 FLOOR_ID=1 ROOM_LOCATION="Main Entrance" python main.py

# Camera 2 - Second Floor
CAMERA_ID=1 FLOOR_ID=2 ROOM_LOCATION="Office Area" python main.py

# Camera 3 - Third Floor (IP Camera)
CAMERA_ID="rtsp://192.168.1.100:554/stream" FLOOR_ID=3 ROOM_LOCATION="Conference Room" python main.py
```

## Presence Tracking Details

### Timer Behavior
- Person detected → Timer starts at 5:00
- Seen at 2:30 remaining → Timer resets to 5:00
- Not seen after 5:00 → Removed from floor
- Seen again later → New 5:00 timer starts

### Database Updates
- Every detection updates `employees.last_seen_at`
- Every detection creates `presence_logs` entry
- Floor occupancy snapshots track real-time presence
- Fire events include list of people on floor (from presence tracking)

## Troubleshooting

**Camera not opening**:
- Check `CAMERA_ID` is correct
- Try `CAMERA_ID=0` for default webcam
- For IP cameras, use full RTSP URL

**No face detections**:
- Ensure face service is running on port 8001
- Check employees have registered faces in database
- Adjust `FACE_CONFIDENCE_THRESHOLD` (lower = more matches)

**Too many fire alerts**:
- Increase `FIRE_CONFIDENCE_THRESHOLD`
- Increase fire cooldown in code (default 15s)

**People not expiring**:
- Check `PRESENCE_TIMEOUT` setting
- Cleanup runs every 50 frames (look for logs)
