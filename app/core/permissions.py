"""Catálogo central de permissões do sistema RBAC."""

from enum import StrEnum


class PermissionCode(StrEnum):
    """Códigos de permissões padronizados no sistema."""

    USERS_MANAGE = "users.manage"
    ROLES_MANAGE = "roles.manage"

    CONVERSATIONS_VIEW_OWN = "conversations.view_own"
    CONVERSATIONS_VIEW_ALL = "conversations.view_all"
    CONVERSATIONS_CREATE = "conversations.create"

    AGENTS_VIEW_OWN = "agents.view_own"
    AGENTS_VIEW_ALL = "agents.view_all"
    AGENTS_CREATE = "agents.create"
    AGENTS_MANAGE_ALL = "agents.manage_all"

    KB_VIEW_OWN = "kb.view_own"
    KB_VIEW_ALL = "kb.view_all"
    KB_CREATE = "kb.create"
    KB_MANAGE_ALL = "kb.manage_all"

    SHARING_MANAGE = "sharing.manage"
    PROVIDER_CREDENTIALS_MANAGE_OWN = "provider_credentials.manage_own"
    PROVIDER_CREDENTIALS_MANAGE_GLOBAL = "provider_credentials.manage_global"
    SYSTEM_SETTINGS = "system.settings"


PERMISSIONS_CATALOG = [
    {"code": PermissionCode.USERS_MANAGE, "description": "Criar, editar, desativar usuários e atribuir roles."},
    {"code": PermissionCode.ROLES_MANAGE, "description": "Criar, editar e excluir roles customizadas e suas permissões."},
    {"code": PermissionCode.CONVERSATIONS_VIEW_OWN, "description": "Ver as próprias conversas."},
    {"code": PermissionCode.CONVERSATIONS_VIEW_ALL, "description": "Ver conversas de todos os usuários (visão administrativa)."},
    {"code": PermissionCode.CONVERSATIONS_CREATE, "description": "Criar novas conversas."},
    {"code": PermissionCode.AGENTS_VIEW_OWN, "description": "Ver os próprios agentes."},
    {"code": PermissionCode.AGENTS_VIEW_ALL, "description": "Ver agentes de todos os usuários."},
    {"code": PermissionCode.AGENTS_CREATE, "description": "Criar novos agentes."},
    {"code": PermissionCode.AGENTS_MANAGE_ALL, "description": "Editar e excluir agentes de qualquer usuário."},
    {"code": PermissionCode.KB_VIEW_OWN, "description": "Ver as próprias bases de conhecimento."},
    {"code": PermissionCode.KB_VIEW_ALL, "description": "Ver bases de conhecimento de todos os usuários."},
    {"code": PermissionCode.KB_CREATE, "description": "Criar base de conhecimento e subir documentos."},
    {"code": PermissionCode.KB_MANAGE_ALL, "description": "Editar e excluir bases de conhecimento de qualquer usuário."},
    {"code": PermissionCode.SHARING_MANAGE, "description": "Alterar visibilidade (privado/compartilhado/público) dos próprios recursos."},
    {"code": PermissionCode.PROVIDER_CREDENTIALS_MANAGE_OWN, "description": "Cadastrar a própria chave de API de provedor."},
    {"code": PermissionCode.PROVIDER_CREDENTIALS_MANAGE_GLOBAL, "description": "Cadastrar chaves globais do sistema."},
    {"code": PermissionCode.SYSTEM_SETTINGS, "description": "Acessar configurações gerais do sistema."},
]

DEFAULT_USER_PERMISSIONS = [
    PermissionCode.CONVERSATIONS_VIEW_OWN,
    PermissionCode.CONVERSATIONS_CREATE,
    PermissionCode.AGENTS_VIEW_OWN,
    PermissionCode.AGENTS_CREATE,
    PermissionCode.KB_VIEW_OWN,
    PermissionCode.KB_CREATE,
    PermissionCode.SHARING_MANAGE,
    PermissionCode.PROVIDER_CREDENTIALS_MANAGE_OWN,
]
