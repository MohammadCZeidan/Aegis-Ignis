"""
Person detection inference using YOLOv8.
"""
from .detector_base import BaseDetector
from ultralytics import YOLO
import numpy as np
from typing import List, Dict


class PersonDetectorInference(BaseDetector):
    """Person detection inference."""
    
    def __init__(self, model_path: str = None):
        """
        Initialize person detector.
        
        Args:
            model_path: Path to YOLOv8 model (None for default)
        """
        self.model = None
        if model_path:
            self.load_model(model_path)
        else:
            # Use default YOLOv8-nano
            self.model = YOLO('yolov8n.pt')
    
    def load_model(self, model_path: str):
        """Load YOLOv8 model."""
        self.model = YOLO(model_path)
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect people in frame.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List of detections with format:
            {
                'confidence': float,
                'bbox': [x1, y1, x2, y2]
            }
        """
        results = self.model(frame, conf=0.5, classes=[0])  # class 0 = person
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                conf = float(box.conf[0])
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                
                detections.append({
                    'confidence': conf,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)]
                })
        
        return detections

