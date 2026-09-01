"""Módulo de segurança para criptografia de senhas, JWT e segredos."""

from datetime import datetime, timedelta, timezone
from typing import Any
import base64
import bcrypt
from cryptography.fernet import Fernet
from jose import JWTError, jwt

from backend.core.config import settings


def get_password_hash(password: str) -> str:
    """Gera hash seguro para a senha informada usando bcrypt."""
    # Trunca em 72 bytes para conformidade com a especificação bcrypt se necessário
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano coincide com o hash."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Cria token JWT de acesso com tempo de expiração."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Cria token JWT de refresh com maior tempo de expiração."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.refresh_token_expire_days)
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    """Decodifica e valida o token JWT."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def get_fernet_cipher() -> Fernet:
    """Obtém instância do cifrador Fernet."""
    key = settings.encryption_key
    if len(key) != 44:
        padded = key.ljust(32, "x")[:32].encode("utf-8")
        key = base64.urlsafe_b64encode(padded).decode("utf-8")
    return Fernet(key.encode("utf-8"))


def encrypt_secret(plain_text: str) -> str:
    """Criptografa um texto/segredo com Fernet."""
    cipher = get_fernet_cipher()
    return cipher.encrypt(plain_text.encode("utf-8")).decode("utf-8")


def decrypt_secret(cipher_text: str) -> str:
    """Descriptografa um texto/segredo criptografado com Fernet."""
    cipher = get_fernet_cipher()
    return cipher.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
