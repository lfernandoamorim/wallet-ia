"""Testes para o módulo core de segurança (hash, JWT, criptografia)."""

import pytest
from backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    encrypt_secret,
    decrypt_secret,
)


def test_password_hashing():
    """Testa geração e validação de hash de senha."""
    password = "minhasenhasecreta123"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("outrasenha", hashed) is False


def test_jwt_tokens():
    """Testa criação e decodificação de tokens de acesso e refresh."""
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    access_token = create_access_token(data={"sub": user_id, "username": "admin"})
    payload = decode_token(access_token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["username"] == "admin"
    assert payload["type"] == "access"

    refresh_token = create_refresh_token(data={"sub": user_id})
    refresh_payload = decode_token(refresh_token)
    assert refresh_payload is not None
    assert refresh_payload["sub"] == user_id
    assert refresh_payload["type"] == "refresh"


def test_secret_encryption_and_decryption():
    """Testa criptografia e descriptografia de credenciais/segredos."""
    plain_key = "sk-proj-1234567890abcdef"
    encrypted = encrypt_secret(plain_key)
    assert encrypted != plain_key
    decrypted = decrypt_secret(encrypted)
    assert decrypted == plain_key
