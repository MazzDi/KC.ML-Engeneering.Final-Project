from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseModel


if TYPE_CHECKING:
    from models.client import Client
    from models.user import User
    

class Employee(table=True):
    """
    Дополнительная информация о пользователе, который является сотрудником банка.
    """
    id: int = Field(foreign_key="user.id", index=True, unique=True)
    # Связи
    user: Optional["User"] = Relationship(back_populates="employee")
    clients: List["Client"] = Relationship(back_populates="employee")
    