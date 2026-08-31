"""Módulo central para importação e registro de todos os modelos ORM do SQLAlchemy."""

from app.core.base_model import Base
from app.domains.users.execution import User
from app.domains.roles.execution import Role, Permission, RolePermission, UserRole
from app.domains.providers.execution import ProviderCredential
from app.domains.knowledge_bases.execution import KnowledgeBase, KBDocument, KBChunk
from app.domains.agents.execution import Agent, AgentKnowledgeBase
from app.domains.conversations.execution import Conversation, ConversationMessage, MessageAttachment, ResourceShare

__all__ = [
    "Base",
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "UserRole",
    "ProviderCredential",
    "KnowledgeBase",
    "KBDocument",
    "KBChunk",
    "Agent",
    "AgentKnowledgeBase",
    "Conversation",
    "ConversationMessage",
    "MessageAttachment",
    "ResourceShare",
]
