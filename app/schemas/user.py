from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    login: str
    first_name: str
    last_name: str
    role: str | None = None
    is_admin: bool
    is_test: bool


