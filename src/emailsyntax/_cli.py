"""Command-line interface for emailsyntax: validate one address or a batch from stdin.

Syntax only. This command never looks up DNS, MX records or a mailbox, and never touches the
network. A zero exit code means every address checked is well formed, not that it can receive
mail.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence

from . import __version__
from ._api import validate
from ._result import ValidationResult

_EXAMPLES = """\
examples:
  emailsyntax user@example.com            check one address (exit 0 if valid)
  emailsyntax --allow-unicode josé@example.com
  emailsyntax --allow-ip-literal user@[192.168.0.1]
  printf 'a@b.co\\nbad\\n' | emailsyntax --stdin   check one address per line
  emailsyntax --json user@example.com     machine-readable output
"""


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser used by :func:`main`."""
    parser = argparse.ArgumentParser(
        prog="emailsyntax",
        description="Validate email address syntax offline. No DNS, no network, syntax only.",
        epilog=_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("addresses", nargs="*", help="one or more addresses to validate")
    parser.add_argument("--stdin", action="store_true", help="read one address per line from stdin")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="strict ASCII dot-atom mode (the default); disables the allow-* options",
    )
    parser.add_argument("--allow-unicode", action="store_true", help="accept IDN/EAI unicode")
    parser.add_argument("--allow-quoted", action="store_true", help="accept quoted local parts")
    parser.add_argument(
        "--allow-ip-literal", action="store_true", help="accept [IPv4] and [IPv6:...] domains"
    )
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    parser.add_argument("--quiet", action="store_true", help="print nothing; use the exit code")
    parser.add_argument("--version", action="version", version=f"emailsyntax {__version__}")
    return parser


def _collect(args: argparse.Namespace) -> list[str]:
    addresses = list(args.addresses)
    if args.stdin:
        addresses.extend(line.strip() for line in sys.stdin if line.strip())
    return addresses


def _result_dict(result: ValidationResult) -> dict[str, object]:
    return {
        "address": result.address,
        "valid": result.valid,
        "code": result.code,
        "reason": result.reason,
        "normalized": result.normalized,
        "local": result.local,
        "domain": result.domain,
        "is_quoted_local": result.is_quoted_local,
        "is_ip_literal": result.is_ip_literal,
    }


def _print_human(result: ValidationResult) -> None:
    if result.valid:
        print(f"{result.address}: valid -> {result.normalized}")
    else:
        print(f"{result.address}: invalid ({result.code}) {result.reason}")


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the ``emailsyntax`` console script. Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    addresses = _collect(args)
    if not addresses:
        print("error: no address given; pass one or use --stdin", file=sys.stderr)
        return 1

    unicode_ok = args.allow_unicode and not args.strict
    quoted_ok = args.allow_quoted and not args.strict
    ip_ok = args.allow_ip_literal and not args.strict

    results = [
        validate(a, allow_unicode=unicode_ok, allow_quoted=quoted_ok, allow_ip_literal=ip_ok)
        for a in addresses
    ]

    if args.json:
        payload: object = (
            _result_dict(results[0]) if len(results) == 1 else [_result_dict(r) for r in results]
        )
        print(json.dumps(payload, ensure_ascii=False))
    elif not args.quiet:
        for result in results:
            _print_human(result)

    return 0 if all(result.valid for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
