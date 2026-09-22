from app.matching.application_matcher import find_existing_application
from app.models.application import Application


class FakeQuery:
    def __init__(self, applications: list[Application]) -> None:
        self._applications = applications

    def filter(self, *args):
        return self

    def all(self):
        return self._applications


class FakeSession:
    def __init__(self, applications: list[Application]) -> None:
        self._applications = applications

    def query(self, model):
        return FakeQuery(self._applications)


def make_application(
    company: str,
    role: str,
    application_id: int = 1,
) -> Application:
    application = Application(
        company=company,
        role=role,
        current_status="APPLIED",
    )
    application.id = application_id
    return application


def test_finds_existing_application():
    application = make_application(
        "Mercor",
        "Software Engineer, Python",
    )
    db = FakeSession([application])

    result = find_existing_application(
        db,
        "mercor",
        "Software Engineer, Python",
    )

    assert result is application
    assert result.id == 1


def test_does_not_match_different_role():
    application = make_application(
        "Mercor",
        "Software Engineer, Python",
    )
    db = FakeSession([application])

    result = find_existing_application(
        db,
        "Mercor",
        "Software Engineer, Go",
    )

    assert result is None


def test_does_not_match_different_company():
    application = make_application(
        "Mercor",
        "Software Engineer, Python",
    )
    db = FakeSession([application])

    result = find_existing_application(
        db,
        "Google",
        "Software Engineer, Python",
    )

    assert result is None


def test_returns_none_when_company_or_role_is_missing():
    application = make_application(
        "Mercor",
        "Software Engineer, Python",
    )
    db = FakeSession([application])

    assert find_existing_application(
        db, None, "Software Engineer, Python"
    ) is None

    assert find_existing_application(
        db, "Mercor", None
    ) is None
