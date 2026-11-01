# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-01

- Stabilize the ten public names, signatures, keyword defaults, result fields and failure
  codes from 0.2.0. Ship runnable examples, typed contracts and Python 3.10 through 3.14 support.
- Remove the accidental `annotations` module attribute; `__all__` remains unchanged.
- Reject non-string addresses and non-bool allow options with fixed `TypeError` messages.
  Previously some wrong types crashed with `AttributeError` or used truthiness.
- Read string subclasses as built-in strings without invoking overridden methods. This
  prevents forged validation and arbitrary exceptions; result and error address fields
  contain the underlying string value.
- Reject non-string addresses without reading overridable `__class__` properties, so
  hostile or spoofed types receive the fixed `TypeError` across all six address APIs.
- Exception messages contain only the reason, never the address. The explicit `address`
  attribute remains available. `EmailSyntaxError` now supports copying and pickling.
- Quoted backslash escapes require ASCII code points 32 through 126, including Unicode mode;
  escaped controls, surrogates and non-ASCII characters previously passed unchecked.
- Reject IPv6 zone identifiers. Accept the `IPv6:` literal tag case-insensitively and
  normalize it to `IPv6:`; 0.2.0 required that exact case.
- Validate encoded Unicode domain labels as single ASCII labels, rejecting separators,
  illegal characters and edge hyphens introduced by IDNA mapping.
- Measure the local limit as 64 UTF-8 octets and the whole-address limit as 254 octets after
  IDNA domain encoding, in addition to the existing 254-character input limit. Long Unicode
  addresses that 0.2.0 accepted can now fail. Length error messages describe octets.
- Check the whole-input character bound before the ASCII check, so oversized non-ASCII
  input now reports `address_too_long` rather than `not_ascii`.
- Enforce character and encoded limits on normalized output too. Unicode lowercase
  expansion beyond the limits now reports `address_too_long`, preserving idempotence.
- Add `python -m emailsyntax`. Invalid human-readable CLI results omit the original input;
  JSON still explicitly includes it and now uses ASCII escapes. Argument errors use a fixed
  message without echoing arguments. Closed output pipes exit 1 quietly.
- Malformed stdin bytes exit 1 with a fixed input-free diagnostic and no partial results.
  Human-readable CLI output escapes characters unsupported by stdout's encoding while
  preserving exit 0 for valid Unicode addresses.
- Correct the guide's IPv4-mapped IPv6 description: formatting follows `ipaddress`, with
  dotted IPv4 tails on Python 3.14.6 and potentially hexadecimal tails on other versions.
- Extend contracts for quoted-local metadata, equality of every result field, positional
  whitespace rejection, Unicode whitespace trimming on stdin and ASCII-only JSON output.
- Pin exact cp1252 output bytes for representable non-ASCII addresses through both
  installed CLI entry points, retaining empty stderr and successful exit status.
- Document the practical subset accurately: IDNA 2003, printable Unicode local characters,
  dotted domains, no full RFC 5322 or HTML email-input conformance. Normalization retains
  Unicode domain spelling and local case. Runtime dependencies remain empty.

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
