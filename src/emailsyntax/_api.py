"""Public syntax primitives: validate, normalize and split email addresses."""

from __future__ import annotations

from ._rules import MAX_ADDRESS_LENGTH, domain_is_valid, local_is_valid


def is_valid(address: str) -> bool:
    """Return True if the string is a syntactically valid email address.

    This is a pure syntax check: it never looks up DNS or touches the network. It applies
    the practical WHATWG/HTML5 rules, not full RFC 5322. The input must be ASCII, so an
    internationalized domain has to be IDNA encoded to punycode before it is passed in.
    """
    if not address or not address.isascii():
        return False
    if len(address) > MAX_ADDRESS_LENGTH:
        return False
    local, separator, domain = address.rpartition("@")
    if not separator:
        return False
    return local_is_valid(local) and domain_is_valid(domain)


def split(address: str) -> tuple[str, str]:
    """Return the (local, domain) pair, raising ValueError if the syntax is invalid."""
    if not is_valid(address):
        raise ValueError(f"not a syntactically valid email address: {address!r}")
    local, _, domain = address.rpartition("@")
    return local, domain


def normalize(address: str) -> str:
    """Trim surrounding whitespace and lowercase the domain, keeping the local part as is.

    Raises ValueError if the trimmed string is not syntactically valid.
    """
    trimmed = address.strip()
    if not is_valid(trimmed):
        raise ValueError(f"not a syntactically valid email address: {address!r}")
    local, _, domain = trimmed.rpartition("@")
    return f"{local}@{domain.lower()}"
