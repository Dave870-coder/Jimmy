#!/usr/bin/env python
"""Start the Telegram bot in polling mode."""

import asyncio
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Start the Telegram bot."""
    try:
        from src.config import get_settings
        from src.bot.telegram.handler import get_telegram_bot
        
        settings = get_settings()
        
        if not settings.telegram_bot_token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not configured in .env")
            logger.error("Please add your Telegram bot token to .env file")
            sys.exit(1)
        
        logger.info("🤖 Initializing Telegram bot...")
        bot = await get_telegram_bot()
        
        if not bot:
            logger.error("❌ Failed to initialize Telegram bot")
            sys.exit(1)
        
        logger.info("✅ Telegram bot initialized successfully!")
        logger.info("📱 Bot is now listening for messages...")
        logger.info("Press Ctrl+C to stop")
        
        # Start polling
        await bot.run_polling()
        
    except KeyboardInterrupt:
        logger.info("⛔ Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
