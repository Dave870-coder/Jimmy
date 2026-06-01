"""FastAPI application with incremental feature restoration."""

import logging
from datetime import datetime
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track initialization status
init_status = {
    "fastapi": False,
    "database": False,
    "config": False,
}

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    init_status["fastapi"] = True
    
    # Try to initialize config and database
    try:
        from src.config import get_settings
        settings = get_settings()
        init_status["config"] = True
        logger.info(f"✅ Config loaded: {settings.app_env}")
    except Exception as e:
        logger.warning(f"⚠️ Config init failed: {e}")
    
    # Initialize database (best effort)
    db_ready = False
    try:
        from src.database import engine, Base
        init_status["database"] = True
        logger.info("✅ Database engine initialized")
        db_ready = True
    except Exception as e:
        logger.warning(f"⚠️ Database init failed: {e}")
    
    # Define lifespan for startup/shutdown
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        try:
            logger.info("=" * 60)
            logger.info("🚀 APPLICATION STARTING UP")
            logger.info("=" * 60)
            
            if db_ready:
                try:
                    from src.database import engine, Base
                    async with engine.begin() as conn:
                        await conn.run_sync(Base.metadata.create_all)
                    logger.info("✅ Database tables created/verified")
                except Exception as e:
                    logger.warning(f"⚠️ Database table creation failed: {e}")
            
            logger.info("🎉 APPLICATION READY")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"❌ Startup error (but continuing): {e}")
        
        yield
        
        # Shutdown
        try:
            logger.info("🛑 APPLICATION SHUTTING DOWN")
            if db_ready:
                from src.database import engine
                await engine.dispose()
                logger.info("✅ Database cleanup completed")
        except Exception as e:
            logger.error(f"❌ Shutdown error: {e}")
    
    app = FastAPI(
        title="AI Bot Platform",
        version="1.0.0",
        lifespan=lifespan,
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
            "database": "ready" if db_ready else "not_initialized",
        }
    
    @app.get("/health")
    async def health():
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "ready" if db_ready else "not_initialized",
        }
    
    @app.get("/ready")
    async def ready():
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_ready,
        }
    
    @app.get("/init-status")
    async def init_status_endpoint():
        """Debug endpoint showing initialization status."""
        return {
            "fastapi": init_status["fastapi"],
            "database": init_status["database"],
            "config": init_status["config"],
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    logger.info("✅ App created successfully")

except Exception as e:
    logger.error(f"❌ Failed to create app: {e}", exc_info=True)
    raise
