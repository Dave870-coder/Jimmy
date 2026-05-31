"""Database models for the AI Bot Platform."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from src.database import Base


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = String(36, primary_key=True)
    username = String(255, unique=True, nullable=False, index=True)
    email = String(255, unique=True, nullable=False, index=True)
    password_hash = String(255, nullable=False)
    first_name = String(255)
    last_name = String(255)
    avatar_url = String(512)
    is_active = Boolean(default=True)
    is_admin = Boolean(default=False)
    telegram_user_id = String(255, unique=True, nullable=True)
    whatsapp_phone = String(50, unique=True, nullable=True)
    created_at = DateTime(timezone=True, server_default=func.now())
    updated_at = DateTime(timezone=True, onupdate=func.now())
    last_login = DateTime(timezone=True, nullable=True)

    # Relationships
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_email", "email"),
        Index("idx_telegram_user_id", "telegram_user_id"),
        Index("idx_whatsapp_phone", "whatsapp_phone"),
    )


class Message(Base):
    """Message model for storing conversations."""

    __tablename__ = "messages"

    id = String(36, primary_key=True)
    user_id = String(36, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Text(nullable=False)
    message_type = String(50)  # text, voice, image, document
    source = String(50)  # telegram, whatsapp, api
    source_message_id = String(255)
    response = Text(nullable=True)
    ai_model = String(100)
    tokens_used = Integer(default=0)
    confidence_score = Float(nullable=True)
    is_learning = Boolean(default=False)
    created_at = DateTime(timezone=True, server_default=func.now())
    updated_at = DateTime(timezone=True, onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="messages")

    __table_args__ = (
        Index("idx_user_id_created", "user_id", "created_at"),
        Index("idx_source", "source"),
    )


class Memory(Base):
    """Memory model for storing user memories."""

    __tablename__ = "memories"

    id = String(36, primary_key=True)
    user_id = String(36, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = String(255, nullable=False)
    content = Text(nullable=False)
    memory_type = String(50)  # fact, preference, relationship, context
    category = String(100)
    importance = Integer(default=5)  # 1-10
    embedding_id = String(255)  # Reference to vector DB
    tags = String(500)  # Comma-separated
    created_at = DateTime(timezone=True, server_default=func.now())
    updated_at = DateTime(timezone=True, onupdate=func.now())
    last_accessed = DateTime(timezone=True, nullable=True)
    access_count = Integer(default=0)

    # Relationships
    user = relationship("User", back_populates="memories")

    __table_args__ = (
        Index("idx_user_id_type", "user_id", "memory_type"),
        Index("idx_category", "category"),
    )


class Document(Base):
    """Document model for uploaded documents."""

    __tablename__ = "documents"

    id = String(36, primary_key=True)
    user_id = String(36, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = String(255, nullable=False)
    file_type = String(50)  # pdf, docx, txt, md
    file_size = Integer()
    file_path = String(512)
    s3_key = String(512)
    document_type = String(100)
    content_preview = Text()
    embedding_id = String(255)  # Reference to vector DB
    is_indexed = Boolean(default=False)
    created_at = DateTime(timezone=True, server_default=func.now())
    updated_at = DateTime(timezone=True, onupdate=func.now())

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_is_indexed", "is_indexed"),
    )


class Embedding(Base):
    """Embedding model for vector storage."""

    __tablename__ = "embeddings"

    id = String(36, primary_key=True)
    user_id = String(36, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    content = Text(nullable=False)
    embedding_type = String(50)  # memory, document, message
    reference_id = String(255)  # Foreign key to memory, document, or message
    model = String(100)
    vector_id = String(255)  # Reference to ChromaDB
    created_at = DateTime(timezone=True, server_default=func.now())

    __table_args__ = (
        Index("idx_reference_id", "reference_id"),
        Index("idx_user_id", "user_id"),
    )


class Workflow(Base):
    """Workflow model for task automation."""

    __tablename__ = "workflows"

    id = String(36, primary_key=True)
    user_id = String(36, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = String(255, nullable=False)
    description = Text()
    trigger_type = String(100)  # manual, scheduled, event-based
    trigger_config = Text()  # JSON configuration
    actions = Text()  # JSON array of actions
    is_active = Boolean(default=True)
    created_at = DateTime(timezone=True, server_default=func.now())
    updated_at = DateTime(timezone=True, onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="workflows")

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_is_active", "is_active"),
    )


class Task(Base):
    """Task model for workflow execution."""

    __tablename__ = "tasks"

    id = String(36, primary_key=True)
    workflow_id = String(36, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    user_id = String(36, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = String(255, nullable=False)
    status = String(50, default="pending")  # pending, running, completed, failed
    scheduled_time = DateTime(timezone=True, nullable=True)
    execution_time = DateTime(timezone=True, nullable=True)
    completed_time = DateTime(timezone=True, nullable=True)
    result = Text()
    error_message = Text()
    retry_count = Integer(default=0)
    created_at = DateTime(timezone=True, server_default=func.now())
    updated_at = DateTime(timezone=True, onupdate=func.now())

    __table_args__ = (
        Index("idx_user_id_status", "user_id", "status"),
        Index("idx_scheduled_time", "scheduled_time"),
    )


class Feedback(Base):
    """Feedback model for learning."""

    __tablename__ = "feedback"

    id = String(36, primary_key=True)
    user_id = String(36, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_id = String(255, nullable=True)
    rating = Integer()  # 1-5 stars or thumbs up/down
    feedback_type = String(50)  # positive, negative, neutral
    comment = Text()
    improvement_suggestion = Text()
    created_at = DateTime(timezone=True, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="feedback")

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_message_id", "message_id"),
    )


class Analytics(Base):
    """Analytics model for metrics."""

    __tablename__ = "analytics"

    id = String(36, primary_key=True)
    user_id = String(36, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    event_type = String(100)
    event_data = Text()  # JSON
    date = DateTime(timezone=True, server_default=func.now())

    __table_args__ = (
        Index("idx_user_id_date", "user_id", "date"),
        Index("idx_event_type", "event_type"),
    )


class Settings(Base):
    """User settings model."""

    __tablename__ = "settings"

    id = String(36, primary_key=True)
    user_id = String(36, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme = String(50, default="light")
    language = String(50, default="en")
    timezone = String(100, default="UTC")
    notifications_enabled = Boolean(default=True)
    email_notifications = Boolean(default=True)
    sms_notifications = Boolean(default=False)
    auto_learning_enabled = Boolean(default=True)
    model_preference = String(100)
    max_memory_items = Integer(default=1000)
    created_at = DateTime(timezone=True, server_default=func.now())
    updated_at = DateTime(timezone=True, onupdate=func.now())

    __table_args__ = (
        Index("idx_user_id", "user_id"),
    )


class AuditLog(Base):
    """Audit log for security and compliance."""

    __tablename__ = "audit_logs"

    id = String(36, primary_key=True)
    user_id = String(36, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    action = String(255)
    resource_type = String(100)
    resource_id = String(255)
    changes = Text()  # JSON of changes
    ip_address = String(50)
    user_agent = String(512)
    status = String(50)  # success, failure
    error_message = Text()
    created_at = DateTime(timezone=True, server_default=func.now())

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_resource_type_id", "resource_type", "resource_id"),
        Index("idx_created_at", "created_at"),
    )
