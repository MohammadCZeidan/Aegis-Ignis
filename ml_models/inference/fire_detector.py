"""
Fire detection inference using YOLOv8.
"""
from .detector_base import BaseDetector
from ultralytics import YOLO
import numpy as np
from typing import List, Dict, Optional


class FireDetectionConstants:
    DEFAULT_CONFIDENCE_THRESHOLD = 0.5
    FIRE_CLASS_ID = 0
    SMOKE_CLASS_ID = 1
    
    CLASS_NAMES = {
        FIRE_CLASS_ID: 'fire',
        SMOKE_CLASS_ID: 'smoke'
    }


class FireDetectorInference(BaseDetector):
    """Fire detection inference using YOLOv8 model."""
    
    def __init__(self, model_path: str):
        self.model: Optional[YOLO] = None
        self.load_model(model_path)
    
    def load_model(self, model_path: str) -> None:
        """Load YOLOv8 model from path."""
        self.model = YOLO(model_path)
    
    def detect(self, frame: np.ndarray, confidence_threshold: float = FireDetectionConstants.DEFAULT_CONFIDENCE_THRESHOLD) -> List[Dict]:
        """
        Detect fire and smoke in frame.
        
        Args:
            frame: Input frame in BGR format
            confidence_threshold: Minimum confidence threshold for detections
            
        Returns:
            List of detections with format:
            {
                'type': 'fire' or 'smoke',
                'confidence': float,
                'bbox': [x1, y1, x2, y2]
            }
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        results = self.model(frame, conf=confidence_threshold)
        detections = []
        
        for result in results:
            detections.extend(self._process_detection_result(result))
        
        return detections
    
    def _process_detection_result(self, result) -> List[Dict]:
        """Process a single detection result from the model."""
        detections = []
        
        if result.boxes is None:
            return detections
            
        for box in result.boxes:
            detection = self._create_detection_from_box(box)
            if detection:
                detections.append(detection)
        
        return detections
    
    def _create_detection_from_box(self, box) -> Optional[Dict]:
        """Create detection dictionary from bounding box."""
        try:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            coordinates = box.xyxy[0].cpu().numpy()
            
            if len(coordinates) >= 4:
                x1, y1, x2, y2 = coordinates[:4]
                
                return {
                    'type': self._get_detection_type(class_id),
                    'confidence': confidence,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                }
        except (IndexError, ValueError) as e:
            # Log error but continue processing other detections
            return None
        
        return None
    
    def _get_detection_type(self, class_id: int) -> str:
        """Map class ID to detection type."""
        return FireDetectionConstants.CLASS_NAMES.get(
            class_id, 
            FireDetectionConstants.CLASS_NAMES[FireDetectionConstants.FIRE_CLASS_ID]
        )

