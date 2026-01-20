"""
Test face identification endpoint
"""
import requests

# Test with a photo
url = "http://localhost:8001/identify-face"

# You need to provide an actual image file
image_path = input("Enter path to image file to identify: ")

with open(image_path, 'rb') as f:
    files = {'file': f}
    response = requests.post(url, files=files)
    
print(f"Status: {response.status_code}")
print(response.json())
