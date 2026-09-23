from sqlalchemy.orm import Session

from app.matching.matcher import applications_match
from app.matching.normalization import normalize_company, normalize_role
from app.models.application import Application


def find_existing_application(
    db: Session,
    company: str | None,
    role: str | None,
) -> Application | None:
    applications = (
        db.query(Application)
        .filter(Application.company.isnot(None))
        .filter(Application.role.isnot(None))
        .all()
    )

    # First: strict company + role matching.
    for application in applications:
        if applications_match(
            company,
            role,
            application.company,
            application.role,
        ):
            return application

    # Fallback: exact role match when the new email has no company.
    if company is None and role is not None:
        normalized_role = normalize_role(role)

        for application in applications:
            if normalize_role(application.role) == normalized_role:
                return application

    return None