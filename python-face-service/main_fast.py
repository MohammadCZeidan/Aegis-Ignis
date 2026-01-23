"""
Face Recognition Service
Provides face detection, identification, and duplicate checking using InsightFace.
Uses cached employee embeddings for efficient similarity comparisons.
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

import os
import threading
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import logging
import requests
import json
import base64
import asyncio
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Face Recognition Service", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ServiceConfig:
    """Configuration constants for the face recognition service."""
    LARAVEL_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000').rstrip('/api/v1')
    
    # Face matching threshold (0.0-1.0)
    # Lower values catch more potential duplicates but may have false positives
    FACE_MATCH_THRESHOLD = 0.40
    
    # Cache refresh interval in seconds
    CACHE_REFRESH_SECONDS = 10
    
    # Image processing settings
    IMAGE_MAX_SIZE = 320  # Maximum dimension for face detection (balance speed/accuracy)
    DETECTION_SIZE = (96, 96)  # InsightFace detection size (smaller = faster)
    EXPECTED_EMBEDDING_DIM = 512  # InsightFace embedding dimension
    
    # Cache refresh settings
    CACHE_STALE_THRESHOLD = 60  # Seconds before cache is considered stale
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # Seconds between retries
    REQUEST_TIMEOUT = 10  # Seconds


class ThreadSafeCache:
    """Thread-safe cache for employee embeddings."""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._employees: List[Dict] = []
        self._embeddings_matrix: Optional[np.ndarray] = None
        self._employee_info: List[Dict] = []
        self._timestamp: Optional[datetime] = None
    
    def update(self, employees: List[Dict], embeddings_matrix: Optional[np.ndarray], 
               employee_info: List[Dict]) -> None:
        """Update cache with new data."""
        with self._lock:
            self._employees = employees
            self._embeddings_matrix = embeddings_matrix
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


# Global thread-safe cache
cache = ThreadSafeCache()

# Face detector instance
face_detector = None
INSIGHTFACE_AVAILABLE = False

try:
    import insightface
    logger.info("Loading InsightFace...")
    face_detector = insightface.app.FaceAnalysis(
        name='buffalo_l',
        providers=['CPUExecutionProvider']
    )
    face_detector.prepare(ctx_id=-1, det_size=ServiceConfig.DETECTION_SIZE)
    INSIGHTFACE_AVAILABLE = True
    logger.info(f"InsightFace loaded (detection size: {ServiceConfig.DETECTION_SIZE})")
except Exception as e:
    logger.error(f"InsightFace initialization failed: {e}")
    INSIGHTFACE_AVAILABLE = False


class FaceDetectionResponse(BaseModel):
    """Response model for face detection."""
    success: bool
    faces_detected: int
    faces: List[dict]
    ideal_head_position: Optional[dict] = None
    message: str = ""


def image_to_numpy(file_bytes: bytes, max_size: int = None) -> np.ndarray:
    """
    Convert image bytes to numpy array.
    
    Args:
        file_bytes: Image file bytes
        max_size: Maximum dimension (defaults to ServiceConfig.IMAGE_MAX_SIZE)
        
    Returns:
        Numpy array of image in RGB format
    """
    if max_size is None:
        max_size = ServiceConfig.IMAGE_MAX_SIZE
        
    image = Image.open(BytesIO(file_bytes))
    
    if image.width > max_size or image.height > max_size:
        image.thumbnail((max_size, max_size), Image.BILINEAR)
    
    image = image.convert('RGB')
    return np.array(image)


def calculate_similarity_matrix(
    embeddings_matrix: np.ndarray, 
    query_embedding: np.ndarray
) -> np.ndarray:
    """
    Calculate cosine similarity between query embedding and all cached embeddings.
    
    Args:
        embeddings_matrix: Matrix of cached embeddings (N x D)
        query_embedding: Query embedding vector (D,)
        
    Returns:
        Array of similarity scores (N,)
    """
    norms = np.linalg.norm(embeddings_matrix, axis=1) * np.linalg.norm(query_embedding)
    similarities = np.dot(embeddings_matrix, query_embedding) / norms
    return similarities


def find_best_match(
    embeddings_matrix: np.ndarray,
    employee_info: List[Dict],
    query_embedding: np.ndarray,
    threshold: float
) -> Tuple[Optional[Dict], float]:
    """
    Find best matching employee for given embedding.
    
    Args:
        embeddings_matrix: Matrix of cached embeddings
        employee_info: List of employee info dicts
        query_embedding: Query embedding to match
        threshold: Minimum similarity threshold
        
    Returns:
        Tuple of (matched_employee_dict, similarity_score) or (None, score) if no match
    """
    if len(embeddings_matrix) == 0 or len(employee_info) == 0:
        return None, 0.0
    
    similarities = calculate_similarity_matrix(embeddings_matrix, query_embedding)
    max_idx = np.argmax(similarities)
    max_similarity = float(similarities[max_idx])
    
    if max_similarity >= threshold:
        return employee_info[max_idx], max_similarity
    
    return None, max_similarity


def parse_employee_embeddings(employees: List[Dict]) -> Tuple[List[np.ndarray], List[Dict]]:
    """
    Parse and validate employee embeddings from API response.
    
    Args:
        employees: List of employee dicts from API
        
    Returns:
        Tuple of (embeddings_list, valid_employee_info_list)
    """
    embeddings_list = []
    employee_info_list = []
    
    for employee in employees:
        if not employee.get('face_embedding'):
            continue
        
        try:
            stored_embedding = json.loads(employee['face_embedding'])
            
            if len(stored_embedding) != ServiceConfig.EXPECTED_EMBEDDING_DIM:
                logger.warning(
                    f"Skipping employee {employee.get('id')} - "
                    f"Invalid embedding dimension: {len(stored_embedding)} "
                    f"(expected {ServiceConfig.EXPECTED_EMBEDDING_DIM})"
                )
                continue
            
            embeddings_list.append(stored_embedding)
            employee_info_list.append(employee)
        except Exception as e:
            logger.warning(f"Skipping employee {employee.get('id')} - Invalid embedding: {e}")
            continue
    
    return embeddings_list, employee_info_list


def fetch_employees_from_api() -> Optional[List[Dict]]:
    """
    Fetch employees from Laravel API with retry logic.
    
    Returns:
        List of employee dicts or None if failed
    """
    for attempt in range(1, ServiceConfig.MAX_RETRIES + 1):
        try:
            start_time = time.time()
            logger.info(f"Fetching employees from API (attempt {attempt}/{ServiceConfig.MAX_RETRIES})")
            
            response = requests.get(
                f"{ServiceConfig.LARAVEL_API_URL}/api/v1/employees/registered-faces",
                timeout=ServiceConfig.REQUEST_TIMEOUT
            )
            
            fetch_time = (time.time() - start_time) * 1000
            logger.info(f"API response received in {fetch_time:.0f}ms")
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"API returned status {response.status_code}")
                if attempt < ServiceConfig.MAX_RETRIES:
                    logger.warning(f"Retrying in {ServiceConfig.RETRY_DELAY} seconds...")
                    time.sleep(ServiceConfig.RETRY_DELAY)
                    continue
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"API request timeout (>{ServiceConfig.REQUEST_TIMEOUT}s)")
            if attempt < ServiceConfig.MAX_RETRIES:
                logger.warning(f"Retrying in {ServiceConfig.RETRY_DELAY} seconds...")
                time.sleep(ServiceConfig.RETRY_DELAY)
                continue
            return None
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to API at {ServiceConfig.LARAVEL_API_URL}")
            if attempt < ServiceConfig.MAX_RETRIES:
                logger.warning(f"Retrying in {ServiceConfig.RETRY_DELAY} seconds...")
                time.sleep(ServiceConfig.RETRY_DELAY)
                continue
            return None
            
        except Exception as e:
            logger.error(f"Error fetching employees: {e}")
            if attempt < ServiceConfig.MAX_RETRIES:
                logger.warning(f"Retrying in {ServiceConfig.RETRY_DELAY} seconds...")
                time.sleep(ServiceConfig.RETRY_DELAY)
                continue
            return None
    
    logger.error(f"Failed to fetch employees after {ServiceConfig.MAX_RETRIES} attempts")
    return None


def refresh_employee_cache() -> bool:
    """
    Refresh cached employee data from backend and precompute embeddings matrix.
    
    Returns:
        True if successful, False otherwise
    """
    employees = fetch_employees_from_api()
    if employees is None:
        return False
    
    start_time = time.time()
    embeddings_list, employee_info_list = parse_employee_embeddings(employees)
    
    if embeddings_list:
        embeddings_matrix = np.array(embeddings_list)
        cache.update(employees, embeddings_matrix, employee_info_list)
        total_time = (time.time() - start_time) * 1000
        logger.info(
            f"Cache updated in {total_time:.0f}ms: "
            f"{len(employees)} employees, {len(embeddings_list)} with embeddings"
        )
    else:
        cache.update(employees, None, [])
        total_time = (time.time() - start_time) * 1000
        logger.info(
            f"Cache updated in {total_time:.0f}ms: "
            f"{len(employees)} employees, 0 with embeddings"
        )
    
    return True


def ensure_cache_fresh() -> None:
    """Refresh cache if it's stale or empty."""
    if cache.is_stale():
        refresh_employee_cache()


def calculate_scale_factors(original_size: Tuple[int, int], resized_size: Tuple[int, int]) -> Tuple[float, float]:
    """Calculate scale factors for coordinate conversion."""
    scale_x = original_size[0] / resized_size[0]
    scale_y = original_size[1] / resized_size[1]
    return scale_x, scale_y


def scale_bbox(bbox: np.ndarray, scale_x: float, scale_y: float) -> List[int]:
    """Scale bounding box coordinates from resized to original image size."""
    return [
        int(bbox[0] * scale_x),
        int(bbox[1] * scale_y),
        int(bbox[2] * scale_x),
        int(bbox[3] * scale_y)
    ]


def calculate_head_guide_box(face_bbox: np.ndarray, image_size: Tuple[int, int]) -> Dict[str, int]:
    """
    Calculate head guide box from face bounding box.
    
    Args:
        face_bbox: Face bounding box [x1, y1, x2, y2]
        image_size: (width, height) of resized image
        
    Returns:
        Dict with x, y, width, height of head guide box
    """
    x1, y1, x2, y2 = face_bbox.astype(int)
    face_width = x2 - x1
    face_height = y2 - y1
    resized_width, resized_height = image_size
    
    head_top = max(0, int(y1 - face_height * 0.5))
    head_left = max(0, int(x1 - face_width * 0.25))
    head_right = min(resized_width, int(x2 + face_width * 0.25))
    head_bottom = min(resized_height, int(y2 + face_height * 0.15))
    
    return {
        'x': head_left,
        'y': head_top,
        'width': head_right - head_left,
        'height': head_bottom - head_top
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    embeddings_matrix = cache.get_embeddings_matrix()
    return {
        "status": "healthy",
        "model": "InsightFace" if INSIGHTFACE_AVAILABLE else "None",
        "cache_size": len(cache.get_employees()),
        "precomputed_embeddings": embeddings_matrix.shape[0] if embeddings_matrix is not None else 0,
        "cache_age_seconds": cache.get_cache_age()
    }


@app.post("/detect-faces", response_model=FaceDetectionResponse)
async def detect_faces(file: UploadFile = File(...)):
    """Detect faces in image and return bounding boxes with head guide position."""
    if not INSIGHTFACE_AVAILABLE:
        raise HTTPException(503, "Face detection unavailable")
    
    try:
        contents = await file.read()
        
        pil_img = Image.open(BytesIO(contents))
        original_size = pil_img.size
        
        image = image_to_numpy(contents)
        resized_size = (image.shape[1], image.shape[0])
        
        scale_x, scale_y = calculate_scale_factors(original_size, resized_size)
        
        logger.info(
            f"Image: {original_size[0]}x{original_size[1]} → "
            f"{resized_size[0]}x{resized_size[1]}, "
            f"scale: {scale_x:.2f}x, {scale_y:.2f}y"
        )
        
        faces = face_detector.get(image)
        results = []
        head_guide_box = None
        
        if len(faces) > 0:
            face = faces[0]
            face_bbox = face.bbox.astype(int)
            
            head_box_resized = calculate_head_guide_box(face_bbox, resized_size)
            head_guide_box = {
                'x': int(head_box_resized['x'] * scale_x),
                'y': int(head_box_resized['y'] * scale_y),
                'width': int(head_box_resized['width'] * scale_x),
                'height': int(head_box_resized['height'] * scale_y)
            }
            
            for f in faces:
                bbox_resized = f.bbox.astype(int)
                results.append({
                    'bbox': scale_bbox(bbox_resized, scale_x, scale_y),
                    'confidence': float(f.det_score),
                    'embedding': f.embedding.tolist()
                })
        
        return FaceDetectionResponse(
            success=True,
            faces_detected=len(results),
            faces=results,
            ideal_head_position=head_guide_box,
            message=f"{len(results)} face(s) detected"
        )
    
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        raise HTTPException(500, str(e))


@app.post("/check-face-duplicate")
async def check_face_duplicate(file: UploadFile = File(...)):
    """Check if face already exists in registered employees."""
    if not INSIGHTFACE_AVAILABLE:
        raise HTTPException(503, "Service unavailable")
    
    start_time = time.time()
    
    try:
        contents = await file.read()
        image = image_to_numpy(contents)
        faces = face_detector.get(image)
        
        detection_time = (time.time() - start_time) * 1000
        logger.info(f"Face detection completed in {detection_time:.0f}ms")
        
        if len(faces) == 0:
            raise HTTPException(400, "No face detected - Move closer")
        if len(faces) > 1:
            raise HTTPException(400, "Multiple faces detected - Only one person allowed")
        
        detected_embedding = faces[0].embedding
        
        cache_age = cache.get_cache_age()
        if cache_age > ServiceConfig.CACHE_STALE_THRESHOLD:
            logger.info(f"Cache stale ({cache_age}s) - Refreshing in background...")
            asyncio.create_task(asyncio.to_thread(refresh_employee_cache))
        
        embeddings_matrix = cache.get_embeddings_matrix()
        employee_info = cache.get_employee_info()
        
        if embeddings_matrix is None or len(employee_info) == 0:
            logger.warning("No registered faces in cache")
            return {
                "success": True,
                "is_duplicate": False,
                "message": "Cache loading... try again"
            }
        
        comparison_start = time.time()
        matched, max_similarity = find_best_match(
            embeddings_matrix,
            employee_info,
            detected_embedding,
            ServiceConfig.FACE_MATCH_THRESHOLD
        )
        comparison_time = (time.time() - comparison_start) * 1000
        total_time = (time.time() - start_time) * 1000
        
        if matched:
            logger.warning(
                f"Duplicate found: {matched.get('name')} "
                f"({max_similarity:.1%}) in {total_time:.0f}ms "
                f"[{len(employee_info)} compared]"
            )
            return {
                "success": True,
                "is_duplicate": True,
                "matched_employee": {
                    "id": matched['id'],
                    "name": matched.get('name', 'Unknown'),
                    "employee_number": matched.get('employee_number', 'N/A'),
                    "department": matched.get('department', 'N/A')
                },
                "similarity": float(max_similarity),
                "message": f"Already registered: {matched.get('name')}",
                "processing_time_ms": round(total_time, 1),
                "processing_time_seconds": round(total_time/1000, 2)
            }
        
        logger.info(
            f"New face ({max_similarity:.1%} max) in {total_time:.0f}ms "
            f"[{len(employee_info)} compared]"
        )
        return {
            "success": True,
            "is_duplicate": False,
            "message": "Ready to register",
            "processing_time_ms": round(total_time, 1),
            "processing_time_seconds": round(total_time/1000, 2)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Duplicate check error: {e}")
        raise HTTPException(500, str(e))


@app.post("/register-face")
async def register_face(
    file: UploadFile = File(...),
    employee_id: int = Form(...),
    floor_id: int = Form(...),
    room_location: str = Form(...)
):
    """Register a new face for an employee with duplicate checking."""
    if not INSIGHTFACE_AVAILABLE:
        raise HTTPException(503, "Face recognition unavailable - InsightFace not loaded")
    
    try:
        contents = await file.read()
        image = image_to_numpy(contents)
        faces = face_detector.get(image)
        
        if len(faces) == 0:
            raise HTTPException(400, "No face detected in image")
        if len(faces) > 1:
            raise HTTPException(400, "Multiple faces detected - only one person allowed")
        
        face = faces[0]
        face_embedding_array = face.embedding
        face_embedding = face_embedding_array.tolist()
        confidence = float(face.det_score)
        bbox = face.bbox.astype(int).tolist()
        
        if len(face_embedding) != ServiceConfig.EXPECTED_EMBEDDING_DIM:
            raise HTTPException(
                500,
                f"Invalid embedding dimension: {len(face_embedding)} "
                f"(expected {ServiceConfig.EXPECTED_EMBEDDING_DIM}). "
                f"Please restart the face service."
            )
        
        cache_age = cache.get_cache_age()
        if cache_age > ServiceConfig.CACHE_REFRESH_SECONDS:
            logger.info(f"Cache stale ({cache_age}s) - Refreshing...")
            refresh_employee_cache()
        
        embeddings_matrix = cache.get_embeddings_matrix()
        employee_info = cache.get_employee_info()
        
        logger.info(
            f"Checking against {len(employee_info)} registered faces "
            f"(cache age: {cache_age}s)"
        )
        
        if embeddings_matrix is not None and len(employee_info) > 0:
            matched, max_similarity = find_best_match(
                embeddings_matrix,
                employee_info,
                face_embedding_array,
                ServiceConfig.FACE_MATCH_THRESHOLD
            )
            
            if matched:
                raise HTTPException(
                    400,
                    f"Duplicate found: {matched.get('name', 'Employee')} "
                    f"already registered as #{matched.get('employee_number', matched['id'])} "
                    f"(Match: {max_similarity:.0%})"
                )
        
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        logger.info(f"Registering face for employee {employee_id}")
        logger.info(f"  - Confidence: {confidence:.2%}")
        logger.info(f"  - Embedding size: {len(face_embedding)}")
        logger.info(f"  - Floor ID: {floor_id}, Room: {room_location}")
        
        response = requests.post(
            f"{ServiceConfig.LARAVEL_API_URL}/api/v1/employees/{employee_id}/register-face",
            json={
                'embedding': face_embedding,
                'confidence': confidence,
                'bbox': bbox,
                'image_data': image_base64,
                'floor_id': floor_id,
                'room_location': room_location
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest"
            },
            timeout=ServiceConfig.REQUEST_TIMEOUT
        )
        
        logger.info(f"Backend response: Status {response.status_code}")
        
        if response.status_code != 200:
            error_text = response.text
            logger.error(f"Registration failed: {error_text}")
            try:
                error_data = response.json()
                raise HTTPException(response.status_code, error_data.get('message', error_text))
            except:
                raise HTTPException(response.status_code, f"Backend error: {error_text}")
        
        response_data = response.json()
        logger.info(f"Face registered successfully for employee {employee_id}")
        
        logger.info("Refreshing employee cache with new face...")
        refresh_employee_cache()
        logger.info(f"Cache updated - Now tracking {len(cache.get_employees())} employees")
        
        return {
            "success": True,
            "message": "Face registered successfully",
            "employee_id": employee_id,
            "confidence": confidence,
            "has_embedding": True,
            "backend_response": response_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face registration error: {e}")
        raise HTTPException(500, str(e))


@app.post("/identify-face")
async def identify_face(file: UploadFile = File(...)):
    """Identify a face by comparing against registered employees."""
    if not INSIGHTFACE_AVAILABLE:
        raise HTTPException(503, "Face recognition unavailable")
    
    try:
        contents = await file.read()
        image = image_to_numpy(contents)
        faces = face_detector.get(image)
        
        if not faces:
            return {
                "success": True,
                "identified": False,
                "message": "No face detected in image",
                "face_count": 0
            }
        
        face = faces[0]
        face_embedding = face.embedding
        
        embeddings_matrix = cache.get_embeddings_matrix()
        employee_info = cache.get_employee_info()
        
        if embeddings_matrix is not None and len(employee_info) > 0:
            matched, best_similarity = find_best_match(
                embeddings_matrix,
                employee_info,
                face_embedding,
                ServiceConfig.FACE_MATCH_THRESHOLD
            )
            
            if matched:
                logger.info(
                    f"Face identified: {matched.get('name')} (ID: {matched['id']}) - "
                    f"Similarity: {best_similarity:.3f}"
                )
                return {
                    "success": True,
                    "identified": True,
                    "employee_id": matched['id'],
                    "employee_name": matched.get('name', 'Unknown'),
                    "similarity": best_similarity,
                    "confidence": float(face.det_score),
                    "message": f"Identified as {matched.get('name')}"
                }
            else:
                logger.info(
                    f"No match found - Best similarity: {best_similarity:.3f} "
                    f"(threshold: {ServiceConfig.FACE_MATCH_THRESHOLD})"
                )
                return {
                    "success": True,
                    "identified": False,
                    "best_similarity": best_similarity,
                    "threshold": ServiceConfig.FACE_MATCH_THRESHOLD,
                    "message": "Face not recognized"
                }
        else:
            return {
                "success": True,
                "identified": False,
                "message": "No registered faces in database to compare against"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face identification error: {e}")
        raise HTTPException(500, str(e))


@app.on_event("startup")
async def startup_event():
    """Load employee cache on service startup."""
    logger.info("Face Recognition Service starting...")
    logger.info("Loading employee cache...")
    await asyncio.to_thread(refresh_employee_cache)
    logger.info("Cache loaded - Service ready")


if __name__ == "__main__":
    import uvicorn
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", 8001))
        sock.close()
        logger.info("Port 8001 is available")
    except OSError:
        logger.warning("Port 8001 already in use, will attempt to reuse...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="warning",
        access_log=False,
        server_header=False,
        limit_concurrency=50,
        timeout_keep_alive=5
    )
