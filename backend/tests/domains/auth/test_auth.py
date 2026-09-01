"""Testes para o domínio de autenticação (login, tokens, current_user)."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from domains.auth.orchestration import authenticate_user, login_for_access_token, refresh_access_token
from domains.users.execution import User
from core.security import get_password_hash, create_refresh_token


@pytest.mark.asyncio
async def test_authenticate_user_success():
    """Testa autenticação de usuário com credenciais válidas."""
    session = AsyncMock()
    user = User(
        email="admin@advance.com.br",
        username="admin",
        password_hash=get_password_hash("senha123"),
        is_active=True,
        is_superadmin=True,
    )
    
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = user
    session.execute.return_value = mock_result

    auth_user = await authenticate_user(session, "admin", "senha123")
    assert auth_user is not None
    assert auth_user.username == "admin"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    """Testa falha de autenticação com senha incorreta."""
    session = AsyncMock()
    user = User(
        email="admin@advance.com.br",
        username="admin",
        password_hash=get_password_hash("senha123"),
        is_active=True,
    )
    
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = user
    session.execute.return_value = mock_result

    auth_user = await authenticate_user(session, "admin", "senhaerrada")
    assert auth_user is None


@pytest.mark.asyncio
async def test_login_and_refresh():
    """Testa geração de tokens no login e renovação via refresh token."""
    user = User(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="admin@advance.com.br",
        username="admin",
        is_active=True,
        is_superadmin=True,
    )
    
    tokens = login_for_access_token(user)
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"

    session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars().first.return_value = user
    session.execute.return_value = mock_result

    new_tokens = await refresh_access_token(session, tokens["refresh_token"])
    assert "access_token" in new_tokens
    assert new_tokens["access_token"] is not None
