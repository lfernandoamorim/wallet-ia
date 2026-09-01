"""Camada de Orquestração para o domínio de Agentes de IA."""

import uuid
from typing import Any
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domains.agents.execution import Agent, AgentKnowledgeBase
from domains.conversations.execution import ResourceShare
from domains.knowledge_bases.execution import KnowledgeBase
from domains.users.execution import User


async def create_agent(
    session: AsyncSession,
    owner_id: str,
    name: str,
    system_prompt: str,
    provider: str,
    model: str,
    description: str | None = None,
    temperature: float = 0.7,
    max_tokens: int | None = None,
    visibility: str = "private",
    knowledge_base_ids: list[str] | None = None,
) -> Agent:
    """Cria e persiste um novo agente com sua persona e vínculos de base de conhecimento."""
    slug = str(uuid.uuid4())[:8] if visibility == "public" else None

    agent = Agent(
        owner_id=owner_id,
        name=name,
        description=description,
        system_prompt=system_prompt,
        provider=provider.lower(),
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        visibility=visibility,
        public_slug=slug,
    )

    if knowledge_base_ids:
        query_kbs = select(KnowledgeBase).where(KnowledgeBase.id.in_(knowledge_base_ids))
        res_kbs = await session.execute(query_kbs)
        agent.knowledge_bases = list(res_kbs.scalars().all())

    session.add(agent)
    await session.commit()
    await session.refresh(agent)
    return agent


async def list_agents(
    session: AsyncSession,
    user_id: str,
    can_view_all: bool = False,
) -> list[Agent]:
    """Lista agentes disponíveis para o usuário (próprios, compartilhados, públicos ou todos se admin)."""
    if can_view_all:
        query = select(Agent).options(selectinload(Agent.knowledge_bases)).order_by(Agent.created_at.desc())
    else:
        # Busca IDs de recursos compartilhados com o usuário
        query_shared = select(ResourceShare.resource_id).where(
            ResourceShare.resource_type == "agent",
            ResourceShare.shared_with == user_id,
        )
        res_shared = await session.execute(query_shared)
        shared_ids = list(res_shared.scalars().all())

        query = select(Agent).where(
            or_(
                Agent.owner_id == user_id,
                Agent.visibility == "public",
                Agent.id.in_(shared_ids) if shared_ids else False,
            )
        ).options(selectinload(Agent.knowledge_bases)).order_by(Agent.created_at.desc())

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_agent_by_id(
    session: AsyncSession,
    agent_id: str,
    user_id: str | None = None,
    can_view_all: bool = False,
) -> Agent:
    """Busca um agente por ID validando regras de visibilidade e compartilhamento."""
    query = select(Agent).where(Agent.id == agent_id).options(selectinload(Agent.knowledge_bases))
    result = await session.execute(query)
    agent = result.scalars().first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente não encontrado.")

    if not can_view_all and agent.visibility != "public" and user_id and str(agent.owner_id) != str(user_id):
        # Verifica se foi compartilhado com o usuário
        query_share = select(ResourceShare).where(
            ResourceShare.resource_type == "agent",
            ResourceShare.resource_id == agent_id,
            ResourceShare.shared_with == user_id,
        )
        res_share = await session.execute(query_share)
        if not res_share.scalars().first():
            raise HTTPException(status_code=403, detail="Acesso não autorizado a este agente.")

    return agent


async def update_agent(
    session: AsyncSession,
    agent_id: str,
    user_id: str,
    can_manage_all: bool = False,
    **kwargs: Any,
) -> Agent:
    """Atualiza dados e configurações de um agente."""
    agent = await get_agent_by_id(session, agent_id, user_id, can_view_all=can_manage_all)
    if not can_manage_all and str(agent.owner_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar este agente.")

    if "knowledge_base_ids" in kwargs and kwargs["knowledge_base_ids"] is not None:
        kb_ids = kwargs.pop("knowledge_base_ids")
        query_kbs = select(KnowledgeBase).where(KnowledgeBase.id.in_(kb_ids))
        res_kbs = await session.execute(query_kbs)
        agent.knowledge_bases = list(res_kbs.scalars().all())

    for field, val in kwargs.items():
        if val is not None and hasattr(agent, field):
            if field == "visibility" and val == "public" and not agent.public_slug:
                agent.public_slug = str(uuid.uuid4())[:8]
            setattr(agent, field, val)

    await session.commit()
    await session.refresh(agent)
    return agent


async def delete_agent(
    session: AsyncSession,
    agent_id: str,
    user_id: str,
    can_manage_all: bool = False,
) -> None:
    """Exclui um agente."""
    agent = await get_agent_by_id(session, agent_id, user_id, can_view_all=can_manage_all)
    if not can_manage_all and str(agent.owner_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Você não tem permissão para excluir este agente.")

    await session.delete(agent)
    await session.commit()


async def share_agent(
    session: AsyncSession,
    agent_id: str,
    owner_id: str,
    shared_with_user_id: str,
    permission: str = "view",
) -> ResourceShare:
    """Compartilha um agente com outro usuário específico."""
    agent = await get_agent_by_id(session, agent_id, owner_id)
    if str(agent.owner_id) != str(owner_id):
        raise HTTPException(status_code=403, detail="Apenas o proprietário pode compartilhar o agente.")

    agent.visibility = "shared"

    share = ResourceShare(
        resource_type="agent",
        resource_id=agent.id,
        shared_with=shared_with_user_id,
        permission=permission,
        shared_by=owner_id,
    )
    session.add(share)
    await session.commit()
    await session.refresh(share)
    return share
