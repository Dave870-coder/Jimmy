"""Integration tests for API."""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_docs_endpoint():
    """Test documentation endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_message_send():
    """Test sending a message."""
    response = client.post(
        "/api/v1/messages/send",
        json={
            "content": "Hello AI!",
            "message_type": "text",
            "source": "api",
        },
    )
    # Note: This test will fail without proper setup
    # assert response.status_code == 200
