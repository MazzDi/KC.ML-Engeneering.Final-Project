from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from database.database import get_session
from models.user import User
from schemas.user import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: Session = Depends(get_session)) -> UserRead:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


