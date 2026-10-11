"""Validation and canonicalisation of RFC 5321 domain literals ([IPv4] and [IPv6:...]).

Uses the standard library :mod:`ipaddress` module, so parsing is linear and there is no
risk of catastrophic regex backtracking.
"""

from __future__ import annotations

import ipaddress

_IPV6_TAG = "IPv6:"


def is_ip_literal(domain: str) -> bool:
    """Return True when the domain is bracketed, for example ``[192.168.0.1]``."""
    return len(domain) >= 2 and domain.startswith("[") and domain.endswith("]")


def parse_ip_literal(domain: str) -> str | None:
    """Return the canonical literal for a bracketed domain, or None if it is not valid.

    IPv4 literals come back as ``[1.2.3.4]``. IPv6 literals come back as
    ``[IPv6:<compressed lowercase address>]`` per RFC 5321.
    """
    inner = domain[1:-1]
    if not inner:
        return None
    if inner.startswith(_IPV6_TAG):
        return _canonical_ipv6(inner[len(_IPV6_TAG) :])
    return _canonical_ipv4(inner)


def _canonical_ipv4(text: str) -> str | None:
    try:
        parsed = ipaddress.IPv4Address(text)
    except ValueError:
        return None
    # Reject shorthand such as "127.1"; require four explicit octets.
    if text.count(".") != 3:
        return None
    return f"[{parsed.compressed}]"


def _canonical_ipv6(text: str) -> str | None:
    try:
        parsed = ipaddress.IPv6Address(text)
    except ValueError:
        return None
    return f"[{_IPV6_TAG}{parsed.compressed}]"
