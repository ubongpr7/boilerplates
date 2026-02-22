import json
import logging
from typing import Any, Iterable
import uuid

from confluent_kafka import Producer
from confluent_kafka.error import KafkaException
from django.conf import settings

logger = logging.getLogger(__name__)

_producer: Producer | None = None


def _get_producer() -> Producer:
    """
    Lazily initialise a single confluent-kafka Producer for the process.
    """
    global _producer
    if _producer is not None:
        return _producer

    config = {
        "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
        "socket.timeout.ms": 10000,
        "message.timeout.ms": 10000,
        "enable.idempotence": True,
        "retries": 5
    }

    _producer = Producer(config)
    return _producer


def _delivery_report(err, msg):
    if err is not None:
        logger.error(
            "Kafka delivery failed for topic=%s partition=%s: %s",
            msg.topic(),
            msg.partition(),
            err,
        )
    else:
        logger.debug(
            "Kafka message delivered topic=%s partition=%s offset=%s",
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )


def produce_json_message(
    topic: str,
    payload: dict[str, Any],
    *,
    key: str | None = None,
    headers: Iterable[tuple[str, str]] | None = None,
) -> None:
    """
    Produce a JSON message to Kafka using confluent-kafka.
    """
    producer = _get_producer()
    payload['event_id']=str(uuid.uuid4())
    data = json.dumps(payload).encode("utf-8")

    try:
        producer.produce(
            topic,
            value=data,
            key=key,
            headers=headers,
            on_delivery=_delivery_report,
        )
    except KafkaException:
        logger.exception("Failed to enqueue Kafka message for topic %s", topic)
        raise

    producer.poll(0)
