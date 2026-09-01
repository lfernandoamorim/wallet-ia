"""Configuração do motor de banco de dados assíncrono e gerenciamento de sessões."""

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Gera uma sessão assíncrona do banco de dados para injeção de dependência."""
    async with AsyncSessionLocal() as session:
        yield session
