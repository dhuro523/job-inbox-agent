import logging

from sqlalchemy.orm import Session

from app.detection.pipeline import classify_email
from app.extraction.extractor import extract_application_data
from app.gmail.client import EmailMessage
from app.database.email_repository import save_email
from app.matching.application_service import create_or_get_application

logger = logging.getLogger(__name__)


def process_email(
    db: Session,
    message: EmailMessage,
) -> dict:
    """
    Process one Gmail message through the complete job-email pipeline.

    Flow:
    1. Detect whether the email is job-related.
    2. If not job-related, stop.
    3. Save the email to PostgreSQL.
    4. Extract structured application data.
    5. Create/reuse the application and record the event.
    """

    detection = classify_email(
        sender=message.sender,
        subject=message.subject,
        body_text=message.body_text,
    )

    logger.info(
        "Detection result: subject=%r job_related=%s confidence=%.2f decided_by=%s",
        message.subject,
        detection.is_job_related,
        detection.confidence,
        detection.decided_by,
    )

    if not detection.is_job_related:
        return {
            "gmail_message_id": message.gmail_message_id,
            "is_job_related": False,
            "detection_confidence": detection.confidence,
            "decided_by": detection.decided_by,
            "application_id": None,
            "event_type": None,
        }

    email = save_email(
        db=db,
        gmail_message_id=message.gmail_message_id,
        thread_id=message.thread_id,
        sender=message.sender,
        subject=message.subject,
        received_at=message.received_at,
        snippet=message.snippet,
        body_text=message.body_text,
    )

    extracted = extract_application_data(
        sender=message.sender,
        subject=message.subject,
        body_text=message.body_text,
        received_at=message.received_at,
    )

    application = create_or_get_application(
        db=db,
        extracted=extracted,
        email_id=email.id,
    )

    return {
        "gmail_message_id": message.gmail_message_id,
        "is_job_related": True,
        "detection_confidence": detection.confidence,
        "decided_by": detection.decided_by,
        "application_id": application.id if application else None,
        "event_type": extracted.event_type,
    }