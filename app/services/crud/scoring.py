import json
import os
import time
import uuid
from typing import Any

import pika
from loguru import logger
from sqlmodel import Session

from models.client import Client
from models.scoring import Score


QUEUE_NAME = "ml_scoring_queue"


def _client_features(client: Client) -> dict[str, Any]:
    """
    Build feature dict in the raw-feature format expected by the current CatBoost model:
    ['code_gender','flag_own_car','flag_own_realty','cnt_children','amt_income_total','name_income_type',
     'name_education_type','name_family_status','name_housing_type','days_birth','days_employed',
     'flag_work_phone','flag_phone','flag_email','occupation_type','cnt_fam_members','age_group','days_employed_bin']
    """
    return {
        "code_gender": client.code_gender,
        "flag_own_car": client.flag_own_car,
        "flag_own_realty": client.flag_own_realty,
        "cnt_children": client.cnt_children,
        "amt_income_total": client.amt_income_total,
        "name_income_type": client.name_income_type,
        "name_education_type": client.name_education_type,
        "name_family_status": client.name_family_status,
        "name_housing_type": client.name_housing_type,
        "days_birth": client.days_birth,
        "days_employed": client.days_employed,
        "flag_work_phone": client.flag_work_phone,
        "flag_phone": client.flag_phone,
        "flag_email": client.flag_email,
        "occupation_type": client.occupation_type,
        "cnt_fam_members": client.cnt_fam_members,
        "age_group": client.age_group,
        "days_employed_bin": client.days_employed_bin,
    }


def _rpc_call(payload: dict[str, Any], *, timeout_s: float = 15.0) -> dict[str, Any]:
    host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    port = int(os.environ.get("RABBITMQ_PORT", "5672"))
    user = os.environ.get("RABBITMQ_USER", "guest")
    password = os.environ.get("RABBITMQ_PASSWORD", "guest")

    params = pika.ConnectionParameters(
        host=host,
        port=port,
        virtual_host="/",
        credentials=pika.PlainCredentials(username=user, password=password),
        heartbeat=30,
        blocked_connection_timeout=2,
    )

    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    result = ch.queue_declare(queue="", exclusive=True)
    callback_queue = result.method.queue

    corr_id = str(uuid.uuid4())
    response: dict[str, Any] | None = None

    def on_resp(_ch, _m, props, body) -> None:
        nonlocal response
        if props.correlation_id != corr_id:
            return
        try:
            response = json.loads(body)
        except Exception:
            response = {"status": "error", "error": "Invalid JSON response from ml-worker"}

    ch.basic_consume(queue=callback_queue, on_message_callback=on_resp, auto_ack=True)
    ch.basic_publish(
        exchange="",
        routing_key=QUEUE_NAME,
        properties=pika.BasicProperties(reply_to=callback_queue, correlation_id=corr_id),
        body=json.dumps(payload),
    )

    started = time.time()
    while response is None and (time.time() - started) < timeout_s:
        conn.process_data_events(time_limit=1)

    try:
        conn.close()
    except Exception:
        pass

    if response is None:
        return {"status": "error", "error": f"ml-worker timeout after {timeout_s}s"}
    return response


def score_client(client: Client, session: Session) -> Score:
    """
    Calls ml-worker and stores resulting score (proba) into Score table.
    """
    payload = {"client_id": client.user_id, "features": _client_features(client)}
    resp = _rpc_call(payload)
    if resp.get("status") != "success":
        raise RuntimeError(f"ml-worker error: {resp}")

    proba = float(resp["proba"])
    score_obj = Score(
        client_id=client.user_id,
        score=proba,
    )
    session.add(score_obj)
    session.commit()
    session.refresh(score_obj)
    logger.info(f"Scored client={client.user_id}: proba={proba}")
    return score_obj


