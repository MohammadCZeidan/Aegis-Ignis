"""
Check floors in database
"""
import requests

url = "http://35.180.227.44/api/v1/floors"
headers = {
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")
print(response.json())
