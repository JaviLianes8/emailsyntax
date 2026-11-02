"""Command contracts, including fixed errors and all option combinations."""

from __future__ import annotations

import io
import json

import pytest

from emailsyntax._cli import main


def test_json_has_complete_result_fields(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--json", "User@Example.COM", "bad"]) == 1
    good, bad = json.loads(capsys.readouterr().out)
    assert good == dict(
        address="User@Example.COM",
        valid=True,
        code=None,
        reason=None,
        local="User",
        domain="Example.COM",
        normalized="User@example.com",
        is_quoted_local=False,
        is_ip_literal=False,
    )
    assert bad == dict(
        address="bad",
        valid=False,
        code="no_at",
        reason="address has no '@' separator",
        local=None,
        domain=None,
        normalized=None,
        is_quoted_local=False,
        is_ip_literal=False,
    )


@pytest.mark.parametrize(
    ("flag", "address"),
    [
        ("--allow-quoted", '"a b"@example.com'),
        ("--allow-unicode", "jos\u00e9@example.com"),
        ("--allow-ip-literal", "a@[1.2.3.4]"),
    ],
)
def test_flags_and_strict_override(
    flag: str, address: str, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["--quiet", flag, address]) == 0
    assert main(["--quiet", flag, "--strict", address]) == 1
    assert capsys.readouterr() == ("", "")


def test_stdin_trims_and_skips_empty_lines(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("\n a@b.co \n\t\n"))
    assert main(["--stdin", "--json", "--quiet"]) == 0
    assert json.loads(capsys.readouterr().out)["address"] == "a@b.co"


def test_cli_errors_do_not_echo_sensitive_input(capsys: pytest.CaptureFixture[str]) -> None:
    secret = "private-token" * 10000
    assert main([secret]) == 1
    output = capsys.readouterr()
    assert secret not in output.out and len(output.out) < 150
    with pytest.raises(SystemExit) as error:
        main(["--" + secret])
    assert error.value.code == 2
    output = capsys.readouterr()
    assert "private-token" not in output.err and len(output.err) < 1000


def test_closed_output_pipe_returns_one(monkeypatch: pytest.MonkeyPatch) -> None:
    class ClosedPipe(io.StringIO):
        def write(self, value: str) -> int:
            raise BrokenPipeError

    monkeypatch.setattr("sys.stdout", ClosedPipe())
    assert main(["a@b.co"]) == 1
