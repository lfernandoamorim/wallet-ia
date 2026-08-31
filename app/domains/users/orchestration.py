"""Camada de Orquestração para o domínio de Usuários."""

import uuid
from typing import Any, TypedDict
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash
from app.domains.roles.execution import Role
from app.domains.users.execution import User


class UserCreateData(TypedDict, total=False):
    """Tipagem para criação de usuário."""

    email: str
    username: str
    password: str
    full_name: str | None
    is_superadmin: bool | None
    role_ids: list[str] | None


class UserUpdateData(TypedDict, total=False):
    """Tipagem para atualização de usuário."""

    email: str | None
    username: str | None
    full_name: str | None
    is_active: bool | None
    is_superadmin: bool | None
    password: str | None
    role_ids: list[str] | None


async def get_user_by_id(session: AsyncSession, user_id: str) -> User:
    """Busca um usuário por ID."""
    query = select(User).where(User.id == user_id).options(selectinload(User.roles))
    result = await session.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    return user


async def list_users(session: AsyncSession) -> list[User]:
    """Lista todos os usuários cadastrados."""
    query = select(User).options(selectinload(User.roles)).order_by(User.created_at.desc())
    result = await session.execute(query)
    return list(result.scalars().all())


async def create_user(session: AsyncSession, user_data: UserCreateData) -> User:
    """Cria e persiste um novo usuário no banco com hash seguro de senha."""
    # Valida duplicidade de username e email
    query_exist = select(User).where(
        or_(User.username == user_data["username"], User.email == user_data["email"])
    )
    res_exist = await session.execute(query_exist)
    existing = res_exist.scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ou nome de usuário já cadastrado.",
        )

    roles: list[Role] = []
    if "role_ids" in user_data and user_data["role_ids"]:
        query_roles = select(Role).where(Role.id.in_(user_data["role_ids"]))
        res_roles = await session.execute(query_roles)
        roles = list(res_roles.scalars().all())
    else:
        # Atribui role 'user' padrão se não informada
        query_default = select(Role).where(Role.name == "user")
        res_default = await session.execute(query_default)
        default_role = res_default.scalars().first()
        if default_role:
            roles = [default_role]

    user = User(
        email=user_data["email"],
        username=user_data["username"],
        password_hash=get_password_hash(user_data["password"]),
        full_name=user_data.get("full_name"),
        is_superadmin=user_data.get("is_superadmin", False),
        is_active=True,
        roles=roles,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(session: AsyncSession, user_id: str, user_data: UserUpdateData) -> User:
    """Atualiza dados, status, senha e roles de um usuário."""
    user = await get_user_by_id(session, user_id)

    if user_data.get("email") and user_data["email"] != user.email:
        res = await session.execute(select(User).where(User.email == user_data["email"]))
        if res.scalars().first():
            raise HTTPException(status_code=400, detail="Email já cadastrado para outro usuário.")
        user.email = user_data["email"]

    if user_data.get("username") and user_data["username"] != user.username:
        res = await session.execute(select(User).where(User.username == user_data["username"]))
        if res.scalars().first():
            raise HTTPException(status_code=400, detail="Nome de usuário já cadastrado.")
        user.username = user_data["username"]

    if "full_name" in user_data:
        user.full_name = user_data["full_name"]

    if "is_active" in user_data and user_data["is_active"] is not None:
        user.is_active = user_data["is_active"]

    if "is_superadmin" in user_data and user_data["is_superadmin"] is not None:
        user.is_superadmin = user_data["is_superadmin"]

    if user_data.get("password"):
        user.password_hash = get_password_hash(user_data["password"])

    if "role_ids" in user_data and user_data["role_ids"] is not None:
        query_roles = select(Role).where(Role.id.in_(user_data["role_ids"]))
        res_roles = await session.execute(query_roles)
        user.roles = list(res_roles.scalars().all())

    await session.commit()
    await session.refresh(user)
    return user
