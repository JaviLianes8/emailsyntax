"""Syntax rules for email addresses: character sets and length limits."""

from __future__ import annotations

import re

MAX_ADDRESS_LENGTH = 254
MAX_LOCAL_LENGTH = 64
MAX_DOMAIN_LENGTH = 255

_LOCAL_SEGMENT = re.compile(r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+")
_DOMAIN_LABEL = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?")


def local_is_valid(local: str) -> bool:
    """A non-empty local part whose dot-separated atoms use only the allowed characters."""
    if not local or len(local) > MAX_LOCAL_LENGTH:
        return False
    # Splitting on the dot rejects leading, trailing and consecutive dots: an empty atom
    # cannot match the one-or-more pattern below.
    return all(_fullmatch(_LOCAL_SEGMENT, atom) for atom in local.split("."))


def domain_is_valid(domain: str) -> bool:
    """A dotted domain of valid labels: no dotless domains, no leading or trailing hyphens."""
    if not domain or len(domain) > MAX_DOMAIN_LENGTH:
        return False
    labels = domain.split(".")
    if len(labels) < 2:
        return False
    return all(_fullmatch(_DOMAIN_LABEL, label) for label in labels)


def _fullmatch(pattern: re.Pattern[str], value: str) -> bool:
    return pattern.fullmatch(value) is not None
