"""
Advanced Fire Detection Service with ML Integration
- ML-based fire and smoke detection using YOLOv8
- Automatic fallback to color-based detection
- N8N webhook integration for WhatsApp/Voice alerts
- AI-powered emergency communication
"""
import cv2
import numpy as np
import requests
import time
import logging
import os
import sys
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import base64

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
LARAVEL_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000/api/v1')
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')
ML_MODEL_PATH = os.getenv('ML_MODEL_PATH', '../ml_models/weights/fire_detection.pt')
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
USE_ML_DETECTION = os.getenv('USE_ML_DETECTION', 'true').lower() == 'true'
USE_COLOR_FALLBACK = os.getenv('USE_COLOR_FALLBACK', 'true').lower() == 'true'

# Legacy thresholds for color-based detection
CONFIDENCE_THRESHOLD_WARNING = 0.08  # Ultra-sensitive for lighters and small flames
CONFIDENCE_THRESHOLD_ALERT = 0.20     # Lower threshold for faster critical alerts

app = FastAPI(title="ML Fire Detection Service", version="3.0.0")

# Initialize ML detector and alert manager
ml_detector = MLFireDetector(
    model_path=ML_MODEL_PATH if USE_ML_DETECTION else None,
    confidence_threshold=CONFIDENCE_THRESHOLD,
    use_color_fallback=USE_COLOR_FALLBACK
)

alert_manager = AlertManager(n8n_webhook_url=N8N_WEBHOOK_URL)


class FireDetectionResult(BaseModel):
    detected: bool
    type: str  # 'smoke', 'small_flame', 'large_flame', 'none'
    severity: str  # 'warning', 'alert', 'critical'
    confidence: float
    bbox: Optional[List[int]] = None
    area_percentage: float = 0.0
    message: str = ""


class AdvancedFireDetector:
    """
    Advanced fire detection with smoke and flame differentiation.
    """
    
    def __init__(self):
        self.frame_width = 640
        self.frame_height = 480
        
        # Detection thresholds - ULTRA SENSITIVE for immediate detection
        self.small_fire_threshold = 0.001  # 0.1% of frame (ULTRA TINY - lighter flames)
        self.large_fire_threshold = 0.03  # 3% of frame (larger fire)
        
    def detect_black_smoke(self, frame: np.ndarray) -> Dict:
        """
        Detect black smoke using color and texture analysis.
        Black smoke appears as dark, semi-transparent regions.
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect dark regions (smoke is typically dark)
        _, dark_mask = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY_INV)
        
        # Convert to HSV for better smoke detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Black/gray smoke HSV range
        lower_smoke = np.array([0, 0, 0])
        upper_smoke = np.array([180, 100, 100])
        smoke_mask = cv2.inRange(hsv, lower_smoke, upper_smoke)
        
        # Combine masks
        combined_mask = cv2.bitwise_and(dark_mask, smoke_mask)
        
        # Apply morphological operations
        kernel = np.ones((7, 7), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        total_area = 0
        largest_contour = None
        largest_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum area
                total_area += area
                if area > largest_area:
                    largest_area = area
                    largest_contour = contour
        
        frame_area = frame.shape[0] * frame.shape[1]
        smoke_percentage = (total_area / frame_area) * 100
        
        if largest_contour is not None and smoke_percentage > 2:
            x, y, w, h = cv2.boundingRect(largest_contour)
            confidence = min(smoke_percentage / 20, 1.0)  # Normalize to 0-1
            
            return {
                'detected': True,
                'bbox': [x, y, x+w, y+h],
                'confidence': confidence,
                'area_percentage': smoke_percentage
            }
        
        return {'detected': False}
    
    def detect_flames(self, frame: np.ndarray) -> Dict:
        """
        Detect flames using advanced color, brightness, and shape analysis.
        Distinguishes between small and large fires while avoiding false positives.
        """
        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Define flame color ranges - ULTRA SENSITIVE for lighters and bright sources
        # Range 1: Bright Red flames - ULTRA SENSITIVE
        lower_red1 = np.array([0, 20, 70])  # MUCH lower saturation and value for lighters
        upper_red1 = np.array([15, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        
        # Range 2: Orange-Yellow flames - ULTRA CAPTURES LIGHTERS
        lower_red2 = np.array([5, 15, 70])  # Much wider range, ultra low thresholds
        upper_red2 = np.array([50, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        
        # Range 3: Bright white (for very bright lighter flames)
        lower_white = np.array([0, 0, 140])  # Lower threshold to catch lighter flames
        upper_white = np.array([180, 100, 255])
        mask3 = cv2.inRange(hsv, lower_white, upper_white)
        
        # Combine all masks including bright white
        flame_mask = cv2.bitwise_or(mask1, cv2.bitwise_or(mask2, mask3))
        
        # Additional brightness check - fire is bright
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, bright_mask = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY)  # ULTRA LOW threshold for lighter flames
        
        # Combine with brightness - fire must be both colored AND bright
        flame_mask = cv2.bitwise_and(flame_mask, bright_mask)
        
        # Apply morphological operations
        kernel = np.ones((5, 5), np.uint8)
        flame_mask = cv2.morphologyEx(flame_mask, cv2.MORPH_CLOSE, kernel)
        flame_mask = cv2.morphologyEx(flame_mask, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(flame_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        total_area = 0
        largest_contour = None
        largest_area = 0
        all_boxes = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10:  # ULTRA SENSITIVE - catches even tiny lighter flames
                # Skip overly strict shape analysis for small flames
                x, y, w, h = cv2.boundingRect(contour)
                
                # Very lenient checks for tiny bright sources
                if area < 300:  # For very small flames (lighters), skip all shape checks
                    total_area += area
                    all_boxes.append([x, y, x+w, y+h])
                    if area > largest_area:
                        largest_area = area
                        largest_contour = contour
                    continue
                
                # For larger areas, do minimal shape filtering
                perimeter = cv2.arcLength(contour, True)
                if perimeter > 0:
                    circularity = 4 * np.pi * area / (perimeter * perimeter)
                    # Only reject perfect circles (like faces)
                    if circularity > 0.92:
                        continue
                
                # Very lenient aspect ratio
                aspect_ratio = h / w if w > 0 else 0
                if aspect_ratio < 0.15:  # Very lenient
                    continue
                
                total_area += area
                all_boxes.append([x, y, x+w, y+h])
                
                if area > largest_area:
                    largest_area = area
                    largest_contour = contour
        
        if largest_contour is not None:
            frame_area = frame.shape[0] * frame.shape[1]
            flame_percentage = (total_area / frame_area) * 100
            
            x, y, w, h = cv2.boundingRect(largest_contour)
            # Ultra-sensitive confidence - any flame gets high confidence
            confidence = min(max(flame_percentage / 1.5, 0.4), 1.0)  # Minimum 40% confidence for any flame
            
            # Determine fire size
            is_large = flame_percentage > (self.large_fire_threshold * 100)
            is_small = not is_large and flame_percentage > (self.small_fire_threshold * 100)
            
            return {
                'detected': True,
                'bbox': [x, y, x+w, y+h],
                'all_boxes': all_boxes,
                'confidence': confidence,
                'area_percentage': flame_percentage,
                'is_large': is_large,
                'is_small': is_small
            }
        
        return {'detected': False}
    
    def analyze_frame(self, frame: np.ndarray) -> FireDetectionResult:
        """
        Comprehensive fire analysis of a frame.
        Returns detection type and severity.
        """
        # Resize for consistent processing
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        
        # Check for smoke first
        smoke_result = self.detect_black_smoke(frame)
        
        # Check for flames
        flame_result = self.detect_flames(frame)
        
        # Determine result based on detections
        if flame_result['detected']:
            if flame_result['is_large']:
                return FireDetectionResult(
                    detected=True,
                    type='large_flame',
                    severity='critical',
                    confidence=flame_result['confidence'],
                    bbox=flame_result['bbox'],
                    area_percentage=flame_result['area_percentage'],
                    message="CRITICAL: Large fire detected! Immediate evacuation required!"
                )
            elif flame_result['is_small']:
                return FireDetectionResult(
                    detected=True,
                    type='small_flame',
                    severity='alert',
                    confidence=flame_result['confidence'],
                    bbox=flame_result['bbox'],
                    area_percentage=flame_result['area_percentage'],
                    message="ALERT: Small fire detected! Monitor closely and prepare to evacuate."
                )
            else:
                return FireDetectionResult(
                    detected=True,
                    type='small_flame',
                    severity='warning',
                    confidence=flame_result['confidence'],
                    bbox=flame_result['bbox'],
                    area_percentage=flame_result['area_percentage'],
                    message="WARNING: Possible fire detected. Investigating..."
                )
        
        elif smoke_result['detected']:
            return FireDetectionResult(
                detected=True,
                type='smoke',
                severity='warning',
                confidence=smoke_result['confidence'],
                bbox=smoke_result['bbox'],
                area_percentage=smoke_result['area_percentage'],
                message="WARNING: Smoke detected! Possible fire hazard."
            )
        
        return FireDetectionResult(
            detected=False,
            type='none',
            severity='normal',
            confidence=0.0,
            message="No fire or smoke detected."
        )


# Global detector instance
detector = AdvancedFireDetector()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ML Fire Detection API",
        "version": "3.0.0",
        "docs": "/docs",
        "health": "/health",
        "detection_method": ml_detector.get_detection_method(),
        "ml_available": ml_detector.is_ml_available(),
        "n8n_configured": N8N_WEBHOOK_URL is not None
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "features": ["ml_detection", "smoke_detection", "flame_detection", "n8n_integration"],
        "detection_method": ml_detector.get_detection_method(),
        "ml_model_loaded": ml_detector.is_ml_available()
    }


@app.post("/detect-fire-ml")
async def detect_fire_ml(
    file: UploadFile = File(...),
    camera_id: int = Form(...),
    camera_name: str = Form("Unknown Camera"),
    floor_id: int = Form(...),
    room_location: str = Form("Unknown Room"),
    send_n8n_alert: bool = Form(True)
):
    """
    ML-based fire detection with N8N alert integration.
    Detects fire using YOLOv8 ML model (or color fallback).
    Sends alerts to N8N for WhatsApp/Voice notifications.
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Detect fire using ML
        result = ml_detector.detect(frame, return_annotated=False)
        
        # If fire detected, send alerts
        if result['detected'] and result['confidence'] >= CONFIDENCE_THRESHOLD:
            logger.info(f"FIRE DETECTED! Type: {result['type']}, Confidence: {result['confidence']:.2%}, Method: {result['method']}")
            
            # Save screenshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_filename = f"fire_cam{camera_id}_floor{floor_id}_{timestamp}.jpg"
            screenshot_dir = os.path.join("..", "backend-laravel", "public", "storage", "alerts")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(screenshot_dir, screenshot_filename)
            cv2.imwrite(screenshot_path, frame)
            
            # Get floor occupancy
            occupancy_data = alert_manager.get_floor_occupancy(floor_id)
            people_count = occupancy_data['people_count']
            people_details = occupancy_data['people_details']
            
            # Send N8N alert if enabled
            if send_n8n_alert:
                alert_success = alert_manager.send_fire_alert(
                    floor_id=floor_id,
                    camera_id=camera_id,
                    camera_name=camera_name,
                    room=room_location,
                    people_detected=people_details,
                    fire_type=result['type'],
                    confidence=result['confidence'],
                    severity=result['severity'],
                    screenshot_path=f"storage/alerts/{screenshot_filename}"
                )
                
                # Send CRITICAL alert if people present
                if people_count > 0:
                    alert_manager.send_critical_evacuation_alert(
                        floor_id=floor_id,
                        camera_id=camera_id,
                        people_count=people_count,
                        fire_confidence=result['confidence']
                    )
            
            return {
                "detected": True,
                "detection_method": result['method'],
                "fire_type": result['type'],
                "severity": result['severity'],
                "confidence": result['confidence'],
                "area_percentage": result['area_percentage'],
                "bbox": result['bbox'],
                "people_on_floor": people_count,
                "screenshot_path": f"storage/alerts/{screenshot_filename}",
                "alert_sent": send_n8n_alert,
                "message": f"{result['type'].upper()} detected on Floor {floor_id} ({people_count} people present)"
            }
        
        return {
            "detected": False,
            "detection_method": result['method'],
            "message": "No fire detected"
        }
    
    except Exception as e:
        logger.error(f"ML Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-fire")
async def detect_fire(
    file: UploadFile = File(...),
    camera_id: str = Form(None),
    floor_id: int = Form(None),
    room_location: str = Form(None)
):
    """
    Analyze image for fire/smoke detection.
    Returns detection type and severity.
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Analyze frame
        result = detector.analyze_frame(frame)
        
        # If fire/smoke detected, report to Laravel
        if result.detected and result.confidence >= CONFIDENCE_THRESHOLD_WARNING:
            try:
                # Convert image to base64
                _, buffer = cv2.imencode('.jpg', frame)
                image_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Map type to alert_type
                alert_type_map = {
                    'smoke': 'fire_smoke',
                    'small_flame': 'fire_small',
                    'large_flame': 'fire_large'
                }
                
                # Report to Laravel
                response = requests.post(
                    f"{LARAVEL_API_URL}/emergency/fire-alert",
                    json={
                        'alert_type': alert_type_map.get(result.type, 'fire_small'),
                        'severity': result.severity,
                        'floor_id': floor_id,
                        'room_location': room_location,
                        'camera_id': camera_id,
                        'confidence': result.confidence * 100,
                        'description': result.message,
                        'detection_image': image_base64,
                        'metadata': {
                            'detection_type': result.type,
                            'area_percentage': result.area_percentage,
                            'bbox': result.bbox
                        }
                    },
                    timeout=15
                )
                
                logger.info(f"Fire alert sent to Laravel: {result.type} - {result.severity}")
            except Exception as e:
                logger.error(f"Failed to report to Laravel: {e}")
        
        return result.model_dump()
    
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze-stream")
async def analyze_stream(
    camera_id: str = Form(...),
    floor_id: int = Form(...),
    room_location: str = Form(...)
):
    """
    Start analyzing a live camera stream.
    Opens webcam and continuously monitors for fire/smoke.
    """
    # This would be implemented for continuous monitoring
    # For now, return endpoint info
    return {
        "message": "Stream analysis endpoint",
        "camera_id": camera_id,
        "floor_id": floor_id,
        "room_location": room_location,
        "note": "Use /detect-fire endpoint for individual frame analysis"
    }


if __name__ == "__main__":
    logger.info("Starting Advanced Fire Detection Service...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
