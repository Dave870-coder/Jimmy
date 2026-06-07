"""Regression tests for database URL normalization."""

from src.database import normalize_database_url


def test_normalize_database_url_uses_async_sqlite_driver() -> None:
    """SQLite URLs must convert to the async SQLite driver without extra slashes."""
    assert normalize_database_url("sqlite:///./data/bot.db") == "sqlite+aiosqlite:///./data/bot.db"


def test_normalize_database_url_preserves_postgresql_urls() -> None:
    """PostgreSQL URLs should still use the async PostgreSQL driver."""
    assert normalize_database_url("postgresql://user:pass@localhost/db") == "postgresql+asyncpg://user:pass@localhost/db"


def test_normalize_database_url_handles_case_insensitive_prefixes() -> None:
    """Database URLs should normalize even when the scheme casing differs."""
    assert normalize_database_url("POSTGRESQL://user:pass@localhost/db") == "postgresql+asyncpg://user:pass@localhost/db"
    assert normalize_database_url("SQLITE:///./data/bot.db") == "sqlite+aiosqlite:///./data/bot.db"


def test_normalize_database_url_leaves_already_normalized_urls_unchanged() -> None:
    """Already normalized async URLs should not be modified again."""
    assert normalize_database_url("sqlite+aiosqlite:///./data/bot.db") == "sqlite+aiosqlite:///./data/bot.db"
    assert normalize_database_url("postgresql+asyncpg://user:pass@localhost/db") == "postgresql+asyncpg://user:pass@localhost/db"
