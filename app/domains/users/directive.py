"""
Módulo de diretiva para o domínio de usuários.
Contém os endpoints da API para gerenciamento de usuários.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domains.users import orchestration
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    """Esquema para criação de usuário."""
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    """Esquema para resposta com dados do usuário."""
    id: str
    email: str
    username: str

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, session: AsyncSession = Depends(get_session)):
    """
    Cria um novo usuário.
    
    Args:
        user: Dados do usuário a ser criado.
        session: Sessão do banco de dados assíncrono.
        
    Returns:
        UserResponse: Os dados do usuário criado.
    """
    created_user = await orchestration.create_user(session, user.model_dump())
    return UserResponse(
        id=str(created_user.id),
        email=created_user.email,
        username=created_user.username
    )
