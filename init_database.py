#!/usr/bin/env python3
"""Pre-deployment database initialization script."""

import os
import sys
import logging
import pathlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database with all required tables."""
    try:
        logger.info("=" * 60)
        logger.info("🚀 DATABASE INITIALIZATION SCRIPT")
        logger.info("=" * 60)
        
        from sqlalchemy import create_engine, inspect
        from src.config import get_settings
        
        # Get settings
        logger.info("Loading configuration...")
        settings = get_settings()
        logger.info(f"✅ Config loaded: {settings.app_env}")
        logger.info(f"Database URL: {settings.database_url}")
        
        sync_url = settings.database_url
        if sync_url.startswith('sqlite+'):
            sync_url = sync_url.replace('sqlite+aiosqlite:', 'sqlite:')
        
        logger.info(f"Converted URL: {sync_url}")
        
        # Create directory if needed
        if sync_url.startswith('sqlite:///'):
            db_path = sync_url.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir:
                logger.info(f"Creating database directory: {db_dir}")
                pathlib.Path(db_dir).mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Directory ready: {db_dir}")
                logger.info(f"  - Exists: {os.path.isdir(db_dir)}")
                logger.info(f"  - Readable: {os.access(db_dir, os.R_OK)}")
                logger.info(f"  - Writable: {os.access(db_dir, os.W_OK)}")
        
        # Load all models
        logger.info("Loading database models...")
        import src.database.models  # noqa
        from src.database import Base
        logger.info("✅ All models loaded")
        
        # List models
        model_names = [table.name for table in Base.metadata.tables.values()]
        logger.info(f"Models to create: {model_names}")
        
        # Create tables
        logger.info("Creating database tables...")
        sync_engine = create_engine(sync_url, echo=False)
        Base.metadata.create_all(sync_engine)
        logger.info("✅ metadata.create_all() completed")
        
        # Verify
        logger.info("Verifying tables...")
        inspector = inspect(sync_engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables created: {tables}")
        logger.info(f"Total: {len(tables)} tables")
        
        sync_engine.dispose()
        logger.info("✅ Engine disposed")
        
        if len(tables) > 0:
            logger.info("=" * 60)
            logger.info("✅ DATABASE INITIALIZATION SUCCESSFUL")
            logger.info("=" * 60)
            return True
        else:
            logger.error("=" * 60)
            logger.error("❌ DATABASE INITIALIZATION FAILED - No tables created")
            logger.error("=" * 60)
            return False
            
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ INITIALIZATION FAILED: {e}")
        logger.error("=" * 60)
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)
