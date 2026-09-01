"""Camada de Diretiva para o domínio de Conversas e Chat (Endpoints REST e WebSocket)."""

import json
from typing import Annotated
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database import AsyncSessionLocal, get_session
from core.permissions import PermissionCode
from core.security import decode_token
from domains.auth.directive import get_current_user
from domains.auth.orchestration import user_has_permission
from domains.conversations import orchestration
from domains.conversations.execution import Conversation, ConversationMessage
from domains.users.execution import User

router = APIRouter(tags=["conversations"])


class ConversationCreate(BaseModel):
    """Esquema para criação de conversa."""

    title: str | None = None
    agent_id: str | None = None
    visibility: str = "private"


class MessageAttachmentResponse(BaseModel):
    """Esquema de anexo de mensagem."""

    id: str
    file_name: str
    mime_type: str
    size_bytes: int | None


class MessageResponse(BaseModel):
    """Esquema de mensagem de conversa."""

    id: str
    role: str
    content: str | None
    created_at: str
    attachments: list[MessageAttachmentResponse] = []


class ConversationResponse(BaseModel):
    """Esquema detalhado de conversa."""

    id: str
    owner_id: str
    agent_id: str | None
    title: str | None
    visibility: str
    public_slug: str | None
    created_at: str
    updated_at: str
    messages: list[MessageResponse] = []


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Lista as conversas disponíveis para o usuário."""
    can_view_all = user_has_permission(current_user, PermissionCode.CONVERSATIONS_VIEW_ALL)
    convs = await orchestration.list_conversations(session, str(current_user.id), can_view_all=can_view_all)
    return [
        ConversationResponse(
            id=str(c.id),
            owner_id=str(c.owner_id),
            agent_id=str(c.agent_id) if c.agent_id else None,
            title=c.title,
            visibility=c.visibility,
            public_slug=c.public_slug,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
            messages=[
                MessageResponse(
                    id=str(m.id),
                    role=m.role,
                    content=m.content,
                    created_at=m.created_at.isoformat(),
                    attachments=[
                        MessageAttachmentResponse(
                            id=str(att.id),
                            file_name=att.file_name,
                            mime_type=att.mime_type,
                            size_bytes=att.size_bytes,
                        )
                        for att in (m.attachments or [])
                    ],
                )
                for m in (c.messages or [])
            ],
        )
        for c in convs
    ]


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation_endpoint(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Cria uma nova conversa."""
    if not user_has_permission(current_user, PermissionCode.CONVERSATIONS_CREATE):
        raise HTTPException(status_code=403, detail="Permissão para criar conversas negada.")

    conv = await orchestration.create_conversation(
        session=session,
        owner_id=str(current_user.id),
        title=data.title,
        agent_id=data.agent_id,
        visibility=data.visibility,
    )
    return ConversationResponse(
        id=str(conv.id),
        owner_id=str(conv.owner_id),
        agent_id=str(conv.agent_id) if conv.agent_id else None,
        title=conv.title,
        visibility=conv.visibility,
        public_slug=conv.public_slug,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        messages=[],
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_endpoint(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Obtém detalhes de uma conversa."""
    can_view_all = user_has_permission(current_user, PermissionCode.CONVERSATIONS_VIEW_ALL)
    conv = await orchestration.get_conversation_by_id(
        session, conversation_id, str(current_user.id), can_view_all=can_view_all
    )
    return ConversationResponse(
        id=str(conv.id),
        owner_id=str(conv.owner_id),
        agent_id=str(conv.agent_id) if conv.agent_id else None,
        title=conv.title,
        visibility=conv.visibility,
        public_slug=conv.public_slug,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        messages=[
            MessageResponse(
                id=str(m.id),
                role=m.role,
                content=m.content,
                created_at=m.created_at.isoformat(),
                attachments=[
                    MessageAttachmentResponse(
                        id=str(att.id),
                        file_name=att.file_name,
                        mime_type=att.mime_type,
                        size_bytes=att.size_bytes,
                    )
                    for att in (m.attachments or [])
                ],
            )
            for m in (conv.messages or [])
        ],
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_endpoint(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Exclui uma conversa."""
    can_view_all = user_has_permission(current_user, PermissionCode.CONVERSATIONS_VIEW_ALL)
    conv = await orchestration.get_conversation_by_id(
        session, conversation_id, str(current_user.id), can_view_all=can_view_all
    )
    if not can_view_all and str(conv.owner_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Você não tem permissão para excluir esta conversa.")

    await session.delete(conv)
    await session.commit()
    return None


@router.post("/conversations/{conversation_id}/messages")
async def send_message_endpoint(
    conversation_id: str,
    content: str = Form(...),
    file: UploadFile | None = File(None),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Envia uma mensagem para a conversa (com anexo opcional) e transmite a resposta do assistente."""
    attachment_bytes = await file.read() if file else None
    attachment_filename = file.filename if file else None
    mime_type = file.content_type if file else None

    async def token_generator():
        async for token in orchestration.stream_agent_response(
            session=session,
            conversation_id=conversation_id,
            user_message_text=content,
            user_id=str(current_user.id),
            attachment_bytes=attachment_bytes,
            attachment_filename=attachment_filename,
            mime_type=mime_type,
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")


@router.get("/public/conversations/{slug}", response_model=ConversationResponse)
async def get_public_conversation(slug: str, session: AsyncSession = Depends(get_session)):
    """Acesso público a uma conversa através do slug público."""
    query = select(Conversation).where(
        Conversation.public_slug == slug, Conversation.visibility == "public"
    ).options(
        selectinload(Conversation.messages).selectinload(ConversationMessage.attachments)
    )
    result = await session.execute(query)
    conv = result.scalars().first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversa pública não encontrada.")

    return ConversationResponse(
        id=str(conv.id),
        owner_id=str(conv.owner_id),
        agent_id=str(conv.agent_id) if conv.agent_id else None,
        title=conv.title,
        visibility=conv.visibility,
        public_slug=conv.public_slug,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        messages=[
            MessageResponse(
                id=str(m.id),
                role=m.role,
                content=m.content,
                created_at=m.created_at.isoformat(),
                attachments=[],
            )
            for m in (conv.messages or [])
        ],
    )


@router.websocket("/ws/conversations/{conversation_id}")
async def websocket_chat_endpoint(websocket: WebSocket, conversation_id: str):
    """Canal WebSocket para envio e recebimento de tokens de chat em tempo real."""
    await websocket.accept()
    try:
        # 1. Autenticação inicial via payload JSON {"token": "jwt_access_token"}
        auth_msg = await websocket.receive_text()
        auth_data = json.loads(auth_msg)
        token = auth_data.get("token")
        payload = decode_token(token) if token else None

        if not payload or payload.get("type") != "access":
            await websocket.send_json({"error": "Autenticação inválida ou token expirado."})
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user_id = payload.get("sub")

        while True:
            # 2. Recebe mensagem do usuário
            data_text = await websocket.receive_text()
            data_json = json.loads(data_text)
            user_content = data_json.get("content", "")

            if not user_content.strip():
                continue

            async with AsyncSessionLocal() as session:
                try:
                    async for token_chunk in orchestration.stream_agent_response(
                        session=session,
                        conversation_id=conversation_id,
                        user_message_text=user_content,
                        user_id=user_id,
                    ):
                        await websocket.send_json({"type": "token", "data": token_chunk})
                    await websocket.send_json({"type": "done"})
                except Exception as e:
                    await websocket.send_json({"type": "error", "message": str(e)})

    except WebSocketDisconnect:
        pass
