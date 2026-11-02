"""Hand-written contracts for public limits, failures and value objects."""

from __future__ import annotations

import copy
import inspect
import pickle
from dataclasses import FrozenInstanceError
from typing import get_type_hints

import pytest

import emailsyntax as e


@pytest.mark.parametrize(
    "name", ["is_valid", "validate", "parse", "validate_or_raise", "split", "normalize"]
)
def test_function_signatures_and_types(name: str) -> None:
    function = getattr(e, name)
    parameters = inspect.signature(function).parameters
    assert list(parameters) == ["address", "allow_unicode", "allow_quoted", "allow_ip_literal"]
    for option in list(parameters.values())[1:]:
        assert option.default is False
        assert option.kind == inspect.Parameter.KEYWORD_ONLY
    assert get_type_hints(function)["address"] is str
    wrong_values: tuple[object, ...] = (None, 123, b"a@b.co", [], {})
    for value in wrong_values:
        with pytest.raises(TypeError, match="address must be a string"):
            function(value)
    for option_name in ("allow_unicode", "allow_quoted", "allow_ip_literal"):
        with pytest.raises(TypeError, match="allow options must be bool"):
            function("", **{option_name: 1})


@pytest.mark.parametrize(
    ("address", "code"),
    [
        ("", "empty"),
        ("\u00e9@a.co", "not_ascii"),
        ("x" * 255, "address_too_long"),
        ("bad", "no_at"),
        ("@a.co", "empty_local"),
        ("a" * 65 + "@a.co", "local_too_long"),
        ("a..b@a.co", "local_bad_dot"),
        ("a b@a.co", "local_bad_char"),
        ('"a"@a.co', "quoted_not_allowed"),
        ("a@", "empty_domain"),
        ("a@local", "domain_not_dotted"),
        ("a@b..co", "label_empty"),
        ("a@" + "b" * 64 + ".co", "label_too_long"),
        ("a@b_c.co", "label_bad_char"),
        ("a@-b.co", "label_hyphen"),
        ("a@[1.2.3.4]", "ip_literal_not_allowed"),
    ],
)
def test_failure_contract(address: str, code: str) -> None:
    result = e.validate(address)
    assert result.address == address and not result and not e.is_valid(address)
    assert result.code == code
    assert result.reason == e.FailureReason(code).message
    assert (result.local, result.domain, result.normalized) == (None, None, None)
    assert not result.is_quoted_local and not result.is_ip_literal
    for function in (e.parse, e.validate_or_raise, e.split, e.normalize):
        with pytest.raises(e.EmailSyntaxError) as caught:
            function(address)
        error = caught.value
        assert error.code == code and error.address == address
        assert error.failure is e.FailureReason(code)
        assert str(error) == error.reason == result.reason


@pytest.mark.parametrize(
    ("address", "code"),
    [
        ('"a@b.co', "quoted_unterminated"),
        ('"a\\"@b.co', "quoted_unterminated"),
        ('"a\n"@b.co', "quoted_bad_char"),
        ('"a\\\n"@b.co', "quoted_bad_char"),
        ('"a\\\u00e9"@b.co', "quoted_bad_char"),
        ("a@[300.1.1.1]", "ip_literal_invalid"),
        ("a@[IPv6:fe80::1%zone]", "ip_literal_invalid"),
        ("a@\u00e9_.co", "unicode_label_invalid"),
        ("a@b\u3002c.co", "unicode_label_invalid"),
        ("a@\u00ad.co", "unicode_label_invalid"),
    ],
)
def test_optional_failure_codes(address: str, code: str) -> None:
    result = e.validate(address, allow_unicode=True, allow_quoted=True, allow_ip_literal=True)
    assert result.code == code


def test_lengths_measure_utf8_local_and_idna_domain() -> None:
    assert e.is_valid("\u00e9" * 32 + "@a.co", allow_unicode=True)
    assert e.validate("\u00e9" * 33 + "@a.co", allow_unicode=True).code == "local_too_long"
    domain = ".".join(["b" * 63, "c" * 63, "d" * 61])
    assert len("a" * 64 + "@" + domain) == 254
    assert e.is_valid("a" * 64 + "@" + domain)
    assert not e.is_valid("a" * 64 + "@" + domain + "d")
    domain = ".".join(["\u00e9" * 57] * 4)
    assert e.validate("a@" + domain, allow_unicode=True).code == "address_too_long"


def test_error_never_formats_input_and_supports_copy_and_pickle() -> None:
    secret = "private-token" * 100000
    with pytest.raises(e.EmailSyntaxError) as caught:
        e.parse(secret)
    error = caught.value
    assert len(str(error)) < 100 and "private-token" not in repr(error)
    assert error.address is secret
    for clone in (copy.copy(error), copy.deepcopy(error), pickle.loads(pickle.dumps(error))):
        assert clone.address == secret and clone.failure is error.failure
        assert clone.args == error.args


def test_result_objects_are_frozen_values() -> None:
    parsed = e.parse('"A@B"@[ipv6:2001:DB8::1]', allow_quoted=True, allow_ip_literal=True)
    assert parsed == e.EmailAddress(
        '"A@B"', "[ipv6:2001:DB8::1]", '"A@B"@[IPv6:2001:db8::1]', True, True
    )
    assert str(parsed) == '"A@B"@[ipv6:2001:DB8::1]'
    for value in (parsed, e.validate("User@Example.COM")):
        assert pickle.loads(pickle.dumps(value)) == value
        assert copy.copy(value) == value
        assert hash(value) == hash(copy.deepcopy(value))
        with pytest.raises(FrozenInstanceError):
            attribute = "local"
            setattr(value, attribute, "changed")
    result = e.validate("User@Example.COM")
    assert result.code is result.reason is None


def test_failure_enum_is_exact_and_includes_reserved_domain_length() -> None:
    assert {reason.value for reason in e.FailureReason} == {
        "empty",
        "not_ascii",
        "address_too_long",
        "no_at",
        "empty_local",
        "local_too_long",
        "local_bad_dot",
        "local_bad_char",
        "quoted_not_allowed",
        "quoted_unterminated",
        "quoted_bad_char",
        "empty_domain",
        "domain_too_long",
        "domain_not_dotted",
        "label_empty",
        "label_too_long",
        "label_bad_char",
        "label_hyphen",
        "unicode_label_invalid",
        "ip_literal_not_allowed",
        "ip_literal_invalid",
    }
    assert e.FailureReason.DOMAIN_TOO_LONG.message == "domain is longer than 255 characters"


def test_normalization_is_idempotent_and_only_normalize_trims() -> None:
    for address in (" User@Example.COM ", "\tUser@Example.COM\n"):
        assert not e.is_valid(address)
        assert e.normalize(address) == "User@example.com"
        assert e.normalize(e.normalize(address)) == e.normalize(address)
    assert e.normalize("User@M\u00dcNCHEN.DE", allow_unicode=True) == "User@m\u00fcnchen.de"
    assert e.split("User@Example.COM") == ("User", "Example.COM")
