"""Testes para o domínio de Provedores de IA e Credenciais."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.domains.providers.execution import ProviderCredential
from backend.domains.providers.orchestration import (
    create_credential,
    resolve_api_key,
    get_provider_adapter,
    ProviderMessage,
)
from backend.core.security import encrypt_secret


@pytest.mark.asyncio
async def test_create_and_resolve_credential():
    """Testa armazenamento criptografado e resolução de chave de API."""
    session = AsyncMock()
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    plain_key = "sk-ant-api03-123456789"
    
    cred = ProviderCredential(
        id="987e6543-e89b-12d3-a456-426614174000",
        owner_id=user_id,
        provider="anthropic",
        api_key_encrypted=encrypt_secret(plain_key),
        is_active=True,
    )

    mock_result = MagicMock()
    mock_result.scalars().first.return_value = cred
    session.execute.return_value = mock_result

    resolved = await resolve_api_key(session, provider="anthropic", user_id=user_id)
    assert resolved == plain_key


def test_provider_adapter_instantiation():
    """Testa obtenção do adaptador para os provedores suportados."""
    adapter_openai = get_provider_adapter("openai")
    adapter_openrouter = get_provider_adapter("openrouter")
    adapter_anthropic = get_provider_adapter("anthropic")
    adapter_gemini = get_provider_adapter("gemini")

    assert adapter_openai is not None
    assert adapter_openrouter is not None
    assert adapter_anthropic is not None
    assert adapter_gemini is not None
