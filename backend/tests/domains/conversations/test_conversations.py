"""Testes para o domínio de conversas e mensagens."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from domains.conversations.execution import Conversation, ConversationMessage
from domains.conversations.orchestration import (
    create_conversation,
    build_conversation_prompt,
)
from domains.agents.execution import Agent


@pytest.mark.asyncio
async def test_create_conversation():
    """Testa criação de nova conversa."""
    session = AsyncMock()
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    
    conv = await create_conversation(
        session=session,
        owner_id=user_id,
        title="Minha Conversa com IA",
        agent_id=None,
    )
    assert conv.title == "Minha Conversa com IA"
    assert str(conv.owner_id) == user_id


@pytest.mark.asyncio
async def test_build_conversation_prompt():
    """Testa montagem de prompt enriquecido com persona do agente e histórico."""
    session = AsyncMock()
    agent = Agent(
        system_prompt="Você é um assistente financeiro sênior.",
        knowledge_bases=[],
    )
    conv = Conversation(agent=agent, messages=[])

    messages = await build_conversation_prompt(
        session=session,
        conversation=conv,
        user_message_text="Qual a melhor forma de organizar investimentos?",
        attachment_text=None,
    )

    assert len(messages) >= 2
    assert messages[0].role == "system"
    assert "assistente financeiro sênior" in messages[0].content
    assert messages[-1].role == "user"
    assert "organizar investimentos" in messages[-1].content
