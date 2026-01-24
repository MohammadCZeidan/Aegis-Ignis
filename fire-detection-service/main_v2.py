"""
Advanced Fire Detection Service with ML Integration
- ML-based fire and smoke detection using YOLOv8
- Automatic fallback to color-based detection
- N8N webhook integration for WhatsApp/Voice alerts
- AI-powered emergency communication
"""
import logging
import uvicorn
import sys
import os
from fastapi import FastAPI

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from routes import register_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="ML Fire Detection Service", version="3.0.0")

# Register all routes
register_routes(app)

# Log startup information
logger.info("=" * 60)
logger.info("Fire Detection Service Starting...")
logger.info("=" * 60)
config_status = Config.validate()
logger.info(f"✓ ML Detection: {'Enabled' if config_status['ml_enabled'] else 'Disabled'}")
logger.info(f"✓ Color Fallback: {'Enabled' if config_status['color_fallback'] else 'Disabled'}")
logger.info(f"✓ N8N Integration: {'Enabled' if config_status['n8n_configured'] else 'Disabled'}")
if config_status['n8n_configured']:
    logger.info(f"  N8N Webhook URL: {config_status['n8n_url']}")
else:
    logger.warning("  ⚠ N8N_WEBHOOK_URL not configured - alerts will be disabled")
    logger.info("  To enable: Set N8N_WEBHOOK_URL in your .env file")
logger.info(f"✓ Twilio Integration: {'Enabled' if config_status['twilio_configured'] else 'Disabled'}")
logger.info(f"✓ Backend API: {config_status['backend_url']}")
logger.info("=" * 60)


if __name__ == "__main__":
    logger.info(f"Starting Fire Detection Service on port {Config.PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=Config.PORT)
