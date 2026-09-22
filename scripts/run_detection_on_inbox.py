"""
Runs the detection pipeline against real ingested emails from data/emails.json.
Useful for eyeballing accuracy before building extraction on top of it.

Run: uv run python -m scripts.run_detection_on_inbox
"""

import json

from dotenv import load_dotenv
load_dotenv()

from app.detection.pipeline import classify_email


def main() -> None:
    with open("data/emails.json", "r", encoding="utf-8") as f:
        emails = json.load(f)

    print(f"Running detection on {len(emails)} emails...\n")

    job_related_count = 0
    llm_calls = 0

    for email in emails:
        result = classify_email(
            sender=email["sender"],
            subject=email["subject"],
            body_text=email["body_text"],
        )

        if result.is_job_related:
            job_related_count += 1
        if result.decided_by == "llm":
            llm_calls += 1

        marker = "✅ JOB" if result.is_job_related else "  ---"
        print(f"{marker} [{result.decided_by:5}] {email['subject'][:60]:60} | {email['sender'][:40]}")
    print(f"\n--- Summary ---")
    print(f"Total emails:       {len(emails)}")
    print(f"Job-related:        {job_related_count}")
    print(f"Decided by LLM:     {llm_calls}")
    print(f"Decided by rules:   {len(emails) - llm_calls}")


if __name__ == "__main__":
    main()