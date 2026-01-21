# 🔥 ML Fire Detection with N8N Integration - Quick Reference

## ✅ What Was Implemented

### 1. ML Fire Detector (`services/ml_fire_detector.py`)
- YOLOv8-based fire and smoke detection
- Automatic fallback to color-based detection
- Configurable confidence thresholds
- Bounding box visualization

### 2. Alert Manager (`services/alert_manager.py`)
- N8N webhook integration for WhatsApp/Voice alerts
- Floor occupancy tracking
- Critical evacuation alerts
- Backend logging integration

### 3. Updated Fire Detection Service (`fire-detection-service/main_v2.py`)
- New `/detect-fire-ml` endpoint with ML detection
- N8N alert integration
- People count in fire alerts
- Screenshot saving with annotations

### 4. Updated Live Camera Server (`live_camera_detection_server.py`)
- Real-time ML fire detection (15 FPS)
- Automatic N8N alerts when fire detected
- Critical evacuation alerts when people present
- Maintains face recognition and presence tracking

### 5. Configuration Files
- `.env.example` - Complete configuration template
- `ML_FIRE_DETECTION_SETUP.md` - Detailed setup guide
- `n8n-workflow-fire-alert.json` - N8N workflow template
- `test_ml_integration.py` - Integration test suite

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Dependencies
```bash
pip install ultralytics opencv-python numpy requests python-dotenv fastapi uvicorn flask flask-cors
```

### Step 2: Configure Environment
```bash
copy .env.example .env
# Edit .env and set N8N_WEBHOOK_URL
```

### Step 3: Run Test
```bash
python test_ml_integration.py
```

### Step 4: Start Services
```bash
# Terminal 1 - Fire Detection Service
cd fire-detection-service
python main_v2.py

# Terminal 2 - Live Camera Server
python live_camera_detection_server.py

# Terminal 3 - N8N (optional)
n8n start
```

## 📱 N8N WhatsApp Setup

### Install N8N
```bash
npm install -g n8n
n8n start
# Opens at http://localhost:5678
```

### Import Workflow
1. Open N8N dashboard
2. Click "Import from File"
3. Select `n8n-workflow-fire-alert.json`
4. Configure Twilio credentials:
   - Account SID
   - Auth Token
   - Phone numbers
5. Copy webhook URL to `.env` → `N8N_WEBHOOK_URL`

### Twilio WhatsApp Setup
1. Sign up at [twilio.com](https://www.twilio.com/)
2. Get WhatsApp Sandbox: `whatsapp:+14155238886`
3. Join sandbox by sending code to WhatsApp
4. Update N8N workflow with your WhatsApp number

## 🔧 Configuration Options

### Fire Detection Sensitivity
```env
# High sensitivity (more alerts, some false positives)
FIRE_CONFIDENCE_THRESHOLD=0.3

# Balanced (recommended)
FIRE_CONFIDENCE_THRESHOLD=0.5

# Low false positives (might miss small fires)
FIRE_CONFIDENCE_THRESHOLD=0.7
```

### Alert Cooldown
```env
# Send alerts every 10 seconds
COOLDOWN_SECONDS=10

# Default: every 30 seconds
COOLDOWN_SECONDS=30

# Conservative: every 60 seconds
COOLDOWN_SECONDS=60
```

### Detection Method
```env
# ML only (requires trained model)
USE_ML_DETECTION=true
USE_COLOR_FALLBACK=false

# Hybrid (ML with color fallback) - RECOMMENDED
USE_ML_DETECTION=true
USE_COLOR_FALLBACK=true

# Color only (no ML model needed)
USE_ML_DETECTION=false
USE_COLOR_FALLBACK=true
```

## 🤖 Getting a Fire Detection Model

### Option 1: Download Pretrained (Easiest)
1. Visit [Roboflow Universe](https://universe.roboflow.com/)
2. Search "fire detection yolov8"
3. Download .pt model file
4. Save to `ml_models/weights/fire_detection.pt`

### Option 2: Train Your Own
1. Collect fire/smoke images
2. Annotate using [Roboflow](https://roboflow.com/)
3. Export as YOLOv8 format
4. Use `ml_models/train/train_fire_model.py`

### Option 3: Use Fallback
- Set `USE_ML_DETECTION=false`
- System uses HSV color detection
- Works immediately, no model needed

## 📊 Alert Flow

```
Camera detects fire
    ↓
ML Fire Detector
    ↓
Get floor occupancy from backend
    ↓
Alert Manager
    ├─ Send to N8N → WhatsApp message
    ├─ If people present → Voice call
    └─ Log to Laravel backend
```

## 🧪 Testing

### Test Fire Detection
```bash
python test_ml_integration.py
```

### Test N8N Webhook Manually
```bash
curl -X POST "YOUR_N8N_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"alert_type":"FIRE_EMERGENCY","floor_id":1,"message":"Test alert","people_count":5}'
```

### Test ML Detection API
```bash
curl -X POST "http://localhost:8002/detect-fire-ml" \
  -F "file=@test_image.jpg" \
  -F "camera_id=1" \
  -F "camera_name=Test" \
  -F "floor_id=1" \
  -F "room_location=Room 101"
```

## 🎯 Alert Types

### FIRE_EMERGENCY
- Fire or smoke detected
- Sends WhatsApp notification
- Logs to backend dashboard

### CRITICAL_EVACUATION
- Fire detected + people present
- Sends WhatsApp notification
- Makes voice call to security
- Requires immediate action

### PRESENCE_UPDATE
- Regular occupancy updates
- Low priority
- WhatsApp only (no voice call)

## 📞 WhatsApp Message Examples

**Fire Alert:**
```
🔥 FIRE ALERT - Floor 3
Location: Conference Room
Camera: Main Camera
Type: FIRE
Severity: CRITICAL
Confidence: 87.5%
👥 People on floor: 5
⏰ Time: 2026-01-21 14:30:25

⚠️ EVACUATION REQUIRED - 5 people present!
```

**Critical Evacuation:**
```
🚨 CRITICAL EMERGENCY - Floor 3
🔥 ACTIVE FIRE DETECTED (87% confidence)
👥 5 PEOPLE NEED EVACUATION
⚠️ IMMEDIATE ACTION REQUIRED!
⏰ 2026-01-21 14:30:25
```

## 🐛 Troubleshooting

### "ML model not available"
✅ Download model from Roboflow
✅ Check `ML_MODEL_PATH` in .env
✅ Enable fallback: `USE_COLOR_FALLBACK=true`

### "N8N webhook not configured"
✅ Set `N8N_WEBHOOK_URL` in .env
✅ Start N8N: `n8n start`
✅ Import workflow JSON

### "Cannot connect to backend"
✅ Start Laravel: `cd backend-laravel && php artisan serve`
✅ Check `BACKEND_API_URL` in .env

### Too many false alerts
✅ Increase threshold: `FIRE_CONFIDENCE_THRESHOLD=0.7`
✅ Use ML model (more accurate)
✅ Increase cooldown: `COOLDOWN_SECONDS=60`

## 📁 Files Created

```
services/
├── ml_fire_detector.py          # ML detection wrapper
└── alert_manager.py              # N8N alert integration

fire-detection-service/
└── main_v2.py                    # Updated with ML + N8N

live_camera_detection_server.py  # Updated with ML detection

.env.example                      # Configuration template
ML_FIRE_DETECTION_SETUP.md       # Full setup guide
n8n-workflow-fire-alert.json     # N8N workflow
test_ml_integration.py            # Test suite
QUICK_REFERENCE.md               # This file
```

## 🎓 Next Steps

1. ✅ Get YOLOv8 fire detection model
2. ✅ Set up N8N with Twilio
3. ✅ Configure WhatsApp sandbox
4. ✅ Run integration tests
5. ✅ Deploy to production cameras
6. ✅ Monitor and tune sensitivity

## 📚 Resources

- [YOLOv8 Docs](https://docs.ultralytics.com/)
- [Roboflow Universe](https://universe.roboflow.com/)
- [N8N Documentation](https://docs.n8n.io/)
- [Twilio WhatsApp](https://www.twilio.com/docs/whatsapp)

## 💡 Tips

- Start with hybrid mode (ML + color fallback)
- Test with small fires first (lighter, candle)
- Adjust threshold based on your environment
- Use voice calls only for critical alerts
- Monitor alert frequency and adjust cooldown
- Train custom model for best accuracy

---

**Need help?** Check `ML_FIRE_DETECTION_SETUP.md` for detailed instructions!
