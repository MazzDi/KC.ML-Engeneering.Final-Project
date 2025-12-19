from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseModel

if TYPE_CHECKING:
    from models.user import User


class Score(BaseModel, table=True):
    """
    Событие скоринга: фиксирует рассчитанный скор для пользователя в момент времени.
    """

    user_id: Optional[int] = Field(default=None, index=True, foreign_key="user.id")
    score: float = Field(description="Скоринговый балл / вероятность дефолта")
    scored_at: datetime = Field(default_factory=datetime.utcnow, description="Время расчёта скоринга")
    user: Optional["User"] = Relationship(back_populates="scores")


# Алиас для истории скоринга
ScoringHistory = List[Score]

