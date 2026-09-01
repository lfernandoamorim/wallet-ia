"""Módulo central para importação e registro de todos os modelos ORM do SQLAlchemy."""

from backend.core.base_model import Base
from backend.domains.users.execution import User
from backend.domains.roles.execution import Role, Permission, RolePermission, UserRole
from backend.domains.providers.execution import ProviderCredential
from backend.domains.knowledge_bases.execution import KnowledgeBase, KBDocument, KBChunk
from backend.domains.agents.execution import Agent, AgentKnowledgeBase
from backend.domains.conversations.execution import Conversation, ConversationMessage, MessageAttachment, ResourceShare

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
