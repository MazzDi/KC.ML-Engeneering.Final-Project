from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from models.base_model import BaseModel

if TYPE_CHECKING:
    from models.client import Client


class Score(BaseModel, table=True):
    """
    Событие скоринга: фиксирует рассчитанный скор для пользователя в момент времени.
    """
    user_id: int = Field(index=True, foreign_key="user.id")
    score: float = Field(description="Скоринговый балл / вероятность дефолта")
    Optional["Client"] = Relationship(back_populates="scores")
