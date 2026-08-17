from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações centrais da aplicação carregadas de variáveis de ambiente."""

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/appdb"
    secret_key: str = "test_secret"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
