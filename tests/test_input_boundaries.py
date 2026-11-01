"""Hand-written contracts for normalization limits and hostile string subclasses."""

from __future__ import annotations

import pytest

import emailsyntax as e

APIS = ["validate", "is_valid", "parse", "validate_or_raise", "split", "normalize"]


@pytest.mark.parametrize("name", APIS)
@pytest.mark.parametrize("spoof", [False, True], ids=["raising-class", "spoofed-class"])
def test_wrong_type_never_reads_class_property(name: str, spoof: bool) -> None:
    accesses: list[str] = []

    class HostileAddress:
        @property  # type: ignore[misc]
        def __class__(self) -> type[object]:  # type: ignore[override]
            accesses.append("__class__")
            if spoof:
                return str
            raise RuntimeError("private-token")

    with pytest.raises(TypeError, match=r"^address must be a string$"):
        getattr(e, name)(HostileAddress())
    assert accesses == []


class ForgedString(str):
    def rpartition(self, sep: str) -> tuple[str, str, str]:
        return "a", "@", "b.co"

    def strip(self, chars: str | None = None) -> str:
        return self

    def __str__(self) -> str:
        return "a@b.co"


class ExplodingString(str):
    def __len__(self) -> int:
        raise RuntimeError("private-token")

    def __bool__(self) -> bool:
        raise RuntimeError("private-token")

    def strip(self, chars: str | None = None) -> str:
        raise RuntimeError("private-token")

    def __str__(self) -> str:
        raise RuntimeError("private-token")


@pytest.mark.parametrize("name", APIS)
def test_subclass_cannot_forge_validation(name: str) -> None:
    function = getattr(e, name)
    address = ForgedString("not-an-address")
    if name == "is_valid":
        assert function(address) is False
    elif name == "validate":
        result = function(address)
        assert not result and result.code == "no_at"
        assert type(result.address) is str and result.address == "not-an-address"
    else:
        with pytest.raises(e.EmailSyntaxError) as caught:
            function(address)
        assert caught.value.code == "no_at"
        assert type(caught.value.address) is str
        assert caught.value.address == "not-an-address"


@pytest.mark.parametrize("name", APIS)
@pytest.mark.parametrize("address", ["a@b.co", "bad", ""])
def test_subclass_overrides_are_never_called(name: str, address: str) -> None:
    function = getattr(e, name)
    if address == "a@b.co" or name in ("validate", "is_valid"):
        assert function(ExplodingString(address)) == function(address)
    else:
        with pytest.raises(e.EmailSyntaxError) as caught:
            function(ExplodingString(address))
        assert caught.value.address == address
        assert type(caught.value.address) is str
        assert "private-token" not in str(caught.value)


@pytest.mark.parametrize("name", APIS)
@pytest.mark.parametrize("suffix", ["co", "de"])
def test_normalized_character_overflow_is_rejected(name: str, suffix: str) -> None:
    address = "a@\u0130" + "\u00ad" * 248 + "." + suffix
    assert len(address) == 254
    function = getattr(e, name)
    if name == "is_valid":
        assert function(address, allow_unicode=True) is False
    elif name == "validate":
        result = function(address, allow_unicode=True)
        assert not result and result.code == "address_too_long"
        assert result.normalized is None
    else:
        with pytest.raises(e.EmailSyntaxError) as caught:
            function(address, allow_unicode=True)
        assert caught.value.code == "address_too_long"


@pytest.mark.parametrize("padding", [0, 246, 247])
def test_lowercase_expansion_at_character_boundary_is_idempotent(padding: int) -> None:
    address = "a@\u0130" + "\u00ad" * padding + ".co"
    normalized = e.normalize(address, allow_unicode=True)
    assert normalized == "a@i\u0307" + "\u00ad" * padding + ".co"
    assert len(normalized) <= 254
    assert e.validate(normalized, allow_unicode=True).valid
    assert e.normalize(normalized, allow_unicode=True) == normalized


@pytest.mark.parametrize("last_label, valid", [(51, True), (52, False)])
def test_normalized_encoded_length_boundary(last_label: int, valid: bool) -> None:
    domain = "\u0130." + ".".join(["b" * 63, "c" * 63, "d" * last_label])
    address = "a" * 64 + "@" + domain
    assert len(address) < 254
    assert len(("a" * 64 + "@" + domain.lower().encode("idna").decode()).encode()) == (
        254 if valid else 255
    )
    result = e.validate(address, allow_unicode=True)
    assert result.valid is valid
    if valid:
        assert result.normalized is not None
        assert e.normalize(result.normalized, allow_unicode=True) == result.normalized
    else:
        assert result.code == "address_too_long"
