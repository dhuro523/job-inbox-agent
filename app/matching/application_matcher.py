from sqlalchemy.orm import Session

from app.matching.matcher import applications_match
from app.models.application import Application


def find_existing_application(
    db: Session,
    company: str | None,
    role: str | None,
) -> Application | None:
    if not company or not role:
        return None

    candidates = (
        db.query(Application)
        .filter(Application.company.isnot(None))
        .filter(Application.role.isnot(None))
        .all()
    )

    for application in candidates:
        if applications_match(
            company,
            role,
            application.company,
            application.role,
        ):
            return application

    return None