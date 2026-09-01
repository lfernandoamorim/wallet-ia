"""Camada de Diretiva para o domínio de Roles e Permissões (Endpoints Administrativos)."""

from typing import Annotated
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.permissions import PermissionCode
from domains.auth.directive import require_permission
from domains.roles import orchestration
from domains.users.execution import User

router = APIRouter(prefix="/admin", tags=["admin-roles"])


class PermissionResponse(BaseModel):
    """Esquema de resposta para permissão."""

    id: str
    code: str
    description: str | None


class RoleResponse(BaseModel):
    """Esquema de resposta para role."""

    id: str
    name: str
    description: str | None
    is_system: bool
    permissions: list[PermissionResponse]


class RoleCreate(BaseModel):
    """Esquema para criação de role customizada."""

    name: str
    description: str | None = None
    permission_codes: list[str] = []


class RoleUpdate(BaseModel):
    """Esquema para atualização de role."""

    name: str | None = None
    description: str | None = None
    permission_codes: list[str] | None = None


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    dependencies=[Depends(require_permission(PermissionCode.ROLES_MANAGE))],
)
async def list_permissions(session: AsyncSession = Depends(get_session)):
    """Lista todas as permissões disponíveis no sistema."""
    perms = await orchestration.list_permissions(session)
    return [
        PermissionResponse(id=str(p.id), code=p.code, description=p.description)
        for p in perms
    ]


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission(PermissionCode.ROLES_MANAGE))],
)
async def list_roles(session: AsyncSession = Depends(get_session)):
    """Lista todas as roles configuradas no sistema com suas permissões."""
    roles = await orchestration.list_roles(session)
    return [
        RoleResponse(
            id=str(r.id),
            name=r.name,
            description=r.description,
            is_system=r.is_system,
            permissions=[
                PermissionResponse(id=str(p.id), code=p.code, description=p.description)
                for p in r.permissions
            ],
        )
        for r in roles
    ]


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    data: RoleCreate,
    current_user: User = Depends(require_permission(PermissionCode.ROLES_MANAGE)),
    session: AsyncSession = Depends(get_session),
):
    """Cria uma nova role personalizada."""
    role = await orchestration.create_custom_role(
        session=session,
        name=data.name,
        description=data.description,
        permission_codes=data.permission_codes,
        created_by_id=str(current_user.id),
    )
    return RoleResponse(
        id=str(role.id),
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        permissions=[
            PermissionResponse(id=str(p.id), code=p.code, description=p.description)
            for p in role.permissions
        ],
    )


@router.get(
    "/roles/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission(PermissionCode.ROLES_MANAGE))],
)
async def get_role(role_id: str, session: AsyncSession = Depends(get_session)):
    """Obtém detalhes de uma role por ID."""
    role = await orchestration.get_role_by_id(session, role_id)
    return RoleResponse(
        id=str(role.id),
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        permissions=[
            PermissionResponse(id=str(p.id), code=p.code, description=p.description)
            for p in role.permissions
        ],
    )


@router.patch(
    "/roles/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission(PermissionCode.ROLES_MANAGE))],
)
async def update_role(
    role_id: str,
    data: RoleUpdate,
    session: AsyncSession = Depends(get_session),
):
    """Atualiza nome, descrição ou permissões de uma role."""
    role = await orchestration.update_custom_role(
        session=session,
        role_id=role_id,
        name=data.name,
        description=data.description,
        permission_codes=data.permission_codes,
    )
    return RoleResponse(
        id=str(role.id),
        name=role.name,
        description=role.description,
        is_system=role.is_system,
        permissions=[
            PermissionResponse(id=str(p.id), code=p.code, description=p.description)
            for p in role.permissions
        ],
    )


@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(PermissionCode.ROLES_MANAGE))],
)
async def delete_role(role_id: str, session: AsyncSession = Depends(get_session)):
    """Exclui uma role customizada."""
    await orchestration.delete_custom_role(session, role_id)
    return None
