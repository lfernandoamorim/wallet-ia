"""Testes para o domínio de Agentes e Persona."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from domains.agents.execution import Agent
from domains.agents.orchestration import create_agent, get_agent_by_id


@pytest.mark.asyncio
async def test_create_agent():
    """Testa criação de agente com persona e modelo."""
    session = AsyncMock()
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    
    mock_res_kb = MagicMock()
    mock_res_kb.scalars().all.return_value = []
    session.execute.return_value = mock_res_kb

    agent = await create_agent(
        session=session,
        owner_id=user_id,
        name="Assistente Especialista",
        description="Agente de suporte técnico",
        system_prompt="Você é um assistente técnico prestativo.",
        provider="openai",
        model="gpt-4o",
        temperature=0.5,
        max_tokens=2048,
        visibility="private",
    )

    assert agent.name == "Assistente Especialista"
    assert agent.provider == "openai"
    assert agent.model == "gpt-4o"
    assert agent.system_prompt == "Você é um assistente técnico prestativo."
