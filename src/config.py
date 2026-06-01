"""Configuration management for the AI Bot Platform."""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "AI Bot Platform"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "your-secret-key-change-in-production"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_version: str = "v1"

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/aibot_db"
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_ttl: int = 3600
    redis_enabled: bool = False

    # JWT
    jwt_secret_key: str = "your-jwt-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 7

    # Telegram
    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""
    telegram_webhook_path: str = "/api/v1/telegram/webhook"
    telegram_webhook_secret: str = ""

    # Public deployment URL
    public_base_url: str = ""

    # WhatsApp
    whatsapp_business_account_id: str = ""
    whatsapp_business_phone_number_id: str = ""
    whatsapp_api_version: str = "v18.0"
    whatsapp_access_token: str = ""
    whatsapp_webhook_verify_token: str = ""
    whatsapp_qr_timeout: int = 120
    whatsapp_qr_expiry: int = 300

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"

    # Google AI
    google_api_key: str = ""
    google_model: str = "gemini-1.5-pro"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "neural-chat"

    # Vector Database
    chroma_persist_directory: str = "./data/chroma"
    chroma_collection_name: str = "aibot_knowledge"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Twilio
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = ""

    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "AI Bot Platform"
    smtp_from_email: str = "noreply@aibot.com"

    # Monitoring
    log_level: str = "INFO"
    sentry_dsn: str = ""
    prometheus_port: int = 9090
    enable_monitoring: bool = False
    enable_metrics: bool = False
    health_check_interval: int = 60
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Database Connection Pooling
    db_pool_size: int = 10
    db_pool_recycle: int = 3600
    db_pool_pre_ping: bool = True
    db_pool_timeout: int = 30
    
    # Request Timeouts
    request_timeout: int = 30
    api_timeout: int = 60
    telegram_timeout: int = 30

    # Security
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    rate_limit_requests: int = 100
    rate_limit_period: int = 3600

    # Features
    enable_voice_support: bool = True
    enable_file_upload: bool = True
    enable_workflow_automation: bool = True
    enable_learning_system: bool = True
    max_file_size: int = 10485760  # 10MB

    # Deployment
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    gcp_project_id: Optional[str] = None
    gcp_credentials_json: Optional[str] = None

    class Config:
        """Configuration class."""

        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get application settings (cached)."""
    return Settings()
