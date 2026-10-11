"""Syntax rules for the local part and the domain name: character sets and length limits.

All parsing here is linear (character scans and a single bounded character class per label),
so there is no risk of catastrophic regex backtracking.
"""

from __future__ import annotations

from ._result import FailureReason

MAX_ADDRESS_LENGTH = 254
MAX_LOCAL_LENGTH = 64
MAX_DOMAIN_LENGTH = 255
MAX_LABEL_LENGTH = 63

# RFC 5321 atext: letters, digits and this punctuation set.
_ATEXT = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!#$%&'*+/=?^_`{|}~-"
)
_LABEL_CHARS = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-")


def check_local(local: str, *, allow_quoted: bool, allow_unicode: bool) -> FailureReason | None:
    """Validate the local part. Returns the first failure reason, or None when valid."""
    if not local:
        return FailureReason.EMPTY_LOCAL
    if len(local) > MAX_LOCAL_LENGTH:
        return FailureReason.LOCAL_TOO_LONG
    if local.startswith('"'):
        if not allow_quoted:
            return FailureReason.QUOTED_NOT_ALLOWED
        return _check_quoted(local, allow_unicode=allow_unicode)
    return _check_dot_atom(local, allow_unicode=allow_unicode)


def _check_dot_atom(local: str, *, allow_unicode: bool) -> FailureReason | None:
    for atom in local.split("."):
        if not atom:
            return FailureReason.LOCAL_BAD_DOT
        for char in atom:
            if not _atom_char_ok(char, allow_unicode=allow_unicode):
                return FailureReason.LOCAL_BAD_CHAR
    return None


def _atom_char_ok(char: str, *, allow_unicode: bool) -> bool:
    if char in _ATEXT:
        return True
    if allow_unicode and not char.isascii():
        return char.isprintable() and not char.isspace()
    return False


def _check_quoted(local: str, *, allow_unicode: bool) -> FailureReason | None:
    if len(local) < 2 or not local.endswith('"'):
        return FailureReason.QUOTED_UNTERMINATED
    inner = local[1:-1]
    index = 0
    while index < len(inner):
        char = inner[index]
        if char == "\\":
            if index + 1 >= len(inner):
                return FailureReason.QUOTED_UNTERMINATED
            index += 2
            continue
        if char == '"':
            return FailureReason.QUOTED_UNTERMINATED
        if not _qtext_char_ok(char, allow_unicode=allow_unicode):
            return FailureReason.QUOTED_BAD_CHAR
        index += 1
    return None


def _qtext_char_ok(char: str, *, allow_unicode: bool) -> bool:
    if " " <= char <= "~":
        return True
    if allow_unicode and not char.isascii():
        return char.isprintable() and not char.isspace()
    return False


def check_domain_name(domain: str, *, allow_unicode: bool) -> FailureReason | None:
    """Validate a dotted domain name (not an IP literal). Returns a reason or None."""
    if not domain:
        return FailureReason.EMPTY_DOMAIN
    if len(domain) > MAX_DOMAIN_LENGTH:
        return FailureReason.DOMAIN_TOO_LONG
    labels = domain.split(".")
    if len(labels) < 2:
        return FailureReason.DOMAIN_NOT_DOTTED
    for label in labels:
        reason = _check_label(label, allow_unicode=allow_unicode)
        if reason is not None:
            return reason
    return None


def _check_label(label: str, *, allow_unicode: bool) -> FailureReason | None:
    if not label:
        return FailureReason.LABEL_EMPTY
    if allow_unicode and not label.isascii():
        return _check_unicode_label(label)
    if len(label) > MAX_LABEL_LENGTH:
        return FailureReason.LABEL_TOO_LONG
    if label.startswith("-") or label.endswith("-"):
        return FailureReason.LABEL_HYPHEN
    if any(char not in _LABEL_CHARS for char in label):
        return FailureReason.LABEL_BAD_CHAR
    return None


def _check_unicode_label(label: str) -> FailureReason | None:
    if label.startswith("-") or label.endswith("-"):
        return FailureReason.LABEL_HYPHEN
    try:
        encoded = label.encode("idna")
    except UnicodeError:
        return FailureReason.UNICODE_LABEL_INVALID
    if len(encoded) > MAX_LABEL_LENGTH:
        return FailureReason.LABEL_TOO_LONG
    return None
