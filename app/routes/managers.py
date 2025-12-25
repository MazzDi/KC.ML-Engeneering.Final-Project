from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from database.database import get_session
from models.client import Client
from models.manager import Manager
from schemas.client import ClientRead
from schemas.manager import ManagerRead

router = APIRouter(prefix="/managers", tags=["managers"])


@router.get("/{user_id}", response_model=ManagerRead)
def get_manager(user_id: int, session: Session = Depends(get_session)) -> ManagerRead:
    manager = session.get(Manager, user_id)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")
    return ManagerRead.model_validate(manager)


@router.get("/{user_id}/clients", response_model=list[ClientRead])
def get_manager_clients(user_id: int, session: Session = Depends(get_session)) -> list[ClientRead]:
    # Ensure manager exists (otherwise return 404 instead of empty list)
    manager = session.get(Manager, user_id)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    clients = session.exec(select(Client).where(Client.manager_id == user_id)).all()
    return [ClientRead.model_validate(c) for c in clients]


