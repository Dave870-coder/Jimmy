"""WhatsApp bot integration using Twilio."""

import json
import logging
from typing import Optional

import httpx

from src.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class WhatsAppBot:
    """WhatsApp bot handler using Twilio or native API."""

    def __init__(self):
        """Initialize WhatsApp bot."""
        self.api_version = settings.whatsapp_api_version
        self.access_token = settings.whatsapp_access_token
        self.phone_number_id = settings.whatsapp_business_phone_number_id
        self.account_id = settings.whatsapp_business_account_id
        self.base_url = f"https://graph.instagram.com/{self.api_version}"

    async def send_message(self, phone: str, message: str) -> bool:
        """Send a text message via WhatsApp."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message,
            },
        }
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            return response.status_code == 200

    async def send_image(self, phone: str, image_url: str, caption: str = "") -> bool:
        """Send an image via WhatsApp."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "image",
            "image": {
                "link": image_url,
            },
        }
        
        if caption:
            payload["image"]["caption"] = caption
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            return response.status_code == 200

    async def send_document(self, phone: str, document_url: str, filename: str = "") -> bool:
        """Send a document via WhatsApp."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "document",
            "document": {
                "link": document_url,
            },
        }
        
        if filename:
            payload["document"]["filename"] = filename
        
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            return response.status_code == 200

    async def handle_webhook(self, payload: dict) -> bool:
        """Handle incoming webhook from WhatsApp."""
        try:
            if "messages" in payload.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}):
                message_data = payload["entry"][0]["changes"][0]["value"]["messages"][0]
                
                sender_phone = message_data["from"]
                message_id = message_data["id"]
                message_type = message_data["type"]
                
                # TODO: Process message based on type
                logger.info(f"Received WhatsApp message from {sender_phone}")
                return True
        except (KeyError, IndexError) as e:
            logger.error(f"Error handling WhatsApp webhook: {e}")
            return False
        
        return False

    def verify_webhook_token(self, token: str) -> bool:
        """Verify webhook token."""
        return token == settings.whatsapp_webhook_verify_token


# Global WhatsApp bot instance
whatsapp_bot: Optional[WhatsAppBot] = None


async def get_whatsapp_bot() -> Optional[WhatsAppBot]:
    """Get WhatsApp bot instance."""
    global whatsapp_bot
    if whatsapp_bot is None:
        try:
            whatsapp_bot = WhatsAppBot()
        except Exception:
            logger.error("WhatsApp bot not available")
            return None
    return whatsapp_bot
