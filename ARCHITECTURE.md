# System Architecture - ML Fire Detection with N8N Integration

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Physical Infrastructure                          │
│                                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Camera 1 │  │ Camera 2 │  │ Camera 3 │  │ Camera N │               │
│  │ Floor 1  │  │ Floor 2  │  │ Floor 3  │  │ Floor N  │               │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └─────┬────┘               │
│        │             │             │             │                      │
└────────┼─────────────┼─────────────┼─────────────┼──────────────────────┘
         │             │             │             │
         └─────────────┴─────────────┴─────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Live Camera Detection Server                          │
│                   (live_camera_detection_server.py)                      │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Camera Stream Processing (15 FPS fire detection)                 │  │
│  │                                                                    │  │
│  │  Every Frame:     Capture → Resize → Stream to Dashboard          │  │
│  │  Every 2 Frames:  Face Detection → Person Tracking                │  │
│  │  Every 4 Frames:  Fire Detection → ML Inference                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  ML Fire Detector (services/ml_fire_detector.py)                  │  │
│  │                                                                    │  │
│  │  ┌──────────────┐                                                 │  │
│  │  │  YOLOv8 Model│ ──> Fire/Smoke Detection                        │  │
│  │  └──────┬───────┘                                                 │  │
│  │         │ (if unavailable)                                        │  │
│  │         ▼                                                          │  │
│  │  ┌──────────────┐                                                 │  │
│  │  │ Color-Based  │ ──> HSV Fire Detection (Fallback)              │  │
│  │  │  Detection   │                                                 │  │
│  │  └──────────────┘                                                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
┌──────────────────────────────┐   ┌──────────────────────────────┐
│   Alert Manager              │   │   Backend API                │
│ (services/alert_manager.py)  │   │   (Laravel)                  │
│                              │   │                              │
│  When Fire Detected:         │   │  Endpoints:                  │
│  1. Get floor occupancy      │◄──┤  • /presence/floor-live/{id}│
│  2. Save screenshot          │   │  • /alerts/fire             │
│  3. Send N8N alert           │   │  • /employees/*             │
│  4. Log to backend           │──►│                              │
│                              │   │  Features:                   │
│  If people present:          │   │  • Presence tracking         │
│  → CRITICAL_EVACUATION       │   │  • Alert history            │
│                              │   │  • Dashboard updates        │
└──────────────┬───────────────┘   └──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         N8N Workflow Engine                              │
│                                                                          │
│  ┌──────────────┐                                                       │
│  │   Webhook    │ ◄─── Receives fire alerts                            │
│  │   Trigger    │                                                       │
│  └──────┬───────┘                                                       │
│         │                                                                │
│         ▼                                                                │
│  ┌──────────────┐                                                       │
│  │    Switch    │ ──┬─ FIRE_EMERGENCY                                  │
│  │  Alert Type  │   ├─ CRITICAL_EVACUATION                             │
│  └──────────────┘   └─ PRESENCE_UPDATE                                 │
│         │                                                                │
│    ┌────┴────┬───────────┬────────────┐                                │
│    ▼         ▼           ▼            ▼                                 │
│ ┌──────┐ ┌──────┐ ┌──────────┐ ┌──────────┐                           │
│ │WhatsApp│Voice │ │  SMS     │ │ Backend  │                           │
│ │Message│ Call  │ │ Alert    │ │ Logging  │                           │
│ └───┬──┘ └──┬──┘ └────┬─────┘ └────┬─────┘                           │
│     │       │         │            │                                    │
└─────┼───────┼─────────┼────────────┼────────────────────────────────────┘
      │       │         │            │
      ▼       ▼         ▼            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      External Services (Twilio)                          │
│                                                                          │
│  WhatsApp    Voice Call    SMS    Cloud Storage                        │
│                                                                          │
│  Recipients:                                                             │
│  • Security Team                                                         │
│  • Building Manager                                                      │
│  • Emergency Services (critical alerts only)                             │
│  • Floor Occupants (future feature)                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

### 1. Fire Detection Flow

```
Camera Frame
    │
    ├─► ML Fire Detector
    │   ├─► YOLOv8 Model (.pt file)
    │   │   └─► Fire/Smoke Detection (0-1 confidence)
    │   │
    │   └─► Color-Based Fallback (if ML unavailable)
    │       └─► HSV Analysis → Orange/Yellow/Red detection
    │
    └─► Detection Result
        {
          detected: true/false,
          type: 'fire' | 'smoke',
          confidence: 0.85,
          bbox: [x1, y1, x2, y2],
          severity: 'warning' | 'critical',
          method: 'ml' | 'color'
        }
```

### 2. Alert Distribution Flow

```
Fire Detected
    │
    ├─► Get Floor Occupancy
    │   └─► Laravel API: /presence/floor-live/{floor_id}
    │       └─► Returns: { people_count: 5, people_details: [...] }
    │
    ├─► Save Screenshot
    │   └─► backend-laravel/public/storage/alerts/fire_cam1_floor2_20260121.jpg
    │
    ├─► Alert Manager
    │   │
    │   ├─► N8N Webhook
    │   │   {
    │   │     alert_type: "FIRE_EMERGENCY",
    │   │     floor_id: 2,
    │   │     people_count: 5,
    │   │     confidence: 0.85,
    │   │     message: "FIRE ALERT - Floor 2 (5 people present)"
    │   │   }
    │   │
    │   └─► Laravel Backend
    │       POST /api/v1/alerts/fire
    │       └─► Stores in database
    │           └─► Broadcasts to dashboard via WebSocket
    │
    └─► N8N Processing
        │
        ├─► Switch on alert_type
        │   │
        │   ├─► FIRE_EMERGENCY
        │   │   └─► WhatsApp Message
        │   │
        │   ├─► CRITICAL_EVACUATION (if people_count > 0)
        │   │   ├─► WhatsApp Message
        │   │   ├─► Voice Call
        │   │   └─► SMS Alert
        │   │
        │   └─► PRESENCE_UPDATE
        │       └─► WhatsApp Summary (low priority)
        │
        └─► Delivery Confirmation
            └─► Log to backend
```

### 3. WhatsApp Message Flow

```
Alert Manager
    │
    ├─► Compose Message
    │   FIRE ALERT - Floor 2
    │   Location: Conference Room
    │   Camera: Main Camera
    │   Type: FIRE
    │   Severity: CRITICAL
    │   Confidence: 85.0%
    │   People on floor: 5
    │   Time: 2026-01-21 14:30:25
    │   
    │   EVACUATION REQUIRED - 5 people present!
    │
    ├─► Send to N8N Webhook
    │
    └─► N8N Workflow
        │
        ├─► Twilio WhatsApp Node
        │   From: whatsapp:+14155238886
        │   To: whatsapp:+1234567890
        │   Message: [composed message]
        │
        └─► Delivery
            └─► Security team receives WhatsApp notification
```

## Component Integration

```
┌────────────────────────────────────────────────────────────┐
│  Service Layer                                             │
│                                                            │
│  ┌─────────────────────┐  ┌──────────────────────────┐   │
│  │ ml_fire_detector.py │  │  alert_manager.py        │   │
│  │                     │  │                          │   │
│  │ • YOLOv8 inference  │  │ • N8N webhook sender     │   │
│  │ • Color fallback    │  │ • Floor occupancy fetch  │   │
│  │ • Confidence calc   │  │ • Critical alerts        │   │
│  │ • Bbox annotation   │  │ • Backend logging        │   │
│  └─────────────────────┘  └──────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌───────────────────┐  ┌────────────────────┐
│ Fire Detection    │  │ Live Camera        │
│ Service (FastAPI) │  │ Server (Flask)     │
│                   │  │                    │
│ Port: 8002        │  │ Port: 5000         │
│ /detect-fire-ml   │  │ /video_feed        │
│ /health           │  │ /api/cameras       │
└───────────────────┘  └────────────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
        ┌─────────────────────┐
        │ Laravel Backend     │
        │ Port: 8000          │
        │                     │
        │ • Presence tracking │
        │ • Alert storage     │
        │ • Dashboard API     │
        │ • WebSocket events  │
        └─────────────────────┘
```

## Technology Stack

```
┌────────────────────────────────────────────────────────┐
│ Computer Vision & ML                                   │
│ • OpenCV 4.8+          - Image processing              │
│ • YOLOv8 (Ultralytics) - Fire/smoke detection         │
│ • NumPy               - Array operations               │
│ • InsightFace         - Face recognition              │
└────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────┐
│ Backend Services                                       │
│ • FastAPI             - Fire detection API             │
│ • Flask               - Camera streaming server        │
│ • Laravel (PHP)       - Main backend & dashboard       │
│ • PostgreSQL/MySQL    - Database                       │
└────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────┐
│ Integration & Automation                               │
│ • N8N                 - Workflow automation            │
│ • Twilio              - WhatsApp/Voice/SMS            │
│ • WebSockets          - Real-time dashboard updates    │
│ • python-dotenv       - Environment configuration      │
└────────────────────────────────────────────────────────┘
```

## Security & Performance

```
┌────────────────────────────────────────────────────────┐
│ Performance Optimizations                              │
│                                                        │
│ • Frame skip (every 4th frame for fire = 15 FPS)      │
│ • Low resolution (480x360 for speed)                  │
│ • JPEG compression (75% quality for streaming)        │
│ • Memory cleanup (GC every 200 frames)                │
│ • Alert cooldown (30s between alerts)                 │
│ • Non-blocking detection (threaded)                   │
└────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────┐
│ Security Features                                      │
│                                                        │
│ • CORS protection                                      │
│ • API authentication (Laravel Sanctum)                │
│ • Webhook signature verification (N8N)                │
│ • Rate limiting on alerts                              │
│ • Screenshot access control                            │
│ • Environment variable secrets                         │
└────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
Production Environment:

┌─────────────────────┐   ┌─────────────────────┐
│  Physical Cameras   │   │  Physical Cameras   │
│  Building A         │   │  Building B         │
└──────────┬──────────┘   └──────────┬──────────┘
           │                         │
           └────────┬────────────────┘
                    │
            ┌───────▼────────┐
            │  Edge Server   │
            │  (Local)       │
            │                │
            │ • Camera feeds │
            │ • ML inference │
            │ • Fast alerts  │
            └───────┬────────┘
                    │
            ┌───────▼────────┐
            │  Cloud Backend │
            │  (AWS/Azure)   │
            │                │
            │ • Laravel API  │
            │ • Database     │
            │ • Dashboard    │
            │ • N8N          │
            └───────┬────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐      ┌──────────────┐
│   Twilio     │      │  Dashboard   │
│   (WhatsApp/ │      │  (Web/Mobile)│
│    Voice)    │      │              │
└──────────────┘      └──────────────┘
```

---

**This architecture provides:**
- Real-time fire detection (15 FPS)
- ML-powered accuracy
- Instant WhatsApp/Voice alerts
- People tracking and evacuation alerts
- Low latency (< 2 seconds from detection to alert)
- Automatic failover (ML → Color fallback)
- Full dashboard integration
