import json
import sys
import time
from pathlib import Path

import pandas as pd
import pika
from catboost import CatBoostClassifier
from catboost import Pool
from loguru import logger

from ml_worker.config import get_settings

# Logging
logger.remove()
logger.add(sys.stderr, level="INFO")

QUEUE_NAME = "ml_scoring_queue"
MODEL_PATH = Path(__file__).resolve().parent / "model.cbm"

EXPECTED_FEATURES = [
    "code_gender",
    "flag_own_car",
    "flag_own_realty",
    "cnt_children",
    "amt_income_total",
    "name_income_type",
    "name_education_type",
    "name_family_status",
    "name_housing_type",
    "days_birth",
    "days_employed",
    "flag_work_phone",
    "flag_phone",
    "flag_email",
    "occupation_type",
    "cnt_fam_members",
    "age_group",
    "days_employed_bin",
]

def _load_model() -> CatBoostClassifier:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"CatBoost model file not found at {MODEL_PATH}. "
            f"Put your .cbm model there (e.g. model.cbm)."
        )
    model = CatBoostClassifier()
    model.load_model(str(MODEL_PATH))
    return model


model = _load_model()
MODEL_FEATURES = list(getattr(model, "feature_names_", []) or [])
if MODEL_FEATURES:
    logger.info(f"Model expects {len(MODEL_FEATURES)} features: {MODEL_FEATURES}")
else:
    logger.warning("Model has no feature_names_; will use EXPECTED_FEATURES order.")


def _predict(payload: dict) -> dict:
    """
    Expected request payload:
      {
        "client_id": 123,              # optional, echoed back
        "features": { "f1": 1, ... }   # required
      }
    Response:
      { "client_id": 123, "proba": 0.42, "pred": 0, "status": "success" }
    """
    features = payload.get("features") or {}
    if not isinstance(features, dict):
        raise TypeError("payload.features must be a dict")

    # Prefer model-declared order (feature_names_), fallback to the expected API order.
    columns = MODEL_FEATURES if MODEL_FEATURES else EXPECTED_FEATURES
    row = {c: features.get(c) for c in columns}
    df = pd.DataFrame([row], columns=columns)

    proba = float(model.predict_proba(df)[0][1])
    pred = int(proba >= 0.5)

    return {
        "client_id": payload.get("client_id"),
        "proba": proba,
        "pred": pred,
        "status": "success",
    }


def main() -> None:
    settings = get_settings()
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=int(settings.RABBITMQ_PORT),
            virtual_host="/",
            credentials=pika.PlainCredentials(
                username=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASSWORD,
            ),
            heartbeat=30,
            blocked_connection_timeout=2,
        )
    )

    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=False)

    def send_result(result_data: dict, properties: pika.BasicProperties) -> None:
        channel.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            body=json.dumps(result_data),
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
        )

    def on_request(ch, method, properties, body) -> None:
        started = time.time()
        try:
            payload = json.loads(body)
            result = _predict(payload)
            result["processing_time"] = time.time() - started
            send_result(result, properties)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.exception(f"ml_worker error: {e}")
            try:
                send_result(
                    {"status": "error", "error": str(e), "processing_time": time.time() - started},
                    properties,
                )
            except Exception:
                pass
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_request, auto_ack=False)
    channel.start_consuming()


if __name__ == "__main__":
    main()