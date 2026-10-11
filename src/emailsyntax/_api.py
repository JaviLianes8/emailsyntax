"""Public API: boolean, structured-result and raising entry points, plus normalize/split.

Everything here is syntax only. It never looks up DNS, MX records or a mailbox, and it never
touches the network: a True result means the address is well formed, not that it can receive
mail. The defaults reproduce a strict ASCII, dotted-domain check (no quoted local parts, no
domain literals). The richer RFC 5321/5322 shapes are opt-in through the keyword flags.
"""

from __future__ import annotations

from ._result import EmailAddress, ValidationResult
from ._validate import require_valid, to_result


def is_valid(
    address: str,
    *,
    allow_unicode: bool = False,
    allow_quoted: bool = False,
    allow_ip_literal: bool = False,
) -> bool:
    """Return True if the string is a syntactically valid email address.

    This is a pure syntax check: it never looks up DNS and never touches the network. With the
    default options it applies a strict ASCII dot-atom rule with a dotted domain, matching the
    practical WHATWG/HTML5 shape. Set ``allow_unicode`` for internationalized (IDN/EAI)
    addresses, ``allow_quoted`` for quoted local parts and ``allow_ip_literal`` for bracketed
    IPv4 or IPv6 domain literals.
    """
    return to_result(
        address,
        allow_unicode=allow_unicode,
        allow_quoted=allow_quoted,
        allow_ip_literal=allow_ip_literal,
    ).valid


def validate(
    address: str,
    *,
    allow_unicode: bool = False,
    allow_quoted: bool = False,
    allow_ip_literal: bool = False,
) -> ValidationResult:
    """Validate an address and return a :class:`ValidationResult`.

    The result is truthy when the address is valid and carries the parsed ``local``,
    ``domain`` and ``normalized`` form. When it is invalid, ``code`` is a stable machine
    string and ``reason`` is a human message explaining the first problem found. This never
    checks DNS or deliverability: it reports syntax only.
    """
    return to_result(
        address,
        allow_unicode=allow_unicode,
        allow_quoted=allow_quoted,
        allow_ip_literal=allow_ip_literal,
    )


def validate_or_raise(
    address: str,
    *,
    allow_unicode: bool = False,
    allow_quoted: bool = False,
    allow_ip_literal: bool = False,
) -> EmailAddress:
    """Return a parsed :class:`EmailAddress`, or raise :class:`EmailSyntaxError`.

    The exception subclasses :class:`ValueError` and exposes ``code``, ``reason`` and
    ``address``. Like the rest of the library this is syntax only, with no DNS lookup.
    """
    parsed = require_valid(
        address,
        allow_unicode=allow_unicode,
        allow_quoted=allow_quoted,
        allow_ip_literal=allow_ip_literal,
    )
    return EmailAddress(
        local=parsed.local,
        domain=parsed.domain,
        normalized=parsed.normalized,
        is_quoted_local=parsed.is_quoted_local,
        is_ip_literal=parsed.is_ip_literal,
    )


def parse(
    address: str,
    *,
    allow_unicode: bool = False,
    allow_quoted: bool = False,
    allow_ip_literal: bool = False,
) -> EmailAddress:
    """Alias of :func:`validate_or_raise`: parse into an :class:`EmailAddress` or raise."""
    return validate_or_raise(
        address,
        allow_unicode=allow_unicode,
        allow_quoted=allow_quoted,
        allow_ip_literal=allow_ip_literal,
    )


def split(
    address: str,
    *,
    allow_unicode: bool = False,
    allow_quoted: bool = False,
    allow_ip_literal: bool = False,
) -> tuple[str, str]:
    """Return the (local, domain) pair, raising :class:`EmailSyntaxError` on invalid syntax."""
    parsed = require_valid(
        address,
        allow_unicode=allow_unicode,
        allow_quoted=allow_quoted,
        allow_ip_literal=allow_ip_literal,
    )
    return parsed.local, parsed.domain


def normalize(
    address: str,
    *,
    allow_unicode: bool = False,
    allow_quoted: bool = False,
    allow_ip_literal: bool = False,
) -> str:
    """Trim surrounding whitespace and canonicalise the domain, keeping the local part case.

    The domain is lowercased, and an IP-literal domain is rewritten to its canonical form.
    Raises :class:`EmailSyntaxError` if the trimmed string is not syntactically valid.
    """
    parsed = require_valid(
        address.strip(),
        allow_unicode=allow_unicode,
        allow_quoted=allow_quoted,
        allow_ip_literal=allow_ip_literal,
    )
    return parsed.normalized
