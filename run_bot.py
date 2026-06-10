#!/usr/bin/env python3
"""
Production bot entry point with comprehensive error handling.
Designed to run seamlessly online without crashing on Render.
"""

import sys
import os
import logging
from pathlib import Path

# Ensure we're in the right directory
project_root = Path(__file__).parent
os.chdir(project_root)

# Add project to path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Setup logging immediately
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("=" * 70)
logger.info("🚀 STARTING PRODUCTION BOT FOR RENDER")
logger.info("=" * 70)


def create_app():
    """Create and configure FastAPI app with error handling."""
    try:
        from src.main import app
        logger.info("✅ FastAPI app created successfully")
        return app
    except Exception as e:
        logger.error(f"❌ Failed to create app: {e}")
        logger.error("Attempting to start minimal app...")
        import traceback
        logger.error(traceback.format_exc())
        
        # Minimal fallback app
        from fastapi import FastAPI
        from datetime import datetime
        
        fallback_app = FastAPI(title="AI Bot (Degraded Mode)")
        
        @fallback_app.get("/")
        async def root():
            return {
                "status": "error", 
                "message": "App initialization failed",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        @fallback_app.get("/health")
        async def health():
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        logger.warning("⚠️  Running in degraded mode")
        return fallback_app


def main():
    """Main entry point."""
    try:
        logger.info("📦 Loading configuration...")
        from src.config import get_settings
        settings = get_settings()
        
        # Get port and workers from environment (Render sets these)
        port = int(os.getenv('PORT', settings.api_port))
        # Render free tier: use 1 worker to avoid memory issues
        workers = int(os.getenv('WEB_CONCURRENCY', '1'))
        
        logger.info(f"Environment: {settings.app_env}")
        logger.info(f"Debug: {settings.debug}")
        logger.info(f"Port: {port}")
        logger.info(f"Workers: {workers}")
        logger.info(f"Database URL: {settings.database_url[:50]}...")
        
        logger.info("🔧 Creating FastAPI application...")
        app = create_app()
        
        logger.info("=" * 70)
        logger.info("✅ BOT READY - Starting uvicorn server")
        logger.info("=" * 70)
        logger.info(f"🌐 Listening on {settings.api_host}:{port}")
        logger.info(f"📚 API Docs: http://{settings.api_host}:{port}/docs")
        logger.info("=" * 70)
        
        # Start uvicorn server with minimal dependencies for Render
        # Don't use uvloop or httptools - stick with default async implementation
        import uvicorn
        
        uvicorn.run(
            app,
            host=settings.api_host,
            port=port,
            workers=workers,
            loop="asyncio",
            log_level=settings.log_level.lower() if hasattr(settings, 'log_level') else "info",
        )
        
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        logger.error("Bot failed to start")
        sys.exit(1)


if __name__ == "__main__":
    main()
