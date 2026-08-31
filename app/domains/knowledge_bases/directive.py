"""Camada de Diretiva para o domínio de Base de Conhecimento e RAG (Endpoints REST)."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_session
from app.core.permissions import PermissionCode
from app.domains.auth.directive import get_current_user
from app.domains.auth.orchestration import user_has_permission
from app.domains.knowledge_bases import orchestration
from app.domains.knowledge_bases.execution import KBDocument, KnowledgeBase
from app.domains.users.execution import User

router = APIRouter(tags=["knowledge-bases"])


class KnowledgeBaseCreate(BaseModel):
    """Esquema para criação de base de conhecimento."""

    name: str
    description: str | None = None
    visibility: str = "private"  # 'private' | 'shared' | 'public'


class KnowledgeBaseResponse(BaseModel):
    """Esquema de resposta de base de conhecimento."""

    id: str
    owner_id: str
    name: str
    description: str | None
    visibility: str
    public_slug: str | None
    created_at: str


class DocumentResponse(BaseModel):
    """Esquema de resposta para documento enviado."""

    id: str
    knowledge_base_id: str
    file_name: str
    file_type: str
    status: str
    error_message: str | None
    created_at: str


@router.get("/knowledge-bases", response_model=list[KnowledgeBaseResponse])
async def list_knowledge_bases_endpoint(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Lista as bases de conhecimento acessíveis pelo usuário."""
    can_view_all = user_has_permission(current_user, PermissionCode.KB_VIEW_ALL)
    kbs = await orchestration.list_knowledge_bases(session, str(current_user.id), can_view_all=can_view_all)
    return [
        KnowledgeBaseResponse(
            id=str(kb.id),
            owner_id=str(kb.owner_id),
            name=kb.name,
            description=kb.description,
            visibility=kb.visibility,
            public_slug=kb.public_slug,
            created_at=kb.created_at.isoformat(),
        )
        for kb in kbs
    ]


@router.post("/knowledge-bases", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base_endpoint(
    data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Cria uma nova base de conhecimento."""
    if not user_has_permission(current_user, PermissionCode.KB_CREATE):
        raise HTTPException(status_code=403, detail="Permissão para criar base de conhecimento negada.")

    kb = await orchestration.create_knowledge_base(
        session=session,
        owner_id=str(current_user.id),
        name=data.name,
        description=data.description,
        visibility=data.visibility,
    )
    return KnowledgeBaseResponse(
        id=str(kb.id),
        owner_id=str(kb.owner_id),
        name=kb.name,
        description=kb.description,
        visibility=kb.visibility,
        public_slug=kb.public_slug,
        created_at=kb.created_at.isoformat(),
    )


@router.get("/knowledge-bases/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base_endpoint(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Obtém detalhes de uma base de conhecimento."""
    can_view_all = user_has_permission(current_user, PermissionCode.KB_VIEW_ALL)
    kb = await orchestration.get_knowledge_base_by_id(session, kb_id, str(current_user.id), can_view_all=can_view_all)
    return KnowledgeBaseResponse(
        id=str(kb.id),
        owner_id=str(kb.owner_id),
        name=kb.name,
        description=kb.description,
        visibility=kb.visibility,
        public_slug=kb.public_slug,
        created_at=kb.created_at.isoformat(),
    )


@router.delete("/knowledge-bases/{kb_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_knowledge_base_endpoint(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Exclui uma base de conhecimento."""
    can_manage_all = user_has_permission(current_user, PermissionCode.KB_MANAGE_ALL)
    kb = await orchestration.get_knowledge_base_by_id(session, kb_id, str(current_user.id), can_view_all=can_manage_all)
    if not can_manage_all and str(kb.owner_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Você não tem permissão para excluir esta base.")
    await session.delete(kb)
    await session.commit()
    return None


@router.post("/knowledge-bases/{kb_id}/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document_endpoint(
    kb_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Envia e ingere um arquivo (.md, .docx, .xlsx, .txt) para a base de conhecimento RAG."""
    can_view_all = user_has_permission(current_user, PermissionCode.KB_VIEW_ALL)
    await orchestration.get_knowledge_base_by_id(session, kb_id, str(current_user.id), can_view_all=can_view_all)

    content = await file.read()
    doc = await orchestration.ingest_document(
        session=session,
        knowledge_base_id=kb_id,
        file_name=file.filename or "arquivo.txt",
        content_bytes=content,
        uploaded_by_id=str(current_user.id),
    )
    return DocumentResponse(
        id=str(doc.id),
        knowledge_base_id=str(doc.knowledge_base_id),
        file_name=doc.file_name,
        file_type=doc.file_type,
        status=doc.status,
        error_message=doc.error_message,
        created_at=doc.created_at.isoformat(),
    )


@router.get("/knowledge-bases/{kb_id}/documents", response_model=list[DocumentResponse])
async def list_documents_endpoint(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Lista todos os documentos de uma base de conhecimento."""
    can_view_all = user_has_permission(current_user, PermissionCode.KB_VIEW_ALL)
    await orchestration.get_knowledge_base_by_id(session, kb_id, str(current_user.id), can_view_all=can_view_all)

    query = select(KBDocument).where(KBDocument.knowledge_base_id == kb_id).order_by(KBDocument.created_at.desc())
    result = await session.execute(query)
    docs = result.scalars().all()
    return [
        DocumentResponse(
            id=str(d.id),
            knowledge_base_id=str(d.knowledge_base_id),
            file_name=d.file_name,
            file_type=d.file_type,
            status=d.status,
            error_message=d.error_message,
            created_at=d.created_at.isoformat(),
        )
        for d in docs
    ]


@router.get("/public/knowledge-bases/{slug}", response_model=KnowledgeBaseResponse)
async def get_public_knowledge_base(slug: str, session: AsyncSession = Depends(get_session)):
    """Acesso público a uma base de conhecimento através do slug público."""
    query = select(KnowledgeBase).where(KnowledgeBase.public_slug == slug, KnowledgeBase.visibility == "public")
    result = await session.execute(query)
    kb = result.scalars().first()
    if not kb:
        raise HTTPException(status_code=404, detail="Base de conhecimento pública não encontrada.")
    return KnowledgeBaseResponse(
        id=str(kb.id),
        owner_id=str(kb.owner_id),
        name=kb.name,
        description=kb.description,
        visibility=kb.visibility,
        public_slug=kb.public_slug,
        created_at=kb.created_at.isoformat(),
    )
