"""Regression tests for admin settings persistence."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api.routes import admin as admin_routes


def test_save_settings_persists_env_values(tmp_path, monkeypatch):
    """The admin settings endpoint should write secrets to the project .env file."""
    monkeypatch.setattr(admin_routes, "ENV_FILE", tmp_path / ".env")
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    app = FastAPI()
    app.include_router(admin_routes.router)
    client = TestClient(app)

    response = client.post(
        "/api/v1/admin/settings",
        json={
            "telegram_bot_token": "token-123",
            "google_api_key": "google-key-456",
        },
    )

    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert "TELEGRAM_BOT_TOKEN=token-123" in (tmp_path / ".env").read_text()
    assert "GOOGLE_API_KEY=google-key-456" in (tmp_path / ".env").read_text()
