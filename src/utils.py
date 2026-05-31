"""Utility functions for the application."""

import uuid
from datetime import datetime


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat()


def parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp string."""
    return datetime.fromisoformat(ts)


def paginate(items: list, page: int = 1, page_size: int = 10) -> dict:
    """Paginate a list of items."""
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "items": items[start:end],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
    }


def merge_dicts(dict1: dict, dict2: dict) -> dict:
    """Merge two dictionaries."""
    result = dict1.copy()
    result.update(dict2)
    return result


def truncate_string(s: str, length: int = 100, suffix: str = "...") -> str:
    """Truncate string to specified length."""
    if len(s) <= length:
        return s
    return s[:length - len(suffix)] + suffix
