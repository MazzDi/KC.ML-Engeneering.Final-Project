from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional

class BaseModel(SQLModel):
    """
    Базовые сущности любой модели данных для наследования
    
    Attributes:
        id (int): Уникальный идентификатор сущности
        timestamp (datetime): Временная метка создания сущности
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)