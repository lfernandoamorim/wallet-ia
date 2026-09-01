"""Camada de Orquestração para o domínio de Provedores de IA e Credenciais."""

import json
from typing import AsyncIterator, Protocol
import httpx
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.security import decrypt_secret, encrypt_secret
from backend.domains.providers.execution import ProviderCredential


class ProviderMessage(BaseModel):
    """Estrutura padrão de mensagem trocada com os provedores de IA."""

    role: str  # 'system' | 'user' | 'assistant'
    content: str


class ChatProvider(Protocol):
    """Protocolo base para adaptadores de provedores de IA."""

    async def stream_chat(
        self,
        messages: list[ProviderMessage],
        model: str,
        temperature: float,
        max_tokens: int | None,
        api_key: str,
    ) -> AsyncIterator[str]:
        """Realiza chamada de chat em streaming devolvendo chunks de texto em tempo real."""
        ...


class OpenRouterProvider:
    """Adaptador para chamadas à API da OpenRouter (compatível com OpenAI API)."""

    def __init__(self, base_url: str = "https://openrouter.ai/api/v1"):
        self.base_url = base_url

    async def stream_chat(
        self,
        messages: list[ProviderMessage],
        model: str,
        temperature: float,
        max_tokens: int | None,
        api_key: str,
    ) -> AsyncIterator[str]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://advance.com.br",
            "X-Title": "Plataforma IA",
        }
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", f"{self.base_url}/chat/completions", headers=headers, json=payload
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Erro no provedor OpenRouter: {error_text.decode('utf-8')}",
                    )
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data_json = json.loads(data_str)
                            choice = data_json["choices"][0]
                            delta = choice.get("delta", {})
                            content = delta.get("content")
                            if content:
                                yield content
                        except Exception:
                            continue


class OpenAIProvider:
    """Adaptador para chamadas à API da OpenAI."""

    def __init__(self, base_url: str = "https://api.openai.com/v1"):
        self.base_url = base_url

    async def stream_chat(
        self,
        messages: list[ProviderMessage],
        model: str,
        temperature: float,
        max_tokens: int | None,
        api_key: str,
    ) -> AsyncIterator[str]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [m.model_dump() for m in messages],
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", f"{self.base_url}/chat/completions", headers=headers, json=payload
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Erro no provedor OpenAI: {error_text.decode('utf-8')}",
                    )
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            data_json = json.loads(data_str)
                            choice = data_json["choices"][0]
                            delta = choice.get("delta", {})
                            content = delta.get("content")
                            if content:
                                yield content
                        except Exception:
                            continue


class AnthropicProvider:
    """Adaptador para chamadas à API da Anthropic Claude."""

    def __init__(self, base_url: str = "https://api.anthropic.com/v1"):
        self.base_url = base_url

    async def stream_chat(
        self,
        messages: list[ProviderMessage],
        model: str,
        temperature: float,
        max_tokens: int | None,
        api_key: str,
    ) -> AsyncIterator[str]:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        system_prompt = ""
        formatted_messages = []
        for m in messages:
            if m.role == "system":
                system_prompt += m.content + "\n"
            else:
                formatted_messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": model,
            "messages": formatted_messages,
            "max_tokens": max_tokens or 4096,
            "temperature": temperature,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt.strip()

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST", f"{self.base_url}/messages", headers=headers, json=payload
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Erro no provedor Anthropic: {error_text.decode('utf-8')}",
                    )
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        try:
                            data_json = json.loads(data_str)
                            if data_json.get("type") == "content_block_delta":
                                text = data_json.get("delta", {}).get("text")
                                if text:
                                    yield text
                        except Exception:
                            continue


class GeminiProvider:
    """Adaptador para chamadas à API do Google Gemini."""

    def __init__(self, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        self.base_url = base_url

    async def stream_chat(
        self,
        messages: list[ProviderMessage],
        model: str,
        temperature: float,
        max_tokens: int | None,
        api_key: str,
    ) -> AsyncIterator[str]:
        formatted_contents = []
        system_instruction = None
        for m in messages:
            if m.role == "system":
                system_instruction = {"parts": [{"text": m.content}]}
            else:
                role = "user" if m.role == "user" else "model"
                formatted_contents.append({"role": role, "parts": [{"text": m.content}]})

        payload: dict = {
            "contents": formatted_contents,
            "generationConfig": {"temperature": temperature},
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens
        if system_instruction:
            payload["systemInstruction"] = system_instruction

        url = f"{self.base_url}/models/{model}:streamGenerateContent?key={api_key}&alt=sse"
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Erro no provedor Gemini: {error_text.decode('utf-8')}",
                    )
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        try:
                            data_json = json.loads(data_str)
                            candidates = data_json.get("candidates", [])
                            if candidates:
                                parts = candidates[0].get("content", {}).get("parts", [])
                                for p in parts:
                                    text = p.get("text")
                                    if text:
                                        yield text
                        except Exception:
                            continue


PROVIDERS_MAP: dict[str, ChatProvider] = {
    "openrouter": OpenRouterProvider(),
    "openai": OpenAIProvider(),
    "anthropic": AnthropicProvider(),
    "gemini": GeminiProvider(),
}


def get_provider_adapter(provider_name: str) -> ChatProvider:
    """Retorna a instância do adaptador correspondente ao provedor informado."""
    provider = PROVIDERS_MAP.get(provider_name.lower())
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provedor de IA '{provider_name}' não é suportado.",
        )
    return provider


async def resolve_api_key(session: AsyncSession, provider: str, user_id: str | None = None) -> str:
    """
    Resolve a chave de API a ser utilizada:
    1. Chave própria do usuário (owner_id = user_id)
    2. Chave global do sistema (owner_id IS NULL)
    3. Erro caso não configurada
    """
    if user_id:
        query_user = select(ProviderCredential).where(
            ProviderCredential.provider == provider,
            ProviderCredential.owner_id == user_id,
            ProviderCredential.is_active == True,  # noqa: E712
        )
        res_user = await session.execute(query_user)
        user_cred = res_user.scalars().first()
        if user_cred:
            return decrypt_secret(user_cred.api_key_encrypted)

    query_global = select(ProviderCredential).where(
        ProviderCredential.provider == provider,
        ProviderCredential.owner_id.is_(None),
        ProviderCredential.is_active == True,  # noqa: E712
    )
    res_global = await session.execute(query_global)
    global_cred = res_global.scalars().first()
    if global_cred:
        return decrypt_secret(global_cred.api_key_encrypted)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Nenhuma chave de API configurada para o provedor '{provider}'. Cadastre uma credencial própria ou global.",
    )


async def list_credentials(session: AsyncSession, user_id: str, is_admin: bool = False) -> list[ProviderCredential]:
    """Lista as credenciais visíveis para o usuário."""
    if is_admin:
        query = select(ProviderCredential).order_by(ProviderCredential.created_at.desc())
    else:
        query = select(ProviderCredential).where(
            or_(ProviderCredential.owner_id == user_id, ProviderCredential.owner_id.is_(None))
        ).order_by(ProviderCredential.created_at.desc())
    result = await session.execute(query)
    return list(result.scalars().all())


async def create_credential(
    session: AsyncSession,
    provider: str,
    api_key: str,
    owner_id: str | None = None,
) -> ProviderCredential:
    """Cria e persiste uma nova credencial criptografada."""
    encrypted_key = encrypt_secret(api_key)
    cred = ProviderCredential(
        provider=provider.lower(),
        owner_id=owner_id,
        api_key_encrypted=encrypted_key,
        is_active=True,
    )
    session.add(cred)
    await session.commit()
    await session.refresh(cred)
    return cred


async def delete_credential(session: AsyncSession, credential_id: str, user_id: str, is_admin: bool = False) -> None:
    """Exclui uma credencial respeitando as regras de permissão."""
    query = select(ProviderCredential).where(ProviderCredential.id == credential_id)
    result = await session.execute(query)
    cred = result.scalars().first()
    if not cred:
        raise HTTPException(status_code=404, detail="Credencial não encontrada.")

    if not is_admin and str(cred.owner_id) != str(user_id):
        raise HTTPException(status_code=403, detail="Você não tem permissão para excluir esta credencial.")

    await session.delete(cred)
    await session.commit()
