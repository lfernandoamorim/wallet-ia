### Task 3: Users Domain - Execution Layer (Models)

**Files:**
- Create: `app/domains/users/execution.py`
- Create: `tests/domains/users/test_execution.py`

**Interfaces:**
- Consumes: `Base` model.
- Produces: `User` SQLAlchemy model.

- [ ] **Step 1: Write test for user model fields**

```python
# tests/domains/users/test_execution.py
from app.domains.users.execution import User

def test_user_model_instantiation():
    user = User(email="test@test.com", username="testuser", password_hash="hash")
    assert user.email == "test@test.com"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/domains/users/test_execution.py -v`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Write minimal implementation**

```bash
mkdir -p app/domains/users tests/domains/users
touch app/domains/__init__.py app/domains/users/__init__.py tests/domains/__init__.py tests/domains/users/__init__.py
```

```python
# app/domains/users/execution.py
from sqlalchemy import Column, String, Boolean
from app.core.base_model import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superadmin = Column(Boolean, default=False, nullable=False)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/domains/users/test_execution.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app/domains tests/domains
git commit -m "feat(users): criar modelo execution de usuario"
```
