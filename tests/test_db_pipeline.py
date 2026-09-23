from app.ingestion.db_pipeline import run_db_processing


class FakeMessage:
    def __init__(
        self,
        gmail_message_id,
        sender="jobs@example.com",
        subject="Application received",
        body_text="Thank you for applying.",
    ):
        self.gmail_message_id = gmail_message_id
        self.thread_id = f"thread-{gmail_message_id}"
        self.sender = sender
        self.subject = subject
        self.received_at = "Mon, 21 Sep 2026 12:00:00 +0000"
        self.snippet = body_text[:50]
        self.body_text = body_text


class FakeGmailClient:
    def __init__(self, messages):
        self.messages = {
            message.gmail_message_id: message
            for message in messages
        }

    def list_message_ids(self, query="", max_results=20):
        return list(self.messages.keys())[:max_results]

    def get_message(self, message_id):
        return self.messages[message_id]


class FakeEmail:
    def __init__(self, gmail_message_id):
        self.gmail_message_id = gmail_message_id


class FakeDB:
    def __init__(self, emails=None):
        self.emails = emails or []


def test_processes_new_emails(monkeypatch):
    messages = [
        FakeMessage("gmail-1"),
        FakeMessage(
            "gmail-2",
            sender="newsletter@example.com",
            subject="Weekly newsletter",
            body_text="Here is this week's newsletter.",
        ),
    ]

    client = FakeGmailClient(messages)
    db = FakeDB()

    def fake_get_email_by_gmail_id(db, message_id):
        return next(
            (
                email
                for email in db.emails
                if email.gmail_message_id == message_id
            ),
            None,
        )

    def fake_process_email(db, message):
        db.emails.append(FakeEmail(message.gmail_message_id))

        return {
            "gmail_message_id": message.gmail_message_id,
            "is_job_related": message.gmail_message_id == "gmail-1",
        }

    monkeypatch.setattr(
        "app.ingestion.db_pipeline.get_email_by_gmail_id",
        fake_get_email_by_gmail_id,
    )

    monkeypatch.setattr(
        "app.ingestion.db_pipeline.process_email",
        fake_process_email,
    )

    result = run_db_processing(
        client,
        db,
        max_results=20,
    )

    assert result["total_found"] == 2
    assert result["processed"] == 2
    assert result["skipped"] == 0
    assert result["job_related"] == 1
    assert len(db.emails) == 2


def test_skips_existing_emails(monkeypatch):
    existing = FakeEmail("gmail-1")

    messages = [
        FakeMessage("gmail-1"),
        FakeMessage("gmail-2"),
    ]

    client = FakeGmailClient(messages)
    db = FakeDB([existing])

    processed_ids = []

    def fake_get_email_by_gmail_id(db, message_id):
        return next(
            (
                email
                for email in db.emails
                if email.gmail_message_id == message_id
            ),
            None,
        )

    def fake_process_email(db, message):
        processed_ids.append(message.gmail_message_id)
        db.emails.append(FakeEmail(message.gmail_message_id))

        return {
            "gmail_message_id": message.gmail_message_id,
            "is_job_related": True,
        }

    monkeypatch.setattr(
        "app.ingestion.db_pipeline.get_email_by_gmail_id",
        fake_get_email_by_gmail_id,
    )

    monkeypatch.setattr(
        "app.ingestion.db_pipeline.process_email",
        fake_process_email,
    )

    result = run_db_processing(
        client,
        db,
    )

    assert result["total_found"] == 2
    assert result["processed"] == 1
    assert result["skipped"] == 1
    assert result["job_related"] == 1
    assert processed_ids == ["gmail-2"]