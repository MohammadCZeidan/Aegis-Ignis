"""
Fire Detection Service - Microservice
Reports fire detection metadata to Laravel Backend API.
Includes health endpoints, environment configuration, and proper error handling.
"""
import cv2
import numpy as np
import requests
import time
import logging
import os
import sys
import base64
from typing import Optional, Dict, List
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.alert_manager import AlertManager

load_dotenv()

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FireDetectionConfig:
    API_BASE_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000/api/v1')
    CAMERA_ID = int(os.getenv('CAMERA_ID', '1'))
    CAMERA_NAME = None
    FLOOR_ID = None
    ROOM_LOCATION = None
    DETECTION_INTERVAL = float(os.getenv('DETECTION_INTERVAL', '1.0'))
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.85'))
    COOLDOWN_SECONDS = int(os.getenv('COOLDOWN_SECONDS', '5'))
    SERVICE_PORT = int(os.getenv('FIRE_SERVICE_PORT', '8002'))
    
    @classmethod
    def update_camera_location(cls, floor_id: int, room_location: str, camera_name: str = None):
        cls.FLOOR_ID = floor_id
        cls.ROOM_LOCATION = room_location
        if camera_name:
            cls.CAMERA_NAME = camera_name

# Legacy CONFIG for backward compatibility
CONFIG = {
    'api_base_url': FireDetectionConfig.API_BASE_URL,
    'camera_id': FireDetectionConfig.CAMERA_ID,
    'camera_name': FireDetectionConfig.CAMERA_NAME,
    'floor_id': FireDetectionConfig.FLOOR_ID,
    'room_location': FireDetectionConfig.ROOM_LOCATION,
    'detection_interval': FireDetectionConfig.DETECTION_INTERVAL,
    'confidence_threshold': FireDetectionConfig.CONFIDENCE_THRESHOLD,
    'cooldown_seconds': FireDetectionConfig.COOLDOWN_SECONDS,
    'service_port': FireDetectionConfig.SERVICE_PORT,
}


class CameraLocationService:
    @staticmethod
    def fetch_camera_location() -> bool:
        """Fetch camera's floor and location from database on startup."""
        try:
            camera_id = FireDetectionConfig.CAMERA_ID
            logger.info(f"Fetching location for Camera {camera_id}...")
            
            response = requests.get(
                f"{FireDetectionConfig.API_BASE_URL}/cameras/{camera_id}",
                timeout=3
            )
            
            if response.status_code == 200:
                camera_data = response.json().get('data', {})
                floor_id = camera_data.get('floor_id', 3)
                room_location = camera_data.get('location', 'Unknown')
                camera_name = camera_data.get('name', f'Camera {camera_id}')
                
                FireDetectionConfig.update_camera_location(floor_id, room_location, camera_name)
                CONFIG['floor_id'] = floor_id
                CONFIG['room_location'] = room_location
                CONFIG['camera_name'] = camera_name
                
                CameraLocationService._log_camera_info(camera_data, camera_id)
                return True
            else:
                logger.warning(f"Camera {camera_id} not in database, using defaults")
                CameraLocationService._use_default_location()
                return False
        except Exception as e:
            logger.error(f"Error fetching camera location: {e}")
            CameraLocationService._use_default_location()
            return False
    
    @staticmethod
    def _log_camera_info(camera_data: dict, camera_id: int):
        logger.info(f"Camera location from database:")
        logger.info(f"   Name: {camera_data.get('name', 'Camera ' + str(camera_id))}")
        logger.info(f"   Floor: {FireDetectionConfig.FLOOR_ID}")
        logger.info(f"   Location: {FireDetectionConfig.ROOM_LOCATION}")
    
    @staticmethod
    def _use_default_location():
        """Fetch first available floor as fallback."""
        try:
            response = requests.get(
                f"{FireDetectionConfig.API_BASE_URL}/floors",
                timeout=3
            )
            if response.status_code == 200:
                floors = response.json().get('data', [])
                if floors:
                    first_floor = floors[0]
                    floor_id = first_floor.get('id', 1)
                    floor_name = first_floor.get('name', 'Main')
                    camera_id = FireDetectionConfig.CAMERA_ID
                    default_name = f'Camera {camera_id}'
                    FireDetectionConfig.update_camera_location(floor_id, f'{floor_name} Hall', default_name)
                    CONFIG['floor_id'] = floor_id
                    CONFIG['room_location'] = f'{floor_name} Hall'
                    CONFIG['camera_name'] = default_name
                    logger.info(f"Using first available floor: {floor_name} (ID: {floor_id})")
                    return
        except Exception as e:
            logger.error(f"Error fetching floors: {e}")
        
        # Ultimate fallback - let backend handle it
        camera_id = FireDetectionConfig.CAMERA_ID
        default_name = f'Camera {camera_id}'
        FireDetectionConfig.update_camera_location(None, 'Unknown', default_name)
        CONFIG['floor_id'] = None
        CONFIG['room_location'] = 'Unknown'
        CONFIG['camera_name'] = default_name

# Backward compatibility function
def fetch_camera_location() -> bool:
    return CameraLocationService.fetch_camera_location()

# FastAPI app for health checks
app = FastAPI(title="Fire Detection Service", version="1.0.0")


class FireColorDetector:
    """Handles fire color detection using HSV color space."""
    
    # Fire color ranges for HSV detection
    WHITE_LOWER = np.array([0, 0, 200])
    WHITE_UPPER = np.array([180, 60, 255])
    
    ORANGE_LOWER = np.array([8, 220, 248])
    ORANGE_UPPER = np.array([18, 255, 255])
    
    RED_LOWER_1 = np.array([0, 100, 150])
    RED_UPPER_1 = np.array([10, 255, 255])
    RED_LOWER_2 = np.array([165, 100, 150])
    RED_UPPER_2 = np.array([180, 255, 255])
    
    YELLOW_LOWER = np.array([18, 200, 250])
    YELLOW_UPPER = np.array([30, 255, 255])
    
    BRIGHTNESS_THRESHOLD = 253
    MIN_CONTOUR_AREA = 3000
    MIN_FILL_RATIO = 0.4
    
    @staticmethod
    def create_color_masks(hsv_frame):
        """Create color masks for different fire colors."""
        mask_white = cv2.inRange(hsv_frame, FireColorDetector.WHITE_LOWER, FireColorDetector.WHITE_UPPER)
        mask_orange = cv2.inRange(hsv_frame, FireColorDetector.ORANGE_LOWER, FireColorDetector.ORANGE_UPPER)
        
        mask_red = cv2.bitwise_or(
            cv2.inRange(hsv_frame, FireColorDetector.RED_LOWER_1, FireColorDetector.RED_UPPER_1),
            cv2.inRange(hsv_frame, FireColorDetector.RED_LOWER_2, FireColorDetector.RED_UPPER_2)
        )
        
        mask_yellow = cv2.inRange(hsv_frame, FireColorDetector.YELLOW_LOWER, FireColorDetector.YELLOW_UPPER)
        
        return cv2.bitwise_or(mask_white, cv2.bitwise_or(mask_orange, cv2.bitwise_or(mask_red, mask_yellow)))
    
    @staticmethod
    def apply_brightness_filter(frame, color_mask):
        """Apply brightness filtering to color mask."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, ultra_bright = cv2.threshold(gray, FireColorDetector.BRIGHTNESS_THRESHOLD, 255, cv2.THRESH_BINARY)
        return cv2.bitwise_and(color_mask, ultra_bright)
    
    @staticmethod
    def extract_detections_from_contours(contours, mask):
        """Extract fire detections from contours."""
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > FireColorDetector.MIN_CONTOUR_AREA:
                detection = FireColorDetector._process_contour(contour, mask)
                if detection:
                    detections.append(detection)
        
        return sorted(detections, key=lambda d: d['confidence'], reverse=True)
    
    @staticmethod
    def _process_contour(contour, mask):
        """Process individual contour to extract detection data."""
        x, y, w, h = cv2.boundingRect(contour)
        roi = mask[y:y+h, x:x+w]
        fill_ratio = np.sum(roi > 0) / (w * h)
        
        if fill_ratio >= FireColorDetector.MIN_FILL_RATIO:
            confidence = min(1.0, fill_ratio * 1.5)
            
            if confidence >= CONFIG['confidence_threshold']:
                return {
                    'bbox': [int(x), int(y), int(w), int(h)],
                    'confidence': float(confidence),
                    'area': int(cv2.contourArea(contour))
                }
        return None

class CameraManager:
    """Handles camera initialization and management."""
    
    @staticmethod
    def initialize_camera(camera_id: int = 0) -> cv2.VideoCapture:
        """Initialize camera feed - camera_id for DB, physical camera always 0."""
        try:
            camera = cv2.VideoCapture(0)  # Physical webcam
            if not camera.isOpened():
                logger.error("Failed to open physical webcam (using camera 0)")
                return None
            logger.info(f"Physical webcam initialized (Database ID: {camera_id})")
            return camera
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            return None

class ScreenshotHandler:
    """Handles screenshot capture and upload functionality."""
    
    def __init__(self, session: requests.Session):
        self.session = session
    
    def save_screenshot(self, frame: np.ndarray, detection: Dict) -> Optional[str]:
        """Upload fire detection screenshot directly to EC2 Laravel storage."""
        try:
            filename = self._generate_filename()
            annotated_frame = self._annotate_frame(frame, detection)
            encoded_buffer = self._encode_frame(annotated_frame)
            
            if encoded_buffer is not None:
                return self._upload_or_encode(filename, encoded_buffer)
            else:
                logger.error("Failed to encode screenshot")
                return None
                
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_filename(self) -> str:
        """Generate unique filename for screenshot."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"fire_cam{CONFIG['camera_id']}_floor{CONFIG['floor_id']}_{timestamp}.jpg"
    
    def _annotate_frame(self, frame: np.ndarray, detection: Dict) -> np.ndarray:
        """Draw bounding box and confidence on frame."""
        annotated_frame = frame.copy()
        bbox = detection['bbox']
        cv2.rectangle(annotated_frame, (bbox[0], bbox[1]), 
                     (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 0, 255), 3)
        cv2.putText(annotated_frame, f"FIRE {detection['confidence']:.0%}", 
                   (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        return annotated_frame
    
    def _encode_frame(self, frame: np.ndarray) -> Optional[bytes]:
        """Encode frame as JPEG."""
        success, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return buffer.tobytes() if success else None
    
    def _upload_or_encode(self, filename: str, buffer: bytes) -> Optional[str]:
        """Encode screenshot as base64 (upload disabled for now)."""
        # Direct base64 encoding - EC2 upload endpoint not available
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        logger.info("Screenshot encoded as base64")
        return image_base64
    
    def _upload_to_storage(self, filename: str, buffer: bytes) -> Optional[str]:
        """Upload file to EC2 Laravel storage."""
        files = {'file': (filename, buffer, 'image/jpeg')}
        data = {'disk': 'public', 'folder': 'alerts'}
        
        response = self.session.post(
            f"{CONFIG['api_base_url']}/upload",
            files=files,
            data=data,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            return result.get('path', f"alerts/{filename}")
        else:
            logger.error(f"Upload failed: {response.status_code}")
            return None

class DetectionReporter:
    """Handles fire detection reporting to backend API."""
    
    def __init__(self, session: requests.Session):
        self.session = session
        self.screenshot_handler = ScreenshotHandler(session)
    
    def report_detection(self, detection: Dict, frame: np.ndarray) -> bool:
        """Report fire detection to Laravel backend API with screenshot."""
        try:
            screenshot_data = self.screenshot_handler.save_screenshot(frame, detection)
            payload = self._build_payload(detection, screenshot_data)
            
            response = self._send_report(payload)
            
            if response:
                alert_id = response.get('alert', {}).get('id', 'Unknown')
                logger.info(f"Detection reported successfully: Alert ID {alert_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error reporting detection: {e}")
            return False
    
    def _build_payload(self, detection: Dict, screenshot_data: Optional[str]) -> Dict:
        """Build API payload for detection report."""
        confidence_percentage = round(detection['confidence'] * 100, 2)
        severity = 'critical' if detection['confidence'] > 0.7 else 'warning'
        
        base_payload = {
            'camera_name': CONFIG['camera_name'] or f"Camera {CONFIG['camera_id']}",
            'event_type': 'fire',
            'severity': severity,
            'camera_id': CONFIG['camera_id'],
            'floor_id': CONFIG['floor_id'],
            'room': CONFIG['room_location'],
            'confidence': confidence_percentage,
            'fire_type': 'fire',
            'detected_at': datetime.now().isoformat()
        }
        
        if screenshot_data and not screenshot_data.startswith('http'):
            base_payload['image'] = screenshot_data  # Base64 data
        else:
            base_payload['screenshot_path'] = screenshot_data  # URL path
        
        return base_payload
    
    def _send_report(self, payload: Dict) -> Optional[Dict]:
        """Send detection report to API endpoint."""
        endpoint = f"{CONFIG['api_base_url']}/alerts/fire"
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            }
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"API error: {e.response.status_code} - {e.response.text}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: Cannot reach backend at {endpoint}")
        except requests.exceptions.Timeout:
            logger.error("Request timeout: Backend took too long to respond")
        
        return None

class FireDetectionService:
    """Fire detection service with API reporting."""
    
    def __init__(self):
        self.camera = None
        self.running = False
        self.last_detection_time = None
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.detection_reporter = DetectionReporter(self.session)
        # Initialize AlertManager for WhatsApp alerts
        self.alert_manager = AlertManager(n8n_webhook_url=os.getenv('N8N_WEBHOOK_URL'))
        
    def initialize_camera(self, camera_id: int = 0) -> bool:
        """Initialize camera feed."""
        self.camera = CameraManager.initialize_camera(camera_id)
        return self.camera is not None
    
    def detect_fire_colors(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect fire-like colors in frame using HSV color space.
        Returns list of detections with bounding boxes and confidence.
        """
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            color_mask = FireColorDetector.create_color_masks(hsv)
            final_mask = FireColorDetector.apply_brightness_filter(frame, color_mask)
            contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            return FireColorDetector.extract_detections_from_contours(contours, final_mask)
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def report_detection(self, detection: Dict, frame: np.ndarray) -> bool:
        """Report fire detection to Laravel backend API with screenshot."""
        return self.detection_reporter.report_detection(detection, frame)
    
    def can_report(self) -> bool:
        """Check if enough time has passed since last detection (cooldown)."""
        if self.last_detection_time is None:
            return True
        
        elapsed = time.time() - self.last_detection_time
        return elapsed >= CONFIG['cooldown_seconds']
    
    def run(self):
        """Main detection loop."""
        service_runner = ServiceRunner(self)
        service_runner.run()
    
    def stop(self):
        """Stop the service and release resources."""
        self.running = False
        if self.camera:
            self.camera.release()
        logger.info("Fire Detection Service stopped")

class ServiceRunner:
    """Handles the main service execution loop."""
    
    def __init__(self, fire_service: FireDetectionService):
        self.fire_service = fire_service
    
    def run(self):
        """Execute the main service loop."""
        self._initialize_service()
        
        if not self._prepare_camera():
            logger.error("Cannot start: Camera initialization failed")
            return
        
        self._start_monitoring_loop()
    
    def _initialize_service(self):
        """Initialize service configuration."""
        fetch_camera_location()
        
    def _prepare_camera(self) -> bool:
        """Prepare camera for monitoring."""
        return self.fire_service.initialize_camera(CONFIG['camera_id'])
    
    def _start_monitoring_loop(self):
        """Start the main monitoring loop."""
        self.fire_service.running = True
        self._log_service_info()
        
        frame_count = 0
        
        try:
            while self.fire_service.running:
                if self._process_frame(frame_count):
                    frame_count += 1
                    
                if frame_count % 100 == 0:
                    logger.info(f"Monitoring... ({frame_count} frames processed)")
                
                time.sleep(CONFIG['detection_interval'])
                
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
        finally:
            self.fire_service.stop()
    
    def _log_service_info(self):
        """Log service startup information."""
        logger.info("Fire Detection Service started")
        logger.info(f"   Physical Camera: Webcam 0")
        logger.info(f"   Database Camera ID: {CONFIG['camera_id']}")
        logger.info(f"   Floor ID: {CONFIG['floor_id']}")
        logger.info(f"   Room: {CONFIG['room_location']}")
        logger.info(f"   Backend API: {CONFIG['api_base_url']}")
        logger.info(f"   Confidence threshold: {CONFIG['confidence_threshold']}")
    
    def _process_frame(self, frame_count: int) -> bool:
        """Process a single frame from camera."""
        ret, frame = self.fire_service.camera.read()
        if not ret:
            logger.warning("Failed to read frame from camera")
            time.sleep(1)
            return False
        
        detections = self.fire_service.detect_fire_colors(frame)
        
        if detections and self.fire_service.can_report():
            self._handle_detection(detections[0], frame)
        
        return True
    
    def _handle_detection(self, detection: Dict, frame: np.ndarray):
        """Handle a positive fire detection."""
        logger.warning(f"FIRE DETECTED! Confidence: {detection['confidence']:.2%}")
        
        # Report to backend
        if self.fire_service.report_detection(detection, frame):
            self.fire_service.last_detection_time = time.time()
            
            # Send WhatsApp alert with floor occupancy
            try:
                # Get current floor occupancy
                occupancy_data = self.fire_service.alert_manager.get_floor_occupancy(CONFIG['floor_id'])
                people_detected = occupancy_data.get('people_details', [])
                people_count = len(people_detected)
                
                # Send fire alert via WhatsApp and N8N
                self.fire_service.alert_manager.send_fire_alert(
                    floor_id=CONFIG['floor_id'],
                    camera_id=CONFIG['camera_id'],
                    camera_name=CONFIG['camera_name'] or f"Camera {CONFIG['camera_id']}",
                    room=CONFIG['room_location'] or 'Unknown',
                    people_detected=people_detected,
                    fire_type='fire',
                    confidence=detection['confidence'],
                    severity='critical' if detection['confidence'] > 0.7 else 'warning'
                )
                logger.info(f"WhatsApp alert sent for fire on Floor {CONFIG['floor_id']}")
            except Exception as e:
                logger.error(f"Failed to send WhatsApp alert: {e}")


# Global service instance
fire_service = FireDetectionService()


# FastAPI Endpoints
from fastapi import File, UploadFile, Form

@app.post("/detect-fire")
async def detect_fire(
    file: UploadFile = File(...),
    camera_id: str = Form(None),
    floor_id: int = Form(None),
    room_location: str = Form(None)
):
    """
    Analyze image for fire detection.
    Called by camera detection service.
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Analyze frame using existing detection method
        detections = fire_service.detect_fire_colors(frame)
        
        if detections:
            detection = detections[0]  # Take the first detection
            confidence = detection['confidence']
            
            return {
                "fire_detected": True,
                "detected": True,
                "confidence": confidence,
                "bounding_box": detection['bbox'],
                "type": "fire",
                "severity": "critical" if confidence > 0.7 else "warning"
            }
        else:
            return {
                "fire_detected": False,
                "detected": False,
                "confidence": 0.0,
                "type": "none"
            }
            
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    camera_status = "healthy" if fire_service.camera and fire_service.camera.isOpened() else "unhealthy"
    
    return {
        "status": "healthy" if fire_service.running else "stopped",
        "service": "fire-detection",
        "version": "1.0.0",
        "camera": {
            "status": camera_status,
            "id": CONFIG['camera_id']
        },
        "configuration": {
            "floor_id": CONFIG['floor_id'],
            "room_location": CONFIG['room_location'],
            "backend_api": CONFIG['api_base_url']
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/status")
async def get_status():
    """Detailed service status."""
    return {
        "running": fire_service.running,
        "last_detection": fire_service.last_detection_time,
        "config": CONFIG
    }


@app.post("/start")
async def start_service():
    """Start the fire detection service."""
    if fire_service.running:
        return {"message": "Service is already running"}
    
    # Start in background
    import threading
    thread = threading.Thread(target=fire_service.run, daemon=True)
    thread.start()
    
    return {"message": "Service started", "status": "running"}


@app.post("/stop")
async def stop_service():
    """Stop the fire detection service."""
    fire_service.stop()
    return {"message": "Service stopped", "status": "stopped"}


if __name__ == "__main__":
    # Start FastAPI server for health checks
    logger.info("Starting Fire Detection Microservice...")
    
    # Start detection service in background thread
    import threading
    detection_thread = threading.Thread(target=fire_service.run, daemon=True)
    detection_thread.start()
    
    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=CONFIG['service_port'])
