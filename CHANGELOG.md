# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0]

- Structured validation: `validate` returns a typed `ValidationResult` with a stable failure
  `code`, a human `reason`, and the parsed `local`, `domain` and `normalized` form.
- Raising API: `validate_or_raise` (alias `parse`) returns a parsed `EmailAddress` or raises
  `EmailSyntaxError`, which subclasses `ValueError` and exposes `code`, `reason` and `address`.
- `FailureReason` enum covering every rejection, with stable codes and messages.
- Opt-in `allow_quoted` for quoted local parts (RFC 5321/5322 quoted-string).
- Opt-in `allow_ip_literal` for IPv4 and IPv6 domain literals, validated with the standard
  library and canonicalised on normalization.
- Opt-in `allow_unicode` for internationalized addresses (IDN domains and RFC 6531 EAI local
  parts), with the default staying ASCII-only strict.
- `is_valid`, `normalize` and `split` gain the same keyword flags; defaults are unchanged.
- New `emailsyntax` command-line interface (validate, batch from stdin, JSON, exit codes).
- Still syntax only: no DNS, no MX, no network, no dependencies.

## [0.1.0]

- First release.
- `is_valid`, `normalize` and `split` for syntax-only email addresses.
- Pure syntax, no DNS and no network: practical WHATWG/HTML5 rules, ASCII input,
  length limits, dotless domain rejection and no leading, trailing or consecutive dots.
