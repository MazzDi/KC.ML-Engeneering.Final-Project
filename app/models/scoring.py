from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseModel

if TYPE_CHECKING:
    from models.client import Client
    from models.user import User
    from models.credit import Credit

class Score(BaseModel, table=True):
    """
    Событие скоринга: фиксирует рассчитанный скор для пользователя в момент времени.
    """
    client_id: int = Field(index=True, foreign_key="client.user_id")
    score: float = Field(description="Скоринговый балл / вероятность дефолта")
    # Связи
    client: Optional["Client"] = Relationship(back_populates="scores")
