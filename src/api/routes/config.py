"""API routes for configuration management."""

import logging
import os
from pathlib import Path
from dotenv import set_key
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/config", tags=["config"])

# Get project root for .env file
ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"


def _ensure_env_file() -> Path:
    """Create the project env file if needed."""
    ENV_FILE.touch(exist_ok=True)
    try:
        os.chmod(ENV_FILE, 0o600)
    except OSError:
        pass
    return ENV_FILE


class GoogleApiKeyRequest(BaseModel):
    """Request to configure Google API key."""
    api_key: str


@router.post("/google-api")
async def configure_google_api(request: GoogleApiKeyRequest):
    """Configure Google API key for AI responses."""
    if not request.api_key or not request.api_key.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google API key is required",
        )
    
    try:
        # Validate API key format (basic check)
        api_key = request.api_key.strip()
        
        if len(api_key) < 20:
            raise ValueError("API key appears to be invalid (too short)")
        
        # Save to .env file
        _ensure_env_file()
        set_key(str(ENV_FILE), "GOOGLE_API_KEY", api_key, quote_mode="never")
        
        # Update current environment
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Clear settings cache to reload from env
        from src.config import get_settings
        get_settings.cache_clear()
        
        logger.info("✅ Google API key configured successfully")
        
        return {
            "ok": True,
            "message": "Google API key configured successfully!",
            "key_preview": f"{api_key[:4]}...{api_key[-4:]}",
        }
    except Exception as e:
        logger.error(f"❌ Failed to configure Google API: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure Google API: {str(e)}",
        )


@router.get("/google-api/status")
async def google_api_status():
    """Check if Google API key is configured."""
    from src.config import get_settings
    
    settings = get_settings()
    is_configured = bool(settings.google_api_key and settings.google_api_key.strip())
    
    return {
        "ok": True,
        "configured": is_configured,
        "key_preview": f"{settings.google_api_key[:4]}...{settings.google_api_key[-4:]}" if is_configured else None,
        "model": settings.google_model,
    }
