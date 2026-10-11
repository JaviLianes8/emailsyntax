import pytest

from emailsyntax import normalize, split


def test_normalize_lowercases_the_domain() -> None:
    assert normalize("user@Example.COM") == "user@example.com"


def test_normalize_keeps_the_local_part_case() -> None:
    assert normalize("User.Name@Example.com") == "User.Name@example.com"


def test_normalize_trims_surrounding_whitespace() -> None:
    assert normalize("  user@example.com\n") == "user@example.com"


def test_normalize_rejects_invalid_input() -> None:
    with pytest.raises(ValueError):
        normalize("not-an-email")


def test_split_returns_local_and_domain() -> None:
    assert split("user@example.com") == ("user", "example.com")


def test_split_keeps_subdomains_in_the_domain() -> None:
    assert split("a.b@mail.example.co.uk") == ("a.b", "mail.example.co.uk")


def test_split_does_not_lowercase() -> None:
    assert split("User@Example.COM") == ("User", "Example.COM")


def test_split_rejects_invalid_input() -> None:
    with pytest.raises(ValueError):
        split("user@@example.com")
