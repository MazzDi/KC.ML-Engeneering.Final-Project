from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from database.database import get_session
from models.client import Client
from models.manager import Manager
from schemas.client import ClientRead, ClientSummary, ClientUpdate
from schemas.credit import CreditRead
from schemas.manager import ManagerRead, ManagerSummary
from schemas.scoring import ScoreRead
from services.crud.client import (
    get_client_by_user_id,
    get_client_with_user,
    list_client_summaries,
    list_clients,
    update_client,
)
from services.crud.credit import get_credit_by_client_id
from services.crud.manager import get_manager_by_user_id, get_manager_summary
from services.crud.scoring import get_latest_score, score_client
from schemas.user import UserRead

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

    manager_summary: dict | None = None
    if client.manager_id is not None:
        manager_summary = get_manager_summary(client.manager_id, session=session)

    credit = get_credit_by_client_id(client_id=user_id, session=session)
    latest = get_latest_score(client_id=user_id, session=session)

    return {
        "client": ClientRead.model_validate(client),
        "manager": ManagerSummary(**manager_summary) if manager_summary else None,
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


@router.get("/client/credit", response_model=CreditRead | None)
async def client_credit(req: Request, session: Session = Depends(get_session)) -> CreditRead | None:
    user_id, role = _require_auth(req)
    if role != "client":
        raise HTTPException(status_code=403, detail="Forbidden")
    credit = get_credit_by_client_id(client_id=user_id, session=session)
    return CreditRead.model_validate(credit) if credit else None


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


@router.get("/manager/clients/summary", response_model=list[ClientSummary])
async def manager_clients_summary(
    req: Request, session: Session = Depends(get_session), all: bool = False
) -> list[ClientSummary]:
    user_id, role = _require_auth(req)
    if role != "manager":
        raise HTTPException(status_code=403, detail="Forbidden")

    manager = get_manager_by_user_id(user_id, session=session)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    rows = list_client_summaries(session=session, manager_id=None if all else manager.user_id)
    return [ClientSummary(**r) for r in rows]


@router.get("/manager/clients/{client_id}")
async def manager_client_detail(
    client_id: int,
    req: Request,
    session: Session = Depends(get_session),
) -> dict:
    user_id, role = _require_auth(req)
    if role != "manager":
        raise HTTPException(status_code=403, detail="Forbidden")

    manager = get_manager_by_user_id(user_id, session=session)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    row = get_client_with_user(session=session, client_id=client_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Client not found")
    client, user = row
    return {
        "client": ClientRead.model_validate(client),
        "user": UserRead.model_validate(user),
    }


@router.get("/manager/clients/{client_id}/score", response_model=ScoreRead | None)
async def manager_client_score(
    client_id: int,
    req: Request,
    session: Session = Depends(get_session),
) -> ScoreRead | None:
    user_id, role = _require_auth(req)
    if role != "manager":
        raise HTTPException(status_code=403, detail="Forbidden")
    manager = get_manager_by_user_id(user_id, session=session)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    s = get_latest_score(client_id=client_id, session=session)
    return ScoreRead.model_validate(s) if s else None


@router.post("/manager/clients/{client_id}/score", response_model=ScoreRead)
async def manager_client_rescore(
    client_id: int,
    req: Request,
    session: Session = Depends(get_session),
) -> ScoreRead:
    user_id, role = _require_auth(req)
    if role != "manager":
        raise HTTPException(status_code=403, detail="Forbidden")
    manager = get_manager_by_user_id(user_id, session=session)
    if manager is None:
        raise HTTPException(status_code=404, detail="Manager not found")

    client = get_client_by_user_id(client_id, session=session)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    s = score_client(client=client, session=session)
    return ScoreRead.model_validate(s)


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


