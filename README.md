# emailsyntax

[![Lianes8 Certified](https://lianes8studio.com/certified/lianes8-certified-badge.svg)](https://lianes8studio.com/certified)

Validate email address syntax and normalize its domain without DNS, network access or
runtime dependencies. A valid result says nothing about mailbox existence or delivery.
Python 3.10 through 3.14 are supported.

## Install

```sh
pip install emailsyntax
```

## Quick start

```python
from emailsyntax import is_valid, normalize, split, validate, parse, EmailSyntaxError

assert is_valid("User@Example.com")
assert not is_valid("user@localhost")
assert normalize("  User.Name@Example.COM ") == "User.Name@example.com"
assert split("user@sub.example.com") == ("user", "sub.example.com")
assert validate("bad").code == "no_at"
assert parse("User@Example.COM").normalized == "User@example.com"
try:
    parse("bad")
except EmailSyntaxError as error:
    assert error.code == "no_at"
```

`validate` returns a frozen `ValidationResult`; its truth value is `valid`. Invalid results
have a stable `code` and a short `reason`. `parse` and `validate_or_raise` return a frozen
`EmailAddress` or raise `EmailSyntaxError`, a `ValueError`. Exception messages never include
input; the explicit `address` attribute still holds it.

## Optional syntax

Every validation function accepts these keyword-only boolean flags, all defaulting to False:

```python
assert is_valid('"john doe"@example.com', allow_quoted=True)
assert is_valid("user@[192.168.0.1]", allow_ip_literal=True)
assert is_valid("user@[IPv6:2001:db8::1]", allow_ip_literal=True)
assert is_valid("josé@example.com", allow_unicode=True)
assert is_valid("user@münchen.de", allow_unicode=True)
```

Defaults require an ASCII dot-atom local part and a domain with at least two labels.
Local parts are limited to 64 UTF-8 octets; domain labels to 63 ASCII/IDNA octets;
the address to 254 characters and 254 octets after encoding its domain with IDNA.
These are this library's practical limits, based on
[RFC 5321](https://www.rfc-editor.org/rfc/rfc5321.html#section-4.5.3.1).
Comments, display names, folding whitespace, trailing domain dots and dotless domains are
rejected. This is neither a complete RFC 5322 parser nor HTML email-input validation.

Unicode mode uses Python's IDNA 2003 codec, not IDNA 2008, and accepts only printable,
non-whitespace Unicode local characters. Normalization preserves Unicode spelling and local
case, lowercases domain names and compresses IP literals. It does not produce punycode output
or normalize the local part to NFC. See the guide for exact rules and limitations.

## Command line

```sh
emailsyntax user@example.com
emailsyntax --json user@example.com
emailsyntax --allow-ip-literal 'user@[192.168.0.1]'
printf 'a@b.co\nbad\n' | emailsyntax --stdin
python -m emailsyntax --version
```

Exit 0 means all inputs passed, 1 means invalid or missing input, and 2 means invalid command
arguments. `--strict` disables all opt-in flags. `--quiet` suppresses normal output;
`--json` takes precedence and includes the original addresses. Invalid human-readable output
omits the input. Stdin trims each line and skips empty lines; positional arguments are not
trimmed. Use `--` before a positional address beginning with a hyphen.

## Why use it?

Use emailsyntax when you need an offline gate, a stable rejection code and typed parsed
results with no runtime dependencies. Python's
[email package](https://docs.python.org/3/library/email.html) is intended for complete mail
messages and headers, including display names and comments.
[email-validator](https://pypi.org/project/email-validator/) offers normalization and optional
DNS deliverability checks (`check_deliverability=False` disables them), and depends on
`idna` and `dnspython`. Choose it when you need those broader internationalization and
mail-domain policies. emailsyntax deliberately has a narrower, explicit policy.

Read the [guide](https://github.com/JaviLianes8/emailsyntax/blob/main/GUIDE.md),
[changelog](https://github.com/JaviLianes8/emailsyntax/blob/main/CHANGELOG.md) and
[MIT license](https://github.com/JaviLianes8/emailsyntax/blob/main/LICENSE).
Report problems at [GitHub Issues](https://github.com/JaviLianes8/emailsyntax/issues).
