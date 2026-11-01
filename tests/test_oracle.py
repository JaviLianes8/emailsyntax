"""Derived grammar cases and independent standard-library reference checks."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import random
import re
from email.headerregistry import Address
from pathlib import Path

import pytest

from emailsyntax import is_valid, normalize, validate


def test_fetched_sources_match_recorded_hashes() -> None:
    location = os.environ.get("EMAILSYNTAX_SOURCES")
    if not location:
        pytest.skip("set EMAILSYNTAX_SOURCES to the fetched source directory")
    manifest = Path(__file__).resolve().parents[1] / "sources" / "MANIFEST.json"
    for item in json.loads(manifest.read_text(encoding="utf-8")):
        data = (Path(location) / item["name"]).read_bytes()
        assert len(data) == item["size"]
        assert hashlib.sha256(data).hexdigest() == item["sha256"]


def test_short_rfc_example() -> None:
    # RFC 5322 Appendix A.1.1, fetched 2026-11-01:
    # https://www.rfc-editor.org/rfc/rfc5322.txt
    address = "jdoe@machine.example"
    assert is_valid(address)
    assert Address(addr_spec=address).addr_spec == address


def test_quoted_pairs_follow_fetched_rfc5321_grammar() -> None:
    # Derived from section 4.1.2, not copied test vectors.
    # https://www.rfc-editor.org/rfc/rfc5321.txt (2026-11-01)
    for code in range(256):
        address = '"a\\' + chr(code) + 'b"@example.com'
        assert is_valid(address, allow_quoted=True, allow_unicode=True) == (32 <= code <= 126)


def test_seeded_ascii_grammar_and_reference_parser() -> None:
    # Independent regex transcription of the documented subset of RFC 5321.
    atom = r"[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+"
    label = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    grammar = re.compile(rf"{atom}(?:\.{atom})*@{label}(?:\.{label})+")
    rng = random.Random(20261101)
    alphabet = 'abcABC019.-_+!@ ()\\"\t\r\n'
    for _ in range(10000):
        local = "".join(rng.choices(alphabet, k=rng.randrange(1, 70)))
        domain = "".join(rng.choices("abc019-_.", k=rng.randrange(1, 80)))
        address = f"{local}@{domain}"
        expected = (
            len(local) <= 64 and len(address) <= 254 and grammar.fullmatch(address) is not None
        )
        assert is_valid(address) == expected
        if expected:
            reference = Address(addr_spec=address)
            assert reference.username == local and reference.domain == domain
    for _ in range(1000):
        local = "".join(rng.choices("abcABC019+!_", k=rng.randrange(1, 65)))
        address = local + "@Example.COM"
        assert is_valid(address)
        assert Address(addr_spec=address).username == local


def test_seeded_ipaddress_reference() -> None:
    rng = random.Random(6531)
    for bits, kind in ((32, ipaddress.IPv4Address), (128, ipaddress.IPv6Address)):
        for _ in range(500):
            ip = kind(rng.getrandbits(bits))
            prefix = "IPv6:" if bits == 128 else ""
            address = f"u@[{prefix}{ip.exploded.upper()}]"
            assert normalize(address, allow_ip_literal=True) == f"u@[{prefix}{ip.compressed}]"


def test_seeded_unicode_robustness() -> None:
    rng = random.Random(5322)
    alphabet = 'aA1.@-\\"\x00\n\t \u00e9\u3002\u200b\ud800\U0001f600'
    for _ in range(5000):
        address = "".join(rng.choices(alphabet, k=rng.randrange(280)))
        flags = dict(allow_unicode=True, allow_quoted=True, allow_ip_literal=True)
        result = validate(address, **flags)
        assert isinstance(result.valid, bool)
        if result:
            assert result.normalized is not None
            assert normalize(result.normalized, **flags) == result.normalized
    for count in (1000, 10000, 1000000):
        for character in ("@", "\u00e9", "\\", "\ud800"):
            assert validate(character * count, allow_unicode=True).code == "address_too_long"
