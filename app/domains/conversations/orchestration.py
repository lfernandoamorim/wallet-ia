"""Camada de Orquestração para o domínio de Conversas, Mensagens e Chat."""

import os
import uuid
from typing import AsyncIterator
from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.domains.agents.execution import Agent
from app.domains.conversations.execution import (
    Conversation,
    ConversationMessage,
    MessageAttachment,
    ResourceShare,
)
from app.domains.knowledge_bases.orchestration import (
    extract_text_from_file,
    retrieve_relevant_chunks,
)
from app.domains.providers.orchestration import (
    ProviderMessage,
    get_provider_adapter,
    resolve_api_key,
)
from app.domains.users.execution import User


async def create_conversation(
    session: AsyncSession,
    owner_id: str,
    title: str | None = None,
    agent_id: str | None = None,
    visibility: str = "private",
) -> Conversation:
    """Cria e persiste uma nova conversa."""
    slug = str(uuid.uuid4())[:8] if visibility == "public" else None

    conv = Conversation(
        owner_id=owner_id,
        agent_id=agent_id,
        title=title or "Nova Conversa",
        visibility=visibility,
        public_slug=slug,
    )
    session.add(conv)
    await session.commit()
    await session.refresh(conv)
    return conv


async def list_conversations(
    session: AsyncSession,
    user_id: str,
    can_view_all: bool = False,
) -> list[Conversation]:
    """Lista as conversas visíveis para o usuário."""
    if can_view_all:
        query = select(Conversation).options(
            selectinload(Conversation.agent),
            selectinload(Conversation.messages),
        ).order_by(Conversation.updated_at.desc())
    else:
        query_shared = select(ResourceShare.resource_id).where(
            ResourceShare.resource_type == "conversation",
            ResourceShare.shared_with == user_id,
        )
        res_shared = await session.execute(query_shared)
        shared_ids = list(res_shared.scalars().all())

        query = select(Conversation).where(
            or_(
                Conversation.owner_id == user_id,
                Conversation.visibility == "public",
                Conversation.id.in_(shared_ids) if shared_ids else False,
            )
        ).options(
            selectinload(Conversation.agent),
            selectinload(Conversation.messages),
        ).order_by(Conversation.updated_at.desc())

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_conversation_by_id(
    session: AsyncSession,
    conversation_id: str,
    user_id: str | None = None,
    can_view_all: bool = False,
) -> Conversation:
    """Busca uma conversa por ID validando visibilidade."""
    query = select(Conversation).where(Conversation.id == conversation_id).options(
        selectinload(Conversation.agent),
        selectinload(Conversation.messages).selectinload(ConversationMessage.attachments),
    )
    result = await session.execute(query)
    conv = result.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")

    if not can_view_all and conv.visibility != "public" and user_id and str(conv.owner_id) != str(user_id):
        query_share = select(ResourceShare).where(
            ResourceShare.resource_type == "conversation",
            ResourceShare.resource_id == conversation_id,
            ResourceShare.shared_with == user_id,
        )
        res_share = await session.execute(query_share)
        if not res_share.scalars().first():
            raise HTTPException(status_code=403, detail="Acesso não autorizado a esta conversa.")

    return conv


async def build_conversation_prompt(
    session: AsyncSession,
    conversation: Conversation,
    user_message_text: str,
    attachment_text: str | None = None,
) -> list[ProviderMessage]:
    """Monta a lista de mensagens formatadas com persona do agente, RAG e histórico."""
    messages: list[ProviderMessage] = []

    system_prompt = "Você é um assistente de inteligência artificial prestativo, objetivo e preciso."
    rag_context = ""

    if conversation.agent:
        system_prompt = conversation.agent.system_prompt
        # Se o agente possuir bases de conhecimento vinculadas, busca chunks mais relevantes via RAG
        if conversation.agent.knowledge_bases:
            kb_ids = [str(kb.id) for kb in conversation.agent.knowledge_bases]
            relevant_chunks = await retrieve_relevant_chunks(
                session=session,
                knowledge_base_ids=kb_ids,
                query_text=user_message_text,
                top_k=4,
            )
            if relevant_chunks:
                rag_context = "\n\n--- Base de Conhecimento Relevante ---\n" + "\n---\n".join(relevant_chunks)

    full_system_content = system_prompt + rag_context
    messages.append(ProviderMessage(role="system", content=full_system_content))

    # Inclui histórico recente das últimas 10 mensagens
    if conversation.messages:
        for msg in conversation.messages[-10:]:
            if msg.role in ["user", "assistant"] and msg.content:
                messages.append(ProviderMessage(role=msg.role, content=msg.content))

    # Mensagem atual do usuário com texto extraído de anexos se houver
    final_user_content = user_message_text
    if attachment_text:
        final_user_content += f"\n\n[Texto do Arquivo Anexo]:\n{attachment_text}"

    messages.append(ProviderMessage(role="user", content=final_user_content))
    return messages


async def stream_agent_response(
    session: AsyncSession,
    conversation_id: str,
    user_message_text: str,
    user_id: str,
    attachment_bytes: bytes | None = None,
    attachment_filename: str | None = None,
    mime_type: str | None = None,
) -> AsyncIterator[str]:
    """
    Executa o pipeline completo de resposta em streaming da IA:
    1. Salva mensagem do usuário e anexo
    2. Monta prompt enriquecido (Persona + RAG + Histórico)
    3. Resolve chave e chama provedor de IA
    4. Transmite tokens em tempo real e persiste resposta final
    """
    conv = await get_conversation_by_id(session, conversation_id, user_id=user_id)

    # 1. Salva mensagem do usuário
    user_msg = ConversationMessage(
        conversation_id=conv.id,
        role="user",
        content=user_message_text,
    )
    session.add(user_msg)
    await session.flush()

    extracted_attachment_text = None
    if attachment_bytes and attachment_filename:
        os.makedirs(settings.storage_path, exist_ok=True)
        storage_path = os.path.join(settings.storage_path, f"{uuid.uuid4()}_{attachment_filename}")
        with open(storage_path, "wb") as f:
            f.write(attachment_bytes)

        extracted_attachment_text = extract_text_from_file(attachment_filename, attachment_bytes)
        attachment = MessageAttachment(
            message_id=user_msg.id,
            file_name=attachment_filename,
            mime_type=mime_type or "application/octet-stream",
            storage_path=storage_path,
            size_bytes=len(attachment_bytes),
            extracted_text=extracted_attachment_text,
        )
        session.add(attachment)

    await session.commit()

    # 2. Configurações de provedor e modelo
    provider_name = conv.agent.provider if conv.agent else "openrouter"
    model_name = conv.agent.model if conv.agent else "openai/gpt-4o-mini"
    temperature = conv.agent.temperature if conv.agent else 0.7
    max_tokens = conv.agent.max_tokens if conv.agent else 2048

    api_key = await resolve_api_key(session, provider=provider_name, user_id=user_id)
    adapter = get_provider_adapter(provider_name)

    prompt_messages = await build_conversation_prompt(
        session=session,
        conversation=conv,
        user_message_text=user_message_text,
        attachment_text=extracted_attachment_text,
    )

    # 3. Execução do streaming e persistência da resposta do assistente
    full_response_text = []
    async for token in adapter.stream_chat(
        messages=prompt_messages,
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key,
    ):
        full_response_text.append(token)
        yield token

    assistant_reply = "".join(full_response_text)
    assistant_msg = ConversationMessage(
        conversation_id=conv.id,
        role="assistant",
        content=assistant_reply,
    )
    session.add(assistant_msg)
    await session.commit()
