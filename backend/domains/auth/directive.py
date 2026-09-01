"""Camada de Diretiva para o domínio de Autenticação (Endpoints e Dependências)."""

from typing import Annotated, Callable
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.core.security import decode_token
from backend.domains.auth import orchestration
from backend.domains.users.execution import User

router = APIRouter(prefix="/auth", tags=["auth"])
security_scheme = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    """Payload para autenticação no sistema."""

    username_or_email: str
    password: str


class RefreshRequest(BaseModel):
    """Payload para renovação de token."""

    refresh_token: str


class UserInfoResponse(BaseModel):
    """Informações resumidas do usuário autenticado."""

    id: str
    username: str
    email: str
    full_name: str | None
    is_superadmin: bool
    permissions: list[str]


class AuthResponse(BaseModel):
    """Resposta com tokens de acesso e refresh."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserInfoResponse


@router.post("/login", response_model=AuthResponse)
async def login(data: LoginRequest, session: AsyncSession = Depends(get_session)):
    """Endpoint para autenticação de usuários e geração de tokens JWT."""
    user = await orchestration.authenticate_user(session, data.username_or_email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas ou usuário inativo.",
        )
    return orchestration.login_for_access_token(user)


@router.post("/refresh", response_model=AuthResponse)
async def refresh(data: RefreshRequest, session: AsyncSession = Depends(get_session)):
    """Endpoint para renovação do access token via refresh token."""
    return await orchestration.refresh_access_token(session, data.refresh_token)


@router.post("/logout")
async def logout():
    """Endpoint de logout."""
    return {"message": "Sessão finalizada com sucesso."}


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    session: AsyncSession = Depends(get_session),
) -> User:
    """Dependência para obter o usuário autenticado atual a partir do token Bearer."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação obrigatória.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalars().first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo ou não encontrado.",
        )

    return user


def require_permission(permission_code: str) -> Callable:
    """Factory de dependência que valida se o usuário possui a permissão requerida."""

    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if not orchestration.user_has_permission(current_user, permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Acesso restrito a usuários com a permissão '{permission_code}'.",
            )
        return current_user

    return dependency


@router.get("/me", response_model=UserInfoResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Endpoint para obter os dados do perfil autenticado."""
    return UserInfoResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_superadmin=current_user.is_superadmin,
        permissions=list(orchestration.get_user_permissions(current_user)),
    )
