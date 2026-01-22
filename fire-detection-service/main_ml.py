"""
ML Fire Detection Service with N8N Alerts + Live Camera Monitoring
- YOLOv8 ML-based fire and smoke detection
- Automatic fallback to color-based detection if model unavailable
- N8N webhook integration for WhatsApp/Voice alerts
- EC2 Laravel backend integration
- Screenshot capture and alert logging
- LIVE CAMERA STREAMING with continuous fire detection
"""
import cv2
import numpy as np
import requests
import time
import logging
import os
import sys
import json
from typing import Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import base64
from threading import Thread, Lock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ml_fire_detector import MLFireDetector
from services.alert_manager import AlertManager

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
LARAVEL_API_URL = os.getenv('BACKEND_API_URL', 'http://35.180.227.44/api/v1')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', '')
ML_MODEL_PATH = os.getenv('ML_MODEL_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml_models', 'weights', 'fire_detection.pt'))
FIRE_CONFIDENCE_THRESHOLD = float(os.getenv('FIRE_CONFIDENCE_THRESHOLD', '0.1'))
USE_ML_DETECTION = os.getenv('USE_ML_DETECTION', 'true').lower() == 'true'
USE_COLOR_FALLBACK = os.getenv('USE_COLOR_FALLBACK', 'false').lower() == 'true'

app = FastAPI(title="ML Fire Detection Service", version="4.0.0-ML")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Camera state management
active_cameras = {}  # {camera_id: cv2.VideoCapture}
camera_locks = {}  # {camera_id: Lock}
last_fire_alert_time = {}  # {camera_id: timestamp}
FIRE_ALERT_COOLDOWN = 30  # seconds
CAMERA_CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "camera_config.json")

# Initialize ML detector and alert manager
print("\n" + "="*80)
print(" INITIALIZING ML FIRE DETECTION SERVICE")
print("="*80)

ml_detector = MLFireDetector(
    model_path=ML_MODEL_PATH if USE_ML_DETECTION else None,
    confidence_threshold=FIRE_CONFIDENCE_THRESHOLD,
    use_color_fallback=USE_COLOR_FALLBACK
)

alert_manager = AlertManager(n8n_webhook_url=N8N_WEBHOOK_URL)

print(f" ML Model: {'Loaded' if ml_detector.model is not None else 'Using Color Fallback'}")
print(f" N8N Alerts: {'Enabled' if N8N_WEBHOOK_URL else 'Disabled'}")
print(f" Confidence Threshold: {FIRE_CONFIDENCE_THRESHOLD*100}%")
print(f" Color Fallback: {'Enabled' if USE_COLOR_FALLBACK else 'DISABLED - ML ONLY'}")
print(f" Backend API: {LARAVEL_API_URL}")
print("="*80 + "\n")

# Camera configuration
CAMERA_ID = 1
FLOOR_ID = 3
ROOM = "Office"


def load_cameras():
    """Load camera configuration from JSON file"""
    try:
        with open(CAMERA_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('cameras', [])
    except Exception as e:
        logger.error(f"Error loading camera config: {e}")
        return []


def get_camera(camera_id: int):
    """Get or create camera instance"""
    if camera_id not in active_cameras:
        cameras = load_cameras()
        cam_config = next((c for c in cameras if c['id'] == camera_id), None)
        
        if not cam_config:
            return None
        
        # Parse stream URL (0 for webcam, or RTSP URL)
        stream_url = cam_config['stream_url']
        try:
            stream_url = int(stream_url)  # Webcam index
        except ValueError:
            pass  # RTSP URL
        
        cap = cv2.VideoCapture(stream_url)
        if cap.isOpened():
            active_cameras[camera_id] = cap
            camera_locks[camera_id] = Lock()
            logger.info(f" Camera {camera_id} initialized")
        else:
            logger.error(f" Failed to open camera {camera_id}")
            return None
    
    return active_cameras.get(camera_id)


def release_camera(camera_id: int):
    """Release camera resources"""
    if camera_id in active_cameras:
        active_cameras[camera_id].release()
        del active_cameras[camera_id]
        if camera_id in camera_locks:
            del camera_locks[camera_id]
        logger.info(f"Camera {camera_id} released")


def generate_frames(camera_id: int):
    """Generate video frames with ML fire detection overlay"""
    cap = get_camera(camera_id)
    if not cap:
        return
    
    frame_count = 0
    
    while True:
        try:
            with camera_locks[camera_id]:
                success, frame = cap.read()
            
            if not success:
                logger.warning(f"Failed to read from camera {camera_id}")
                break
            
            # Run fire detection every 6 frames (~10 FPS detection)
            if frame_count % 6 == 0:
                detection_result = ml_detector.detect(frame)
                
                if detection_result['detected']:
                    # Annotate frame with fire detection
                    frame = ml_detector.annotate_frame(frame.copy(), detection_result)
                    
                    # Send alert if cooldown expired
                    current_time = time.time()
                    last_alert = last_fire_alert_time.get(camera_id, 0)
                    
                    if current_time - last_alert > FIRE_ALERT_COOLDOWN:
                        # Background alert sending (don't block stream)
                        Thread(target=send_fire_alert_async, args=(
                            camera_id, frame.copy(), detection_result
                        )).start()
                        
                        last_fire_alert_time[camera_id] = current_time
            
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            frame_count += 1
            time.sleep(0.033)  # ~30 FPS
            
        except Exception as e:
            logger.error(f"Error in frame generation: {e}")
            break


def send_fire_alert_async(camera_id: int, frame, detection_result: dict):
    """Send fire alert asynchronously (non-blocking)"""
    try:
        confidence = detection_result['confidence']
        fire_type = detection_result['type']
        method = detection_result['method']
        
        logger.warning(f" FIRE DETECTED on Camera {camera_id}! Confidence: {confidence*100:.1f}% (Method: {method})")
        
        # Encode screenshot
        _, buffer = cv2.imencode('.jpg', frame)
        screenshot_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Get cameras config for floor_id
        cameras = load_cameras()
        cam_config = next((c for c in cameras if c['id'] == camera_id), None)
        floor_id = cam_config.get('floor_id', FLOOR_ID) if cam_config else FLOOR_ID
        room = cam_config.get('room', ROOM) if cam_config else ROOM
        
        # Get people count
        people_count = alert_manager.get_floor_occupancy(floor_id)
        
        # Send N8N alert
        if N8N_WEBHOOK_URL:
            alert_manager.send_fire_alert(
                camera_id=camera_id,
                floor_id=floor_id,
                screenshot_base64=screenshot_base64,
                people_count=people_count,
                fire_confidence=confidence
            )
            
            if people_count > 0:
                alert_manager.send_critical_evacuation_alert(
                    floor_id=floor_id,
                    people_count=people_count,
                    camera_id=camera_id
                )
        
        # Send to Laravel backend
        send_fire_alert_to_backend(
            camera_id=camera_id,
            camera_name=f"Camera {camera_id}",
            floor_id=floor_id,
            room=room,
            screenshot_base64=screenshot_base64,
            confidence=confidence,
            fire_type=fire_type
        )
        
    except Exception as e:
        logger.error(f"Error sending async alert: {e}")


def monitor_camera_background(camera_id: int):
    """Background thread for continuous camera monitoring and fire detection"""
    logger.info(f"🎥 Starting background monitoring for Camera {camera_id}")
    
    cap = get_camera(camera_id)
    if not cap:
        logger.error(f" Failed to start camera {camera_id}")
        return
    
    frame_count = 0
    
    while camera_id in active_cameras:
        try:
            with camera_locks[camera_id]:
                success, frame = cap.read()
            
            if not success:
                logger.warning(f"Failed to read from camera {camera_id}, retrying...")
                time.sleep(1)
                continue
            
            # Run fire detection every 10 frames (~6 FPS detection for efficiency)
            if frame_count % 10 == 0:
                detection_result = ml_detector.detect(frame)
                
                # Log detection result for debugging
                if frame_count % 100 == 0:  # Log every 100 frames
                    logger.info(f"Detection check: detected={detection_result['detected']}, confidence={detection_result['confidence']*100:.1f}%, method={detection_result['method']}")
                
                if detection_result['detected']:
                    confidence = detection_result['confidence']
                    method = detection_result['method']
                    fire_type = detection_result['type']
                    
                    logger.warning(f" FIRE! Camera {camera_id} - {fire_type.upper()} - {confidence*100:.1f}% ({method})")
                    
                    # Check cooldown
                    current_time = time.time()
                    last_alert = last_fire_alert_time.get(camera_id, 0)
                    
                    if current_time - last_alert > FIRE_ALERT_COOLDOWN:
                        # Send alert in separate thread
                        Thread(target=send_fire_alert_async, args=(
                            camera_id, frame.copy(), detection_result
                        )).start()
                        
                        last_fire_alert_time[camera_id] = current_time
                        logger.info(f" Alert sent for Camera {camera_id}")
                    else:
                        remaining = int(FIRE_ALERT_COOLDOWN - (current_time - last_alert))
                        logger.info(f" Alert cooldown active ({remaining}s remaining)")
            
            frame_count += 1
            time.sleep(0.1)  # ~10 FPS
            
        except Exception as e:
            logger.error(f"Error in background monitoring: {e}")
            time.sleep(1)
    
    logger.info(f"Background monitoring stopped for Camera {camera_id}")


def send_fire_alert_to_backend(camera_id: int, camera_name: str, floor_id: int, 
                                room: str, screenshot_base64: str, confidence: float,
                                fire_type: str) -> Optional[int]:
    """Send fire alert to Laravel backend (EC2)"""
    try:
        # Convert confidence from 0-1 to 0-100 scale
        confidence_percentage = confidence * 100
        
        # Ensure base64 has proper data URI prefix for image display
        if not screenshot_base64.startswith('data:image'):
            screenshot_base64 = f"data:image/jpeg;base64,{screenshot_base64}"
        
        alert_data = {
            "camera_id": camera_id,
            "camera_name": camera_name,
            "floor_id": floor_id,
            "room": room,
            "confidence": confidence_percentage,  # Send as 0-100
            "screenshot": screenshot_base64,  # With data URI prefix
            "detected_at": datetime.now().isoformat(),
            "type": fire_type,
            "severity": "critical" if confidence > 0.8 else "high" if confidence > 0.6 else "medium"
        }
        
        response = requests.post(
            f"{LARAVEL_API_URL}/alerts",
            json=alert_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            alert_id = result.get('id') or result.get('alert', {}).get('id')
            logger.info(f" Alert sent to EC2 backend - Alert ID: {alert_id}, Confidence: {confidence_percentage:.1f}%")
            return alert_id
        else:
            logger.error(f" Failed to send alert to backend: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f" Error sending alert to backend: {e}")
        return None


@app.post("/detect-fire-ml")
async def detect_fire_ml(
    file: UploadFile = File(...),
    camera_id: int = Form(default=CAMERA_ID),
    floor_id: int = Form(default=FLOOR_ID)
):
    """
    ML-based fire detection endpoint
    Detects fire/smoke using YOLOv8 ML model with color fallback
    Sends alerts to both N8N and Laravel backend
    """
    try:
        # Read and decode image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Run ML detection
        detection_result = ml_detector.detect(frame)
        
        detected = detection_result['detected']
        confidence = detection_result['confidence']
        fire_type = detection_result['type']
        method = detection_result['method']
        
        logger.info(f"Detection - Method: {method}, Type: {fire_type}, Confidence: {confidence*100:.2f}%, Detected: {detected}")
        
        if detected:
            logger.warning(f" FIRE DETECTED! Confidence: {confidence*100:.2f}% (Method: {method})")
            
            # Annotate frame with detection
            annotated_frame = ml_detector.annotate_frame(
                frame.copy(),
                detection_result
            )
            
            # Encode screenshot as base64
            _, buffer = cv2.imwrite('.temp_fire_screenshot.jpg', annotated_frame)
            screenshot_base64 = base64.b64encode(cv2.imencode('.jpg', annotated_frame)[1]).decode('utf-8')
            logger.info("📸 Screenshot captured and encoded")
            
            # Get people count from backend
            people_count = alert_manager.get_floor_occupancy(floor_id)
            
            # Send N8N alert if configured
            n8n_success = False
            if N8N_WEBHOOK_URL:
                n8n_success = alert_manager.send_fire_alert(
                    camera_id=camera_id,
                    floor_id=floor_id,
                    screenshot_base64=screenshot_base64,
                    people_count=people_count,
                    fire_confidence=confidence
                )
                
                if n8n_success:
                    logger.info("📱 N8N alert sent successfully")
                    
                    # Send critical evacuation alert if people present
                    if people_count > 0:
                        alert_manager.send_critical_evacuation_alert(
                            floor_id=floor_id,
                            people_count=people_count,
                            camera_id=camera_id
                        )
                        logger.warning(f" CRITICAL: {people_count} people on floor during fire!")
            
            # Send to Laravel backend (EC2)
            alert_id = send_fire_alert_to_backend(
                camera_id=camera_id,
                camera_name=f"Camera {camera_id}",
                floor_id=floor_id,
                room=ROOM,
                screenshot_base64=screenshot_base64,
                confidence=confidence,
                fire_type=fire_type
            )
            
            return JSONResponse({
                "detected": True,
                "confidence": confidence,
                "type": fire_type,
                "method": method,
                "severity": "critical" if confidence > 0.8 else "high" if confidence > 0.6 else "medium",
                "alert_id": alert_id,
                "n8n_alert_sent": n8n_success,
                "people_on_floor": people_count,
                "message": f" Fire detected! ({method} detection - {confidence*100:.1f}% confidence)",
                "bbox": detection_result.get('bbox'),
                "screenshot_saved": True
            })
        else:
            return JSONResponse({
                "detected": False,
                "confidence": confidence,
                "type": "none",
                "method": method,
                "message": "No fire detected"
            })
            
    except Exception as e:
        logger.error(f" Error in fire detection: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ML Fire Detection",
        "version": "4.0.0-ML",
        "ml_model_available": ml_detector.model is not None,
        "detection_method": ml_detector.detection_method,
        "n8n_configured": bool(N8N_WEBHOOK_URL),
        "backend_api": LARAVEL_API_URL,
        "confidence_threshold": FIRE_CONFIDENCE_THRESHOLD
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ML Fire Detection Service",
        "version": "4.0.0-ML",
        "endpoints": {
            "detect": "/detect-fire-ml (POST)",
            "health": "/health (GET)",
            "stream": "/stream/{camera_id} (GET) - NEW!",
            "cameras": "/cameras (GET) - NEW!",
            "start_camera": "/start-camera/{camera_id} (POST) - NEW!",
            "stop_camera": "/stop-camera/{camera_id} (POST) - NEW!"
        },
        "ml_enabled": ml_detector.model is not None,
        "detection_method": ml_detector.detection_method,
        "live_cameras": list(active_cameras.keys())
    }


@app.get("/cameras")
async def get_cameras():
    """Get list of configured cameras"""
    cameras = load_cameras()
    return {
        "cameras": cameras,
        "active_cameras": list(active_cameras.keys())
    }


@app.get("/stream/{camera_id}")
async def stream_camera(camera_id: int):
    """
    Stream live camera feed with ML fire detection overlay
    Returns MJPEG stream that can be displayed in browser or dashboard
    """
    try:
        return StreamingResponse(
            generate_frames(camera_id),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    except Exception as e:
        logger.error(f"Error starting stream for camera {camera_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/start-camera/{camera_id}")
async def start_camera(camera_id: int):
    """Start monitoring a camera"""
    cap = get_camera(camera_id)
    if cap:
        return {
            "status": "success",
            "message": f"Camera {camera_id} started",
            "camera_id": camera_id
        }
    else:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found or failed to open")


@app.post("/stop-camera/{camera_id}")
async def stop_camera(camera_id: int):
    """Stop monitoring a camera"""
    release_camera(camera_id)
    return {
        "status": "success",
        "message": f"Camera {camera_id} stopped",
        "camera_id": camera_id
    }


if __name__ == "__main__":
    print("\n" + "="*80)
    print(" STARTING ML FIRE DETECTION SERVICE")
    print("="*80)
    print(f" Port: 8004 (ML Service)")
    print(f" Detection Method: {ml_detector.detection_method}")
    print(f" Confidence Threshold: {FIRE_CONFIDENCE_THRESHOLD*100}%")
    print(f" Backend API: {LARAVEL_API_URL}")
    print(f" N8N Webhook: {' Configured' if N8N_WEBHOOK_URL else ' Not configured'}")
    print(f" Model Path: {ML_MODEL_PATH}")
    print("="*80 + "\n")
    
    # Auto-start camera monitoring
    print("🎥 AUTO-STARTING CAMERA MONITORING...")
    cameras = load_cameras()
    if cameras:
        for cam in cameras:
            cam_id = cam['id']
            print(f"   Starting Camera {cam_id} ({cam['name']})...")
            
            # Start background monitoring thread
            monitor_thread = Thread(target=monitor_camera_background, args=(cam_id,), daemon=True)
            monitor_thread.start()
            
            time.sleep(1)  # Brief delay between cameras
        
        print(f" Started monitoring {len(cameras)} camera(s)")
        print(" Fire detection active - alerts will be sent automatically!")
    else:
        print("  No cameras configured in camera_config.json")
    
    print("="*80 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8004)
