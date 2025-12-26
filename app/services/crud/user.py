from models.user import User
from models.enum import UserRole
from sqlmodel import Session
import bcrypt
from loguru import logger


def create_user(
    login: str,
    password: str,
    first_name: str,
    last_name: str,
    role: UserRole,
    session: Session,
    is_admin: bool = False,
    is_test: bool = False
) -> User:
    """
    Создание пользователя.
    """
    # Создание пользователя
    user = User(
        login=login,
        password_hash= hash_password(password),
        first_name=first_name,
        last_name=last_name,
        role=role,
        is_admin=is_admin,
        is_test=True,
    )
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"Пользователь {user.login} id: {user.id} создан")
        return user
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя {user.login} id: {user.id}: {e}")
        raise

def get_user_by_id(id: int, session: Session) -> User:
    """
    Получить юзера по айдишнику.
    """
    try:
        user = session.get(User, id)
        if not user:
            error_msg = f"Пользователя с ID {id} не существует"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return user
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя по ID {id}: {e}")
        raise

def delete_user(id: int, session: Session) -> bool:
    """
    Удаление пользователя по id.
    """
    try:
        user = get_user_by_id(id, session)
        if user:
            session.delete(user)
            session.commit()
            logger.info(f"Пользователь {user.login} id: {user.id} удален")
            return True
        logger.warning(f"Пользователь с ID {id} не найден")
        return False
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при удалении пользователя {user.login} id: {user.id}: {e}")
        raise


def hash_password(password: str) -> str:
    """
    Хеширование пароля с использованием bcrypt.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Проверка пароля.
    """
    return bcrypt.checkpw(password.encode(), hashed_password.encode())
