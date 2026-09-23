from sqlalchemy.orm import Session

from app.database.email_repository import get_email_by_gmail_id
from app.gmail.client import GmailClient
from app.processing import process_email


def run_db_processing(
    client: GmailClient,
    db: Session,
    query: str = "",
    max_results: int = 20,
) -> dict:
    message_ids = client.list_message_ids(
        query=query,
        max_results=max_results,
    )

    processed_count = 0
    skipped_count = 0
    job_related_count = 0

    for message_id in message_ids:
        existing = get_email_by_gmail_id(db, message_id)

        if existing is not None:
            skipped_count += 1
            continue

        message = client.get_message(message_id)
        result = process_email(db, message)

        processed_count += 1

        if result["is_job_related"]:
            job_related_count += 1

    return {
        "total_found": len(message_ids),
        "processed": processed_count,
        "skipped": skipped_count,
        "job_related": job_related_count,
    }