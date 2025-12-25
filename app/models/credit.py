from typing import Any, Optional, TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship
from models.base_model import BaseModel

if TYPE_CHECKING:
    from models.client import Client


class Credit(BaseModel, table=True):
    """
    Кредит, привязанный к конкретному клиенту.
    """
    client_id: int = Field(foreign_key="client.user_id", index=True, unique=True)
    amount_total: float = Field(description="Первоначально выданная сумма кредита")
    annual_rate: float = Field(description="Годовая процентная ставка в долях (например 0.12)")
    # История выплат из credit_history.csv (по месяцам относительно текущего: 0 = текущий месяц)
    payment_history: list[dict[str, Any]] = Field(
        default_factory=list,
        sa_column=Column(JSONB, nullable=False),
        description="Список объектов вида {months_ago: int, status: str}",
    )
    # Связи
    client: Optional["Client"] = Relationship(back_populates="credits")
