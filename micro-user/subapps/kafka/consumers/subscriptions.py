from typing import Any, Dict, Optional

from mainapps.subscriptions.services.usage import apply_exam_session


def handle_conversation_started_event(payload: Dict[str, Any], idempotency_key: Optional[str] = None):
    """
    Consume conversation.started events from the AI service and increment exam usage.

    Expected payload keys:
      - user_id: identifier of the user starting the conversation
      - event_id/session_id: optional unique identifier used for idempotency
    """
    user_id = payload.get("user_id") or payload.get("userId")
    if not user_id:
        return
    key = idempotency_key or payload.get("session_id") or payload.get("event_id")
    apply_exam_session(user_id=user_id, idempotency_key=key, payload=payload)
