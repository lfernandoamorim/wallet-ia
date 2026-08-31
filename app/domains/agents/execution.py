"""Camada de Execução para o domínio de Agentes (Modelos ORM)."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.base_model import Base


class AgentKnowledgeBase(Base):
    """Tabela de associação entre Agente e Base de Conhecimento (N:N)."""

    __tablename__ = "agent_knowledge_bases"

    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True)
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), primary_key=True)


class Agent(Base):
    """Modelo ORM representando um Agente de IA com persona."""

    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    system_prompt = Column(Text, nullable=False)  # A "persona"
    provider = Column(String, nullable=False)  # 'openrouter' | 'openai' | 'anthropic' | 'gemini'
    model = Column(String, nullable=False)  # ex: 'gpt-4o', 'claude-3-5-sonnet', 'gemini-1.5-pro'
    temperature = Column(Float, default=0.7, nullable=False)
    max_tokens = Column(Integer, nullable=True)
    visibility = Column(String, default="private", nullable=False)  # 'private' | 'shared' | 'public'
    public_slug = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    owner = relationship("User", backref="agents")
    knowledge_bases = relationship(
        "KnowledgeBase",
        secondary="agent_knowledge_bases",
        back_populates="agents",
        lazy="selectin",
    )
    conversations = relationship("Conversation", back_populates="agent")
