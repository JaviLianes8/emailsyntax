# emailsyntax guide

Task-oriented recipes for the library. Everything here is syntax only: no DNS lookup, no MX
record check, no mailbox probe and no network access. A valid result means the address is well
formed, not that it can receive mail.

## Pick the right entry point

| You want | Use | Returns |
| --- | --- | --- |
| A quick yes or no | `is_valid(address)` | `bool` |
| The reason it failed | `validate(address)` | `ValidationResult` (truthy) |
| A parsed address or an exception | `validate_or_raise(address)` / `parse(address)` | `EmailAddress` |
| Just the two halves | `split(address)` | `tuple[str, str]` |
| A canonical form | `normalize(address)` | `str` |

## Check a form field

```python
from emailsyntax import validate

result = validate(user_input)
if not result:
    show_error(result.reason)  # "domain must have at least two labels"
else:
    store(result.normalized)
```

`result.code` is a stable machine string (for example `"local_bad_dot"`) good for logging and
tests. `result.reason` is a human message. The full set lives in the `FailureReason` enum.

## Raise instead of branch

```python
from emailsyntax import validate_or_raise, EmailSyntaxError

try:
    address = validate_or_raise(user_input)
except EmailSyntaxError as error:
    # EmailSyntaxError is a ValueError, so existing handlers keep working.
    log.warning("rejected %s: %s", error.address, error.code)
else:
    use(address.local, address.domain)
```

## Normalize before storing

```python
from emailsyntax import normalize

normalize("  User.Name@Example.COM ")  # "User.Name@example.com"
```

The domain is lowercased and surrounding whitespace is trimmed; the local part keeps its case,
because local parts are case sensitive per the spec. IP-literal domains are canonicalised, for
example `[IPv6:2001:DB8::0:1]` becomes `[IPv6:2001:db8::1]`.

## Accept more than the strict default

The defaults are strict ASCII. Opt in per call:

```python
from emailsyntax import is_valid

is_valid('"john doe"@example.com', allow_quoted=True)  # quoted local part
is_valid("user@[192.168.0.1]", allow_ip_literal=True)  # IPv4 domain literal
is_valid("user@[IPv6:2001:db8::1]", allow_ip_literal=True)  # IPv6 domain literal
is_valid("josé@example.com", allow_unicode=True)  # EAI unicode local part
is_valid("user@münchen.de", allow_unicode=True)  # IDN unicode domain
```

Every public function accepts `allow_unicode`, `allow_quoted` and `allow_ip_literal`.

## From the command line

```
emailsyntax user@example.com            # exit 0 when valid
emailsyntax user@localhost              # exit 1 and the reason when invalid
emailsyntax --allow-unicode josé@example.com
printf 'a@b.co\nbad\n' | emailsyntax --stdin   # one address per line
emailsyntax --json user@example.com     # JSON report
```

The exit code is 0 only when every address checked is valid. Usage problems go to stderr.

## What this library does not do

- It does not check DNS, MX records, SMTP, a mailbox or deliverability.
- It does not implement the obsolete RFC 5322 grammar (comments, folding whitespace, groups).
- It does not access the network or pull in any dependency.

If you need deliverability, pair this syntax gate with a separate DNS or SMTP step.
