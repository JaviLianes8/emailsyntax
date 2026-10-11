import importlib.resources

import pytest

import emailsyntax
from emailsyntax import (
    EmailAddress,
    EmailSyntaxError,
    FailureReason,
    ValidationResult,
    is_valid,
    normalize,
    parse,
    split,
    validate,
    validate_or_raise,
)

# The public API. Add every exported name here as the library grows; this list is the
# contract and the test below fails if the module and this list disagree.
PUBLIC_API: list[str] = [
    "EmailAddress",
    "EmailSyntaxError",
    "FailureReason",
    "ValidationResult",
    "is_valid",
    "normalize",
    "parse",
    "split",
    "validate",
    "validate_or_raise",
]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(emailsyntax.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in emailsyntax.__all__:
        assert hasattr(emailsyntax, name)


def test_version_is_a_three_part_string() -> None:
    parts = emailsyntax.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("emailsyntax").joinpath("py.typed").is_file()


# The complete promise of the strict (default) mode, over tricky RFC-flavoured cases.
STRICT_VALID = [
    "user@example.com",
    "a@b.co",
    "first.last@example.co.uk",
    "USER@Example.COM",
    "user+tag@example.com",
    "x!#$%&'*+/=?^_`{|}~@example.com",
    "user@a-b.example.com",
    "1234567890@example.com",
]

STRICT_INVALID = [
    "",
    "plainaddress",
    "@example.com",
    "user@",
    "user@localhost",
    ".user@example.com",
    "user.@example.com",
    "us..er@example.com",
    "user@-example.com",
    "user@example-.com",
    "user name@example.com",
    "user@exámple.com",
    '"john doe"@example.com',
    "user@[192.168.0.1]",
]


@pytest.mark.parametrize("address", STRICT_VALID)
def test_strict_mode_accepts(address: str) -> None:
    assert is_valid(address) is True
    assert bool(validate(address)) is True


@pytest.mark.parametrize("address", STRICT_INVALID)
def test_strict_mode_rejects(address: str) -> None:
    assert is_valid(address) is False
    assert bool(validate(address)) is False


def test_quoted_local_is_opt_in() -> None:
    assert is_valid('"john doe"@example.com') is False
    assert is_valid('"john doe"@example.com', allow_quoted=True) is True
    assert is_valid(r'"a\"b"@example.com', allow_quoted=True) is True
    assert is_valid('"unterminated@example.com', allow_quoted=True) is False


def test_ip_literals_are_opt_in_and_canonicalised() -> None:
    assert is_valid("user@[192.168.0.1]") is False
    assert is_valid("user@[192.168.0.1]", allow_ip_literal=True) is True
    assert is_valid("user@[IPv6:2001:db8::1]", allow_ip_literal=True) is True
    assert is_valid("user@[999.1.1.1]", allow_ip_literal=True) is False
    result = validate("user@[IPv6:2001:DB8::0:1]", allow_ip_literal=True)
    assert result.is_ip_literal is True
    assert result.normalized == "user@[IPv6:2001:db8::1]"


def test_unicode_is_opt_in() -> None:
    assert is_valid("josé@example.com") is False
    assert is_valid("josé@example.com", allow_unicode=True) is True
    assert is_valid("user@münchen.de", allow_unicode=True) is True
    assert is_valid("user@xn--mnchen-3ya.de") is True


def test_validate_reports_a_reason_and_code() -> None:
    result = validate("user@localhost")
    assert isinstance(result, ValidationResult)
    assert result.valid is False
    assert result.code == FailureReason.DOMAIN_NOT_DOTTED.value
    assert result.reason == FailureReason.DOMAIN_NOT_DOTTED.message
    assert result.local is None and result.domain is None


def test_validate_fills_parsed_fields_when_valid() -> None:
    result = validate("First.Last@Sub.Example.COM")
    assert result.valid is True
    assert result.local == "First.Last"
    assert result.domain == "Sub.Example.COM"
    assert result.normalized == "First.Last@sub.example.com"


def test_validate_or_raise_returns_parsed_address() -> None:
    parsed = validate_or_raise("a.b@example.com")
    assert isinstance(parsed, EmailAddress)
    assert parsed.local == "a.b"
    assert parsed.domain == "example.com"
    assert str(parsed) == "a.b@example.com"
    assert parse("a.b@example.com") == parsed


def test_validate_or_raise_raises_typed_error() -> None:
    with pytest.raises(EmailSyntaxError) as info:
        validate_or_raise("nope")
    error = info.value
    assert isinstance(error, ValueError)
    assert error.code == FailureReason.NO_AT.value
    assert error.address == "nope"


def test_split_and_normalize_still_work() -> None:
    assert split("user@sub.example.com") == ("user", "sub.example.com")
    assert normalize("  User@Example.COM ") == "User@example.com"
    with pytest.raises(EmailSyntaxError):
        split("user@@localhost")


def test_every_failure_reason_has_a_message() -> None:
    for reason in FailureReason:
        assert reason.message
        assert reason.value
