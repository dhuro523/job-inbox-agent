import json

from app.extraction.extractor import extract_application_data


with open("data/emails.json", encoding="utf-8") as f:
    emails = json.load(f)


TEST_SUBJECTS = [
    "Giti//c: Thank you for submitting your application",
    "Thank you for applying to Ritual",
    "Application Submitted - Software Engineer, Python — Codebase Q&A on Mercor",
    "Application Submitted - QA / Software Engineering Reviewer – Browser Test Validation on Mercor",
    "Application Submitted - Software Engineer, C — Codebase Q&A on Mercor",
    "Application Submitted - Software Engineer, Go — Codebase Q&A on Mercor",
]


for subject in TEST_SUBJECTS:
    email = next(
        (e for e in emails if e["subject"] == subject),
        None,
    )

    if email is None:
        print(f"NOT FOUND: {subject}")
        continue

    print("=" * 80)
    print("Subject:", email["subject"])
    print("Sender:", email["sender"])

    result = extract_application_data(
        sender=email["sender"],
        subject=email["subject"],
        body_text=email["body_text"],
        received_at=email["received_at"],
    )

    print(result.model_dump_json(indent=2))
    print()