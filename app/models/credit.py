from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship
from models.base_model import BaseModel

if TYPE_CHECKING:
    from models.client import Client


class Credit(BaseModel, table=True):
    """
    Кредит, привязанный к конкретному клиенту.
    """
    client_id: int = Field(foreign_key="client.user_id", index=True)
    amount_total: float = Field(description="Первоначально выданная сумма кредита")
    annual_rate: float = Field(description="Годовая процентная ставка в долях (например 0.12)")
    # Связи
    client: Optional["Client"] = Relationship(back_populates="credits")
