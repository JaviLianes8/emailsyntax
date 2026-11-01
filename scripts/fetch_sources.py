"""Fetch the external evidence recorded in sources/MANIFEST.json."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path


def main() -> None:
    manifest = Path(__file__).resolve().parents[1] / "sources" / "MANIFEST.json"
    destination = Path(sys.argv[1])
    destination.mkdir(parents=True, exist_ok=True)
    for item in json.loads(manifest.read_text(encoding="utf-8")):
        with urllib.request.urlopen(item["url"], timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError(f"source changed: {item['name']}")
        (destination / item["name"]).write_bytes(data)


if __name__ == "__main__":
    main()
