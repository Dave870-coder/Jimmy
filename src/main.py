"""Minimal FastAPI application - bulletproof startup."""

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="AI Bot Platform",
        version="1.0.0",
    )
    
    # Add CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        return {
            "status": "running",
            "message": "AI Bot Platform API",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @app.get("/ready")
    async def ready():
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    logger.info("✅ Minimal app created successfully")

except Exception as e:
    logger.error(f"❌ Failed to create app: {e}", exc_info=True)
    raise
