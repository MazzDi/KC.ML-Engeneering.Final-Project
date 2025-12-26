from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    client_id: int
    score: float


