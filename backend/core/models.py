"""Módulo central para importação e registro de todos os modelos ORM do SQLAlchemy."""

from core.base_model import Base
from domains.users.execution import User
from domains.roles.execution import Role, Permission, RolePermission, UserRole
from domains.providers.execution import ProviderCredential
from domains.knowledge_bases.execution import KnowledgeBase, KBDocument, KBChunk
from domains.agents.execution import Agent, AgentKnowledgeBase
from domains.conversations.execution import Conversation, ConversationMessage, MessageAttachment, ResourceShare

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
