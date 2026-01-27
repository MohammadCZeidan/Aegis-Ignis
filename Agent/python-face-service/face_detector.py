"""
Face detector initialization and management.
"""
import logging
from config import ServiceConfig

logger = logging.getLogger(__name__)

face_detector = None
INSIGHTFACE_AVAILABLE = False

try:
    import insightface
    logger.info("Loading InsightFace...")
    face_detector = insightface.app.FaceAnalysis(
        name='buffalo_l',
        providers=['CPUExecutionProvider']
    )
    face_detector.prepare(ctx_id=-1, det_size=ServiceConfig.DETECTION_SIZE)
    INSIGHTFACE_AVAILABLE = True
    logger.info(f"InsightFace loaded (detection size: {ServiceConfig.DETECTION_SIZE})")
except Exception as e:
    logger.error(f"InsightFace initialization failed: {e}")
    INSIGHTFACE_AVAILABLE = False
