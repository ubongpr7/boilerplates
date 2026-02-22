from django.contrib.auth import get_user_model


def _coerce_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes"}
    if isinstance(value, int):
        return value == 1
    return False


def handle_institution_user_event(payload: dict, **_):
    user_id = payload.get("user_id")
    if not user_id:
        return False

    user = get_user_model().objects.filter(id=user_id).first()
    if not user:
        return False

    event_name = payload.get("event_name")
    role = payload.get("role")

    if event_name == "user.onboarded":
        user.has_onboarded = True
        user.save(update_fields=["has_onboarded"])
        return True

    if "has_onboarded" in payload:
        user.has_onboarded = _coerce_bool(payload.get("has_onboarded"))
        user.save(update_fields=["has_onboarded"])
        return True

    return False

def handle_examiner_onboarded_event(payload: dict, **_):
    user_id = payload.get("user_id")
    if not user_id:
        return False

    if payload.get("event_name") != "user.onboarded":
        return False
    if payload.get("role") != "examiner":
        return False

    user = get_user_model().objects.filter(id=user_id).first()
    if not user:
        return False

    update_fields = []
    user.has_onboarded = True
    update_fields.append("has_onboarded")

    examiner_profile_id = payload.get("examiner_profile_id")
    if examiner_profile_id and hasattr(user, "examiner_profile_id"):
        setattr(user, "examiner_profile_id", examiner_profile_id)
        update_fields.append("examiner_profile_id")

    user.save(update_fields=update_fields)
    return True
