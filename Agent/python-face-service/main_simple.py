"""
Simple Face Detection Service using OpenCV
Fallback when InsightFace is not available
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Face Detection Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load OpenCV Haar Cascade face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

logger.info(" OpenCV Face Detector loaded successfully")


class FaceDetectionResponse(BaseModel):
    success: bool
    faces_detected: int
    faces: List[dict]
    message: str = ""


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "model": "OpenCV Haar Cascade",
        "ready": True
    }


@app.post("/detect-faces")
async def detect_faces(file: UploadFile = File(...)):
    """Detect faces using OpenCV"""
    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents))
        image_np = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        results = []
        for (x, y, w, h) in faces:
            results.append({
                'bbox': [int(x), int(y), int(x+w), int(y+h)],
                'confidence': 0.95,  # OpenCV doesn't provide confidence
                'embedding': []  # No embedding from OpenCV
            })
        
        return {
            "success": True,
            "faces_detected": len(results),
            "faces": results,
            "message": f"Detected {len(results)} face(s)"
        }
    
    except Exception as e:
        logger.error(f"Error detecting faces: {e}")
        raise HTTPException(500, f"Face detection error: {str(e)}")


@app.post("/detect-face")
async def detect_face(photo: UploadFile = File(...)):
    """Single face detection for registration"""
    try:
        contents = await photo.read()
        image = Image.open(BytesIO(contents))
        image_np = np.array(image.convert('RGB'))
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            raise HTTPException(
                status_code=400,
                detail="No face detected in the image. Please upload a clear photo with a visible face."
            )
        
        # Use first detected face
        x, y, w, h = faces[0]
        
        # Generate a simple "embedding" (just using pixel values for now)
        face_region = image_np[y:y+h, x:x+w]
        face_resized = cv2.resize(face_region, (128, 128))
        embedding = face_resized.flatten()[:512].tolist()  # Simple 512-dim vector
        
        return {
            "embedding": embedding,
            "confidence": 0.95,
            "bounding_box": [int(x), int(y), int(x+w), int(y+h)],
            "success": True
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting face: {e}")
        raise HTTPException(500, f"Face detection error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    logger.info(" Starting Simple Face Detection Service on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
