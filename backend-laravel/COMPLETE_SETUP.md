# Complete Laravel Backend Setup

## Overview

This Laravel backend handles:
- **Employee photos** - Stored from registration apps
- **Camera management** - Add/edit/delete cameras
- **Fire detection** - Live detection reporting (metadata only, no photos)
- **People tracking** - Who is on which floor when fire detected

## Key Features

### 1. Photo Storage
- Employee photos from registration apps are stored in `storage/app/public/employees/`
- Photos are accessible via `/storage/employees/filename.jpg`
- Photos are linked to employee records

### 2. Camera Management
- Add cameras with RTSP URLs
- Assign cameras to floors
- Set camera positions (x, y, z coordinates)
- Enable/disable cameras

### 3. Fire Detection
- **NO PHOTOS SAVED** - Only metadata stored:
  - Floor ID and name
  - Room location where fire started
  - People present on floor (from occupancy system)
  - Detection confidence
  - Timestamp
- Live detection from camera feeds
- Automatic alert creation

## Setup Steps

### 1. Install Dependencies
```bash
cd backend-laravel
composer install
```

### 2. Configure Environment
```bash
cp .env.example .env
php artisan key:generate
```

Edit `.env`:
```env
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=aegis_ignis
DB_USERNAME=aegis_user
DB_PASSWORD=aegis_password

APP_URL=http://localhost:8000
```

### 3. Create Storage Link
```bash
php artisan storage:link
```

This creates a symlink so photos are accessible via `/storage/...`

### 4. Run Migrations
```bash
php artisan migrate
```

### 5. Seed Database
```bash
php artisan db:seed
```

### 6. Start Server
```bash
php artisan serve
```

## API Endpoints

### Camera Management
```bash
# List cameras
GET /api/v1/cameras

# Get camera
GET /api/v1/cameras/{id}

# Add camera (admin only)
POST /api/v1/cameras
{
  "floor_id": 1,
  "name": "Main Entrance Camera",
  "rtsp_url": "rtsp://camera-ip:554/stream",
  "position_x": 10.5,
  "position_y": 20.3,
  "position_z": 2.1,
  "is_active": true
}

# Update camera (admin only)
PUT /api/v1/cameras/{id}

# Delete camera (admin only)
DELETE /api/v1/cameras/{id}
```

### Fire Detection Reporting
```bash
# Report fire detection (called by detection service)
POST /api/v1/fire-detections/report
{
  "camera_id": 1,
  "floor_id": 1,
  "detection_type": "fire",
  "confidence": 0.85,
  "room_location": "Main Hall",
  "bounding_box": [100, 200, 150, 180],
  "coordinates": {"x": 10.5, "y": 20.3, "z": 2.1}
}

# Get fire events (requires auth)
GET /api/v1/fire-detections

# Get fire event details
GET /api/v1/fire-detections/{id}

# Resolve fire event
POST /api/v1/fire-detections/{id}/resolve
```

### Floor Management
```bash
# List floors
GET /api/v1/floors

# Get floor
GET /api/v1/floors/{id}

# Add floor (admin only)
POST /api/v1/floors
{
  "building_id": 1,
  "floor_number": 4,
  "name": "Fourth Floor"
}

# Update floor (admin only)
PUT /api/v1/floors/{id}

# Delete floor (admin only)
DELETE /api/v1/floors/{id}
```

## Fire Detection Service Setup

### 1. Configure Fire Detection Service
Edit `fire-detection-service/.env`:
```env
API_BASE_URL=http://localhost:8000/api/v1
CAMERA_ID=0
FLOOR_ID=1
ROOM_LOCATION=Main Hall
DETECTION_INTERVAL=1.0
CONFIDENCE_THRESHOLD=0.5
```

### 2. Run Fire Detection Service
```bash
cd fire-detection-service
python main.py
```

The service will:
- Monitor camera feed in real-time
- Detect fire-like colors
- Report to backend API (metadata only)
- **NOT save any photos**

## Data Stored for Fire Events

When fire is detected, the backend stores:

```json
{
  "fire_event_id": 1,
  "floor_id": 1,
  "floor_name": "Ground Floor",
  "room_location": "Main Hall",
  "camera_id": 1,
  "camera_name": "Main Entrance Camera",
  "detection_type": "fire",
  "confidence": 0.85,
  "timestamp": "2024-01-15T10:30:00Z",
  "people_on_floor": {
    "total_count": 3,
    "people": [
      {
        "track_id": "person_123",
        "employee_id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "confidence": 0.95
      },
      {
        "track_id": "person_124",
        "employee_id": 2,
        "name": "Jane Smith",
        "email": "jane@example.com",
        "confidence": 0.92
      },
      {
        "track_id": "person_125",
        "employee_id": null,
        "confidence": 0.88
      }
    ]
  }
}
```

## Photo Storage

Employee photos are stored in:
- **Path:** `storage/app/public/employees/`
- **URL:** `http://localhost:8000/storage/employees/filename.jpg`
- **Database:** `employees.photo_url` stores the URL

## Testing

### Test Camera Creation
```bash
curl -X POST http://localhost:8000/api/v1/cameras \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "floor_id": 1,
    "name": "Test Camera",
    "rtsp_url": "rtsp://test:554/stream",
    "is_active": true
  }'
```

### Test Fire Detection Report
```bash
curl -X POST http://localhost:8000/api/v1/fire-detections/report \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": 1,
    "floor_id": 1,
    "detection_type": "fire",
    "confidence": 0.85,
    "room_location": "Test Room"
  }'
```

## Production Notes

1. **Photo Storage:** Use S3 or similar for production
2. **Fire Detection:** Add authentication token for detection service
3. **Queue Jobs:** Use queues for fire detection processing
4. **WebSockets:** Add real-time notifications for fire events
5. **Rate Limiting:** Add rate limiting to fire detection endpoint

