"""Camada de Diretiva para o domínio de Provedores de IA (Endpoints REST)."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_session
from backend.core.permissions import PermissionCode
from backend.domains.auth.directive import get_current_user
from backend.domains.auth.orchestration import user_has_permission
from backend.domains.providers import orchestration
from backend.domains.users.execution import User

router = APIRouter(prefix="/provider-credentials", tags=["provider-credentials"])


class ProviderCredentialCreate(BaseModel):
    """Esquema para criação de credencial de provedor."""

    provider: str  # 'openrouter' | 'openai' | 'anthropic' | 'gemini'
    api_key: str
    is_global: bool = False  # Se verdadeiro, requer permissão provider_credentials.manage_global


class ProviderCredentialResponse(BaseModel):
    """Esquema de resposta de credencial sem expor o segredo."""

    id: str
    provider: str
    is_global: bool
    is_active: bool
    created_at: str


@router.get("/", response_model=list[ProviderCredentialResponse])
async def list_credentials_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Lista as credenciais de provedor de IA disponíveis."""
    is_admin = user_has_permission(current_user, PermissionCode.PROVIDER_CREDENTIALS_MANAGE_GLOBAL)
    creds = await orchestration.list_credentials(session, str(current_user.id), is_admin=is_admin)
    return [
        ProviderCredentialResponse(
            id=str(c.id),
            provider=c.provider,
            is_global=c.owner_id is None,
            is_active=c.is_active,
            created_at=c.created_at.isoformat(),
        )
        for c in creds
    ]


@router.post("/", response_model=ProviderCredentialResponse, status_code=status.HTTP_201_CREATED)
async def create_credential_endpoint(
    data: ProviderCredentialCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Cadastra uma nova chave de API de provedor de IA (própria ou global)."""
    owner_id: str | None = str(current_user.id)
    if data.is_global:
        if not user_has_permission(current_user, PermissionCode.PROVIDER_CREDENTIALS_MANAGE_GLOBAL):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem cadastrar credenciais globais.",
            )
        owner_id = None
    else:
        if not user_has_permission(current_user, PermissionCode.PROVIDER_CREDENTIALS_MANAGE_OWN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão para gerenciar credenciais próprias não concedida.",
            )

    cred = await orchestration.create_credential(
        session=session,
        provider=data.provider,
        api_key=data.api_key,
        owner_id=owner_id,
    )
    return ProviderCredentialResponse(
        id=str(cred.id),
        provider=cred.provider,
        is_global=cred.owner_id is None,
        is_active=cred.is_active,
        created_at=cred.created_at.isoformat(),
    )


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential_endpoint(
    credential_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Exclui uma credencial cadastrada."""
    is_admin = user_has_permission(current_user, PermissionCode.PROVIDER_CREDENTIALS_MANAGE_GLOBAL)
    await orchestration.delete_credential(
        session=session,
        credential_id=credential_id,
        user_id=str(current_user.id),
        is_admin=is_admin,
    )
    return None
