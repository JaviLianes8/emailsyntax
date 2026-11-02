"""Execute public docstrings and the Python examples in the documentation."""

from __future__ import annotations

import doctest
import importlib
import re
from pathlib import Path

import emailsyntax


def test_all_public_names_have_passing_examples() -> None:
    for name in emailsyntax.__all__:
        assert ">>>" in (getattr(emailsyntax, name).__doc__ or "")
    for name in ("emailsyntax._api", "emailsyntax._result"):
        result = doctest.testmod(importlib.import_module(name), raise_on_error=True)
        assert result.attempted > 0


def test_readme_and_guide_examples() -> None:
    root = Path(__file__).resolve().parents[1]
    for name in ("README.md", "GUIDE.md"):
        namespace: dict[str, object] = {}
        text = (root / name).read_text(encoding="utf-8")
        for example in re.findall(r"```python\n(.*?)```", text, re.DOTALL):
            exec(compile(example, name, "exec"), namespace)
