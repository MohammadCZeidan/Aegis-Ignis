"""
Configuration management for Fire Detection Service
Loads and validates environment variables
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(PROJECT_ROOT, "env", ".env")
load_dotenv(dotenv_path=ENV_PATH if os.path.exists(ENV_PATH) else None)


class Config:
    """Centralized configuration for Fire Detection Service"""
    
    # Service Configuration
    PORT: int = int(os.getenv('PORT', '8002'))
    BACKEND_API_URL: str = os.getenv('BACKEND_API_URL', 'http://localhost:8000/api/v1')
    
    # ML Detection Configuration
    ML_MODEL_PATH: str = os.getenv('ML_MODEL_PATH', '../ml_models/weights/fire_detection.pt')
    CONFIDENCE_THRESHOLD: float = float(os.getenv('CONFIDENCE_THRESHOLD', '0.5'))
    USE_ML_DETECTION: bool = os.getenv('USE_ML_DETECTION', 'true').lower() == 'true'
    USE_COLOR_FALLBACK: bool = os.getenv('USE_COLOR_FALLBACK', 'true').lower() == 'true'
    
    # Legacy thresholds for color-based detection
    CONFIDENCE_THRESHOLD_WARNING: float = 0.08
    CONFIDENCE_THRESHOLD_ALERT: float = 0.20
    
    # N8N Webhook Configuration
    N8N_WEBHOOK_URL: Optional[str] = os.getenv('N8N_WEBHOOK_URL') or os.getenv('N8N_WEBHOOK_URL')
    N8N_PRESENCE_WEBHOOK_URL: Optional[str] = os.getenv('N8N_PRESENCE_WEBHOOK_URL')
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_FROM: Optional[str] = os.getenv('TWILIO_WHATSAPP_FROM')
    TWILIO_WHATSAPP_TO: Optional[str] = os.getenv('TWILIO_WHATSAPP_TO')
    
    @classmethod
    def is_n8n_configured(cls) -> bool:
        """Check if N8N webhook is configured"""
        return cls.N8N_WEBHOOK_URL is not None and cls.N8N_WEBHOOK_URL.strip() != ''
    
    @classmethod
    def validate(cls) -> dict:
        """Validate configuration and return status"""
        status = {
            'n8n_configured': cls.is_n8n_configured(),
            'n8n_url': cls.N8N_WEBHOOK_URL if cls.is_n8n_configured() else None,
            'twilio_configured': bool(cls.TWILIO_ACCOUNT_SID and cls.TWILIO_AUTH_TOKEN),
            'backend_url': cls.BACKEND_API_URL,
            'ml_enabled': cls.USE_ML_DETECTION,
            'color_fallback': cls.USE_COLOR_FALLBACK
        }
        return status
