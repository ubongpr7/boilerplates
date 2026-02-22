
from mainapps.subscriptions.models import SubscriptionEvent
from subapps.kafka.client import produce_json_message

def subscription_event_producer(event: SubscriptionEvent):
    """
    Sends a subscription event to Kafka.
    """
    event_payload = {
        "event_name": f"subscription.{event.event_type}",
        "event_timestamp": event.created_at.isoformat(),
        "subscription_id": str(event.subscription.identifier),
        "user_id": str(event.subscription.user_id),
        "payload": event.payload
    }
    produce_json_message('subscription_events', event_payload, key=str(event.subscription.user_id))
