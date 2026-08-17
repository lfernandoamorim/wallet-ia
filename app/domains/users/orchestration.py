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
