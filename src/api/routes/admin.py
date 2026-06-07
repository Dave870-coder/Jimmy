"""API routes for admin operations."""

import os
from datetime import datetime
from pathlib import Path

from dotenv import set_key
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_settings
from src.database import get_db
from src.database.models import Message, User, Workflow

settings = get_settings()
ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"
router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


def _ensure_env_file() -> Path:
    """Create the project env file if needed and lock it down for local use."""
    ENV_FILE.touch(exist_ok=True)
    try:
        os.chmod(ENV_FILE, 0o600)
    except OSError:
        pass
    return ENV_FILE


@router.get("/users")
async def get_users(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """Get a lightweight list of users for the dashboard."""
    result = await db.execute(
        select(User.id, User.username, User.email, User.is_active, User.created_at)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.all()
    return [
        {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "is_active": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
        }
        for row in rows
    ]


@router.get("/analytics")
async def get_analytics(start_date: str = None, end_date: str = None, db: AsyncSession = Depends(get_db)):
    """Get platform analytics for the dashboard cards."""
    total_users = await db.scalar(select(func.count(User.id))) or 0
    active_users = await db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0
    total_messages = await db.scalar(select(func.count(Message.id))) or 0
    total_workflows = await db.scalar(select(func.count(Workflow.id))) or 0

    return {
        "active_users": int(active_users),
        "total_users": int(total_users),
        "total_messages": int(total_messages),
        "total_workflows": int(total_workflows),
        "average_response_time": 0.0,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/integrations")
async def get_integrations():
    """Get integration and connection setup details for the dashboard."""
    current_settings = get_settings()
    public_base_url = current_settings.public_base_url.rstrip("/") if current_settings.public_base_url else None
    webhook_url = f"{public_base_url}/api/v1/telegram/webhook" if public_base_url else None

    return {
        "telegram_webhook_url": webhook_url,
        "telegram_configured": bool(current_settings.telegram_bot_token and current_settings.telegram_webhook_secret and webhook_url),
        "whatsapp_connection_endpoint": "/api/v1/whatsapp-qr/start-connection",
        "whatsapp_status_endpoint": "/api/v1/whatsapp-qr/status/{connection_id}",
        "supported_integrations": ["telegram", "whatsapp"],
    }


@router.post("/settings")
async def save_settings(payload: dict):
    """Persist production secrets and base URL settings for the dashboard and runtime."""
    mapping = {
        "telegram_bot_token": "TELEGRAM_BOT_TOKEN",
        "google_api_key": "GOOGLE_API_KEY",
        "openai_api_key": "OPENAI_API_KEY",
        "whatsapp_access_token": "WHATSAPP_ACCESS_TOKEN",
        "telegram_webhook_secret": "TELEGRAM_WEBHOOK_SECRET",
        "public_base_url": "PUBLIC_BASE_URL",
        "database_url": "DATABASE_URL",
    }

    saved = []
    try:
        _ensure_env_file()

        for key, env_key in mapping.items():
            if key not in payload:
                continue

            value = payload[key]
            if value is None:
                continue

            normalized = value if isinstance(value, str) else str(value)
            normalized = normalized.strip()

            os.environ[env_key] = normalized
            set_key(str(ENV_FILE), env_key, normalized, quote_mode="never")
            saved.append(env_key)

        get_settings.cache_clear()

        return {
            "ok": True,
            "saved": saved,
            "message": "Secure settings saved to .env and loaded into the current runtime.",
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.get("/health")
async def health_check():
    """Check system health."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }


@router.post("/restart")
async def restart_bot():
    """Restart the bot system."""
    # TODO: Implement restart logic
    return {"status": "restarting"}


@router.get("/logs")
async def get_logs(limit: int = 100):
    """Get recent logs."""
    # TODO: Retrieve logs
    return []


@router.delete("/cache")
async def clear_cache():
    """Clear application cache."""
    # TODO: Implement cache clearing
    return {"status": "cache cleared"}
