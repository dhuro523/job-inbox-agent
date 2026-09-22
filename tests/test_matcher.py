from app.matching.matcher import applications_match


def test_matching_company_and_role():
    assert applications_match(
        "Mercor",
        "Software Engineer, Python",
        "Mercor",
        "Software Engineer, Python",
    )


def test_matching_is_case_insensitive():
    assert applications_match(
        "MERCOR",
        "Software Engineer, Python",
        "mercor",
        "software engineer, python",
    )


def test_different_roles_do_not_match():
    assert not applications_match(
        "Mercor",
        "Software Engineer, Python",
        "Mercor",
        "Software Engineer, Go",
    )


def test_different_companies_do_not_match():
    assert not applications_match(
        "Mercor",
        "Software Engineer, Python",
        "Giti",
        "Software Engineer, Python",
    )


def test_missing_company_does_not_match():
    assert not applications_match(
        None,
        "Software Engineer, Python",
        "Mercor",
        "Software Engineer, Python",
    )


def test_missing_role_does_not_match():
    assert not applications_match(
        "Mercor",
        None,
        "Mercor",
        "Software Engineer, Python",
    )


def test_whitespace_is_ignored():
    assert applications_match(
        "  Mercor  ",
        "  Software Engineer, Python  ",
        "mercor",
        "software engineer, python",
    )