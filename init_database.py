#!/usr/bin/env python3
"""Pre-deployment database initialization script."""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🚀 DATABASE INITIALIZATION")
    logger.info("=" * 60)
    
    try:
        from src.db_init import init_db_safe
        
        success, msg = init_db_safe()
        
        logger.info("=" * 60)
        if success:
            logger.info("✅ DATABASE READY")
        else:
            logger.error(f"⚠️ Database initialization: {msg}")
            logger.error("Note: May be retried on first startup")
        logger.info("=" * 60)
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
