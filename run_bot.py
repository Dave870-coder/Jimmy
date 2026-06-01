#!/usr/bin/env python3
"""
Production bot entry point with comprehensive error handling.
Designed to run seamlessly online without crashing.
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
logger.info("🚀 STARTING PRODUCTION BOT")
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
        
        # Minimal fallback app
        from fastapi import FastAPI
        
        fallback_app = FastAPI(title="AI Bot (Degraded Mode)")
        
        @fallback_app.get("/")
        async def root():
            return {"status": "error", "message": "App initialization failed"}
        
        @fallback_app.get("/health")
        async def health():
            return {"status": "unhealthy"}
        
        logger.warning("⚠️  Running in degraded mode")
        return fallback_app


def main():
    """Main entry point."""
    try:
        logger.info("📦 Loading configuration...")
        from src.config import get_settings
        settings = get_settings()
        
        # Override port from environment if set (Railway/Heroku)
        port = int(os.getenv('PORT', settings.api_port))
        workers = int(os.getenv('WEB_CONCURRENCY', settings.workers))
        
        logger.info(f"Environment: {settings.app_env}")
        logger.info(f"Debug: {settings.debug}")
        logger.info(f"Port: {port}")
        logger.info(f"Workers: {workers}")
        
        logger.info("🔧 Creating FastAPI application...")
        app = create_app()
        
        logger.info("=" * 70)
        logger.info("✅ BOT READY")
        logger.info("=" * 70)
        logger.info(f"🌐 Listening on {settings.api_host}:{port}")
        logger.info(f"📚 API Docs: http://{settings.api_host}:{port}/docs")
        logger.info("=" * 70)
        
        # Start uvicorn server
        import uvicorn
        
        uvicorn.run(
            app,
            host=settings.api_host,
            port=port,
            log_level=settings.log_level.lower(),
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
