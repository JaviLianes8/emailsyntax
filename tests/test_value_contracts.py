"""Hand-written contracts for all value fields and quoted-local metadata."""

from __future__ import annotations

from dataclasses import asdict, fields, replace

import pytest

import emailsyntax as e


def test_validate_preserves_quoted_local_metadata() -> None:
    assert asdict(e.validate('"a b"@Example.COM', allow_quoted=True)) == {
        "address": '"a b"@Example.COM',
        "valid": True,
        "code": None,
        "reason": None,
        "local": '"a b"',
        "domain": "Example.COM",
        "normalized": '"a b"@example.com',
        "is_quoted_local": True,
        "is_ip_literal": False,
    }


@pytest.mark.parametrize("field", [field.name for field in fields(e.EmailAddress)])
def test_email_address_equality_includes_every_field(field: str) -> None:
    original = e.EmailAddress("a", "b.co", "a@b.co")
    value = getattr(original, field)
    changes = asdict(original)
    changes[field] = not value if isinstance(value, bool) else "changed"
    changed = replace(original, **changes)
    assert changed != original
    assert len({original, changed}) == 2
    assert changed not in {original}
    assert replace(original) == original
    assert hash(replace(original)) == hash(original)


@pytest.mark.parametrize("field", [field.name for field in fields(e.ValidationResult)])
def test_validation_result_equality_includes_every_field(field: str) -> None:
    original = e.ValidationResult("a@b.co", True)
    value = getattr(original, field)
    changes = asdict(original)
    changes[field] = not value if isinstance(value, bool) else "changed"
    changed = replace(original, **changes)
    assert changed != original
    assert len({original, changed}) == 2
    assert changed not in {original}
    assert replace(original) == original
    assert hash(replace(original)) == hash(original)
