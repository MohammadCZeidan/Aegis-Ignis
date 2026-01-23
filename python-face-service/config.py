"""
Configuration constants for the face recognition service.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class ServiceConfig:
    """Configuration constants for the face recognition service."""
    LARAVEL_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000').rstrip('/api/v1')
    
    # Face matching threshold (0.0-1.0)
    # Lower values catch more potential duplicates but may have false positives
    FACE_MATCH_THRESHOLD = 0.40
    
    # Cache refresh interval in seconds
    CACHE_REFRESH_SECONDS = 10
    
    # Image processing settings
    IMAGE_MAX_SIZE = 240  # Maximum dimension for face detection (reduced for faster processing)
    DETECTION_SIZE = (96, 96)  # InsightFace detection size (smaller = faster)
    EXPECTED_EMBEDDING_DIM = 512  # InsightFace embedding dimension
    
    # Cache refresh settings
    CACHE_STALE_THRESHOLD = 60  # Seconds before cache is considered stale
    MAX_RETRIES = 2  # Reduced retries for faster failure
    RETRY_DELAY = 1  # Reduced delay between retries
    REQUEST_TIMEOUT = 5  # Reduced timeout for faster failure detection
