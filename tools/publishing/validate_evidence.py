from __future__ import annotations

import argparse
import re
from pathlib import Path

from tools.publishing.common import (
    ARCHETYPES, CheckResult, EVIDENCE_LEVELS, EVENT_TYPES, FULL_SHA, ROOT, TRIGGER_ID,
    ValidationError, git_commit_exists, git_object_exists, git_tag_exists, load_yaml, print_result,
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
        source = {}
    for field in ("repository", "identifier", "detected_at"):
        if not source.get(field):
            errors.append(f"source.{field} is required")
    if source.get("repository") not in {"puckworks", "espresso-whole-pull"}:
        errors.append("source.repository is invalid")
    identifier = str(source.get("identifier", ""))
    source_repo = repos.get(str(source.get("repository")))
    if identifier.startswith("commit:"):
        commit = identifier.removeprefix("commit:")
        if source_repo is None or not git_commit_exists(source_repo, commit):
            errors.append("source.identifier commit does not resolve")
    elif identifier.startswith("release:"):
        tag = identifier.removeprefix("release:")
        if source_repo is None or not git_tag_exists(source_repo, tag):
            errors.append("source.identifier release does not resolve")
    elif not re.fullmatch(r"(?:issue:#\d+|run:[A-Za-z0-9._:-]+)", identifier):
        errors.append("source.identifier has an invalid kind or value")
    state = doc.get("scientific_state", {})
    if not isinstance(state, dict):
        errors.append("scientific_state must be a mapping")
        state = {}
    if not state.get("disposition"):
        errors.append("scientific_state.disposition is required")
    if state.get("evidence_level") not in EVIDENCE_LEVELS:
        errors.append("scientific_state.evidence_level is invalid")
    if not isinstance(state.get("hypothesis_ids"), list):
        errors.append("scientific_state.hypothesis_ids must be a list")
    if not isinstance(state.get("changes_claim_ceiling"), bool):
        errors.append("scientific_state.changes_claim_ceiling must be boolean")
    recommended = doc.get("recommended_content", {})
    if not isinstance(recommended, dict):
        errors.append("recommended_content must be a mapping")
    else:
        if recommended.get("archetype") not in ARCHETYPES:
            errors.append("recommended_content.archetype is invalid")
        if recommended.get("urgency") not in {"routine", "timely", "correction"}:
            errors.append("recommended_content.urgency is invalid")
        targets = recommended.get("target_platforms")
        if not isinstance(targets, list) or "substack" not in targets or any(
            platform not in {"substack", "medium"} for platform in targets
        ):
            errors.append("recommended_content.target_platforms is invalid")
        for field in ("provisional_title", "public_value_summary"):
            if not recommended.get(field):
                errors.append(f"recommended_content.{field} is required")
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
        checksum = artifact.get("sha256")
        if checksum is not None and not re.fullmatch(r"[0-9a-f]{64}", str(checksum)):
            errors.append(f"{prefix}.sha256 must be lowercase SHA-256")
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


def validate_ledger(path: Path, repositories: dict[str, Path] | None = None) -> CheckResult:
    errors: list[str] = []
    repos = repositories or {"puckworks": ROOT}
    try:
        doc = load_yaml(path)
    except ValidationError as exc:
        return CheckResult(path, (str(exc),))
    if doc.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not TRIGGER_ID.fullmatch(str(doc.get("trigger_id", ""))):
        errors.append("trigger_id is invalid")
    if not doc.get("draft_slug") or not doc.get("assembled_at"):
        errors.append("draft_slug and assembled_at are required")
    artifacts = doc.get("artifacts")
    ids: set[str] = set()
    if not isinstance(artifacts, list) or not artifacts:
        return CheckResult(path, tuple(errors + ["artifacts must not be empty"]))
    for index, item in enumerate(artifacts):
        prefix = f"artifacts[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be a mapping")
            continue
        evidence_id = str(item.get("evidence_id", ""))
        if not re.fullmatch(r"E\d+", evidence_id) or evidence_id in ids:
            errors.append(f"{prefix}.evidence_id is invalid or duplicated")
        ids.add(evidence_id)
        if item.get("evidence_level") not in EVIDENCE_LEVELS:
            errors.append(f"{prefix}.evidence_level is invalid")
        for field in ("establishes", "does_not_establish"):
            if not item.get(field):
                errors.append(f"{prefix}.{field} is required")
        repository = item.get("repository")
        if repository == "external-paper":
            if not item.get("paper_citation"):
                errors.append(f"{prefix}.paper_citation is required")
        else:
            commit, relative = str(item.get("commit_sha", "")), item.get("path")
            repo = repos.get(str(repository))
            if not FULL_SHA.fullmatch(commit):
                errors.append(f"{prefix}.commit_sha must be a full SHA")
            elif repo is None:
                errors.append(f"{prefix}.repository is unavailable")
            elif not isinstance(relative, str) or not git_object_exists(repo, commit, relative):
                errors.append(f"{prefix}.path does not exist at commit")
    claims = doc.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("claims must not be empty")
    else:
        for index, claim in enumerate(claims):
            cited = claim.get("evidence_ids", []) if isinstance(claim, dict) else []
            if not cited or set(map(str, cited)) - ids:
                errors.append(f"claims[{index}] has missing or unknown evidence_ids")
    return CheckResult(path, tuple(errors))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--espresso-repo", type=Path)
    args = parser.parse_args()
    repos = {"puckworks": ROOT}
    if args.espresso_repo:
        repos["espresso-whole-pull"] = args.espresso_repo.resolve()
    results = [
        validate_trigger(path, repos) if "triggers" in path.parts else validate_ledger(path, repos)
        for path in args.paths
    ]
    return max(print_result(result) for result in results)


if __name__ == "__main__":
    raise SystemExit(main())
