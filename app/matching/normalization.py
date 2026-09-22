"""
Normalization helpers for application entity matching.

Normalization is used only for comparison.
Original values should always be preserved in the database.
"""

import re
import unicodedata


def normalize_text(value: str | None) -> str | None:
    """Normalize text for deterministic comparisons."""
    if value is None:
        return None

    value = unicodedata.normalize("NFKC", value)
    value = value.strip().lower()
    value = re.sub(r"\s+", " ", value)

    return value


def normalize_company(value: str | None) -> str | None:
    """Normalize a company name for matching."""
    return normalize_text(value)


def normalize_role(value: str | None) -> str | None:
    """Normalize a job role for matching."""
    return normalize_text(value)