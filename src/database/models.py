"""Database models for the AI Bot Platform."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
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

    id = Column(String(36), primary_key=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(255))
    last_name = Column(String(255))
    avatar_url = Column(String(512))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    telegram_user_id = Column(String(255), unique=True, nullable=True)
    whatsapp_phone = Column(String(50), unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

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

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(50))  # text, voice, image, document
    source = Column(String(50))  # telegram, whatsapp, api
    source_message_id = Column(String(255))
    response = Column(Text, nullable=True)
    ai_model = Column(String(100))
    tokens_used = Column(Integer, default=0)
    confidence_score = Column(Float, nullable=True)
    is_learning = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="messages")

    __table_args__ = (
        Index("idx_user_id_created", "user_id", "created_at"),
        Index("idx_source", "source"),
    )


class Memory(Base):
    """Memory model for storing user memories."""

    __tablename__ = "memories"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    memory_type = Column(String(50))  # fact, preference, relationship, context
    category = Column(String(100))
    importance = Column(Integer, default=5)  # 1-10
    embedding_id = Column(String(255))  # Reference to vector DB
    tags = Column(String(500))  # Comma-separated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    access_count = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="memories")

    __table_args__ = (
        Index("idx_user_id_type", "user_id", "memory_type"),
        Index("idx_category", "category"),
    )


class Document(Base):
    """Document model for uploaded documents."""

    __tablename__ = "documents"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50))  # pdf, docx, txt, md
    file_size = Column(Integer)
    file_path = Column(String(512))
    s3_key = Column(String(512))
    document_type = Column(String(100))
    content_preview = Column(Text)
    embedding_id = Column(String(255))  # Reference to vector DB
    is_indexed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_is_indexed", "is_indexed"),
    )


class Embedding(Base):
    """Embedding model for vector storage."""

    __tablename__ = "embeddings"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    embedding_type = Column(String(50))  # memory, document, message
    reference_id = Column(String(255))  # Foreign key to memory, document, or message
    model = Column(String(100))
    vector_id = Column(String(255))  # Reference to ChromaDB
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_reference_id", "reference_id"),
        Index("idx_user_id", "user_id"),
    )


class Workflow(Base):
    """Workflow model for task automation."""

    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    trigger_type = Column(String(100))  # manual, scheduled, event-based
    trigger_config = Column(Text)  # JSON configuration
    actions = Column(Text)  # JSON array of actions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="workflows")

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_is_active", "is_active"),
    )


class Task(Base):
    """Task model for workflow execution."""

    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    scheduled_time = Column(DateTime(timezone=True), nullable=True)
    execution_time = Column(DateTime(timezone=True), nullable=True)
    completed_time = Column(DateTime(timezone=True), nullable=True)
    result = Column(Text)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_user_id_status", "user_id", "status"),
        Index("idx_scheduled_time", "scheduled_time"),
    )


class Feedback(Base):
    """Feedback model for learning."""

    __tablename__ = "feedback"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String(255), nullable=True)
    rating = Column(Integer)  # 1-5 stars or thumbs up/down
    feedback_type = Column(String(50))  # positive, negative, neutral
    comment = Column(Text)
    improvement_suggestion = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="feedback")

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_message_id", "message_id"),
    )


class Analytics(Base):
    """Analytics model for metrics."""

    __tablename__ = "analytics"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    event_type = Column(String(100))
    event_data = Column(Text)  # JSON
    date = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_user_id_date", "user_id", "date"),
        Index("idx_event_type", "event_type"),
    )


class Settings(Base):
    """User settings model."""

    __tablename__ = "settings"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme = Column(String(50), default="light")
    language = Column(String(50), default="en")
    timezone = Column(String(100), default="UTC")
    notifications_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    auto_learning_enabled = Column(Boolean, default=True)
    model_preference = Column(String(100))
    max_memory_items = Column(Integer, default=1000)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index("idx_user_id", "user_id"),
    )


class AuditLog(Base):
    """Audit log for security and compliance."""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    action = Column(String(255))
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    changes = Column(Text)  # JSON of changes
    ip_address = Column(String(50))
    user_agent = Column(String(512))
    status = Column(String(50))  # success, failure
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_resource_type_id", "resource_type", "resource_id"),
        Index("idx_created_at", "created_at"),
    )
