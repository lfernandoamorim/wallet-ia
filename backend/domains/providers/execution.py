"""Camada de Execução para o domínio de Provedores de IA (Modelos ORM)."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.base_model import Base


class ProviderCredential(Base):
    """Modelo ORM para credenciais de provedores de IA (criptografadas)."""

    __tablename__ = "provider_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # NULL = global
    provider = Column(String, nullable=False, index=True)  # 'openrouter' | 'openai' | 'anthropic' | 'gemini'
    api_key_encrypted = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    owner = relationship("User", backref="provider_credentials")
