EVENT_STATUS_MAP = {
    "APPLICATION_SUBMITTED": "APPLIED",
    "APPLICATION_RECEIVED": "APPLIED",
    "ASSESSMENT_REQUESTED": "ASSESSMENT",
    "INTERVIEW_INVITED": "INTERVIEW",
    "INTERVIEW_COMPLETED": "INTERVIEW",
    "REJECTION": "REJECTED",
    "OFFER": "OFFER",
    "WITHDRAWN": "WITHDRAWN",
    "FOLLOW_UP": "FOLLOW_UP",
    "OTHER": "UNKNOWN",
}


STATUS_PRIORITY = {
    "UNKNOWN": 0,
    "APPLIED": 1,
    "ASSESSMENT": 2,
    "INTERVIEW": 3,
    "FOLLOW_UP": 4,
    "REJECTED": 5,
    "OFFER": 6,
    "WITHDRAWN": 6,
}


def status_from_event(event_type: str | None) -> str:
    if not event_type:
        return "UNKNOWN"

    return EVENT_STATUS_MAP.get(event_type, "UNKNOWN")


def should_update_status(
    current_status: str | None,
    new_status: str,
) -> bool:
    current_priority = STATUS_PRIORITY.get(
        current_status or "UNKNOWN",
        0,
    )
    new_priority = STATUS_PRIORITY.get(
        new_status,
        0,
    )

    return new_priority >= current_priority