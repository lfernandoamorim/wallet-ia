"""Camada de Diretiva para o domínio de Agentes de IA (Endpoints REST)."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.permissions import PermissionCode
from app.domains.agents import orchestration
from app.domains.agents.execution import Agent
from app.domains.auth.directive import get_current_user
from app.domains.auth.orchestration import user_has_permission
from app.domains.users.execution import User

router = APIRouter(tags=["agents"])


class KnowledgeBaseSimpleResponse(BaseModel):
    """Esquema resumido de base de conhecimento vinculada."""

    id: str
    name: str


class AgentCreate(BaseModel):
    """Esquema para criação de agente."""

    name: str
    description: str | None = None
    system_prompt: str
    provider: str  # 'openrouter' | 'openai' | 'anthropic' | 'gemini'
    model: str
    temperature: float = 0.7
    max_tokens: int | None = None
    visibility: str = "private"
    knowledge_base_ids: list[str] = []


class AgentUpdate(BaseModel):
    """Esquema para atualização de agente."""

    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    provider: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    visibility: str | None = None
    knowledge_base_ids: list[str] | None = None


class AgentShareRequest(BaseModel):
    """Esquema para compartilhamento de agente."""

    shared_with_user_id: str
    permission: str = "view"  # 'view' | 'edit'


class VisibilityUpdateRequest(BaseModel):
    """Esquema para atualização de visibilidade."""

    visibility: str  # 'private' | 'shared' | 'public'


class AgentResponse(BaseModel):
    """Esquema de resposta detalhada do agente."""

    id: str
    owner_id: str
    name: str
    description: str | None
    system_prompt: str
    provider: str
    model: str
    temperature: float
    max_tokens: int | None
    visibility: str
    public_slug: str | None
    knowledge_bases: list[KnowledgeBaseSimpleResponse] = []
    created_at: str


@router.get("/agents", response_model=list[AgentResponse])
async def list_agents_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Lista todos os agentes disponíveis para o usuário."""
    can_view_all = user_has_permission(current_user, PermissionCode.AGENTS_VIEW_ALL)
    agents = await orchestration.list_agents(session, str(current_user.id), can_view_all=can_view_all)
    return [
        AgentResponse(
            id=str(a.id),
            owner_id=str(a.owner_id),
            name=a.name,
            description=a.description,
            system_prompt=a.system_prompt,
            provider=a.provider,
            model=a.model,
            temperature=a.temperature,
            max_tokens=a.max_tokens,
            visibility=a.visibility,
            public_slug=a.public_slug,
            knowledge_bases=[
                KnowledgeBaseSimpleResponse(id=str(kb.id), name=kb.name)
                for kb in (a.knowledge_bases or [])
            ],
            created_at=a.created_at.isoformat(),
        )
        for a in agents
    ]


@router.post("/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent_endpoint(
    data: AgentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Cria um novo agente com persona e modelo configurados."""
    if not user_has_permission(current_user, PermissionCode.AGENTS_CREATE):
        raise HTTPException(status_code=403, detail="Permissão para criar agentes não concedida.")

    agent = await orchestration.create_agent(
        session=session,
        owner_id=str(current_user.id),
        name=data.name,
        description=data.description,
        system_prompt=data.system_prompt,
        provider=data.provider,
        model=data.model,
        temperature=data.temperature,
        max_tokens=data.max_tokens,
        visibility=data.visibility,
        knowledge_base_ids=data.knowledge_base_ids,
    )
    return AgentResponse(
        id=str(agent.id),
        owner_id=str(agent.owner_id),
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        provider=agent.provider,
        model=agent.model,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        visibility=agent.visibility,
        public_slug=agent.public_slug,
        knowledge_bases=[
            KnowledgeBaseSimpleResponse(id=str(kb.id), name=kb.name)
            for kb in (agent.knowledge_bases or [])
        ],
        created_at=agent.created_at.isoformat(),
    )


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent_endpoint(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Obtém detalhes do agente por ID."""
    can_view_all = user_has_permission(current_user, PermissionCode.AGENTS_VIEW_ALL)
    agent = await orchestration.get_agent_by_id(session, agent_id, str(current_user.id), can_view_all=can_view_all)
    return AgentResponse(
        id=str(agent.id),
        owner_id=str(agent.owner_id),
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        provider=agent.provider,
        model=agent.model,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        visibility=agent.visibility,
        public_slug=agent.public_slug,
        knowledge_bases=[
            KnowledgeBaseSimpleResponse(id=str(kb.id), name=kb.name)
            for kb in (agent.knowledge_bases or [])
        ],
        created_at=agent.created_at.isoformat(),
    )


@router.patch("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent_endpoint(
    agent_id: str,
    data: AgentUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Atualiza configurações de um agente."""
    can_manage_all = user_has_permission(current_user, PermissionCode.AGENTS_MANAGE_ALL)
    agent = await orchestration.update_agent(
        session=session,
        agent_id=agent_id,
        user_id=str(current_user.id),
        can_manage_all=can_manage_all,
        **data.model_dump(exclude_unset=True),
    )
    return AgentResponse(
        id=str(agent.id),
        owner_id=str(agent.owner_id),
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        provider=agent.provider,
        model=agent.model,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        visibility=agent.visibility,
        public_slug=agent.public_slug,
        knowledge_bases=[
            KnowledgeBaseSimpleResponse(id=str(kb.id), name=kb.name)
            for kb in (agent.knowledge_bases or [])
        ],
        created_at=agent.created_at.isoformat(),
    )


@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_endpoint(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Exclui um agente."""
    can_manage_all = user_has_permission(current_user, PermissionCode.AGENTS_MANAGE_ALL)
    await orchestration.delete_agent(session, agent_id, str(current_user.id), can_manage_all=can_manage_all)
    return None


@router.post("/agents/{agent_id}/share")
async def share_agent_endpoint(
    agent_id: str,
    data: AgentShareRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Compartilha um agente com outro usuário."""
    share = await orchestration.share_agent(
        session=session,
        agent_id=agent_id,
        owner_id=str(current_user.id),
        shared_with_user_id=data.shared_with_user_id,
        permission=data.permission,
    )
    return {"message": "Agente compartilhado com sucesso.", "share_id": str(share.id)}


@router.patch("/agents/{agent_id}/visibility", response_model=AgentResponse)
async def update_agent_visibility_endpoint(
    agent_id: str,
    data: VisibilityUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Altera a visibilidade do agente ('private', 'shared', 'public')."""
    can_manage_all = user_has_permission(current_user, PermissionCode.AGENTS_MANAGE_ALL)
    agent = await orchestration.update_agent(
        session=session,
        agent_id=agent_id,
        user_id=str(current_user.id),
        can_manage_all=can_manage_all,
        visibility=data.visibility,
    )
    return AgentResponse(
        id=str(agent.id),
        owner_id=str(agent.owner_id),
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        provider=agent.provider,
        model=agent.model,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        visibility=agent.visibility,
        public_slug=agent.public_slug,
        knowledge_bases=[
            KnowledgeBaseSimpleResponse(id=str(kb.id), name=kb.name)
            for kb in (agent.knowledge_bases or [])
        ],
        created_at=agent.created_at.isoformat(),
    )


@router.get("/public/agents/{slug}", response_model=AgentResponse)
async def get_public_agent(slug: str, session: AsyncSession = Depends(get_session)):
    """Acesso público a um agente através de seu slug público."""
    query = select(Agent).where(Agent.public_slug == slug, Agent.visibility == "public").options(
        selectinload(Agent.knowledge_bases)
    )
    result = await session.execute(query)
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente público não encontrado.")
    return AgentResponse(
        id=str(agent.id),
        owner_id=str(agent.owner_id),
        name=agent.name,
        description=agent.description,
        system_prompt=agent.system_prompt,
        provider=agent.provider,
        model=agent.model,
        temperature=agent.temperature,
        max_tokens=agent.max_tokens,
        visibility=agent.visibility,
        public_slug=agent.public_slug,
        knowledge_bases=[
            KnowledgeBaseSimpleResponse(id=str(kb.id), name=kb.name)
            for kb in (agent.knowledge_bases or [])
        ],
        created_at=agent.created_at.isoformat(),
    )
