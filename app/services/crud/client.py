from models.user import User
from models.client import Client
from models.manager import Manager
from sqlmodel import Session
from typing import Optional
from loguru import logger
from sqlmodel import select


def create_client(
    user: User,
    session: Session,
    manager: Manager = None,
    code_gender: Optional[str] = None,
    flag_own_car: Optional[str] = None,
    flag_own_realty: Optional[str] = None,
    cnt_children: Optional[int] = None,
    amt_income_total: Optional[float] = None,
    name_income_type: Optional[str] = None,
    name_education_type: Optional[str] = None,
    name_family_status: Optional[str] = None,
    name_housing_type: Optional[str] = None,
    days_birth: Optional[int] = None,
    days_employed: Optional[int] = None,
    flag_work_phone: Optional[int] = None,
    flag_phone: Optional[int] = None,
    flag_email: Optional[int] = None,
    occupation_type: Optional[str] = None,
    cnt_fam_members: Optional[int] = None,
    age_group: Optional[str] = None,
    days_employed_bin: Optional[str] = None,
) -> Client:
    """
    Создание клиента.
    """
    try:
        client = Client(
            user_id=user.id,
            manager_id=manager.user_id if manager else None,
            code_gender=code_gender,
            flag_own_car=flag_own_car,
            flag_own_realty=flag_own_realty,
            cnt_children=cnt_children,
            amt_income_total=amt_income_total,
            name_income_type=name_income_type,
            name_education_type=name_education_type,
            name_family_status=name_family_status,
            name_housing_type=name_housing_type,
            days_birth=days_birth,
            days_employed=days_employed,
            flag_work_phone=flag_work_phone,
            flag_phone=flag_phone,
            flag_email=flag_email,
            occupation_type=occupation_type,
            cnt_fam_members=cnt_fam_members,
            age_group=age_group,
            days_employed_bin=days_employed_bin,
            user=user,
            manager=manager,
        )
        session.add(client)
        session.commit()
        session.refresh(client)
        logger.info(f"Клиент {client.user_id} создан")
        return client
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при создании клиента {client.user_id}: {e}")
        raise

async def assign_manager(
    client: Client,
    manager: Manager,
    session: Session,
) -> Client:
    """
    Назначение менеджера клиенту.
    """
    try:
        client.manager = manager
        session.commit()
        session.refresh(client)
    except Exception as e:
        session.rollback()
        logger.error(f"Ошибка при назначении менеджера {manager.user.login} id: {manager.user.id} клиенту {client.user.login} id: {client.user.id}: {e}")
        raise


def get_client_by_user_id(user_id: int, session: Session) -> Client | None:
    return session.get(Client, user_id)


def list_clients(session: Session, *, manager_id: int | None = None) -> list[Client]:
    q = select(Client)
    if manager_id is not None:
        q = q.where(Client.manager_id == manager_id)
    return list(session.exec(q).all())


def update_client(client: Client, session: Session, **updates) -> Client:
    """
    Частичное обновление полей клиента.
    Разрешаем редактировать только фичи + manager_id.
    """
    allowed = {
        "manager_id",
        "code_gender",
        "flag_own_car",
        "flag_own_realty",
        "cnt_children",
        "amt_income_total",
        "name_income_type",
        "name_education_type",
        "name_family_status",
        "name_housing_type",
        "days_birth",
        "days_employed",
        "flag_work_phone",
        "flag_phone",
        "flag_email",
        "occupation_type",
        "cnt_fam_members",
        "age_group",
        "days_employed_bin",
    }
    for k, v in updates.items():
        if k in allowed and v is not None:
            setattr(client, k, v)
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


def list_client_summaries(session: Session, *, manager_id: int | None = None) -> list[dict]:
    """
    Returns list of {user_id, first_name, last_name} joined from Client->User.
    """
    q = select(Client.user_id, User.first_name, User.last_name).join(User, User.id == Client.user_id)
    if manager_id is not None:
        q = q.where(Client.manager_id == manager_id)
    rows = session.exec(q).all()
    return [{"user_id": int(uid), "first_name": fn, "last_name": ln} for uid, fn, ln in rows]


def get_client_with_user(session: Session, client_id: int) -> tuple[Client, User] | None:
    q = select(Client, User).join(User, User.id == Client.user_id).where(Client.user_id == client_id)
    row = session.exec(q).first()
    if row is None:
        return None
    return row