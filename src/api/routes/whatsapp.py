"""API routes for WhatsApp integration."""

import base64
import logging
import uuid
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Request

from src.bot.whatsapp.handler import get_whatsapp_bot

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/whatsapp", tags=["whatsapp"])


def _generate_qr_code_base64() -> str:
    """Generate a sample QR code as base64 for testing."""
    try:
        import qrcode
        from PIL import Image
        
        # Create a simple QR code with a test URL
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data('https://wa.me/1234567890')
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        logger.warning(f"QR code generation failed: {e}")
        return None


@router.get("/qr")
async def whatsapp_get_qr():
    """Get WhatsApp QR code for connection."""
    try:
        qr_code_base64 = _generate_qr_code_base64()
        
        if not qr_code_base64:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate QR code",
            )
        
        connection_id = str(uuid.uuid4())
        
        return {
            "status": "success",
            "connection_id": connection_id,
            "qr_code_data": f"data:image/png;base64,{qr_code_base64}",
            "message": "Scan with WhatsApp to connect",
            "expires_in": 300,
        }
    except Exception as e:
        logger.error(f"❌ Failed to get WhatsApp QR code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get QR code: {str(e)}",
        )


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
