"""
A thin, read-only Gmail client.

Why thin: this module's only responsibility is talking to the Gmail API
and returning normalized Python data. It does NOT decide what's job-related,
does NOT store anything in a database, and does NOT call any LLM. Those are
separate concerns (Phases 3, 5, 6).
"""

import base64
from dataclasses import dataclass

from googleapiclient.discovery import build

from app.gmail.auth import get_gmail_credentials


@dataclass
class EmailMessage:
    gmail_message_id: str
    thread_id: str
    sender: str
    subject: str
    received_at: str  # raw header value for now; we'll parse to datetime in Phase 3
    snippet: str
    body_text: str


class GmailClient:
    def __init__(self) -> None:
        creds = get_gmail_credentials()
        self._service = build("gmail", "v1", credentials=creds)

    def list_message_ids(self, query: str = "", max_results: int = 10) -> list[str]:
        """Return raw Gmail message IDs matching an optional search query."""
        response = (
            self._service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )
        return [m["id"] for m in response.get("messages", [])]

    def get_message(self, message_id: str) -> EmailMessage:
        """Fetch and normalize a single message by ID."""
        raw = (
            self._service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )

        headers = {
            h["name"]: h["value"]
            for h in raw["payload"].get("headers", [])
        }

        return EmailMessage(
            gmail_message_id=raw["id"],
            thread_id=raw["threadId"],
            sender=headers.get("From", ""),
            subject=headers.get("Subject", ""),
            received_at=headers.get("Date", ""),
            snippet=raw.get("snippet", ""),
            body_text=self._extract_body_text(raw["payload"]),
        )

    def _extract_body_text(self, payload: dict) -> str:
        """
        Gmail payloads can be a single part or deeply nested multipart
        (plain text + HTML + attachments). For now we only extract
        text/plain. We'll handle HTML-only emails properly in Phase 3.
        """
        if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
            return self._decode(payload["body"]["data"])

        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                return self._decode(part["body"]["data"])
            # recurse into nested multipart
            if part.get("parts"):
                text = self._extract_body_text(part)
                if text:
                    return text

        return ""

    @staticmethod
    def _decode(data: str) -> str:
        decoded_bytes = base64.urlsafe_b64decode(data.encode("ASCII"))
        return decoded_bytes.decode("utf-8", errors="replace")