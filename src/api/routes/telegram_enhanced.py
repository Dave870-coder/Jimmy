"""Telegram bot integration routes."""

import logging
from typing import Optional
import httpx
import asyncio

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from src.security.validator import SecurityValidator
from src.ai.orchestrator import get_agent_orchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])

# Store telegram bot tokens (in production, use database/Redis)
telegram_bots = {}
telegram_user_conversations = {}  # Track conversations per user


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
    
    Validates token format, verifies with Telegram API, and sets up webhook.
    """
    try:
        # Validate token format
        SecurityValidator.validate_token(request.token)
        
        bot_id = request.token.split(':')[0]
        
        # Verify token with Telegram API
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"https://api.telegram.org/bot{request.token}/getMe"
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Telegram bot token. Please verify and try again."
                    )
                
                bot_info = response.json()
                if not bot_info.get('ok'):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Telegram API returned error. Token may be invalid."
                    )
                
                bot_username = bot_info.get('result', {}).get('username', 'unknown')
        
        except httpx.RequestError as e:
            logger.error(f"Telegram API connection error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Cannot reach Telegram API. Please try again later."
            )
        
        # Store bot information
        telegram_bots[bot_id] = {
            'token': request.token,
            'status': 'connected',
            'username': bot_username,
            'created_at': __import__('datetime').datetime.now().isoformat(),
        }
        
        logger.info(f"Telegram bot connected: {bot_id} (@{bot_username})")
        
        return {
            'status': 'success',
            'message': f'Telegram bot @{bot_username} connected successfully!',
            'bot_id': bot_id,
            'username': bot_username,
            'webhook_url': 'https://jimmy-ai-bot.onrender.com/api/v1/telegram/webhook',
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect Telegram bot: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to connect Telegram bot: {str(e)}"
        )


@router.get("/status")
async def get_telegram_status():
    """Get status of connected Telegram bots."""
    bots_list = []
    for bot_id, bot_data in telegram_bots.items():
        bots_list.append({
            'bot_id': bot_id,
            'username': bot_data.get('username', 'unknown'),
            'status': bot_data.get('status', 'unknown'),
            'connected_at': bot_data.get('created_at', 'unknown'),
        })
    
    return {
        'connected_bots': len(telegram_bots),
        'bots': bots_list,
        'status': 'active',
        'webhook_url': 'https://jimmy-ai-bot.onrender.com/api/v1/telegram/webhook',
    }


@router.post("/setup-webhook/{bot_id}")
async def setup_telegram_webhook(bot_id: str, webhook_url: str = None):
    """Register webhook URL with Telegram for a connected bot."""
    if bot_id not in telegram_bots:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bot not found. Please connect bot first."
        )
    
    bot_data = telegram_bots[bot_id]
    bot_token = bot_data['token']
    
    if not webhook_url:
        webhook_url = 'https://jimmy-ai-bot.onrender.com/api/v1/telegram/webhook'
    
    try:
        success = await set_telegram_webhook(bot_token, webhook_url)
        
        if success:
            telegram_bots[bot_id]['webhook_registered'] = True
            logger.info(f"Webhook registered for bot {bot_id}")
            
            return {
                'status': 'success',
                'message': f'Webhook registered: {webhook_url}',
                'bot_id': bot_id,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to register webhook with Telegram"
            )
    
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to setup webhook: {str(e)}"
        )


@router.post("/webhook")
async def handle_telegram_webhook(data: dict):
    """
    Handle incoming Telegram webhook messages in real-time.
    
    This endpoint receives messages from Telegram and:
    1. Validates the message
    2. Sends to AI for processing
    3. Sends response back to Telegram user
    """
    try:
        # Extract message from Telegram webhook
        if 'message' not in data:
            return {'ok': True}
        
        message = data['message']
        user_id = message.get('from', {}).get('id')
        text = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')
        bot_token = None
        
        # Find which bot this message is for
        for bid, bot_data in telegram_bots.items():
            bot_token = bot_data['token']
            break  # Use first connected bot
        
        if not text or not user_id or not bot_token:
            return {'ok': True}
        
        # Ignore command messages
        if text.startswith('/'):
            if text == '/start':
                await send_telegram_message(
                    chat_id,
                    "👋 Hello! I'm Jimmy, your AI Bot. Send me any message and I'll respond with intelligence!",
                    bot_token
                )
            return {'ok': True}
        
        # Create conversation ID for this Telegram user
        conversation_id = f"telegram_{user_id}"
        
        # Initialize conversation if needed
        if conversation_id not in telegram_user_conversations:
            telegram_user_conversations[conversation_id] = {
                'messages': [],
                'user_id': user_id,
                'chat_id': chat_id,
            }
        
        # Validate and sanitize input
        try:
            sanitized_text = SecurityValidator.sanitize_input(text)
        except Exception as e:
            logger.warning(f"Input validation failed: {e}")
            await send_telegram_message(
                chat_id,
                "⚠️ Your message contains invalid characters. Please try again.",
                bot_token
            )
            return {'ok': True}
        
        # Send "typing" indicator
        await send_telegram_action(chat_id, "typing", bot_token)
        
        # Get AI response
        try:
            orchestrator = get_agent_orchestrator()
            response = orchestrator.process_message(
                sanitized_text,
                conversation_id=conversation_id
            )
            
            # Store conversation
            telegram_user_conversations[conversation_id]['messages'].append({
                'role': 'user',
                'content': sanitized_text,
            })
            telegram_user_conversations[conversation_id]['messages'].append({
                'role': 'assistant',
                'content': response,
            })
            
            logger.info(f"Telegram message processed from {user_id}")
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            response = "Sorry, I encountered an error processing your message. Please try again."
        
        # Send response back to Telegram
        await send_telegram_message(chat_id, response, bot_token)
        
        return {'ok': True, 'user_id': user_id, 'chat_id': chat_id}
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return {'ok': False, 'error': str(e)}


async def send_telegram_message(chat_id: int, text: str, bot_token: str, parse_mode: str = "HTML"):
    """Send a message to a Telegram chat."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        # Limit message length for Telegram (4096 characters max)
        if len(text) > 4096:
            text = text[:4093] + "..."
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
            
            logger.info(f"Message sent to Telegram chat {chat_id}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")
        return False


async def send_telegram_action(chat_id: int, action: str, bot_token: str):
    """Send a typing indicator or other action to Telegram."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendChatAction"
        
        payload = {
            "chat_id": chat_id,
            "action": action,  # "typing", "upload_photo", etc.
        }
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload)
            
    except Exception as e:
        logger.debug(f"Failed to send Telegram action: {e}")


async def set_telegram_webhook(bot_token: str, webhook_url: str):
    """Register webhook URL with Telegram."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        
        payload = {
            "url": webhook_url,
            "allowed_updates": ["message"],
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code != 200:
                logger.error(f"Webhook setup failed: {response.text}")
                return False
            
            logger.info(f"Telegram webhook registered: {webhook_url}")
            return True
            
    except Exception as e:
        logger.error(f"Webhook registration error: {e}")
        return False


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
