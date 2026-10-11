"""Syntax-only email address validation and normalization, zero dependencies, no DNS or network.

This package checks the *shape* of an email address. It never looks up DNS or MX records, never
contacts a mail server and never touches the network: a valid result means the address is well
formed, not that a mailbox exists or can receive mail. Defaults are a strict ASCII dot-atom
check; quoted local parts, IP-literal domains and internationalized (IDN/EAI) addresses are
opt-in through keyword flags.
"""

from __future__ import annotations

__version__ = "0.2.0"

from ._api import (
    is_valid,
    normalize,
    parse,
    split,
    validate,
    validate_or_raise,
)
from ._result import EmailAddress, EmailSyntaxError, FailureReason, ValidationResult

__all__ = [
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
