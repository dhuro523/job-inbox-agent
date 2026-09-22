from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ExtractedApplicationData(BaseModel):
    company: str | None = None
    role: str | None = None
    location: str | None = None
    employment_type: str | None = None

    event_type: Literal[
        "APPLICATION_SUBMITTED",
        "APPLICATION_RECEIVED",
        "ASSESSMENT_REQUESTED",
        "INTERVIEW_INVITED",
        "INTERVIEW_COMPLETED",
        "REJECTION",
        "OFFER",
        "WITHDRAWN",
        "FOLLOW_UP",
        "OTHER",
    ] | None = None

    event_date: date | None = None
    deadline: date | None = None

    application_status: str | None = None
    source: str | None = None

    confidence: float = Field(ge=0.0, le=1.0)