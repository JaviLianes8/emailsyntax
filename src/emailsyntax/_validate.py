"""The validation engine shared by the boolean, result and raising APIs."""

from __future__ import annotations

from dataclasses import dataclass

from ._ip import is_ip_literal, parse_ip_literal
from ._result import EmailSyntaxError, FailureReason, ValidationResult
from ._rules import MAX_ADDRESS_LENGTH, check_domain_name, check_local


@dataclass(frozen=True)
class _Parsed:
    local: str
    domain: str
    normalized: str
    is_quoted_local: bool
    is_ip_literal: bool


def evaluate(
    address: str,
    *,
    allow_unicode: bool,
    allow_quoted: bool,
    allow_ip_literal: bool,
) -> tuple[FailureReason | None, _Parsed | None]:
    """Run the full syntax check. Returns (reason, None) on failure or (None, parsed)."""
    if not address:
        return FailureReason.EMPTY, None
    if not allow_unicode and not address.isascii():
        return FailureReason.NOT_ASCII, None
    if len(address) > MAX_ADDRESS_LENGTH:
        return FailureReason.ADDRESS_TOO_LONG, None

    local, separator, domain = address.rpartition("@")
    if not separator:
        return FailureReason.NO_AT, None

    local_reason = check_local(local, allow_quoted=allow_quoted, allow_unicode=allow_unicode)
    if local_reason is not None:
        return local_reason, None

    domain_reason, normalized_domain, literal = _check_domain(
        domain, allow_unicode=allow_unicode, allow_ip_literal=allow_ip_literal
    )
    if domain_reason is not None:
        return domain_reason, None

    is_quoted = local.startswith('"')
    parsed = _Parsed(
        local=local,
        domain=domain,
        normalized=f"{local}@{normalized_domain}",
        is_quoted_local=is_quoted,
        is_ip_literal=literal,
    )
    return None, parsed


def _check_domain(
    domain: str, *, allow_unicode: bool, allow_ip_literal: bool
) -> tuple[FailureReason | None, str, bool]:
    if not domain:
        return FailureReason.EMPTY_DOMAIN, "", False
    if is_ip_literal(domain):
        if not allow_ip_literal:
            return FailureReason.IP_LITERAL_NOT_ALLOWED, "", False
        canonical = parse_ip_literal(domain)
        if canonical is None:
            return FailureReason.IP_LITERAL_INVALID, "", False
        return None, canonical, True
    reason = check_domain_name(domain, allow_unicode=allow_unicode)
    if reason is not None:
        return reason, "", False
    return None, domain.lower(), False


def to_result(
    address: str,
    *,
    allow_unicode: bool,
    allow_quoted: bool,
    allow_ip_literal: bool,
) -> ValidationResult:
    """Turn a raw address into a :class:`ValidationResult`."""
    reason, parsed = evaluate(
        address,
        allow_unicode=allow_unicode,
        allow_quoted=allow_quoted,
        allow_ip_literal=allow_ip_literal,
    )
    if parsed is None:
        assert reason is not None
        return ValidationResult(
            address=address, valid=False, code=reason.value, reason=reason.message
        )
    return ValidationResult(
        address=address,
        valid=True,
        local=parsed.local,
        domain=parsed.domain,
        normalized=parsed.normalized,
        is_quoted_local=parsed.is_quoted_local,
        is_ip_literal=parsed.is_ip_literal,
    )


def require_valid(
    address: str,
    *,
    allow_unicode: bool,
    allow_quoted: bool,
    allow_ip_literal: bool,
) -> _Parsed:
    """Return the parsed address or raise :class:`EmailSyntaxError`."""
    reason, parsed = evaluate(
        address,
        allow_unicode=allow_unicode,
        allow_quoted=allow_quoted,
        allow_ip_literal=allow_ip_literal,
    )
    if parsed is None:
        assert reason is not None
        raise EmailSyntaxError(address, reason)
    return parsed
