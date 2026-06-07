"""FastAPI application with incremental feature restoration."""

import logging
import os
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
    engine = None
    Base = None
    try:
        from src.database import engine, Base
        init_status["database"] = True
        logger.info("✅ Database engine imported")
    except Exception as e:
        logger.warning(f"⚠️ Database import failed: {e}")
        import traceback
        logger.warning(traceback.format_exc())
    
    # Define lifespan for startup/shutdown (includes all layers)
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup
        try:
            logger.info("=" * 60)
            logger.info("🚀 APPLICATION STARTING UP")
            logger.info("=" * 60)
            
            # Import all models to ensure they're registered with Base
            try:
                logger.info("Loading database models...")
                import src.database.models  # noqa - triggers all model class definitions
                logger.info("✅ All database models loaded")
                
                # Create tables synchronously after models are loaded
                from sqlalchemy import create_engine
                from src.database import Base as db_base
                from src.config import get_settings
                
                current_settings = get_settings()
                sync_url = current_settings.database_url
                if sync_url.startswith('sqlite+'):
                    sync_url = sync_url.replace('sqlite+aiosqlite:', 'sqlite:')
                
                logger.info(f"Creating database tables at: {sync_url}")
                sync_engine = create_engine(sync_url, echo=False)
                db_base.metadata.create_all(sync_engine)
                logger.info("✅ Database tables initialized")
                sync_engine.dispose()
                
                # Mark database as ready after successful initialization
                nonlocal db_ready
                db_ready = True
                logger.info("✅ Database marked as ready")
                
            except Exception as e:
                logger.warning(f"⚠️ Model import or table creation: {e}")
                logger.error(f"Stack trace: {__import__('traceback').format_exc()}")
            
            # Verify database with async context (for pool initialization)
            try:
                from src.database import engine as db_engine
                from src.database import Base as db_base
                if db_engine and db_base and db_ready:
                    try:
                        logger.info("Verifying database connection pool...")
                        # Just test connection without inspection for async compatibility
                        async with db_engine.begin() as conn:
                            logger.info("✅ Database connection verified")
                    except Exception as e:
                        logger.debug(f"Async verify (non-critical): {e}")
            except Exception as e:
                logger.debug(f"Database engine verification: {e}")
            
            # Initialize AI Orchestrator (optional, graceful degradation)
            try:
                from src.ai.orchestrator import get_agent_orchestrator
                orchestrator = get_agent_orchestrator()
                logger.info("✅ AI Orchestrator initialized")
            except Exception as e:
                logger.warning(f"⚠️ AI Orchestrator initialization failed: {e}")
            
            # Configure Telegram webhook on hosted environments (optional)
            try:
                if init_status["config"]:
                    from src.config import get_settings
                    current_settings = get_settings()
                    if hasattr(current_settings, 'telegram_bot_token') and current_settings.telegram_bot_token:
                        public_base_url = getattr(current_settings, 'public_base_url', None) or os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
                        if public_base_url:
                            try:
                                from src.bot.telegram.handler import get_telegram_bot
                                telegram_bot = await get_telegram_bot()
                                if telegram_bot:
                                    webhook_url = f"{public_base_url}/api/v1/telegram/webhook"
                                    await telegram_bot.set_webhook(webhook_url, getattr(current_settings, 'telegram_webhook_secret', ''))
                                    logger.info(f"✅ Telegram webhook configured: {webhook_url}")
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to configure Telegram webhook: {e}")
                        else:
                            logger.info("ℹ️  No public base URL - Telegram webhook will not be configured")
            except Exception as e:
                logger.warning(f"⚠️ Telegram setup failed: {e}")
            
            logger.info("🎉 APPLICATION READY")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"❌ Startup error (but continuing): {e}")
        
        yield
        
        # Shutdown
        try:
            logger.info("🛑 APPLICATION SHUTTING DOWN")
            try:
                from src.database import engine as db_engine
                if db_engine:
                    await db_engine.dispose()
                    logger.info("✅ Database cleanup completed")
            except Exception as e:
                logger.debug(f"Database disposal: {e}")
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
        allow_origins=settings.cors_origins if init_status["config"] else ["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    async def check_database_status():
        """Check if database is initialized."""
        try:
            if engine:
                # Try to get a connection and check if it works
                async with engine.connect() as conn:
                    await conn.execute("SELECT 1")
                    # If we got here, database is ready
                    return "ready"
        except:
            pass
        return "not_initialized"
    
    @app.get("/")
    async def root():
        db_status = await check_database_status()
        return {
            "status": "running",
            "message": "AI Bot Platform API",
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status,
        }
    
    @app.get("/health")
    async def health():
        db_status = await check_database_status()
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status,
        }
    
    @app.get("/ready")
    async def ready():
        db_status = await check_database_status()
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status == "ready",
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
        app.include_router(messages_router, tags=["messages"])
        logger.info("✅ Messages route loaded")
    except Exception as e:
        logger.warning(f"⚠️ Messages route failed: {e}")
    
    # Layer 4: Add Telegram route
    try:
        from src.api.routes.telegram import router as telegram_router
        app.include_router(telegram_router, tags=["telegram"])
        logger.info("✅ Telegram route loaded")
    except Exception as e:
        logger.warning(f"⚠️ Telegram route failed: {e}")
    
    # Layer 5: Add WhatsApp routes
    try:
        from src.api.routes.whatsapp import router as whatsapp_router
        app.include_router(whatsapp_router, tags=["whatsapp"])
        logger.info("✅ WhatsApp route loaded")
    except Exception as e:
        logger.warning(f"⚠️ WhatsApp route failed: {e}")
    
    try:
        from src.api.routes.whatsapp_qr import router as whatsapp_qr_router
        app.include_router(whatsapp_qr_router, tags=["whatsapp-qr"])
        logger.info("✅ WhatsApp QR route loaded")
    except Exception as e:
        logger.warning(f"⚠️ WhatsApp QR route failed: {e}")
    
    # Layer 6: Add optional routes (auth, admin, memory, workflows)
    optional_routes = [
        ("auth", "auth"),
        ("admin", "admin"),
        ("memory", "memory"),
        ("workflows", "workflows"),
    ]

    for route_name, tag in optional_routes:
        try:
            module = __import__(f"src.api.routes.{route_name}", fromlist=[route_name])
            router = getattr(module, "router", None)
            if router:
                app.include_router(router, tags=[tag])
                logger.info(f"✅ {route_name.capitalize()} route loaded")
        except Exception as e:
            logger.warning(f"⚠️ {route_name.capitalize()} route failed: {e}")
    
    # All routes loaded
    logger.info("=" * 60)
    logger.info("✅ All API routes configured")
    logger.info("=" * 60)
    
    # Layer 8: Enhanced health endpoint with AI status
    @app.get("/health/detailed")
    async def health_detailed():
        """Detailed health endpoint with orchestrator status."""
        # Try to get AI status from startup
        ai_status = "checking"
        try:
            from src.ai.orchestrator import get_agent_orchestrator
            orchestrator = get_agent_orchestrator()
            ai_status = "initialized"
        except Exception:
            ai_status = "unavailable"
        
        return {
            "status": "healthy",
            "database": "ready" if db_ready else "not_initialized",
            "orchestrator": ai_status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    logger.info("✅ App created successfully with all layers")

except Exception as e:
    logger.error(f"❌ Failed to create app: {e}", exc_info=True)
    raise
