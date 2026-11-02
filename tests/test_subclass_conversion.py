"""Hand-written contracts for subclass string-conversion hooks."""

from __future__ import annotations

from typing import SupportsIndex

import pytest

import emailsyntax as e


@pytest.mark.parametrize(
    "name", ["validate", "is_valid", "parse", "validate_or_raise", "split", "normalize"]
)
@pytest.mark.parametrize(
    "method", ["__add__", "removeprefix", "__mul__", "replace", "removesuffix", "ljust", "rjust"]
)
@pytest.mark.parametrize("raises", [False, True], ids=["forged", "raising"])
@pytest.mark.parametrize("address", ["not-an-address", "User@Example.COM"])
def test_subclass_conversion_never_overrides_underlying_input(
    name: str, method: str, raises: bool, address: str
) -> None:
    accesses: list[object] = []

    def override(argument: object) -> str:
        accesses.append(argument)
        if raises:
            raise RuntimeError("private-token")
        return "a@b.co"

    class HostileAddition(str):
        def __add__(self, other: str) -> str:
            return override(other)

    class HostilePrefixRemoval(str):
        def removeprefix(self, prefix: str, /) -> str:
            return override(prefix)

    class HostileMultiplication(str):
        def __mul__(self, count: SupportsIndex, /) -> str:
            return override(count)

    class HostileReplacement(str):
        def replace(self, old: str, new: str, /, count: SupportsIndex = -1) -> str:
            return override((old, new, count))

    class HostileSuffixRemoval(str):
        def removesuffix(self, suffix: str, /) -> str:
            return override(suffix)

    class HostileLeftJustification(str):
        def ljust(self, width: SupportsIndex, fillchar: str = " ", /) -> str:
            return override((width, fillchar))

    class HostileRightJustification(str):
        def rjust(self, width: SupportsIndex, fillchar: str = " ", /) -> str:
            return override((width, fillchar))

    subclasses: dict[str, type[str]] = {
        "__add__": HostileAddition,
        "removeprefix": HostilePrefixRemoval,
        "__mul__": HostileMultiplication,
        "replace": HostileReplacement,
        "removesuffix": HostileSuffixRemoval,
        "ljust": HostileLeftJustification,
        "rjust": HostileRightJustification,
    }
    subclass = subclasses[method]
    function = getattr(e, name)
    if address == "User@Example.COM":
        result = function(subclass(address))
        assert result == function(address)
        if name == "validate":
            assert type(result.address) is str and result.address == address
    elif name == "is_valid":
        assert function(subclass(address)) is False
    elif name == "validate":
        result = function(subclass(address))
        assert not result and result.code == "no_at"
        assert type(result.address) is str and result.address == address
    else:
        with pytest.raises(e.EmailSyntaxError) as caught:
            function(subclass(address))
        assert caught.value.code == "no_at"
        assert type(caught.value.address) is str and caught.value.address == address
    assert accesses == []
