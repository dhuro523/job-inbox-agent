from app.extraction.schema import ExtractedApplicationData
from app.matching.application_service import create_or_get_application


class FakeQuery:
    def __init__(self, applications):
        self._applications = applications

    def filter(self, *args):
        return self

    def all(self):
        return self._applications


class FakeSession:
    def __init__(self):
        self.applications = []
        self.events = []

    def query(self, model):
        from app.models.application import Application

        if model is Application:
            return FakeQuery(self.applications)

        return FakeQuery([])

    def add(self, obj):
        from app.models.application import Application
        from app.models.application_event import ApplicationEvent

        if isinstance(obj, Application):
            self.applications.append(obj)
        elif isinstance(obj, ApplicationEvent):
            self.events.append(obj)

    def flush(self):
        if self.applications:
            self.applications[-1].id = 1

    def commit(self):
        pass


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


def test_creates_new_application_and_event():
    db = FakeSession()

    result = create_or_get_application(
        db,
        make_extracted(),
        email_id=123,
    )

    assert result is not None
    assert result.company == "Mercor"
    assert result.role == "Software Engineer, Python"
    assert len(db.applications) == 1
    assert len(db.events) == 1
    assert db.events[0].application_id == 1
    assert db.events[0].email_id == 123
    assert db.events[0].event_type == "APPLICATION_SUBMITTED"


def test_reuses_existing_application():
    db = FakeSession()

    first = create_or_get_application(
        db,
        make_extracted(),
        email_id=123,
    )

    second = create_or_get_application(
        db,
        make_extracted(
            event_type="ASSESSMENT_REQUESTED",
        ),
        email_id=456,
    )

    assert first is second
    assert len(db.applications) == 1
    assert len(db.events) == 2
    assert db.events[0].event_type == "APPLICATION_SUBMITTED"
    assert db.events[1].event_type == "ASSESSMENT_REQUESTED"


def test_returns_none_when_company_or_role_missing():
    db = FakeSession()

    result = create_or_get_application(
        db,
        make_extracted(company=None),
    )

    assert result is None
    assert len(db.applications) == 0
    assert len(db.events) == 0