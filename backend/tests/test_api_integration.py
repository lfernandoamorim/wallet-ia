"""Testes de integração para a API da Plataforma de IA."""

import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from main import app
from core.database import get_session
from core.security import create_access_token
from domains.auth.directive import get_current_user
from domains.users.execution import User
from domains.roles.execution import Role, Permission

client = TestClient(app)


@pytest.fixture
def admin_user():
    user = User(
        id="11111111-1111-1111-1111-111111111111",
        email="admin@advance.com.br",
        username="admin",
        full_name="Administrador do Sistema",
        is_active=True,
        is_superadmin=True,
    )
    user.roles = []
    return user


@pytest.fixture
def admin_token(admin_user):
    return create_access_token({"sub": str(admin_user.id), "username": admin_user.username})


def test_health_check():
    """Testa endpoint de integridade /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_get_me_profile(admin_user, admin_token):
    """Testa endpoint /auth/me com dependência de usuário autenticado sobrescrita."""
    app.dependency_overrides[get_current_user] = lambda: admin_user
    try:
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["is_superadmin"] is True
    finally:
        app.dependency_overrides.clear()
