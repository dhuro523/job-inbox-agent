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


def status_from_event(event_type: str | None) -> str:
    if not event_type:
        return "UNKNOWN"

    return EVENT_STATUS_MAP.get(event_type, "UNKNOWN")