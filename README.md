# emailsyntax

Syntax-only email address validation and normalization, zero dependencies, no DNS or network

## Install

```
pip install emailsyntax
```

## Usage

```python
from emailsyntax import is_valid, normalize, split

is_valid("User@Example.com")        # True
is_valid("user@localhost")          # False (dotless domain)
is_valid("us..er@example.com")      # False (consecutive dots)

normalize("  User.Name@Example.COM ")  # "User.Name@example.com"

split("user@sub.example.co.uk")     # ("user", "sub.example.co.uk")
```

`normalize` and `split` raise `ValueError` on input that is not syntactically valid.
`is_valid` returns a plain boolean.

## What it checks

This is a pure syntax check. It never looks up DNS and never touches the network. It follows
the practical WHATWG/HTML5 rules rather than the full RFC 5322 grammar (no quoted strings, no
comments, no folding whitespace). The rules enforced:

- Exactly one unquoted `@`, with a non-empty local part and domain on each side.
- Local part up to 64 characters, made of dot-separated atoms using
  `A-Z a-z 0-9 ! # $ % & ' * + / = ? ^ _ `` { | } ~ -`. No leading, trailing or consecutive dots.
- Domain up to 255 characters with at least two labels: a dotless domain such as `localhost`
  is rejected. Each label is 1 to 63 characters of letters, digits and hyphens, with no leading
  or trailing hyphen and no empty label (so no leading, trailing or consecutive dots).
- Whole address up to 254 characters.
- ASCII only. An internationalized domain must be IDNA encoded to punycode (for example
  `xn--mnchen-3ya.de`) before it is passed in. This keeps the primitive dependency free and
  leaves the Unicode policy to the caller.

`normalize` lowercases the domain and trims surrounding whitespace, keeping the local-part case
(local parts are case sensitive per the spec, even though most providers ignore it).

## Why

Most email helpers do more than check syntax. `email-validator` pulls in `dnspython` and checks
deliverability, and `pyisemail` aims at the full RFC grammar. When all you want is a fast,
offline "does this look like an address" gate plus a canonical form, those are heavy. This is the
small, typed, zero-dependency primitive for that: no network, no surprises, one job.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
