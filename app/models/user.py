from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship
from typing import Optional
import re
from typing import TYPE_CHECKING
from pydantic import field_validator
from models.base_model import BaseModel
from models.enum import UserRole

if TYPE_CHECKING:
    from models.client import Client
    from models.manager import Manager


class User(BaseModel, table=True):
    """
    Класс для представления пользователя.
    """
    login: str = Field(unique=True, index=True, min_length=5, max_length=255)
    password_hash: str = Field(min_length=5, max_length=255)
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    role: UserRole = Field(
        default=UserRole.DEFAULT,
        sa_column=Column(
            SAEnum(
                UserRole,
                name="userrole",
                values_callable=lambda enum: [e.value for e in enum],
            ),
            nullable=False,
        ),
    )
    is_admin: bool = Field(default=False)
    is_test: bool = Field(default=False)
    # Связи
    client: Optional["Client"] = Relationship(back_populates="user")
    manager: Optional["Manager"] = Relationship(back_populates="user")

    @field_validator("login")
    @classmethod
    def validate_login(cls, login: str) -> str:
        """Проверяет формат логина адреса"""
        if not re.match(r"^[a-zA-Z0-9_]+$", login):
            raise ValueError("Неверный формат логина")
        return login
    
    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, first_name: str) -> str:
        """Проверяет формат имени пользователя"""
        if not re.match(r"^[а-яА-ЯёЁ]+$", first_name):
            raise ValueError("Неверный формат имени")
        return first_name
    
    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, last_name: str) -> str:
        """Проверяет формат фамилии пользователя"""
        if not re.match(r"^[а-яА-ЯёЁ]+$", last_name):
            raise ValueError("Неверный формат фамилии")
        return last_name
