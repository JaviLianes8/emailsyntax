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


def as_string(address: str) -> str:
    if not issubclass(type(address), str):
        raise TypeError("address must be a string")
    # Bypass subclass overrides, including __str__, before inspecting any input.
    return str.__str__(address)


def evaluate(
    address: str,
    *,
    allow_unicode: bool,
    allow_quoted: bool,
    allow_ip_literal: bool,
) -> tuple[FailureReason | None, _Parsed | None]:
    """Run the full syntax check. Returns (reason, None) on failure or (None, parsed)."""
    if any(type(flag) is not bool for flag in (allow_unicode, allow_quoted, allow_ip_literal)):
        raise TypeError("allow options must be bool")
    if not address:
        return FailureReason.EMPTY, None
    if len(address) > MAX_ADDRESS_LENGTH:
        return FailureReason.ADDRESS_TOO_LONG, None
    if not allow_unicode and not address.isascii():
        return FailureReason.NOT_ASCII, None

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

    wire_domain = domain if literal else domain.encode("idna").decode("ascii")
    if len(local.encode("utf-8")) + 1 + len(wire_domain) > MAX_ADDRESS_LENGTH:
        return FailureReason.ADDRESS_TOO_LONG, None

    normalized = f"{local}@{normalized_domain}"
    if len(normalized) > MAX_ADDRESS_LENGTH:
        return FailureReason.ADDRESS_TOO_LONG, None
    normalized_wire_domain = (
        normalized_domain if literal else normalized_domain.encode("idna").decode("ascii")
    )
    if len(local.encode("utf-8")) + 1 + len(normalized_wire_domain) > MAX_ADDRESS_LENGTH:
        return FailureReason.ADDRESS_TOO_LONG, None

    is_quoted = local.startswith('"')
    parsed = _Parsed(
        local=local,
        domain=domain,
        normalized=normalized,
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
    address = as_string(address)
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
    address = as_string(address)
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
