from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações centrais da aplicação carregadas de variáveis de ambiente."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/appdb"
    secret_key: str = "test_secret_key_super_segura_para_desenvolvimento_local_12345"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    # Chave Fernet de 32 bytes codificada em base64 url-safe padrão para testes/dev
    encryption_key: str = "J1d_5m0lV8kG7t9_x6w2P3r7Y1q0z8N5L4m3K2j1H0g="
    redis_url: str = "redis://localhost:6379/0"
    storage_path: str = "./storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
