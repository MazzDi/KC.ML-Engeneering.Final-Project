import pytest

from models.enum import UserRole
from services.crud.user import create_user


@pytest.mark.api
def test_auth_login_me_logout_flow(client, session):
    u = create_user(
        login="auth_user_01",
        password="Pass12345",
        first_name="A",
        last_name="B",
        role=UserRole.CLIENT,
        session=session,
        is_test=True,
    )

    # not logged in
    r = client.get("/auth/me")
    assert r.status_code == 401

    # login ok
    r = client.post("/auth/login", json={"login": u.login, "password": "Pass12345"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["user_id"] == u.id
    assert body["role"] == "client"

    # me ok
    r = client.get("/auth/me")
    assert r.status_code == 200
    assert r.json()["user_id"] == u.id

    # logout ok
    r = client.post("/auth/logout")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

    # me after logout
    r = client.get("/auth/me")
    assert r.status_code == 401


@pytest.mark.api
def test_auth_login_invalid_credentials(client, session):
    create_user(
        login="auth_user_02",
        password="Pass12345",
        first_name="A",
        last_name="B",
        role=UserRole.CLIENT,
        session=session,
        is_test=True,
    )
    r = client.post("/auth/login", json={"login": "auth_user_02", "password": "wrong"})
    assert r.status_code == 401


