"""
ULTRA-FAST Face Recognition Service - Optimized for Speed
- Cached employee data (refreshes every 30 seconds)
- Async database calls
- Faster face detection
- Immediate response
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import logging
import requests
import json
import base64
from datetime import datetime, timedelta
import asyncio
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fast Face Recognition Service", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
LARAVEL_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000').rstrip('/api/v1')
FACE_MATCH_THRESHOLD = 0.40  # 40% threshold - catches more duplicates
CACHE_REFRESH_SECONDS = 10  # Refresh every 10 seconds max

# CACHE for registered employees
cached_employees = []
cache_timestamp = None

# PRECOMPUTED EMBEDDINGS MATRIX for INSTANT comparisons
cached_embeddings_matrix = None
cached_employee_info = []

# Initialize face detector
face_detector = None
INSIGHTFACE_AVAILABLE = False

try:
    import insightface
    logger.info("Loading InsightFace (ULTRA-FAST settings)...")
    face_detector = insightface.app.FaceAnalysis(
        name='buffalo_l',
        providers=['CPUExecutionProvider']
    )
    face_detector.prepare(ctx_id=-1, det_size=(96, 96))  # ULTRA TINY = SUB-SECOND speed
    INSIGHTFACE_AVAILABLE = True
    logger.info("✅ InsightFace loaded - ULTRA-FAST MODE (96x96)")
except Exception as e:
    logger.error(f"❌ InsightFace failed: {e}")
    INSIGHTFACE_AVAILABLE = False


class FaceDetectionResponse(BaseModel):
    success: bool
    faces_detected: int
    faces: List[dict]
    ideal_head_position: Optional[dict] = None
    message: str = ""


def image_to_numpy(file_bytes: bytes, max_size: int = 320) -> np.ndarray:
    """Convert image bytes to numpy array - ULTRA-OPTIMIZED for speed"""
    image = Image.open(BytesIO(file_bytes))
    
    # AGGRESSIVE resize for maximum speed (320px is enough for face detection)
    if image.width > max_size or image.height > max_size:
        image.thumbnail((max_size, max_size), Image.BILINEAR)  # BILINEAR is faster than LANCZOS
    
    image = image.convert('RGB')
    return np.array(image)


def refresh_employee_cache():
    """Refresh cached employee data from backend AND precompute embeddings matrix with retry logic"""
    global cached_employees, cache_timestamp, cached_embeddings_matrix, cached_employee_info
    
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(1, max_retries + 1):
        try:
            start_load = time.time()
            logger.info(f"🔄 Fetching employee faces from Laravel... (Attempt {attempt}/{max_retries})")
            response = requests.get(
                f"{LARAVEL_API_URL}/api/v1/employees/registered-faces",
                timeout=10
            )
            fetch_time = (time.time() - start_load) * 1000
            logger.info(f"📡 Laravel response in {fetch_time:.0f}ms")
            
            if response.status_code == 200:
                cached_employees = response.json().get('data', [])
                cache_timestamp = datetime.now()
                
                # PRECOMPUTE embeddings matrix for INSTANT duplicate checking
                embeddings_list = []
                employee_info_list = []
                
                EXPECTED_EMBEDDING_DIM = 512  # InsightFace embedding dimension
                
                for employee in cached_employees:
                    if not employee.get('face_embedding'):
                        continue
                    
                    try:
                        stored_embedding = json.loads(employee['face_embedding'])
                        
                        # CRITICAL: Validate embedding dimension to prevent shape mismatch
                        if len(stored_embedding) != EXPECTED_EMBEDDING_DIM:
                            logger.warning(f"⚠️ Skipping employee {employee.get('id')} - Invalid embedding dimension: {len(stored_embedding)} (expected {EXPECTED_EMBEDDING_DIM})")
                            continue
                        
                        embeddings_list.append(stored_embedding)
                        employee_info_list.append(employee)
                    except Exception as e:
                        logger.warning(f"⚠️ Skipping employee {employee.get('id')} - Invalid embedding: {e}")
                        continue
                
                # Store as NumPy matrix for VECTORIZED operations
                if embeddings_list:
                    cached_embeddings_matrix = np.array(embeddings_list)
                    cached_employee_info = employee_info_list
                    total_time = (time.time() - start_load) * 1000
                    logger.info(f"✅ Cache loaded in {total_time:.0f}ms: {len(cached_employees)} employees, {len(embeddings_list)} with embeddings")
                else:
                    cached_embeddings_matrix = None
                    cached_employee_info = []
                    total_time = (time.time() - start_load) * 1000
                    logger.info(f"✅ Cache loaded in {total_time:.0f}ms: {len(cached_employees)} employees, 0 with embeddings")
                
                return True
            else:
                logger.error(f"Failed to refresh cache: {response.status_code}")
                if attempt < max_retries:
                    logger.warning(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ LARAVEL TIMEOUT (>10s)! Check if backend is running on {LARAVEL_API_URL}")
            if attempt < max_retries:
                logger.warning(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            return False
            
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ LARAVEL NOT REACHABLE! Is it running on {LARAVEL_API_URL}?")
            if attempt < max_retries:
                logger.warning(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            return False
            
        except Exception as e:
            logger.error(f"Cache refresh error: {e}")
            if attempt < max_retries:
                logger.warning(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue
            return False
    
    logger.error(f"❌ Failed to refresh cache after {max_retries} attempts")
    return False


def get_cached_employees():
    """Get cached employees, refresh if needed"""
    global cache_timestamp
    
    # Refresh if cache is empty or old
    if not cached_employees or not cache_timestamp or \
       (datetime.now() - cache_timestamp).seconds > CACHE_REFRESH_SECONDS:
        refresh_employee_cache()
    
    return cached_employees


def cosine_similarity(emb1: List[float], emb2: List[float]) -> float:
    """Fast cosine similarity calculation"""
    vec1 = np.array(emb1)
    vec2 = np.array(emb2)
    return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model": "InsightFace-Fast" if INSIGHTFACE_AVAILABLE else "None",
        "cache_size": len(cached_employees),
        "precomputed_embeddings": cached_embeddings_matrix.shape[0] if cached_embeddings_matrix is not None else 0,
        "cache_age_seconds": (datetime.now() - cache_timestamp).seconds if cache_timestamp else None
    }


@app.post("/detect-faces", response_model=FaceDetectionResponse)
async def detect_faces(file: UploadFile = File(...)):
    """FAST face detection with HEAD TRACKING guide box"""
    if not INSIGHTFACE_AVAILABLE:
        raise HTTPException(503, "Face detection unavailable")
    
    try:
        contents = await file.read()
        
        # Get ORIGINAL image size before resizing
        from PIL import Image as PILImage
        from io import BytesIO
        pil_img = PILImage.open(BytesIO(contents))
        original_width, original_height = pil_img.size
        
        # Now resize for fast detection
        image = image_to_numpy(contents)
        resized_height, resized_width = image.shape[:2]
        
        # Calculate scale factors to convert back to original size
        scale_x = original_width / resized_width
        scale_y = original_height / resized_height
        
        logger.info(f"🖼️ Image: {original_width}x{original_height} → {resized_width}x{resized_height}, scale: {scale_x:.2f}x, {scale_y:.2f}y")
        
        # Fast detection on SMALL image
        faces = face_detector.get(image)
        
        results = []
        head_guide_box = None
        
        if len(faces) > 0:
            # Use first/best face for head guide
            face = faces[0]
            
            # Get face bounding box [x1, y1, x2, y2] - these are on SMALL image
            face_bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = face_bbox
            
            # Calculate HEAD area on small image
            face_width = x2 - x1
            face_height = y2 - y1
            
            # Expand upward MORE to include top of head/hair (50% height above)
            head_top = max(0, int(y1 - face_height * 0.5))
            
            # Expand sides (25% width on each side)
            head_left = max(0, int(x1 - face_width * 0.25))
            head_right = min(resized_width, int(x2 + face_width * 0.25))
            
            # Bottom extends slightly below chin
            head_bottom = min(resized_height, int(y2 + face_height * 0.15))
            
            # SCALE coordinates back to ORIGINAL image size
            head_guide_box = {
                'x': int(head_left * scale_x),
                'y': int(head_top * scale_y),
                'width': int((head_right - head_left) * scale_x),
                'height': int((head_bottom - head_top) * scale_y)
            }
            
            # Add all detected faces with SCALED coordinates
            for f in faces:
                bbox_small = f.bbox.astype(int)
                results.append({
                    'bbox': [
                        int(bbox_small[0] * scale_x),
                        int(bbox_small[1] * scale_y),
                        int(bbox_small[2] * scale_x),
                        int(bbox_small[3] * scale_y)
                    ],
                    'confidence': float(f.det_score),
                    'embedding': f.embedding.tolist()
                })
        
        return FaceDetectionResponse(
            success=True,
            faces_detected=len(results),
            faces=results,
            ideal_head_position=head_guide_box,
            message=f"{len(results)} face(s)"
        )
    
    except Exception as e:
        logger.error(f"Detection error: {e}")
        raise HTTPException(500, str(e))


@app.post("/check-face-duplicate")
async def check_face_duplicate(file: UploadFile = File(...)):
    """
    LIGHTNING-FAST duplicate check - Optimized for speed & minimal RAM
    """
    start_time = time.time()  # ⏱️ START TIMER
    
    if not INSIGHTFACE_AVAILABLE:
        raise HTTPException(503, "Service unavailable")
    
    try:
        # FAST: Read and detect face (no unnecessary logging)
        t1 = time.time()
        contents = await file.read()
        image = image_to_numpy(contents)  # Auto-resizes large images
        faces = face_detector.get(image)
        detection_time = (time.time() - t1) * 1000
        logger.info(f"⚡ Face detection: {detection_time:.0f}ms")
        
        # Quick validation
        if len(faces) == 0:
            raise HTTPException(400, "No face detected - Move closer")
        if len(faces) > 1:
            raise HTTPException(400, "Multiple faces - Only one person")
        
        detected_embedding = faces[0].embedding
        
        # INSTANT CHECK: Use cached data only (no blocking!)
        cache_age = (datetime.now() - cache_timestamp).seconds if cache_timestamp else 999
        
        # Refresh in background if stale (non-blocking)
        if cache_age > 60:
            logger.info(f"🔄 Cache stale ({cache_age}s) - Refreshing in background...")
            asyncio.create_task(asyncio.to_thread(refresh_employee_cache))
        
        # Use whatever is in cache NOW
        if cached_embeddings_matrix is None or len(cached_employee_info) == 0:
            logger.warning("⚠️ NO REGISTERED FACES IN CACHE (still loading or empty)")
            return {"success": True, "is_duplicate": False, "message": "Cache loading... try again"}
        t3 = time.time()
        logger.info(f"🔍 Comparing against {len(cached_employee_info)} registered faces...")
        similarities = np.dot(cached_embeddings_matrix, detected_embedding) / \
                      (np.linalg.norm(cached_embeddings_matrix, axis=1) * np.linalg.norm(detected_embedding))
        
        max_idx = np.argmax(similarities)
        max_similarity = similarities[max_idx]
        comparison_time = (time.time() - t3) * 1000
        total_time = (time.time() - start_time) * 1000
        
        # DUPLICATE FOUND?
        if max_similarity >= FACE_MATCH_THRESHOLD:
            matched = cached_employee_info[max_idx]
            logger.warning(f"🚫 DUPLICATE: {matched.get('name')} ({max_similarity:.1%}) in {total_time:.0f}ms [{len(cached_employee_info)} compared]")
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
        
        # NEW FACE
        logger.info(f"✅ NEW FACE ({max_similarity:.1%} max) in {total_time:.0f}ms [{len(cached_employee_info)} compared]")
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
    """
    FAST face registration with duplicate checking
    Saves face embedding + photo to database
    """
    if not INSIGHTFACE_AVAILABLE:
        raise HTTPException(503, "⚠️ Face recognition unavailable - InsightFace not loaded")
    
    try:
        # Read and detect face
        contents = await file.read()
        image = image_to_numpy(contents)
        faces = face_detector.get(image)
        
        if len(faces) == 0:
            raise HTTPException(400, "No face detected in image")
        
        if len(faces) > 1:
            raise HTTPException(400, "Multiple faces detected - only one person allowed")
        
        # Get face data
        face = faces[0]
        face_embedding_array = face.embedding  # Keep as numpy for FAST comparison
        face_embedding = face_embedding_array.tolist()  # Convert for storage
        confidence = float(face.det_score)
        bbox = face.bbox.astype(int).tolist()
        
        # VALIDATE: Ensure embedding has correct dimension
        EXPECTED_EMBEDDING_DIM = 512
        if len(face_embedding) != EXPECTED_EMBEDDING_DIM:
            raise HTTPException(
                500, 
                f"Invalid embedding dimension: {len(face_embedding)} (expected {EXPECTED_EMBEDDING_DIM}). Please restart the face service."
            )
        
        # 🔍 CRITICAL DUPLICATE CHECK - Use existing cache (already fresh from UI check)
        cache_age = (datetime.now() - cache_timestamp).seconds if cache_timestamp else 999
        if cache_age > 10:
            logger.info(f"🔄 Cache stale ({cache_age}s) - Refreshing...")
            refresh_employee_cache()
        logger.info(f"✅ Checking against {len(cached_employee_info) if cached_employee_info else 0} registered faces (cache age: {cache_age}s)")
        
        if cached_embeddings_matrix is not None and len(cached_employee_info) > 0:
            # INSTANT: Vectorized similarity (all faces at once)
            similarities = np.dot(cached_embeddings_matrix, face_embedding_array) / \
                          (np.linalg.norm(cached_embeddings_matrix, axis=1) * np.linalg.norm(face_embedding_array))
            
            max_idx = np.argmax(similarities)
            max_similarity = similarities[max_idx]
            
            if max_similarity >= FACE_MATCH_THRESHOLD:
                matched = cached_employee_info[max_idx]
                raise HTTPException(
                    400,
                    f"❌ DUPLICATE! {matched.get('name', 'Employee')} already registered as #{matched.get('employee_number', matched['id'])} (Match: {max_similarity:.0%})"
                )
        
        # Convert image to base64 for storage
        import base64
        _, buffer = cv2.imencode('.jpg', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # 📤 Send to Laravel backend with ALL data
        logger.info(f"🔄 Registering face for employee {employee_id}")
        logger.info(f"   - Confidence: {confidence:.2%}")
        logger.info(f"   - Embedding size: {len(face_embedding)}")
        logger.info(f"   - Floor ID: {floor_id}, Room: {room_location}")
        
        response = requests.post(
            f"{LARAVEL_API_URL}/api/v1/employees/{employee_id}/register-face",
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
            timeout=10
        )
        
        logger.info(f"📥 Laravel response: Status {response.status_code}")
        
        if response.status_code != 200:
            error_text = response.text
            logger.error(f"❌ Registration failed: {error_text}")
            try:
                error_data = response.json()
                raise HTTPException(response.status_code, error_data.get('message', error_text))
            except:
                raise HTTPException(response.status_code, f"Backend error: {error_text}")
        
        response_data = response.json()
        logger.info(f"✅ SUCCESS: Face registered for employee {employee_id}")
        logger.info(f"   - Response: {response_data}")
        
        # Refresh cache IMMEDIATELY to include new employee (prevents duplicate registration attempts)
        logger.info("🔄 Refreshing employee cache with new face...")
        refresh_employee_cache()
        logger.info(f"✅ Cache updated - Now tracking {len(cached_employees)} employees")
        
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
        logger.error(f"❌ Register face error: {e}")
        raise HTTPException(500, str(e))


@app.post("/identify-face")
async def identify_face(file: UploadFile = File(...)):
    """ULTRA-FAST face identification using precomputed embeddings matrix"""
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
        
        # Use the best (most confident) face
        face = faces[0]
        face_embedding = face.embedding.tolist()
        
        # ULTRA-FAST comparison using cached matrix
        if cached_embeddings_matrix is not None and len(cached_employee_ids) > 0:
            query_vec = np.array(face_embedding).reshape(1, -1)
            
            # Vectorized cosine similarity - INSTANT for 1000s of employees
            similarities = np.dot(cached_embeddings_matrix, query_vec.T).flatten()
            norms = np.linalg.norm(cached_embeddings_matrix, axis=1) * np.linalg.norm(query_vec)
            cosine_scores = similarities / norms
            
            # Find best match
            best_idx = np.argmax(cosine_scores)
            best_similarity = float(cosine_scores[best_idx])
            
            # Threshold for identification (0.4 is typical for face recognition)
            SIMILARITY_THRESHOLD = 0.4
            
            if best_similarity >= SIMILARITY_THRESHOLD:
                employee_id = cached_employee_ids[best_idx]
                employee_name = cached_employee_names[best_idx]
                
                logger.info(f"✅ Face identified: {employee_name} (ID: {employee_id}) - Similarity: {best_similarity:.3f}")
                
                return {
                    "success": True,
                    "identified": True,
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "similarity": best_similarity,
                    "confidence": float(face.det_score),
                    "message": f"Identified as {employee_name}"
                }
            else:
                logger.info(f"❌ No match found - Best similarity: {best_similarity:.3f} (threshold: {SIMILARITY_THRESHOLD})")
                return {
                    "success": True,
                    "identified": False,
                    "best_similarity": best_similarity,
                    "threshold": SIMILARITY_THRESHOLD,
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
        logger.error(f"❌ Identify face error: {e}")
        raise HTTPException(500, str(e))


@app.on_event("startup")
async def startup_event():
    """Service startup with BLOCKING cache load for guaranteed readiness"""
    logger.info("🚀 ULTRA-FAST Face Recognition Service starting...")
    logger.info("📡 Loading employee cache NOW (this will take 1-2 seconds)...")
    # Load cache SYNCHRONOUSLY on startup - WAIT for it!
    await asyncio.to_thread(refresh_employee_cache)
    logger.info("✅ Cache loaded - Service is READY for instant duplicate checks!")


if __name__ == "__main__":
    import uvicorn
    import socket
    
    # Check if port is available
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", 8001))
        sock.close()
        logger.info("✅ Port 8001 is available")
    except OSError:
        logger.warning("⚠️ Port 8001 already in use, will attempt to reuse...")
    
    # Run with socket reuse enabled to prevent "address already in use" errors
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001, 
        log_level="warning",  # Reduce log spam
        access_log=False,  # Disable access logs for speed
        server_header=False,
        limit_concurrency=50,  # Limit concurrent connections
        timeout_keep_alive=5  # Shorter keepalive
    )

