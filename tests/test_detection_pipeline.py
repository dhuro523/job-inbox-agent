"""
Unit tests for the combined detection pipeline.
Uses a fake LLM classifier so these tests run fast, free, and
deterministically — no real Groq API calls in the normal test suite.
"""

from unittest.mock import patch

from app.detection.llm_classifier import LLMClassification
from app.detection.pipeline import classify_email


def test_confident_positive_rule_skips_llm():
    with patch("app.detection.pipeline.classify_email_with_llm") as mock_llm:
        result = classify_email(
            sender="no-reply@us.greenhouse-mail.io",
            subject="Thank you for applying to Ritual",
            body_text="Thanks for applying to Ritual. Your application has been received.",
        )
        assert result.is_job_related is True
        assert result.decided_by == "rules"
        mock_llm.assert_not_called()


def test_confident_negative_rule_skips_llm():
    with patch("app.detection.pipeline.classify_email_with_llm") as mock_llm:
        result = classify_email(
            sender="Google <no-reply@accounts.google.com>",
            subject="Security alert",
            body_text="2-Step Verification backup codes generated.",
        )
        assert result.is_job_related is False
        assert result.decided_by == "rules"
        mock_llm.assert_not_called()


def test_ambiguous_email_calls_llm():
    fake_llm_response = LLMClassification(
        is_job_related=True,
        confidence=0.9,
        reason="Follow-up about an open position.",
    )
    with patch(
        "app.detection.pipeline.classify_email_with_llm",
        return_value=fake_llm_response,
    ) as mock_llm:
        result = classify_email(
            sender="jane@randomstartup.io",
            subject="Quick question about the position",
            body_text="Just following up about the open position.",
        )
        assert result.is_job_related is True
        assert result.decided_by == "llm"
        mock_llm.assert_called_once()