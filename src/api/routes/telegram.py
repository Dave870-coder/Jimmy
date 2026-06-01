"""API routes for Telegram integration."""

from fastapi import APIRouter, Header, HTTPException, status

from src.config import get_settings
from src.bot.telegram.handler import get_telegram_bot

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])
settings = get_settings()


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
