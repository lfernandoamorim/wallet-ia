"""Ponto de entrada principal da aplicação FastAPI Plataforma de IA."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.core.models  # Garante o mapeamento de todos os modelos ORM
from app.core.database import AsyncSessionLocal
from app.domains.agents.directive import router as agents_router
from app.domains.auth.directive import router as auth_router
from app.domains.conversations.directive import router as conversations_router
from app.domains.knowledge_bases.directive import router as kb_router
from app.domains.providers.directive import router as providers_router
from app.domains.roles.directive import router as roles_router
from app.domains.roles.orchestration import seed_permissions_and_roles
from app.domains.users.directive import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação (startup e shutdown)."""
    # Tenta realizar o seed de permissões no startup caso o banco esteja acessível
    try:
        async with AsyncSessionLocal() as session:
            await seed_permissions_and_roles(session)
    except Exception:
        # Banco pode não estar conectado em tempo de testes locais/mock
        pass
    yield


app = FastAPI(
    title="Plataforma IA Backend",
    description="API para Agentes de IA, RAG (Base de Conhecimento), Chat em Tempo Real e RBAC.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuração de CORS para frontend (React / Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de todos os domínios da aplicação
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(providers_router)
app.include_router(kb_router)
app.include_router(agents_router)
app.include_router(conversations_router)


@app.get("/health", tags=["health"])
def health_check():
    """Endpoint para verificação de integridade da aplicação."""
    return {"status": "ok", "app": "Plataforma IA API"}
