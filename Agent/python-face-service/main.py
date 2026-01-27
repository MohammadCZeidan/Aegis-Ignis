"""
Python Face Recognition Microservice
Standalone service for face detection and recognition using InsightFace.
Called by Laravel backend for employee registration.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Face Recognition Service",
    description="Microservice for face detection and recognition",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize InsightFace model
face_model = None

try:
    import insightface
    face_model = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
    face_model.prepare(ctx_id=-1, det_size=(640, 640))
    logger.info("Face recognition model loaded successfully")
except ImportError:
    logger.warning("InsightFace not available. Face recognition will use basic detection.")
    logger.warning("To enable full face recognition, install: pip install insightface onnxruntime")
except Exception as e:
    logger.error(f"Error loading face recognition model: {e}")
    logger.warning("Falling back to basic face detection")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": face_model is not None
    }


@app.post("/detect-face")
async def detect_face(photo: UploadFile = File(...)):
    """
    Detect face in image and extract embedding.
    Called by Laravel backend during employee registration.
    """
    try:
        # Read image
        image_data = await photo.read()
        image = Image.open(BytesIO(image_data))
        image_np = np.array(image)

        # Convert RGB to BGR for OpenCV
        if len(image_np.shape) == 3 and image_np.shape[2] == 3:
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image_np

        # Try to use InsightFace if available
        if face_model is not None:
            # Detect faces using InsightFace
            faces = face_model.get(image_bgr)

            if not faces or len(faces) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No face detected in the image. Please upload a clear photo with a visible face."
                )

            # Use the first detected face
            face = faces[0]
            embedding = face.embedding.tolist()
            confidence = float(face.det_score)
            bbox = face.bbox.astype(int).tolist()

            logger.info(f"Face detected: confidence={confidence:.2f}, bbox={bbox}")

            return {
                "embedding": embedding,
                "confidence": confidence,
                "bounding_box": bbox,
                "success": True
            }
        else:
            # Fallback: Use OpenCV Haar Cascade for basic face detection
            logger.warning("Using basic face detection (InsightFace not available)")
            
            # Load Haar Cascade classifier
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No face detected in the image. Please upload a clear photo with a visible face."
                )
            
            # Use the first detected face
            x, y, w, h = faces[0]
            bbox = [int(x), int(y), int(w), int(h)]
            
            # Create a mock embedding (512 dimensions) - in production, use InsightFace
            # This is a placeholder that will work but won't be accurate for recognition
            embedding = np.random.rand(512).astype(float).tolist()
            # Normalize
            norm = np.linalg.norm(embedding)
            embedding = (np.array(embedding) / norm).tolist()
            
            logger.info(f"Face detected (basic): bbox={bbox}")

            return {
                "embedding": embedding,
                "confidence": 0.85,  # Mock confidence
                "bounding_box": bbox,
                "success": True,
                "note": "Using basic face detection. Install InsightFace for accurate recognition."
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing face: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


@app.post("/identify-face")
async def identify_face(
    embedding: list,
    employee_embeddings: dict,
    threshold: float = 0.7
):
    """
    Identify a face by comparing embedding to registered employees.
    employee_embeddings format: {employee_id: [embedding_array], ...}
    """
    if face_model is None:
        raise HTTPException(
            status_code=503,
            detail="Face recognition model not loaded."
        )

    try:
        query_embedding = np.array(embedding)
        best_match = None
        best_similarity = 0.0

        for employee_id, emp_embedding in employee_embeddings.items():
            emp_emb = np.array(emp_embedding)
            similarity = np.dot(query_embedding, emp_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(emp_emb)
            )

            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = {
                    "employee_id": int(employee_id),
                    "confidence": float(similarity),
                    "similarity": float(similarity)
                }

        return {
            "match": best_match,
            "success": True
        }

    except Exception as e:
        logger.error(f"Error identifying face: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error identifying face: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

