# tests/test_detection_rules.py
"""
Unit tests for deterministic job-email detection rules.
Uses realistic sender/subject patterns rather than synthetic data,
since the whole point of this module is real-world accuracy.
"""

from app.detection.rules import detect_job_email


def test_greenhouse_application_confirmation_is_job_related():
    result = detect_job_email(
        sender="no-reply@us.greenhouse-mail.io",
        subject="Thank you for applying to Ritual",
        body_text="Thanks for applying to Ritual. Your application has been received.",
    )
    assert result.is_job_related is True
    assert result.confidence > 0.8


def test_mercor_application_submitted_is_job_related():
    result = detect_job_email(
        sender="Mercor <team@mercor.com>",
        subject="Application Submitted - Software Engineer, Python",
        body_text="We've received your application for the Software Engineer role.",
    )
    assert result.is_job_related is True


def test_google_security_alert_is_not_job_related():
    result = detect_job_email(
        sender="Google <no-reply@accounts.google.com>",
        subject="Security alert",
        body_text="2-Step Verification backup codes generated for your account.",
    )
    assert result.is_job_related is False


def test_promotional_email_is_not_job_related():
    result = detect_job_email(
        sender="Codecademy <learn@itr.mail.codecademy.com>",
        subject="Final hours: 50% off Pro",
        body_text="Our sale ends at midnight! Use promo code LEARNFALL to save 50%.",
    )
    assert result.is_job_related is False

def test_ambiguous_email_defers_to_llm():
    # Exactly one weak positive signal ("position"), no platform domain
    # match, and no negative signal — not enough to decide confidently
    # either way, so this should be deferred to the LLM.
    result = detect_job_email(
        sender="jane@randomstartup.io",
        subject="Quick question about the position",
        body_text="Hi, just wanted to follow up on our conversation last week.",
    )
    assert result.is_job_related is None


def test_linkedin_job_alert_is_job_related():
    result = detect_job_email(
        sender="LinkedIn Job Alerts <jobalerts-noreply@linkedin.com>",
        subject="QAIrbon is hiring a Junior Data Analyst",
        body_text="New jobs match your preferences. Junior Data Analyst at QAIrbon.",
    )
    assert result.is_job_related is True