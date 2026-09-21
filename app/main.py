"""
Minimal entry point to verify the environment is wired correctly.
No Gmail, no database, no LLM yet — just config loading and a sanity check.
"""
from dotenv import load_dotenv
load_dotenv()

from app.config.settings import settings


def main() -> None:
    print("Hello, Job Agent.")
    print(f"Environment: {settings.app_env}")
    print(f"Log level:   {settings.log_level}")


if __name__ == "__main__":
    main()