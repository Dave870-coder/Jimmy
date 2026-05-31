"""Pydantic schemas for API validation."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""

    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """User update schema."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""

    id: str
    is_active: bool
    is_admin: bool
    telegram_user_id: Optional[str] = None
    whatsapp_phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# Message Schemas
class MessageCreate(BaseModel):
    """Message creation schema."""

    content: str
    message_type: str = "text"
    source: str = "api"


class MessageResponse(BaseModel):
    """Message response schema."""

    id: str
    user_id: str
    content: str
    response: Optional[str] = None
    ai_model: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Memory Schemas
class MemoryCreate(BaseModel):
    """Memory creation schema."""

    title: str
    content: str
    memory_type: str
    category: Optional[str] = None
    importance: int = Field(default=5, ge=1, le=10)
    tags: Optional[str] = None


class MemoryUpdate(BaseModel):
    """Memory update schema."""

    title: Optional[str] = None
    content: Optional[str] = None
    importance: Optional[int] = Field(None, ge=1, le=10)
    tags: Optional[str] = None


class MemoryResponse(BaseModel):
    """Memory response schema."""

    id: str
    user_id: str
    title: str
    content: str
    memory_type: str
    importance: int
    created_at: datetime
    last_accessed: Optional[datetime] = None

    class Config:
        from_attributes = True


# Document Schemas
class DocumentCreate(BaseModel):
    """Document creation schema."""

    filename: str
    file_type: str
    file_size: int


class DocumentResponse(BaseModel):
    """Document response schema."""

    id: str
    user_id: str
    filename: str
    file_type: str
    file_size: int
    is_indexed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Workflow Schemas
class WorkflowCreate(BaseModel):
    """Workflow creation schema."""

    name: str
    description: Optional[str] = None
    trigger_type: str
    trigger_config: dict
    actions: list[dict]


class WorkflowUpdate(BaseModel):
    """Workflow update schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    actions: Optional[list[dict]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(BaseModel):
    """Workflow response schema."""

    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    trigger_type: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Task Schemas
class TaskResponse(BaseModel):
    """Task response schema."""

    id: str
    workflow_id: str
    name: str
    status: str
    scheduled_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None

    class Config:
        from_attributes = True


# Feedback Schemas
class FeedbackCreate(BaseModel):
    """Feedback creation schema."""

    message_id: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    feedback_type: str
    comment: Optional[str] = None
    improvement_suggestion: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Feedback response schema."""

    id: str
    user_id: str
    rating: int
    feedback_type: str
    created_at: datetime

    class Config:
        from_attributes = True


# Auth Schemas
class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh schema."""

    refresh_token: str


# Settings Schemas
class SettingsUpdate(BaseModel):
    """Settings update schema."""

    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None


class SettingsResponse(BaseModel):
    """Settings response schema."""

    theme: str
    language: str
    timezone: str
    notifications_enabled: bool

    class Config:
        from_attributes = True


# Search Schemas
class SearchQuery(BaseModel):
    """Search query schema."""

    query: str
    search_type: str = "hybrid"  # hybrid, semantic, keyword
    limit: int = Field(default=10, ge=1, le=100)


class SearchResult(BaseModel):
    """Search result schema."""

    id: str
    title: str
    content: str
    score: float
    source_type: str  # memory, document, message


# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str
    version: str
    database: str
    redis: str
    timestamp: datetime
