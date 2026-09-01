"""Camada de Execução para o domínio de Base de Conhecimento e RAG (Modelos ORM)."""

import uuid
from datetime import datetime, timezone
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.base_model import Base


class KnowledgeBase(Base):
    """Modelo ORM representando uma Base de Conhecimento RAG."""

    __tablename__ = "knowledge_bases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    visibility = Column(String, default="private", nullable=False)  # 'private' | 'shared' | 'public'
    public_slug = Column(String, unique=True, nullable=True, index=True)
    embedding_model = Column(String, default="text-embedding-3-small", nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    owner = relationship("User", backref="knowledge_bases")
    documents = relationship("KBDocument", back_populates="knowledge_base", cascade="all, delete-orphan")
    chunks = relationship("KBChunk", back_populates="knowledge_base", cascade="all, delete-orphan")
    agents = relationship("Agent", secondary="agent_knowledge_bases", back_populates="knowledge_bases")


class KBDocument(Base):
    """Modelo ORM para documentos enviados à base de conhecimento."""

    __tablename__ = "kb_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # 'md' | 'docx' | 'xlsx'
    storage_path = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)  # 'pending' | 'processing' | 'ready' | 'error'
    error_message = Column(Text, nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    chunks = relationship("KBChunk", back_populates="document", cascade="all, delete-orphan")


class KBChunk(Base):
    """Modelo ORM para chunks vetorizados de documentos da base de conhecimento."""

    __tablename__ = "kb_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("kb_documents.id", ondelete="CASCADE"), nullable=False)
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    meta_info = Column("metadata", JSON, nullable=True)
    chunk_index = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    knowledge_base = relationship("KnowledgeBase", back_populates="chunks")
    document = relationship("KBDocument", back_populates="chunks")
