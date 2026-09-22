"""
Deterministic application matching.

The matcher is intentionally conservative:
an application is automatically matched only when both the
company and role match after normalization.
"""

from app.matching.normalization import normalize_company, normalize_role


def applications_match(
    company_a: str | None,
    role_a: str | None,
    company_b: str | None,
    role_b: str | None,
) -> bool:
    """
    Return True only when both company and role are present
    and match after normalization.
    """
    normalized_company_a = normalize_company(company_a)
    normalized_company_b = normalize_company(company_b)

    normalized_role_a = normalize_role(role_a)
    normalized_role_b = normalize_role(role_b)

    if not all(
        [
            normalized_company_a,
            normalized_company_b,
            normalized_role_a,
            normalized_role_b,
        ]
    ):
        return False

    return (
        normalized_company_a == normalized_company_b
        and normalized_role_a == normalized_role_b
    )