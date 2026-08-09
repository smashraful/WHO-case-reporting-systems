"""Notification worker: consumes case events and sends alerts.

Consumes from the ``case_events`` topic exchange (routing keys ``case.*``) and
dispatches an alert (here: logged as a stub for SMS/email to district officers).

Run::

    python -m app.workers.notifications

Extension point: outbreak detection — on ``case.confirmed``, count confirmed
cases in the same location within a rolling window and escalate if a threshold
is crossed.
"""

import json
import logging

import pika

from app.core.config import settings
from app.core.messaging import EXCHANGE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notifications-worker")

QUEUE = "case_notifications"


def handle_event(routing_key: str, payload: dict) -> None:
    if routing_key == "case.created":
        logger.info(
            "[ALERT] New measles case #%s filed (patient %s) — notifying district officer.",
            payload.get("case_id"),
            payload.get("patient_id"),
        )
    elif routing_key == "case.confirmed":
        logger.info(
            "[ALERT] Case #%s CONFIRMED in location %s — escalating to surveillance team.",
            payload.get("case_id"),
            payload.get("location_id"),
        )
    else:
        logger.info("[EVENT] %s: %s", routing_key, payload)


def _on_message(channel, method, _properties, body) -> None:
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        payload = {"raw": body.decode(errors="replace")}
    handle_event(method.routing_key, payload)
    channel.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    connection = pika.BlockingConnection(pika.URLParameters(settings.RABBITMQ_URL))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key="case.*")
    channel.basic_qos(prefetch_count=10)
    channel.basic_consume(queue=QUEUE, on_message_callback=_on_message)
    logger.info("Notification worker started; waiting for case events...")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()


if __name__ == "__main__":
    main()
