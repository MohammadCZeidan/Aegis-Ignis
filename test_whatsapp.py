"""
Test script to verify WhatsApp alerts are working
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("WHATSAPP ALERT TEST SCRIPT")
print("="*80)
print()

# Check environment variables
print("1. Checking environment variables...")
twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_from = os.getenv('TWILIO_WHATSAPP_FROM')
twilio_to = os.getenv('TWILIO_WHATSAPP_TO')

print(f"   TWILIO_ACCOUNT_SID: {'✅ SET' if twilio_sid else '❌ NOT SET'}")
print(f"   TWILIO_AUTH_TOKEN: {'✅ SET' if twilio_token else '❌ NOT SET'}")
print(f"   TWILIO_WHATSAPP_FROM: {twilio_from}")
print(f"   TWILIO_WHATSAPP_TO: {twilio_to}")
print()

# Check if Twilio is installed
print("2. Checking Twilio installation...")
try:
    from twilio.rest import Client as TwilioClient
    print("   ✅ Twilio library is installed")
    twilio_available = True
except ImportError as e:
    print(f"   ❌ Twilio not installed: {e}")
    print("   Installing Twilio...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "twilio"])
    from twilio.rest import Client as TwilioClient
    twilio_available = True
    print("   ✅ Twilio installed successfully")
print()

# Test AlertManager initialization
print("3. Testing AlertManager initialization...")
try:
    from services.alert_manager import AlertManager
    
    alert_manager = AlertManager()
    
    if alert_manager.twilio_client:
        print("   ✅ Twilio client initialized")
    else:
        print("   ❌ Twilio client NOT initialized")
        if not twilio_sid or not twilio_token:
            print("      Reason: Missing TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN")
    print()
    
    # Test sending a fire alert
    print("4. Testing fire alert...")
    try:
        result = alert_manager.send_fire_alert(
            floor_id=3,
            camera_id=1,
            camera_name="Test Camera",
            room="Test Room",
            people_detected=[
                {"name": "John Doe", "employee_number": "EMP001", "department": "IT"},
                {"name": "Jane Smith", "employee_number": "EMP002", "department": "HR"}
            ],
            fire_type="fire",
            confidence=0.85,
            severity="critical"
        )
        
        if result:
            print("   ✅ Fire alert sent successfully!")
            print("      Check your WhatsApp for the message")
        else:
            print("   ❌ Fire alert failed")
        print()
    except Exception as e:
        print(f"   ❌ Error sending fire alert: {e}")
        import traceback
        traceback.print_exc()
        print()
    
    # Test sending a presence update
    print("5. Testing presence update alert...")
    try:
        result = alert_manager.send_presence_update(
            floor_id=3,
            people_count=2,
            people_details=[
                {"name": "John Doe", "employee_number": "EMP001", "department": "IT"},
                {"name": "Jane Smith", "employee_number": "EMP002", "department": "HR"}
            ]
        )
        
        if result:
            print("   ✅ Presence alert sent successfully!")
            print("      Check your WhatsApp for the message")
        else:
            print("   ⚠️ Presence alert may not have been sent")
            print("      (This is normal if N8N webhook is not configured)")
        print()
    except Exception as e:
        print(f"   ❌ Error sending presence alert: {e}")
        import traceback
        traceback.print_exc()
        print()
    
except Exception as e:
    print(f"   ❌ Error initializing AlertManager: {e}")
    import traceback
    traceback.print_exc()
    print()

print("="*80)
print("TEST COMPLETE")
print("="*80)
print()
print("If you didn't receive WhatsApp messages:")
print("1. Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are correct")
print("2. Make sure Twilio is configured in your account")
print("3. Check the Twilio WhatsApp phone numbers are valid")
print("4. Ensure the phone number receiving alerts (+905317093987) is registered with Twilio")
print()
