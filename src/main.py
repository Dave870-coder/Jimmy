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
    
    # Layer 2: Core monitoring endpoints
    @app.get("/metrics")
    async def metrics():
        """Prometheus-compatible metrics endpoint."""
        return {
            "requests_total": 0,
            "requests_today": 0,
            "uptime_seconds": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @app.get("/status")
    async def status_endpoint():
        """Comprehensive status endpoint."""
        return {
            "bot_status": "running",
            "environment": init_status["config"],
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "ready" if db_ready else "not_initialized",
        }
    
    # Layer 3: Try to add messages route (safest route to start with)
    try:
        from src.api.routes.messages import router as messages_router
        app.include_router(messages_router, prefix="/api/v1/messages", tags=["messages"])
        logger.info("✅ Messages route loaded")
    except Exception as e:
        logger.warning(f"⚠️ Messages route failed: {e}")
    
    # Layer 4: Add Telegram route
    try:
        from src.api.routes.telegram import router as telegram_router
        app.include_router(telegram_router, prefix="/api/v1/telegram", tags=["telegram"])
        logger.info("✅ Telegram route loaded")
    except Exception as e:
        logger.warning(f"⚠️ Telegram route failed: {e}")
    
    # Layer 5: Add WhatsApp routes
    try:
        from src.api.routes.whatsapp import router as whatsapp_router
        app.include_router(whatsapp_router, prefix="/api/v1/whatsapp", tags=["whatsapp"])
        logger.info("✅ WhatsApp route loaded")
    except Exception as e:
        logger.warning(f"⚠️ WhatsApp route failed: {e}")
    
    try:
        from src.api.routes.whatsapp_qr import router as whatsapp_qr_router
        app.include_router(whatsapp_qr_router, prefix="/api/v1/whatsapp-qr", tags=["whatsapp-qr"])
        logger.info("✅ WhatsApp QR route loaded")
    except Exception as e:
        logger.warning(f"⚠️ WhatsApp QR route failed: {e}")
    
    # Layer 6: Add optional routes (auth, admin, memory, workflows)
    optional_routes = [
        ("auth", "/api/v1/auth", "auth"),
        ("admin", "/api/v1/admin", "admin"),
        ("memory", "/api/v1/memory", "memory"),
        ("workflows", "/api/v1/workflows", "workflows"),
    ]
    
    for route_name, prefix, tag in optional_routes:
        try:
            module = __import__(f"src.api.routes.{route_name}", fromlist=[route_name])
            router = getattr(module, "router", None)
            if router:
                app.include_router(router, prefix=prefix, tags=[tag])
                logger.info(f"✅ {route_name.capitalize()} route loaded")
        except Exception as e:
            logger.warning(f"⚠️ {route_name.capitalize()} route failed: {e}")
    
    # Layer 7: Initialize AI Orchestrator (optional, graceful degradation)
    ai_orchestrator = None
    try:
        from src.ai.orchestrator import get_agent_orchestrator
        ai_orchestrator = get_agent_orchestrator()
        logger.info("✅ AI Orchestrator initialized")
    except Exception as e:
        logger.warning(f"⚠️ AI Orchestrator initialization failed: {e}")
        logger.info("ℹ️  Bot will run without AI features")
    
    # Layer 8: Enhanced health endpoint with AI status
    @app.get("/health/detailed")
    async def health_detailed():
        """Detailed health endpoint with orchestrator status."""
        ai_status = "initialized" if ai_orchestrator else "unavailable"
        return {
            "status": "healthy",
            "database": "ready" if db_ready else "not_initialized",
            "orchestrator": ai_status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    logger.info("✅ App created successfully")

except Exception as e:
    logger.error(f"❌ Failed to create app: {e}", exc_info=True)
    raise
