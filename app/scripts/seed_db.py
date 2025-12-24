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
            print("Seed: already exists (found test users). Skipping.")
            return

        used_logins: set[str] = set()
        df_clients_path = Path(__file__).resolve().parent / "test_data" / "df_to_keep.csv"
        df_clients = _df_clients(str(df_clients_path))

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
                cli_created += 1
            elif role == "manager":
                session.add(Manager(user_id=user.id))
                mgr_created += 1
            else:
                adm_created += 1

        session.commit()
        print(
            f"Seed: created clients={cli_created}, managers={mgr_created}, admins={adm_created}."
        )


if __name__ == "__main__":
    seed()


