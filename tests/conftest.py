"""pytest configuration."""

import pytest


@pytest.fixture
def test_user_id():
    """Provide a test user ID."""
    return "test_user_123"


@pytest.fixture
def test_message():
    """Provide a test message."""
    return {
        "content": "Hello AI!",
        "message_type": "text",
        "source": "api",
    }
