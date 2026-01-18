"""
Live Camera Detection & Streaming Server
- Real-time camera streaming to dashboard
- Face recognition with person tracking (5-minute timeout)
- Fire detection with alert screenshots
- Integration with Laravel backend for alerts
"""
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import cv2
import numpy as np
import requests
import time
import json
import base64
from datetime import datetime, timedelta
from threading import Thread, Lock
from collections import defaultdict
import os

app = Flask(__name__)
CORS(app)

# Configuration
FACE_SERVICE_URL = "http://localhost:8001"
LARAVEL_API_URL = "http://35.180.117.85/api/v1"
CAMERA_CONFIG_FILE = "camera_config.json"

# Performance settings - MAXIMUM SPEED!
CAMERA_FPS = 60  # Target FPS
FRAME_SKIP_FACE = 2  # Check faces every 2 frames (30 FPS - FAST!)
FRAME_SKIP_FIRE = 4  # Check fire every 4 frames (15 per second - VERY FAST!)
JPEG_QUALITY = 75  # Lower quality for speed
STREAM_FPS = 30  # Stream at 30 FPS

# Person tracking (5-minute timeout)
PERSON_TIMEOUT_SECONDS = 300  # 5 minutes
person_last_seen = {}  # {employee_name: timestamp}
person_tracker_lock = Lock()
people_in_rooms = defaultdict(set)  # {camera_id: set of employee_names}

# Fire detection state
last_fire_alert_time = {}  # {camera_id: timestamp}
FIRE_ALERT_COOLDOWN = 30  # Send alert max once per 30 seconds (prevent spam!)

# Camera instances
cameras = {}
camera_locks = {}

print("="*80)
print("LIVE CAMERA DETECTION & STREAMING SERVER")
print("="*80)

def load_cameras():
    """Load camera configuration"""
    try:
        with open(CAMERA_CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('cameras', [])
    except Exception as e:
        print(f"Error loading camera config: {e}")
        return []

def save_screenshot(frame, camera_id, detection_type="fire"):
    """Save screenshot to Laravel public storage"""
    try:
        # Use absolute path based on current directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        screenshot_dir = os.path.join(base_dir, "backend-laravel", "public", "storage", "alerts")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        # Generate filename with microseconds to prevent overwriting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{detection_type}_cam{camera_id}_{timestamp}.jpg"
        filepath = os.path.join(screenshot_dir, filename)
        
        # Save image with high quality
        success = cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        if success:
            print(f"✅ Screenshot saved: {filepath}")
            # Return web-accessible path
            return f"storage/alerts/{filename}"
        else:
            print(f"❌ Failed to write image to: {filepath}")
            return None
    except Exception as e:
        print(f"❌ Error saving screenshot: {e}")
        import traceback
        traceback.print_exc()
        return None

def send_fire_alert(camera_id, camera_name, floor_id, room, frame, confidence, fire_type="fire"):
    """Send fire alert to Laravel backend with screenshot"""
    try:
        # Save screenshot
        screenshot_path = save_screenshot(frame, camera_id, detection_type="fire")
        
        # Send alert to Laravel
        alert_data = {
            "event_type": "fire",
            "severity": "critical" if confidence > 0.7 else "warning",
            "camera_id": camera_id,
            "camera_name": camera_name,
            "floor_id": floor_id,
            "room": room,
            "confidence": confidence,
            "fire_type": fire_type,
            "screenshot_path": screenshot_path,
            "detected_at": datetime.now().isoformat()
        }
        
        response = requests.post(
            f"{LARAVEL_API_URL}/alerts/fire",
            json=alert_data,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            print(f"✓ Fire alert sent for camera {camera_id}")
            return True
        else:
            print(f"✗ Failed to send fire alert: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error sending fire alert: {e}")
        return False

def track_person(employee_name, camera_id, camera_name, floor_id, room):
    """Track person presence with 5-minute timeout"""
    with person_tracker_lock:
        current_time = datetime.now()
        
        # Check if person just entered
        if employee_name not in person_last_seen:
            # Person entered
            print(f"👤 {employee_name} ENTERED {room} (Floor {floor_id})")
            people_in_rooms[camera_id].add(employee_name)
            
            # Log entry to Laravel
            try:
                requests.post(
                    f"{LARAVEL_API_URL}/presence/entry",
                    json={
                        "employee_name": employee_name,
                        "camera_id": camera_id,
                        "camera_name": camera_name,
                        "floor_id": floor_id,
                        "room": room,
                        "action": "entered",
                        "timestamp": current_time.isoformat()
                    },
                    timeout=2
                )
            except:
                pass
        
        # Update last seen time
        person_last_seen[employee_name] = current_time

def check_person_timeouts():
    """Check for people who haven't been seen in 5 minutes"""
    while True:
        try:
            time.sleep(30)  # Check every 30 seconds
            
            with person_tracker_lock:
                current_time = datetime.now()
                timeout_threshold = current_time - timedelta(seconds=PERSON_TIMEOUT_SECONDS)
                
                # Find people who timed out
                timed_out = []
                for employee_name, last_seen in list(person_last_seen.items()):
                    if last_seen < timeout_threshold:
                        timed_out.append(employee_name)
                
                # Remove timed out people
                for employee_name in timed_out:
                    del person_last_seen[employee_name]
                    
                    # Remove from all rooms
                    for camera_id in people_in_rooms:
                        if employee_name in people_in_rooms[camera_id]:
                            people_in_rooms[camera_id].remove(employee_name)
                            print(f"👤 {employee_name} LEFT (timeout - not seen for 5 min)")
                            
                            # Log exit to Laravel
                            try:
                                requests.post(
                                    f"{LARAVEL_API_URL}/presence/exit",
                                    json={
                                        "employee_name": employee_name,
                                        "action": "left",
                                        "reason": "timeout",
                                        "timestamp": current_time.isoformat()
                                    },
                                    timeout=2
                                )
                            except:
                                pass
        except Exception as e:
            print(f"Error in person timeout checker: {e}")

class CameraStream:
    def __init__(self, camera_config):
        self.camera_id = camera_config['id']
        self.name = camera_config['name']
        self.stream_url = camera_config['stream_url']
        self.floor_id = camera_config['floor_id']
        self.room = camera_config.get('room', 'Unknown')
        self.is_active = camera_config.get('is_active', True)
        
        self.cap = None
        self.frame = None
        self.lock = Lock()
        self.running = False
        
        # Detection counters
        self.frame_count = 0
        self.face_detect_interval = FRAME_SKIP_FACE  # Faster face detection!
        self.fire_detect_interval = FRAME_SKIP_FIRE  # MUCH faster fire detection!
        
    def start(self):
        """Start camera capture thread"""
        if self.running:
            return
            
        # Open camera with optimized settings
        stream_source = int(self.stream_url) if self.stream_url.isdigit() else self.stream_url
        self.cap = cv2.VideoCapture(stream_source)
        
        # Optimize camera settings for MAXIMUM SPEED
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize lag
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)  # Lower res for speed
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)  # Lower res for speed
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # Faster codec
        
        if not self.cap.isOpened():
            print(f"✗ Failed to open camera {self.name}")
            return False
            
        self.running = True
        Thread(target=self._capture_loop, daemon=True).start()
        print(f"✓ Camera {self.name} started")
        return True
        
    def stop(self):
        """Stop camera capture"""
        self.running = False
        if self.cap:
            self.cap.release()
            
    def _capture_loop(self):
        """Main capture loop with detection"""
        import gc
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue
                
            self.frame_count += 1
            
            # Face recognition (with safety check)
            if self.face_detect_interval > 0 and self.frame_count % self.face_detect_interval == 0:
                self._detect_faces(frame)
            
            # Fire detection (with safety check)
            if self.fire_detect_interval > 0 and self.frame_count % self.fire_detect_interval == 0:
                self._detect_fire(frame)
            
            # Store frame for streaming
            with self.lock:
                self.frame = frame.copy()
            
            # Memory management - cleanup every 200 frames
            if self.frame_count % 200 == 0:
                gc.collect()
                
            # Small sleep to prevent CPU overload
            time.sleep(0.01)  # 10ms delay prevents CPU spike
            
    def _detect_faces(self, frame):
        """Run face recognition"""
        try:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            
            response = requests.post(
                f"{FACE_SERVICE_URL}/recognize-face",
                files={"file": ("frame.jpg", buffer.tobytes(), "image/jpeg")},
                data={
                    "camera_id": self.camera_id,
                    "floor_id": self.floor_id,
                    "room_location": self.room
                },
                timeout=2
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('matched'):
                    employee_name = result.get('employee_name', 'Unknown')
                    track_person(employee_name, self.camera_id, self.name, 
                               self.floor_id, self.room)
        except:
            pass
            
    def _detect_fire(self, frame):
        """Detect ONLY actual fire flames - very strict to avoid false positives from red lights"""
        try:
            # Convert to HSV for color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # ULTRA-STRICT FIRE DETECTION - Excludes red lights, LEDs, faces
            # Real fire characteristics:
            # 1. Orange/Yellow dominant (NOT pure red like LEDs)
            # 2. Extremely bright (250+ brightness)
            # 3. High saturation (150+)
            # 4. Irregular, flickering shape
            
            # Orange flames - PRIMARY fire indicator
            lower_orange = np.array([8, 150, 230])  # Bright saturated orange
            upper_orange = np.array([20, 255, 255])
            mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
            
            # Yellow flames - SECONDARY fire indicator
            lower_yellow = np.array([20, 120, 240])  # Bright yellow
            upper_yellow = np.array([30, 255, 255])
            mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
            
            # EXCLUDE pure red (red LEDs, red lights have LOW saturation or mid brightness)
            # Only detect DEEP saturated red that appears in real flames
            lower_red = np.array([0, 200, 230])  # VERY high saturation + brightness
            upper_red = np.array([6, 255, 255])
            mask_red = cv2.inRange(hsv, lower_red, upper_red)
            
            # Combine fire colors (orange is most important)
            fire_mask = cv2.bitwise_or(mask_orange, cv2.bitwise_or(mask_yellow, mask_red))
            
            # CRITICAL: Must be ULTRA bright (real fire is intensely bright)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, ultra_bright = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)  # Higher threshold
            
            # Fire = Highly saturated color + Ultra brightness
            fire_mask = cv2.bitwise_and(fire_mask, ultra_bright)
            
            # Morphological operations
            kernel = np.ones((3, 3), np.uint8)
            fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel)
            fire_mask = cv2.dilate(fire_mask, kernel, iterations=1)
            
            # Count fire pixels
            fire_pixels = cv2.countNonZero(fire_mask)
            total_pixels = frame.shape[0] * frame.shape[1]
            fire_ratio = fire_pixels / total_pixels
            
            # STRICT threshold - must be at least 2% of frame (real flame is visible, not tiny LED)
            if fire_ratio > 0.02:  # 2% minimum - excludes small red LEDs
                
                # Must be clustered (not scattered pixels)
                contours, _ = cv2.findContours(fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if len(contours) > 0:
                    # Get largest contour
                    largest_contour = max(contours, key=cv2.contourArea)
                    contour_area = cv2.contourArea(largest_contour)
                    contour_ratio = contour_area / total_pixels
                    
                    # Must have significant clustered area (2%+ prevents small LEDs)
                    if contour_ratio > 0.02:
                        # Verify it's flame-shaped (not circular like a light bulb)
                        x, y, w, h = cv2.boundingRect(largest_contour)
                        aspect_ratio = h / w if w > 0 else 0
                        
                        # Flames are elongated or compact, NOT wide and flat
                        if aspect_ratio > 0.5:  # Must have some vertical dimension
                            confidence = min(fire_ratio * 20, 1.0)
                        
                        # Draw bounding box
                        annotated_frame = frame.copy()
                        cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 0, 255), 3)
                        cv2.putText(annotated_frame, f"FIRE - {confidence*100:.0f}%", 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                        
                        print(f"🔥 ACTUAL FIRE! Area: {fire_ratio*100:.1f}%, Cluster: {contour_ratio*100:.1f}%, Confidence: {confidence*100:.0f}%")
                        
                        # Send alert
                        current_time = time.time()
                        last_alert = last_fire_alert_time.get(self.camera_id, 0)
                        
                        if current_time - last_alert > FIRE_ALERT_COOLDOWN:
                            print(f"🚨 Sending FIRE ALERT")
                            success = send_fire_alert(
                                self.camera_id, self.name, self.floor_id,
                                self.room, annotated_frame, confidence, "fire"
                            )
                            if success:
                                last_fire_alert_time[self.camera_id] = current_time
                                print(f"✅ Alert sent!")
                        else:
                            print(f"⏳ Cooldown ({FIRE_ALERT_COOLDOWN - (current_time - last_alert):.0f}s)")
                    else:
                        print(f"❌ Fire pixels too scattered - cluster: {contour_ratio:.3f} ({contour_ratio*100:.1f}%), need 2%+")
        except Exception as e:
            print(f"❌ Fire detection error: {e}")
            
    def get_frame(self):
        """Get current frame for streaming"""
        with self.lock:
            if self.frame is None:
                # Return blank frame
                return np.zeros((480, 640, 3), dtype=np.uint8)
            return self.frame.copy()

def generate_frames(camera_id):
    """Generator for video streaming"""
    camera = cameras.get(camera_id)
    if not camera:
        # Return blank frame
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(blank, "Camera Not Found", (150, 240),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        ret, buffer = cv2.imencode('.jpg', blank)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        return
    
    frame_counter = 0
    while True:
        frame = camera.get_frame()
        
        # Add overlay info
        cv2.putText(frame, f"{camera.name} - Floor {camera.floor_id}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, camera.room, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Show people in room
        people = list(people_in_rooms.get(camera_id, set()))
        if people:
            y_pos = 90
            for person in people[:5]:  # Show max 5
                cv2.putText(frame, f"✓ {person}", (10, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                y_pos += 25
        
        # Encode frame (lower quality for speed)
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        frame_bytes = buffer.tobytes()
        del buffer  # Free memory immediately
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Memory management - force garbage collection every 100 frames
        frame_counter += 1
        if frame_counter % 100 == 0:
            import gc
            gc.collect()
        
        time.sleep(0.033)  # 30fps

# API Endpoints
@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "service": "Live Camera Detection Server",
        "cameras_active": len([c for c in cameras.values() if c.running]),
        "total_cameras": len(cameras)
    })

@app.route('/api/cameras')
def get_cameras():
    """Get all cameras with stream URLs"""
    camera_list = []
    for cam_id, cam in cameras.items():
        camera_list.append({
            "id": cam.camera_id,
            "name": cam.name,
            "floor_id": cam.floor_id,
            "room": cam.room,
            "is_active": cam.running,
            "stream_url": f"/video_feed/{cam.camera_id}",
            "people_present": list(people_in_rooms.get(cam_id, set()))
        })
    
    return jsonify({
        "success": True,
        "cameras": camera_list
    })

@app.route('/video_feed/<int:camera_id>')
def video_feed(camera_id):
    """Video streaming route"""
    return Response(
        generate_frames(camera_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/api/people-present')
def get_people_present():
    """Get all people currently present"""
    with person_tracker_lock:
        people_by_location = {}
        for camera_id, people_set in people_in_rooms.items():
            camera = cameras.get(camera_id)
            if camera and people_set:
                location_key = f"Floor {camera.floor_id} - {camera.room}"
                people_by_location[location_key] = list(people_set)
        
        return jsonify({
            "success": True,
            "people_present": people_by_location,
            "total_count": len(person_last_seen)
        })

@app.route('/api/camera/<int:camera_id>/snapshot')
def get_snapshot(camera_id):
    """Get current frame as base64"""
    camera = cameras.get(camera_id)
    if not camera:
        return jsonify({"error": "Camera not found"}), 404
    
    frame = camera.get_frame()
    ret, buffer = cv2.imencode('.jpg', frame)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return jsonify({
        "success": True,
        "image": img_base64,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/cameras/update-config', methods=['POST'])
def update_camera_config():
    """Update camera floor assignments in config file"""
    try:
        data = request.json
        assignments = data.get('assignments', [])
        
        # Load current config
        try:
            with open(CAMERA_CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except:
            config = {"cameras": []}
        
        # Update camera assignments
        for assignment in assignments:
            camera_id = int(assignment['cameraId'])
            floor_id = int(assignment['floorId'])
            location = assignment.get('location', '')
            
            # Find and update camera in config
            for cam in config['cameras']:
                if cam['id'] == camera_id:
                    cam['floor_id'] = floor_id
                    cam['room'] = location
                    break
        
        # Save updated config
        with open(CAMERA_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Update running camera instances
        for assignment in assignments:
            camera_id = int(assignment['cameraId'])
            floor_id = int(assignment['floorId'])
            location = assignment.get('location', '')
            
            if camera_id in cameras:
                old_floor = cameras[camera_id].floor_id
                old_room = cameras[camera_id].room
                cameras[camera_id].floor_id = floor_id
                cameras[camera_id].room = location
                print(f"  📹 Camera {camera_id}: Floor {old_floor} → {floor_id}, Room '{old_room}' → '{location}'")
            else:
                print(f"  ⚠ Camera {camera_id} not found in active cameras")
        
        print(f"✓ Camera config updated: {len(assignments)} cameras")
        print(f"✓ Config file saved to: {CAMERA_CONFIG_FILE}")
        
        return jsonify({
            "success": True,
            "message": "Camera configuration updated successfully",
            "updated_cameras": len(assignments),
            "active_cameras": list(cameras.keys())
        })
        
    except Exception as e:
        print(f"✗ Failed to update camera config: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # Load and start cameras
    camera_configs = load_cameras()
    print(f"\nLoading {len(camera_configs)} cameras...")
    
    for config in camera_configs:
        cam = CameraStream(config)
        cameras[config['id']] = cam
        if config.get('is_active', True):
            cam.start()
    
    # Start person timeout checker
    Thread(target=check_person_timeouts, daemon=True).start()
    print("\n✓ Person tracking system started (5-minute timeout)")
    
    print("\n" + "="*80)
    print("SERVER READY")
    print("="*80)
    print(f"Streaming at: http://localhost:5000")
    print(f"Camera API: http://localhost:5000/api/cameras")
    print(f"People Present: http://localhost:5000/api/people-present")
    print("="*80 + "\n")
    
    # Start Flask server
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
