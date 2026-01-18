"""
Face recognition inference using ArcFace/InsightFace.
"""
from .detector_base import BaseDetector
import numpy as np
from typing import List, Dict, Optional
import insightface


class FaceRecognizerInference(BaseDetector):
    """Face recognition inference."""
    
    def __init__(self, model_path: str = None):
        """
        Initialize face recognizer.
        
        Args:
            model_path: Path to InsightFace model
        """
        self.model = None
        self.load_model(model_path)
    
    def load_model(self, model_path: str = None):
        """Load InsightFace model."""
        self.model = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
        self.model.prepare(ctx_id=-1, det_size=(640, 640))
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect and recognize faces in frame.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List of face detections with format:
            {
                'bbox': [x1, y1, x2, y2],
                'embedding': np.ndarray,
                'confidence': float
            }
        """
        faces = self.model.get(frame)
        detections = []
        
        for face in faces:
            bbox = face.bbox.astype(int)
            detections.append({
                'bbox': [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
                'embedding': face.embedding,
                'confidence': float(face.det_score)
            })
        
        return detections
    
    def identify(self, embedding: np.ndarray, employee_embeddings: Dict[int, np.ndarray], threshold: float = 0.7) -> Optional[int]:
        """
        Identify face by comparing with employee embeddings.
        
        Args:
            embedding: Face embedding to identify
            employee_embeddings: Dictionary mapping employee_id to embedding
            threshold: Similarity threshold
            
        Returns:
            Employee ID if match found, None otherwise
        """
        best_match = None
        best_similarity = 0.0
        
        for employee_id, emp_embedding in employee_embeddings.items():
            similarity = self._cosine_similarity(embedding, emp_embedding)
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = employee_id
        
        return best_match
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

