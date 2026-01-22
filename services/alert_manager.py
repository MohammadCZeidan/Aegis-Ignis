"""
Alert Manager for fire and presence notifications via N8N and Twilio WhatsApp
Sends fire alerts to N8N webhook for WhatsApp and voice notifications
Direct Twilio WhatsApp integration for instant fire alerts
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

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
        
        # Initialize Twilio client
        self.twilio_client = None
        if TWILIO_AVAILABLE and self.twilio_sid and self.twilio_token:
            try:
                self.twilio_client = TwilioClient(self.twilio_sid, self.twilio_token)
                logger.info(" Twilio WhatsApp client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio: {e}")
        
        if not self.n8n_webhook_url:
            logger.warning("N8N_WEBHOOK_URL not configured. N8N alerts will be disabled.")
    
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
        fire_emoji = "" if fire_type == "fire" else "💨"
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
        
        # Send via Twilio WhatsApp (instant notification)
        logger.info(f"📱 Attempting to send WhatsApp alert for Floor {floor_id}")
        whatsapp_success = self._send_whatsapp_alert(
            floor_id=floor_id,
            room=room,
            fire_type=fire_type,
            confidence=confidence,
            people_count=people_count,
            severity=severity
        )
        if whatsapp_success:
            logger.info(f" WhatsApp alert sent successfully for Floor {floor_id}")
        
        # Also log to backend (existing system)
        backend_success = self._log_to_backend(alert_data)
        
        return n8n_success or whatsapp_success or backend_success
    
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
        
        return self._send_to_n8n(alert_data)
    
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
            logger.debug("Twilio not configured, skipping WhatsApp alert")
            return False
        
        try:
            # Format current time
            current_time = datetime.now().strftime('%I:%M %p')
            current_date = datetime.now().strftime('%m/%d/%Y')
            
            # Create alert message
            fire_emoji = "" if fire_type == "fire" else "💨"
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
            message = self.twilio_client.messages.create(
                from_=self.twilio_from,
                to=self.twilio_to,
                body=message_body
            )
            
            logger.info(f" WhatsApp alert sent - SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f" Failed to send WhatsApp alert: {e}")
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
                logger.info(f" N8N alert sent successfully: {alert_data['alert_type']}")
                return True
            else:
                logger.error(f" N8N alert failed: {response.status_code} - {response.text}")
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
