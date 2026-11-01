"""Hand-written transport contracts for the installed module and console script."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest
from test_e2e import console_script as console_script


@pytest.fixture(params=["module", "console"])
def command(request: pytest.FixtureRequest, console_script: Path) -> list[str]:
    if request.param == "module":
        python = console_script.with_name("python.exe" if os.name == "nt" else "python")
        return [str(python), "-m", "emailsyntax"]
    return [str(console_script)]


def run(
    command: list[str],
    *args: str,
    stdin: bytes | None = None,
    encoding: str = "utf-8:strict",
) -> subprocess.CompletedProcess[bytes]:
    env = dict(os.environ, PYTHONIOENCODING=encoding)
    env.pop("PYTHONPATH", None)
    return subprocess.run(
        [*command, *args],
        input=stdin,
        capture_output=True,
        env=env,
        timeout=30,
    )


@pytest.mark.parametrize("mode", [[], ["--json"], ["--quiet"]])
def test_malformed_stdin_has_fixed_input_free_error(command: list[str], mode: list[str]) -> None:
    result = run(command, "--stdin", *mode, stdin=b"private-token@b.co\xff\n")
    assert result.returncode == 1
    assert result.stdout == b""
    assert result.stderr.replace(b"\r\n", b"\n") == (
        b"error: stdin cannot be decoded with its configured encoding\n"
    )


@pytest.mark.parametrize("encoding", ["cp1252:strict", "ascii:strict", "utf-8:strict"])
def test_unicode_human_output_preserves_success(command: list[str], encoding: str) -> None:
    address = "\u7528\u6237@example.com"
    result = run(command, "--allow-unicode", address, encoding=encoding)
    assert result.returncode == 0
    assert result.stderr == b""
    expected = f"{address}: valid -> {address}\n".encode(encoding.split(":")[0], "backslashreplace")
    assert result.stdout.replace(b"\r\n", b"\n") == expected


@pytest.mark.parametrize("address", [" a@b.co", "a@b.co ", "\ta@b.co\t", "\u2003a@b.co\u2003"])
def test_positional_whitespace_is_rejected_and_preserved(command: list[str], address: str) -> None:
    result = run(command, "--json", address)
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["address"] == address
    assert payload["valid"] is False


@pytest.mark.parametrize("space", ["\t", "\u2003", "\u00a0"])
def test_stdin_trims_nonempty_lines_with_unicode_whitespace(command: list[str], space: str) -> None:
    result = run(command, "--stdin", "--json", stdin=f"{space}a@b.co{space}\n".encode())
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["address"] == "a@b.co"
    assert payload["valid"] is True


def test_json_uses_ascii_unicode_escapes(command: list[str]) -> None:
    result = run(command, "--json", "--allow-unicode", "jos\u00e9@example.com")
    assert result.returncode == 0
    assert result.stdout.isascii()
    assert b"jos\\u00e9@example.com" in result.stdout
    assert json.loads(result.stdout)["address"] == "jos\u00e9@example.com"


def test_json_preserves_quoted_metadata(command: list[str]) -> None:
    result = run(command, "--json", "--allow-quoted", '"a b"@Example.COM')
    assert result.returncode == 0
    assert json.loads(result.stdout) == {
        "address": '"a b"@Example.COM',
        "valid": True,
        "code": None,
        "reason": None,
        "local": '"a b"',
        "domain": "Example.COM",
        "normalized": '"a b"@example.com',
        "is_quoted_local": True,
        "is_ip_literal": False,
    }
