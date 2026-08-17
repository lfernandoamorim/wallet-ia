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
