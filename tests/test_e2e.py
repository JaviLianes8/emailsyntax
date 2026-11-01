"""Real end-to-end test: install the built wheel into a fresh virtual environment and
drive the actual ``emailsyntax`` console script through subprocess. No mocks, no stubs."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import venv
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _script_path(env_dir: Path) -> Path:
    if sys.platform == "win32":
        return env_dir / "Scripts" / "emailsyntax.exe"
    return env_dir / "bin" / "emailsyntax"


def _python_path(env_dir: Path) -> Path:
    if sys.platform == "win32":
        return env_dir / "Scripts" / "python.exe"
    return env_dir / "bin" / "python"


@pytest.fixture(scope="module")
def console_script(tmp_path_factory: pytest.TempPathFactory) -> Path:
    env_dir = tmp_path_factory.mktemp("venv")
    venv.create(env_dir, with_pip=True)
    wheel_dir = tmp_path_factory.mktemp("wheel")
    supplied = os.environ.get("EMAILSYNTAX_WHEEL")
    if supplied:
        wheel = Path(supplied)
    else:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "build",
                "--wheel",
                "--outdir",
                str(wheel_dir),
                str(PROJECT_ROOT),
            ],
            check=True,
            timeout=120,
            capture_output=True,
        )
        wheel = next(wheel_dir.glob("*.whl"))
    subprocess.run(
        [str(_python_path(env_dir)), "-m", "pip", "install", str(wheel), "--quiet"],
        check=True,
        timeout=120,
    )
    consumer = subprocess.run(
        [
            str(_python_path(env_dir)),
            "-I",
            "-c",
            "import emailsyntax; from pathlib import Path; "
            "assert 'site-packages' in str(Path(emailsyntax.__file__)); "
            "assert emailsyntax.normalize(' User@Example.COM ') == 'User@example.com'",
        ],
        cwd=env_dir,
        check=True,
        capture_output=True,
        timeout=60,
    )
    assert consumer.returncode == 0
    script = _script_path(env_dir)
    assert script.is_file(), f"console script was not installed at {script}"
    return script


def _run(script: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(script), *args],
        input=stdin,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_console_script_reports_version(console_script: Path) -> None:
    result = _run(console_script, "--version")
    assert result.returncode == 0
    assert result.stdout.strip() == "emailsyntax 1.0.0"


def test_console_script_accepts_a_valid_address(console_script: Path) -> None:
    result = _run(console_script, "user@example.com")
    assert result.returncode == 0
    assert "valid -> user@example.com" in result.stdout


def test_console_script_rejects_an_invalid_address(console_script: Path) -> None:
    result = _run(console_script, "user@localhost")
    assert result.returncode == 1
    assert "invalid (domain_not_dotted)" in result.stdout


def test_console_script_batch_from_stdin(console_script: Path) -> None:
    result = _run(console_script, "--stdin", stdin="a@b.co\nbad\n")
    assert result.returncode == 1
    assert "a@b.co: valid" in result.stdout
    assert "invalid (no_at)" in result.stdout


def test_console_script_json_output(console_script: Path) -> None:
    result = _run(console_script, "--json", "user@example.com")
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["valid"] is True
    assert payload["normalized"] == "user@example.com"


def test_console_script_allow_ip_literal(console_script: Path) -> None:
    rejected = _run(console_script, "user@[192.168.0.1]")
    assert rejected.returncode == 1
    accepted = _run(console_script, "--allow-ip-literal", "user@[192.168.0.1]")
    assert accepted.returncode == 0
    assert "valid -> user@[192.168.0.1]" in accepted.stdout


def test_console_script_errors_to_stderr_on_no_input(console_script: Path) -> None:
    result = _run(console_script)
    assert result.returncode == 1
    assert "no address given" in result.stderr
    assert result.stdout == ""
