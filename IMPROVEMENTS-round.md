# emailsyntax improvement round

Ranked, substantial improvements for this release. The library stays a fast, typed,
zero-dependency, syntax-only email checker. It never looks up DNS and never touches the
network, and nothing below changes that promise. Every item is additive: the existing
`is_valid`, `normalize` and `split` keep their behaviour and defaults.

## Design principle

One validation engine, one set of options, consistent defaults across every entry point.
The defaults reproduce the current strict behaviour (ASCII only, dotted domain required,
no quoted local parts, no domain literals) so existing callers see no change. The richer
RFC 5321/5322 shapes are opt-in through keyword flags.

## Ranked improvements

1. Detailed, structured validation result. New `validate(address, ...) -> ValidationResult`
   returns a frozen, typed result carrying `valid`, a machine `code`, a human `reason`,
   and the parsed `local`, `domain` and `normalized` form. `ValidationResult.__bool__`
   makes it drop-in for a truthy check. This is the headline feature: callers learn *why*
   an address failed, not just that it did.

2. Stable failure reason codes. A typed `FailureReason` enum enumerates every rejection
   (empty, no `@`, local too long, bad dot-atom, unterminated quoted string, label too
   long, hyphen rules, bad domain literal, non-ASCII without unicode mode, and so on).
   Codes are stable strings for logging and tests; messages are human readable.

3. Validate-or-raise API with a typed exception. New `validate_or_raise(address, ...)`
   and its alias `parse(address, ...)` return a frozen `EmailAddress` or raise
   `EmailSyntaxError`. The exception subclasses `ValueError`, so existing
   `except ValueError` around `normalize`/`split` keeps working, and it exposes `.code`,
   `.reason` and `.address`.

4. Quoted local parts (RFC 5321/5322 dot-atom vs quoted-string). Opt-in `allow_quoted`
   accepts `"john doe"@example.com` and quoted pairs such as `"a\"b"@example.com`,
   parsed character by character (no regex, so no backtracking risk). Off by default to
   preserve current behaviour.

5. Domain literals: IPv4 and IPv6 address literals. Opt-in `allow_ip_literal` accepts
   `user@[192.168.0.1]` and `user@[IPv6:2001:db8::1]`, validated with the standard
   library `ipaddress` module (robust, linear, no catastrophic backtracking). Parsed
   results flag `is_ip_literal`, and normalization canonicalises the literal.

6. Internationalized addresses (IDN / EAI) with an ASCII-only strict mode. Opt-in
   `allow_unicode` accepts Unicode local parts (RFC 6531 EAI) and Unicode domain labels
   (IDN U-labels), validating each U-label by its IDNA A-label encoding and length. The
   default stays ASCII-only strict, so `allow_unicode=False` is the honest, predictable
   gate it is today.

7. Normalization upgrades. `normalize` keeps its signature and behaviour (trim, lowercase
   the domain, preserve local-part case) and now also canonicalises IP-literal domains and
   handles the opt-in shapes consistently. `ValidationResult.normalized` exposes the same.

8. A real command-line interface. New `emailsyntax` console script (argparse,
   `[project.scripts]`): validate one address with a meaningful exit code and reason,
   batch-validate from stdin, `--strict` / `--allow-unicode` / `--allow-quoted` /
   `--allow-ip-literal`, `--json`, `--quiet`, `--version`, and a `--help` with runnable
   examples. Errors go to stderr with exit code 1; invalid addresses exit non-zero.

9. Honest scope, stated loudly. Docstrings, README, the new GUIDE and the CLI help all
   repeat that this is syntax only: it does not check DNS, MX records, mailbox existence or
   deliverability. No overclaiming. RFC 5321/5322 behaviour is referenced, not claimed in
   full (no comments, no folding whitespace, no obsolete grammar).

10. Typed throughout and documented. `py.typed` already ships; every new symbol is fully
    annotated and passes `mypy --strict`. Great docstrings on every public name, a new
    `GUIDE.md` with task-oriented recipes, and an expanded README.

11. Hardened tests. A contract test asserting the complete promise over a strong table of
    valid and invalid addresses, including tricky RFC cases, plus a real end-to-end test
    that pip-installs the package editable and drives the real console script through
    `subprocess`, asserting real stdout and exit codes. No mocks.

## Explicitly out of scope

- DNS, MX, SMTP, mailbox or deliverability checks. This library is syntax only.
- Full RFC 5322 obsolete grammar (comments, folding whitespace, nested groups).
- Any network access or third-party dependency.
