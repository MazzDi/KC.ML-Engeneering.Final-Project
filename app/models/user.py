from __future__ import annotations
from sqlmodel import Field, Relationship
from typing import List, Optional
import re
from typing import TYPE_CHECKING
from pydantic import field_validator
import bcrypt
from models.base_model import BaseModel
from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from models.scoring import Score
    from models.credit import Credit


class User(BaseModel):
    """
    Класс для представления пользователя.
    """
    login: str = Field(unique=True, index=True, min_length=5, max_length=255)
    password_hash: str = Field(min_length=5, max_length=255)
    
    @field_validator("login")
    @classmethod
    def validate_login(cls, login: str) -> str:
        """Проверяет формат логина адреса"""
        if not re.match(r"^[a-zA-Z0-9]+$", login):
            raise ValueError("Неверный формат login")
        return login
    
    def auth_pwd_validate(self, password: str) -> bool:
        """
        Проверяет что переданный пароль соответствует актуальному паролю юзера.
        
        Args:
            user: объект текущего пользователя
            password: строка для сравнения с паролем
        
        Returns:
            bool: возвращает True, если соответствует, иначе - ошибка
        """
        if not bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8")):
            raise ValueError("Некорректный пароль")
        return True

class Client(User, table=True):
    """
    Клиент: содержит анкетные признаки, необходимые для скоринга.
    """
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
    # Связи
    manager: Optional["Manager"] = Relationship(back_populates="clients")
    scores: List["Score"] = Relationship(back_populates="user")
    credits: List["Credit"] = Relationship(back_populates="user")

class Admin(User, table=True):
    """
    Администратор: управляет доступами и настройками системы.
    """
    role: str = Field(default="admin", max_length=20)
    is_actual: bool = Field(default=True)
    permissions: Optional[str] = Field(
        default=None, max_length=255
    )  # строка/JSON со списком прав

class Manager(User, table=True):
    """
    Кредитный менеджер: отвечает за обработку заявок и ведение клиентов.
    """
    role: str = Field(default="manager", max_length=20)
    is_actual: bool = Field(default=True)
    permissions: Optional[str] = Field(
        default=None, max_length=255
    )  # строка/JSON со списком прав
    clients: List["Client"] = Relationship(back_populates="manager")
