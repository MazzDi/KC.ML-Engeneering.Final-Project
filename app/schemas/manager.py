from pydantic import BaseModel, ConfigDict


class ManagerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int


class ManagerSummary(BaseModel):
    user_id: int
    first_name: str
    last_name: str


