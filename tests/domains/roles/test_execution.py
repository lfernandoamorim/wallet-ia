"""Testes para os modelos do domínio de roles e permissões."""

import uuid
from backend.domains.roles.execution import Role, Permission, RolePermission, UserRole


def test_role_and_permission_instantiation():
    """Verifica instanciação dos modelos de Role e Permission."""
    perm = Permission(code="users.manage", description="Gerenciar usuários")
    assert perm.code == "users.manage"

    role = Role(name="admin", description="Administrador Geral", is_system=True)
    assert role.name == "admin"
    assert role.is_system is True


def test_role_permission_association():
    """Verifica associação de role com permissão."""
    role_id = uuid.uuid4()
    perm_id = uuid.uuid4()
    assoc = RolePermission(role_id=role_id, permission_id=perm_id)
    assert assoc.role_id == role_id
    assert assoc.permission_id == perm_id
