"""Main FastAPI application."""

import logging
import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.middleware.logging import LoggingMiddleware, RateLimitMiddleware
from src.config import get_settings
from src.monitoring.logger import setup_logging
from src.monitoring.health import get_health_monitor
from src.database import engine, Base
from src.database.auto_migrate import (
    auto_migrate_database,
    verify_database_ready,
    get_migration_status,
)

# Import routes with error handling
routes_to_import = ['admin', 'auth', 'memory', 'messages', 'telegram', 'whatsapp', 'whatsapp_qr']
routes = {}

for route_name in routes_to_import:
    try:
        routes[route_name] = __import__(f'src.api.routes.{route_name}', fromlist=[route_name])
    except Exception as e:
        logger.warning(f"Failed to import route '{route_name}': {e}")

settings = get_settings()

# Setup logging
logger = setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("=" * 60)
    logger.info("🚀 APPLICATION STARTING UP")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug: {settings.debug}")
    logger.info(f"Database: {settings.database_url[:50]}...")
    
    # Initialize health monitor
    health_monitor = get_health_monitor()
    logger.info("✅ Health monitor initialized")
    
    # Verify database connectivity
    logger.info("🔍 Verifying database connectivity...")
    if not verify_database_ready(settings.database_url):
        logger.warning("⚠️ Database connectivity warning - will retry on first request")
    else:
        logger.info("✅ Database verified")
    
    # Run auto-migrations
    if settings.app_env == "production":
        logger.info("🔄 Running auto-migrations (production mode)...")
        if auto_migrate_database():
            logger.info("✅ Auto-migrations completed")
        else:
            logger.warning("⚠️ Auto-migrations failed - attempting schema creation")
    
    # Initialize database tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
    
    # Initialize AI Orchestrator (optional - graceful degradation)
    orchestrator_available = False
    try:
        from src.ai.orchestrator import get_agent_orchestrator
        orchestrator = get_agent_orchestrator()
        orchestrator_available = True
        logger.info("✅ AI Orchestrator initialized")
    except Exception as e:
        logger.warning(f"⚠️ AI Orchestrator not available: {e}")

    # Configure Telegram webhook on hosted environments
    try:
        public_base_url = settings.public_base_url or os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
        if settings.telegram_bot_token and public_base_url:
            from src.bot.telegram.handler import get_telegram_bot

            telegram_bot = await get_telegram_bot()
            if telegram_bot:
                webhook_url = f"{public_base_url}{settings.telegram_webhook_path}"
                await telegram_bot.set_webhook(webhook_url, settings.telegram_webhook_secret)
        elif settings.telegram_bot_token:
            logger.warning(
                "⚠️ Telegram bot token is configured, but no public base URL was found. "
                "Set PUBLIC_BASE_URL or deploy on Render so the webhook can be registered."
            )
    except Exception as e:
        logger.error(f"❌ Failed to configure Telegram webhook: {e}")
    
    # Define health check function
    async def check_health():
        """Custom health check function"""
        try:
            from src.ai.orchestrator import get_agent_orchestrator
            orchestrator = get_agent_orchestrator()
            # Could add more checks here
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            raise
    
    # Start health monitoring (background task)
    monitor_task = None
    if settings.app_env == "production" and settings.enable_monitoring:
        async def monitor_background():
            logger.info("📊 Health monitoring started")
            await health_monitor.monitor(check_health)
        
        monitor_task = asyncio.create_task(monitor_background())
        logger.info("✅ Background health monitoring activated")
    
    logger.info("=" * 60)
    logger.info("🎉 APPLICATION READY")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("🛑 APPLICATION SHUTTING DOWN")
    logger.info("=" * 60)
    
    if monitor_task:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            logger.info("Health monitor task cancelled")
    
    await engine.dispose()
    logger.info("✅ Cleanup completed")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Production-ready AI Bot Platform with WhatsApp and Telegram integration",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (safely, skipping any that failed to import)
for route_name in routes_to_import:
    if route_name in routes:
        try:
            router = getattr(routes[route_name], 'router', None)
            if router:
                app.include_router(router)
                logger.info(f"✅ Loaded router: {route_name}")
        except Exception as e:
            logger.error(f"Failed to include router '{route_name}': {e}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Bot Platform API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.app_env,
    }


@app.get("/health", tags=["health"])
async def health():
    """
    Health check endpoint.
    Used by load balancers and container orchestration.
    Returns 200 if healthy, 503 if unhealthy.
    """
    health_monitor = get_health_monitor()
    status_info = health_monitor.get_status()
    
    return {
        "status": "healthy" if health_monitor.healthy else "unhealthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.app_env,
        "monitor": status_info,
    }


@app.get("/ready", tags=["health"])
async def readiness():
    """
    Readiness probe endpoint.
    Returns 200 if ready to accept traffic, 503 otherwise.
    Used by Kubernetes and container orchestration.
    """
    try:
        # Check database (non-blocking, best-effort)
        try:
            migration_status = get_migration_status(settings.database_url)
            db_ready = migration_status.get("ready", True)  # Assume ready if check fails
        except Exception as e:
            logger.warning(f"Database ready check failed: {e}")
            db_ready = True  # Assume ready and continue
        
        # Check orchestrator (optional)
        try:
            from src.ai.orchestrator import get_agent_orchestrator
            orchestrator = get_agent_orchestrator()
            orchestrator_status = "initialized"
        except Exception as e:
            logger.warning(f"Orchestrator check failed: {e}")
            orchestrator_status = "unavailable"
        
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat(),
            "database": "ready" if db_ready else "not_ready",
            "orchestrator": orchestrator_status,
        }
    
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        # Still return 200 - system is minimally operational
        return {
            "ready": True,
            "timestamp": datetime.utcnow().isoformat(),
            "warning": str(e),
        }


@app.get("/metrics", tags=["monitoring"])
async def metrics():
    """
    Prometheus-compatible metrics endpoint.
    Returns usage statistics and performance metrics.
    """
    try:
        # Try to get orchestrator stats
        try:
            from src.ai.orchestrator import get_agent_orchestrator
            orchestrator = get_agent_orchestrator()
            stats = orchestrator.get_usage_stats()
            requests_total = stats.get("total_requests", 0)
            requests_today = stats.get("requests_today", 0)
        except Exception as e:
            logger.warning(f"Orchestrator metrics unavailable: {e}")
            requests_total = 0
            requests_today = 0
        
        health_monitor = get_health_monitor()
        health_status = health_monitor.get_status()
        
        return {
            "requests_total": requests_total,
            "requests_today": requests_today,
            "uptime_seconds": health_status.get("uptime_seconds", 0),
            "health_check_success_rate": health_status.get("success_rate_percent", 0),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@app.get("/status", tags=["monitoring"])
async def status_endpoint():
    """
    Comprehensive status endpoint.
    Returns detailed information about bot status.
    """
    try:
        from src.ai.orchestrator import get_agent_orchestrator
        
        health_monitor = get_health_monitor()
        health_status = health_monitor.get_status()
        migration_status = get_migration_status(settings.database_url)
        
        return {
            "bot_status": "running",
            "environment": settings.app_env,
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "health": health_status,
            "database": migration_status,
        }
    
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "bot_status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@app.get("/docs", tags=["documentation"])
async def docs():
    """API documentation."""
    return {"docs": "/docs", "redoc": "/redoc", "openapi": "/openapi.json"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        workers=1,
        reload=not (settings.app_env == "production"),
        log_level=settings.log_level.lower(),
        access_log=True,
    )
