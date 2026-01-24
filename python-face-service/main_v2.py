"""
Improved Face Recognition Service with Database Integration
- Fast face detection and embedding generation
- Database integration for face matching
- Real-time presence tracking
- OPTIMIZED: Uses cached embeddings and vectorized operations for ultra-fast duplicate checking
"""
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Tuple
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import logging
import requests
import json
import base64
import os
import time
import asyncio
from datetime import datetime
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Advanced Face Recognition Service",
    description="Fast face detection with database integration",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
LARAVEL_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000/api/v1')
FACE_MATCH_THRESHOLD = 0.6  # Cosine similarity threshold
DUPLICATE_THRESHOLD = 0.50  # Threshold for duplicate detection
CACHE_STALE_THRESHOLD = 30  # Refresh cache if older than 30 seconds

# Initialize face detection model
face_detector = None
opencv_detector = None  # Fallback for detection only (no embeddings)
face_recognizer = None
INSIGHTFACE_AVAILABLE = False

try:
    import insightface
    logger.info("Loading InsightFace models...")
    face_detector = insightface.app.FaceAnalysis(
        name='buffalo_l',
        providers=['CPUExecutionProvider']
    )
    face_detector.prepare(ctx_id=-1, det_size=(640, 640))
    INSIGHTFACE_AVAILABLE = True
    logger.info("✓ InsightFace model loaded successfully with Python 3.12!")
except ImportError as e:
    logger.error(f"InsightFace not installed: {e}")
    logger.error("Install with: pip install insightface onnxruntime")
    # Load OpenCV fallback for basic detection (no embeddings)
    opencv_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    logger.warning(" Using OpenCV fallback for face DETECTION only. Face REGISTRATION disabled.")
except Exception as e:
    logger.error(f"Error loading face model: {e}")
    logger.error("InsightFace is installed but failed to load. This is likely a version incompatibility.")
    # Load OpenCV fallback for basic detection (no embeddings)
    opencv_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    logger.warning(" Using OpenCV fallback for face DETECTION only. Face REGISTRATION disabled.")


class FaceDetectionResponse(BaseModel):
    success: bool
    faces_detected: int
    faces: List[dict]
    message: str = ""


class FaceRegistrationRequest(BaseModel):
    employee_id: int
    floor_id: int
    room_location: str


class FaceRecognitionResponse(BaseModel):
    success: bool
    matched: bool
    employee_id: Optional[int] = None
    employee_name: Optional[str] = None
    confidence: float = 0.0
    floor_id: Optional[int] = None
    room_location: Optional[str] = None


def image_to_numpy(file_bytes: bytes) -> np.ndarray:
    """Convert uploaded image bytes to numpy array."""
    try:
        image = Image.open(BytesIO(file_bytes))
        image = image.convert('RGB')
        return np.array(image)
    except Exception as e:
        logger.error(f"Error converting image: {e}")
        raise HTTPException(status_code=400, detail="Invalid image format")


def detect_faces_insightface(image: np.ndarray):
    """Detect faces using InsightFace (fast and accurate)."""
    faces = face_detector.get(image)
    results = []
    
    for face in faces:
        bbox = face.bbox.astype(int).tolist()
        embedding = face.embedding.tolist()  # 512-dimensional vector
        
        results.append({
            'bbox': bbox,  # [x1, y1, x2, y2]
            'confidence': float(face.det_score),
            'embedding': embedding,
            'landmarks': face.landmark_2d_106.tolist() if hasattr(face, 'landmark_2d_106') else None
        })
    
    return results


def detect_faces_opencv(image: np.ndarray):
    """Fallback: Detect faces using OpenCV (faster but less accurate)."""
    if opencv_detector is None:
        raise Exception("No face detector available. Please install InsightFace.")
    
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    faces = opencv_detector.detectMultiScale(gray, 1.3, 5)
    
    results = []
    for (x, y, w, h) in faces:
        results.append({
            'bbox': [int(x), int(y), int(x+w), int(y+h)],
            'confidence': 0.9,  # OpenCV doesn't provide confidence
            'embedding': None  # No embedding from Haar Cascades
        })
    
    return results


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """Calculate cosine similarity between two embeddings."""
    vec1 = np.array(embedding1)
    vec2 = np.array(embedding2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


# ============================================================================
# FAST CACHING SYSTEM FOR ULTRA-FAST DUPLICATE CHECKING
# ============================================================================
class FastCache:
    """Thread-safe cache for employee embeddings with precomputed norms."""
    def __init__(self):
        self._lock = threading.RLock()
        self._embeddings_matrix: Optional[np.ndarray] = None
        self._embeddings_norms: Optional[np.ndarray] = None  # Precomputed norms
        self._employee_info: List[Dict] = []
        self._timestamp: Optional[datetime] = None
    
    def update(self, employees: List[Dict]) -> None:
        """Update cache with employee data and precompute embeddings matrix."""
        with self._lock:
            embeddings_list = []
            employee_info_list = []
            
            for emp in employees:
                if not emp.get('face_embedding'):
                    continue
                try:
                    embedding = json.loads(emp['face_embedding'])
                    if isinstance(embedding, list) and len(embedding) > 0:
                        embeddings_list.append(embedding)
                        employee_info_list.append(emp)
                except:
                    continue
            
            if embeddings_list:
                self._embeddings_matrix = np.array(embeddings_list, dtype=np.float32)
                # Precompute norms for ultra-fast similarity calculation
                self._embeddings_norms = np.linalg.norm(self._embeddings_matrix, axis=1)
            else:
                self._embeddings_matrix = None
                self._embeddings_norms = None
            
            self._employee_info = employee_info_list
            self._timestamp = datetime.now()
            logger.info(f"Cache updated: {len(employee_info_list)} employees with embeddings")
    
    def get_cache_age(self) -> int:
        """Get cache age in seconds."""
        with self._lock:
            if not self._timestamp:
                return 999
            return int((datetime.now() - self._timestamp).total_seconds())
    
    def get_embeddings_matrix(self) -> Optional[np.ndarray]:
        """Get cached embeddings matrix."""
        with self._lock:
            return self._embeddings_matrix.copy() if self._embeddings_matrix is not None else None
    
    def get_embeddings_norms(self) -> Optional[np.ndarray]:
        """Get precomputed norms."""
        with self._lock:
            return self._embeddings_norms.copy() if self._embeddings_norms is not None else None
    
    def get_employee_info(self) -> List[Dict]:
        """Get cached employee info."""
        with self._lock:
            return self._employee_info.copy()


# Global cache instance
employee_cache = FastCache()


def refresh_cache() -> bool:
    """Refresh employee cache from Laravel API."""
    try:
        logger.info("Refreshing employee cache...")
        response = requests.get(f"{LARAVEL_API_URL}/employees/registered-faces", timeout=5)
        if response.status_code == 200:
            employees = response.json().get('data', [])
            employee_cache.update(employees)
            return True
        return False
    except Exception as e:
        logger.error(f"Cache refresh failed: {e}")
        return False


def find_best_match_vectorized(
    query_embedding: np.ndarray,
    threshold: float = DUPLICATE_THRESHOLD
) -> Tuple[Optional[Dict], float]:
    """
    ULTRA-FAST vectorized duplicate check using cached embeddings.
    Uses numpy matrix operations for O(1) comparison instead of O(N) loop.
    """
    embeddings_matrix = employee_cache.get_embeddings_matrix()
    embeddings_norms = employee_cache.get_embeddings_norms()
    employee_info = employee_cache.get_employee_info()
    
    if embeddings_matrix is None or len(employee_info) == 0:
        return None, 0.0
    
    # Vectorized cosine similarity calculation (MUCH faster than loop)
    query_norm = np.linalg.norm(query_embedding)
    if query_norm == 0:
        return None, 0.0
    
    # Use precomputed norms for speed
    if embeddings_norms is not None:
        norms = embeddings_norms * query_norm
    else:
        norms = np.linalg.norm(embeddings_matrix, axis=1) * query_norm
    
    # Single vectorized operation instead of N individual calculations
    similarities = np.dot(embeddings_matrix, query_embedding) / norms
    
    # Find best match
    max_idx = np.argmax(similarities)
    max_similarity = float(similarities[max_idx])
    
    if max_similarity >= threshold:
        return employee_info[max_idx], max_similarity
    
    return None, max_similarity


@app.on_event("startup")
async def startup_event():
    """Initialize cache on startup."""
    logger.info("Initializing employee cache...")
    await asyncio.to_thread(refresh_cache)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Face Recognition API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    model_type = "InsightFace" if isinstance(face_detector, object) and hasattr(face_detector, 'get') else "OpenCV"
    return {
        "status": "healthy",
        "model": model_type,
        "embeddings_supported": model_type == "InsightFace"
    }


@app.post("/detect-faces", response_model=FaceDetectionResponse)
async def detect_faces(file: UploadFile = File(...)):
    """
    Detect faces in an uploaded image.
    Returns face bounding boxes and embeddings (if InsightFace available).
    Falls back to OpenCV for detection only.
    """
    try:
        # Read and convert image
        contents = await file.read()
        image = image_to_numpy(contents)
        
        # Detect faces with InsightFace (preferred) or OpenCV (fallback)
        if INSIGHTFACE_AVAILABLE and hasattr(face_detector, 'get'):
            faces = detect_faces_insightface(image)
        elif opencv_detector is not None:
            faces = detect_faces_opencv(image)
        else:
            raise HTTPException(
                status_code=503,
                detail="No face detection model available. Please install InsightFace."
            )
        
        return FaceDetectionResponse(
            success=True,
            faces_detected=len(faces),
            faces=faces,
            message=f"Detected {len(faces)} face(s)"
        )
    
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/register-face")
async def register_face(
    file: UploadFile = File(...),
    employee_id: int = Form(...),
    floor_id: int = Form(...),
    room_location: str = Form(...)
):
    """
    Register a face for an employee.
    Generates embedding and stores in database via Laravel API.
    REQUIRES InsightFace for duplicate detection.
    """
    try:
        # CRITICAL: Block registration if InsightFace is not available
        if not INSIGHTFACE_AVAILABLE or face_detector is None:
            raise HTTPException(
                status_code=503,
                detail=" Face registration is currently unavailable. InsightFace model is not loaded. Please contact system administrator to install InsightFace properly for face recognition to work."
            )
        
        # Read image
        contents = await file.read()
        image = image_to_numpy(contents)
        
        # Detect faces with InsightFace (required for embeddings)
        faces = detect_faces_insightface(image)
        
        if len(faces) == 0:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        if len(faces) > 1:
            raise HTTPException(status_code=400, detail="Multiple faces detected. Please provide image with single face")
        
        face = faces[0]
        
        # ULTRA-FAST duplicate check using cached embeddings and vectorized operations
        try:
            # Refresh cache if stale (in background, non-blocking)
            cache_age = employee_cache.get_cache_age()
            if cache_age > CACHE_STALE_THRESHOLD:
                logger.info(f"Cache stale ({cache_age}s) - Refreshing in background...")
                asyncio.create_task(asyncio.to_thread(refresh_cache))
            
            # Fast vectorized duplicate check
            query_embedding = np.array(face['embedding'], dtype=np.float32)
            matched, similarity = find_best_match_vectorized(query_embedding, DUPLICATE_THRESHOLD)
            
            if matched:
                employee_name = matched.get('name', 'Unknown')
                raise HTTPException(
                    status_code=400,
                    detail=f"Hi {employee_name}! You're already registered. Employee ID: {matched.get('employee_number', matched['id'])}. Match: {similarity:.0%}"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Duplicate check error: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Could not verify if this face is already registered. Please try again."
            )
        
        # Convert image to base64 for storage
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Send to Laravel API with embedding
        payload = {
            'confidence': face['confidence'],
            'bbox': face['bbox'],
            'image_data': image_base64,
            'floor_id': floor_id,
            'room_location': room_location,
            'embedding': face['embedding']  # Always include - we verified InsightFace is available
        }
        
        logger.info(f" Sending face registration to Laravel API for employee {employee_id}")
        logger.info(f"   - Confidence: {face['confidence']:.2%}")
        logger.info(f"   - Embedding size: {len(face['embedding']) if face.get('embedding') else 'NO EMBEDDING'}")
        logger.info(f"   - Floor ID: {floor_id}, Room: {room_location}")
        
        response = requests.post(
            f"{LARAVEL_API_URL}/employees/{employee_id}/register-face",
            json=payload,
            timeout=10
        )
        
        logger.info(f" Laravel API response: Status {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f" SUCCESS: Face registered for employee {employee_id}")
            logger.info(f"   - Response: {response_data}")
            # Refresh cache with new face (in background)
            asyncio.create_task(asyncio.to_thread(refresh_cache))
            return {
                "success": True,
                "employee_id": employee_id,
                "message": "Face registered successfully",
                "confidence": face['confidence'],
                "has_embedding": True,
                "backend_response": response_data
            }
        else:
            error_text = response.text
            logger.error(f" FAILED: Laravel API returned {response.status_code}")
            logger.error(f"   - Error: {error_text}")
            raise HTTPException(status_code=response.status_code, detail=f"Backend error: {error_text}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-face-duplicate")
async def check_face_duplicate(file: UploadFile = File(...)):
    """
    Check if a face is already registered (for pre-registration validation).
    Returns information about the matched employee if found.
    REQUIRES InsightFace for duplicate detection.
    """
    try:
        # CRITICAL: Block if InsightFace is not available
        if not INSIGHTFACE_AVAILABLE or face_detector is None:
            raise HTTPException(
                status_code=503,
                detail=" Face duplicate checking is currently unavailable. InsightFace model is not loaded. Please contact system administrator."
            )
        
        # Read image
        contents = await file.read()
        image = image_to_numpy(contents)
        
        # Detect faces with InsightFace
        faces = detect_faces_insightface(image)
        
        if len(faces) == 0:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        if len(faces) > 1:
            raise HTTPException(status_code=400, detail="Multiple faces detected. Please provide image with single face")
        
        face = faces[0]
        
        # ULTRA-FAST duplicate check using cached embeddings and vectorized operations
        start_time = time.time()
        try:
            # Refresh cache if stale (in background, non-blocking)
            cache_age = employee_cache.get_cache_age()
            if cache_age > CACHE_STALE_THRESHOLD:
                logger.info(f"Cache stale ({cache_age}s) - Refreshing in background...")
                asyncio.create_task(asyncio.to_thread(refresh_cache))
            
            # Early exit if no cached data
            employee_info = employee_cache.get_employee_info()
            if len(employee_info) == 0:
                logger.info("No registered faces in cache - ready to register")
                return {
                    "success": True,
                    "is_duplicate": False,
                    "message": "No registered faces found - ready to register",
                    "processing_time_ms": round((time.time() - start_time) * 1000, 1)
                }
            
            # Fast vectorized duplicate check (MUCH faster than sequential loop)
            query_embedding = np.array(face['embedding'], dtype=np.float32)
            matched, similarity = find_best_match_vectorized(query_embedding, DUPLICATE_THRESHOLD)
            
            processing_time = (time.time() - start_time) * 1000
            
            if matched:
                logger.info(f"DUPLICATE FOUND: {matched.get('name')} ({similarity:.1%}) in {processing_time:.0f}ms")
                return {
                    "success": True,
                    "is_duplicate": True,
                    "matched_employee": {
                        "id": matched['id'],
                        "name": matched.get('name', 'Unknown'),
                        "employee_number": matched.get('employee_number', 'N/A'),
                        "department": matched.get('department', 'N/A')
                    },
                    "similarity": float(similarity),
                    "message": f"Hi {matched.get('name')}! Already registered. Employee ID: {matched.get('employee_number', matched['id'])} | Match: {similarity:.0%}",
                    "processing_time_ms": round(processing_time, 1)
                }
            
            logger.info(f"No duplicate found ({similarity:.1%} max) in {processing_time:.0f}ms")
            return {
                "success": True,
                "is_duplicate": False,
                "message": "Face is not registered yet. Safe to proceed with registration.",
                "processing_time_ms": round(processing_time, 1)
            }
        except Exception as e:
            logger.error(f"Duplicate check error: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Could not verify if this face is already registered. Please try again."
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face duplicate check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recognize-face", response_model=FaceRecognitionResponse)
async def recognize_face(
    file: UploadFile = File(...),
    camera_id: str = Form(None),
    floor_id: int = Form(None),
    room_location: str = Form(None)
):
    """
    Recognize a face by matching against registered employees.
    Updates presence tracking in database.
    """
    try:
        # Read image
        contents = await file.read()
        image = image_to_numpy(contents)
        
        # Detect faces
        if hasattr(face_detector, 'get'):
            faces = detect_faces_insightface(image)
        else:
            raise HTTPException(status_code=400, detail="Face recognition requires InsightFace")
        
        if len(faces) == 0:
            return FaceRecognitionResponse(
                success=True,
                matched=False,
                message="No face detected"
            )
        
        # Use the first detected face
        detected_face = faces[0]
        detected_embedding = np.array(detected_face['embedding'], dtype=np.float32)
        
        # Refresh cache if stale (in background)
        cache_age = employee_cache.get_cache_age()
        if cache_age > CACHE_STALE_THRESHOLD:
            asyncio.create_task(asyncio.to_thread(refresh_cache))
        
        # Fast vectorized matching
        best_match, best_similarity = find_best_match_vectorized(detected_embedding, FACE_MATCH_THRESHOLD)
        
        if best_match:
            # Log presence detection
            _, buffer = cv2.imencode('.jpg', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            requests.post(
                f"{LARAVEL_API_URL}/presence/log",
                json={
                    'employee_id': best_match['id'],
                    'floor_id': floor_id,
                    'room_location': room_location,
                    'camera_id': camera_id,
                    'confidence': best_similarity * 100,
                    'detection_image': image_base64,
                    'event_type': 'detected'
                },
                timeout=5
            )
            
            return FaceRecognitionResponse(
                success=True,
                matched=True,
                employee_id=best_match['id'],
                employee_name=best_match.get('name', 'Unknown'),
                confidence=best_similarity,
                floor_id=best_match.get('current_floor_id'),
                room_location=best_match.get('current_room')
            )
        else:
            return FaceRecognitionResponse(
                success=True,
                matched=False,
                message="No matching employee found"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face recognition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
