"""
Deterministic, rule-based job-email detection.

Why deterministic-first: most emails are trivially classifiable by sender
and subject alone (a LinkedIn job alert, a Greenhouse confirmation, a
Google security notice). Running these through an LLM would be slow,
costly, and an unnecessary privacy exposure. This module handles the
easy majority; only genuinely ambiguous cases fall through to the LLM
classifier in llm_classifier.py.
"""

from dataclasses import dataclass


# Known Applicant Tracking Systems / job platforms — strong positive signal
JOB_PLATFORM_DOMAINS = [
    "greenhouse-mail.io",
    "greenhouse.io",
    "lever.co",
    "myworkday.com",
    "workday.com",
    "icims.com",
    "smartrecruiters.com",
    "ashbyhq.com",
    "bamboohr.com",
    "mercor.com",
    "linkedin.com",
]

# Subject/body keywords that suggest job-application content
POSITIVE_KEYWORDS = [
    "application submitted",
    "thank you for applying",
    "thanks for applying",
    "your application",
    "application received",
    "interview",
    "assessment",
    "coding challenge",
    "technical screen",
    "next steps",
    "we regret to inform",
    "unfortunately",
    "not moving forward",
    "offer",
    "candidate",
    "recruiter",
    "hiring",
    "position",
    "role you applied",
]

# Strong negative signals — these push AWAY from job-related even if
# other weak signals are present
NEGATIVE_KEYWORDS = [
    "verification code",
    "security alert",
    "password reset",
    "sign-in",
    "sign in",
    "2-step verification",
    "payment successful",
    "invoice",
    "unsubscribe from this newsletter",
    "% off",
    "discount",
    "sale ends",
]


@dataclass
class DetectionResult:
    is_job_related: bool | None  # None = ambiguous, needs LLM
    confidence: float
    reason: str


def detect_job_email(sender: str, subject: str, body_text: str) -> DetectionResult:
    """
    Applies deterministic rules to decide if an email is job-related.
    Returns is_job_related=None when the signal is too weak/mixed to
    decide confidently — caller should then use the LLM classifier.
    """
    sender_lower = sender.lower()
    subject_lower = (subject or "").lower()
    body_lower = (body_text or "").lower()[:2000]  # cap to avoid scanning huge bodies

    domain_match = any(domain in sender_lower for domain in JOB_PLATFORM_DOMAINS)

    positive_hits = [kw for kw in POSITIVE_KEYWORDS if kw in subject_lower or kw in body_lower]
    negative_hits = [kw for kw in NEGATIVE_KEYWORDS if kw in subject_lower or kw in body_lower]

    # Strong negative signal wins outright — e.g. a security alert from
    # a platform that also sends job emails (like Google) should not
    # be misclassified just because "Google" sounds job-adjacent.
    if negative_hits and not domain_match:
        return DetectionResult(
            is_job_related=False,
            confidence=0.9,
            reason=f"Negative signal(s) matched: {negative_hits[:3]}",
        )

    # Strong positive: known platform domain AND keyword match
    if domain_match and positive_hits:
        return DetectionResult(
            is_job_related=True,
            confidence=0.95,
            reason=f"Known job platform domain + keywords: {positive_hits[:3]}",
        )

    # Strong positive: multiple keyword hits even without domain match
    # (covers direct company ATS emails we don't have in our domain list)
    if len(positive_hits) >= 2:
        return DetectionResult(
            is_job_related=True,
            confidence=0.85,
            reason=f"Multiple keyword matches: {positive_hits[:3]}",
        )

    # Weak/no signal at all — confidently not job-related
    if not domain_match and not positive_hits:
        return DetectionResult(
            is_job_related=False,
            confidence=0.85,
            reason="No job-related domain or keyword signals found",
        )

    # Everything else is genuinely ambiguous — let the LLM decide
    return DetectionResult(
        is_job_related=None,
        confidence=0.5,
        reason="Mixed or weak signals — deferring to LLM classifier",
    )