"""
Handles Gmail OAuth2 authentication.

Why a separate module: authentication is a distinct concern from *using*
the Gmail API. This module's only job is to produce valid, authorized
credentials. It knows nothing about messages, parsing, or ingestion.

Flow:
1. If a saved token exists and is valid (or refreshable), use it.
2. Otherwise, run the interactive OAuth consent flow in a browser,
   then save the resulting token to disk for next time.

This means you only need to log in once. After that, refresh tokens
handle renewing access automatically and silently.
"""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from app.config.settings import settings


def get_gmail_credentials() -> Credentials:
    creds: Credentials | None = None

    # 1. Try to load an existing token from disk.
    if os.path.exists(settings.google_token_file):
        creds = Credentials.from_authorized_user_file(
            settings.google_token_file, settings.gmail_scopes
        )

    # 2. If no valid creds, either refresh or run the interactive flow.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(settings.google_client_secret_file):
                raise FileNotFoundError(
                    f"OAuth client secret file not found at "
                    f"'{settings.google_client_secret_file}'. "
                    "Download it from Google Cloud Console → Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.google_client_secret_file, settings.gmail_scopes
            )
            creds = flow.run_local_server(port=0)

        # 3. Save the (possibly refreshed) token for next time.
        with open(settings.google_token_file, "w") as token_file:
            token_file.write(creds.to_json())

    return creds