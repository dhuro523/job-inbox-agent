from datetime import datetime
from email.utils import parsedate_to_datetime

from sqlalchemy.orm import Session

from app.models.email import Email


def parse_received_at(value: str | None) -> datetime | None:
    if not value:
        return None

    try:
        return parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None


def get_email_by_gmail_id(
    db: Session,
    gmail_message_id: str,
) -> Email | None:
    return (
        db.query(Email)
        .filter(Email.gmail_message_id == gmail_message_id)
        .first()
    )


def save_email(
    db: Session,
    gmail_message_id: str,
    thread_id: str,
    sender: str,
    subject: str | None,
    received_at: str | None,
    snippet: str | None,
    body_text: str | None,
) -> Email:
    existing = get_email_by_gmail_id(
        db,
        gmail_message_id,
    )

    if existing is not None:
        return existing

    email = Email(
        gmail_message_id=gmail_message_id,
        thread_id=thread_id,
        sender=sender,
        subject=subject,
        received_at=parse_received_at(received_at),
        snippet=snippet,
        body_text=body_text,
    )

    db.add(email)
    db.commit()
    db.refresh(email)

    return email