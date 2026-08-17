### Task 2: Core Database and Base Model

**Files:**
- Create: `app/core/database.py`
- Create: `app/core/base_model.py`
- Create: `tests/core/test_database.py`

**Interfaces:**
- Consumes: `settings.database_url`
- Produces: `get_session` dependency, `Base` SQLAlchemy class.

- [ ] **Step 1: Write test for db connection setup**

```python
# tests/core/test_database.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session

async def test_get_session_yields_async_session():
    async for session in get_session():
        assert isinstance(session, AsyncSession)
        break
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/core/test_database.py -v`
Expected: FAIL 

- [ ] **Step 3: Write minimal implementation**

```python
# app/core/base_model.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/core/test_database.py -v`
Expected: PASS

- [ ] **Step 5: Initialize Alembic**

```bash
uv run alembic init migrations
```

- [ ] **Step 6: Configure Alembic (env.py)**

Modify `migrations/env.py` to use async engine and `Base.metadata`.
```python
# Insert at top of migrations/env.py
import asyncio
from sqlalchemy.ext.asyncio import async_engine_from_config
from app.core.base_model import Base
from app.core.config import settings
target_metadata = Base.metadata

# Replace run_migrations_online with:
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url
    connectable = async_engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())
```

- [ ] **Step 7: Commit**

```bash
git add app/core migrations alembic.ini tests
git commit -m "feat: config de banco de dados base e alembic"
```
