from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
TRIGGER_ID = re.compile(r"^PW-PUB-\d{4}-\d{3}$")
EVIDENCE_LEVELS = {
    "independent", "post_fit", "calibration", "verification", "descriptive",
    "exploratory", "qualitative", "mixed",
}
TERMINAL_SCHEDULE_STATUSES = {"published", "cancelled", "withdrawn"}
SCHEDULE_STATUSES = {
    "planned", "drafting", "evidence_review", "human_review", "ready",
    *TERMINAL_SCHEDULE_STATUSES,
}
ARCHETYPES = {
    "finding_report", "myth_check", "innovation_review", "practical_guide",
    "behind_model", "data_release", "correction",
}
EVENT_TYPES = {
    "tagged_release", "milestone_closed", "dataset_added", "validation_completed",
    "hypothesis_updated", "correction", "blocked_result", "public_explainer",
}


class ValidationError(ValueError):
    """Raised when publishing metadata violates a governing invariant."""


@dataclass(frozen=True)
class CheckResult:
    path: Path
    errors: tuple[str, ...]
    warnings: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValidationError(f"{path}: cannot read YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path}: top level must be a mapping")
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValidationError(f"{path}: missing YAML frontmatter")
    try:
        raw, body = text[4:].split("\n---\n", 1)
        metadata = yaml.safe_load(raw)
    except (ValueError, yaml.YAMLError) as exc:
        raise ValidationError(f"{path}: invalid frontmatter: {exc}") from exc
    if not isinstance(metadata, dict):
        raise ValidationError(f"{path}: frontmatter must be a mapping")
    return metadata, body


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_object_exists(repo: Path, commit: str, relative_path: str) -> bool:
    if not FULL_SHA.fullmatch(commit) or relative_path.startswith(("/", "../")):
        return False
    result = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{commit}:{relative_path}"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def git_commit_exists(repo: Path, commit: str) -> bool:
    if not FULL_SHA.fullmatch(commit):
        return False
    result = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True, check=False,
    )
    return result.returncode == 0


def git_tag_exists(repo: Path, tag: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}^{{}}"],
        capture_output=True, check=False,
    )
    return result.returncode == 0


def parse_date(value: Any, field: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValidationError(f"{field} must be YYYY-MM-DD") from exc


def require(mapping: dict[str, Any], field: str, errors: list[str], prefix: str = "") -> Any:
    value = mapping.get(field)
    if value is None or value == "":
        errors.append(f"{prefix}{field}: required")
    return value


def print_result(result: CheckResult) -> int:
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    print(f"{'PASS' if result.ok else 'FAIL'}: {result.path}")
    return 0 if result.ok else 1
