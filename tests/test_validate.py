import pytest

from emailsyntax import is_valid

VALID = [
    "user@example.com",
    "a@b.co",
    "first.last@example.co.uk",
    "USER@Example.COM",
    "user+tag@example.com",
    "user_name@example.com",
    "user-name@sub.example.com",
    "x!#$%&'*+/=?^_`{|}~@example.com",
    "1234567890@example.com",
    "a@a-b.example.com",
]

INVALID = [
    "",
    "plainaddress",
    "@example.com",
    "user@",
    "user@@example.com",
    "user@localhost",
    "user@example",
    ".user@example.com",
    "user.@example.com",
    "us..er@example.com",
    "user@.example.com",
    "user@example.com.",
    "user@exa..mple.com",
    "user@-example.com",
    "user@example-.com",
    "user name@example.com",
    "user@exam ple.com",
    " user@example.com",
    "user@example.com ",
    "user@exámple.com",
    "usér@example.com",
]


@pytest.mark.parametrize("address", VALID)
def test_accepts_valid_addresses(address: str) -> None:
    assert is_valid(address) is True


@pytest.mark.parametrize("address", INVALID)
def test_rejects_invalid_addresses(address: str) -> None:
    assert is_valid(address) is False


def test_rejects_local_part_over_sixty_four_characters() -> None:
    assert is_valid("a" * 64 + "@example.com") is True
    assert is_valid("a" * 65 + "@example.com") is False


def test_rejects_address_over_two_hundred_fifty_four_characters() -> None:
    local = "a" * 64
    domain = ".".join(["abcdefghij"] * 18) + ".com"
    address = f"{local}@{domain}"
    assert len(address) > 254
    assert is_valid(address) is False


def test_rejects_label_over_sixty_three_characters() -> None:
    assert is_valid("user@" + "a" * 63 + ".com") is True
    assert is_valid("user@" + "a" * 64 + ".com") is False


def test_rejects_non_ascii_without_crashing() -> None:
    assert is_valid("user@xn--mnchen-3ya.de") is True
