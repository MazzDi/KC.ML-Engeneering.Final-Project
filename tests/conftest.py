import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from api import app
from database.database import get_session
from models.enum import UserRole
from services.crud.user import create_user
from services.crud.client import create_client
from services.crud.manager import create_manager


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture()
def session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture()
def client(session):
    async def _override_get_session():
        yield session

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def client_no_raise(session):
    """
    Same as client(), but returns HTTP 500 responses instead of raising server exceptions.
    Useful for testing error-handling paths.
    """
    async def _override_get_session():
        yield session

    app.dependency_overrides[get_session] = _override_get_session
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def client_user(session):
    return create_user(
        login="client_00001",
        password="Pass123",
        first_name="C",
        last_name="L",
        role=UserRole.CLIENT,
        session=session,
        is_test=True,
    )


@pytest.fixture()
def manager_user(session):
    return create_user(
        login="manager_00001",
        password="Pass123",
        first_name="M",
        last_name="N",
        role=UserRole.MANAGER,
        session=session,
        is_test=True,
    )


@pytest.fixture()
def client_entity(session, client_user):
    # minimal viable client row
    return create_client(user=client_user, session=session)


@pytest.fixture()
def manager_entity(session, manager_user):
    return create_manager(user=manager_user, session=session)


