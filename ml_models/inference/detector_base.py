"""
Base detector class for all detection models.
"""
from abc import ABC, abstractmethod
import numpy as np
from typing import List, Dict


class BaseDetector(ABC):
    """Base class for all detectors."""
    
    @abstractmethod
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in a frame.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List of detections
        """
        pass
    
    @abstractmethod
    def load_model(self, model_path: str):
        """Load model from file."""
        pass

