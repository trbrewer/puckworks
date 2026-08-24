"""Deterministic sanitized JSON reporting."""
from __future__ import annotations

import json
from pathlib import Path


def write_json(path: str | None, payload: dict) -> None:
    if not path:
        return
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

