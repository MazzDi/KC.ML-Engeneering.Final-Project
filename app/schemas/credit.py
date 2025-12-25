from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CreditRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    client_id: int
    amount_total: float
    annual_rate: float
    payment_history: list[dict]


