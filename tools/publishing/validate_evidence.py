from __future__ import annotations

import argparse
from pathlib import Path

from tools.publishing.common import (
    CheckResult, EVIDENCE_LEVELS, EVENT_TYPES, FULL_SHA, ROOT, TRIGGER_ID,
    ValidationError, git_object_exists, load_yaml, print_result,
)


def validate_trigger(path: Path, repositories: dict[str, Path] | None = None) -> CheckResult:
    errors: list[str] = []
    repos = repositories or {"puckworks": ROOT}
    try:
        doc = load_yaml(path)
    except ValidationError as exc:
        return CheckResult(path, (str(exc),))
    if doc.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if doc.get("publication_trigger") is not True:
        errors.append("publication_trigger must be true")
    if not TRIGGER_ID.fullmatch(str(doc.get("trigger_id", ""))):
        errors.append("trigger_id must match PW-PUB-YYYY-NNN")
    source = doc.get("source", {})
    if not isinstance(source, dict) or source.get("event_type") not in EVENT_TYPES:
        errors.append("source.event_type is invalid")
    state = doc.get("scientific_state", {})
    if not isinstance(state, dict):
        errors.append("scientific_state must be a mapping")
        state = {}
    if not state.get("disposition"):
        errors.append("scientific_state.disposition is required")
    if state.get("evidence_level") not in EVIDENCE_LEVELS:
        errors.append("scientific_state.evidence_level is invalid")
    artifacts = doc.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        return CheckResult(path, tuple(errors + ["artifacts must contain at least one item"]))
    listed_paths: set[str] = set()
    for index, artifact in enumerate(artifacts):
        prefix = f"artifacts[{index}]"
        if not isinstance(artifact, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        repository = artifact.get("repository")
        relative_path = artifact.get("path")
        commit = artifact.get("commit_sha")
        if not FULL_SHA.fullmatch(str(commit or "")):
            errors.append(f"{prefix}.commit_sha must be a full lowercase SHA")
        if not isinstance(relative_path, str) or not relative_path:
            errors.append(f"{prefix}.path is required")
        else:
            listed_paths.add(relative_path)
        repo = repos.get(str(repository))
        if repo is None:
            errors.append(f"{prefix}.repository is unavailable for validation")
        elif isinstance(relative_path, str) and FULL_SHA.fullmatch(str(commit or "")):
            if not git_object_exists(repo, str(commit), relative_path):
                errors.append(f"{prefix}: {relative_path} does not exist at {commit}")
        if not artifact.get("purpose"):
            errors.append(f"{prefix}.purpose is required")
    ceiling = state.get("claim_ceiling_path")
    project = state.get("project_state_path")
    if not ceiling or not project:
        errors.append("claim_ceiling_path and project_state_path are required")
    if state.get("changes_claim_ceiling") is True and ceiling not in listed_paths:
        errors.append("changed claim ceiling must be a listed artifact")
    stop_reasons = doc.get("stop_reasons", [])
    if not isinstance(stop_reasons, list):
        errors.append("stop_reasons must be a list")
    elif stop_reasons:
        errors.append("trigger has fatal stop_reasons: " + "; ".join(map(str, stop_reasons)))
    return CheckResult(path, tuple(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--espresso-repo", type=Path)
    args = parser.parse_args()
    repos = {"puckworks": ROOT}
    if args.espresso_repo:
        repos["espresso-whole-pull"] = args.espresso_repo.resolve()
    results = [validate_trigger(path, repos) for path in args.paths]
    return max(print_result(result) for result in results)


if __name__ == "__main__":
    raise SystemExit(main())
