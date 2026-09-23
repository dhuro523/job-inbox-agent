from datetime import datetime

from app.database.email_repository import (
    get_email_by_gmail_id,
    parse_received_at,
    save_email,
)


class FakeQuery:
    def __init__(self, emails):
        self._emails = emails

    def filter(self, *args):
        return self

    def first(self):
        return self._emails[0] if self._emails else None


class FakeSession:
    def __init__(self):
        self.emails = []

    def query(self, model):
        return FakeQuery(self.emails)

    def add(self, obj):
        self.emails.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        if obj.id is None:
            obj.id = len(self.emails)


def test_parse_received_at():
    result = parse_received_at(
        "Mon, 21 Sep 2026 14:32:10 +0200"
    )

    assert isinstance(result, datetime)
    assert result.year == 2026
    assert result.month == 9
    assert result.day == 21
    assert result.hour == 14
    assert result.minute == 32


def test_parse_received_at_returns_none_for_missing_value():
    assert parse_received_at(None) is None
    assert parse_received_at("") is None


def test_parse_received_at_returns_none_for_invalid_value():
    assert parse_received_at("not-a-date") is None


def test_saves_new_email():
    db = FakeSession()

    result = save_email(
        db,
        gmail_message_id="gmail-123",
        thread_id="thread-123",
        sender="jobs@example.com",
        subject="Application Received",
        received_at="Mon, 21 Sep 2026 14:32:10 +0200",
        snippet="Thank you for applying.",
        body_text="Your application has been received.",
    )

    assert result is not None
    assert result.gmail_message_id == "gmail-123"
    assert result.thread_id == "thread-123"
    assert result.sender == "jobs@example.com"
    assert result.subject == "Application Received"
    assert result.body_text == "Your application has been received."
    assert result.received_at is not None
    assert len(db.emails) == 1


def test_does_not_duplicate_existing_email():
    db = FakeSession()

    first = save_email(
        db,
        gmail_message_id="gmail-123",
        thread_id="thread-123",
        sender="jobs@example.com",
        subject="Application Received",
        received_at="Mon, 21 Sep 2026 14:32:10 +0200",
        snippet="Thank you for applying.",
        body_text="Your application has been received.",
    )

    second = save_email(
        db,
        gmail_message_id="gmail-123",
        thread_id="thread-123",
        sender="jobs@example.com",
        subject="Application Received",
        received_at="Mon, 21 Sep 2026 14:32:10 +0200",
        snippet="Thank you for applying.",
        body_text="Your application has been received.",
    )

    assert first is second
    assert len(db.emails) == 1


def test_get_email_by_gmail_id():
    db = FakeSession()

    saved = save_email(
        db,
        gmail_message_id="gmail-456",
        thread_id="thread-456",
        sender="jobs@example.com",
        subject="Interview",
        received_at=None,
        snippet="Interview invitation.",
        body_text="We would like to interview you.",
    )

    result = get_email_by_gmail_id(
        db,
        "gmail-456",
    )

    assert result is saved
    assert result.gmail_message_id == "gmail-456"