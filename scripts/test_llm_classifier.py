"""
Manual smoke test for the LLM fallback classifier.
Run: uv run python -m scripts.test_llm_classifier
"""

from dotenv import load_dotenv
load_dotenv()

from app.detection.llm_classifier import classify_email_with_llm


def main() -> None:
    # A genuinely ambiguous case: mentions "position" but generic sender/subject
    result = classify_email_with_llm(
        sender="jane@randomstartup.io",
        subject="Quick question about the position",
        body_text="Hi, just wanted to follow up on our conversation last week about the open position on your team.",
    )
    print(f"is_job_related: {result.is_job_related}")
    print(f"confidence:      {result.confidence}")
    print(f"reason:          {result.reason}")


if __name__ == "__main__":
    main()