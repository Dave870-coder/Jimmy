#!/usr/bin/env python3
"""
Telegram Webhook Setup & Configuration Script

This script helps set up real-time Telegram bot integration with Jimmy AI.
It validates tokens, registers webhooks, and tests the connection.

Usage:
    python setup_telegram_webhook.py
"""

import asyncio
import json
import logging
import os
import secrets
import sys
from typing import Optional, Tuple

import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)


class TelegramWebhookSetup:
    """Handles Telegram webhook configuration."""
    
    def __init__(self):
        """Initialize setup helper."""
        self.token = None
        self.bot_info = None
        self.webhook_url = None
        self.webhook_secret = None
        self.public_url = None
    
    async def validate_token(self, token: str) -> Tuple[bool, str]:
        """Validate Telegram bot token format and validity."""
        logger.info("🔍 Validating Telegram token...")
        
        if not token or not token.strip():
            return False, "Token is empty"
        
        # Check format: number:string
        if ':' not in token:
            return False, "Invalid token format (should be: 123456789:ABCdEF...)"
        
        try:
            bot_id, token_secret = token.split(':', 1)
            if not bot_id.isdigit() or len(token_secret) < 20:
                return False, "Invalid token format"
        except Exception as e:
            return False, f"Token format error: {e}"
        
        # Test token with Telegram API
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"https://api.telegram.org/bot{token}/getMe"
                logger.info(f"   Testing with Telegram API...")
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        self.bot_info = data.get('result', {})
                        self.token = token
                        logger.info(f"   ✅ Valid token for bot: @{self.bot_info.get('username')}")
                        return True, f"Valid token for @{self.bot_info.get('username')}"
                    else:
                        error = data.get('description', 'Unknown error')
                        return False, f"API error: {error}"
                else:
                    return False, f"HTTP {response.status_code}: {response.text}"
        
        except httpx.RequestError as e:
            return False, f"Network error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    async def register_webhook(
        self,
        public_url: str,
        webhook_secret: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Register webhook with Telegram."""
        if not self.token:
            return False, "Token not validated yet"
        
        logger.info("📍 Registering webhook...")
        
        self.public_url = public_url.rstrip('/')
        self.webhook_url = f"{self.public_url}/api/v1/telegram/webhook"
        self.webhook_secret = webhook_secret or secrets.token_urlsafe(32)
        
        logger.info(f"   Webhook URL: {self.webhook_url}")
        logger.info(f"   Using secret token: {self.webhook_secret[:20]}...")
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"https://api.telegram.org/bot{self.token}/setWebhook"
                
                payload = {
                    "url": self.webhook_url,
                    "secret_token": self.webhook_secret,
                    "allowed_updates": ["message", "edited_channel_post", "callback_query"],
                    "max_connections": 40,
                }
                
                logger.info(f"   Setting webhook with Telegram API...")
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        logger.info(f"   ✅ Webhook registered successfully")
                        return True, "Webhook registered"
                    else:
                        error = data.get('description', 'Unknown error')
                        return False, f"API error: {error}"
                else:
                    return False, f"HTTP {response.status_code}: {response.text}"
        
        except httpx.RequestError as e:
            return False, f"Network error: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"
    
    async def get_webhook_info(self) -> dict:
        """Get current webhook information."""
        if not self.token:
            return {"error": "Token not validated"}
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"https://api.telegram.org/bot{self.token}/getWebhookInfo"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        return data.get('result', {})
        except Exception as e:
            logger.error(f"Error getting webhook info: {e}")
        
        return {"error": "Failed to get webhook info"}
    
    async def test_webhook(self) -> Tuple[bool, str]:
        """Test webhook by sending a test message."""
        if not self.token or not self.webhook_url:
            return False, "Webhook not registered"
        
        logger.info("🧪 Testing webhook...")
        
        # Create test update
        test_message = {
            "update_id": 999999,
            "message": {
                "message_id": 1,
                "date": 1234567890,
                "chat": {"id": 123456789, "type": "private"},
                "from": {"id": 123456789, "is_bot": False, "first_name": "Test"},
                "text": "/start"
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                headers = {
                    "X-Telegram-Bot-Api-Secret-Token": self.webhook_secret,
                    "Content-Type": "application/json"
                }
                
                # Try local first
                local_urls = [
                    "http://localhost:8000",
                    "http://127.0.0.1:8000",
                ]
                
                for base_url in local_urls:
                    try:
                        url = f"{base_url}/api/v1/telegram/webhook"
                        logger.info(f"   Testing local endpoint: {url}")
                        response = await client.post(
                            url,
                            json=test_message,
                            headers=headers,
                            timeout=5
                        )
                        
                        if response.status_code in [200, 400]:
                            logger.info(f"   ✅ Webhook endpoint accessible")
                            return True, "Webhook test successful"
                    except httpx.ConnectError:
                        continue
                    except Exception as e:
                        logger.debug(f"   Error testing local: {e}")
                        continue
                
                logger.warning("   ⚠️  Could not test local endpoint")
                return False, "Webhook endpoint not accessible locally"
        
        except Exception as e:
            return False, f"Test failed: {e}"
    
    def print_summary(self):
        """Print configuration summary."""
        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 TELEGRAM WEBHOOK CONFIGURATION SUMMARY")
        logger.info("=" * 70)
        
        if self.bot_info:
            logger.info(f"Bot Name:       {self.bot_info.get('first_name')}")
            logger.info(f"Bot Username:   @{self.bot_info.get('username')}")
            logger.info(f"Bot ID:         {self.bot_info.get('id')}")
        
        if self.webhook_url:
            logger.info(f"Webhook URL:    {self.webhook_url}")
        
        if self.webhook_secret:
            logger.info(f"Secret Token:   {self.webhook_secret[:20]}...")
        
        logger.info("")
        logger.info("📝 Environment Variables to set:")
        logger.info("")
        logger.info(f"TELEGRAM_BOT_TOKEN={self.token}")
        logger.info(f"TELEGRAM_WEBHOOK_URL={self.webhook_url}")
        logger.info(f"TELEGRAM_WEBHOOK_SECRET={self.webhook_secret}")
        logger.info("")
        logger.info("=" * 70)


async def interactive_setup():
    """Interactive setup wizard."""
    logger.info("")
    logger.info("🚀 TELEGRAM REAL-TIME BOT SETUP WIZARD")
    logger.info("=" * 70)
    logger.info("")
    
    setup = TelegramWebhookSetup()
    
    # Step 1: Get token
    logger.info("📋 STEP 1: Telegram Bot Token")
    logger.info("-" * 70)
    logger.info("Get your token from @BotFather on Telegram")
    logger.info("")
    
    while True:
        token = input("Enter your Telegram bot token: ").strip()
        valid, msg = await setup.validate_token(token)
        
        if valid:
            logger.info(f"✅ {msg}")
            break
        else:
            logger.error(f"❌ {msg}")
            logger.info("Please try again or get a new token from @BotFather")
            logger.info("")
    
    # Step 2: Get public URL
    logger.info("")
    logger.info("📍 STEP 2: Public URL")
    logger.info("-" * 70)
    logger.info("Where is your Jimmy bot deployed?")
    logger.info("Examples:")
    logger.info("  - Production: https://jimmy-ai-bot.onrender.com")
    logger.info("  - Local ngrok: https://abc123.ngrok.io")
    logger.info("  - Local tunnel: https://yourname.loca.lt")
    logger.info("")
    
    while True:
        public_url = input("Enter public URL (without /api/v1/telegram/webhook): ").strip()
        
        if public_url.startswith("http"):
            break
        else:
            logger.error("❌ URL must start with http:// or https://")
            logger.info("")
    
    # Step 3: Optional secret
    logger.info("")
    logger.info("🔐 STEP 3: Webhook Secret (Optional)")
    logger.info("-" * 70)
    secret = input("Enter webhook secret (press Enter to generate): ").strip()
    
    if not secret:
        secret = secrets.token_urlsafe(32)
        logger.info(f"Generated secret: {secret}")
    
    # Step 4: Register webhook
    logger.info("")
    logger.info("📡 STEP 4: Registering Webhook")
    logger.info("-" * 70)
    
    success, msg = await setup.register_webhook(public_url, secret)
    
    if not success:
        logger.error(f"❌ Failed to register webhook: {msg}")
        return False
    
    logger.info(f"✅ {msg}")
    
    # Step 5: Get webhook info
    logger.info("")
    logger.info("✅ STEP 5: Webhook Status")
    logger.info("-" * 70)
    
    webhook_info = await setup.get_webhook_info()
    
    if "error" not in webhook_info:
        logger.info(f"Webhook URL:        {webhook_info.get('url')}")
        logger.info(f"Pending updates:    {webhook_info.get('pending_update_count', 0)}")
        logger.info(f"Max connections:    {webhook_info.get('max_connections', 40)}")
    else:
        logger.warning(f"⚠️  {webhook_info.get('error')}")
    
    # Step 6: Test webhook
    logger.info("")
    logger.info("🧪 STEP 6: Testing Webhook")
    logger.info("-" * 70)
    
    success, msg = await setup.test_webhook()
    if success:
        logger.info(f"✅ {msg}")
    else:
        logger.warning(f"⚠️  {msg}")
        logger.info("The endpoint may not be accessible locally, but should work once deployed.")
    
    # Print summary
    logger.info("")
    setup.print_summary()
    
    # Step 7: Save to .env
    logger.info("")
    logger.info("💾 STEP 7: Saving to .env")
    logger.info("-" * 70)
    
    save_to_env = input("Save configuration to .env? (y/n): ").strip().lower()
    
    if save_to_env == 'y':
        env_file = ".env"
        
        if os.path.exists(env_file):
            # Read existing
            with open(env_file, 'r') as f:
                lines = f.readlines()
            
            # Update or add
            keys_to_update = {
                'TELEGRAM_BOT_TOKEN': setup.token,
                'TELEGRAM_WEBHOOK_URL': setup.webhook_url,
                'TELEGRAM_WEBHOOK_SECRET': setup.webhook_secret,
            }
            
            updated_keys = set()
            new_lines = []
            
            for line in lines:
                for key, value in keys_to_update.items():
                    if line.startswith(key + '='):
                        new_lines.append(f"{key}={value}\n")
                        updated_keys.add(key)
                        break
                else:
                    new_lines.append(line)
            
            # Add missing keys
            for key, value in keys_to_update.items():
                if key not in updated_keys:
                    new_lines.append(f"\n{key}={value}\n")
            
            # Write back
            with open(env_file, 'w') as f:
                f.writelines(new_lines)
        
        else:
            # Create new .env
            with open(env_file, 'w') as f:
                f.write(f"TELEGRAM_BOT_TOKEN={setup.token}\n")
                f.write(f"TELEGRAM_WEBHOOK_URL={setup.webhook_url}\n")
                f.write(f"TELEGRAM_WEBHOOK_SECRET={setup.webhook_secret}\n")
        
        logger.info(f"✅ Configuration saved to {env_file}")
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("🎉 TELEGRAM SETUP COMPLETE!")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Restart your bot (python run_bot.py)")
    logger.info("2. Open Telegram and find @your_bot_username")
    logger.info("3. Send /start to test the bot")
    logger.info("4. Send a message and you should get a real AI response!")
    logger.info("")
    logger.info("📚 For more info: See TELEGRAM_REALTIME_SETUP.md")
    logger.info("")
    
    return True


async def main():
    """Main entry point."""
    try:
        success = await interactive_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
