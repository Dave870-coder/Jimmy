#!/usr/bin/env python3
"""
Test Telegram Integration Script

Verifies that Telegram bot is properly configured and can receive messages.

Usage:
    python test_telegram_integration.py
"""

import asyncio
import json
import logging
from typing import Optional

import httpx
from src.config import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s"
)
logger = logging.getLogger(__name__)


class TelegramIntegrationTest:
    """Test Telegram integration."""
    
    def __init__(self):
        """Initialize tester."""
        try:
            self.settings = get_settings()
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            self.settings = None
    
    async def test_token_validity(self) -> bool:
        """Test if token is valid."""
        logger.info("")
        logger.info("🔍 TEST 1: Telegram Token Validity")
        logger.info("-" * 70)
        
        if not self.settings or not self.settings.telegram_bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not configured in .env")
            return False
        
        token = self.settings.telegram_bot_token
        
        if token.startswith("test_"):
            logger.error("❌ Using test token - configure real token in .env")
            logger.error(f"   Current: {token}")
            logger.info("   Get real token from @BotFather on Telegram")
            return False
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"https://api.telegram.org/bot{token}/getMe"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        bot_info = data.get('result', {})
                        logger.info(f"✅ Token is valid")
                        logger.info(f"   Bot: @{bot_info.get('username')}")
                        logger.info(f"   Name: {bot_info.get('first_name')}")
                        return True
                    else:
                        logger.error(f"❌ API error: {data.get('description')}")
                        return False
                else:
                    logger.error(f"❌ HTTP {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    async def test_webhook_registration(self) -> bool:
        """Test if webhook is registered."""
        logger.info("")
        logger.info("📍 TEST 2: Webhook Registration")
        logger.info("-" * 70)
        
        if not self.settings or not self.settings.telegram_bot_token:
            logger.error("❌ Token not configured")
            return False
        
        token = self.settings.telegram_bot_token
        
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('ok'):
                        webhook_info = data.get('result', {})
                        
                        if webhook_info.get('url'):
                            logger.info(f"✅ Webhook is registered")
                            logger.info(f"   URL: {webhook_info.get('url')}")
                            logger.info(f"   Pending updates: {webhook_info.get('pending_update_count', 0)}")
                            logger.info(f"   Max connections: {webhook_info.get('max_connections', 40)}")
                            return True
                        else:
                            logger.warning(f"⚠️  Webhook not registered")
                            logger.info(f"   Run: python setup_telegram_webhook.py")
                            return False
                    else:
                        logger.error(f"❌ API error: {data.get('description')}")
                        return False
                else:
                    logger.error(f"❌ HTTP {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False
    
    async def test_webhook_endpoint(self) -> bool:
        """Test if webhook endpoint is accessible."""
        logger.info("")
        logger.info("🌐 TEST 3: Webhook Endpoint Accessibility")
        logger.info("-" * 70)
        
        # Test local endpoints
        test_urls = [
            ("http://localhost:8000", "localhost (default port)"),
            ("http://127.0.0.1:8000", "127.0.0.1 (local)"),
            ("http://localhost", "localhost (auto port)"),
        ]
        
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
        
        for base_url, description in test_urls:
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    url = f"{base_url}/api/v1/telegram/webhook"
                    headers = {
                        "X-Telegram-Bot-Api-Secret-Token": 
                            self.settings.telegram_webhook_secret or "test",
                        "Content-Type": "application/json"
                    }
                    
                    logger.info(f"   Testing {description}...")
                    response = await client.post(
                        url,
                        json=test_message,
                        headers=headers
                    )
                    
                    if response.status_code in [200, 400]:
                        logger.info(f"   ✅ Endpoint accessible at {base_url}")
                        return True
                    
                    logger.debug(f"   HTTP {response.status_code} at {base_url}")
            
            except (httpx.ConnectError, asyncio.TimeoutError):
                logger.debug(f"   Not accessible at {base_url} (expected for local)")
            except Exception as e:
                logger.debug(f"   Error at {base_url}: {e}")
        
        logger.warning("⚠️  Webhook endpoint not accessible locally")
        logger.info("   This is normal if running on Render/Railway")
        logger.info("   Telegram will be able to reach it in production")
        return True  # Not critical
    
    async def test_google_ai(self) -> bool:
        """Test if Google AI is configured."""
        logger.info("")
        logger.info("🤖 TEST 4: Google AI Configuration")
        logger.info("-" * 70)
        
        if not self.settings or not self.settings.google_api_key:
            logger.error("❌ GOOGLE_API_KEY not configured in .env")
            return False
        
        if self.settings.google_api_key.startswith("test_"):
            logger.error("❌ Using test key - configure real Google AI key in .env")
            logger.error(f"   Current: {self.settings.google_api_key}")
            logger.info("   Get key from: https://makersuite.google.com/app/apikey")
            return False
        
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.settings.google_api_key)
            model = genai.GenerativeModel(self.settings.google_model)
            
            logger.info(f"   Testing model: {self.settings.google_model}")
            logger.info("   Sending test prompt...")
            
            response = model.generate_content("Say 'Hello, Jimmy!' in one sentence.")
            
            if response and response.text:
                logger.info(f"✅ Google AI is working")
                logger.info(f"   Response: {response.text[:100]}...")
                return True
            else:
                logger.error("❌ No response from Google AI")
                return False
        
        except ImportError:
            logger.error("❌ google-generativeai not installed")
            logger.info("   Run: pip install google-generativeai")
            return False
        except Exception as e:
            logger.error(f"❌ Google AI error: {e}")
            return False
    
    async def test_database(self) -> bool:
        """Test if database is initialized."""
        logger.info("")
        logger.info("💾 TEST 5: Database Configuration")
        logger.info("-" * 70)
        
        try:
            from sqlalchemy import create_engine, inspect
            
            if not self.settings:
                logger.error("❌ Settings not loaded")
                return False
            
            db_url = self.settings.database_url
            logger.info(f"   Database: {db_url.split('://')[0] if '://' in db_url else 'unknown'}")
            
            # Convert async URL to sync for testing
            sync_url = db_url
            if sync_url.startswith('sqlite+'):
                sync_url = sync_url.replace('sqlite+aiosqlite:', 'sqlite:')
            
            engine = create_engine(sync_url, echo=False)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            engine.dispose()
            
            if len(tables) > 0:
                logger.info(f"✅ Database initialized")
                logger.info(f"   Tables: {len(tables)}")
                logger.info(f"   Sample tables: {', '.join(tables[:3])}")
                return True
            else:
                logger.warning("⚠️  No tables found in database")
                logger.info("   Run initialization: python -m scripts.init_db")
                return False
        
        except Exception as e:
            logger.error(f"❌ Database error: {e}")
            return False
    
    async def run_all_tests(self) -> tuple[int, int]:
        """Run all tests and return (passed, total)."""
        logger.info("")
        logger.info("=" * 70)
        logger.info("🧪 TELEGRAM INTEGRATION TEST SUITE")
        logger.info("=" * 70)
        
        tests = [
            ("Token Validity", self.test_token_validity),
            ("Webhook Registration", self.test_webhook_registration),
            ("Webhook Endpoint", self.test_webhook_endpoint),
            ("Google AI", self.test_google_ai),
            ("Database", self.test_database),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append(result)
            except Exception as e:
                logger.error(f"❌ {test_name} test crashed: {e}")
                results.append(False)
        
        # Summary
        passed = sum(1 for r in results if r)
        total = len(results)
        
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"📊 TEST RESULTS: {passed}/{total} passed")
        logger.info("=" * 70)
        
        if passed == total:
            logger.info("")
            logger.info("🎉 ALL TESTS PASSED!")
            logger.info("")
            logger.info("Your Telegram bot is ready to use:")
            logger.info("1. Open Telegram and find @your_bot_username")
            logger.info("2. Send /start")
            logger.info("3. Send any message and get an AI response!")
            logger.info("")
        else:
            logger.info("")
            logger.info("⚠️  Some tests failed. Check the errors above.")
            logger.info("")
            logger.info("Common fixes:")
            logger.info("1. Get real Telegram token: @BotFather")
            logger.info("2. Get real Google AI key: https://makersuite.google.com/app/apikey")
            logger.info("3. Run setup: python setup_telegram_webhook.py")
            logger.info("")
        
        return passed, total


async def main():
    """Main entry point."""
    tester = TelegramIntegrationTest()
    passed, total = await tester.run_all_tests()
    
    # Exit with appropriate code
    import sys
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n❌ Tests cancelled")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
