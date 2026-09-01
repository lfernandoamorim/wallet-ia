"""Testes para os endpoints do domínio de usuários."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app
from core.database import get_session
from domains.users.execution import User

client = TestClient(app)


@pytest.fixture(autouse=True)
def override_dependencies():
    mock_session = AsyncMock()
    app.dependency_overrides[get_session] = lambda: mock_session
    yield
    app.dependency_overrides.clear()


@patch("domains.users.orchestration.create_user")
def test_create_user(mock_create_user):
    """Testa criação de usuário com sucesso."""
    mock_user = User(
        id="123e4567-e89b-12d3-a456-426614174000",
        email="test@test.com",
        username="test",
        is_active=True,
        is_superadmin=False,
    )
    mock_user.roles = []
    mock_create_user.return_value = mock_user

    response = client.post(
        "/users/",
        json={"email": "test@test.com", "username": "test", "password": "pwd"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@test.com"
    assert data["username"] == "test"
    assert data["id"] == "123e4567-e89b-12d3-a456-426614174000"
