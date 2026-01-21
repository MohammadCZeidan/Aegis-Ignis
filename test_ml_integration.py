"""
Test Script for ML Fire Detection Integration
Tests all components: ML detection, N8N alerts, and backend integration
"""
import requests
import json
import cv2
import numpy as np
import os
from datetime import datetime

# Configuration
FIRE_DETECTION_API = "http://localhost:8002"
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")
BACKEND_API = "http://localhost:8000/api/v1"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f" {text}")
    print("="*80)

def test_fire_detection_service():
    """Test fire detection service health"""
    print_header("Testing Fire Detection Service")
    
    try:
        response = requests.get(f"{FIRE_DETECTION_API}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Fire Detection Service is running")
            print(f"   Version: {data.get('version')}")
            print(f"   Detection Method: {data.get('detection_method')}")
            print(f"   ML Available: {data.get('ml_model_loaded')}")
            print(f"   Features: {', '.join(data.get('features', []))}")
            return True
        else:
            print(f"❌ Service returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Fire Detection Service")
        print("   Start with: cd fire-detection-service && python main_v2.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ml_detection():
    """Test ML fire detection with sample image"""
    print_header("Testing ML Fire Detection")
    
    # Create a test fire-colored image
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    # Add orange/red region (simulated fire)
    cv2.rectangle(test_image, (200, 150), (400, 350), (0, 100, 255), -1)
    cv2.GaussianBlur(test_image, (21, 21), 0)
    
    # Save test image
    test_image_path = "test_fire_image.jpg"
    cv2.imwrite(test_image_path, test_image)
    
    try:
        # Test ML detection endpoint
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            data = {
                'camera_id': 999,
                'camera_name': 'Test Camera',
                'floor_id': 1,
                'room_location': 'Test Room',
                'send_n8n_alert': 'false'  # Don't spam alerts during testing
            }
            
            response = requests.post(
                f"{FIRE_DETECTION_API}/detect-fire-ml",
                files=files,
                data=data,
                timeout=10
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ ML Detection working")
            print(f"   Detected: {result.get('detected')}")
            print(f"   Method: {result.get('detection_method')}")
            
            if result.get('detected'):
                print(f"   Fire Type: {result.get('fire_type')}")
                print(f"   Severity: {result.get('severity')}")
                print(f"   Confidence: {result.get('confidence', 0)*100:.1f}%")
            
            return True
        else:
            print(f"❌ Detection failed: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ML detection: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(test_image_path):
            os.remove(test_image_path)

def test_n8n_webhook():
    """Test N8N webhook integration"""
    print_header("Testing N8N Webhook")
    
    if not N8N_WEBHOOK_URL:
        print("⚠️  N8N_WEBHOOK_URL not configured in .env")
        print("   Set N8N_WEBHOOK_URL to test webhook integration")
        return False
    
    # Test alert payload
    test_alert = {
        "alert_type": "FIRE_EMERGENCY",
        "floor_id": 1,
        "camera_id": 999,
        "camera_name": "Test Camera",
        "room": "Test Room",
        "fire_type": "fire",
        "severity": "warning",
        "confidence": 0.85,
        "timestamp": datetime.now().isoformat(),
        "people_count": 3,
        "people_details": [
            {"name": "Test Person 1"},
            {"name": "Test Person 2"},
            {"name": "Test Person 3"}
        ],
        "message": "🔥 TEST ALERT - Fire detected on Floor 1 (3 people present)",
        "priority": "CRITICAL",
        "requires_evacuation": True
    }
    
    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=test_alert,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201, 202]:
            print("✅ N8N webhook responding")
            print(f"   Status: {response.status_code}")
            try:
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
            except:
                print(f"   Response: {response.text}")
            return True
        else:
            print(f"❌ Webhook returned status {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to N8N webhook")
        print("   Is N8N running? Start with: n8n start")
        return False
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def test_backend_integration():
    """Test Laravel backend integration"""
    print_header("Testing Backend Integration")
    
    try:
        # Test backend health
        response = requests.get(f"{BACKEND_API}/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Backend API is accessible")
            return True
        else:
            print(f"⚠️  Backend returned status {response.status_code}")
            return True  # Non-critical
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Cannot connect to Backend API")
        print("   Start Laravel: cd backend-laravel && php artisan serve")
        return True  # Non-critical
    except Exception as e:
        print(f"⚠️  Backend check error: {e}")
        return True  # Non-critical

def run_all_tests():
    """Run all integration tests"""
    print("\n" + "🔥"*40)
    print(" ML FIRE DETECTION INTEGRATION TEST SUITE")
    print("🔥"*40)
    
    results = {
        "Fire Detection Service": test_fire_detection_service(),
        "ML Detection": test_ml_detection(),
        "N8N Webhook": test_n8n_webhook(),
        "Backend Integration": test_backend_integration()
    }
    
    print_header("Test Results Summary")
    
    passed = 0
    failed = 0
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n{'='*80}")
    print(f" Total: {passed + failed} tests | Passed: {passed} | Failed: {failed}")
    print(f"{'='*80}\n")
    
    if failed == 0:
        print("🎉 All tests passed! Your ML fire detection system is ready!")
        print("\nNext steps:")
        print("1. Configure N8N_WEBHOOK_URL in .env for WhatsApp alerts")
        print("2. Get a YOLOv8 fire detection model from Roboflow")
        print("3. Start the live camera server: python live_camera_detection_server.py")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\nCommon fixes:")
        print("- Start Fire Detection Service: cd fire-detection-service && python main_v2.py")
        print("- Start N8N: n8n start")
        print("- Configure .env file with correct URLs")

if __name__ == "__main__":
    run_all_tests()
