
from mainapps.accounts.models import User
from subapps.kafka import produce_json_message
import uuid


def _build_examiner_payload(user: User, profile=None):
    profile_pic_url = ""
    if profile and getattr(profile, "profile_picture", None):
        try:
            profile_pic_url = profile.profile_picture.url
        except Exception:
            profile_pic_url = ""

    full_name = getattr(user, "get_full_name", None)
    if callable(full_name):
        full_name = full_name()

    return {
        "user_id": str(user.id),
        "email": user.email,
        "full_name": full_name or f"{user.first_name} {user.last_name}".strip() or user.email,
        "profile_pic_url": profile_pic_url,
        "role": user.role,
        "is_active": user.is_active,
    }


def _build_candidate_payload(user: User, profile=None):
    profile_pic_url = ""
    if profile and getattr(profile, "profile_picture", None):
        try:
            profile_pic_url = profile.profile_picture.url
        except Exception:
            profile_pic_url = ""

    full_name = getattr(user, "get_full_name", None)
    if callable(full_name):
        full_name = full_name()

    return {
        "user_id": str(user.id),
        "email": user.email,
        "full_name": full_name or f"{user.first_name} {user.last_name}".strip() or user.email,
        "profile_pic_url": profile_pic_url,
        "role": user.role,
        "is_active": user.is_active,
    }

def user_created_producer(user: User):
    """
    Sends a 'user.created' event to Kafka.
    """
    event_payload = {
        "event_id": str(uuid.uuid4()),
        "event_name": "user.created",
        "event_timestamp": user.date_joined.isoformat(),
        "user_id": str(user.id),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "date_joined": user.date_joined.isoformat(),
        "role": user.role,
    }
    produce_json_message('user_events', event_payload, key=str(user.id))

    if user.role == "examiner":
        examiner_payload = {
            **event_payload,
            "event_name": "examiner.created",
            "examiner": _build_examiner_payload(user),
        }
        produce_json_message('user_events', examiner_payload, key=str(user.id))
    if user.role == "candidate":
        candidate_payload = {
            **event_payload,
            "event_name": "candidate.created",
            "candidate": _build_candidate_payload(user),
        }
        produce_json_message('user_events', candidate_payload, key=str(user.id))

def user_updated_producer(user: User, updated_fields: list):
    """
    Sends a 'user.updated' event to Kafka.
    """
    user_data = {field: getattr(user, field) for field in updated_fields}
    event_payload = {
        "event_id": str(uuid.uuid4()),
        "event_name": "user.updated",
        "event_timestamp": user.last_login.isoformat() if user.last_login else user.date_joined.isoformat(),
        "user_id": str(user.id),
        "updated_fields": updated_fields,
        "user_data": user_data,
        "role": user.role,
    }
    produce_json_message('user_events', event_payload, key=str(user.id))

    if user.role == "examiner":
        examiner_payload = {
            **event_payload,
            "event_name": "examiner.updated",
            "examiner": _build_examiner_payload(user),
        }
        produce_json_message('user_events', examiner_payload, key=str(user.id))
    if user.role == "candidate":
        candidate_payload = {
            **event_payload,
            "event_name": "candidate.updated",
            "candidate": _build_candidate_payload(user),
        }
        produce_json_message('user_events', candidate_payload, key=str(user.id))

def user_deleted_producer(user: User):
    """
    Sends a 'user.deleted' event to Kafka.
    """
    event_payload = {
        "event_id": str(uuid.uuid4()),
        "event_name": "user.deleted",
        "event_timestamp": user.date_joined.isoformat(), # There is no deleted_at field
        "user_id": str(user.id)
    }
    produce_json_message('user_events', event_payload, key=str(user.id))


def examiner_profile_updated_producer(user: User, profile):
    """
    Sends a 'examiner.profile.updated' event to Kafka when examiner profile changes.
    """
    if user.role != "examiner":
        return
    event_payload = {
        "event_id": str(uuid.uuid4()),
        "event_name": "examiner.profile.updated",
        "event_timestamp": profile.updated_at.isoformat(),
        "user_id": str(user.id),
        "examiner": _build_examiner_payload(user, profile=profile),
    }
    produce_json_message('user_events', event_payload, key=str(user.id))


def candidate_profile_updated_producer(user: User, profile):
    """
    Sends a 'candidate.profile.updated' event to Kafka when candidate profile changes.
    """
    if user.role != "candidate":
        return
    event_payload = {
        "event_id": str(uuid.uuid4()),
        "event_name": "candidate.profile.updated",
        "event_timestamp": profile.updated_at.isoformat(),
        "user_id": str(user.id),
        "candidate": _build_candidate_payload(user, profile=profile),
    }
    produce_json_message('user_events', event_payload, key=str(user.id))
