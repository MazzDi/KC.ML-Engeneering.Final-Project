import pytest


@pytest.mark.unit
def test_dismiss_manager_detaches_clients(session, manager_entity):
    from models.enum import UserRole
    from services.crud.user import create_user
    from services.crud.client import create_client
    from services.crud.manager import dismiss_manager

    c1_user = create_user(
        login="client_01",
        password="Pass123",
        first_name="C1",
        last_name="L",
        role=UserRole.CLIENT,
        session=session,
        is_test=True,
    )
    c2_user = create_user(
        login="client_02",
        password="Pass123",
        first_name="C2",
        last_name="L",
        role=UserRole.CLIENT,
        session=session,
        is_test=True,
    )
    c1 = create_client(user=c1_user, session=session)
    c2 = create_client(user=c2_user, session=session)
    c1.manager_id = manager_entity.user_id
    c2.manager_id = manager_entity.user_id
    session.add(c1)
    session.add(c2)
    session.commit()

    dismiss_manager(manager=manager_entity, session=session)

    session.refresh(c1)
    session.refresh(c2)
    assert c1.manager_id is None
    assert c2.manager_id is None
    assert manager_entity.user.role == UserRole.DISMISSED


