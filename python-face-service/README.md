# Python Face Recognition Microservice

Standalone microservice for face detection and recognition using InsightFace. Called by Laravel backend.

## Purpose

This service handles face recognition processing that requires Python/ML libraries. The Laravel backend calls this service when:
- Registering employees with face photos
- Identifying people in camera feeds

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start service:**
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```

Service will be available at: http://localhost:8001

## Endpoints

### Health Check
```
GET /health
```

### Detect Face
```
POST /detect-face
Content-Type: multipart/form-data

Body: photo (image file)

Response:
{
  "embedding": [0.123, 0.456, ...],
  "confidence": 0.95,
  "bounding_box": [x, y, x2, y2],
  "success": true
}
```

### Identify Face
```
POST /identify-face
Content-Type: application/json

Body:
{
  "embedding": [0.123, 0.456, ...],
  "employee_embeddings": {
    "1": [0.111, 0.222, ...],
    "2": [0.333, 0.444, ...]
  },
  "threshold": 0.7
}

Response:
{
  "match": {
    "employee_id": 1,
    "confidence": 0.85,
    "similarity": 0.85
  },
  "success": true
}
```

## Integration with Laravel

Update `backend-laravel/app/Services/FaceRecognitionService.php`:

```php
public function detectAndExtractFace(UploadedFile $image): ?array
{
    $client = new \GuzzleHttp\Client();
    
    try {
        $response = $client->post('http://localhost:8001/detect-face', [
            'multipart' => [
                [
                    'name' => 'photo',
                    'contents' => fopen($image->getRealPath(), 'r'),
                    'filename' => $image->getClientOriginalName()
                ]
            ],
            'timeout' => 30
        ]);
        
        $result = json_decode($response->getBody(), true);
        
        if ($result['success'] ?? false) {
            return [
                'embedding' => $result['embedding'],
                'confidence' => $result['confidence'],
            ];
        }
        
        return null;
    } catch (\Exception $e) {
        Log::error('Face recognition service error: ' . $e->getMessage());
        return null;
    }
}
```

## Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

## Notes

- This service only handles face recognition
- All other API endpoints are in Laravel
- Database is managed by Laravel
- This is a stateless microservice

