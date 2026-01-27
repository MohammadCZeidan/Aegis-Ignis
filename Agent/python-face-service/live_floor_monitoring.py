"""
LIVE Floor Monitoring Service - Real-time Employee Detection
- Monitors camera feeds continuously
- Identifies employees on each floor
- Reports presence to backend for dashboard display
- Optimized for speed with cached embeddings
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

import os
import sys
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(PROJECT_ROOT, "env", ".env")
load_dotenv(dotenv_path=ENV_PATH if os.path.exists(ENV_PATH) else None)

# Add repo root to path so "services" package is found
_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import numpy as np
import cv2
import logging
import requests
import json
from datetime import datetime, timedelta
import asyncio
import time
from collections import defaultdict

# Import AlertManager for WhatsApp alerts
from services.alert_manager import AlertManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Live Floor Monitoring Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
LARAVEL_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:8000').rstrip('/api/v1')
FACE_MATCH_THRESHOLD = 0.35  # 35% threshold for live recognition (lower for easier detection)
CACHE_REFRESH_SECONDS = 30  # Refresh employee cache every 30 seconds
DETECTION_INTERVAL = 3  # Process frames every 3 seconds per camera
PRESENCE_TIMEOUT = 60  # Consider person left if not seen for 60 seconds

# Initialize AlertManager for WhatsApp alerts
alert_manager = AlertManager(n8n_webhook_url=os.getenv('N8N_WEBHOOK_URL'))
logger.info(" AlertManager initialized - WhatsApp alerts enabled")

# CACHE for registered employees
cached_employees = []
cache_timestamp = None
cached_embeddings_matrix = None
cached_employee_info = []

# Track camera streams
camera_streams = {}  # {camera_id: stream_url}
camera_floors = {}  # {camera_id: floor_id}
active_monitoring = {}  # {camera_id: is_running}

# Track detected people per floor
floor_presence = defaultdict(dict)  # {floor_id: {employee_id: last_seen_timestamp}}
last_whatsapp_alert = {}  # {floor_id: timestamp} - to avoid spam

# Initialize face detector
face_detector = None
INSIGHTFACE_AVAILABLE = False

try:
    import insightface
    logger.info("Loading InsightFace for live monitoring...")
    face_detector = insightface.app.FaceAnalysis(
        name='buffalo_l',
        providers=['CPUExecutionProvider']
    )
    face_detector.prepare(ctx_id=-1, det_size=(160, 160))  # Balanced for live detection
    INSIGHTFACE_AVAILABLE = True
    logger.info(" InsightFace loaded - Live monitoring ready")
except Exception as e:
    logger.error(f" InsightFace failed: {e}")
    INSIGHTFACE_AVAILABLE = False


class FloorPresenceResponse(BaseModel):
    floor_id: int
    people: List[Dict]
    count: int
    last_updated: str


def refresh_employee_cache():
    """Refresh cached employee data from backend"""
    global cached_employees, cache_timestamp, cached_embeddings_matrix, cached_employee_info
    
    try:
        logger.info("🔄 Refreshing employee cache...")
        response = requests.get(
            f"{LARAVEL_API_URL}/api/v1/employees/registered-faces",
            timeout=10
        )
        
        if response.status_code == 200:
            cached_employees = response.json().get('data', [])
            cache_timestamp = datetime.now()
            
            # Precompute embeddings matrix
            embeddings_list = []
            employee_info_list = []
            
            for employee in cached_employees:
                if not employee.get('face_embedding'):
                    continue
                
                try:
                    stored_embedding = json.loads(employee['face_embedding'])
                    embeddings_list.append(stored_embedding)
                    employee_info_list.append(employee)
                except:
                    continue
            
            if embeddings_list:
                cached_embeddings_matrix = np.array(embeddings_list)
                cached_employee_info = employee_info_list
                logger.info(f" Cache loaded: {len(cached_employees)} employees, {len(embeddings_list)} with faces")
            else:
                cached_embeddings_matrix = None
                cached_employee_info = []
                logger.info(f" Cache loaded: {len(cached_employees)} employees, 0 with faces")
            
            return True
        else:
            logger.error(f"Failed to refresh cache: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Cache refresh error: {e}")
        return False


def identify_face(face_embedding: np.ndarray) -> Optional[Dict]:
    """Identify a face against cached employees"""
    if cached_embeddings_matrix is None or len(cached_employee_info) == 0:
        return None
    
    try:
        # Vectorized similarity comparison
        similarities = np.dot(cached_embeddings_matrix, face_embedding) / \
                      (np.linalg.norm(cached_embeddings_matrix, axis=1) * np.linalg.norm(face_embedding))
        
        max_idx = np.argmax(similarities)
        max_similarity = similarities[max_idx]
        
        if max_similarity >= FACE_MATCH_THRESHOLD:
            matched = cached_employee_info[max_idx]
            return {
                "employee_id": matched['id'],
                "name": matched.get('name', 'Unknown'),
                "employee_number": matched.get('employee_number', 'N/A'),
                "department": matched.get('department', 'N/A'),
                "similarity": float(max_similarity)
            }
        
        return None
    except Exception as e:
        logger.error(f"Face identification error: {e}")
        return None


async def process_camera_feed(camera_id: int, stream_url: str, floor_id: int):
    """Process a single camera feed continuously"""
    logger.info(f"📹 Starting monitoring: Camera {camera_id} on Floor {floor_id}")
    
    cap = None
    frame_skip_counter = 0
    
    try:
        cap = cv2.VideoCapture(stream_url)
        
        if not cap.isOpened():
            logger.error(f"Cannot open camera {camera_id}: {stream_url}")
            return
        
        while active_monitoring.get(camera_id, False):
            ret, frame = cap.read()
            
            if not ret:
                logger.warning(f"Cannot read from camera {camera_id}")
                await asyncio.sleep(1)
                continue
            
            # Skip frames to reduce processing load
            frame_skip_counter += 1
            if frame_skip_counter % (30 * DETECTION_INTERVAL) != 0:  # Process every N seconds at 30fps
                continue
            
            # Process frame for face detection
            await process_frame(frame, camera_id, floor_id)
            
            await asyncio.sleep(0.1)  # Small delay to prevent CPU overload
    
    except Exception as e:
        logger.error(f"Camera {camera_id} error: {e}")
    
    finally:
        if cap:
            cap.release()
        logger.info(f"📹 Stopped monitoring: Camera {camera_id}")


async def process_frame(frame: np.ndarray, camera_id: int, floor_id: int):
    """Process a single frame for face detection and recognition"""
    try:
        # Resize for faster detection
        height, width = frame.shape[:2]
        max_size = 640
        if width > max_size or height > max_size:
            scale = max_size / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        faces = face_detector.get(rgb_frame)
        
        logger.info(f" Camera {camera_id}: Detected {len(faces)} face(s) in frame")
        
        current_time = datetime.now()
        detected_employees = []
        newly_detected = []  # Track newly detected employees for alerts
        
        for face in faces:
            # Identify face
            identified = identify_face(face.embedding)
            
            if identified:
                employee_id = identified['employee_id']
                
                logger.info(f" Identified: {identified['name']} (similarity: {identified['similarity']:.2%})")
                
                # Check if this is a new detection (not seen recently on this floor)
                if employee_id not in floor_presence[floor_id]:
                    newly_detected.append(identified)
                
                # Update floor presence
                floor_presence[floor_id][employee_id] = {
                    'employee_id': employee_id,
                    'name': identified['name'],
                    'employee_number': identified['employee_number'],
                    'department': identified['department'],
                    'last_seen': current_time,
                    'camera_id': camera_id,
                    'similarity': identified['similarity']
                }
                
                detected_employees.append(identified['name'])
            else:
                logger.warning(f" Unknown face detected (no match above {FACE_MATCH_THRESHOLD:.0%})")
        
        if detected_employees:
            logger.info(f" Floor {floor_id} - Camera {camera_id}: Detected {', '.join(detected_employees)}")
        
        # Send WhatsApp alert for newly detected people (with rate limiting)
        if newly_detected and floor_id not in last_whatsapp_alert:
            send_people_detected_alert(floor_id, newly_detected)
            last_whatsapp_alert[floor_id] = current_time
        elif newly_detected and (current_time - last_whatsapp_alert[floor_id]).seconds > 300:
            # Send alert again if 5 minutes have passed
            send_people_detected_alert(floor_id, newly_detected)
            last_whatsapp_alert[floor_id] = current_time
        
        # Clean up old presence records (not seen for PRESENCE_TIMEOUT seconds)
        cleanup_old_presence()
        
        # Report to backend
        await report_floor_presence(floor_id)
        
    except Exception as e:
        logger.error(f"Frame processing error: {e}")


def cleanup_old_presence():
    """Remove employees not seen recently"""
    current_time = datetime.now()
    timeout_threshold = timedelta(seconds=PRESENCE_TIMEOUT)
    
    for floor_id in list(floor_presence.keys()):
        for employee_id in list(floor_presence[floor_id].keys()):
            last_seen = floor_presence[floor_id][employee_id]['last_seen']
            if current_time - last_seen > timeout_threshold:
                logger.info(f"🚶 Employee {employee_id} left Floor {floor_id}")
                del floor_presence[floor_id][employee_id]


def send_people_detected_alert(floor_id: int, detected_people: List[Dict]):
    """Send WhatsApp alert with names of newly detected people on the floor"""
    try:
        if not detected_people:
            return
        
        # Build list of names and departments
        names = [person['name'] for person in detected_people]
        departments = [person.get('department', 'Unknown') for person in detected_people]
        
        # Create WhatsApp message
        message = f"**PEOPLE DETECTED - Floor {floor_id}**\n\n"
        for i, person in enumerate(detected_people, 1):
            message += f"  {i}. {person['name']}\n"
            if person.get('employee_number'):
                message += f"     ID: {person['employee_number']}\n"
            if person.get('department'):
                message += f"     Department: {person['department']}\n"
        
        message += f"\n Location: Floor {floor_id}\n"
        message += f" Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Send via AlertManager presence update (WhatsApp friendly)
        people_details = [
            {
                'name': p['name'],
                'employee_number': p.get('employee_number', ''),
                'department': p.get('department', 'Unknown'),
                'similarity': p.get('similarity', 0)
            }
            for p in detected_people
        ]
        
        success = alert_manager.send_presence_update(
            floor_id=floor_id,
            people_count=len(detected_people),
            people_details=people_details
        )
        
        if success:
            logger.info(f" WhatsApp presence alert sent: {', '.join(names)} on Floor {floor_id}")
        else:
            logger.warning(f" Failed to send WhatsApp presence alert for Floor {floor_id}")
            
    except Exception as e:
        logger.error(f"Error sending people detected alert: {e}")


async def report_floor_presence(floor_id: int):
    """Report current floor presence to backend"""
    try:
        people = list(floor_presence[floor_id].values())
        
        # Prepare data for backend
        presence_data = [
            {
                'employee_id': p['employee_id'],
                'name': p['name'],
                'employee_number': p['employee_number'],
                'department': p['department'],
                'camera_id': p['camera_id'],
                'last_seen': p['last_seen'].isoformat()
            }
            for p in people
        ]
        
        # Send to backend
        response = requests.post(
            f"{LARAVEL_API_URL}/api/v1/presence/update-floor",
            json={
                'floor_id': floor_id,
                'people': presence_data,
                'timestamp': datetime.now().isoformat()
            },
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f" Reported {len(presence_data)} people on Floor {floor_id}")
        else:
            logger.warning(f"Failed to report presence: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error reporting presence: {e}")


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "monitoring_cameras": len([c for c, active in active_monitoring.items() if active]),
        "total_cameras": len(camera_streams),
        "employees_cached": len(cached_employee_info),
        "insightface_available": INSIGHTFACE_AVAILABLE
    }


@app.post("/start-camera/{camera_id}")
async def start_camera_monitoring(camera_id: int):
    """Start monitoring a specific camera"""
    if not INSIGHTFACE_AVAILABLE:
        raise HTTPException(503, "Face detection unavailable")
    
    try:
        # Get camera details from backend
        response = requests.get(f"{LARAVEL_API_URL}/api/v1/cameras/{camera_id}")
        
        if response.status_code != 200:
            raise HTTPException(404, "Camera not found")
        
        camera_data = response.json()['data']
        stream_url = camera_data.get('stream_url') or camera_data.get('rtsp_url')
        floor_id = camera_data.get('floor_id')
        
        # Handle webcam:// format - convert to device ID
        if stream_url and stream_url.startswith('webcam://'):
            stream_url = int(stream_url.replace('webcam://', ''))
            logger.info(f"Converted webcam URL to device ID: {stream_url}")
        
        if not stream_url and stream_url != 0:  # 0 is valid for webcam
            raise HTTPException(400, "Camera has no stream URL")
        
        if not floor_id:
            raise HTTPException(400, "Camera not assigned to a floor")
        
        # Store camera info
        camera_streams[camera_id] = stream_url
        camera_floors[camera_id] = floor_id
        active_monitoring[camera_id] = True
        
        # Start monitoring in background
        asyncio.create_task(process_camera_feed(camera_id, stream_url, floor_id))
        
        logger.info(f" Started monitoring Camera {camera_id} on Floor {floor_id}")
        
        return {
            "success": True,
            "message": f"Started monitoring camera {camera_id}",
            "camera_id": camera_id,
            "floor_id": floor_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting camera: {e}")
        raise HTTPException(500, str(e))


@app.post("/stop-camera/{camera_id}")
async def stop_camera_monitoring(camera_id: int):
    """Stop monitoring a specific camera"""
    if camera_id in active_monitoring:
        active_monitoring[camera_id] = False
        logger.info(f" Stopped monitoring Camera {camera_id}")
        
        return {
            "success": True,
            "message": f"Stopped monitoring camera {camera_id}"
        }
    else:
        raise HTTPException(404, "Camera not being monitored")


@app.post("/start-all-cameras")
async def start_all_cameras():
    """Start monitoring all cameras from backend"""
    if not INSIGHTFACE_AVAILABLE:
        raise HTTPException(503, "Face detection unavailable")
    
    try:
        # Get all cameras
        response = requests.get(f"{LARAVEL_API_URL}/api/v1/cameras")
        
        if response.status_code != 200:
            raise HTTPException(500, "Failed to fetch cameras")
        
        cameras = response.json()['data']
        started = []
        failed = []
        
        for camera in cameras:
            camera_id = camera['id']
            stream_url = camera.get('stream_url') or camera.get('rtsp_url')
            floor_id = camera.get('floor_id')
            
            # Handle webcam:// format
            if stream_url and stream_url.startswith('webcam://'):
                stream_url = int(stream_url.replace('webcam://', ''))
            
            if (not stream_url and stream_url != 0) or not floor_id:
                failed.append(camera_id)
                continue
            
            camera_streams[camera_id] = stream_url
            camera_floors[camera_id] = floor_id
            active_monitoring[camera_id] = True
            
            asyncio.create_task(process_camera_feed(camera_id, stream_url, floor_id))
            started.append(camera_id)
        
        logger.info(f" Started monitoring {len(started)} cameras")
        
        return {
            "success": True,
            "started": started,
            "failed": failed,
            "message": f"Monitoring {len(started)} cameras"
        }
        
    except Exception as e:
        logger.error(f"Error starting cameras: {e}")
        raise HTTPException(500, str(e))


@app.get("/floor-presence/{floor_id}", response_model=FloorPresenceResponse)
async def get_floor_presence(floor_id: int):
    """Get current people on a specific floor"""
    cleanup_old_presence()
    
    people = list(floor_presence[floor_id].values())
    
    # Format response
    formatted_people = [
        {
            'employee_id': p['employee_id'],
            'name': p['name'],
            'employee_number': p['employee_number'],
            'department': p['department'],
            'last_seen': p['last_seen'].isoformat(),
            'camera_id': p['camera_id']
        }
        for p in people
    ]
    
    return FloorPresenceResponse(
        floor_id=floor_id,
        people=formatted_people,
        count=len(formatted_people),
        last_updated=datetime.now().isoformat()
    )


@app.get("/all-floors-presence")
async def get_all_floors_presence():
    """Get current people on all floors"""
    cleanup_old_presence()
    
    result = {}
    for floor_id, people_dict in floor_presence.items():
        people = list(people_dict.values())
        result[floor_id] = {
            'floor_id': floor_id,
            'people': [
                {
                    'employee_id': p['employee_id'],
                    'name': p['name'],
                    'employee_number': p['employee_number'],
                    'department': p['department'],
                    'last_seen': p['last_seen'].isoformat()
                }
                for p in people
            ],
            'count': len(people)
        }
    
    return {
        "success": True,
        "floors": result,
        "total_people": sum(len(people) for people in floor_presence.values()),
        "last_updated": datetime.now().isoformat()
    }


@app.post("/test/add-person")
async def test_add_person(
    floor_id: int,
    employee_id: int,
    name: str,
    employee_number: str = "TEST001",
    department: str = "Testing",
    camera_id: int = 1
):
    """TEST ENDPOINT: Manually add a person to a floor for testing"""
    current_time = datetime.now()
    
    floor_presence[floor_id][employee_id] = {
        'employee_id': employee_id,
        'name': name,
        'employee_number': employee_number,
        'department': department,
        'last_seen': current_time,
        'camera_id': camera_id,
        'similarity': 1.0
    }
    
    # Report to backend
    await report_floor_presence(floor_id)
    
    logger.info(f" TEST: Added {name} to Floor {floor_id}")
    
    return {
        "success": True,
        "message": f"Added {name} to floor {floor_id}",
        "floor_id": floor_id,
        "employee": floor_presence[floor_id][employee_id]
    }


@app.delete("/test/clear-floor/{floor_id}")
async def test_clear_floor(floor_id: int):
    """TEST ENDPOINT: Clear all people from a floor"""
    if floor_id in floor_presence:
        count = len(floor_presence[floor_id])
        floor_presence[floor_id].clear()
        await report_floor_presence(floor_id)
        logger.info(f" TEST: Cleared {count} people from Floor {floor_id}")
        return {"success": True, "message": f"Cleared {count} people from floor {floor_id}"}
    else:
        return {"success": True, "message": "Floor was already empty"}


@app.post("/api/cameras/update-floor-assignments")
async def update_camera_floor_assignments(request: Request):
    """Update floor assignments for monitored cameras (syncs with settings changes)"""
    try:
        data = await request.json()
        assignments = data.get('assignments', [])
        
        updated = []
        not_found = []
        
        for assignment in assignments:
            camera_id = int(assignment['cameraId'])
            floor_id = int(assignment['floorId'])
            
            # Check if this camera is being monitored
            if camera_id in camera_floors:
                old_floor = camera_floors[camera_id]
                camera_floors[camera_id] = floor_id
                
                logger.info(f"📹 Updated Camera {camera_id}: Floor {old_floor} → {floor_id}")
                updated.append({
                    'camera_id': camera_id,
                    'old_floor': old_floor,
                    'new_floor': floor_id
                })
            else:
                not_found.append(camera_id)
        
        logger.info(f" Floor monitoring: Updated {len(updated)} camera assignments")
        
        return {
            "success": True,
            "message": f"Updated {len(updated)} camera floor assignments",
            "updated": updated,
            "not_monitored": not_found
        }
        
    except Exception as e:
        logger.error(f" Error updating floor assignments: {e}")
        raise HTTPException(500, str(e))


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info(" Live Floor Monitoring Service starting...")
    
    # Load employee cache
    await asyncio.to_thread(refresh_employee_cache)
    
    # Start cache refresh background task
    asyncio.create_task(cache_refresh_task())
    
    logger.info(" Live monitoring service ready!")


async def cache_refresh_task():
    """Background task to refresh employee cache periodically"""
    while True:
        await asyncio.sleep(CACHE_REFRESH_SECONDS)
        await asyncio.to_thread(refresh_employee_cache)


if __name__ == "__main__":
    import uvicorn
    
    logger.info(" Starting Live Floor Monitoring Service on port 8003")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info",
        access_log=True
    )
