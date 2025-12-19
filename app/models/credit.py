from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseModel

if TYPE_CHECKING:
    from models.user import User


class Credit(BaseModel, table=True):
    """
    Текущий (активный) кредит пользователя.
    Содержит основную финансовую информацию: сумма, тело, проценты, ставка, срок.
    """

    user_id: Optional[int] = Field(default=None, index=True)

    amount_total: float = Field(description="Первоначально выданная сумма кредита")
    principal_outstanding: float = Field(description="Остаток тела кредита")
    interest_outstanding: float = Field(description="Накопленные/неуплаченные проценты")

    annual_rate: float = Field(description="Годовая процентная ставка в долях (например 0.12)")
    term_months: int = Field(description="Срок кредита в месяцах", ge=1)

    issued_at: date = Field(default_factory=date.today, description="Дата выдачи кредита")
    due_at: Optional[date] = Field(default=None, description="Дата планового завершения")

    status: str = Field(default="active", max_length=32, description="active|closed|delinquent")

    history: List["CreditHistory"] = Relationship(back_populates="credit")
    user: Optional["User"] = Relationship(back_populates="credits")


class CreditHistory(BaseModel, table=True):
    """
    История погашений по кредиту.
    Каждая запись отражает платеж: дата, сумма, разбиение на тело/проценты, остаток тела после платежа.
    """

    credit_id: int = Field(foreign_key="credit.id", index=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", index=True)

    payment_date: date = Field(default_factory=date.today)
    payment_amount: float = Field(description="Общая сумма платежа")
    principal_paid: float = Field(default=0.0, description="Погашенное тело")
    interest_paid: float = Field(default=0.0, description="Уплаченные проценты")
    principal_balance_after: float = Field(description="Остаток тела после платежа")

    credit: Optional[Credit] = Relationship(back_populates="history")
    user: Optional["User"] = Relationship(back_populates="credit_histories")


# Удобный алиас для списка кредитов
CreditList = List[Credit]

