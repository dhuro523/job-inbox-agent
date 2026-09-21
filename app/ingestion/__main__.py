"""
Manual ingestion entry point.
Run: uv run python -m app.ingestion
"""

import logging

from dotenv import load_dotenv
load_dotenv()

from app.gmail.client import GmailClient
from app.ingestion.pipeline import run_ingestion
from app.ingestion.store import JsonEmailStore

logging.basicConfig(level=logging.INFO, format="%(levelname)-5s %(message)s")


def main() -> None:
    client = GmailClient()
    store = JsonEmailStore()
    run_ingestion(client, store, max_results=20)


if __name__ == "__main__":
    main()