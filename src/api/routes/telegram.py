"""API routes for Telegram integration."""

import logging
from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel

from src.config import get_settings
from src.bot.telegram.handler import get_telegram_bot

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])
settings = get_settings()


class TelegramConnectRequest(BaseModel):
    """Request to connect Telegram bot."""
    token: str


@router.post("/connect")
async def telegram_connect(request: TelegramConnectRequest):
    """Connect Telegram bot with the provided token."""
    if not request.token or not request.token.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram bot token is required",
        )
    
    try:
        # Try to initialize bot with the token
        from telegram import Bot
        
        bot = Bot(token=request.token)
        me = await bot.get_me()
        
        logger.info(f"✅ Telegram bot connected: {me.username}")
        
        return {
            "ok": True,
            "username": me.username,
            "first_name": me.first_name,
            "is_bot": me.is_bot,
            "message": "Telegram bot connected successfully",
        }
    except Exception as e:
        logger.error(f"❌ Failed to connect Telegram bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Telegram bot: {str(e)}",
        )


@router.post("/webhook")
async def telegram_webhook(
    update: dict,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    """Handle Telegram webhook updates."""
    bot = await get_telegram_bot()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram bot not available",
        )

    if settings.telegram_webhook_secret:
        if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Telegram webhook secret",
            )

    processed = await bot.handle_webhook_update(update)
    if not processed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Telegram webhook payload",
        )

    return {"ok": True}
