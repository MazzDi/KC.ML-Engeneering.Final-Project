from pydantic import BaseModel, ConfigDict


class ManagerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int


