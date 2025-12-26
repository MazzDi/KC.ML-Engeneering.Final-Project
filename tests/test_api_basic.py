import pytest


@pytest.mark.api
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

@pytest.mark.api
def test_get_user_client_manager_endpoints(client, session, client_user, client_entity, manager_entity):
    # attach client to manager
    client_entity.manager_id = manager_entity.user_id
    session.add(client_entity)
    session.commit()

    r = client.get(f"/users/{client_user.id}")
    assert r.status_code == 200
    assert r.json()["id"] == client_user.id

    r = client.get(f"/clients/{client_entity.user_id}")
    assert r.status_code == 200
    assert r.json()["user_id"] == client_entity.user_id

    r = client.get(f"/managers/{manager_entity.user_id}")
    assert r.status_code == 200
    assert r.json()["user_id"] == manager_entity.user_id

    r = client.get(f"/managers/{manager_entity.user_id}/clients")
    assert r.status_code == 200
    assert [x["user_id"] for x in r.json()] == [client_entity.user_id]


@pytest.mark.api
@pytest.mark.parametrize(
    "path",
    [
        "/users/999999",
        "/clients/999999",
        "/managers/999999",
        "/managers/999999/clients",
    ],
)
def test_404s(client, path):
    assert client.get(path).status_code == 404


@pytest.mark.api
def test_manager_clients_empty(client, manager_entity):
    r = client.get(f"/managers/{manager_entity.user_id}/clients")
    assert r.status_code == 200
    assert r.json() == []


