"""
Test Twilio WhatsApp Integration
Quick test to verify Twilio credentials and send a test message
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Import Twilio
try:
    from twilio.rest import Client
    print("✅ Twilio library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Twilio: {e}")
    print("Install with: pip install twilio")
    exit(1)

# Get credentials from .env
TWILIO_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_WHATSAPP_FROM')
TWILIO_TO = os.getenv('TWILIO_WHATSAPP_TO')

if not all([TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM, TWILIO_TO]):
    print("❌ Missing Twilio credentials in .env file!")
    print("Please add the following to your .env file:")
    print("  TWILIO_ACCOUNT_SID=your_account_sid")
    print("  TWILIO_AUTH_TOKEN=your_auth_token")
    print("  TWILIO_WHATSAPP_FROM=whatsapp:+14155238886")
    print("  TWILIO_WHATSAPP_TO=whatsapp:+905317093987")
    exit(1)

print("\n" + "="*80)
print("TESTING TWILIO WHATSAPP INTEGRATION")
print("="*80)
print(f"Account SID: {TWILIO_SID}")
print(f"From Number: {TWILIO_FROM}")
print(f"To Number: {TWILIO_TO}")
print("="*80 + "\n")

# Initialize Twilio client
try:
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    print("✅ Twilio client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Twilio client: {e}")
    exit(1)

# Send test message
try:
    print("\n📱 Sending test WhatsApp message...")
    
    message = client.messages.create(
        from_=TWILIO_FROM,
        to=TWILIO_TO,
        body="🔥 *TEST ALERT* 🔥\n\n"
             "This is a test message from Aegis-Ignis Fire Detection System.\n\n"
             "📍 Floor 1 - Office\n"
             "⏰ Test Time: 02:30 PM\n"
             "✅ WhatsApp integration is working!"
    )
    
    print(f"✅ Message sent successfully!")
    print(f"   Message SID: {message.sid}")
    print(f"   Status: {message.status}")
    print(f"   To: {message.to}")
    print(f"   From: {message.from_}")
    print("\n" + "="*80)
    print("SUCCESS! Check your WhatsApp for the test message.")
    print("="*80)
    
except Exception as e:
    print(f"❌ Failed to send message: {e}")
    print("\nPossible issues:")
    print("1. Invalid Twilio credentials")
    print("2. Twilio account not active")
    print("3. WhatsApp sandbox not configured")
    print("4. Phone number not verified in Twilio")
    exit(1)
