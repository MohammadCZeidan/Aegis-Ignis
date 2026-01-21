"""
ML-based Fire Detector using YOLOv8
This module provides ML fire detection with automatic fallback to color-based detection
"""
import cv2
import numpy as np
import logging
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Try to import ML dependencies
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("Ultralytics YOLO not available. Install with: pip install ultralytics")

logger = logging.getLogger(__name__)


class MLFireDetector:
    """
    ML-based Fire Detection using YOLOv8
    Supports both trained models and automatic fallback to color-based detection
    """
    
    def __init__(
        self, 
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.5,
        use_color_fallback: bool = True
    ):
        """
        Initialize ML Fire Detector
        
        Args:
            model_path: Path to YOLOv8 fire detection model (.pt file)
            confidence_threshold: Minimum confidence for detection (0-1)
            use_color_fallback: Use color-based detection if ML model unavailable
        """
        self.model = None
        self.confidence_threshold = confidence_threshold
        self.use_color_fallback = use_color_fallback
        self.detection_method = "none"
        
        # Try to load ML model
        if model_path and YOLO_AVAILABLE:
            self._load_ml_model(model_path)
        
        # Log initialization status
        if self.model is not None:
            logger.info(f"✅ ML Fire Detector initialized with model: {model_path}")
            self.detection_method = "ml"
        elif use_color_fallback:
            logger.warning("⚠️ ML model not available, using color-based fallback")
            self.detection_method = "color"
        else:
            logger.error("❌ No detection method available!")
    
    def _load_ml_model(self, model_path: str) -> None:
        """Load YOLOv8 model from file"""
        try:
            if not os.path.exists(model_path):
                logger.warning(f"Model file not found: {model_path}")
                logger.info("💡 To train a model, use: ml_models/train/train_fire_model.py")
                logger.info("💡 Or download pretrained from: https://universe.roboflow.com/")
                return
            
            self.model = YOLO(model_path)
            logger.info(f"✅ Loaded ML model: {model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")
            self.model = None
    
    def detect(
        self, 
        frame: np.ndarray,
        return_annotated: bool = False
    ) -> Dict:
        """
        Detect fire in frame using ML or color-based method
        
        Args:
            frame: Input frame (BGR format)
            return_annotated: Return annotated frame with bounding boxes
            
        Returns:
            Dict with detection results:
            {
                'detected': bool,
                'type': str,  # 'fire', 'smoke', or 'none'
                'severity': str,  # 'warning', 'critical'
                'confidence': float,  # 0-1
                'bbox': [x1, y1, x2, y2] or None,
                'area_percentage': float,
                'method': str,  # 'ml' or 'color'
                'annotated_frame': np.ndarray (if return_annotated=True)
            }
        """
        if self.model is not None:
            result = self._detect_ml(frame)
            result['method'] = 'ml'
        elif self.use_color_fallback:
            result = self._detect_color_based(frame)
            result['method'] = 'color'
        else:
            result = self._no_detection_result()
            result['method'] = 'none'
        
        # Add annotated frame if requested
        if return_annotated and result['detected']:
            result['annotated_frame'] = self._annotate_frame(frame, result)
        
        return result
    
    def _detect_ml(self, frame: np.ndarray) -> Dict:
        """
        Detect fire using ML model
        
        Returns:
            Detection result dictionary
        """
        try:
            # Run inference
            results = self.model(frame, conf=self.confidence_threshold, verbose=False)
            
            # Process results
            best_detection = None
            highest_confidence = 0.0
            
            for result in results:
                if result.boxes is None or len(result.boxes) == 0:
                    continue
                
                for box in result.boxes:
                    class_id = int(box.cls[0])
                    confidence = float(box.conf[0])
                    coords = box.xyxy[0].cpu().numpy()
                    
                    if confidence > highest_confidence:
                        highest_confidence = confidence
                        x1, y1, x2, y2 = map(int, coords)
                        
                        # Calculate area percentage
                        bbox_area = (x2 - x1) * (y2 - y1)
                        frame_area = frame.shape[0] * frame.shape[1]
                        area_percentage = (bbox_area / frame_area) * 100
                        
                        best_detection = {
                            'detected': True,
                            'type': 'fire' if class_id == 0 else 'smoke',
                            'severity': 'critical' if area_percentage > 5 else 'warning',
                            'confidence': confidence,
                            'bbox': [x1, y1, x2, y2],
                            'area_percentage': area_percentage
                        }
            
            if best_detection:
                return best_detection
            
        except Exception as e:
            logger.error(f"ML detection error: {e}")
        
        return self._no_detection_result()
    
    def _detect_color_based(self, frame: np.ndarray) -> Dict:
        """
        Fallback color-based fire detection
        Uses HSV color analysis for fire/flame detection
        
        Returns:
            Detection result dictionary
        """
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Define fire color ranges (Orange, Red, Yellow, White-hot)
            lower_red1 = np.array([0, 50, 100])
            upper_red1 = np.array([10, 255, 255])
            
            lower_orange = np.array([8, 100, 140])
            upper_orange = np.array([25, 255, 255])
            
            lower_white = np.array([0, 0, 200])
            upper_white = np.array([180, 50, 255])
            
            # Create masks
            mask_red = cv2.inRange(hsv, lower_red1, upper_red1)
            mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
            mask_white = cv2.inRange(hsv, lower_white, upper_white)
            
            # Combine masks
            fire_mask = cv2.bitwise_or(mask_red, cv2.bitwise_or(mask_orange, mask_white))
            
            # Additional brightness check
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, bright_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            fire_mask = cv2.bitwise_and(fire_mask, bright_mask)
            
            # Find contours
            contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find largest contour
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                
                if area > 500:  # Minimum area threshold
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    
                    # Calculate metrics
                    frame_area = frame.shape[0] * frame.shape[1]
                    area_percentage = (area / frame_area) * 100
                    confidence = min(area_percentage / 10, 1.0)  # Normalize to 0-1
                    
                    return {
                        'detected': True,
                        'type': 'fire',
                        'severity': 'critical' if area_percentage > 3 else 'warning',
                        'confidence': confidence,
                        'bbox': [x, y, x+w, y+h],
                        'area_percentage': area_percentage
                    }
        
        except Exception as e:
            logger.error(f"Color-based detection error: {e}")
        
        return self._no_detection_result()
    
    def _no_detection_result(self) -> Dict:
        """Return result for no detection"""
        return {
            'detected': False,
            'type': 'none',
            'severity': 'none',
            'confidence': 0.0,
            'bbox': None,
            'area_percentage': 0.0
        }
    
    def _annotate_frame(self, frame: np.ndarray, result: Dict) -> np.ndarray:
        """
        Annotate frame with detection bounding box and info
        
        Args:
            frame: Original frame
            result: Detection result
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        if result['bbox']:
            x1, y1, x2, y2 = result['bbox']
            
            # Choose color based on severity
            color = (0, 0, 255) if result['severity'] == 'critical' else (0, 165, 255)
            
            # Draw bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Add label
            label = f"{result['type'].upper()} {result['confidence']*100:.0f}% ({result['method']})"
            
            # Background for text
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated, (x1, y1-text_height-10), (x1+text_width, y1), color, -1)
            
            # Text
            cv2.putText(annotated, label, (x1, y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return annotated
    
    def get_detection_method(self) -> str:
        """Get current detection method being used"""
        return self.detection_method
    
    def is_ml_available(self) -> bool:
        """Check if ML detection is available"""
        return self.model is not None


def download_pretrained_model(save_path: str = "ml_models/weights/fire_detection.pt") -> bool:
    """
    Helper function to download a pretrained YOLOv8 fire detection model
    
    Args:
        save_path: Where to save the downloaded model
        
    Returns:
        True if download successful
    """
    logger.info("📥 Downloading pretrained fire detection model...")
    logger.info("💡 Visit https://universe.roboflow.com/ to find fire detection datasets")
    logger.info("💡 Or train your own model using ml_models/train/train_fire_model.py")
    
    # Create directory if needed
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Note: You would implement actual download logic here
    # For example, from Roboflow API or a public URL
    
    return False
