"""Camada de Orquestração para o domínio de Roles e Permissões (RBAC)."""

import uuid
from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.permissions import DEFAULT_USER_PERMISSIONS, PERMISSIONS_CATALOG
from app.domains.roles.execution import Permission, Role, RolePermission, UserRole
from app.domains.users.execution import User


async def seed_permissions_and_roles(session: AsyncSession) -> None:
    """Popula as permissões do catálogo e garante as roles de sistema 'admin' e 'user'."""
    # 1. Popula ou atualiza permissões
    query_perms = select(Permission)
    res_perms = await session.execute(query_perms)
    existing_perms = {p.code: p for p in res_perms.scalars().all()}

    for item in PERMISSIONS_CATALOG:
        if item["code"] not in existing_perms:
            perm = Permission(code=item["code"], description=item["description"])
            session.add(perm)
            existing_perms[item["code"]] = perm

    await session.flush()

    # 2. Garante Role 'admin' com todas as permissões
    query_admin = select(Role).where(Role.name == "admin").options(selectinload(Role.permissions))
    res_admin = await session.execute(query_admin)
    admin_role = res_admin.scalars().first()

    if not admin_role:
        admin_role = Role(
            name="admin",
            description="Administrador com acesso total ao sistema",
            is_system=True,
        )
        admin_role.permissions = list(existing_perms.values())
        session.add(admin_role)
    else:
        admin_role.permissions = list(existing_perms.values())

    # 3. Garante Role 'user' com permissões padrão
    query_user = select(Role).where(Role.name == "user").options(selectinload(Role.permissions))
    res_user = await session.execute(query_user)
    user_role = res_user.scalars().first()

    user_perms = [
        existing_perms[code] for code in DEFAULT_USER_PERMISSIONS if code in existing_perms
    ]

    if not user_role:
        user_role = Role(
            name="user",
            description="Usuário padrão com acesso básico ao chat, agentes e bases",
            is_system=True,
        )
        user_role.permissions = user_perms
        session.add(user_role)
    else:
        if not user_role.permissions:
            user_role.permissions = user_perms

    await session.commit()


async def list_permissions(session: AsyncSession) -> list[Permission]:
    """Lista todas as permissões cadastradas."""
    query = select(Permission).order_by(Permission.code)
    result = await session.execute(query)
    return list(result.scalars().all())


async def list_roles(session: AsyncSession) -> list[Role]:
    """Lista todas as roles cadastradas com suas permissões."""
    query = select(Role).options(selectinload(Role.permissions)).order_by(Role.name)
    result = await session.execute(query)
    return list(result.scalars().all())


async def get_role_by_id(session: AsyncSession, role_id: str) -> Role:
    """Busca uma role específica por ID."""
    query = select(Role).where(Role.id == role_id).options(selectinload(Role.permissions))
    result = await session.execute(query)
    role = result.scalars().first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role não encontrada.",
        )
    return role


async def create_custom_role(
    session: AsyncSession,
    name: str,
    description: str | None,
    permission_codes: list[str],
    created_by_id: str | None = None,
) -> Role:
    """Cria uma nova role personalizada com as permissões especificadas."""
    query_exist = select(Role).where(Role.name == name)
    res_exist = await session.execute(query_exist)
    if res_exist.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe uma role com o nome '{name}'.",
        )

    # Busca as permissões pelo código
    query_perms = select(Permission).where(Permission.code.in_(permission_codes))
    res_perms = await session.execute(query_perms)
    permissions = list(res_perms.scalars().all())

    new_role = Role(
        name=name,
        description=description,
        is_system=False,
        created_by=created_by_id,
        permissions=permissions,
    )
    session.add(new_role)
    await session.commit()
    await session.refresh(new_role)
    return new_role


async def update_custom_role(
    session: AsyncSession,
    role_id: str,
    name: str | None = None,
    description: str | None = None,
    permission_codes: list[str] | None = None,
) -> Role:
    """Atualiza dados e permissões de uma role."""
    role = await get_role_by_id(session, role_id)

    if role.is_system and name and name != role.name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O nome de uma role de sistema não pode ser alterado.",
        )

    if name and name != role.name:
        query_exist = select(Role).where(Role.name == name)
        res_exist = await session.execute(query_exist)
        if res_exist.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe uma role com o nome '{name}'.",
            )
        role.name = name

    if description is not None:
        role.description = description

    if permission_codes is not None:
        query_perms = select(Permission).where(Permission.code.in_(permission_codes))
        res_perms = await session.execute(query_perms)
        role.permissions = list(res_perms.scalars().all())

    await session.commit()
    await session.refresh(role)
    return role


async def delete_custom_role(session: AsyncSession, role_id: str) -> None:
    """Exclui uma role customizada (proíbe exclusão de roles de sistema)."""
    role = await get_role_by_id(session, role_id)
    if role.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Roles de sistema não podem ser excluídas.",
        )

    await session.delete(role)
    await session.commit()
