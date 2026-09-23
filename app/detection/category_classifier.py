from app.detection.category import EmailCategory
from app.extraction.schema import ExtractedApplicationData


def classify_category(
    is_job_related: bool,
    extracted: ExtractedApplicationData | None,
) -> EmailCategory:
    if not is_job_related:
        return "OTHER"

    if extracted is None:
        return "OTHER"

    if extracted.event_type == "JOB_ALERT":
        return "JOB_ALERT"

    if extracted.event_type in {
        "APPLICATION_SUBMITTED",
        "APPLICATION_RECEIVED",
    }:
        return "APPLICATION"

    if extracted.event_type in {
        "ASSESSMENT_REQUESTED",
        "INTERVIEW_INVITED",
        "INTERVIEW_COMPLETED",
        "REJECTION",
        "OFFER",
        "WITHDRAWN",
        "FOLLOW_UP",
    }:
        return "APPLICATION_UPDATE"

    return "OTHER"