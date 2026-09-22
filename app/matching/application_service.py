from datetime import datetime

from sqlalchemy.orm import Session

from app.extraction.schema import ExtractedApplicationData
from app.matching.application_matcher import find_existing_application
from app.matching.status import should_update_status, status_from_event
from app.models.application import Application
from app.models.application_event import ApplicationEvent


def create_or_get_application(
    db: Session,
    extracted: ExtractedApplicationData,
    email_id: int | None = None,
) -> Application | None:
    if not extracted.company or not extracted.role:
        return None

    application = find_existing_application(
        db,
        extracted.company,
        extracted.role,
    )

    event_type = extracted.event_type or "OTHER"
    new_status = status_from_event(event_type)

    if application is None:
        application = Application(
            company=extracted.company,
            role=extracted.role,
            location=extracted.location,
            source=extracted.source,
            application_date=extracted.event_date,
            current_status=new_status,
            confidence=extracted.confidence,
        )

        db.add(application)
        db.flush()

    elif should_update_status(application.current_status, new_status):
        application.current_status = new_status

    event = ApplicationEvent(
        application_id=application.id,
        email_id=email_id,
        event_type=event_type,
        event_date=(
            datetime.combine(
                extracted.event_date,
                datetime.min.time(),
            )
            if extracted.event_date
            else None
        ),
        confidence=extracted.confidence,
    )

    db.add(event)
    db.commit()

    return application