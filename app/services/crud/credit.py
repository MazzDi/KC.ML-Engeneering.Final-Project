from models.client import Client
from models.credit import Credit
from sqlmodel import Session
from loguru import logger
from typing import Any
from sqlmodel import select


def assign_credit(
    client: Client,
    amount_total: float,
    annual_rate: float,
    payment_history: list[dict[str, Any]],
    session: Session,
) -> Credit:
    """
    Назначение кредита клиенту.
    """
    try:
        credit = Credit(
            client_id=client.user_id,
            amount_total=amount_total,
            annual_rate=annual_rate,
            payment_history=payment_history,
            client=client,
        )
        session.add(credit)
        session.commit()
        session.refresh(credit)
        logger.info(f"Кредит для клиента {credit.client_id} id: {credit.id} создан")
        return credit
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при создании кредита для клиента {client.user_id}: {e}")
        raise


def get_credit_by_client_id(
    client_id: int,
    session: Session,
) -> Credit | None:
    """
    Получить кредит по client_id (user_id клиента).
    """
    return session.exec(select(Credit).where(Credit.client_id == client_id)).first()