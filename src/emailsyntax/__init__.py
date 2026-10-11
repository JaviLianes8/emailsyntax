"""Syntax-only email address validation and normalization, zero dependencies, no DNS or network."""

from __future__ import annotations

from ._api import is_valid, normalize, split

__version__ = "0.1.0"

__all__ = ["is_valid", "normalize", "split"]
