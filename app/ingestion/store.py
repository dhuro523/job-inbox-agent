"""
Temporary storage layer for ingested emails.

Why this exists as its own module: the ingestion pipeline shouldn't care
HOW emails are persisted, only THAT they are, and whether a given
gmail_message_id has already been seen. This is a stand-in for the real
PostgreSQL-backed store we'll build in Phase 4 — same interface, different
backend. Nothing in ingestion.py will need to change when we swap it.
"""

import json
import os
from dataclasses import asdict

from app.gmail.client import EmailMessage


class JsonEmailStore:
    def __init__(self, path: str = "data/emails.json") -> None:
        self._path = path
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        if not os.path.exists(self._path):
            with open(self._path, "w") as f:
                json.dump([], f)

    def _read_all(self) -> list[dict]:
        with open(self._path, "r") as f:
            return json.load(f)

    def _write_all(self, records: list[dict]) -> None:
        with open(self._path, "w") as f:
            json.dump(records, f, indent=2)

    def exists(self, gmail_message_id: str) -> bool:
        """The idempotency check: have we already stored this message?"""
        return any(
            r["gmail_message_id"] == gmail_message_id for r in self._read_all()
        )

    def save(self, message: EmailMessage) -> None:
        if self.exists(message.gmail_message_id):
            return  # already stored — do nothing, this is what makes re-runs safe
        records = self._read_all()
        records.append(asdict(message))
        self._write_all(records)

    def count(self) -> int:
        return len(self._read_all())