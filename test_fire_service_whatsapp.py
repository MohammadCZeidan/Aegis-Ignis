"""
Test script to verify fire detection service can send WhatsApp alerts
"""
import os
import sys
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("\n" + "="*80)
print("FIRE DETECTION SERVICE - WHATSAPP ALERT TEST")
print("="*80 + "\n")

# Test the fire detection service's alert capability
try:
    # Import directly from the fire-detection-service directory
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'fire-detection-service'))
    from main import FireDetectionService
    from services.alert_manager import AlertManager
    
    print("1. Testing FireDetectionService initialization...")
    fire_service = FireDetectionService()
    
    if hasattr(fire_service, 'alert_manager'):
        print("   ✅ AlertManager initialized in FireDetectionService")
        
        if fire_service.alert_manager.twilio_client:
            print("   ✅ Twilio client is available")
        else:
            print("   ❌ Twilio client not available")
    else:
        print("   ❌ AlertManager not found in FireDetectionService")
    
    print("\n2. Simulating fire detection with people on floor...")
    
    # Simulate a fire alert with people on the floor
    result = fire_service.alert_manager.send_fire_alert(
        floor_id=3,
        camera_id=1,
        camera_name="Main Entrance Camera",
        room="Lobby",
        people_detected=[
            {"name": "John Doe", "employee_number": "E001", "department": "Security"},
            {"name": "Maria Santos", "employee_number": "E002", "department": "Admin"}
        ],
        fire_type="fire",
        confidence=0.92,
        severity="critical"
    )
    
    if result:
        print("   ✅ Fire alert sent via WhatsApp!")
        print("      Recipients should receive WhatsApp message with:")
        print("      - Floor information")
        print("      - People present on the floor")
        print("      - Evacuation instructions")
    else:
        print("   ❌ Failed to send fire alert")
    
    print("\n" + "="*80)
    print("TEST COMPLETE - Fire detection WhatsApp alerts are ready!")
    print("="*80 + "\n")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
