"""Testes para a orquestração do domínio de roles e permissões."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from domains.roles.execution import Role, Permission
from domains.roles.orchestration import (
    seed_permissions_and_roles,
    create_custom_role,
    delete_custom_role,
)
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_seed_permissions_and_roles():
    """Testa seed inicial de permissões e roles padrão."""
    session = AsyncMock()
    mock_result_empty = MagicMock()
    mock_result_empty.scalars().all.return_value = []
    mock_result_empty.scalars().first.return_value = None
    session.execute.return_value = mock_result_empty

    await seed_permissions_and_roles(session)
    assert session.commit.called


@pytest.mark.asyncio
async def test_delete_system_role_raises_error():
    """Testa que roles de sistema não podem ser excluídas."""
    session = AsyncMock()
    system_role = Role(name="admin", is_system=True)
    
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = system_role
    session.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await delete_custom_role(session, "123e4567-e89b-12d3-a456-426614174000")
    assert exc.value.status_code == 400
    assert "não podem ser excluídas" in exc.value.detail
