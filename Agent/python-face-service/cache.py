"""
Thread-safe cache for employee embeddings with precomputed norms for fast similarity calculations.
"""
import threading
from typing import Optional, List, Dict
from datetime import datetime
import numpy as np
from config import ServiceConfig

class ThreadSafeCache:
    """Thread-safe cache for employee embeddings."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._employees: List[Dict] = []
        self._embeddings_matrix: Optional[np.ndarray] = None
        self._embeddings_norms: Optional[np.ndarray] = None  # Precomputed norms for speed
        self._employee_info: List[Dict] = []
        self._timestamp: Optional[datetime] = None
    
    def update(self, employees: List[Dict], embeddings_matrix: Optional[np.ndarray], 
               employee_info: List[Dict]) -> None:
        """Update cache with new data and precompute norms."""
        with self._lock:
            self._employees = employees
            self._embeddings_matrix = embeddings_matrix
            # Precompute norms for faster similarity calculation
            if embeddings_matrix is not None and len(embeddings_matrix) > 0:
                self._embeddings_norms = np.linalg.norm(embeddings_matrix, axis=1)
            else:
                self._embeddings_norms = None
            self._employee_info = employee_info
            self._timestamp = datetime.now()
    
    def get_employees(self) -> List[Dict]:
        """Get cached employees list."""
        with self._lock:
            return self._employees.copy()
    
    def get_embeddings_matrix(self) -> Optional[np.ndarray]:
        """Get cached embeddings matrix."""
        with self._lock:
            return self._embeddings_matrix.copy() if self._embeddings_matrix is not None else None
    
    def get_embeddings_norms(self) -> Optional[np.ndarray]:
        """Get precomputed embeddings norms."""
        with self._lock:
            return self._embeddings_norms.copy() if self._embeddings_norms is not None else None
    
    def get_employee_info(self) -> List[Dict]:
        """Get cached employee info list."""
        with self._lock:
            return self._employee_info.copy()
    
    def get_timestamp(self) -> Optional[datetime]:
        """Get cache timestamp."""
        with self._lock:
            return self._timestamp
    
    def is_stale(self) -> bool:
        """Check if cache is stale."""
        with self._lock:
            if not self._timestamp:
                return True
            age = (datetime.now() - self._timestamp).total_seconds()
            return age > ServiceConfig.CACHE_REFRESH_SECONDS
    
    def get_cache_age(self) -> int:
        """Get cache age in seconds."""
        with self._lock:
            if not self._timestamp:
                return 999
            return int((datetime.now() - self._timestamp).total_seconds())
