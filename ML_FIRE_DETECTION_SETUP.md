# ML Fire Detection Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install ultralytics opencv-python numpy requests python-dotenv fastapi uvicorn flask flask-cors
```

### 2. Configure Environment

Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

Edit `.env` and configure:
- `N8N_WEBHOOK_URL` - Your N8N webhook URL
- `ML_MODEL_PATH` - Path to your fire detection model

### 3. Get a Fire Detection Model

**Option A: Download Pretrained Model (Recommended)**
1. Visit [Roboflow Universe](https://universe.roboflow.com/)
2. Search for "fire detection" or "smoke detection"
3. Download a YOLOv8 model (.pt file)
4. Place it in `ml_models/weights/fire_detection.pt`

**Option B: Train Your Own Model**
1. Prepare fire/smoke dataset
2. Use `ml_models/train/train_fire_model.py`
3. Model will be saved to `ml_models/weights/`

**Option C: Use Color-Based Fallback**
- Set `USE_ML_DETECTION=false` in `.env`
- System will use HSV color-based detection

### 4. Set Up N8N Workflow

#### Install N8N
```bash
npm install -g n8n
n8n start
```

#### Create Fire Alert Workflow

1. **Add Webhook Trigger**
   - Name: "Fire Alert Webhook"
   - Method: POST
   - Path: `fire-alert`
   - Copy webhook URL to `.env` as `N8N_WEBHOOK_URL`

2. **Add Switch Node** (Check alert_type)
   - FIRE_EMERGENCY → Critical alert flow
   - CRITICAL_EVACUATION → Emergency evacuation flow
   - PRESENCE_UPDATE → Regular updates

3. **Add WhatsApp Node** (Twilio WhatsApp or WhatsApp Business)
   - Connect Twilio account
   - From: `whatsapp:+14155238886` (Twilio sandbox)
   - To: Your WhatsApp number
   - Message: `{{ $json["message"] }}`

4. **Add Voice Call Node** (for critical alerts only)
   - Twilio Voice Call
   - TwiML: `<Say>{{ $json["message"] }}</Say>`
   - Triggered only for CRITICAL_EVACUATION

5. **Add HTTP Request Node** (log to backend)
   - Updates Laravel backend
   - Stores alert in database

### 5. Run the Services

**Start Fire Detection Service:**
```bash
cd fire-detection-service
python main_v2.py
```

**Start Live Camera Server:**
```bash
python live_camera_detection_server.py
```

**Start Face Recognition (optional):**
```bash
cd python-face-service
python main_fast.py
```

## How It Works

### Detection Flow

```
Camera Frame
    ↓
ML Fire Detector (YOLOv8)
    ↓ (if ML unavailable)
Color-Based Fallback
    ↓ (if fire detected)
Get Floor Occupancy (Laravel API)
    ↓
Alert Manager
    ↓
├─ N8N Webhook → WhatsApp/Voice
└─ Laravel Backend → Dashboard
```

### Alert Types

1. **FIRE_EMERGENCY**
   - Fire or smoke detected
   - Sends WhatsApp message
   - Logs to backend

2. **CRITICAL_EVACUATION**
   - Fire detected + people present
   - Sends WhatsApp message
   - Makes voice call
   - Triggers evacuation protocol

3. **PRESENCE_UPDATE**
   - Regular occupancy updates
   - Low priority notification

## Testing

### Test Fire Detection
```bash
curl -X POST "http://localhost:8002/detect-fire-ml" \
  -F "file=@test_fire_image.jpg" \
  -F "camera_id=1" \
  -F "camera_name=Test Camera" \
  -F "floor_id=1" \
  -F "room_location=Test Room"
```

### Test N8N Webhook
```bash
curl -X POST "YOUR_N8N_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "FIRE_EMERGENCY",
    "floor_id": 1,
    "message": "Test fire alert",
    "people_count": 5
  }'
```

## Configuration Tips

### Adjust Sensitivity
- **High sensitivity:** `FIRE_CONFIDENCE_THRESHOLD=0.3`
- **Balanced:** `FIRE_CONFIDENCE_THRESHOLD=0.5` (default)
- **Low false positives:** `FIRE_CONFIDENCE_THRESHOLD=0.7`

### Cooldown Period
- Prevent spam: `COOLDOWN_SECONDS=30` (default)
- More frequent alerts: `COOLDOWN_SECONDS=10`

### Detection Method
- **ML only:** `USE_ML_DETECTION=true`, `USE_COLOR_FALLBACK=false`
- **Hybrid:** `USE_ML_DETECTION=true`, `USE_COLOR_FALLBACK=true` (recommended)
- **Color only:** `USE_ML_DETECTION=false`, `USE_COLOR_FALLBACK=true`

## Troubleshooting

### No ML Model Available
✓ Check `ML_MODEL_PATH` in `.env`
✓ Download model from Roboflow
✓ Enable fallback: `USE_COLOR_FALLBACK=true`

### N8N Alerts Not Sending
✓ Check `N8N_WEBHOOK_URL` is correct
✓ Verify N8N is running: `http://localhost:5678`
✓ Test webhook with curl command above

### False Fire Alerts
✓ Increase threshold: `FIRE_CONFIDENCE_THRESHOLD=0.7`
✓ Increase min area: `MIN_FIRE_AREA_PERCENTAGE=5.0`
✓ Use ML model (more accurate than color)

### Missing People Count
✓ Start Face Recognition service
✓ Check Laravel backend is running
✓ Verify presence tracking is active

## Next Steps

1. ✅ Train or download ML fire detection model
2. ✅ Set up N8N workflow for WhatsApp/Voice
3. ✅ Configure Twilio account for messaging
4. ✅ Test with sample fire images
5. ✅ Deploy to production cameras
6. ✅ Monitor alerts and adjust sensitivity

## Resources

- [Roboflow Fire Detection Models](https://universe.roboflow.com/search?q=fire%20detection)
- [N8N Documentation](https://docs.n8n.io/)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [YOLOv8 Documentation](https://docs.ultralytics.com/)
