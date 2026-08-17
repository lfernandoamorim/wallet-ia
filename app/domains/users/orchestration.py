"""
Módulo de orquestração para o domínio de usuários.
Contém a lógica de negócio e coordenação de fluxo para usuários.
"""

from typing import TypedDict
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.users.execution import User

class UserData(TypedDict):
    """Tipagem para os dados de criação de usuário."""
    email: str
    username: str
    password: str

async def create_user(session: AsyncSession, user_data: UserData) -> User:
    """
    Cria e persiste um novo usuário no banco de dados.
    
    Implementação inicial básica. O hash de senha ainda é um mock
    que deverá ser substituído por um algoritmo real futuramente.
    
    Args:
        session: Sessão do banco de dados assíncrono.
        user_data: Dicionário contendo email, username e password.
        
    Returns:
        User: A entidade de usuário criada e persistida.
    """
    user = User(
        email=user_data["email"],
        username=user_data["username"],
        password_hash=user_data["password"] + "_hashed"  # FIXME: Hash mockado temporariamente
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
