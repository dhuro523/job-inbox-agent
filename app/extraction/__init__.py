"""
Pydantic schema for structured LLM extraction of job-application data
from an email.

Every field except confidence is nullable by design. The LLM is
instructed to return null rather than guess — this schema is what
enforces that at the data layer: if the model tries to return something
that doesn't fit (wrong type, invalid event_type), Pydantic validation
will catch it before it ever reaches the database.
"""

from typing import Literal

from pydantic import BaseModel, Field

EventType = Literal[
    "APPLICATION_SUBMITTED",
    "APPLICATION_RECEIVED",
    "ASSESSMENT",
    "INTERVIEW",
    "FOLLOW_UP",
    "OFFER",
    "REJECTION",
    "WITHDRAWAL",
    "OTHER",
]


class ExtractedApplicationData(BaseModel):
    company: str | None = None
    role: str | None = None
    location: str | None = None
    employment_type: str | None = None
    event_type: EventType | None = None
    event_date: str | None = None  # ISO date string if present in email, else null
    deadline: str | None = None
    application_status: str | None = None
    source: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)