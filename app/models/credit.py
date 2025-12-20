from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship

from models.base_model import BaseModel

if TYPE_CHECKING:
    from models.client import Client


class Credit(BaseModel, table=True):
    """
    Кредит, привязанный к конкретному пользователю.
    """
    user_id: int = Field(foreign_key="user.id", index=True)
    amount_total: float = Field(description="Первоначально выданная сумма кредита")
    annual_rate: float = Field(description="Годовая процентная ставка в долях (например 0.12)")
    # Связи
    user: Optional["Client"] = Relationship(back_populates="credits")
