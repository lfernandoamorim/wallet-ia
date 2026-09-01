"""Camada de Diretiva para o domínio de Usuários (Endpoints da API)."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.permissions import PermissionCode
from domains.auth.directive import get_current_user, require_permission
from domains.roles.execution import Role
from domains.users import orchestration
from domains.users.execution import User

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


class UserRoleUpdate(BaseModel):
    """Esquema para atualização direta de roles de um usuário."""

    roles: list[str]  # Lista de IDs ou nomes de roles


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


def _to_user_response(u: User) -> UserResponse:
    return UserResponse(
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


@router.get("/users/me", response_model=UserResponse)
async def get_user_me(current_user: User = Depends(get_current_user)):
    """Endpoint para retornar os dados completos do usuário logado."""
    return _to_user_response(current_user)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, session: AsyncSession = Depends(get_session)):
    """Cria um novo usuário."""
    created_user = await orchestration.create_user(session, user.model_dump())
    return _to_user_response(created_user)


@router.get(
    "/users",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permission(PermissionCode.USERS_MANAGE))],
)
@router.get(
    "/admin/users",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permission(PermissionCode.USERS_MANAGE))],
)
async def list_users_admin(session: AsyncSession = Depends(get_session)):
    """Lista todos os usuários cadastrados no sistema."""
    users = await orchestration.list_users(session)
    return [_to_user_response(u) for u in users]


@router.post(
    "/admin/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.USERS_MANAGE))],
)
async def create_user_admin(user: UserCreate, session: AsyncSession = Depends(get_session)):
    """Cria um novo usuário pelo painel administrativo com roles definidas."""
    created_user = await orchestration.create_user(session, user.model_dump())
    return _to_user_response(created_user)


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission(PermissionCode.USERS_MANAGE))],
)
async def get_user_by_id_endpoint(user_id: str, session: AsyncSession = Depends(get_session)):
    """Obtém detalhes de um usuário específico."""
    user = await orchestration.get_user_by_id(session, user_id)
    return _to_user_response(user)


@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission(PermissionCode.USERS_MANAGE))],
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
    """Atualiza dados, roles, status ativo/inativo ou senha de um usuário."""
    user = await orchestration.update_user(session, user_id, data.model_dump(exclude_unset=True))
    return _to_user_response(user)


@router.put(
    "/users/{user_id}/roles",
    response_model=UserResponse,
    dependencies=[Depends(require_permission(PermissionCode.USERS_MANAGE))],
)
async def update_user_roles_endpoint(
    user_id: str,
    data: UserRoleUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Atualiza a lista de roles atribuídas a um usuário."""
    # data.roles pode conter nomes ou IDs de roles
    res_roles = await session.execute(
        select(Role).where((Role.name.in_(data.roles)) | (Role.id.in_(data.roles)))
    )
    found_roles = list(res_roles.scalars().all())
    role_ids = [str(r.id) for r in found_roles]

    user = await orchestration.update_user(session, user_id, {"role_ids": role_ids})
    return _to_user_response(user)
