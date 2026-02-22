import json
import logging
import os
import signal
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional
import django
from confluent_kafka import Consumer, KafkaError
from django.utils.dateparse import parse_datetime
from django.db import close_old_connections

from subapps.kafka.consumers.accounts import handle_institution_user_event, handle_examiner_onboarded_event
from subapps.kafka.consumers.subscriptions import handle_conversation_started_event

logger = logging.getLogger(__name__)



BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
GROUP_ID = os.getenv("KAFKA_CONSUMER_GROUP", "user-consumer")
TOPICS = [
    topic.strip()
    for topic in os.getenv("KAFKA_TOPICS", "institution.user.updated,conversation.started,examiner_onboarded").split(",")
    if topic.strip()
]


def build_consumer() -> Consumer:
    config = {
        "bootstrap.servers": BOOTSTRAP,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        "enable.auto.commit": False,
        "auto.commit.interval.ms": 1000,
    }
    return Consumer(config)


def log_message(message, payload):
    print(
        f"[{message.topic()}] partition={message.partition()} offset={message.offset()} "
        f"key={message.key()} value={payload}"
    )

def parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    parsed = parse_datetime(value)
    return parsed


EVENT_HANDLERS: dict[str, Callable[[Dict[str, Any]], None]] = {
    "institution.user.updated": handle_institution_user_event,
    "conversation.started": handle_conversation_started_event,
    "examiner_onboarded": handle_examiner_onboarded_event,
}


def handle_assessment_event(topic: str, payload: Dict[str, Any], idempotency_key: Optional[str] = None) -> bool:
    handler = EVENT_HANDLERS.get(topic)
    if not handler:
        return False
    try:
        close_old_connections()
        handler(payload, idempotency_key=idempotency_key)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("Failed handling %s payload=%s", topic, payload)
    return True



def dispatch_event(topic, payload, idempotency_key=None):
    return handle_assessment_event(topic, payload, idempotency_key)



def consume_events(run_duration=None, poll_interval=1.0):
    consumer = build_consumer()
    running = True
    deadline = time.monotonic() + run_duration if run_duration else None

    def shutdown(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    consumer.subscribe(TOPICS)
    print(f"Consuming from topics: {TOPICS} on {BOOTSTRAP}")

    try:
        while running:
            if deadline and time.monotonic() >= deadline:
                break
            msg = consumer.poll(poll_interval)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"Kafka error: {msg.error()}")
                continue
            try:
                payload = json.loads(msg.value().decode("utf-8"))
            except (json.JSONDecodeError, AttributeError):
                payload = {}
            log_message(msg, payload or msg.value())
            if payload:
                try:
                    idempotency_key = f"{msg.topic()}:{msg.partition()}:{msg.offset()}"
                    dispatch_event(msg.topic(), payload, idempotency_key=idempotency_key)
                    consumer.commit(message=msg, asynchronous=False)
                except Exception as exc:
                    print(f"Failed to handle event {payload}: {exc}")
    finally:
        consumer.close()


if __name__ == "__main__":
    consume_events()
