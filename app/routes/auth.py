from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlmodel import Session

from database.database import get_session
from services.crud.user import get_user_by_login, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    login: str
    password: str


@router.post("/login")
async def login(req: Request, body: LoginRequest, session: Session = Depends(get_session)) -> dict:
    user = get_user_by_login(body.login, session=session)
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    req.session["user_id"] = int(user.id)
    req.session["role"] = str(user.role.value) if hasattr(user.role, "value") else str(user.role)
    redirect = "/ui"
    return {"status": "ok", "user_id": user.id, "role": req.session["role"], "redirect": redirect}


@router.post("/logout")
async def logout(req: Request) -> dict:
    req.session.clear()
    return {"status": "ok"}


@router.get("/me")
async def me(req: Request) -> dict:
    user_id = req.session.get("user_id")
    role = req.session.get("role")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"user_id": user_id, "role": role}


