from app.matching.normalization import (
    normalize_company,
    normalize_role,
    normalize_text,
)


def test_normalize_text():
    assert normalize_text("  Hello   WORLD  ") == "hello world"


def test_normalize_text_none():
    assert normalize_text(None) is None


def test_normalize_company():
    assert normalize_company("  MERCOR  ") == "mercor"


def test_normalize_role():
    role = "Software   Engineer, Python — Codebase Q&A"
    assert normalize_role(role) == "software engineer, python — codebase q&a"


def test_normalize_unicode():
    assert normalize_text("Café") == "café"


def test_normalize_preserves_original_punctuation():
    value = "QA / Software Engineering Reviewer"
    assert normalize_text(value) == "qa / software engineering reviewer"