from __future__ import annotations

import os
import random
import re
import time
from pathlib import Path
from typing import Iterable

import bcrypt
import pandas as pd
from russian_names import RussianNames
from transliterate import translit
from sqlmodel import SQLModel, Session, select

from database.database import get_database_engine
from models.user import User
from models.client import Client
from models.manager import Manager
from models.credit import Credit  # noqa: F401 (import for SQLModel metadata)
from models.scoring import Score  # noqa: F401 (import for SQLModel metadata)


def _wait_for_db(timeout_s: int = 60) -> None:
    """Ping DB using configured engine until it responds or timeout."""
    engine = get_database_engine()
    start = time.time()
    last_err: Exception | None = None
    while time.time() - start < timeout_s:
        try:
            with engine.connect() as conn:
                conn.exec_driver_sql("SELECT 1")
            return
        except Exception as e:  # noqa: BLE001 - we want to retry on any DB error
            last_err = e
            time.sleep(1)
    raise RuntimeError(f"DB is not ready after {timeout_s}s: {last_err}")


def _ru_to_lat(s: str) -> str:
    try:
        return translit(s, "ru", reversed=True)
    except Exception:
        # Fallback: best-effort plain ASCII
        return s


def _clean_login(login: str) -> str:
    login = login.lower()
    login = re.sub(r"[^a-z0-9_]+", "", login)
    login = re.sub(r"_+", "_", login).strip("_")
    return login


def _make_password(login: str, alias: str = "123") -> str:
    parts = login.split("_", 1)
    if len(parts) == 2 and parts[0] and parts[1]:
        return parts[0][0].upper() + parts[1] + alias
    return login[:1].upper() + login[1:] + alias


def _unique_login(base: str, existing: set[str]) -> str:
    if base not in existing:
        existing.add(base)
        return base
    i = 2
    while True:
        candidate = f"{base}_{i}"
        if candidate not in existing:
            existing.add(candidate)
            return candidate
        i += 1


def _df_clients(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def _credit_history_map(path: str, max_id: int) -> dict[int, list[dict[str, int | str]]]:
    """
    Build mapping: client_id -> list of history items sorted by months_ago ASC.
    CSV has columns: ID, MONTHS_BALANCE (0, -1, -2...), STATUS (C/0/1/.../X).
    We store months_ago as non-negative int where 0 is current month.
    """
    df = pd.read_csv(path)
    df = df[df["ID"].between(1, max_id)]
    # months_ago: convert negative months_balance to positive "months ago"
    df["months_ago"] = (-df["MONTHS_BALANCE"]).astype(int)
    df["status"] = df["STATUS"].astype(str)

    out: dict[int, list[dict[str, int | str]]] = {}
    for client_id, g in df.groupby("ID", sort=False):
        g = g.sort_values("months_ago", ascending=True)
        out[int(client_id)] = [
            {"months_ago": int(m), "status": str(s)}
            for m, s in zip(g["months_ago"].tolist(), g["status"].tolist())
        ]
    return out


def _client_kwargs(row: pd.Series) -> dict:
    return dict(
        code_gender=row.get("CODE_GENDER"),
        flag_own_car=row.get("FLAG_OWN_CAR"),
        flag_own_realty=row.get("FLAG_OWN_REALTY"),
        cnt_children=int(row["CNT_CHILDREN"]),
        amt_income_total=float(row["AMT_INCOME_TOTAL"]),
        name_income_type=row.get("NAME_INCOME_TYPE"),
        name_education_type=row.get("NAME_EDUCATION_TYPE"),
        name_family_status=row.get("NAME_FAMILY_STATUS"),
        name_housing_type=row.get("NAME_HOUSING_TYPE"),
        days_birth=int(row["DAYS_BIRTH"]),
        days_employed=int(row["DAYS_EMPLOYED"]),
        flag_work_phone=int(row["FLAG_WORK_PHONE"]),
        flag_phone=int(row["FLAG_PHONE"]),
        flag_email=int(row["FLAG_EMAIL"]),
        occupation_type=row.get("OCCUPATION_TYPE"),
        cnt_fam_members=int(row["CNT_FAM_MEMBERS"]),
        age_group=row.get("AGE_GROUP"),
    )


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _pick(seq: Iterable[str]) -> str:
    return random.choice(list(seq))


def seed() -> None:
    random.seed(42)
    _wait_for_db(60)

    engine = get_database_engine()
    SQLModel.metadata.create_all(engine)

    n_clients = 1510
    n_managers = 30
    n_admins = 2

    with Session(engine) as session:
        already_seeded = session.exec(select(User).where(User.is_test == True)).first()
        if already_seeded is not None:
            # Backfill manager_id assignment if DB was seeded with clients lacking managers.
            manager_ids = session.exec(select(Manager.user_id).order_by(Manager.user_id)).all()
            if len(manager_ids) == 0:
                print("Seed: already exists, but no managers found. Skipping.")
                return

            credit_history_path = Path(__file__).resolve().parent / "test_data" / "credit_history.csv"
            history_by_client_id = _credit_history_map(str(credit_history_path), max_id=n_clients)

            clients_without_manager = session.exec(
                select(Client).where(Client.manager_id == None).order_by(Client.user_id)  # noqa: E711
            ).all()
            if len(clients_without_manager) == 0:
                # Still may need to backfill credits
                clients_without_manager = []

            for i, client in enumerate(clients_without_manager):
                client.manager_id = manager_ids[i % len(manager_ids)]
            session.commit()

            # Backfill credits: one credit per client (client.user_id == user.id)
            client_ids = session.exec(select(Client.user_id).order_by(Client.user_id)).all()
            existing_credit_client_ids = set(
                session.exec(select(Credit.client_id)).all()
            )
            created = 0
            for client_id in client_ids:
                if client_id in existing_credit_client_ids:
                    continue
                session.add(
                    Credit(
                        client_id=client_id,
                        amount_total=float(random.randint(1, 3_000_000)),
                        annual_rate=0.16,
                        payment_history=history_by_client_id.get(int(client_id), []),
                    )
                )
                created += 1
            session.commit()

            print(
                f"Seed: backfilled manager assignment for clients={len(clients_without_manager)} "
                f"across managers={len(manager_ids)}; created credits={created}."
            )
            return

        used_logins: set[str] = set()
        df_clients_path = Path(__file__).resolve().parent / "test_data" / "df_to_keep.csv"
        df_clients = _df_clients(str(df_clients_path))
        credit_history_path = Path(__file__).resolve().parent / "test_data" / "credit_history.csv"
        history_by_client_id = _credit_history_map(str(credit_history_path), max_id=n_clients)

        total = n_clients + n_managers + n_admins
        rn = RussianNames(
            count=total,
            patronymic=False,
            name_max_len=255,
            surname_max_len=255,
            seed=42,
            output_type="dict",
        )

        mgr_created = 0
        cli_created = 0
        adm_created = 0

        created_client_ids: list[int] = []
        created_manager_ids: list[int] = []

        for i, person in enumerate(rn):
            name = person["name"]
            surname = person["surname"]

            raw_login = f"{_ru_to_lat(name).lower()}_{_ru_to_lat(surname).lower()}"
            login = _clean_login(raw_login) or "user"
            login = _unique_login(login, used_logins)
            password = _make_password(login)

            if i < n_clients:
                role = "client"
                is_admin = False
            elif i < n_clients + n_managers:
                role = "manager"
                is_admin = False
            else:
                role = "admin"
                is_admin = True
            
            # Создание пользователя
            user = User(
                login=login,
                password_hash=_hash_password(password),
                first_name=name,
                last_name=surname,
                role=role,
                is_admin=is_admin,
                is_test=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

            # Создание клиента или менеджера из пользователя
            if role == "client":
                row = df_clients.iloc[cli_created % len(df_clients)]
                session.add(Client(user_id=user.id, **_client_kwargs(row)))
                created_client_ids.append(user.id)
                cli_created += 1
            elif role == "manager":
                session.add(Manager(user_id=user.id))
                created_manager_ids.append(user.id)
                mgr_created += 1
            else:
                adm_created += 1

        session.commit()

        # Аллоцирование клиентов к менеджерам.
        if created_manager_ids:
            for idx, client_user_id in enumerate(created_client_ids):
                client = session.get(Client, client_user_id)
                if client is not None:
                    client.manager_id = created_manager_ids[idx % len(created_manager_ids)]
            session.commit()

        # Создание 1 кредита на каждого клиента + история выплат из credit_history.csv
        for client_user_id in created_client_ids:
            session.add(
                Credit(
                    client_id=client_user_id,
                    amount_total=float(random.randint(1, 3_000_000)),
                    annual_rate=0.16,
                    payment_history=history_by_client_id.get(int(client_user_id), []),
                )
            )
        session.commit()

        print(
            f"Seed: created clients={cli_created}, managers={mgr_created}, admins={adm_created}."
        )
    
if __name__ == "__main__":
    seed()


