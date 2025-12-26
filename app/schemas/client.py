from pydantic import BaseModel, ConfigDict


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    manager_id: int | None = None
    code_gender: str | None = None
    flag_own_car: str | None = None
    flag_own_realty: str | None = None
    cnt_children: int | None = None
    amt_income_total: float | None = None
    name_income_type: str | None = None
    name_education_type: str | None = None
    name_family_status: str | None = None
    name_housing_type: str | None = None
    days_birth: int | None = None
    days_employed: int | None = None
    flag_work_phone: int | None = None
    flag_phone: int | None = None
    flag_email: int | None = None
    occupation_type: str | None = None
    cnt_fam_members: int | None = None
    age_group: str | None = None
    days_employed_bin: str | None = None


class ClientUpdate(BaseModel):
    """
    Patch schema for manager UI.
    All fields optional.
    """
    manager_id: int | None = None
    code_gender: str | None = None
    flag_own_car: str | None = None
    flag_own_realty: str | None = None
    cnt_children: int | None = None
    amt_income_total: float | None = None
    name_income_type: str | None = None
    name_education_type: str | None = None
    name_family_status: str | None = None
    name_housing_type: str | None = None
    days_birth: int | None = None
    days_employed: int | None = None
    flag_work_phone: int | None = None
    flag_phone: int | None = None
    flag_email: int | None = None
    occupation_type: str | None = None
    cnt_fam_members: int | None = None
    age_group: str | None = None
    days_employed_bin: str | None = None


class ClientSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    first_name: str
    last_name: str


