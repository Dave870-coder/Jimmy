"""FastAPI application with incremental feature restoration."""

import logging
import os
from datetime import datetime
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to check if database is initialized
def check_database_initialized() -> bool:
    """Check if database tables have been created."""
    try:
        from sqlalchemy import create_engine, inspect
        from src.config import get_settings
        
        settings = get_settings()
        sync_url = settings.database_url
        if sync_url.startswith('sqlite+'):
            sync_url = sync_url.replace('sqlite+aiosqlite:', 'sqlite:')
        
        logger.debug(f"Checking database at: {sync_url}")
        engine = create_engine(sync_url, echo=False)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        engine.dispose()
        
        table_count = len(tables)
        logger.debug(f"Found {table_count} tables: {tables}")
        
        # If we have any tables, database is initialized
        if table_count > 0:
            logger.info(f"✅ Database initialized: {table_count} tables found")
            return True
        
        # No tables found - try to create them
        logger.warning(f"⚠️ No tables found - attempting emergency initialization")
        try:
            import pathlib
            import src.database.models  # noqa
            from src.database import Base as db_base
            
            # Ensure directory exists
            if sync_url.startswith('sqlite:///'):
                db_path = sync_url.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)
                if db_dir:
                    pathlib.Path(db_dir).mkdir(parents=True, exist_ok=True)
            
            # Create tables
            logger.info(f"Creating tables via emergency initialization...")
            sync_engine = create_engine(sync_url, echo=False)
            db_base.metadata.create_all(sync_engine)
            sync_engine.dispose()
            logger.info(f"✅ Emergency initialization completed")
            
            # Verify
            engine = create_engine(sync_url, echo=False)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            engine.dispose()
            
            if len(tables) > 0:
                logger.info(f"✅ Emergency initialization succeeded: {len(tables)} tables created")
                return True
            else:
                logger.error(f"❌ Emergency initialization failed - no tables after create_all")
                return False
                
        except Exception as e:
            logger.error(f"❌ Emergency initialization exception: {e}")
            logger.error(f"Stack trace: {__import__('traceback').format_exc()}")
            return False
            
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return False

def ensure_database_initialized() -> bool:
    """Ensure database is initialized - create tables if needed (lazy initialization)."""
    try:
        # First check if already initialized
        if check_database_initialized():
            logger.info("✅ Database already initialized")
            return True
        
        logger.warning("⚠️ Database not initialized - attempting to create tables now")
        
        from sqlalchemy import create_engine, inspect
        from src.database import Base as db_base
        from src.config import get_settings
        import pathlib
        
        # Ensure models are loaded
        try:
            import src.database.models  # noqa
            logger.info("✅ Models loaded for lazy initialization")
        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            return False
        
        current_settings = get_settings()
        sync_url = current_settings.database_url
        logger.info(f"Original database_url: {sync_url}")
        
        if sync_url.startswith('sqlite+'):
            sync_url = sync_url.replace('sqlite+aiosqlite:', 'sqlite:')
        
        logger.info(f"Converted sync_url: {sync_url}")
        
        # Create directory if needed
        db_path = None
        if sync_url.startswith('sqlite:///'):
            db_path = sync_url.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            logger.info(f"Database path: {db_path}")
            logger.info(f"Database dir: {db_dir}")
            
            if db_dir:
                try:
                    pathlib.Path(db_dir).mkdir(parents=True, exist_ok=True)
                    logger.info(f"✅ Database directory ensured: {db_dir}")
                    logger.info(f"  - Is directory: {os.path.isdir(db_dir)}")
                    logger.info(f"  - Is readable: {os.access(db_dir, os.R_OK)}")
                    logger.info(f"  - Is writable: {os.access(db_dir, os.W_OK)}")
                except Exception as e:
                    logger.error(f"❌ Failed to create database directory: {e}")
                    return False
        
        # Create tables
        logger.info(f"Creating tables via lazy initialization...")
        try:
            sync_engine = create_engine(sync_url, echo=False)
            logger.info(f"Sync engine created successfully")
            
            # Log metadata
            table_names = [t.name for t in db_base.metadata.tables.values()]
            logger.info(f"Tables to create: {table_names}")
            
            db_base.metadata.create_all(sync_engine)
            logger.info("✅ metadata.create_all() completed")
            
            # Verify immediately
            inspector = inspect(sync_engine)
            created_tables = inspector.get_table_names()
            logger.info(f"Tables actually created: {created_tables}")
            logger.info(f"Total tables: {len(created_tables)}")
            
            sync_engine.dispose()
            logger.info("✅ Engine disposed")
            
        except Exception as e:
            logger.error(f"❌ Failed during table creation: {e}")
            logger.error(f"Stack trace: {__import__('traceback').format_exc()}")
            return False
        
        logger.info("✅ Lazy initialization tables created")
        
        # Verify one final time
        if check_database_initialized():
            logger.info("✅ Lazy initialization verified - tables exist")
            return True
        else:
            logger.error("❌ Lazy initialization failed - tables still not found after creation")
            return False
            
    except Exception as e:
        logger.error(f"❌ Lazy initialization exception: {e}")
        logger.error(f"Stack trace: {__import__('traceback').format_exc()}")
        return False

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
            
            # Use centralized db_init for database initialization
            from src.db_init import init_db_safe, check_db_status
            
            logger.info("Initializing database...")
            success, msg = init_db_safe()
            
            if success:
                logger.info(f"✅ Database initialization successful: {msg}")
                status = check_db_status()
                logger.info(f"✅ Database status: {status}")
            else:
                logger.error(f"❌ Database initialization failed: {msg}")
                logger.error("⚠️  Database will be created on first request")
            
            logger.info("=" * 60)
            logger.info("🎉 APPLICATION READY")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ Startup error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            # Don't fail - application can still start and initialize on first request
        
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
        """Check if database is initialized and force initialization if needed."""
        from src.db_init import check_db_status, init_db_safe
        
        try:
            # First check current status
            status = check_db_status()
            
            # If not initialized, force initialization
            if status != "ready":
                logger.warning(f"Database status is '{status}', attempting initialization...")
                success, msg = init_db_safe()
                
                if success:
                    logger.info(f"✅ Force initialization successful: {msg}")
                    return "ready"
                else:
                    logger.warning(f"Force initialization incomplete: {msg}")
                    # Check again after attempt
                    status = check_db_status()
                    return status
            
            return status
        except Exception as e:
            logger.error(f"Database status check failed: {e}")
            return "error"
    
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
        # Return 200 even if database is initializing - Render will retry
        # This allows the service to start while database is being set up
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_status,
            "version": "1.0.0",
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
    
    @app.post("/initialize-db")
    async def initialize_db_endpoint():
        """Manual database initialization endpoint (for recovery)."""
        try:
            logger.info("🔧 Manual database initialization requested...")
            from src.db_init import init_db_safe
            
            success, msg = init_db_safe()
            
            logger.info(f"Database initialization: {'✅ Success' if success else '❌ Failed'} - {msg}")
            
            return {
                "success": success,
                "message": msg,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"❌ Manual initialization failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "message": str(e),
                "error": traceback.format_exc(),
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
        # Try lazy initialization
        ensure_database_initialized()
        
        return {
            "bot_status": "running",
            "environment": init_status["config"],
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "ready" if check_database_initialized() else "not_initialized",
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
        # Try lazy initialization
        ensure_database_initialized()
        
        # Try to get AI status from startup
        ai_status = "checking"
        try:
            from src.ai.orchestrator import get_agent_orchestrator
            orchestrator = get_agent_orchestrator()
            ai_status = "initialized"
        except Exception:
            ai_status = "unavailable"
        
        db_status = "ready" if check_database_initialized() else "not_initialized"
        return {
            "status": "healthy",
            "database": db_status,
            "orchestrator": ai_status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    # Diagnostic endpoint for database troubleshooting
    @app.get("/health/diagnostics")
    async def health_diagnostics():
        """Detailed diagnostics for database and environment issues."""
        # Try lazy initialization first
        ensure_database_initialized()
        
        from src.config import get_settings
        from sqlalchemy import create_engine, inspect
        import pathlib
        
        diagnostics = {
            "timestamp": datetime.utcnow().isoformat(),
            "environment": {},
            "database": {},
            "filesystem": {},
        }
        
        try:
            settings = get_settings()
            diagnostics["environment"]["app_env"] = settings.app_env
            diagnostics["environment"]["database_url"] = settings.database_url
            
            # Parse database URL
            sync_url = settings.database_url
            if sync_url.startswith('sqlite+'):
                sync_url = sync_url.replace('sqlite+aiosqlite:', 'sqlite:')
            diagnostics["database"]["parsed_url"] = sync_url
            
            # Extract path
            if sync_url.startswith('sqlite:///'):
                db_path = sync_url.replace('sqlite:///', '')
                diagnostics["database"]["path"] = db_path
                
                db_dir = os.path.dirname(db_path)
                diagnostics["filesystem"]["directory"] = db_dir
                diagnostics["filesystem"]["dir_exists"] = os.path.isdir(db_dir)
                diagnostics["filesystem"]["dir_readable"] = os.access(db_dir, os.R_OK) if os.path.isdir(db_dir) else False
                diagnostics["filesystem"]["dir_writable"] = os.access(db_dir, os.W_OK) if os.path.isdir(db_dir) else False
                diagnostics["filesystem"]["file_exists"] = os.path.isfile(db_path)
                diagnostics["filesystem"]["file_readable"] = os.access(db_path, os.R_OK) if os.path.isfile(db_path) else False
                
                # Try to create engine and inspect tables
                try:
                    engine = create_engine(sync_url, echo=False)
                    inspector = inspect(engine)
                    tables = inspector.get_table_names()
                    diagnostics["database"]["tables_found"] = len(tables)
                    diagnostics["database"]["table_names"] = tables
                    diagnostics["database"]["initialized"] = len(tables) > 0
                    engine.dispose()
                except Exception as e:
                    diagnostics["database"]["error"] = str(e)
                    diagnostics["database"]["initialized"] = False
        except Exception as e:
            diagnostics["error"] = str(e)
        
        return diagnostics
    
    logger.info("✅ App created successfully with all layers")

except Exception as e:
    logger.error(f"❌ Failed to create app: {e}", exc_info=True)
    raise

# Force rebuild 2026-06-07 14:44:36
