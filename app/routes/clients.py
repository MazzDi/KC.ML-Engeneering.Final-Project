from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from database.database import get_session
from models.client import Client
from schemas.client import ClientRead
from schemas.credit import CreditRead
from schemas.scoring import ScoreRead
from services.crud.credit import get_credit_by_client_id
from services.crud.scoring import score_client

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/{user_id}", response_model=ClientRead)
async def get_client(user_id: int, session: Session = Depends(get_session)) -> ClientRead:
    client = session.get(Client, user_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return ClientRead.model_validate(client)


@router.get("/{user_id}/credits", response_model=list[CreditRead])
async def get_client_credits(user_id: int, session: Session = Depends(get_session)) -> list[CreditRead]:
    # Ensure client exists
    client = session.get(Client, user_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")

    credit = get_credit_by_client_id(client_id=user_id, session=session)
    if credit is None:
        return []
    return [CreditRead.model_validate(credit)]


@router.post("/{user_id}/score", response_model=ScoreRead)
async def score_client_endpoint(user_id: int, session: Session = Depends(get_session)) -> ScoreRead:
    client = session.get(Client, user_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    score_obj = score_client(client=client, session=session)
    return ScoreRead.model_validate(score_obj)


