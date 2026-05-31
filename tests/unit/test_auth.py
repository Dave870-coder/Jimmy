"""Unit tests for authentication."""

import pytest
from src.security.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password_123"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_token_creation_and_verification():
    """Test JWT token creation and verification."""
    data = {"sub": "test_user_id"}
    token = create_access_token(data)
    
    payload = verify_token(token)
    assert payload is not None
    assert payload.get("sub") == "test_user_id"


def test_invalid_token():
    """Test verification of invalid token."""
    payload = verify_token("invalid_token")
    assert payload is None
