import pytest

from models.enum import UserRole
from services.crud.client import create_client
from services.crud.credit import assign_credit
from services.crud.manager import create_manager
from services.crud.user import create_user


@pytest.mark.api
def test_client_credit_requires_auth(client):
    r = client.get("/api/client/credit")
    assert r.status_code == 401


@pytest.mark.api
def test_client_credit_ok(client, session):
    u = create_user(
        login="client_credit_01",
        password="Pass12345",
        first_name="C",
        last_name="L",
        role=UserRole.CLIENT,
        session=session,
        is_test=True,
    )
    c = create_client(user=u, session=session)
    assign_credit(
        client=c,
        amount_total=1234.0,
        annual_rate=0.16,
        payment_history=[{"months_ago": 0, "status": "C"}],
        session=session,
    )

    # login as client
    r = client.post("/auth/login", json={"login": u.login, "password": "Pass12345"})
    assert r.status_code == 200

    r = client.get("/api/client/credit")
    assert r.status_code == 200
    body = r.json()
    assert body["client_id"] == c.user_id
    assert body["amount_total"] == 1234.0


@pytest.mark.api
def test_manager_summary_and_detail(client, session):
    # manager
    mu = create_user(
        login="mgr_01",
        password="Pass12345",
        first_name="M",
        last_name="G",
        role=UserRole.MANAGER,
        session=session,
        is_test=True,
    )
    manager = create_manager(user=mu, session=session)

    # client under manager
    cu = create_user(
        login="cli_01",
        password="Pass12345",
        first_name="Ivan",
        last_name="Ivanov",
        role=UserRole.CLIENT,
        session=session,
        is_test=True,
    )
    c = create_client(user=cu, session=session)
    c.manager_id = manager.user_id
    session.add(c)
    session.commit()

    # login as manager
    r = client.post("/auth/login", json={"login": mu.login, "password": "Pass12345"})
    assert r.status_code == 200

    r = client.get("/api/manager/clients/summary?all=false")
    assert r.status_code == 200
    arr = r.json()
    assert any(x["user_id"] == c.user_id and x["first_name"] == "Ivan" for x in arr)

    r = client.get(f"/api/manager/clients/{c.user_id}")
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["first_name"] == "Ivan"
    assert body["client"]["user_id"] == c.user_id


@pytest.mark.api
def test_manager_score_get_and_rescore(client, session, monkeypatch):
    import services.crud.scoring as scoring_crud

    # manager
    mu = create_user(
        login="mgr_02",
        password="Pass12345",
        first_name="M",
        last_name="G",
        role=UserRole.MANAGER,
        session=session,
        is_test=True,
    )
    manager = create_manager(user=mu, session=session)

    # client under manager
    cu = create_user(
        login="cli_02",
        password="Pass12345",
        first_name="P",
        last_name="Q",
        role=UserRole.CLIENT,
        session=session,
        is_test=True,
    )
    c = create_client(user=cu, session=session)
    c.manager_id = manager.user_id
    session.add(c)
    session.commit()

    # mock RPC
    monkeypatch.setattr(scoring_crud, "_rpc_call", lambda payload, *, timeout_s=15.0: {"status": "success", "proba": 0.25})

    # login as manager
    r = client.post("/auth/login", json={"login": mu.login, "password": "Pass12345"})
    assert r.status_code == 200

    # initially no score
    r = client.get(f"/api/manager/clients/{c.user_id}/score")
    assert r.status_code == 200
    assert r.json() is None

    # rescore creates
    r = client.post(f"/api/manager/clients/{c.user_id}/score", json={})
    assert r.status_code == 200
    assert r.json()["score"] == 0.25

    # now exists
    r = client.get(f"/api/manager/clients/{c.user_id}/score")
    assert r.status_code == 200
    assert r.json()["score"] == 0.25


@pytest.mark.api
def test_role_forbidden(client, session):
    # create client user and login
    u = create_user(
        login="cli_role",
        password="Pass12345",
        first_name="C",
        last_name="L",
        role=UserRole.CLIENT,
        session=session,
        is_test=True,
    )
    create_client(user=u, session=session)
    client.post("/auth/login", json={"login": u.login, "password": "Pass12345"})

    # client cannot call manager endpoints
    assert client.get("/api/manager/clients/summary?all=true").status_code == 403


