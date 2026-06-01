"""Database configuration and utilities."""

from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import get_settings

settings = get_settings()

# Handle both SQLite and PostgreSQL
database_url = settings.database_url

if database_url.startswith("sqlite:///"):
    sqlite_path = Path(database_url.replace("sqlite:///", "", 1))
    if sqlite_path.as_posix() != ":memory:":
        sqlite_path.parent.mkdir(parents=True, exist_ok=True)

if database_url.startswith("sqlite://"):
    # SQLite with aiosqlite for async support
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite:///")
    engine = create_async_engine(
        database_url,
        echo=settings.database_echo,
        pool_pre_ping=False,
        connect_args={"timeout": 30},
    )
else:
    # PostgreSQL - convert to async
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(
        database_url,
        echo=settings.database_echo,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
    )

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
