"""RabbitMQ publisher for case surveillance events.

Publishes to a topic exchange ``case_events`` with routing keys like
``case.created`` / ``case.confirmed``. A worker (app/workers/notifications.py)
consumes these to send alerts asynchronously.

Degrades gracefully: if the broker is unreachable, publishing logs a warning
instead of failing the request (the alert is best-effort, the case write is not).
"""

import json
import logging

import pika

from app.core.config import settings

logger = logging.getLogger(__name__)

EXCHANGE = "case_events"


def _connect() -> pika.BlockingConnection:
    params = pika.URLParameters(settings.RABBITMQ_URL)
    params.socket_timeout = 2
    return pika.BlockingConnection(params)


def publish_event(routing_key: str, payload: dict) -> None:
    try:
        connection = _connect()
        channel = connection.channel()
        channel.exchange_declare(
            exchange=EXCHANGE, exchange_type="topic", durable=True
        )
        channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=routing_key,
            body=json.dumps(payload, default=str),
            properties=pika.BasicProperties(
                content_type="application/json", delivery_mode=2
            ),
        )
        connection.close()
        logger.info("Published %s: %s", routing_key, payload)
    except Exception as exc:
        logger.warning("Failed to publish %s: %s", routing_key, exc)
