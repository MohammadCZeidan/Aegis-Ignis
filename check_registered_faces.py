"""
Check registered faces
"""
import requests

url = "http://35.180.227.44/api/v1/employees/registered-faces"
headers = {
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
import json
print(json.dumps(response.json(), indent=2))
