from dotenv import load_dotenv

load_dotenv()

from app.database.session import SessionLocal
from app.models.email import Email
from app.detection.pipeline import classify_email
from app.extraction.extractor import extract_application_data
from app.matching.application_matcher import find_existing_application


def main() -> None:
    db = SessionLocal()

    try:
        emails = db.query(Email).order_by(Email.id).all()

        for email in emails:
            print("\n" + "=" * 80)
            print(f"ID: {email.id}")
            print(f"Subject: {email.subject}")
            print(f"Sender: {email.sender}")

            detection = classify_email(
                sender=email.sender,
                subject=email.subject or "",
                body_text=email.body_text or "",
            )

            print("\nDetection:")
            print(f"  Job-related: {detection.is_job_related}")
            print(f"  Confidence: {detection.confidence}")
            print(f"  Decided by: {detection.decided_by}")
            print(f"  Reason: {detection.reason}")

            if detection.is_job_related:
                extracted = extract_application_data(
                    sender=email.sender,
                    subject=email.subject or "",
                    body_text=email.body_text or "",
                    received_at=(
                        email.received_at.isoformat()
                        if email.received_at
                        else None
                    ),
                )

                print("\nExtraction:")
                print(f"  Company: {extracted.company}")
                print(f"  Role: {extracted.role}")
                print(f"  Location: {extracted.location}")
                print(f"  Event type: {extracted.event_type}")
                print(f"  Application status: {extracted.application_status}")
                print(f"  Source: {extracted.source}")
                print(f"  Confidence: {extracted.confidence}")

                application = find_existing_application(
                    db,
                    extracted.company,
                    extracted.role,
                )

                print("\nMatching:")
                if application:
                    print(f"  Matched application ID: {application.id}")
                    print(f"  Company: {application.company}")
                    print(f"  Role: {application.role}")
                    print(f"  Current status: {application.current_status}")
                else:
                    print("  No existing application matched.")

    finally:
        db.close()


if __name__ == "__main__":
    main()