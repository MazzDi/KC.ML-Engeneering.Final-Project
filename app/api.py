from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session

from database.database import get_session
from models.user import User
from models.client import Client  # noqa: F401
from models.manager import Manager  # noqa: F401
from models.credit import Credit  # noqa: F401
from models.scoring import Score  # noqa: F401

app = FastAPI(title="Credit Scoring API")


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    login: str
    first_name: str
    last_name: str
    role: str | None = None
    is_admin: bool
    is_test: bool


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)) -> UserRead:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


