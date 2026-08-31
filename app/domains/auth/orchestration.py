"""Camada de Orquestração para o domínio de Autenticação."""

from typing import Any
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.domains.users.execution import User


def get_user_permissions(user: User) -> set[str]:
    """Retorna o conjunto de códigos de permissões ativas que o usuário possui."""
    if user.is_superadmin:
        # Superadmin possui acesso irrestrito / todas as permissões
        from app.core.permissions import PERMISSIONS_CATALOG
        return {p["code"] for p in PERMISSIONS_CATALOG}

    perms: set[str] = set()
    if hasattr(user, "roles") and user.roles:
        for role in user.roles:
            if hasattr(role, "permissions") and role.permissions:
                for perm in role.permissions:
                    perms.add(perm.code)
    return perms


def user_has_permission(user: User, permission_code: str) -> bool:
    """Verifica se o usuário possui determinada permissão."""
    if not user.is_active:
        return False
    if user.is_superadmin:
        return True
    perms = get_user_permissions(user)
    return permission_code in perms


async def authenticate_user(session: AsyncSession, username_or_email: str, password: str) -> User | None:
    """Autentica o usuário por email ou username e valida a senha."""
    query = select(User).where(
        or_(User.username == username_or_email, User.email == username_or_email)
    )
    result = await session.execute(query)
    user = result.scalars().first()

    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def login_for_access_token(user: User) -> dict[str, Any]:
    """Gera o par de tokens JWT de acesso e refresh."""
    user_id_str = str(user.id)
    token_data = {
        "sub": user_id_str,
        "username": user.username,
        "email": user.email,
        "is_superadmin": user.is_superadmin,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": user_id_str})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user_id_str,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_superadmin": user.is_superadmin,
            "permissions": list(get_user_permissions(user)),
        },
    }


async def refresh_access_token(session: AsyncSession, refresh_token: str) -> dict[str, Any]:
    """Valida o refresh token e emite um novo access token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado.",
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

    return login_for_access_token(user)
