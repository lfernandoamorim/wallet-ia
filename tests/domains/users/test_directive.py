from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.core.database import get_session
from app.domains.users.execution import User

# Criar um mock assíncrono para o session
async def override_get_session():
    mock_session = AsyncMock()
    # Mock do return type de orchestration.create_user para ser compativel com o return do router.
    # Mas como orchestration tenta criar um User real e fazer commit, o mock_session.add e commit 
    # não vao dar erro.
    yield mock_session

app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={
        "email": "test@test.com", 
        "username": "test", 
        "password": "pwd"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@test.com"
    assert data["username"] == "test"
