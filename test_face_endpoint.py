"""
Test script to verify face embedding endpoint on EC2
"""
import requests
import json

# Test data
employee_id = 1
url = "http://35.180.227.44/api/v1/employees/1/register-face"

payload = {
    "embedding": [0.1, 0.2, 0.3, 0.4, 0.5] * 20,  # 100 values
    "confidence": 0.95,
    "bbox": [100, 100, 200, 200],
    "image_data": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",  # 1x1 pixel test image
    "floor_id": 2,
    "room_location": "Test Room"
}

print(f"Testing: {url}")
print(f"Payload: {json.dumps(payload, indent=2)[:200]}...")
print("-" * 50)

try:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
