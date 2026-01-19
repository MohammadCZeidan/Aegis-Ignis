"""
Improved Face Recognition Service with Database Integration
- Fast face detection and embedding generation
- Database integration for face matching
- Real-time presence tracking
"""
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
from datetime import datetime

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
    logger.warning("⚠️ Using OpenCV fallback for face DETECTION only. Face REGISTRATION disabled.")
except Exception as e:
    logger.error(f"Error loading face model: {e}")
    logger.error("InsightFace is installed but failed to load. This is likely a version incompatibility.")
    # Load OpenCV fallback for basic detection (no embeddings)
    opencv_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    logger.warning("⚠️ Using OpenCV fallback for face DETECTION only. Face REGISTRATION disabled.")


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
                detail="⚠️ Face registration is currently unavailable. InsightFace model is not loaded. Please contact system administrator to install InsightFace properly for face recognition to work."
            )
        
        # Read image
        contents = await file.read()
        image = image_to_numpy(contents)
        
        # Detect faces with InsightFace (required for embeddings)
        faces = detect_faces_insightface(image)
        # Detect faces with InsightFace (required for embeddings)
        faces = detect_faces_insightface(image)
        
        if len(faces) == 0:
            raise HTTPException(status_code=400, detail="No face detected in image")
        
        if len(faces) > 1:
            raise HTTPException(status_code=400, detail="Multiple faces detected. Please provide image with single face")
        
        face = faces[0]
        
        # Check if this face is already registered (duplicate detection)
        # This will ALWAYS run now because we require InsightFace
        try:
            # Get all registered employees from Laravel
            registered_response = requests.get(f"{LARAVEL_API_URL}/employees/registered-faces", timeout=10)
            
            if registered_response.status_code == 200:
                registered_employees = registered_response.json().get('data', [])
                
                # Check for matches against all registered faces
                for employee in registered_employees:
                    if not employee.get('face_embedding'):
                        continue
                    
                    stored_embedding = json.loads(employee['face_embedding'])
                    similarity = cosine_similarity(face['embedding'], stored_embedding)
                    
                    # If very high similarity, this face is already registered
                    # Using stricter threshold to prevent same person registering multiple times
                    if similarity >= 0.50:  # 50% similarity threshold (very strict)
                        employee_name = employee.get('name', 'Unknown')
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Hi {employee_name}! 👋 You're already registered in our system. Your employee ID is {employee.get('employee_number', employee['id'])}. No need to register again! (Match confidence: {similarity:.0%})"
                        )
        except HTTPException:
            raise  # Re-raise the duplicate error
        except Exception as e:
            logger.warning(f"Could not check for duplicate faces: {e}")
            # Don't allow registration if duplicate check fails - too risky!
            raise HTTPException(
                status_code=500,
                detail="Could not verify if this face is already registered. Please try again or contact support."
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
        
        logger.info(f"🔄 Sending face registration to Laravel API for employee {employee_id}")
        logger.info(f"   - Confidence: {face['confidence']:.2%}")
        logger.info(f"   - Embedding size: {len(face['embedding']) if face.get('embedding') else 'NO EMBEDDING'}")
        logger.info(f"   - Floor ID: {floor_id}, Room: {room_location}")
        
        response = requests.post(
            f"{LARAVEL_API_URL}/employees/{employee_id}/register-face",
            json=payload,
            timeout=10
        )
        
        logger.info(f"📥 Laravel API response: Status {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"✅ SUCCESS: Face registered for employee {employee_id}")
            logger.info(f"   - Response: {response_data}")
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
            logger.error(f"❌ FAILED: Laravel API returned {response.status_code}")
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
                detail="⚠️ Face duplicate checking is currently unavailable. InsightFace model is not loaded. Please contact system administrator."
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
        
        # Check if this face is already registered
        try:
                # Get all registered employees from Laravel
                logger.info(f"Fetching registered faces from {LARAVEL_API_URL}/employees/registered-faces")
                registered_response = requests.get(f"{LARAVEL_API_URL}/employees/registered-faces", timeout=10)
                
                if registered_response.status_code != 200:
                    logger.error(f"Laravel API returned status {registered_response.status_code}: {registered_response.text}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Backend API error (status {registered_response.status_code}). Please check Laravel service."
                    )
                
                registered_employees = registered_response.json().get('data', [])
                logger.info(f"Found {len(registered_employees)} registered employees to check")
                
                # Check for matches against all registered faces
                for employee in registered_employees:
                    if not employee.get('face_embedding'):
                        logger.debug(f"Skipping employee {employee.get('id')} - no embedding")
                        continue
                    
                    try:
                        stored_embedding = json.loads(employee['face_embedding'])
                        similarity = cosine_similarity(face['embedding'], stored_embedding)
                        logger.debug(f"Employee {employee.get('name')} similarity: {similarity:.2%}")
                        
                        # If very high similarity, this face is already registered
                        # Using stricter threshold to prevent same person registering multiple times
                        if similarity >= 0.50:  # 50% similarity threshold (very strict)
                            employee_name = employee.get('name', 'Unknown')
                            logger.info(f"DUPLICATE FOUND: {employee_name} with {similarity:.2%} similarity")
                            return {
                                "success": True,
                                "is_duplicate": True,
                                "matched_employee": {
                                    "id": employee['id'],
                                    "name": employee_name,
                                    "employee_number": employee.get('employee_number', 'N/A'),
                                    "department": employee.get('department', 'N/A')
                                },
                                "similarity": similarity,
                                "message": f"Hi {employee_name}! 👋 You're already registered in our system. Employee ID: {employee.get('employee_number', employee['id'])} | Department: {employee.get('department', 'N/A')} | Match: {similarity:.0%}"
                            }
                    except Exception as embedding_error:
                        logger.error(f"Error processing embedding for employee {employee.get('id')} ({employee.get('name')}): {embedding_error}")
                        continue  # Skip this employee and continue checking others
                
                # No match found
                logger.info("No duplicate found - safe to register")
                return {
                    "success": True,
                    "is_duplicate": False,
                    "message": "Face is not registered yet. Safe to proceed with registration."
                }
        except requests.RequestException as req_error:
            logger.error(f"Error calling Laravel API: {req_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Could not connect to backend API. Please try again."
            )
        except Exception as e:
            logger.error(f"Unexpected error checking duplicates: {e}", exc_info=True)
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
        detected_embedding = detected_face['embedding']
        
        # Get all registered employees from Laravel
        response = requests.get(f"{LARAVEL_API_URL}/employees/registered-faces", timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch registered faces")
        
        registered_employees = response.json().get('data', [])
        
        # Find best match
        best_match = None
        best_similarity = 0.0
        
        for employee in registered_employees:
            if not employee.get('face_embedding'):
                continue
            
            stored_embedding = json.loads(employee['face_embedding'])
            similarity = cosine_similarity(detected_embedding, stored_embedding)
            
            if similarity > best_similarity and similarity >= FACE_MATCH_THRESHOLD:
                best_similarity = similarity
                best_match = employee
        
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
