"""
Manual smoke test for the database models.
Run: uv run python -m scripts.test_db
"""

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timezone

from app.database.session import SessionLocal
from app.models.email import Email
from app.models.application import Application
from app.models.application_event import ApplicationEvent


def main() -> None:
    db = SessionLocal()
    try:
        # Insert a fake email
        email = Email(
            gmail_message_id="test-message-id-001",
            thread_id="test-thread-001",
            sender="team@mercor.com",
            subject="Application Submitted - Test Role",
            received_at=datetime.now(timezone.utc),
            snippet="We've received your application...",
            body_text="Full body text here.",
        )
        db.add(email)
        db.flush()  # get email.id without committing yet
        print(f"Inserted email id={email.id}")

        # Insert an application
        application = Application(
            company="Mercor",
            role="Test Role",
            current_status="APPLIED",
            confidence=0.95,
        )
        db.add(application)
        db.flush()
        print(f"Inserted application id={application.id}")

        # Insert an event linking them
        event = ApplicationEvent(
            application_id=application.id,
            email_id=email.id,
            event_type="APPLICATION_SUBMITTED",
            event_date=email.received_at,
            description="Application submitted via Mercor.",
            confidence=0.95,
        )
        db.add(event)
        db.commit()
        print(f"Inserted application_event id={event.id}")

        # Read it back
        result = db.query(Application).filter_by(company="Mercor").first()
        print(f"Read back: {result.company} - {result.role} - {result.current_status}")

       # Clean up test data so re-runs stay idempotent.
        # Order matters: children before parents, with a flush after each
        # delete so the DB sees it before the next delete is attempted.
        db.delete(event)
        db.flush()

        db.delete(application)
        db.flush()

        db.delete(email)
        db.commit()
        print("Cleaned up test data.")

    finally:
        db.close()


if __name__ == "__main__":
    main()