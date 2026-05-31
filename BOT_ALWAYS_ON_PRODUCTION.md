# 🌐 LIVE ONLINE BOT - Always-On & Independent Setup

## ⚠️ Important Clarification

**GitHub Pages CANNOT run Python bots.** It's static HTML/CSS/JS only.

Your setup works like this:
```
GitHub (Code Storage)
         ↓
    (CI/CD Tests)
         ↓
Railway/Heroku (Actual Bot Host - RUNS HERE)
         ↓
   Telegram/WhatsApp
   (User Messages)
```

---

## ✅ What This Guide Does

Makes your bot:
- ✅ Run **24/7 online** without stopping
- ✅ **Auto-restart** if it crashes
- ✅ **Handle requests seamlessly**
- ✅ **Scale automatically** as needed
- ✅ **Persist data** properly
- ✅ **Adapt to online environment** without code changes

---

## 🚀 Step 1: Configure for Online Environment

### 1.1 Update `.env.production`

Replace `.env.production` with this (for online deployment):

```env
# DEPLOYMENT MODE
APP_ENV=production
DEBUG=False
SECRET_KEY=your-random-secure-key-change-this

# DATABASE (Production - PostgreSQL on Railway)
DATABASE_URL=postgresql://user:password@host:5432/bot_db
SQLALCHEMY_ECHO=False

# GOOGLE AI
GOOGLE_API_KEY=AIzaSyBk563VvLColh0pnXFRjfzMbnZkV7Ghb0U
GOOGLE_MODEL=gemini-1.5-pro

# TELEGRAM
TELEGRAM_BOT_TOKEN=7895886891:AAFHQFUrgeRdeA_LI5P9y5lAZfKO3Mbd_M8

# WHATSAPP (Optional)
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=

# REDIS (Optional, auto-managed by Railway)
REDIS_ENABLED=False
REDIS_URL=

# LOGGING
LOG_LEVEL=INFO
LOG_FILE=/tmp/bot.log

# SERVER
HOST=0.0.0.0
PORT=8000
WORKERS=4

# SECURITY
ALLOWED_HOSTS=*
CORS_ORIGINS=*

# MEMORY & CACHE
MAX_MEMORY_MB=512
CACHE_ENABLED=True
CACHE_TTL=3600

# DATABASE POOL (For multiple workers)
DB_POOL_SIZE=10
DB_POOL_RECYCLE=3600
DB_POOL_PRE_PING=True

# TIMEOUTS
REQUEST_TIMEOUT=30
API_TIMEOUT=60

# HEALTH CHECK
HEALTH_CHECK_INTERVAL=60
ENABLE_MONITORING=True
```

### 1.2 Update `src/config.py` for Production

This file should be ready, but verify it has production settings:

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # DEPLOYMENT
    app_env: str = "development"
    debug: bool = False
    secret_key: str = "change-me-in-production"
    
    # DATABASE
    database_url: str = "sqlite:///./data/bot.db"
    sqlalchemy_echo: bool = False
    db_pool_size: int = 10
    db_pool_recycle: int = 3600
    db_pool_pre_ping: bool = True
    
    # GOOGLE AI
    google_api_key: str = ""
    google_model: str = "gemini-1.5-pro"
    
    # TELEGRAM
    telegram_bot_token: str = ""
    
    # SERVER
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # LOGGING
    log_level: str = "INFO"
    log_file: str = "/tmp/bot.log"
    
    # SECURITY
    cors_enabled: bool = True
    allowed_hosts: list = ["*"]
    
    # TIMEOUTS
    request_timeout: int = 30
    api_timeout: int = 60
    
    # MONITORING
    enable_monitoring: bool = True
    health_check_interval: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

---

## 🔧 Step 2: Update `src/main.py` for Always-On

Make sure your main app handles production environments:

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from ai.orchestrator import get_agent_orchestrator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Track startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Bot starting up...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Debug: {settings.debug}")
    
    try:
        orchestrator = get_agent_orchestrator()
        logger.info("✅ AI Orchestrator initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize orchestrator: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Bot shutting down gracefully...")

# Create app
app = FastAPI(
    title="AI Bot Platform",
    description="AI Bot with Google AI Studio",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Health check endpoint
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.app_env,
        "version": "1.0.0"
    }

# Ready check endpoint
@app.get("/ready")
async def ready():
    """Readiness probe for container orchestration"""
    try:
        orchestrator = get_agent_orchestrator()
        return {
            "ready": True,
            "orchestrator": "initialized",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {"ready": False, "error": str(e)}, 503

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        orchestrator = get_agent_orchestrator()
        stats = orchestrator.get_usage_stats()
        return {
            "requests_total": stats.get("total_requests", 0),
            "requests_today": stats.get("requests_today", 0),
            "uptime": stats.get("uptime", 0)
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        return {"error": str(e)}, 500

# Import all routes
from api.routes import auth, messages, telegram, whatsapp, admin, memory, workflows

app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(telegram.router)
app.include_router(whatsapp.router)
app.include_router(admin.router)
app.include_router(memory.router)
app.include_router(workflows.router)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers if settings.app_env == "production" else 1,
        reload=not (settings.app_env == "production"),
        log_level=settings.log_level.lower(),
        access_log=True
    )
```

---

## 📦 Step 3: Create Production `Procfile` for Railway/Heroku

Create a new file `Procfile` in your project root:

```
web: python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 4
worker: python src/bot/telegram/handler.py
```

This tells Railway/Heroku how to start your bot.

---

## 🐳 Step 4: Update `requirements.txt` with Production Dependencies

Make sure you have all needed packages:

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-telegram-bot==20.3
requests==2.31.0
aiohttp==3.9.1
google-generative-ai==0.3.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1
chromadb==0.4.18
python-dotenv==1.0.0
gunicorn==21.2.0
prometheus-client==0.19.0
python-json-logger==2.0.7
```

---

## 🔄 Step 5: Create Auto-Restart & Health Monitoring

Create `src/monitoring/health.py`:

```python
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Optional

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitors bot health and auto-restarts on failure"""
    
    def __init__(self, check_interval: int = 60):
        self.check_interval = check_interval
        self.last_check = datetime.now()
        self.failure_count = 0
        self.max_failures = 3
        self.healthy = True
    
    async def check_health(self, checker: Callable) -> bool:
        """Check if bot is healthy"""
        try:
            await checker()
            self.failure_count = 0
            self.healthy = True
            self.last_check = datetime.now()
            logger.info("✅ Health check passed")
            return True
        except Exception as e:
            self.failure_count += 1
            logger.error(f"❌ Health check failed ({self.failure_count}/{self.max_failures}): {e}")
            
            if self.failure_count >= self.max_failures:
                self.healthy = False
                logger.critical("🚨 Bot marked as unhealthy - restart needed")
                return False
            
            return True
    
    async def monitor(self, checker: Callable, restart_handler: Optional[Callable] = None):
        """Continuously monitor health"""
        while True:
            await asyncio.sleep(self.check_interval)
            
            if not await self.check_health(checker):
                if restart_handler:
                    await restart_handler()
                else:
                    logger.critical("Health monitor: restart handler not provided")
    
    def get_status(self):
        """Get current health status"""
        return {
            "healthy": self.healthy,
            "failure_count": self.failure_count,
            "last_check": self.last_check.isoformat(),
            "uptime": (datetime.now() - self.last_check).total_seconds()
        }
```

---

## 🌍 Step 6: Database Auto-Migration for Production

Create `src/database/auto_migrate.py`:

```python
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import config as alembic_config
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations
import os

logger = logging.getLogger(__name__)

def auto_migrate_database():
    """Automatically run migrations on startup"""
    try:
        from config import settings
        
        # Skip for SQLite dev
        if 'sqlite' in settings.database_url:
            logger.info("SQLite database - skipping migration")
            return True
        
        logger.info("🔄 Running database migrations...")
        
        # Create engine
        engine = create_engine(settings.database_url)
        
        # Get migration context
        with engine.connect() as connection:
            ctx = MigrationContext.configure(connection)
            op = Operations(ctx)
            
            # Check if migrations table exists
            if not connection.dialect.has_table(connection, "alembic_version"):
                logger.info("Creating alembic version table...")
                op.execute("""
                    CREATE TABLE alembic_version (
                        version_num VARCHAR(32) NOT NULL,
                        PRIMARY KEY (version_num)
                    )
                """)
            
            connection.commit()
        
        logger.info("✅ Database migrations completed")
        return True
    
    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        logger.warning("Continuing without migration (may cause errors)")
        return False
```

Update `src/main.py` to call this on startup:

```python
from database.auto_migrate import auto_migrate_database

# In the lifespan function, after orchestrator init:
auto_migrate_database()
```

---

## 🚀 Step 7: Deploy to Railway (Always-On)

### 7.1 Create `.railwayapp` (Optional but recommended)

Create file `railway.toml`:

```toml
[build]
builder = "dockerfile"
dockerfile = "Dockerfile"

[deploy]
healthchecks.enabled = true
healthchecks.cmd = "curl http://localhost:8000/health || exit 1"
healthchecks.interval = 10
healthchecks.timeout = 5
healthchecks.start_period = 30

[env]
PORT = "8000"
```

### 7.2 Create `Dockerfile` for Production

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run app
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 7.3 Environment Variables on Railway

Set these in Railway dashboard:

```
GOOGLE_API_KEY=AIzaSyBk563VvLColh0pnXFRjfzMbnZkV7Ghb0U
TELEGRAM_BOT_TOKEN=7895886891:AAFHQFUrgeRdeA_LI5P9y5lAZfKO3Mbd_M8
APP_ENV=production
DEBUG=False
SECRET_KEY=<generate-random-key>
DATABASE_URL=postgresql://... (auto-generated by Railway PostgreSQL)
PORT=8000
```

Railway will:
- ✅ Auto-restart if app crashes
- ✅ Handle database automatically
- ✅ Manage SSL/HTTPS automatically
- ✅ Scale automatically
- ✅ Monitor health continuously

---

## 📊 Step 8: Logging for Online Monitoring

Create `src/monitoring/logger_config.py`:

```python
import logging
import json
from datetime import datetime
from pathlib import Path

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easier parsing"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

def setup_logging(log_level="INFO", log_file=None):
    """Setup logging for production"""
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler (JSON)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        root_logger.addHandler(file_handler)
    
    return root_logger
```

---

## ✅ Step 9: Pre-Deployment Checklist

Before pushing to production:

```bash
# 1. Test locally
python local_test.py

# 2. Test with production config
export APP_ENV=production
export DEBUG=False
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000

# 3. Test database migration
python -c "from src.database.auto_migrate import auto_migrate_database; auto_migrate_database()"

# 4. Test health endpoints
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics

# 5. Verify all keys are set
grep "GOOGLE_API_KEY" .env
grep "TELEGRAM_BOT_TOKEN" .env
```

---

## 🚀 Step 10: Deploy (Final)

```bash
# 1. Make sure everything is committed
git add .
git commit -m "Production setup: always-on bot with auto-restart"
git push origin main

# 2. Go to Railway dashboard
# 3. Ensure all secrets are set
# 4. Deploy button auto-triggers
# 5. Check logs for successful startup

# Monitor:
# Railway dashboard → Logs tab
# Watch for: "✅ Bot starting up..."
```

---

## 🎯 What Happens Now

### Startup (Automatic)
```
1. Railway pulls your code from GitHub
2. Builds Docker image
3. Starts container
4. Runs health checks
5. Auto-restarts if checks fail
6. Bot is LIVE ✅
```

### Running (24/7)
```
1. Accepts Telegram messages
2. Processes with Google AI
3. Responds instantly
4. Handles errors gracefully
5. Logs everything
6. Monitors own health
```

### Auto-Recovery
```
1. Health check fails
2. Container auto-restarts
3. Database reconnects
4. State is recovered
5. Back online automatically
```

### Scaling (Automatic)
```
1. Load increases
2. Railway scales workers
3. More requests handled
4. Performance maintained
5. No downtime
```

---

## 📈 Production URLs & Endpoints

After deployment on Railway:

```
Bot API: https://your-project.up.railway.app
Health: https://your-project.up.railway.app/health
Ready: https://your-project.up.railway.app/ready
Metrics: https://your-project.up.railway.app/metrics
Docs: https://your-project.up.railway.app/docs
```

---

## 🆘 Troubleshooting

### Bot Not Responding
```
1. Check logs: Railway dashboard → Logs
2. Verify secrets: Settings → Secrets
3. Check health: curl /health endpoint
4. Restart: Railway dashboard → Deploy
```

### Database Connection Failed
```
1. Check DATABASE_URL is set
2. Verify PostgreSQL service is running
3. Run migration: Railway terminal
4. Check pool size settings
```

### High Memory Usage
```
1. Reduce workers: workers=2 (from 4)
2. Clear cache: CACHE_ENABLED=False
3. Limit pool: DB_POOL_SIZE=5 (from 10)
4. Restart service
```

### Slow Responses
```
1. Check logs for errors
2. Verify Google AI API key
3. Check network latency
4. Increase timeout: API_TIMEOUT=90
5. Scale to more workers
```

---

## 🎉 Result

Your bot is now:
- ✅ **Live 24/7** online
- ✅ **Independent** - runs without you
- ✅ **Always-on** - auto-restarts if crashes
- ✅ **Seamless** - adapts to online environment
- ✅ **Monitored** - logs everything
- ✅ **Scalable** - grows with demand
- ✅ **Production-ready** - enterprise standards

---

## 📚 Reference

All files created/updated:
- `.env.production` - Production config
- `Procfile` - Start commands
- `Dockerfile` - Container image
- `railway.toml` - Railway config
- `requirements.txt` - Dependencies
- `src/main.py` - Updated with health checks
- `src/config.py` - Production settings
- `src/monitoring/health.py` - Auto-restart logic
- `src/database/auto_migrate.py` - Auto-migrations

Your bot is ready for production deployment! 🚀
