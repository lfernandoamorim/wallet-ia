### Task 4: Users Domain - Orchestration & Directive

**Files:**
- Create: `app/domains/users/orchestration.py`
- Create: `app/domains/users/directive.py`
- Modify: `app/main.py`
- Create: `tests/domains/users/test_directive.py`

**Interfaces:**
- Consumes: `User` model, `get_session`.
- Produces: `POST /users/` endpoint.

- [ ] **Step 1: Write test for creating user**

```python
# tests/domains/users/test_directive.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={
        "email": "test@test.com", 
        "username": "test", 
        "password": "pwd"
    })
    # Might fail with 404 before implementation
    assert response.status_code != 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/domains/users/test_directive.py -v`

- [ ] **Step 3: Write minimal implementation**

```python
# app/domains/users/orchestration.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.users.execution import User

async def create_user(session: AsyncSession, user_data: dict) -> User:
    # Minimal implementation for MVP
    user = User(
        email=user_data["email"],
        username=user_data["username"],
        password_hash=user_data["password"] + "_hashed" # Mock hash for now
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
```

```python
# app/domains/users/directive.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.domains.users import orchestration
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    username: str

@router.post("/", response_model=UserResponse)
async def create_user_endpoint(user: UserCreate, session: AsyncSession = Depends(get_session)):
    created_user = await orchestration.create_user(session, user.model_dump())
    return UserResponse(
        id=str(created_user.id),
        email=created_user.email,
        username=created_user.username
    )
```

```python
# app/main.py
from fastapi import FastAPI
from app.domains.users.directive import router as users_router

app = FastAPI(title="Plataforma IA API")

app.include_router(users_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/domains/users/test_directive.py -v`

- [ ] **Step 5: Commit**

```bash
git add app/domains/users app/main.py tests/domains/users
git commit -m "feat(users): criar endpoint POST /users e orquestracao"
```
