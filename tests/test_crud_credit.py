import pytest


@pytest.mark.unit
def test_assign_and_get_credit(session, client_entity):
    from services.crud.credit import assign_credit, get_credit_by_client_id

    credit = assign_credit(
        client=client_entity,
        amount_total=1000.0,
        annual_rate=0.16,
        payment_history=[{"months_ago": 0, "status": "C"}],
        session=session,
    )

    got = get_credit_by_client_id(client_id=client_entity.user_id, session=session)
    assert got is not None
    assert got.id == credit.id
    assert got.client_id == client_entity.user_id
    assert got.payment_history[0]["status"] == "C"


@pytest.mark.unit
def test_credit_unique_constraint(session, client_entity):
    from services.crud.credit import assign_credit

    assign_credit(
        client=client_entity,
        amount_total=1000.0,
        annual_rate=0.16,
        payment_history=[],
        session=session,
    )
    with pytest.raises(Exception):
        assign_credit(
            client=client_entity,
            amount_total=2000.0,
            annual_rate=0.16,
            payment_history=[],
            session=session,
        )


