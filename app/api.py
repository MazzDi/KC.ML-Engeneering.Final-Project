from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session

from database.database import get_session
from services.crud.credit import get_credit_by_client_id
from models.user import User
from models.client import Client  # noqa: F401
from models.manager import Manager  # noqa: F401
from models.credit import Credit  # noqa: F401
from models.scoring import Score  # noqa: F401
from schemas.user import UserRead
from schemas.client import ClientRead
from schemas.manager import ManagerRead
from schemas.credit import CreditRead

app = FastAPI(title="Credit Scoring API")


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)) -> UserRead:
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead.model_validate(user)


@app.get("/clients/{user_id}", response_model=ClientRead)
def get_client(user_id: int, session: Session = Depends(get_session)) -> ClientRead:
    client = session.get(Client, user_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientRead.model_validate(client)


@app.get("/clients/{user_id}/credits", response_model=list[CreditRead])
def get_client_credits(user_id: int, session: Session = Depends(get_session)) -> list[CreditRead]:
    # Ensure client exists
    client = session.get(Client, user_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    credit = get_credit_by_client_id(client_id=user_id, session=session)
    if credit is None:
        return []
    return [CreditRead.model_validate(credit)]


@app.get("/managers/{user_id}", response_model=ManagerRead)
def get_manager(user_id: int, session: Session = Depends(get_session)) -> ManagerRead:
    manager = session.get(Manager, user_id)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")
    return ManagerRead.model_validate(manager)


@app.get("/managers/{user_id}/clients", response_model=list[ClientRead])
def get_manager_clients(user_id: int, session: Session = Depends(get_session)) -> list[ClientRead]:
    # Ensure manager exists (otherwise return 404 instead of empty list)
    manager = session.get(Manager, user_id)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    from sqlmodel import select  # local import to keep module top small

    clients = session.exec(select(Client).where(Client.manager_id == user_id)).all()
    return [ClientRead.model_validate(c) for c in clients]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


