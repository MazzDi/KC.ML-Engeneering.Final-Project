import pytest


@pytest.mark.api
def test_score_client_endpoint_persists_score(client, session, client_entity, monkeypatch):
    from models.scoring import Score
    import services.crud.scoring as scoring_crud

    # ensure required model features exist
    client_entity.code_gender = "F"
    client_entity.flag_own_car = "N"
    client_entity.flag_own_realty = "N"
    client_entity.cnt_children = 0
    client_entity.amt_income_total = 100000.0
    client_entity.name_income_type = "Working"
    client_entity.name_education_type = "Higher education"
    client_entity.name_family_status = "Married"
    client_entity.name_housing_type = "House / apartment"
    client_entity.days_birth = 10000
    client_entity.days_employed = 1000
    client_entity.flag_work_phone = 0
    client_entity.flag_phone = 0
    client_entity.flag_email = 0
    client_entity.occupation_type = "Unknown"
    client_entity.cnt_fam_members = 2
    client_entity.age_group = "25-35"
    client_entity.days_employed_bin = "1-3 year"
    session.add(client_entity)
    session.commit()
    session.refresh(client_entity)

    def _fake_rpc_call(payload, *, timeout_s=15.0):
        assert payload["client_id"] == client_entity.user_id
        assert "features" in payload
        return {"status": "success", "proba": 0.42}

    monkeypatch.setattr(scoring_crud, "_rpc_call", _fake_rpc_call)

    r = client.post(f"/clients/{client_entity.user_id}/score")
    assert r.status_code == 200
    body = r.json()
    assert body["client_id"] == client_entity.user_id
    assert body["score"] == 0.42

    saved = session.get(Score, body["id"])
    assert saved is not None
    assert saved.client_id == client_entity.user_id
    assert saved.score == 0.42


@pytest.mark.api
def test_score_client_404(client):
    r = client.post("/clients/999999/score")
    assert r.status_code == 404


@pytest.mark.api
def test_score_client_rpc_error_returns_500(client_no_raise, session, client_entity, monkeypatch):
    import services.crud.scoring as scoring_crud

    def _fake_rpc_call(_payload, *, timeout_s=15.0):
        return {"status": "error", "error": "boom"}

    monkeypatch.setattr(scoring_crud, "_rpc_call", _fake_rpc_call)
    r = client_no_raise.post(f"/clients/{client_entity.user_id}/score")
    assert r.status_code == 500


