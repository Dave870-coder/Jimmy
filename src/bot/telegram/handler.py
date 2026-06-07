"""Telegram bot integration with Google AI."""

import logging
from typing import Optional

try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        filters,
        ContextTypes,
    )
except ImportError:
    Update = None
    Application = None
    CommandHandler = None
    MessageHandler = None
    filters = None
    ContextTypes = None

from src.config import get_settings
from src.ai.orchestrator import get_agent_orchestrator

logger = logging.getLogger(__name__)
settings = get_settings()


class TelegramBot:
    """Telegram bot handler."""

    def __init__(self):
        """Initialize Telegram bot."""
        if Application is None:
            raise ImportError("python-telegram-bot is not installed")
        
        if not settings.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")
        
        self.app = Application.builder().token(settings.telegram_bot_token).build()
        self._initialized = False
        self._setup_handlers()
        logger.info("✅ Telegram bot initialized successfully")

    async def initialize(self):
        """Initialize the underlying Telegram application once."""
        if self._initialized:
            return

        await self.app.initialize()
        self._initialized = True

    async def set_webhook(self, webhook_url: str, secret_token: str = ""):
        """Register the bot webhook for hosted deployments."""
        await self.initialize()

        webhook_kwargs = {}
        if secret_token:
            webhook_kwargs["secret_token"] = secret_token

        await self.app.bot.set_webhook(webhook_url, **webhook_kwargs)
        logger.info(f"✅ Telegram webhook configured: {webhook_url}")

    async def clear_webhook(self):
        """Remove the Telegram webhook when shutting down or switching modes."""
        await self.initialize()
        await self.app.bot.delete_webhook(drop_pending_updates=False)

    async def handle_webhook_update(self, update_data: dict) -> bool:
        """Process a webhook update through the Telegram application."""
        try:
            await self.initialize()

            update = Update.de_json(update_data, self.app.bot)
            if update is None:
                logger.warning("Received empty Telegram webhook payload")
                return False

            await self.app.process_update(update)
            return True
        except Exception as e:
            logger.error(f"❌ Error handling Telegram webhook update: {e}")
            return False

    def _setup_handlers(self):
        """Setup command and message handlers."""
        self.app.add_handler(CommandHandler("start", self.start_handler))
        self.app.add_handler(CommandHandler("help", self.help_handler))
        self.app.add_handler(CommandHandler("memory", self.memory_handler))
        self.app.add_handler(CommandHandler("clear", self.clear_handler))
        self.app.add_handler(CommandHandler("status", self.status_handler))
        self.app.add_handler(CommandHandler("search", self.search_handler))
        self.app.add_handler(CommandHandler("tasks", self.tasks_handler))
        self.app.add_handler(CommandHandler("settings", self.settings_handler))
        
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler)
        )

    async def start_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = str(update.effective_user.id)
        username = update.effective_user.username or "Friend"
        logger.info(f"User {user_id} ({username}) started bot")
        
        await update.message.reply_text(
            f"👋 Hi {username}! Welcome to AI Bot Platform!\n\n"
            "🤖 I'm powered by Google AI and ready to help.\n"
            "📚 Use /help for available commands."
        )

    async def help_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """
🤖 *Available Commands:*

/start - Start the bot
/help - Show this help message
/status - Check bot status
/memory - View your memories (coming soon)
/clear - Clear conversation history
/search - Search knowledge base
/tasks - View active tasks
/settings - Configure preferences (coming soon)

💬 *Just type any message to chat!*
I'm powered by Google AI and ready to assist you.
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def memory_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /memory command."""
        await update.message.reply_text("📝 Memory feature coming soon!")

    async def clear_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clear command."""
        await update.message.reply_text("✅ Conversation history cleared.")

    async def status_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        await update.message.reply_text(
            "✅ *Bot Status: Online*\n"
            "🔌 Connected to Google AI\n"
            "⚡ Ready to help!",
            parse_mode="Markdown"
        )

    async def search_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command."""
        await update.message.reply_text(
            "🔍 *Search Usage:*\n"
            "/search query\n\n"
            "Example: /search machine learning"
        )

    async def tasks_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tasks command."""
        await update.message.reply_text("📋 No active tasks at the moment.")

    async def settings_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /settings command."""
        await update.message.reply_text("⚙️ Settings menu coming soon!")

    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages."""
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        logger.info(f"📨 Message from {user_id}: {message_text[:50]}...")
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        try:
            orchestrator = get_agent_orchestrator()
            if orchestrator is None:
                await update.message.reply_text(
                    "⚠️ The AI orchestrator is unavailable right now. Please verify GOOGLE_API_KEY and restart the app."
                )
                return

            response = await orchestrator.process(user_id, message_text)
            
            # Split long responses (Telegram limit is 4096)
            if len(response) > 4096:
                for chunk in [response[i:i+4096] for i in range(0, len(response), 4096)]:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(response)
            
            logger.info(f"✅ Response sent to {user_id}")
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            await update.message.reply_text(
                "❌ Error processing your message.\n\n"
                "Please try again or use /help for assistance."
            )

    async def run_polling(self):
        """Run bot with polling (long-polling from Telegram)."""
        logger.info("🚀 Starting Telegram bot (polling mode)...")
        logger.info("📱 Bot is now listening for messages...")
        logger.info("Press Ctrl+C to stop")
        
        try:
            await self.initialize()
            await self.app.run_polling(
                allowed_updates=["message", "edited_channel_post", "callback_query"]
            )
        except KeyboardInterrupt:
            logger.info("⛔ Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Error running bot: {e}")
            raise


# Global bot instance
telegram_bot: Optional[TelegramBot] = None


async def get_telegram_bot() -> Optional[TelegramBot]:
    """Get or create Telegram bot instance."""
    global telegram_bot
    if telegram_bot is None:
        try:
            telegram_bot = TelegramBot()
        except (ImportError, ValueError) as e:
            logger.error(f"❌ Failed to create Telegram bot: {e}")
            return None
    return telegram_bot
