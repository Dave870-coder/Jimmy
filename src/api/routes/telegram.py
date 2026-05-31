"""API routes for Telegram integration."""

from fastapi import APIRouter, HTTPException, status

from src.bot.telegram.handler import get_telegram_bot

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(update: dict):
    """Handle Telegram webhook updates."""
    bot = await get_telegram_bot()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram bot not available",
        )
    
    # TODO: Process update through bot
    return {"ok": True}
