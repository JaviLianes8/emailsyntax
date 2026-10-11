"""Typed result objects, failure reasons and the error raised by the raising API."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class FailureReason(Enum):
    """Every reason an address can be rejected. The value is a stable machine code."""

    EMPTY = "empty"
    NOT_ASCII = "not_ascii"
    ADDRESS_TOO_LONG = "address_too_long"
    NO_AT = "no_at"
    EMPTY_LOCAL = "empty_local"
    LOCAL_TOO_LONG = "local_too_long"
    LOCAL_BAD_DOT = "local_bad_dot"
    LOCAL_BAD_CHAR = "local_bad_char"
    QUOTED_NOT_ALLOWED = "quoted_not_allowed"
    QUOTED_UNTERMINATED = "quoted_unterminated"
    QUOTED_BAD_CHAR = "quoted_bad_char"
    EMPTY_DOMAIN = "empty_domain"
    DOMAIN_TOO_LONG = "domain_too_long"
    DOMAIN_NOT_DOTTED = "domain_not_dotted"
    LABEL_EMPTY = "label_empty"
    LABEL_TOO_LONG = "label_too_long"
    LABEL_BAD_CHAR = "label_bad_char"
    LABEL_HYPHEN = "label_hyphen"
    UNICODE_LABEL_INVALID = "unicode_label_invalid"
    IP_LITERAL_NOT_ALLOWED = "ip_literal_not_allowed"
    IP_LITERAL_INVALID = "ip_literal_invalid"

    @property
    def message(self) -> str:
        """A short, human readable explanation for this reason."""
        return _MESSAGES[self]


_MESSAGES: dict[FailureReason, str] = {
    FailureReason.EMPTY: "address is empty",
    FailureReason.NOT_ASCII: "address has non-ASCII characters and allow_unicode is False",
    FailureReason.ADDRESS_TOO_LONG: "address is longer than 254 characters",
    FailureReason.NO_AT: "address has no '@' separator",
    FailureReason.EMPTY_LOCAL: "local part is empty",
    FailureReason.LOCAL_TOO_LONG: "local part is longer than 64 characters",
    FailureReason.LOCAL_BAD_DOT: "local part has a leading, trailing or double dot",
    FailureReason.LOCAL_BAD_CHAR: "local part has a character not allowed in a dot-atom",
    FailureReason.QUOTED_NOT_ALLOWED: "quoted local part is not allowed (set allow_quoted=True)",
    FailureReason.QUOTED_UNTERMINATED: "quoted local part is not properly terminated",
    FailureReason.QUOTED_BAD_CHAR: "quoted local part has an illegal character",
    FailureReason.EMPTY_DOMAIN: "domain is empty",
    FailureReason.DOMAIN_TOO_LONG: "domain is longer than 255 characters",
    FailureReason.DOMAIN_NOT_DOTTED: "domain must have at least two labels",
    FailureReason.LABEL_EMPTY: "domain has a leading, trailing or double dot",
    FailureReason.LABEL_TOO_LONG: "domain label is longer than 63 characters",
    FailureReason.LABEL_BAD_CHAR: "domain label has an illegal character",
    FailureReason.LABEL_HYPHEN: "domain label has a leading or trailing hyphen",
    FailureReason.UNICODE_LABEL_INVALID: "domain label is not valid IDNA",
    FailureReason.IP_LITERAL_NOT_ALLOWED: (
        "domain literal is not allowed (set allow_ip_literal=True)"
    ),
    FailureReason.IP_LITERAL_INVALID: "domain literal is not a valid IPv4 or IPv6 address",
}


@dataclass(frozen=True)
class EmailAddress:
    """A parsed, syntactically valid address returned by the raising API.

    Attributes:
        local: the part before the ``@``, with its original case preserved.
        domain: the part after the ``@``.
        normalized: the canonical form (trimmed, domain lowercased or canonicalised).
        is_quoted_local: True when the local part is a quoted string.
        is_ip_literal: True when the domain is a bracketed IPv4 or IPv6 literal.
    """

    local: str
    domain: str
    normalized: str
    is_quoted_local: bool = False
    is_ip_literal: bool = False

    def __str__(self) -> str:
        return f"{self.local}@{self.domain}"


@dataclass(frozen=True)
class ValidationResult:
    """The outcome of :func:`emailsyntax.validate`, usable directly as a boolean.

    When ``valid`` is True the parsed fields are filled; otherwise ``code`` and ``reason``
    explain the first rejection and the parsed fields are ``None``.
    """

    address: str
    valid: bool
    code: str | None = None
    reason: str | None = None
    local: str | None = None
    domain: str | None = None
    normalized: str | None = None
    is_quoted_local: bool = False
    is_ip_literal: bool = False

    def __bool__(self) -> bool:
        return self.valid


class EmailSyntaxError(ValueError):
    """Raised by the raising API for a syntactically invalid address.

    Subclasses :class:`ValueError`, so code that catches ``ValueError`` still works.
    """

    def __init__(self, address: str, reason: FailureReason) -> None:
        self.address = address
        self.failure = reason
        self.code = reason.value
        self.reason = reason.message
        super().__init__(f"{reason.message}: {address!r}")
