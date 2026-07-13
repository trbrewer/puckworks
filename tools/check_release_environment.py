#!/usr/bin/env python3
"""Fail unless the active interpreter matches the recorded paper-release stack."""
from __future__ import annotations

import argparse
import importlib
import json
import platform
from pathlib import Path
from typing import Any


def _default_lock() -> Path:
    return Path(__file__).resolve().parents[1] / "docs/reproducibility/paper_release_environment.json"


def check(lock_path: Path) -> tuple[bool, list[str], dict[str, Any]]:
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    observed: dict[str, Any] = {
        "python": platform.python_version(),
        "packages": {},
    }
    failures: list[str] = []

    expected_python = str(lock["python"])
    if observed["python"] != expected_python:
        failures.append(
            f"python: expected {expected_python}, observed {observed['python']}"
        )

    for name, expected in lock["packages"].items():
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError:
            observed["packages"][name] = "ABSENT"
            failures.append(f"{name}: expected {expected}, package is absent")
            continue
        actual = str(getattr(module, "__version__", "UNKNOWN"))
        observed["packages"][name] = actual
        if actual != str(expected):
            failures.append(f"{name}: expected {expected}, observed {actual}")

    return not failures, failures, observed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, default=_default_lock())
    parser.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = parser.parse_args(argv)

    ok, failures, observed = check(args.lock)
    payload = {
        "ok": ok,
        "lock": str(args.lock),
        "observed": observed,
        "failures": failures,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("release environment:", "OK" if ok else "MISMATCH")
        print(json.dumps(observed, indent=2, sort_keys=True))
        for failure in failures:
            print("  FAIL:", failure)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
