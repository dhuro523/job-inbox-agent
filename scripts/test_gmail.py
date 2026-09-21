"""
Manual smoke test for Gmail auth + client.
Run: uv run python -m scripts.test_gmail
"""

from dotenv import load_dotenv
load_dotenv()

from app.gmail.client import GmailClient


def main() -> None:
    client = GmailClient()
    ids = client.list_message_ids(max_results=3)
    print(f"Found {len(ids)} messages.")

    for msg_id in ids:
        msg = client.get_message(msg_id)
        print("---")
        print(f"From:    {msg.sender}")
        print(f"Subject: {msg.subject}")
        print(f"Date:    {msg.received_at}")
        print(f"Snippet: {msg.snippet}")


if __name__ == "__main__":
    main()