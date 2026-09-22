"""
LLM-based extraction of structured job-application data from emails.

The extractor follows a strict "never invent data" rule:
if a field is not explicitly supported by the email, the LLM must return null.
"""

import json
import logging

from openai import OpenAI

from app.config.settings import settings
from app.extraction.schema import ExtractedApplicationData

logger = logging.getLogger(__name__)

_client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You extract structured job-application information from emails.

IMPORTANT RULE:
NEVER invent, infer, guess, or assume information.

Only extract information that is explicitly stated in the email.
If a field is not explicitly stated or cannot be determined directly
from the email, return null.

For example:
- If the company name is explicitly mentioned, extract it.
- If the role is explicitly mentioned, extract it.
- Do NOT infer a role from a company name.
- Do NOT infer a location from a company's known location.
- Do NOT infer an employment type.
- Do NOT invent a deadline.
- Do NOT convert vague statements into specific dates.
- Do NOT assume an email is an application confirmation unless the
  email explicitly indicates that.

The event_type must be one of these values:

APPLICATION_SUBMITTED
APPLICATION_RECEIVED
ASSESSMENT_REQUESTED
INTERVIEW_INVITED
INTERVIEW_COMPLETED
REJECTION
OFFER
WITHDRAWN
FOLLOW_UP
OTHER

Use the date of the event only when it is explicitly stated or can be
directly determined from an explicit date in the email.

Use the received_at value only as contextual information. Do not use it
to invent an event_date unless the email clearly indicates that the event
occurred on that date.

For the source field:
- Extract the platform, job board, recruiting system, or application
  platform only when it is explicitly identified in the email.
- Examples include "Mercor", "Greenhouse", "LinkedIn", or "Indeed".
- Do not use generic values such as "email".
- If no specific platform or source is explicitly identified, return null.

Return ONLY a JSON object matching this structure:

{
  "company": string or null,
  "role": string or null,
  "location": string or null,
  "employment_type": string or null,
  "event_type": string or null,
  "event_date": "YYYY-MM-DD" or null,
  "deadline": "YYYY-MM-DD" or null,
  "application_status": string or null,
  "source": string or null,
  "confidence": number between 0.0 and 1.0
}

The confidence value should represent how confident you are that the
extracted information is directly supported by the email.
"""


def extract_application_data(
    sender: str,
    subject: str,
    body_text: str,
    received_at: str | None = None,
) -> ExtractedApplicationData:
    user_prompt = f"""Extract job-application data from this email.

Sender:
{sender}

Subject:
{subject}

Received at:
{received_at}

Email body:
{body_text}
"""

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content

    try:
        data = json.loads(raw)
        return ExtractedApplicationData(**data)
    except (json.JSONDecodeError, TypeError, ValueError):
        logger.exception("Failed to parse LLM extraction response: %s", raw)
        raise