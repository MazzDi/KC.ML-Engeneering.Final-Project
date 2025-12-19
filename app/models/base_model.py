from __future__ import annotations
from datetime import datetime
from sqlmodel import Field, SQLModel

class BaseModel(SQLModel):
    """
    Базовые сущности любой модели данных для наследования
    
    Attributes:
        id (int): Уникальный идентификатор сущности
        timestamp (datetime): Временная метка создания сущности
    """
    id: int = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)