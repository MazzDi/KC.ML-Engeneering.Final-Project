from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.scoring import Score
    from models.credit import Credit
    from models.manager import Manager
    from models.user import User


class Client(SQLModel, table=True):
    """
    Клиент: содержит анкетные признаки, необходимые для скоринга.
    """
    # ID
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    manager_id: Optional[int] = Field(default=None, foreign_key="manager.user_id", index=True)
    # Анкетные признаки
    code_gender: Optional[str] = Field(default=None, max_length=10)
    flag_own_car: Optional[str] = Field(default=None, max_length=5)
    flag_own_realty: Optional[str] = Field(default=None, max_length=5)
    cnt_children: Optional[int] = Field(default=None, ge=0)
    amt_income_total: Optional[float] = Field(default=None, ge=0)
    name_income_type: Optional[str] = Field(default=None, max_length=50)
    name_education_type: Optional[str] = Field(default=None, max_length=50)
    name_family_status: Optional[str] = Field(default=None, max_length=50)
    name_housing_type: Optional[str] = Field(default=None, max_length=50)
    days_birth: Optional[int] = Field(default=None)
    days_employed: Optional[int] = Field(default=None)
    flag_work_phone: Optional[int] = Field(default=None)
    flag_phone: Optional[int] = Field(default=None)
    flag_email: Optional[int] = Field(default=None)
    occupation_type: Optional[str] = Field(default=None, max_length=50)
    cnt_fam_members: Optional[int] = Field(default=None, ge=0)
    age_group: Optional[str] = Field(default=None, max_length=20)
    days_employed_bin: Optional[str] = Field(default=None, max_length=20)
    # Связи
    user: "User" = Relationship(back_populates="client")
    manager: Optional["Manager"] = Relationship(back_populates="clients")
    credits: List["Credit"] = Relationship(back_populates="client")
    scores: List["Score"] = Relationship(back_populates="client")
