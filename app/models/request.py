from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlmodel import Field

from models.base_model import BaseModel


class ChangeEvent(BaseModel, table=True):
    """
    Событие изменения характеристик клиента (например, пола, возраста, статуса занятости и т.п.).
    """

    user_id: Optional[int] = Field(default=None, index=True)

    field_name: str = Field(max_length=64, description="Название изменённого поля")
    old_value: Optional[str] = Field(default=None, description="Значение до изменения")
    new_value: Optional[str] = Field(default=None, description="Значение после изменения")
    changed_at: datetime = Field(default_factory=datetime.utcnow, description="Время изменения")

    comment: Optional[str] = Field(default=None, max_length=255, description="Комментарий/причина")


# Удобный алиас для списка событий
ChangeLog = List[ChangeEvent]

