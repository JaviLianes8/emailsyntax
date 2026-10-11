# emailsyntax

Syntax-only email address validation and normalization, zero dependencies, no DNS or network

## Install

```
pip install emailsyntax
```

## Usage

```python
from emailsyntax import is_valid, validate, validate_or_raise, normalize, split

is_valid("User@Example.com")  # True
is_valid("user@localhost")  # False (dotless domain)
is_valid("us..er@example.com")  # False (consecutive dots)

normalize("  User.Name@Example.COM ")  # "User.Name@example.com"

split("user@sub.example.co.uk")  # ("user", "sub.example.co.uk")
```

### A reason on failure

`validate` returns a typed `ValidationResult` that is truthy when valid and tells you why
when it is not:

```python
result = validate("user@localhost")
result.valid  # False
result.code  # "domain_not_dotted"
result.reason  # "domain must have at least two labels"

ok = validate("a.b@sub.example.com")
ok.local, ok.domain, ok.normalized  # "a.b", "sub.example.com", "a.b@sub.example.com"
```

### Validate or raise

`validate_or_raise` (alias `parse`) returns a parsed `EmailAddress` or raises
`EmailSyntaxError`, which subclasses `ValueError` and carries `.code`, `.reason` and
`.address`:

```python
from emailsyntax import validate_or_raise, EmailSyntaxError

addr = validate_or_raise("User@Example.com")
addr.local, addr.domain, addr.normalized  # "User", "Example.com", "User@example.com"

try:
    validate_or_raise("nope")
except EmailSyntaxError as error:
    error.code  # "no_at"
```

### Opt-in shapes: quoted, IP literals, unicode

Defaults are strict ASCII. The richer RFC 5321/5322 shapes are opt-in keyword flags, so
turning them on never surprises existing callers:

```python
is_valid('"john doe"@example.com', allow_quoted=True)  # True
is_valid("user@[192.168.0.1]", allow_ip_literal=True)  # True
is_valid("user@[IPv6:2001:db8::1]", allow_ip_literal=True)  # True
is_valid("josé@example.com", allow_unicode=True)  # True (EAI local part)
is_valid("user@münchen.de", allow_unicode=True)  # True (IDN domain)
```

Every function accepts `allow_unicode`, `allow_quoted` and `allow_ip_literal`.

## Command line

A console script ships with the package:

```
emailsyntax user@example.com            # exit 0 and a line when valid
emailsyntax user@localhost              # exit 1 and the reason when invalid
emailsyntax --allow-ip-literal user@[192.168.0.1]
printf 'a@b.co\nbad\n' | emailsyntax --stdin   # one address per line
emailsyntax --json user@example.com     # machine-readable output
emailsyntax --version
```

Valid input exits 0, invalid input exits 1, and usage problems print to stderr. Run
`emailsyntax --help` for every flag with runnable examples.

## What it checks

This is a pure syntax check. It never looks up DNS or MX records, never contacts a mail
server and never touches the network. A valid result means the address is well formed, not
that a mailbox exists or can receive mail. With the default options it follows the practical
strict shape (no quoted strings, no domain literals, ASCII only), referencing RFC 5321/5322
behaviour rather than implementing the full obsolete grammar. The rules enforced:

- Exactly one `@` separating a non-empty local part and domain (the last `@` outside a
  quoted string is the separator).
- Local part up to 64 characters, made of dot-separated atoms using
  `A-Z a-z 0-9 ! # $ % & ' * + / = ? ^ _ `` { | } ~ -`. No leading, trailing or consecutive dots.
- Domain up to 255 characters with at least two labels: a dotless domain such as `localhost`
  is rejected. Each label is 1 to 63 characters of letters, digits and hyphens, with no leading
  or trailing hyphen and no empty label.
- Whole address up to 254 characters.
- ASCII only by default. With `allow_unicode`, internationalized domains (IDN U-labels) and
  unicode local parts (RFC 6531 EAI) are accepted; without it, an internationalized domain
  must be IDNA encoded to punycode (for example `xn--mnchen-3ya.de`).

`normalize` lowercases the domain and trims surrounding whitespace, keeping the local-part case
(local parts are case sensitive per the spec, even though most providers ignore it). It also
canonicalises IP-literal domains.

## Why

Most email helpers do more than check syntax. `email-validator` pulls in `dnspython` and checks
deliverability, and `pyisemail` aims at the full RFC grammar. When all you want is a fast,
offline "does this look like an address" gate plus a canonical form, those are heavy. This is the
small, typed, zero-dependency primitive for that: no network, no surprises, one job.

See [GUIDE.md](GUIDE.md) for task-oriented recipes.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
