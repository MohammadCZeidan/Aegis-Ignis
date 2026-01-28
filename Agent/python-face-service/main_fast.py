"""
Face Recognition Service - Main Entry Point
Provides face detection, identification, and duplicate checking using InsightFace.
Uses cached employee embeddings for efficient similarity comparisons.
"""
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

import logging
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import ServiceConfig
from cache import ThreadSafeCache
from face_detector import INSIGHTFACE_AVAILABLE
from cache_service import refresh_employee_cache
from endpoints import register_endpoints

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Face Recognition Service", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global thread-safe cache
cache = ThreadSafeCache()

# Register all endpoints
register_endpoints(app, cache)


@app.on_event("startup")
async def startup_event():
    """Load employee cache on service startup."""
    logger.info("Face Recognition Service starting...")
    logger.info("Loading employee cache...")
    await asyncio.to_thread(refresh_employee_cache, cache)
    logger.info("Cache loaded - Service ready")


if __name__ == "__main__":
    import uvicorn
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("0.0.0.0", 8001))
        sock.close()
        logger.info("Port 8001 is available")
    except OSError:
        logger.warning("Port 8001 already in use, will attempt to reuse...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="warning",
        access_log=False,
        server_header=False,
        limit_concurrency=50,
        timeout_keep_alive=5
    )
