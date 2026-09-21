"""
Combined job-email detection pipeline: deterministic rules first,
LLM fallback only for ambiguous cases.

This is the single entry point the rest of the app (ingestion loop,
manual scripts, later the scheduler) should call — callers don't need
to know or care whether a given email was decided by rules or by LLM.
"""

import logging
from dataclasses import dataclass

from app.detection.llm_classifier import classify_email_with_llm
from app.detection.rules import detect_job_email

logger = logging.getLogger(__name__)


@dataclass
class FinalDetectionResult:
    is_job_related: bool
    confidence: float
    reason: str
    decided_by: str  # "rules" or "llm"


def classify_email(sender: str, subject: str, body_text: str) -> FinalDetectionResult:
    rule_result = detect_job_email(sender, subject, body_text)

    if rule_result.is_job_related is not None:
        # Rules were confident enough to decide — no LLM call needed.
        return FinalDetectionResult(
            is_job_related=rule_result.is_job_related,
            confidence=rule_result.confidence,
            reason=rule_result.reason,
            decided_by="rules",
        )

    # Ambiguous — fall through to the LLM.
    logger.info(f"Ambiguous email from '{sender}' subject '{subject}' — deferring to LLM")
    llm_result = classify_email_with_llm(sender, subject, body_text)

    return FinalDetectionResult(
        is_job_related=llm_result.is_job_related,
        confidence=llm_result.confidence,
        reason=llm_result.reason,
        decided_by="llm",
    )