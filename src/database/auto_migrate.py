"""
Automatic database migration system.
Runs migrations on startup for production deployments.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def auto_migrate_database() -> bool:
    """
    Automatically run database migrations on startup.
    Supports SQLite (dev) and PostgreSQL (production).
    """
    try:
        from src.config import get_settings
        settings = get_settings()

        logger.info("🔄 Checking database migrations...")

        # Skip migrations for SQLite in development
        if "sqlite" in settings.database_url.lower():
            logger.info("SQLite database detected - skipping migration")
            return True

        logger.info("PostgreSQL database detected - running migrations...")

        try:
            from alembic.config import Config
            from alembic.runtime.migration import MigrationContext
            from alembic.operations import Operations
            from sqlalchemy import create_engine, text, inspect

            # Create engine
            engine = create_engine(settings.database_url)

            # Check database connectivity
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("✅ Database connectivity verified")
            except Exception as e:
                logger.error(f"❌ Cannot connect to database: {e}")
                return False

            # Get inspector to check tables
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            logger.info(f"Existing tables: {existing_tables}")

            # Initialize Alembic
            alembic_cfg = Config("alembic.ini")
            alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)

            # Try to run migrations
            from alembic.command import upgrade

            upgrade(alembic_cfg, "head")
            logger.info("✅ Database migrations completed successfully")
            return True

        except ImportError:
            logger.warning("Alembic not installed - attempting manual schema creation")
            return create_schema_manually(settings.database_url)

        except Exception as e:
            logger.error(f"❌ Migration error: {e}")
            logger.warning("Continuing without migration - may cause errors")
            return False

    except Exception as e:
        logger.error(f"❌ Auto-migration failed: {e}")
        return False


def create_schema_manually(database_url: str) -> bool:
    """
    Create database schema manually if Alembic is not available.
    This is a fallback for production environments.
    """
    try:
        from sqlalchemy import create_engine, text

        logger.info("Creating database schema manually...")

        engine = create_engine(database_url)

        # Core tables that must exist
        init_sql = """
        -- Create alembic version table
        CREATE TABLE IF NOT EXISTS alembic_version (
            version_num VARCHAR(32) NOT NULL PRIMARY KEY
        );

        -- Create users table
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create conversations table
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            title VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create messages table
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            conversation_id INTEGER REFERENCES conversations(id),
            role VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create memory table
        CREATE TABLE IF NOT EXISTS memory (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            key VARCHAR(255) NOT NULL,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, key)
        );
        """

        with engine.connect() as conn:
            for statement in init_sql.split(";"):
                if statement.strip():
                    conn.execute(text(statement))
            conn.commit()

        logger.info("✅ Database schema created successfully")
        return True

    except Exception as e:
        logger.error(f"❌ Manual schema creation failed: {e}")
        return False


def verify_database_ready(database_url: str) -> bool:
    """
    Verify that the database is ready for the application.
    Returns True if database exists and is accessible.
    """
    try:
        from sqlalchemy import create_engine, text

        logger.info("Verifying database readiness...")

        engine = create_engine(database_url, pool_pre_ping=True)

        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            if result.fetchone():
                logger.info("✅ Database is ready")
                return True

        return False

    except Exception as e:
        logger.error(f"❌ Database readiness check failed: {e}")
        return False


def get_migration_status(database_url: str) -> dict:
    """
    Get current migration status.
    Returns dict with migration information.
    """
    try:
        from sqlalchemy import create_engine, text, inspect

        engine = create_engine(database_url)
        inspector = inspect(engine)

        tables = inspector.get_table_names()

        # Check for essential tables
        essential_tables = ["users", "conversations", "messages"]
        missing_tables = [t for t in essential_tables if t not in tables]

        return {
            "database_accessible": True,
            "tables": tables,
            "table_count": len(tables),
            "missing_essential_tables": missing_tables,
            "ready": len(missing_tables) == 0,
        }

    except Exception as e:
        logger.error(f"Failed to get migration status: {e}")
        return {
            "database_accessible": False,
            "error": str(e),
            "ready": False,
        }


# Export functions
__all__ = [
    "auto_migrate_database",
    "create_schema_manually",
    "verify_database_ready",
    "get_migration_status",
]
