"""
LLM-based fallback classifier for ambiguous job-email detection.

Only called when Stage 1 (rules.py) returns is_job_related=None. Uses
Groq (OpenAI-compatible API) with structured JSON output so the result
is always predictable and parseable — never free-form text we'd have
to guess at.
"""

import json

from openai import OpenAI
from pydantic import BaseModel

from app.config.settings import settings

_client = OpenAI(
    api_key=settings.groq_api_key,
    base_url="https://api.groq.com/openai/v1",
)

MODEL = "openai/gpt-oss-20b"
SYSTEM_PROMPT = """You classify emails as job-application-related or not.

Job-application-related means: application confirmations, interview \
invitations, assessment/coding challenge invites, recruiter outreach \
about a specific role, offer or rejection notices, or follow-ups about \
a job application the user has submitted.

NOT job-related: security alerts, newsletters, promotions, unrelated \
personal or transactional email, generic job board digests the user \
did not apply through.

Respond with ONLY a JSON object, no other text, in this exact shape:
{"is_job_related": true or false, "confidence": 0.0 to 1.0, "reason": "short explanation"}
"""


class LLMClassification(BaseModel):
    is_job_related: bool
    confidence: float
    reason: str


def classify_email_with_llm(sender: str, subject: str, body_text: str) -> LLMClassification:
    # Minimize what we send: subject + a short body snippet, not the
    # full email. This matters for both cost and privacy (Phase 0).
    body_snippet = (body_text or "")[:500]

    user_prompt = f"Sender: {sender}\nSubject: {subject}\nBody snippet: {body_snippet}"

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
    data = json.loads(raw)
    return LLMClassification(**data)