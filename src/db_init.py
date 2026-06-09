#!/usr/bin/env python3
"""
Production-ready database initialization helper
Used by both init_database.py and src/main.py
"""

import os
import sys
import logging
import pathlib
import shutil
from typing import Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db_safe() -> Tuple[bool, str]:
    """
    Safe database initialization - returns (success, status_message)
    This is the core initialization used everywhere
    Production-tested for Render environment
    """
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            from sqlalchemy import create_engine, inspect
            from src.config import get_settings
            import src.database.models  # noqa - Load all models
            from src.database import Base
            
            if attempt > 0:
                logger.info(f"🔄 Retry attempt {attempt}/{max_retries - 1}")
            
            settings = get_settings()
            sync_url = settings.database_url
            
            # Convert async URL to sync
            if sync_url.startswith('sqlite+'):
                sync_url = sync_url.replace('sqlite+aiosqlite:', 'sqlite:')
            
            logger.info(f"🔧 Database URL: {sync_url}")
            
            # Ensure directory exists and is writable for SQLite
            if sync_url.startswith('sqlite:///'):
                db_path = sync_url.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_path)
                
                if db_dir:
                    logger.info(f"📁 Creating/verifying directory: {db_dir}")
                    
                    try:
                        pathlib.Path(db_dir).mkdir(parents=True, exist_ok=True)
                        logger.info(f"✅ Directory created: {db_dir}")
                        
                        # Verify directory is writable
                        test_file = os.path.join(db_dir, ".write_test")
                        try:
                            with open(test_file, 'w') as f:
                                f.write("test")
                            os.remove(test_file)
                            logger.info(f"✅ Directory is writable")
                        except PermissionError:
                            logger.error(f"❌ Directory is NOT writable: {db_dir}")
                            return False, "directory_not_writable"
                            
                    except Exception as e:
                        logger.error(f"❌ Failed to create directory: {e}")
                        return False, f"mkdir_failed: {str(e)[:30]}"
                
                # Check disk space
                if os.path.exists(db_dir or "/opt/data"):
                    stat = shutil.disk_usage(db_dir or "/opt/data")
                    free_mb = stat.free / (1024 * 1024)
                    logger.info(f"💾 Free disk space: {free_mb:.1f} MB")
                    if free_mb < 10:
                        logger.warning(f"⚠️  Low disk space: {free_mb:.1f} MB")
            
            # Create engine with proper settings
            logger.info("📦 Creating database tables...")
            
            connection_args = {
                "timeout": 15,
                "check_same_thread": False,
            }
            
            engine = create_engine(
                sync_url, 
                echo=False,
                connect_args=connection_args,
                pool_pre_ping=True,
            )
            
            # List models to create
            models_to_create = [t.name for t in Base.metadata.tables.values()]
            logger.info(f"📋 Models to create: {len(models_to_create)} tables")
            
            if len(models_to_create) == 0:
                logger.warning("⚠️ No models found!")
                return False, "no_models"
            
            # Create all tables
            logger.info(f"🔨 Calling metadata.create_all()...")
            Base.metadata.create_all(engine)
            logger.info("✅ metadata.create_all() completed")
            
            # Verify tables were actually created
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"✅ Tables found: {len(tables)}")
            
            if tables:
                logger.info(f"   Tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
            
            engine.dispose()
            
            if len(tables) > 0:
                logger.info(f"✅ Database initialization SUCCESS: {len(tables)} tables ready")
                return True, "ready"
            else:
                logger.warning("⚠️ No tables found after metadata.create_all()")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying...")
                    continue
                return False, "no_tables_created"
                
        except Exception as e:
            logger.error(f"❌ Database init failed (attempt {attempt + 1}/{max_retries}): {e}")
            import traceback
            logger.error(traceback.format_exc())
            
            if attempt < max_retries - 1:
                import time
                time.sleep(1)  # Wait before retry
                continue
            
            return False, f"error: {str(e)[:50]}"
    
    return False, "max_retries_exceeded"

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
