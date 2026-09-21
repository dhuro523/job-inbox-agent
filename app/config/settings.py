"""
Centralized application configuration.

Why this exists: instead of scattering os.getenv() calls across the codebase,
every setting is loaded once, in one place, with explicit types and defaults.
This makes it obvious what configuration the app depends on, and makes
misconfiguration fail fast (at startup) instead of silently later.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_env: str
    log_level: str
    google_client_secret_file: str
    google_token_file: str
    gmail_scopes: list[str]


def load_settings() -> Settings:
    scopes_raw = os.getenv(
        "GMAIL_SCOPES", "https://www.googleapis.com/auth/gmail.readonly"
    )
    return Settings(
        app_env=os.getenv("APP_ENV", "local"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        google_client_secret_file=os.getenv(
            "GOOGLE_CLIENT_SECRET_FILE", "client_secret.json"
        ),
        google_token_file=os.getenv("GOOGLE_TOKEN_FILE", "token.json"),
        gmail_scopes=[s.strip() for s in scopes_raw.split(",")],
    )


settings = load_settings()