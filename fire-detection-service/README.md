# Fire Detection Service

Standalone fire detection service that runs separately from the main backend but reports detections to the same API.

## Features

- Real-time fire detection using color-based detection
- Configurable camera source
- Automatic reporting to backend API (metadata only - NO photos saved)
- Reports: floor, room location, people on floor when fire detected
- Configurable detection thresholds
- Cooldown period to prevent spam

## Setup

1. Install dependencies:
```bash
pip install opencv-python numpy requests python-dotenv
```

2. Configure environment variables (create `.env` file):
```env
API_BASE_URL=http://localhost:8000/api/v1
API_TOKEN=  # Optional: API token if authentication required
CAMERA_ID=0
FLOOR_ID=1
ROOM_LOCATION=Main Hall  # Room name or location
DETECTION_INTERVAL=1.0
CONFIDENCE_THRESHOLD=0.5
```

3. Run the service:
```bash
python main.py
```

## Configuration

- `CAMERA_ID`: Camera device ID (0 for default webcam)
- `FLOOR_ID`: Floor ID for reporting detections
- `DETECTION_INTERVAL`: Seconds between detection checks
- `CONFIDENCE_THRESHOLD`: Minimum confidence for reporting (0.0-1.0)

## How It Works

1. Captures frames from the camera (live feed)
2. Analyzes frames for fire-like colors (orange, red, yellow)
3. Detects regions with sufficient fire-like characteristics
4. Reports detections to the backend API with metadata:
   - Floor ID and name
   - Room location
   - People present on floor (from occupancy system)
   - Detection confidence
   - Bounding box coordinates
5. **NO PHOTOS ARE SAVED** - Only metadata is stored
6. Cooldown period prevents duplicate reports

## Integration

This service is separate from the main backend but uses the same API endpoints for reporting. The main backend handles:
- User authentication
- Employee face registration
- Dashboard and alerts
- WebSocket real-time updates

The fire detection service focuses solely on:
- Camera monitoring
- Fire detection
- Reporting to backend

