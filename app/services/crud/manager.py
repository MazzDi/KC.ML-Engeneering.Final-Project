from loguru import logger
from sqlmodel import Session
from sqlmodel import select
from models.manager import Manager
from models.client import Client
from models.user import User
from models.enum import UserRole


def create_manager(
    user: User,
    session: Session,
) -> Manager:
    """
    Создание менеджера.
    """
    try:
        manager = Manager(user_id=user.id, user=user)
        session.add(manager)
        session.commit()
        session.refresh(manager)
        logger.info(f"Менеджер {user.login} id: {user.id} создан")
        return manager
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при создании менеджера {user.login} id: {user.id}: {e}")
        raise

def dismiss_manager(
    manager: Manager,
    session: Session,
) -> Manager:
    """
    Увольнение менеджера.
    """
    try:
        # Detach all clients from this manager (single transaction)
        clients = session.exec(
            select(Client).where(Client.manager_id == manager.user_id)
        ).all()
        for client in clients:
            client.manager = None
            client.manager_id = None

        manager.user.role = UserRole.DISMISSED
        session.commit()
        session.refresh(manager)
        logger.info(f"Менеджер {manager.user.login} id: {manager.user.id} уволен")
        return manager
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при увольнении менеджера {manager.user.login} id: {manager.user.id}: {e}")
        raise


def get_manager_by_user_id(user_id: int, session: Session) -> Manager | None:
    return session.get(Manager, user_id)


def get_manager_summary(manager_id: int, session: Session) -> dict | None:
    """
    Returns {user_id, first_name, last_name} for manager.
    """
    q = (
        select(Manager.user_id, User.first_name, User.last_name)
        .join(User, User.id == Manager.user_id)
        .where(Manager.user_id == manager_id)
    )
    row = session.exec(q).first()
    if row is None:
        return None
    uid, fn, ln = row
    return {"user_id": int(uid), "first_name": fn, "last_name": ln}