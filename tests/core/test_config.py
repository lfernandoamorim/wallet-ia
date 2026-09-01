from backend.core.config import settings


def test_settings_loads_db_url():
    assert hasattr(settings, "database_url")
    assert "postgresql+asyncpg" in settings.database_url
