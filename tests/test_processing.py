from app.extraction.schema import ExtractedApplicationData
from app.gmail.client import EmailMessage
from app.processing import process_email


class FakeQuery:
    def __init__(self, items):
        self._items = items

    def filter(self, *conditions):
        filtered = self._items

        for condition in conditions:
            right = getattr(condition, "right", None)

            if right is not None and hasattr(right, "value"):
                value = right.value

                if value is not None:
                    filtered = [
                        item
                        for item in filtered
                        if getattr(item, "gmail_message_id", None) == value
                    ]

        return FakeQuery(filtered)

    def first(self):
        return self._items[0] if self._items else None

    def all(self):
        return self._items


class FakeSession:
    def __init__(self):
        self.emails = []
        self.applications = []
        self.events = []

    def query(self, model):
        from app.models.application import Application
        from app.models.email import Email

        if model is Email:
            return FakeQuery(self.emails)

        if model is Application:
            return FakeQuery(self.applications)

        return FakeQuery([])

    def add(self, obj):
        from app.models.application import Application
        from app.models.application_event import ApplicationEvent
        from app.models.email import Email

        if isinstance(obj, Email):
            self.emails.append(obj)

        elif isinstance(obj, Application):
            self.applications.append(obj)

        elif isinstance(obj, ApplicationEvent):
            self.events.append(obj)

    def flush(self):
        if self.applications:
            self.applications[-1].id = 1

    def commit(self):
        pass

    def refresh(self, obj):
        if getattr(obj, "id", None) is None:
            if hasattr(obj, "gmail_message_id"):
                obj.id = len(self.emails)


def make_message():
    return EmailMessage(
        gmail_message_id="gmail-123",
        thread_id="thread-123",
        sender="jobs@mercor.com",
        subject="Application Submitted - Software Engineer, Python",
        received_at="Mon, 21 Sep 2026 14:32:10 +0200",
        snippet="Your application was submitted.",
        body_text=(
            "Your application for Software Engineer, Python was submitted."
        ),
    )


def make_extracted(**overrides):
    data = {
        "company": "Mercor",
        "role": "Software Engineer, Python",
        "location": None,
        "employment_type": None,
        "event_type": "APPLICATION_SUBMITTED",
        "event_date": None,
        "deadline": None,
        "application_status": None,
        "source": None,
        "confidence": 0.95,
    }

    data.update(overrides)

    return ExtractedApplicationData(**data)


def test_processes_job_email(monkeypatch):
    db = FakeSession()

    monkeypatch.setattr(
        "app.processing.classify_email",
        lambda sender, subject, body_text: type(
            "DetectionResult",
            (),
            {
                "is_job_related": True,
                "confidence": 0.95,
                "reason": "application",
                "decided_by": "rules",
            },
        )(),
    )

    monkeypatch.setattr(
        "app.processing.extract_application_data",
        lambda sender, subject, body_text, received_at=None: make_extracted(),
    )

    result = process_email(
        db,
        make_message(),
    )

    assert result["is_job_related"] is True
    assert result["application_id"] == 1
    assert result["event_type"] == "APPLICATION_SUBMITTED"

    assert len(db.emails) == 1
    assert len(db.applications) == 1
    assert len(db.events) == 1

    assert db.emails[0].gmail_message_id == "gmail-123"
    assert db.applications[0].company == "Mercor"
    assert db.applications[0].role == "Software Engineer, Python"
    assert db.events[0].event_type == "APPLICATION_SUBMITTED"


def test_ignores_non_job_email(monkeypatch):
    db = FakeSession()

    monkeypatch.setattr(
        "app.processing.classify_email",
        lambda sender, subject, body_text: type(
            "DetectionResult",
            (),
            {
                "is_job_related": False,
                "confidence": 0.99,
                "reason": "promotional",
                "decided_by": "rules",
            },
        )(),
    )

    result = process_email(
        db,
        make_message(),
    )

    assert result["is_job_related"] is False
    assert result["application_id"] is None
    assert result["event_type"] is None

    assert len(db.emails) == 0
    assert len(db.applications) == 0
    assert len(db.events) == 0


def test_reuses_existing_application(monkeypatch):
    db = FakeSession()

    monkeypatch.setattr(
        "app.processing.classify_email",
        lambda sender, subject, body_text: type(
            "DetectionResult",
            (),
            {
                "is_job_related": True,
                "confidence": 0.95,
                "reason": "application",
                "decided_by": "rules",
            },
        )(),
    )

    extracted_submitted = make_extracted(
        event_type="APPLICATION_SUBMITTED",
    )

    monkeypatch.setattr(
        "app.processing.extract_application_data",
        lambda sender, subject, body_text, received_at=None: extracted_submitted,
    )

    first = process_email(
        db,
        make_message(),
    )

    second_message = EmailMessage(
        gmail_message_id="gmail-456",
        thread_id="thread-123",
        sender="jobs@mercor.com",
        subject="Assessment Requested",
        received_at="Tue, 22 Sep 2026 10:00:00 +0200",
        snippet="Please complete the assessment.",
        body_text=(
            "Please complete the assessment for "
            "Software Engineer, Python."
        ),
    )

    extracted_assessment = make_extracted(
        event_type="ASSESSMENT_REQUESTED",
    )

    monkeypatch.setattr(
        "app.processing.extract_application_data",
        lambda sender, subject, body_text, received_at=None: extracted_assessment,
    )

    second = process_email(
        db,
        second_message,
    )

    assert first["application_id"] == second["application_id"]
    assert len(db.applications) == 1
    assert len(db.emails) == 2
    assert len(db.events) == 2

    assert db.events[0].event_type == "APPLICATION_SUBMITTED"
    assert db.events[1].event_type == "ASSESSMENT_REQUESTED"