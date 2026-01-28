"""
FastAPI endpoints for face recognition service.
"""
import logging
import time
import asyncio
import base64
import cv2
import requests
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from PIL import Image
from io import BytesIO

from config import ServiceConfig
from cache import ThreadSafeCache
from face_detector import face_detector, INSIGHTFACE_AVAILABLE
from similarity import find_best_match
from image_utils import image_to_numpy, calculate_scale_factors, scale_bbox, calculate_head_guide_box
from cache_service import refresh_employee_cache, ensure_cache_fresh

logger = logging.getLogger(__name__)


class FaceDetectionResponse(BaseModel):
    """Response model for face detection."""
    success: bool
    faces_detected: int
    faces: List[dict]
    ideal_head_position: Optional[dict] = None
    message: str = ""

def register_endpoints(app: FastAPI, cache: ThreadSafeCache):
    """Register all API endpoints."""
    
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
            
            # Get original image size for reference
            pil_img = Image.open(BytesIO(contents))
            original_size = pil_img.size
            
            # Resize image for faster detection
            image = image_to_numpy(contents)
            resized_size = (image.shape[1], image.shape[0])
            
            # Calculate scale factors for coordinate conversion
            scale_x = original_size[0] / resized_size[0]
            scale_y = original_size[1] / resized_size[1]
            
            logger.info(
                f"Image: {original_size[0]}x{original_size[1]} → "
                f"{resized_size[0]}x{resized_size[1]}, "
                f"scale: {scale_x:.2f}x, {scale_y:.2f}y"
            )
            
            # Detect faces on resized image (for speed)
            faces = face_detector.get(image)
            results = []
            head_guide_box = None
            
            if len(faces) > 0:
                face = faces[0]
                face_bbox = face.bbox.astype(int)
                
                # Calculate head guide box on resized image, then scale to original blob size
                # Frontend expects coordinates relative to video.videoWidth x video.videoHeight
                head_box_resized = calculate_head_guide_box(face_bbox, resized_size)
                head_guide_box = {
                    'x': int(head_box_resized['x'] * scale_x),
                    'y': int(head_box_resized['y'] * scale_y),
                    'width': int(head_box_resized['width'] * scale_x),
                    'height': int(head_box_resized['height'] * scale_y)
                }
                
                # Return bbox coordinates scaled to original blob size
                # This matches the video stream dimensions that the frontend uses
                for f in faces:
                    bbox_resized = f.bbox.astype(int)
                    scaled_bbox = scale_bbox(bbox_resized, scale_x, scale_y)
                    results.append({
                        'bbox': scaled_bbox,  # [x1, y1, x2, y2] in original blob coordinates
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
            logger.error(f"Face detection error: {e}", exc_info=True)
            raise HTTPException(500, f"Face detection error: {str(e)}")
    
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
            
            # Get cache data first (fast - just reading from memory)
            cache_age = cache.get_cache_age()
            embeddings_matrix = cache.get_embeddings_matrix()
            employee_info = cache.get_employee_info()
            embeddings_norms = cache.get_embeddings_norms()
            
            # Trigger background refresh if stale, but don't wait for it
            if cache_age > ServiceConfig.CACHE_STALE_THRESHOLD:
                logger.info(f"Cache stale ({cache_age}s) - Refreshing in background (non-blocking)...")
                try:
                    asyncio.create_task(asyncio.to_thread(refresh_employee_cache, cache))
                except Exception as e:
                    logger.warning(f"Failed to start background cache refresh: {e}")
            
            # Early exit if no cached data (don't wait for refresh)
            if embeddings_matrix is None or len(employee_info) == 0:
                logger.warning("No registered faces in cache - returning immediately")
                return {
                    "success": True,
                    "is_duplicate": False,
                    "message": "No registered faces found - ready to register",
                    "processing_time_ms": round((time.time() - start_time) * 1000, 1)
                }
            
            # Perform comparison (should be fast with precomputed norms)
            comparison_start = time.time()
            matched, max_similarity = find_best_match(
                embeddings_matrix,
                employee_info,
                detected_embedding,
                ServiceConfig.FACE_MATCH_THRESHOLD,
                embeddings_norms  # Pass precomputed norms for speed
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
                logger.info(f"Cache stale ({cache_age}s) - Refreshing in background (non-blocking)...")
                try:
                    asyncio.create_task(asyncio.to_thread(refresh_employee_cache, cache))
                except Exception as e:
                    logger.warning(f"Failed to start background cache refresh: {e}")
            
            embeddings_matrix = cache.get_embeddings_matrix()
            employee_info = cache.get_employee_info()
            embeddings_norms = cache.get_embeddings_norms()  # Use precomputed norms
            
            logger.info(
                f"Checking against {len(employee_info)} registered faces "
                f"(cache age: {cache_age}s)"
            )
            
            if embeddings_matrix is not None and len(employee_info) > 0:
                matched, max_similarity = find_best_match(
                    embeddings_matrix,
                    employee_info,
                    face_embedding_array,
                    ServiceConfig.FACE_MATCH_THRESHOLD,
                    embeddings_norms  # Pass precomputed norms for speed
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
            refresh_employee_cache(cache)
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
            embeddings_norms = cache.get_embeddings_norms()  # Use precomputed norms
            
            if embeddings_matrix is not None and len(employee_info) > 0:
                matched, best_similarity = find_best_match(
                    embeddings_matrix,
                    employee_info,
                    face_embedding,
                    ServiceConfig.FACE_MATCH_THRESHOLD,
                    embeddings_norms  # Pass precomputed norms for speed
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
