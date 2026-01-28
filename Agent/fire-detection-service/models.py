"""
Pydantic models for Fire Detection Service
"""
from pydantic import BaseModel
from typing import List, Optional

class FireDetectionResult(BaseModel):
    """Fire detection result model"""
    detected: bool
    type: str  # 'smoke', 'small_flame', 'large_flame', 'none'
    severity: str  # 'warning', 'alert', 'critical'
    confidence: float
    bbox: Optional[List[int]] = None
    area_percentage: float = 0.0
    message: str = ""
