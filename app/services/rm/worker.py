import json
import sys
import time

import pika
from loguru import logger

from ml_worker.constants import ModelTypes
from ml_worker.config import get_settings
from ml_worker.embedding import EmbeddingGenerator

# Logging
logger.remove()
logger.add(sys.stderr, level="INFO")

QUEUE_NAME = "rm_task_queue"

# Embedding model for RM service
embedding_generator = EmbeddingGenerator(ModelTypes.MULTILINGUAL.value)


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
            text = payload.get("text")
            if not isinstance(text, str) or not text.strip():
                raise ValueError("Request must contain non-empty 'text'")

            emb = embedding_generator.get_embedding(text)
            result = {
                "embedding": emb,
                "status": "success",
                "processing_time": time.time() - started,
            }
            send_result(result, properties)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.exception(f"rm_worker error: {e}")
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
    logger.info(f"rm_worker: waiting for RPC requests on queue '{QUEUE_NAME}'")
    channel.start_consuming()


if __name__ == "__main__":
    main()


