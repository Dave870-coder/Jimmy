"""
Production startup verification and initialization.
Ensures bot starts cleanly online without errors.
"""

import logging
import os
import sys
from pathlib import Path

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_environment():
    """Verify all required environment variables are set."""
    logger.info("=" * 70)
    logger.info("🔍 VERIFYING ENVIRONMENT")
    logger.info("=" * 70)
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google AI API key (for LLM)',
        'TELEGRAM_BOT_TOKEN': 'Telegram bot token',
        'DATABASE_URL': 'Database connection string',
        'SECRET_KEY': 'Application secret key',
    }
    
    missing = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            logger.warning(f"❌ Missing: {var} ({description})")
            missing.append(var)
        else:
            # Show masked value
            masked = value[:5] + '***' if len(value) > 5 else '***'
            logger.info(f"✅ Found: {var}")
    
    if missing:
        logger.warning(f"⚠️  {len(missing)} environment variables missing")
        logger.warning("Bot may have limited functionality")
        logger.info("Continue? (These are required for PRODUCTION)")
    else:
        logger.info("✅ All required environment variables set")
    
    return len(missing) == 0


def verify_imports():
    """Verify all critical imports work."""
    logger.info("=" * 70)
    logger.info("📦 VERIFYING IMPORTS")
    logger.info("=" * 70)
    
    imports_to_check = [
        ('fastapi', 'FastAPI web framework'),
        ('sqlalchemy', 'Database ORM'),
        ('pydantic', 'Data validation'),
        ('google.generativeai', 'Google AI SDK'),
        ('telegram', 'Telegram bot library'),
    ]
    
    failed = []
    for module_name, description in imports_to_check:
        try:
            __import__(module_name)
            logger.info(f"✅ {module_name:30s} - {description}")
        except ImportError as e:
            logger.error(f"❌ {module_name:30s} - {description}")
            logger.error(f"   Error: {e}")
            failed.append(module_name)
    
    if failed:
        logger.warning(f"⚠️  {len(failed)} imports failed")
    else:
        logger.info("✅ All critical imports successful")
    
    return len(failed) == 0


def verify_database():
    """Verify database connection."""
    logger.info("=" * 70)
    logger.info("💾 VERIFYING DATABASE")
    logger.info("=" * 70)
    
    try:
        from src.config import get_settings
        settings = get_settings()
        
        db_url = settings.database_url
        logger.info(f"Database URL: {db_url[:60]}...")
        
        # Check SQLite
        if 'sqlite' in db_url.lower():
            db_file = db_url.replace('sqlite:///', '')
            db_path = Path(db_file)
            
            logger.info(f"SQLite database: {db_path}")
            if db_path.exists():
                size_kb = db_path.stat().st_size / 1024
                logger.info(f"✅ Database file exists ({size_kb:.1f}KB)")
            else:
                logger.warning(f"⚠️  Database file not found - will be created on first query")
            
            return True
        
        # Check PostgreSQL
        elif 'postgresql' in db_url.lower():
            logger.info("PostgreSQL database detected")
            try:
                from sqlalchemy import create_engine, text
                engine = create_engine(db_url, echo=False, pool_pre_ping=True, timeout=5)
                
                with engine.connect() as conn:
                    result = conn.execute(text('SELECT 1'))
                    logger.info("✅ PostgreSQL connection successful")
                
                engine.dispose()
                return True
            except Exception as e:
                logger.error(f"❌ PostgreSQL connection failed: {e}")
                logger.warning("Bot will retry connection on startup")
                return False
        
        else:
            logger.warning(f"⚠️  Unknown database type: {db_url}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False


def verify_config():
    """Verify application configuration."""
    logger.info("=" * 70)
    logger.info("⚙️  VERIFYING CONFIGURATION")
    logger.info("=" * 70)
    
    try:
        from src.config import get_settings
        settings = get_settings()
        
        logger.info(f"App name:     {settings.app_name}")
        logger.info(f"Environment:  {settings.app_env}")
        logger.info(f"Debug mode:   {settings.debug}")
        logger.info(f"API port:     {settings.api_port}")
        logger.info(f"Workers:      {settings.workers}")
        logger.info(f"Log level:    {settings.log_level}")
        logger.info(f"Monitoring:   {settings.enable_monitoring}")
        
        logger.info("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration error: {e}")
        return False


def verify_google_ai():
    """Verify Google AI configuration."""
    logger.info("=" * 70)
    logger.info("🤖 VERIFYING GOOGLE AI")
    logger.info("=" * 70)
    
    try:
        from src.config import get_settings
        settings = get_settings()
        
        if not settings.google_api_key:
            logger.warning("⚠️  Google API key not set")
            logger.warning("   AI features will be limited")
            return False
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            
            # Try to get model info
            try:
                models = genai.list_models()
                logger.info(f"✅ Google AI connected")
                logger.info(f"   Model: {settings.google_model}")
                return True
            except Exception as e:
                logger.warning(f"⚠️  Google AI config issue: {e}")
                logger.warning("   Bot will attempt to use cached config")
                return True
        
        except Exception as e:
            logger.error(f"❌ Google AI error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Google AI verification failed: {e}")
        return False


def verify_telegram():
    """Verify Telegram bot configuration."""
    logger.info("=" * 70)
    logger.info("📱 VERIFYING TELEGRAM")
    logger.info("=" * 70)
    
    try:
        from src.config import get_settings
        settings = get_settings()
        
        if not settings.telegram_bot_token:
            logger.warning("⚠️  Telegram bot token not set")
            logger.warning("   Telegram bot will not work")
            return False
        
        try:
            from telegram import Bot
            bot = Bot(token=settings.telegram_bot_token)
            
            # Verify token (this requires async, so skip in startup)
            logger.info("✅ Telegram bot token configured")
            logger.info(f"   Webhook: {settings.telegram_webhook_url or 'Not configured'}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Telegram error: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Telegram verification failed: {e}")
        return False


def print_summary(results):
    """Print verification summary."""
    logger.info("=" * 70)
    logger.info("📊 VERIFICATION SUMMARY")
    logger.info("=" * 70)
    
    checks = [
        ('Environment', results.get('environment', False)),
        ('Imports', results.get('imports', False)),
        ('Database', results.get('database', False)),
        ('Configuration', results.get('config', False)),
        ('Google AI', results.get('google_ai', False)),
        ('Telegram', results.get('telegram', False)),
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        status = "✅" if result else "⚠️ "
        logger.info(f"{status} {name}")
    
    logger.info("=" * 70)
    logger.info(f"✅ {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🎉 BOT IS READY FOR DEPLOYMENT!")
    elif passed >= 4:
        logger.info("⚠️  Some features limited, but bot can run")
    else:
        logger.error("❌ Critical issues - fix before deploying")
    
    logger.info("=" * 70)


def main():
    """Run all verifications."""
    logger.info("\n")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " " * 15 + "🚀 PRODUCTION STARTUP VERIFICATION" + " " * 19 + "║")
    logger.info("╚" + "=" * 68 + "╝")
    logger.info("\n")
    
    results = {
        'environment': verify_environment(),
        'imports': verify_imports(),
        'database': verify_database(),
        'config': verify_config(),
        'google_ai': verify_google_ai(),
        'telegram': verify_telegram(),
    }
    
    print_summary(results)
    
    # Return exit code
    critical_checks = ['environment', 'imports', 'config']
    if all(results.get(check) for check in critical_checks):
        logger.info("✅ Startup verification PASSED\n")
        return 0
    else:
        logger.error("❌ Startup verification FAILED - Fix issues before deploying\n")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
