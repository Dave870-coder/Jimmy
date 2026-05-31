"""API routes for WhatsApp integration."""

from fastapi import APIRouter, HTTPException, status

from src.bot.whatsapp.handler import get_whatsapp_bot

router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp"])


@router.get("/webhook")
async def whatsapp_webhook_verify(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None,
):
    """Verify WhatsApp webhook (GET)."""
    bot = await get_whatsapp_bot()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WhatsApp bot not available",
        )
    
    if not bot.verify_webhook_token(hub_verify_token):
        raise HTTPException(status_code=403, detail="Invalid verification token")
    
    if hub_mode == "subscribe":
        return int(hub_challenge)
    
    raise HTTPException(status_code=400, detail="Invalid webhook request")


@router.post("/webhook")
async def whatsapp_webhook_messages(payload: dict):
    """Handle WhatsApp webhook messages (POST)."""
    bot = await get_whatsapp_bot()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="WhatsApp bot not available",
        )
    
    success = await bot.handle_webhook(payload)
    
    return {"ok": success}
