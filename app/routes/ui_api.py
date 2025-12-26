from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from database.database import get_session
from models.client import Client
from models.manager import Manager
from schemas.client import ClientRead, ClientUpdate
from schemas.credit import CreditRead
from schemas.manager import ManagerRead
from schemas.scoring import ScoreRead
from services.crud.client import get_client_by_user_id, list_clients, update_client
from services.crud.credit import get_credit_by_client_id
from services.crud.manager import get_manager_by_user_id
from services.crud.scoring import get_latest_score, score_client

router = APIRouter(prefix="/api", tags=["ui-api"])


def _require_auth(req: Request) -> tuple[int, str]:
    user_id = req.session.get("user_id")
    role = req.session.get("role")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return int(user_id), str(role)


@router.get("/client/dashboard")
async def client_dashboard(req: Request, session: Session = Depends(get_session)) -> dict:
    user_id, role = _require_auth(req)
    if role != "client":
        raise HTTPException(status_code=403, detail="Forbidden")

    client = get_client_by_user_id(user_id, session=session)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    manager: Manager | None = None
    if client.manager_id is not None:
        manager = get_manager_by_user_id(client.manager_id, session=session)

    credit = get_credit_by_client_id(client_id=user_id, session=session)
    latest = get_latest_score(client_id=user_id, session=session)

    return {
        "client": ClientRead.model_validate(client),
        "manager": ManagerRead.model_validate(manager) if manager else None,
        "credit": CreditRead.model_validate(credit) if credit else None,
        "score": ScoreRead.model_validate(latest) if latest else None,
    }


@router.post("/client/score", response_model=ScoreRead)
async def client_score(req: Request, session: Session = Depends(get_session)) -> ScoreRead:
    user_id, role = _require_auth(req)
    if role != "client":
        raise HTTPException(status_code=403, detail="Forbidden")
    client = get_client_by_user_id(user_id, session=session)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    s = score_client(client=client, session=session)
    return ScoreRead.model_validate(s)


@router.get("/manager/clients", response_model=list[ClientRead])
async def manager_clients(req: Request, session: Session = Depends(get_session), all: bool = False) -> list[ClientRead]:
    user_id, role = _require_auth(req)
    if role != "manager":
        raise HTTPException(status_code=403, detail="Forbidden")

    manager = get_manager_by_user_id(user_id, session=session)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    clients = list_clients(session=session, manager_id=None if all else manager.user_id)
    return [ClientRead.model_validate(c) for c in clients]


@router.patch("/manager/clients/{client_id}", response_model=ClientRead)
async def manager_update_client(
    client_id: int,
    req: Request,
    body: ClientUpdate,
    session: Session = Depends(get_session),
) -> ClientRead:
    user_id, role = _require_auth(req)
    if role != "manager":
        raise HTTPException(status_code=403, detail="Forbidden")

    manager = get_manager_by_user_id(user_id, session=session)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    client = get_client_by_user_id(client_id, session=session)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    updated = update_client(client, session=session, **body.model_dump(exclude_unset=True))
    return ClientRead.model_validate(updated)


