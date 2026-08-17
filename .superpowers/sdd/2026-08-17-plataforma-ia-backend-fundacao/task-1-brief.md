### Task 1: Scaffolding and Core Settings

**Files:**
- Create: `pyproject.toml`
- Create: `app/core/config.py`
- Create: `tests/core/test_config.py`

**Interfaces:**
- Produces: `Settings` class with DB URL.

- [ ] **Step 1: Initialize project with uv**

```bash
uv init .
uv add fastapi uvicorn pydantic pydantic-settings sqlalchemy asyncpg alembic python-jose passlib bcrypt pytest pytest-asyncio httpx
```

- [ ] **Step 2: Write failing test for config**

```python
# tests/core/test_config.py
from app.core.config import settings

def test_settings_loads_db_url():
    assert hasattr(settings, "database_url")
    assert "postgresql+asyncpg" in settings.database_url
```

- [ ] **Step 3: Run test to verify it fails**

Run: `uv run pytest tests/core/test_config.py -v`
Expected: FAIL with "No module named app"

- [ ] **Step 4: Write minimal implementation**

```python
# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/appdb"
    secret_key: str = "test_secret"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

- [ ] **Step 5: Create empty __init__.py files to fix imports**

```bash
mkdir -p app/core tests/core
touch app/__init__.py app/core/__init__.py tests/__init__.py tests/core/__init__.py
```

- [ ] **Step 6: Run test to verify it passes**

Run: `uv run pytest tests/core/test_config.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml app tests
git commit -m "chore: setup projeto base e configuracoes centrais"
```
