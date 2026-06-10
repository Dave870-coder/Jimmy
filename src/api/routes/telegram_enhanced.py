"""Telegram bot integration routes."""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.security.validator import SecurityValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])

# Store telegram bot tokens (in production, use database/Redis)
telegram_bots = {}


class TelegramConnectRequest(BaseModel):
    """Request model for connecting Telegram bot."""
    token: str


class TelegramStatus(BaseModel):
    """Response model for Telegram status."""
    connected: bool
    bot_username: Optional[str] = None
    message: str


@router.post("/connect", response_model=dict)
async def connect_telegram_bot(request: TelegramConnectRequest):
    """
    Connect a Telegram bot using bot token.
    
    Validates token format and stores for later use.
    """
    try:
        # Validate token format
        SecurityValidator.validate_token(request.token)
        
        # In production, verify with Telegram API
        # For now, just store the token
        bot_id = request.token.split(':')[0]
        telegram_bots[bot_id] = {
            'token': request.token,
            'status': 'connected',
            'created_at': None,
        }
        
        logger.info(f"Telegram bot connected: {bot_id}")
        
        return {
            'status': 'success',
            'message': 'Telegram bot connected successfully',
            'bot_id': bot_id,
        }
    
    except Exception as e:
        logger.error(f"Failed to connect Telegram bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Telegram bot: {str(e)}"
        )


@router.get("/status")
async def get_telegram_status():
    """Get status of connected Telegram bots."""
    return {
        'connected_bots': len(telegram_bots),
        'bots': list(telegram_bots.keys()),
        'status': 'active',
    }


@router.post("/webhook")
async def handle_telegram_webhook(data: dict):
    """
    Handle incoming Telegram webhook messages.
    
    This endpoint receives messages from Telegram and processes them.
    """
    try:
        # Extract message from Telegram webhook
        if 'message' not in data:
            return {'ok': True}
        
        message = data['message']
        user_id = message.get('from', {}).get('id')
        text = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')
        
        if not text or not user_id:
            return {'ok': True}
        
        # Process message through bot
        # In production, this would call the bot's message handler
        logger.info(f"Telegram message from {user_id}: {text[:50]}")
        
        return {
            'ok': True,
            'user_id': user_id,
            'chat_id': chat_id,
            'message_received': True,
        }
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {'ok': False, 'error': str(e)}


@router.get("/qr")
async def get_telegram_qr():
    """Get QR code for Telegram bot connection (if applicable)."""
    return {
        'message': 'Use BotFather to create bot or add bot token in settings',
        'botfather_url': 'https://t.me/botfather',
    }


@router.delete("/disconnect/{bot_id}")
async def disconnect_telegram_bot(bot_id: str):
    """Disconnect a Telegram bot."""
    if bot_id not in telegram_bots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found"
        )
    
    del telegram_bots[bot_id]
    logger.info(f"Telegram bot disconnected: {bot_id}")
    
    return {'status': 'success', 'message': 'Bot disconnected'}
