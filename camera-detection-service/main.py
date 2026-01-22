"""
Camera Detection Service
Captures frames from cameras and runs both fire and face detection
Tracks presence on floors with 5-minute timer
"""
import cv2
import numpy as np
import requests
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import base64
from threading import Thread, Lock
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CONFIG = {
    'backend_api': 'http://localhost:8000/api/v1',
    'fire_service': 'http://localhost:8002',
    'face_service': 'http://localhost:8001',
    'camera_id': 0,
    'floor_id': 3,
    'room_location': 'Office',
    'detection_interval': 2.0,  # seconds between detections
    'fire_confidence_threshold': 0.3,
    'face_confidence_threshold': 0.6,
    'presence_timeout': 300,  # 5 minutes in seconds
}


class PresenceTracker:
    """Tracks people on floors with 5-minute timeout"""
    
    def __init__(self):
        self.presence_data: Dict[int, Dict] = {}  # employee_id -> {floor_id, last_seen, camera_id}
        self.lock = Lock()
        self.timeout_seconds = CONFIG['presence_timeout']
        
    def update_presence(self, employee_id: int, floor_id: int, camera_id: str):
        """Update or reset presence timer for employee"""
        with self.lock:
            current_time = datetime.now()
            
            if employee_id in self.presence_data:
                old_data = self.presence_data[employee_id]
                logger.info(f" Employee {employee_id} seen again on floor {floor_id} - resetting 5min timer")
            else:
                logger.info(f" Employee {employee_id} detected on floor {floor_id} - starting 5min timer")
                
            self.presence_data[employee_id] = {
                'floor_id': floor_id,
                'last_seen': current_time,
                'camera_id': camera_id,
            }
    
    def get_people_on_floor(self, floor_id: int) -> List[int]:
        """Get list of employee IDs currently on a floor (within 5 min)"""
        with self.lock:
            current_time = datetime.now()
            people = []
            
            for employee_id, data in list(self.presence_data.items()):
                if data['floor_id'] == floor_id:
                    time_since_seen = (current_time - data['last_seen']).total_seconds()
                    
                    if time_since_seen <= self.timeout_seconds:
                        people.append(employee_id)
                    else:
                        # Remove expired presence
                        logger.info(f" Employee {employee_id} expired from floor {floor_id} (>5min)")
                        del self.presence_data[employee_id]
            
            return people
    
    def cleanup_expired(self):
        """Remove all expired presence entries"""
        with self.lock:
            current_time = datetime.now()
            expired_ids = []
            
            for employee_id, data in self.presence_data.items():
                time_since_seen = (current_time - data['last_seen']).total_seconds()
                if time_since_seen > self.timeout_seconds:
                    expired_ids.append(employee_id)
            
            for employee_id in expired_ids:
                floor_id = self.presence_data[employee_id]['floor_id']
                logger.info(f" Employee {employee_id} expired from floor {floor_id}")
                del self.presence_data[employee_id]


class CameraDetectionService:
    """Main service that captures frames and runs detections"""
    
    def __init__(self):
        self.camera = None
        self.running = False
        self.presence_tracker = PresenceTracker()
        self.session = requests.Session()
        self.last_fire_report = None
        self.fire_cooldown = 15  # seconds
        
    def initialize_camera(self) -> bool:
        """Initialize camera feed"""
        try:
            self.camera = cv2.VideoCapture(CONFIG['camera_id'])
            if not self.camera.isOpened():
                logger.error(f"Failed to open camera {CONFIG['camera_id']}")
                return False
            
            # Set camera resolution
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            
            logger.info(f"✓ Camera {CONFIG['camera_id']} initialized")
            return True
        except Exception as e:
            logger.error(f"Camera initialization error: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from camera"""
        if not self.camera or not self.camera.isOpened():
            return None
        
        ret, frame = self.camera.read()
        if not ret:
            logger.warning("Failed to capture frame")
            return None
        
        return frame
    
    def frame_to_base64(self, frame: np.ndarray) -> str:
        """Convert frame to base64 string"""
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return base64.b64encode(buffer).decode('utf-8')
    
    def detect_fire(self, frame: np.ndarray) -> Optional[Dict]:
        """Send frame to fire detection service"""
        try:
            # Encode frame
            _, img_encoded = cv2.imencode('.jpg', frame)
            
            # Send to fire detection service
            files = {'file': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
            response = self.session.post(
                f"{CONFIG['fire_service']}/detect-fire",
                files=files,
                timeout=5
            )
            
            if response.ok:
                result = response.json()
                if result.get('fire_detected'):
                    return {
                        'confidence': result.get('confidence', 0),
                        'bbox': result.get('bounding_box', [0, 0, 0, 0])
                    }
        except Exception as e:
            logger.debug(f"Fire detection error: {e}")
        
        return None
    
    def detect_faces(self, frame: np.ndarray) -> List[Dict]:
        """Send frame to face detection service and identify people"""
        try:
            # Encode frame
            _, img_encoded = cv2.imencode('.jpg', frame)
            
            # Detect faces
            files = {'file': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
            response = self.session.post(
                f"{CONFIG['face_service']}/detect-faces",
                files=files,
                timeout=5
            )
            
            if not response.ok:
                return []
            
            result = response.json()
            faces = result.get('faces', [])
            
            # Identify each face
            identified_people = []
            for face in faces:
                embedding = face.get('embedding')
                if not embedding:
                    continue
                
                # Call identification endpoint
                identify_response = self.session.post(
                    f"{CONFIG['backend_api']}/employees/identify-face",
                    json={'embedding': embedding},
                    timeout=5
                )
                
                if identify_response.ok:
                    person = identify_response.json()
                    if person.get('matched'):
                        identified_people.append({
                            'employee_id': person.get('employee_id'),
                            'name': person.get('name'),
                            'confidence': person.get('confidence', 0),
                            'bbox': face.get('bbox')
                        })
            
            return identified_people
            
        except Exception as e:
            logger.debug(f"Face detection error: {e}")
            return []
    
    def report_fire(self, detection: Dict):
        """Report fire to backend"""
        # Check cooldown
        if self.last_fire_report:
            time_since = (datetime.now() - self.last_fire_report).total_seconds()
            if time_since < self.fire_cooldown:
                return
        
        endpoint = f"{CONFIG['backend_api']}/fire-detections/report"
        
        payload = {
            'camera_id': CONFIG['camera_id'],
            'floor_id': CONFIG['floor_id'],
            'detection_type': 'fire',
            'confidence': detection['confidence'],
            'room_location': CONFIG['room_location'],
            'bounding_box': detection['bbox'],
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            logger.warning(f" FIRE REPORTED! Event ID: {result.get('fire_event_id')}")
            self.last_fire_report = datetime.now()
        except Exception as e:
            logger.error(f"Failed to report fire: {e}")
    
    def report_presence(self, person: Dict):
        """Report person presence to backend"""
        endpoint = f"{CONFIG['backend_api']}/presence/log"
        
        payload = {
            'employee_id': person['employee_id'],
            'floor_id': CONFIG['floor_id'],
            'room_location': CONFIG['room_location'],
            'camera_id': str(CONFIG['camera_id']),
            'confidence': person['confidence'] * 100,
            'event_type': 'detected'
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=10)
            if response.ok:
                logger.info(f"✓ Presence logged: {person['name']} on floor {CONFIG['floor_id']}")
                
                # Update local presence tracker
                self.presence_tracker.update_presence(
                    person['employee_id'],
                    CONFIG['floor_id'],
                    str(CONFIG['camera_id'])
                )
        except Exception as e:
            logger.error(f"Failed to report presence: {e}")
    
    def run(self):
        """Main detection loop"""
        if not self.initialize_camera():
            logger.error("Cannot start - camera initialization failed")
            return
        
        self.running = True
        frame_count = 0
        
        logger.info("🎥 Camera Detection Service STARTED")
        logger.info(f"   Camera: {CONFIG['camera_id']}")
        logger.info(f"   Floor: {CONFIG['floor_id']} ({CONFIG['room_location']})")
        logger.info(f"   Presence Timeout: {CONFIG['presence_timeout']}s (5 minutes)")
        
        try:
            while self.running:
                frame = self.capture_frame()
                if frame is None:
                    time.sleep(1)
                    continue
                
                frame_count += 1
                
                # Run fire detection
                fire_result = self.detect_fire(frame)
                if fire_result and fire_result['confidence'] >= CONFIG['fire_confidence_threshold']:
                    logger.warning(f" Fire detected! Confidence: {fire_result['confidence']:.2%}")
                    self.report_fire(fire_result)
                
                # Run face detection every frame
                people = self.detect_faces(frame)
                for person in people:
                    if person['confidence'] >= CONFIG['face_confidence_threshold']:
                        logger.info(f"👤 Detected: {person['name']} (confidence: {person['confidence']:.2%})")
                        self.report_presence(person)
                
                # Cleanup expired presence entries every 50 frames
                if frame_count % 50 == 0:
                    self.presence_tracker.cleanup_expired()
                
                # Log status every 100 frames
                if frame_count % 100 == 0:
                    people_on_floor = self.presence_tracker.get_people_on_floor(CONFIG['floor_id'])
                    logger.info(f" Status: {frame_count} frames | {len(people_on_floor)} people on floor {CONFIG['floor_id']}")
                
                # Wait before next detection
                time.sleep(CONFIG['detection_interval'])
                
        except KeyboardInterrupt:
            logger.info("Service stopped by user")
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """Stop service and release camera"""
        self.running = False
        if self.camera:
            self.camera.release()
        logger.info("Camera Detection Service stopped")


if __name__ == "__main__":
    service = CameraDetectionService()
    service.run()
