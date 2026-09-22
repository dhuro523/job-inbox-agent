from unittest.mock import MagicMock, patch

from app.extraction.extractor import extract_application_data


def test_extract_application_data():
    fake_response = MagicMock()

    fake_response.choices[0].message.content = """
    {
        "company": "Mercor",
        "role": "Software Engineer, Python — Codebase Q&A",
        "location": null,
        "employment_type": null,
        "event_type": "APPLICATION_SUBMITTED",
        "event_date": null,
        "deadline": null,
        "application_status": null,
        "source": "email",
        "confidence": 0.95
    }
    """

    with patch(
        "app.extraction.extractor._client.chat.completions.create",
        return_value=fake_response,
    ):
        result = extract_application_data(
            sender="Mercor <noreply@example.com>",
            subject="Application Submitted",
            body_text="Thank you for submitting your application.",
            received_at="2026-09-22T10:00:00",
        )

    assert result.company == "Mercor"
    assert result.role == "Software Engineer, Python — Codebase Q&A"
    assert result.event_type == "APPLICATION_SUBMITTED"
    assert result.location is None
    assert result.deadline is None
    assert result.confidence == 0.95