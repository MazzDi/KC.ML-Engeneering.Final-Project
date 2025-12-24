from typing import List, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel


if TYPE_CHECKING:
    from models.client import Client
    from models.user import User
    

class Manager(SQLModel, table=True):
    """
    Дополнительная информация о пользователе, который является сотрудником банка.
    """
    # Manager = уточнённый User: shared primary key (manager.user_id == user.id)
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    # Связи
    user: "User" = Relationship(back_populates="manager")
    clients: List["Client"] = Relationship(back_populates="manager")
    