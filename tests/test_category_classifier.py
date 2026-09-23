from datetime import date

from app.detection.category_classifier import classify_category
from app.extraction.schema import ExtractedApplicationData


def make_extracted(event_type: str | None) -> ExtractedApplicationData:
    return ExtractedApplicationData(
        company="Test Company",
        role="Test Role",
        event_type=event_type,
        event_date=date(2026, 9, 23),
        confidence=0.9,
    )


def test_non_job_email_is_other():
    result = classify_category(
        is_job_related=False,
        extracted=None,
    )

    assert result == "OTHER"


def test_job_alert():
    result = classify_category(
        is_job_related=True,
        extracted=make_extracted("JOB_ALERT"),
    )

    assert result == "JOB_ALERT"


def test_application_submitted():
    result = classify_category(
        is_job_related=True,
        extracted=make_extracted("APPLICATION_SUBMITTED"),
    )

    assert result == "APPLICATION"


def test_application_received():
    result = classify_category(
        is_job_related=True,
        extracted=make_extracted("APPLICATION_RECEIVED"),
    )

    assert result == "APPLICATION"


def test_follow_up_is_application_update():
    result = classify_category(
        is_job_related=True,
        extracted=make_extracted("FOLLOW_UP"),
    )

    assert result == "APPLICATION_UPDATE"


def test_interview_is_application_update():
    result = classify_category(
        is_job_related=True,
        extracted=make_extracted("INTERVIEW_INVITED"),
    )

    assert result == "APPLICATION_UPDATE"


def test_rejection_is_application_update():
    result = classify_category(
        is_job_related=True,
        extracted=make_extracted("REJECTION"),
    )

    assert result == "APPLICATION_UPDATE"


def test_missing_extraction_is_other():
    result = classify_category(
        is_job_related=True,
        extracted=None,
    )

    assert result == "OTHER"