"""
Email ingestion pipeline.

Responsibility: pull messages from Gmail via GmailClient, and persist any
we haven't seen before via the store. This module does NOT decide what's
job-related (Phase 5) and does NOT call any LLM — it only ingests raw,
normalized emails.
"""

import logging

from app.gmail.client import GmailClient
from app.ingestion.store import JsonEmailStore

logger = logging.getLogger(__name__)


def run_ingestion(
    client: GmailClient,
    store: JsonEmailStore,
    query: str = "",
    max_results: int = 20,
) -> dict:
    """
    Fetch up to `max_results` messages matching `query`, store any new ones.
    Returns a summary dict — useful for logging and, later, observability.
    """
    logger.info("Gmail ingestion started")

    message_ids = client.list_message_ids(query=query, max_results=max_results)
    logger.info(f"Found {len(message_ids)} messages from Gmail")

    new_count = 0
    skipped_count = 0

    for message_id in message_ids:
        if store.exists(message_id):
            skipped_count += 1
            continue

        message = client.get_message(message_id)
        store.save(message)
        new_count += 1

    summary = {
        "fetched": len(message_ids),
        "new": new_count,
        "skipped_duplicates": skipped_count,
        "total_in_store": store.count(),
    }
    logger.info(f"Ingestion complete: {summary}")
    return summary