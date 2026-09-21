"""
Unit tests for the ingestion pipeline, using fakes instead of real Gmail.
Why fakes and not real API calls: unit tests should be fast, deterministic,
and not depend on network/credentials. We test the LOGIC (idempotency,
counting) here; real Gmail integration is verified manually via
scripts/test_gmail.py and app/ingestion/__main__.py.
"""

from app.gmail.client import EmailMessage
from app.ingestion.pipeline import run_ingestion


class FakeGmailClient:
    """Stands in for GmailClient — returns canned data, no real API calls."""

    def __init__(self, messages: list[EmailMessage]) -> None:
        self._messages = {m.gmail_message_id: m for m in messages}

    def list_message_ids(self, query: str = "", max_results: int = 20) -> list[str]:
        return list(self._messages.keys())[:max_results]

    def get_message(self, message_id: str) -> EmailMessage:
        return self._messages[message_id]


class FakeStore:
    """Stands in for JsonEmailStore — in-memory, no disk I/O."""

    def __init__(self) -> None:
        self._records: dict[str, EmailMessage] = {}

    def exists(self, gmail_message_id: str) -> bool:
        return gmail_message_id in self._records

    def save(self, message: EmailMessage) -> None:
        self._records[message.gmail_message_id] = message

    def count(self) -> int:
        return len(self._records)


def make_message(msg_id: str) -> EmailMessage:
    return EmailMessage(
        gmail_message_id=msg_id,
        thread_id=f"thread-{msg_id}",
        sender="test@example.com",
        subject="Test subject",
        received_at="Mon, 1 Jan 2026 00:00:00 GMT",
        snippet="a snippet",
        body_text="body",
    )


def test_ingestion_stores_new_messages():
    messages = [make_message("1"), make_message("2")]
    client = FakeGmailClient(messages)
    store = FakeStore()

    summary = run_ingestion(client, store)

    assert summary["fetched"] == 2
    assert summary["new"] == 2
    assert summary["skipped_duplicates"] == 0
    assert store.count() == 2


def test_ingestion_is_idempotent_on_second_run():
    messages = [make_message("1"), make_message("2")]
    client = FakeGmailClient(messages)
    store = FakeStore()

    run_ingestion(client, store)  # first run
    summary = run_ingestion(client, store)  # second run, same data

    assert summary["new"] == 0
    assert summary["skipped_duplicates"] == 2
    assert store.count() == 2  # still 2, not 4