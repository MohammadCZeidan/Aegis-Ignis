"""
Alert Manager for fire and presence notifications via N8N and Twilio WhatsApp
Sends fire alerts to N8N webhook for WhatsApp and voice notifications
Direct Twilio WhatsApp integration for fire alerts
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(PROJECT_ROOT, "env", ".env")
load_dotenv(dotenv_path=ENV_PATH if os.path.exists(ENV_PATH) else None)

logger = logging.getLogger(__name__)

# Import Twilio (optional - only if credentials are set)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    logger.warning("Twilio not installed. Install with: pip install twilio")


class AlertManager:
    """Manages fire and presence alerts with N8N webhook integration"""
    
    def __init__(self, n8n_webhook_url: Optional[str] = None):
        """
        Initialize Alert Manager
        
        Args:
            n8n_webhook_url: N8N webhook URL for sending alerts
        """
        self.n8n_webhook_url = n8n_webhook_url or os.getenv('N8N_WEBHOOK_URL')
        self.backend_url = os.getenv('BACKEND_API_URL', 'http://localhost:8000/api/v1')
        
        # Twilio configuration (loaded from .env file - DO NOT HARDCODE)
        self.twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.twilio_from = os.getenv('TWILIO_WHATSAPP_FROM')
        self.twilio_to = os.getenv('TWILIO_WHATSAPP_TO')
        self.twilio_phone_from = os.getenv('TWILIO_PHONE_FROM')  # For voice calls
        self.twilio_phone_to = os.getenv('TWILIO_PHONE_TO')  # For voice calls
        
        # Initialize Twilio client
        self.twilio_client = None
        if TWILIO_AVAILABLE and self.twilio_sid and self.twilio_token:
            try:
                self.twilio_client = TwilioClient(self.twilio_sid, self.twilio_token)
                logger.info("✓ Twilio WhatsApp client initialized")
                if not self.twilio_from:
                    logger.warning("⚠ TWILIO_WHATSAPP_FROM not configured - WhatsApp messages will fail")
                elif not self.twilio_from.startswith('whatsapp:+'):
                    logger.warning(f"⚠ Invalid TWILIO_WHATSAPP_FROM format: {self.twilio_from}. Must start with 'whatsapp:+'")
                if not self.twilio_to:
                    logger.warning("⚠ TWILIO_WHATSAPP_TO not configured - WhatsApp messages will fail")
                elif not self.twilio_to.startswith('whatsapp:+'):
                    logger.warning(f"⚠ Invalid TWILIO_WHATSAPP_TO format: {self.twilio_to}. Must start with 'whatsapp:+'")
                if not self.twilio_phone_from:
                    logger.warning("⚠ TWILIO_PHONE_FROM not configured - Voice calls will fail")
                if not self.twilio_phone_to:
                    logger.warning("⚠ TWILIO_PHONE_TO not configured - Voice calls will fail")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
        else:
            if not TWILIO_AVAILABLE:
                logger.warning(" Twilio library not installed. Install with: pip install twilio")
            elif not self.twilio_sid:
                logger.warning(" TWILIO_ACCOUNT_SID not configured - WhatsApp alerts will be disabled")
            elif not self.twilio_token:
                logger.warning("⚠ TWILIO_AUTH_TOKEN not configured - WhatsApp alerts will be disabled")
            logger.info("To enable Twilio WhatsApp alerts, set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, and TWILIO_WHATSAPP_TO in your .env file")
            logger.info("To enable Twilio Voice calls, also set TWILIO_PHONE_FROM and TWILIO_PHONE_TO in your .env file")
        
        if not self.n8n_webhook_url:
            logger.warning("N8N_WEBHOOK_URL not configured. N8N alerts will be disabled.")
            logger.info("To enable N8N alerts, set N8N_WEBHOOK_URL in your .env file")
            logger.info("Example: N8N_WEBHOOK_URL=http://localhost:5678/webhook/fire-alert")
        else:
            logger.info(f"✓ N8N webhook configured: {self.n8n_webhook_url}")
    
    def send_fire_alert(
        self, 
        floor_id: int,
        camera_id: int,
        camera_name: str,
        room: str,
        people_detected: List[Dict],
        fire_type: str = 'fire',
        confidence: float = 0.0,
        severity: str = 'critical',
        screenshot_path: Optional[str] = None
    ) -> bool:
        """
        Send fire alert with people count to N8N for WhatsApp/Voice notifications
        
        Args:
            floor_id: Floor number where fire was detected
            camera_id: Camera ID that detected the fire
            camera_name: Human-readable camera name
            room: Room location
            people_detected: List of people currently on the floor
            fire_type: Type of fire detected ('fire' or 'smoke')
            confidence: ML model confidence score (0-1)
            severity: Alert severity ('warning', 'critical')
            screenshot_path: Path to fire screenshot
            
        Returns:
            True if alert was sent successfully
        """
        people_count = len(people_detected)
        
        # Create alert message
        fire_emoji = "" if fire_type == "fire" else "[SMOKE]"
        message = (
            f"{fire_emoji} FIRE ALERT - Floor {floor_id}\n"
            f"Location: {room}\n"
            f"Camera: {camera_name}\n"
            f"Type: {fire_type.upper()}\n"
            f"Severity: {severity.upper()}\n"
            f"Confidence: {confidence*100:.1f}%\n"
            f" People on floor: {people_count}\n"
            f" Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        if people_count > 0:
            message += f"\n\n EVACUATION REQUIRED - {people_count} people present!"
        
        # Prepare alert payload for N8N
        alert_data = {
            "alert_type": "FIRE_EMERGENCY",
            "floor_id": floor_id,
            "camera_id": camera_id,
            "camera_name": camera_name,
            "room": room,
            "fire_type": fire_type,
            "severity": severity,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "people_count": people_count,
            "people_details": people_detected,
            "message": message,
            "priority": "CRITICAL" if severity == "critical" else "HIGH",
            "screenshot_path": screenshot_path,
            "requires_evacuation": people_count > 0,
            "action_required": True
        }
        
        # Send to N8N webhook
        n8n_success = self._send_to_n8n(alert_data)
        
        # Send via Twilio WhatsApp
        logger.info(f"Attempting to send WhatsApp alert for Floor {floor_id}")
        whatsapp_success = self._send_whatsapp_alert(
            floor_id=floor_id,
            room=room,
            fire_type=fire_type,
            confidence=confidence,
            people_count=people_count,
            severity=severity
        )
        if whatsapp_success:
                logger.info(f"WhatsApp alert sent successfully for Floor {floor_id}")
        
        # Send voice call for critical alerts or when people are present
        voice_success = False
        if severity == "critical" or people_count > 0:
            logger.info(f"Attempting to send voice call alert for Floor {floor_id}")
            voice_success = self._send_voice_call_alert(
                floor_id=floor_id,
                room=room,
                fire_type=fire_type,
                confidence=confidence,
                people_count=people_count,
                severity=severity
            )
            if voice_success:
                logger.info(f"Voice call alert sent successfully for Floor {floor_id}")
        
        # Also log to backend (existing system)
        backend_success = self._log_to_backend(alert_data)
        
        return n8n_success or whatsapp_success or voice_success or backend_success
    
    def send_presence_update(
        self, 
        floor_id: int, 
        people_count: int,
        people_details: Optional[List[Dict]] = None
    ) -> bool:
        """
        Send regular presence update (non-emergency)
        
        Args:
            floor_id: Floor number
            people_count: Number of people currently present
            people_details: Optional list of identified people
            
        Returns:
            True if update was sent successfully
        """
        message = (
            f"Floor {floor_id} Occupancy Update\n"
            f"Current occupancy: {people_count} people\n"
            f"Time: {datetime.now().strftime('%H:%M:%S')}"
        )
        
        alert_data = {
            "alert_type": "PRESENCE_UPDATE",
            "floor_id": floor_id,
            "timestamp": datetime.now().isoformat(),
            "people_count": people_count,
            "people_details": people_details or [],
            "message": message,
            "priority": "LOW"
        }
        
        return self._send_to_n8n(alert_data)
    
    def send_critical_evacuation_alert(
        self,
        floor_id: int,
        camera_id: int,
        people_count: int,
        fire_confidence: float
    ) -> bool:
        """
        Send CRITICAL alert for fire + people combination
        This triggers immediate WhatsApp + Voice Call in N8N
        
        Args:
            floor_id: Floor with fire
            camera_id: Camera ID
            people_count: Number of people needing evacuation
            fire_confidence: Fire detection confidence
            
        Returns:
            True if sent successfully
        """
        message = (
            f" CRITICAL EMERGENCY - Floor {floor_id}\n"
            f" ACTIVE FIRE DETECTED ({fire_confidence*100:.0f}% confidence)\n"
            f" {people_count} PEOPLE NEED EVACUATION\n"
            f" IMMEDIATE ACTION REQUIRED!\n"
            f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        alert_data = {
            "alert_type": "CRITICAL_EVACUATION",
            "floor_id": floor_id,
            "camera_id": camera_id,
            "timestamp": datetime.now().isoformat(),
            "people_count": people_count,
            "fire_confidence": fire_confidence,
            "message": message,
            "priority": "EMERGENCY",
            "trigger_voice_call": True,  # Signal N8N to make voice call
            "trigger_whatsapp": True,
            "trigger_sms": True
        }
        
        n8n_success = self._send_to_n8n(alert_data)
        
        # Also send direct Twilio voice call
        voice_success = self._send_voice_call_alert(
            floor_id=floor_id,
            room=f"Floor {floor_id}",
            fire_type="fire",
            confidence=fire_confidence,
            people_count=people_count,
            severity="critical"
        )
        
        return n8n_success or voice_success
    
    def _send_whatsapp_alert(
        self,
        floor_id: int,
        room: str,
        fire_type: str,
        confidence: float,
        people_count: int,
        severity: str
    ) -> bool:
        """
        Send fire alert via Twilio WhatsApp
        
        Args:
            floor_id: Floor number
            room: Room location
            fire_type: Type of fire (fire/smoke)
            confidence: Detection confidence (0-1)
            people_count: Number of people on floor
            severity: Alert severity
            
        Returns:
            True if sent successfully
        """
        if not self.twilio_client:
            logger.warning("Twilio client not initialized - skipping WhatsApp alert")
            return False
        
        if not self.twilio_from:
            logger.error("TWILIO_WHATSAPP_FROM not configured - cannot send WhatsApp message")
            return False
        
        if not self.twilio_to:
            logger.error("TWILIO_WHATSAPP_TO not configured - cannot send WhatsApp message")
            return False
        
        # Validate phone number formats
        if not self.twilio_from.startswith('whatsapp:+'):
            logger.error(f"Invalid TWILIO_WHATSAPP_FROM format: {self.twilio_from}. Must start with 'whatsapp:+'")
            return False
        
        if not self.twilio_to.startswith('whatsapp:+'):
            logger.error(f"Invalid TWILIO_WHATSAPP_TO format: {self.twilio_to}. Must start with 'whatsapp:+'")
            return False
        
        try:
            # Format current time
            current_time = datetime.now().strftime('%I:%M %p')
            current_date = datetime.now().strftime('%m/%d/%Y')
            
            # Create alert message
            fire_emoji = "" if fire_type == "fire" else "[SMOKE]"
            message_body = (
                f"{fire_emoji} *FIRE EMERGENCY ALERT*\n\n"
                f" *Location:* Floor {floor_id} - {room}\n"
                f" *Type:* {fire_type.upper()}\n"
                f" *Severity:* {severity.upper()}\n"
                f" *Confidence:* {confidence*100:.0f}%\n"
                f" *People Present:* {people_count}\n"
                f" *Date:* {current_date}\n"
                f" *Time:* {current_time}\n\n"
            )
            
            if people_count > 0:
                message_body += f" *URGENT: {people_count} people need evacuation!*\n\n"
            
            message_body += "*Immediate action required!*"
            
            # Send WhatsApp message
            logger.info(f"Sending WhatsApp message from {self.twilio_from} to {self.twilio_to}")
            message = self.twilio_client.messages.create(
                from_=self.twilio_from,
                to=self.twilio_to,
                body=message_body
            )
            
            # Check message status - Twilio returns immediately but message might fail
            message_status = message.status
            logger.info(f"Twilio message created - SID: {message.sid}, Status: {message_status}")
            
            # Check for immediate failure statuses
            if message_status in ['failed', 'undelivered', 'canceled']:
                logger.error(f"✗ WhatsApp message failed with status: {message_status}")
                if hasattr(message, 'error_code') and message.error_code:
                    logger.error(f"Error code: {message.error_code}, Error message: {message.error_message}")
                return False
            
            # Status might be 'queued', 'sending', or 'sent' - all are acceptable initially
            if message_status in ['queued', 'sending', 'sent']:
                logger.info(f"✓ WhatsApp alert sent successfully - SID: {message.sid}, Status: {message_status}")
                
                # Log important note about WhatsApp delivery
                if message_status == 'queued':
                    logger.info("ℹ Message is queued. Delivery depends on recipient's WhatsApp opt-in status.")
                    logger.info("ℹ If recipient hasn't sent you a message first, WhatsApp may not deliver the message.")
                
                return True
            else:
                logger.warning(f"⚠ WhatsApp message in unknown status: {message_status} - SID: {message.sid}")
                # Still return True as message was created, but log warning
                return True
            
        except Exception as e:
            logger.error(f"✗ Failed to send WhatsApp alert: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Check for common Twilio errors
            error_str = str(e).lower()
            if 'not a valid' in error_str or 'invalid' in error_str:
                logger.error(" Invalid phone number format. Check TWILIO_WHATSAPP_FROM and TWILIO_WHATSAPP_TO")
                logger.error(" WhatsApp numbers must be in format: whatsapp:+1234567890")
            elif 'authentication' in error_str or 'credentials' in error_str:
                logger.error(" Twilio authentication failed. Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN")
            elif 'whatsapp' in error_str or 'not approved' in error_str:
                logger.error(" WhatsApp-specific error. Ensure:")
                logger.error("   1. Your Twilio account has WhatsApp enabled")
                logger.error("   2. Your WhatsApp number is approved in Twilio console")
                logger.error("   3. The recipient has sent you a message first (WhatsApp opt-in required)")
            elif 'permission' in error_str or 'unauthorized' in error_str:
                logger.error(" Permission denied. Check Twilio account permissions and WhatsApp approval status.")
            
            return False
    
    def _send_voice_call_alert(
        self,
        floor_id: int,
        room: str,
        fire_type: str,
        confidence: float,
        people_count: int,
        severity: str
    ) -> bool:
        """
        Send fire alert via Twilio voice call
        
        Args:
            floor_id: Floor number
            room: Room location
            fire_type: Type of fire (fire/smoke)
            confidence: Detection confidence (0-1)
            people_count: Number of people on floor
            severity: Alert severity
            
        Returns:
            True if sent successfully
        """
        if not self.twilio_client:
            logger.warning("Twilio client not initialized - skipping voice call")
            return False
        
        if not self.twilio_phone_from:
            logger.warning("TWILIO_PHONE_FROM not configured - cannot make voice call")
            return False
        
        if not self.twilio_phone_to:
            logger.warning("TWILIO_PHONE_TO not configured - cannot make voice call")
            return False
        
        try:
            from twilio.twiml.voice_response import VoiceResponse
            
            # Create TwiML for voice message
            response = VoiceResponse()
            
            # Build the message
            message_text = (
                f"Emergency alert! Fire detected on floor {floor_id}, {room}. "
                f"Type: {fire_type.upper()}. "
                f"Confidence: {confidence*100:.0f} percent. "
            )
            
            if people_count > 0:
                message_text += f"URGENT: {people_count} people need evacuation! "
            
            message_text += "Please evacuate immediately and call 911."
            
            response.say(message_text, voice='alice', language='en-US')
            
            # Make the call
            logger.info(f"Making voice call from {self.twilio_phone_from} to {self.twilio_phone_to}")
            call = self.twilio_client.calls.create(
                twiml=str(response),
                to=self.twilio_phone_to,
                from_=self.twilio_phone_from
            )
            
            logger.info(f"✓ Voice call initiated successfully - Call SID: {call.sid}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to make voice call: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def _send_to_n8n(self, alert_data: Dict) -> bool:
        """
        Send alert data to N8N webhook
        
        Args:
            alert_data: Alert payload
            
        Returns:
            True if successful
        """
        if not self.n8n_webhook_url:
            logger.warning("N8N webhook not configured, skipping N8N alert")
            return False
        
        try:
            response = requests.post(
                self.n8n_webhook_url,
                json=alert_data,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"N8N alert sent successfully: {alert_data['alert_type']}")
                return True
            else:
                logger.error(f"N8N alert failed: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("N8N webhook timeout - request took too long")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("N8N webhook connection error - is N8N running?")
            return False
        except Exception as e:
            logger.error(f"N8N alert error: {e}")
            return False
    
    def _log_to_backend(self, alert_data: Dict) -> bool:
        """
        Log alert to Laravel backend (existing system)
        
        Args:
            alert_data: Alert data
            
        Returns:
            True if successful
        """
        try:
            # Send to existing Laravel fire alert endpoint
            endpoint = f"{self.backend_url}/alerts/fire"
            
            payload = {
                "camera_id": alert_data.get("camera_id"),
                "camera_name": alert_data.get("camera_name", "Unknown"),
                "floor_id": alert_data.get("floor_id"),
                "room": alert_data.get("room", "Unknown"),
                "event_type": "fire",
                "severity": alert_data.get("severity", "critical"),
                "confidence": alert_data.get("confidence", 0.0) * 100,
                "fire_type": alert_data.get("fire_type", "fire"),
                "screenshot_path": alert_data.get("screenshot_path"),
                "detected_at": alert_data.get("timestamp")
            }
            
            response = requests.post(endpoint, json=payload, timeout=5)
            
            if response.status_code in [200, 201]:
                logger.info(" Alert logged to backend")
                return True
            else:
                logger.warning(f"Backend logging failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Backend logging error: {e}")
            return False
    
    def get_floor_occupancy(self, floor_id: int) -> Dict:
        """
        Get current occupancy for a floor from backend
        
        Args:
            floor_id: Floor ID
            
        Returns:
            Dict with people_count and people_details
        """
        try:
            endpoint = f"{self.backend_url}/presence/floor-live/{floor_id}"
            response = requests.get(endpoint, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "people_count": data.get("current_count", 0),
                    "people_details": data.get("current_people", [])
                }
        except Exception as e:
            logger.error(f"Error fetching floor occupancy: {e}")
        
        return {"people_count": 0, "people_details": []}
