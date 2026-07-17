#!/usr/bin/env python3
"""Strict loader/validator for the public-release display record (docs/status/public_release.json).

This record is a compact, machine-readable **projection of durable release facts** for
public-experience tooling (the README project-pulse and the Colab quickstart). It is NOT a
project-status authority — current project work is governed by ``docs/status/current.json`` and the
generated ``STATE_OF_TRUTH.md``; historical release verification is governed by
``docs/reproducibility/RELEASE_VERIFICATION_v0.2.0.md``.

The validator fails closed on: missing fields, unknown fields, wrong scalar types, a malformed
version, a malformed 40-hex source commit or tag object, a malformed full SHA-256, a non-HTTPS
release URL, or an unsupported registry state.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SCHEMA_VERSION = 1

# name -> (python type, validator predicate or None)
_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_VERSION = re.compile(r"^\d+\.\d+\.\d+([.-][0-9A-Za-z.]+)?$")
_RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")
_REGISTRY_STATES = ("github_only", "pypi", "test_pypi", "other")

REQUIRED_FIELDS = (
    "schema_version", "version", "tag", "release_url", "published_at", "source_commit",
    "annotated_tag_object", "wheel_filename", "wheel_sha256", "sdist_filename", "sdist_sha256",
    "manually_attached_asset_count", "registry_status",
)
OPTIONAL_FIELDS = ("note",)


def _is_strict_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def validate(record: dict) -> list[str]:
    """Return a list of problem strings ([] if the record is valid)."""
    problems: list[str] = []
    if not isinstance(record, dict):
        return ["record is not a JSON object"]

    allowed = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)
    for k in record:
        if k not in allowed:
            problems.append(f"unknown unsupported field: {k!r}")
    for f in REQUIRED_FIELDS:
        if f not in record:
            problems.append(f"missing field: {f!r}")
    if problems:
        return problems  # don't index missing fields below

    if record["schema_version"] != SCHEMA_VERSION:
        problems.append(f"schema_version must be {SCHEMA_VERSION}")
    for f in ("version", "tag", "release_url", "published_at", "source_commit",
              "annotated_tag_object", "wheel_filename", "wheel_sha256", "sdist_filename",
              "sdist_sha256", "registry_status"):
        if not isinstance(record[f], str):
            problems.append(f"{f} must be a string")
    if "note" in record and not isinstance(record["note"], str):
        problems.append("note must be a string")

    if isinstance(record["version"], str) and not _VERSION.match(record["version"]):
        problems.append("version is malformed")
    if isinstance(record["published_at"], str) and not _RFC3339.match(record["published_at"]):
        problems.append("published_at must be an RFC 3339 timestamp with an explicit offset")
    if isinstance(record["source_commit"], str) and not _HEX40.match(record["source_commit"]):
        problems.append("source_commit must be a full 40-char lowercase hex commit")
    if isinstance(record["annotated_tag_object"], str) and not _HEX40.match(record["annotated_tag_object"]):
        problems.append("annotated_tag_object must be a full 40-char lowercase hex object")
    for f in ("wheel_sha256", "sdist_sha256"):
        if isinstance(record[f], str) and not _SHA256.match(record[f]):
            problems.append(f"{f} must be a full lowercase SHA-256")
    if isinstance(record["release_url"], str) and not record["release_url"].startswith("https://"):
        problems.append("release_url must be HTTPS")
    if not _is_strict_int(record["manually_attached_asset_count"]) or record["manually_attached_asset_count"] < 0:
        problems.append("manually_attached_asset_count must be a non-negative integer")
    if record["registry_status"] not in _REGISTRY_STATES:
        problems.append(f"registry_status must be one of {_REGISTRY_STATES}")
    return problems


def load(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_validated(path: str | Path) -> dict:
    record = load(path)
    problems = validate(record)
    if problems:
        raise ValueError("invalid public_release.json:\n  " + "\n  ".join(problems))
    return record


def canonical_wheel_url(record: dict) -> str:
    """Derive the canonical release-download URL for the wheel from the validated record."""
    base = record["release_url"].rsplit("/tag/", 1)[0]
    return f"{base}/download/{record['tag']}/{record['wheel_filename']}"


if __name__ == "__main__":
    import sys

    p = sys.argv[1] if len(sys.argv) > 1 else str(
        Path(__file__).resolve().parents[1] / "docs" / "status" / "public_release.json")
    probs = validate(load(p))
    if probs:
        print("INVALID:", *probs, sep="\n  ")
        raise SystemExit(1)
    print(f"public_release.json OK: {load(p)['tag']}")
