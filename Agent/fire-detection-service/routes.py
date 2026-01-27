"""
API routes for Fire Detection Service
"""
import cv2
import numpy as np
import os
import logging
import base64
import requests
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from typing import Optional
import sys

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Add parent directory to path for services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from models import FireDetectionResult
from detectors import AdvancedFireDetector
from services.ml_fire_detector import MLFireDetector
from services.alert_manager import AlertManager

logger = logging.getLogger(__name__)

# Initialize detectors and alert manager
ml_detector = MLFireDetector(
    model_path=Config.ML_MODEL_PATH if Config.USE_ML_DETECTION else None,
    confidence_threshold=Config.CONFIDENCE_THRESHOLD,
    use_color_fallback=Config.USE_COLOR_FALLBACK
)

color_detector = AdvancedFireDetector()

# Initialize AlertManager with N8N webhook URL
alert_manager = AlertManager(n8n_webhook_url=Config.N8N_WEBHOOK_URL)

# Log N8N configuration status
if Config.is_n8n_configured():
    logger.info(f"✓ N8N webhook configured: {Config.N8N_WEBHOOK_URL}")
else:
    logger.warning("⚠ N8N_WEBHOOK_URL not configured. N8N alerts will be disabled.")
    logger.info("To enable N8N alerts, set N8N_WEBHOOK_URL in your .env file")


def register_routes(app: FastAPI):
    """Register all API routes"""
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        config_status = Config.validate()
        return {
            "service": "ML Fire Detection API",
            "version": "3.0.0",
            "docs": "/docs",
            "health": "/health",
            "detection_method": ml_detector.get_detection_method(),
            "ml_available": ml_detector.is_ml_available(),
            "n8n_configured": config_status['n8n_configured'],
            "n8n_url": config_status['n8n_url'],
            "twilio_configured": config_status['twilio_configured']
        }
    
    @app.get("/health")
    async def health():
        """Health check endpoint"""
        config_status = Config.validate()
        return {
            "status": "healthy",
            "version": "3.0.0",
            "features": ["ml_detection", "smoke_detection", "flame_detection", "n8n_integration"],
            "detection_method": ml_detector.get_detection_method(),
            "ml_model_loaded": ml_detector.is_ml_available(),
            "n8n_enabled": config_status['n8n_configured'],
            "twilio_enabled": config_status['twilio_configured']
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
            if result['detected'] and result['confidence'] >= Config.CONFIDENCE_THRESHOLD:
                logger.info(f" FIRE DETECTED! Type: {result['type']}, Confidence: {result['confidence']:.2%}, Method: {result['method']}")
                
                # Save screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_filename = f"fire_cam{camera_id}_floor{floor_id}_{timestamp}.jpg"
                screenshot_dir = os.path.join("..", "..", "Server", "public", "storage", "alerts")
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
                    
                    if alert_success:
                        logger.info(f"✓ Alert sent successfully via N8N/Twilio")
                    else:
                        logger.warning("⚠ Alert sending failed - check N8N webhook and Twilio configuration")
                    
                    # Send CRITICAL alert if people present
                    if people_count > 0:
                        critical_sent = alert_manager.send_critical_evacuation_alert(
                            floor_id=floor_id,
                            camera_id=camera_id,
                            people_count=people_count,
                            fire_confidence=result['confidence']
                        )
                        if critical_sent:
                            logger.info(f"✓ Critical evacuation alert sent for {people_count} people")
                
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
                    "n8n_enabled": Config.is_n8n_configured(),
                    "message": f"{result['type'].upper()} detected on Floor {floor_id} ({people_count} people present)"
                }
            
            return {
                "detected": False,
                "detection_method": result['method'],
                "message": "No fire detected"
            }
        
        except Exception as e:
            logger.error(f"ML Detection error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/detect-fire")
    async def detect_fire(
        file: UploadFile = File(...),
        camera_id: str = Form(None),
        floor_id: int = Form(None),
        room_location: str = Form(None)
    ):
        """
        Analyze image for fire/smoke detection using color-based detection.
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
            result = color_detector.analyze_frame(frame)
            
            # If fire/smoke detected, report to Laravel
            if result.detected and result.confidence >= Config.CONFIDENCE_THRESHOLD_WARNING:
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
                        f"{Config.BACKEND_API_URL}/emergency/fire-alert",
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
            logger.error(f"Detection error: {e}", exc_info=True)
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
        return {
            "message": "Stream analysis endpoint",
            "camera_id": camera_id,
            "floor_id": floor_id,
            "room_location": room_location,
            "note": "Use /detect-fire endpoint for individual frame analysis"
        }
