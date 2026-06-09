#!/usr/bin/env python3
"""
Production-ready database initialization helper
Used by both init_database.py and src/main.py
"""

import os
import sys
import logging
import pathlib
from typing import Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db_safe() -> Tuple[bool, str]:
    """
    Safe database initialization - returns (success, status_message)
    This is the core initialization used everywhere
    """
    try:
        from sqlalchemy import create_engine, inspect
        from src.config import get_settings
        import src.database.models  # noqa - Load all models
        from src.database import Base
        
        settings = get_settings()
        sync_url = settings.database_url
        
        # Convert async URL to sync
        if sync_url.startswith('sqlite+'):
            sync_url = sync_url.replace('sqlite+aiosqlite:', 'sqlite:')
        
        logger.info(f"🔧 Database URL: {sync_url}")
        
        # Ensure directory exists for SQLite
        if sync_url.startswith('sqlite:///'):
            db_path = sync_url.replace('sqlite:///', '')
            db_dir = os.path.dirname(db_path)
            if db_dir:
                pathlib.Path(db_dir).mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Database directory ready: {db_dir}")
        
        # Create engine and tables
        logger.info("📦 Creating database tables...")
        engine = create_engine(sync_url, echo=False, connect_args={"timeout": 15})
        
        # List models to create
        models_to_create = [t.name for t in Base.metadata.tables.values()]
        logger.info(f"📋 Models: {len(models_to_create)} tables")
        
        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("✅ Tables created/verified")
        
        # Verify
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        engine.dispose()
        
        logger.info(f"✅ Database ready: {len(tables)} tables")
        
        if len(tables) > 0:
            return True, "ready"
        else:
            logger.warning("⚠️ No tables found after creation")
            return False, "no_tables"
            
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False, f"error: {str(e)[:50]}"

def check_db_status() -> str:
    """Check database status - returns 'ready', 'not_initialized', or 'error'"""
    try:
        from sqlalchemy import create_engine, inspect, text
        from src.config import get_settings
        
        settings = get_settings()
        sync_url = settings.database_url
        
        if sync_url.startswith('sqlite+'):
            sync_url = sync_url.replace('sqlite+aiosqlite:', 'sqlite:')
        
        engine = create_engine(sync_url, echo=False, connect_args={"timeout": 5})
        
        # Try a simple query to verify connection
        with engine.connect() as conn:
            # Get table count
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if len(tables) > 5:  # We should have at least 5 tables
                return "ready"
            elif len(tables) > 0:
                logger.warning(f"⚠️ Only {len(tables)} tables found, trying to initialize")
                engine.dispose()
                success, _ = init_db_safe()
                return "ready" if success else "not_initialized"
            else:
                logger.warning("No tables found, initializing...")
                engine.dispose()
                success, _ = init_db_safe()
                return "ready" if success else "not_initialized"
                
    except Exception as e:
        logger.debug(f"Database check failed: {e}")
        return "not_initialized"

if __name__ == "__main__":
    # Direct invocation
    success, msg = init_db_safe()
    print(f"Status: {'✅ OK' if success else '❌ FAILED'} ({msg})")
    sys.exit(0 if success else 1)
