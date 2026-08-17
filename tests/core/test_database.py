"""Testes para configuração e sessão do banco de dados assíncrono."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session


async def test_get_session_yields_async_session() -> None:
    """Verifica se o gerador get_session produz uma instância válida de AsyncSession."""
    async for session in get_session():
        assert isinstance(session, AsyncSession)
        break
