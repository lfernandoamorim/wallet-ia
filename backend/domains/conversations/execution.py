"""Camada de Execução para o domínio de Conversas e Mensagens (Modelos ORM)."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.base_model import Base


class Conversation(Base):
    """Modelo ORM representando uma sessão/conversa de chat."""

    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=True)
    visibility = Column(String, default="private", nullable=False)  # 'private' | 'shared' | 'public'
    public_slug = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    owner = relationship("User", backref="conversations")
    agent = relationship("Agent", back_populates="conversations", lazy="selectin")
    messages = relationship(
        "ConversationMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="ConversationMessage.created_at",
        lazy="selectin",
    )


class ConversationMessage(Base):
    """Modelo ORM representando uma mensagem dentro de uma conversa."""

    __tablename__ = "conversation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)  # 'user' | 'assistant' | 'system' | 'tool'
    content = Column(Text, nullable=True)
    tokens_input = Column(Integer, nullable=True)
    tokens_output = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
    attachments = relationship(
        "MessageAttachment",
        back_populates="message",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class MessageAttachment(Base):
    """Modelo ORM para arquivos anexados a mensagens de chat."""

    __tablename__ = "message_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("conversation_messages.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    size_bytes = Column(BigInteger, nullable=True)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    message = relationship("ConversationMessage", back_populates="attachments")


class ResourceShare(Base):
    """Modelo ORM para compartilhamento granular de recursos (conversation, agent, knowledge_base)."""

    __tablename__ = "resource_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_type = Column(String, nullable=False)  # 'conversation' | 'agent' | 'knowledge_base'
    resource_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    shared_with = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission = Column(String, default="view", nullable=False)  # 'view' | 'edit'
    shared_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", foreign_keys=[shared_with], backref="shared_resources")

    __table_args__ = (
        UniqueConstraint("resource_type", "resource_id", "shared_with", name="uq_resource_share"),
    )
