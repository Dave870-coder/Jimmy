#!/usr/bin/env python
"""
Quick startup script for the AI Bot Platform.
Starts the FastAPI server without requiring Docker, PostgreSQL, or complex setup.
"""

import os
import sys
import logging
from importlib.util import find_spec
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are installed."""
    required = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "telegram",
        "google.generativeai",
    ]
    
    missing = []
    for package in required:
        try:
            if find_spec(package) is None:
                raise ImportError(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        logger.error(f"❌ Missing packages: {', '.join(missing)}")
        logger.info(f"Install with: pip install {' '.join(missing)}")
        return False
    
    logger.info("✅ All dependencies installed")
    return True


def setup_environment():
    """Setup environment variables."""
    env_file = project_root / ".env"
    
    if not env_file.exists():
        logger.warning(f"⚠️  .env file not found. Creating from template...")
        env_example = project_root / ".env.example"
        if env_example.exists():
            with open(env_example) as src:
                content = src.read()
            with open(env_file, "w") as dst:
                dst.write(content)
            logger.info(f"✅ Created .env file")
        else:
            logger.error("❌ No .env or .env.example found")
            return False
    
    # Load .env
    from dotenv import load_dotenv
    load_dotenv(env_file)
    logger.info("✅ Environment variables loaded")
    
    return True


def check_google_api():
    """Check if Google API key is configured."""
    from src.config import get_settings
    settings = get_settings()
    
    if not settings.google_api_key or settings.google_api_key == "your-google-api-key-here":
        logger.warning("⚠️  Google API key not configured")
        logger.info("   Get one from: https://makersuite.google.com/app/apikey")
        logger.info("   Set GOOGLE_API_KEY in .env file")
    else:
        logger.info("✅ Google API key configured")


def check_telegram():
    """Check if Telegram bot is configured."""
    from src.config import get_settings
    settings = get_settings()
    
    if not settings.telegram_bot_token or settings.telegram_bot_token == "your-telegram-bot-token-here":
        logger.warning("⚠️  Telegram bot token not configured")
        logger.info("   Get one from @BotFather on Telegram")
        logger.info("   Set TELEGRAM_BOT_TOKEN in .env file")
    else:
        logger.info("✅ Telegram bot token configured")


def print_startup_info():
    """Print startup information."""
    settings = get_settings()
    
    logger.info("\n" + "="*60)
    logger.info("🚀 AI Bot Platform Starting")
    logger.info("="*60)
    logger.info(f"App Name:  {settings.app_name}")
    logger.info(f"Debug:     {settings.debug}")
    logger.info(f"Host:      {settings.api_host}")
    logger.info(f"Port:      {settings.api_port}")
    logger.info(f"Database:  {settings.database_url}")
    logger.info("="*60)
    logger.info("\n📍 API Endpoints:")
    logger.info(f"   • API:      http://localhost:{settings.api_port}")
    logger.info(f"   • Docs:     http://localhost:{settings.api_port}/docs")
    logger.info(f"   • Health:   http://localhost:{settings.api_port}/health")
    logger.info("\n" + "="*60 + "\n")


def create_runtime_directories():
    """Create directories needed for local and production startup."""
    for directory in [project_root / "data", project_root / "data" / "chroma", project_root / "logs"]:
        directory.mkdir(parents=True, exist_ok=True)


def start_api_server():
    """Start the FastAPI server."""
    settings = get_settings()
    
    logger.info("Starting FastAPI server...")
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


def main():
    """Main entry point."""
    try:
        # Check dependencies
        if not check_dependencies():
            return 1
        
        # Setup environment
        if not setup_environment():
            return 1

        create_runtime_directories()
        
        # Check configuration
        print_startup_info()
        check_google_api()
        check_telegram()
        
        # Start API server
        start_api_server()
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
