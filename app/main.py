from dotenv import load_dotenv

load_dotenv()

import logging

from app.database.session import SessionLocal
from app.gmail.client import GmailClient
from app.ingestion.db_pipeline import run_db_processing


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main() -> None:
    client = GmailClient()
    db = SessionLocal()

    try:
        result = run_db_processing(
            client=client,
            db=db,
            max_results=5,
        )

        print("\nProcessing complete")
        print(f"Emails found: {result['total_found']}")
        print(f"Emails processed: {result['processed']}")
        print(f"Emails skipped: {result['skipped']}")
        print(f"Job-related emails: {result['job_related']}")

    finally:
        db.close()


if __name__ == "__main__":
    main()