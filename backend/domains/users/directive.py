"""Camada de Diretiva para o domínio de Usuários (Endpoints da API)."""

from typing import Annotated
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.core.permissions import PermissionCode
from backend.domains.auth.directive import require_permission
from backend.domains.users import orchestration

router = APIRouter(tags=["users"])


class UserCreate(BaseModel):
    """Esquema para criação de usuário."""

    email: EmailStr
    username: str
    password: str
    full_name: str | None = None
    is_superadmin: bool = False
    role_ids: list[str] = []


class UserUpdate(BaseModel):
    """Esquema para atualização de dados de usuário."""

    email: EmailStr | None = None
    username: str | None = None
    password: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    is_superadmin: bool | None = None
    role_ids: list[str] | None = None


class RoleSimpleResponse(BaseModel):
    """Esquema resumido de role."""

    id: str
    name: str


class UserResponse(BaseModel):
    """Esquema completo para resposta de usuário."""

    id: str
    email: str
    username: str
    full_name: str | None
    is_active: bool
    is_superadmin: bool
    roles: list[RoleSimpleResponse] = []


@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, session: AsyncSession = Depends(get_session)):
    """Cria um novo usuário (usado no setup ou cadastro inicial)."""
    created_user = await orchestration.create_user(session, user.model_dump())
    return UserResponse(
        id=str(created_user.id),
        email=created_user.email,
        username=created_user.username,
        full_name=created_user.full_name,
        is_active=created_user.is_active,
        is_superadmin=created_user.is_superadmin,
        roles=[
            RoleSimpleResponse(id=str(r.id), name=r.name)
            for r in (created_user.roles or [])
        ],
    )


@router.get(
    "/admin/users",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permission(PermissionCode.USERS_MANAGE))],
)
async def list_users_admin(session: AsyncSession = Depends(get_session)):
    """Lista todos os usuários cadastrados no sistema (visão administrativa)."""
    users = await orchestration.list_users(session)
    return [
        UserResponse(
            id=str(u.id),
            email=u.email,
            username=u.username,
            full_name=u.full_name,
            is_active=u.is_active,
            is_superadmin=u.is_superadmin,
            roles=[
                RoleSimpleResponse(id=str(r.id), name=r.name)
                for r in (u.roles or [])
            ],
        )
        for u in users
    ]


@router.post(
    "/admin/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.USERS_MANAGE))],
)
async def create_user_admin(user: UserCreate, session: AsyncSession = Depends(get_session)):
    """Cria um novo usuário pelo painel administrativo com roles definidas."""
    created_user = await orchestration.create_user(session, user.model_dump())
    return UserResponse(
        id=str(created_user.id),
        email=created_user.email,
        username=created_user.username,
        full_name=created_user.full_name,
        is_active=created_user.is_active,
        is_superadmin=created_user.is_superadmin,
        roles=[
            RoleSimpleResponse(id=str(r.id), name=r.name)
            for r in (created_user.roles or [])
        ],
    )


@router.patch(
    "/admin/users/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission(PermissionCode.USERS_MANAGE))],
)
async def update_user_admin(
    user_id: str,
    data: UserUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Atualiza dados, roles, status ativo/inativo ou reseta a senha de um usuário."""
    user = await orchestration.update_user(session, user_id, data.model_dump(exclude_unset=True))
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superadmin=user.is_superadmin,
        roles=[
            RoleSimpleResponse(id=str(r.id), name=r.name)
            for r in (user.roles or [])
        ],
    )
