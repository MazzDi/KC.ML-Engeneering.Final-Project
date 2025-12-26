from enum import Enum

class UserRole(str, Enum):
    """Перечисление ролей пользователей"""
    ADMIN = "admin"
    MANAGER = "manager"
    CLIENT = "client"
    DISMISSED = "dismissed"
    DEFAULT = "default"
