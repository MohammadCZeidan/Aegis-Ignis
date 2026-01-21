"""
Test ML Fire Detection - Send image to service and verify EC2 alert
"""
import requests
import cv2
import sys

# Configuration
ML_SERVICE_URL = "http://localhost:8004/detect-fire-ml"
EC2_ALERTS_URL = "http://35.180.227.44/api/v1/alerts"

def test_fire_detection(image_path):
    """Test fire detection with an image"""
    print(f"\n{'='*60}")
    print("🔥 TESTING ML FIRE DETECTION")
    print(f"{'='*60}\n")
    
    # Read image
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
    except FileNotFoundError:
        print(f"❌ Image not found: {image_path}")
        print("\n💡 To test, you need a fire image!")
        print("   1. Find a fire image online")
        print("   2. Save it as 'test_fire.jpg'")
        print("   3. Run: python test_ml_fire_detection.py test_fire.jpg")
        return
    
    print(f"📸 Testing with image: {image_path}")
    
    # Send to ML service
    files = {'file': ('test_fire.jpg', image_data, 'image/jpeg')}
    data = {
        'camera_id': 1,
        'floor_id': 3
    }
    
    try:
        print(f"\n🚀 Sending to ML service: {ML_SERVICE_URL}")
        response = requests.post(ML_SERVICE_URL, files=files, data=data, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ ML Detection Result:")
            print(f"   🔥 Detected: {result.get('detected')}")
            print(f"   📈 Confidence: {result.get('confidence', 0)*100:.1f}%")
            print(f"   🏷️  Type: {result.get('type')}")
            print(f"   🔍 Method: {result.get('method')}")
            print(f"   ⚠️  Severity: {result.get('severity')}")
            print(f"   🆔 Alert ID: {result.get('alert_id')}")
            print(f"   📱 N8N Alert Sent: {result.get('n8n_alert_sent')}")
            print(f"   👥 People on Floor: {result.get('people_on_floor')}")
            
            if result.get('detected'):
                print(f"\n🎉 SUCCESS! Fire detected and alert sent to EC2!")
                
                # Check EC2 alerts
                print(f"\n🔍 Checking EC2 alerts...")
                try:
                    ec2_response = requests.get(EC2_ALERTS_URL, timeout=10)
                    if ec2_response.status_code == 200:
                        alerts = ec2_response.json()
                        if isinstance(alerts, list):
                            print(f"   📊 Total alerts on EC2: {len(alerts)}")
                            if len(alerts) > 0:
                                latest = alerts[-1] if isinstance(alerts[-1], dict) else {}
                                print(f"   🆔 Latest Alert ID: {latest.get('id')}")
                                print(f"   🎯 Confidence: {latest.get('confidence', 0)*100:.1f}%")
                        else:
                            print(f"   ℹ️  Alerts format: {type(alerts)}")
                    else:
                        print(f"   ⚠️  EC2 returned status: {ec2_response.status_code}")
                except Exception as e:
                    print(f"   ⚠️  Could not fetch EC2 alerts: {e}")
            else:
                print(f"\n❌ No fire detected in image")
        else:
            print(f"\n❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to ML service!")
        print(f"   Make sure it's running on port 8004")
        print(f"   Run: cd fire-detection-service && start-ml-service.bat")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "test_fire.jpg"
    
    test_fire_detection(image_path)
    
    print(f"\n{'='*60}")
    print("✅ Test Complete!")
    print(f"{'='*60}\n")
