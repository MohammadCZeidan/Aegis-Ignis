"""
Edge processor for running detection models on edge devices.
"""
import cv2
import numpy as np
from typing import Dict, List, Optional
import paho.mqtt.client as mqtt
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EdgeProcessor:
    """Edge processor for real-time detection."""
    
    def __init__(
        self,
        mqtt_broker: str = "localhost",
        mqtt_port: int = 1883,
        camera_id: int = 1,
        floor_id: int = 1
    ):
        """
        Initialize edge processor.
        
        Args:
            mqtt_broker: MQTT broker host
            mqtt_port: MQTT broker port
            camera_id: Camera identifier
            floor_id: Floor identifier
        """
        self.camera_id = camera_id
        self.floor_id = floor_id
        self.mqtt_client = None
        self.fire_detector = None
        self.person_detector = None
        self._init_mqtt(mqtt_broker, mqtt_port)
        self._load_models()
    
    def _init_mqtt(self, broker: str, port: int):
        """Initialize MQTT client."""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_connect = self._on_connect
            self.mqtt_client.on_publish = self._on_publish
            self.mqtt_client.connect(broker, port, 60)
            self.mqtt_client.loop_start()
            logger.info(f"MQTT client connected to {broker}:{port}")
        except Exception as e:
            logger.error(f"Error connecting to MQTT broker: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            logger.info("MQTT connected successfully")
        else:
            logger.error(f"MQTT connection failed with code {rc}")
    
    def _on_publish(self, client, userdata, mid):
        """MQTT publish callback."""
        pass
    
    def _load_models(self):
        """Load detection models (quantized for edge)."""
        try:
            # Load quantized ONNX models for edge deployment
            # For now, using placeholder
            logger.info("Loading edge detection models...")
            # TODO: Load ONNX models
            logger.info("Models loaded (placeholder)")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def process_frame(self, frame: np.ndarray):
        """
        Process a single frame and publish detections via MQTT.
        
        Args:
            frame: Input frame (BGR format)
        """
        detections = {
            'camera_id': self.camera_id,
            'floor_id': self.floor_id,
            'timestamp': datetime.now().isoformat(),
            'fire_detections': [],
            'person_detections': []
        }
        
        # Run fire detection
        if self.fire_detector:
            fire_detections = self.fire_detector.detect(frame, self.camera_id)
            detections['fire_detections'] = [
                {
                    'type': d.detection_type,
                    'confidence': d.confidence,
                    'bbox': d.bounding_box
                }
                for d in fire_detections
            ]
        
        # Run person detection
        if self.person_detector:
            person_detections = self.person_detector.detect(frame)
            detections['person_detections'] = [
                {
                    'bbox': d.bounding_box,
                    'confidence': d.confidence
                }
                for d in person_detections
            ]
        
        # Publish via MQTT
        topic = f"aegis/detections/{self.camera_id}"
        payload = json.dumps(detections)
        self.mqtt_client.publish(topic, payload)
    
    def cleanup(self):
        """Cleanup resources."""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

