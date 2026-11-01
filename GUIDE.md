# emailsyntax guide

## Entry points

| Function | Result | Invalid syntax |
| --- | --- | --- |
| `is_valid` | `bool` | False |
| `validate` | `ValidationResult` | false result with `code` and `reason` |
| `parse`, `validate_or_raise` | `EmailAddress` | `EmailSyntaxError` |
| `split` | original `(local, domain)` | `EmailSyntaxError` |
| `normalize` | normalized string | `EmailSyntaxError` |

All six functions accept `address: str` and keyword-only `allow_unicode=False`,
`allow_quoted=False`, `allow_ip_literal=False`. Wrong address types or non-bool options raise
`TypeError`, even on empty input. Only `normalize` strips surrounding Unicode whitespace.
The other functions preserve and validate input exactly as supplied.
String subclasses are accepted using their underlying built-in string value; overridden
methods are not called. Returned address fields and syntax-error addresses use that value.

```python
from emailsyntax import validate, parse, normalize, FailureReason

result = validate("User@Example.COM")
assert result.valid and bool(result)
assert result.address == "User@Example.COM"
assert (result.local, result.domain) == ("User", "Example.COM")
assert result.normalized == "User@example.com"
assert result.code is None and result.reason is None
assert not result.is_quoted_local and not result.is_ip_literal
bad = validate("user@localhost")
assert bad.code == FailureReason.DOMAIN_NOT_DOTTED.value
assert bad.reason == FailureReason.DOMAIN_NOT_DOTTED.message
assert bad.local is None and bad.domain is None and bad.normalized is None
assert not bad.is_quoted_local and not bad.is_ip_literal
```

`EmailAddress` holds `local`, `domain`, `normalized`, `is_quoted_local=False` and
`is_ip_literal=False`. `str(parsed)` reproduces the unnormalized address. `ValidationResult`
holds `address`, `valid`, optional `code`, `reason`, `local`, `domain`, `normalized` (all default
None), and the same two flags. Both are frozen dataclasses with equality and hashing.
Direct constructors are value containers: they do not validate consistency. Use `parse` or
`validate` to obtain validated values. Copies and pickles preserve their fields.

## Syntax policy

The ASCII local part is dot-separated nonempty atoms of letters, digits and
`!#$%&'*+/=?^_` plus backtick, braces, vertical bar, tilde and hyphen. A local part is at
most 64 UTF-8 octets, including quote and escape syntax. Quoted mode accepts ASCII space and
printable characters; internal quotes and backslashes must be escaped. Backslash escapes
must always be ASCII code points 32 through 126, including in Unicode mode. Control
characters, CR, LF and tab are rejected.

Domains require at least two dot-separated labels, each 1 to 63 ASCII/IDNA octets. ASCII
labels contain letters, digits and hyphens, with no edge hyphen. No TLD list, DNS existence
check or punycode roundtrip is performed. An ASCII `xn--` label is checked as ordinary ASCII
syntax. Unicode labels use Python's IDNA 2003 codec; the encoded label must still be a single
valid ASCII label. Unicode dot separators are rejected. This is a practical compatibility
policy, not full IDNA 2008 or SMTPUTF8 conformance. Printable non-whitespace Unicode local
characters are allowed; surrogates, controls and Unicode whitespace are not.

The whole input is limited to 254 characters, then to 254 octets with the local part encoded
in UTF-8 and the domain encoded in IDNA (literal domains stay ASCII). The first limit bounds
work before Unicode conversion. IDNA expansion can make an otherwise short address too long.
Both limits also apply to the normalized form. Lowercase expansion that exceeds either
limit is rejected with `address_too_long` before a successful result is returned.
The historical `domain_too_long` enum member remains for compatibility but cannot be returned
through validation: the tighter whole-address limit rejects such input first.

With `allow_ip_literal=True`, bracketed four-octet IPv4 and IPv6 with a case-insensitive
`IPv6:` tag are accepted. IPv4 leading zeroes, IPv6 zone identifiers and arbitrary literal
tags are rejected. IPv6 output uses `IPv6:` followed by Python's `ipaddress` compressed
format, normally lowercase hexadecimal. IPv4-mapped IPv6 can use a dotted IPv4 tail
(including on Python 3.14.6) instead of hexadecimal. Normalization
follows the running interpreter's formatting and is not byte-for-byte stable across versions.

```python
parsed = parse('"A@B"@[ipv6:2001:DB8::1]', allow_quoted=True, allow_ip_literal=True)
assert parsed.is_quoted_local and parsed.is_ip_literal
assert parsed.normalized == '"A@B"@[IPv6:2001:db8::1]'
assert normalize(" User@MÜNCHEN.DE ", allow_unicode=True) == "User@münchen.de"
mapped = normalize("a@[IPv6:::ffff:192.0.2.1]", allow_ip_literal=True)
assert mapped == normalize("a@[IPv6:::ffff:c000:201]", allow_ip_literal=True)
assert mapped in ("a@[IPv6:::ffff:192.0.2.1]", "a@[IPv6:::ffff:c000:201]")
```

Normalization does not unquote local parts, fold their case, emit punycode or perform NFC.
It trims only in `normalize`, lowercases the domain or canonicalizes a literal. Original
`local` and `domain` fields remain unchanged. Results are idempotent under the same flags.

## Errors and precedence

`EmailSyntaxError` is a `ValueError` with `address`, `failure` (a `FailureReason`), `code`
and `reason`. Its message is the fixed reason, without input. Copies and pickles work.
The explicit `address` field, result representations and CLI JSON contain the input;
do not log those if addresses are sensitive. Error messages are stable explanations;
branch on `code` rather than parsing text.

Validation checks types, empty input, character length, ASCII policy, separator, local
syntax, domain syntax, then encoded address length, in that order. For a malformed address
with several problems, only the first failure is reported. The last `@` separates the parts;
an earlier `@` is valid only inside a properly quoted local part.
Normalized character and encoded address limits are checked after the original limits.

```python
from emailsyntax import EmailSyntaxError

try:
    parse("private-token")
except EmailSyntaxError as error:
    assert error.code == "no_at"
    assert str(error) == "address has no '@' separator"
    assert error.address == "private-token"
```

`FailureReason` contains: `empty`, `not_ascii`, `address_too_long`, `no_at`, `empty_local`,
`local_too_long`, `local_bad_dot`, `local_bad_char`, `quoted_not_allowed`,
`quoted_unterminated`, `quoted_bad_char`, `empty_domain`, `domain_too_long`,
`domain_not_dotted`, `label_empty`, `label_too_long`, `label_bad_char`, `label_hyphen`,
`unicode_label_invalid`, `ip_literal_not_allowed`, `ip_literal_invalid`.

## Command line and upgrading

`emailsyntax` and `python -m emailsyntax` provide the same interface. `--help` lists options.
`--json` returns one object for one address and an array for multiple addresses; fields match
`ValidationResult`. JSON uses ASCII escapes for portable Unicode output. Stdin consumes one
trimmed address per nonempty line; the batch is held in memory. A closed output pipe returns 1.
Malformed stdin bytes return 1 with a fixed, input-free diagnostic on stderr and no results.
Human-readable output escapes characters unsupported by stdout's encoding using backslash
escapes; valid Unicode input still exits 0. Positional arguments are never trimmed.
The CLI is intended for bounded batches, not an unbounded stream service.

From PyPI 0.2.0, public names, signatures, field defaults and failure codes remain available.
See the dated [1.0.0 changelog](https://github.com/JaviLianes8/emailsyntax/blob/main/CHANGELOG.md)
for stricter quoting, IDNA and octet limits, literal fixes, safe errors and CLI differences.
No network or runtime dependency is introduced.
