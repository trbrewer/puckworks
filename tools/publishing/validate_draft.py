from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from tools.publishing.common import (
    ARCHETYPES, CheckResult, EVIDENCE_LEVELS, FULL_SHA, ROOT, ValidationError,
    git_object_exists, parse_frontmatter, print_result,
)
from tools.publishing.validate_evidence import validate_trigger

REQUIRED_SECTIONS = (
    "Result or question in one sentence", "Why this matters", "Question or hypothesis",
    "Evidence box", "Method", "Result", "Interpretation", "What this does not show",
    "Uncertainty and limitations", "What evidence would change the conclusion",
    "How to reproduce or inspect the result", "Claims-to-evidence table",
    "AI-assistance disclosure", "Agent self-review",
)
BANNED = (
    "revolutionize", "revolutionary", "game-changing", "journey", "unlock the secret",
    "shocking", "proves once and for all", "science says", "everyone knows",
    "objectively best", "perfect shot", "bad barista", "delve", "tapestry",
    "groundbreaking",
)


def repository_paths() -> dict[str, Path]:
    paths = {"puckworks": ROOT}
    if espresso := os.environ.get("ESPRESSO_WHOLE_PULL_REPO"):
        paths["espresso-whole-pull"] = Path(espresso).resolve()
    return paths


def validate(path: Path, repositories: dict[str, Path] | None = None) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    repos = repositories or repository_paths()
    try:
        meta, body = parse_frontmatter(path)
    except (OSError, ValidationError) as exc:
        return CheckResult(path, (str(exc),))
    if meta.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if meta.get("archetype") not in ARCHETYPES:
        errors.append("archetype is invalid")
    status = meta.get("status")
    if status not in {"draft", "evidence_review", "human_review", "ready", "published", "withdrawn"}:
        errors.append("status is invalid")
    source_event = meta.get("source_event", {})
    trigger_id = source_event.get("trigger_id") if isinstance(source_event, dict) else None
    if not isinstance(trigger_id, str):
        errors.append("source_event.trigger_id is required")
    else:
        trigger_path = ROOT / "content/triggers" / f"{trigger_id}.yml"
        if not trigger_path.exists():
            errors.append(f"source trigger does not exist: {trigger_path.relative_to(ROOT)}")
        else:
            trigger_result = validate_trigger(trigger_path, repos)
            errors.extend(f"source trigger: {error}" for error in trigger_result.errors)
    ceiling = meta.get("claim_ceiling", {})
    if not isinstance(ceiling, dict) or not FULL_SHA.fullmatch(str(ceiling.get("commit_sha", ""))):
        errors.append("claim_ceiling.commit_sha must be a full SHA")
    elif not ceiling.get("path") or not ceiling.get("exact_status"):
        errors.append("claim_ceiling path and exact_status are required")
    evidence = meta.get("source_artifacts")
    evidence_ids: set[str] = set()
    if not isinstance(evidence, list) or not evidence:
        errors.append("source_artifacts must not be empty")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, dict):
                errors.append(f"source_artifacts[{index}] must be a mapping")
                continue
            evidence_id = item.get("evidence_id")
            if not re.fullmatch(r"E\d+", str(evidence_id or "")):
                errors.append(f"source_artifacts[{index}].evidence_id is invalid")
            else:
                evidence_ids.add(str(evidence_id))
            if item.get("evidence_level") not in EVIDENCE_LEVELS:
                errors.append(f"source_artifacts[{index}].evidence_level is invalid")
            if not item.get("establishes") or not item.get("does_not_establish"):
                errors.append(f"source_artifacts[{index}] must define both evidence boundaries")
            if item.get("repository") != "external-paper" and not FULL_SHA.fullmatch(str(item.get("commit_sha", ""))):
                errors.append(f"source_artifacts[{index}].commit_sha must be a full SHA")
            elif item.get("repository") != "external-paper":
                repo = repos.get(str(item.get("repository")))
                if repo is None:
                    errors.append(f"source_artifacts[{index}].repository is unavailable")
                elif not item.get("path") or not git_object_exists(
                    repo, str(item["commit_sha"]), str(item["path"])
                ):
                    errors.append(f"source_artifacts[{index}] path does not exist at commit")
            if item.get("repository") == "external-paper" and not item.get("paper_citation"):
                errors.append(f"source_artifacts[{index}].paper_citation is required")
    claims = meta.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("claims must not be empty")
    else:
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict) or not re.fullmatch(r"C\d+", str(claim.get("claim_id", ""))):
                errors.append(f"claims[{index}].claim_id is invalid")
                continue
            cited = claim.get("evidence_ids")
            if not isinstance(cited, list) or not cited:
                errors.append(f"claims[{index}] has no evidence_ids")
            elif missing := set(map(str, cited)) - evidence_ids:
                errors.append(f"claims[{index}] cites unknown evidence: {sorted(missing)}")
            for field in ("text", "conditions", "evidence_level", "applicability", "caveat"):
                if not claim.get(field):
                    errors.append(f"claims[{index}].{field} is required")
    headings = [match.group(1).strip().casefold() for match in re.finditer(r"^##\s+(.+)$", body, re.M)]
    positions = []
    for required in REQUIRED_SECTIONS:
        target = required.casefold()
        try:
            positions.append(headings.index(target))
        except ValueError:
            errors.append(f"missing required section: {required}")
    if len(positions) == len(REQUIRED_SECTIONS) and positions != sorted(positions):
        errors.append("required body sections are out of order")
    body_lower = body.casefold()
    for phrase in BANNED:
        if re.search(rf"\b{re.escape(phrase)}\b", body_lower):
            errors.append(f"banned wording: {phrase}")
    if "the model shows" in body_lower:
        errors.append("'the model shows' is prohibited; cite the exact artifact")
    practical = meta.get("practical_implication", {})
    if isinstance(practical, dict) and practical.get("supported") is not True and re.search(
        r"^## Practical implication\s*$", body, re.M
    ):
        errors.append("practical implication section present without supported: true")
    review = meta.get("review", {})
    ai = meta.get("ai_assistance", {})
    if status == "ready":
        required_review = ("evidence_gate_passed", "style_gate_passed", "platform_gate_passed", "human_approved")
        if not isinstance(review, dict) or any(review.get(field) is not True for field in required_review):
            errors.append("ready requires every review gate and human_approved")
        checks = ("scientific_claims_checked", "numbers_checked", "citations_checked", "figures_checked")
        if not isinstance(ai, dict) or ai.get("human_reviewer") != "Tim Brewer" or any(ai.get(field) is not True for field in checks):
            errors.append("ready requires Tim Brewer and all human scientific checks")
        if not review.get("approved_at"):
            errors.append("ready requires review.approved_at")
    figures = meta.get("figures", [])
    if isinstance(figures, list):
        for index, figure in enumerate(figures):
            if figure.get("hand_edited") is not False:
                errors.append(f"figures[{index}].hand_edited must be false")
            if not re.fullmatch(r"[0-9a-f]{64}", str(figure.get("output_sha256", ""))):
                errors.append(f"figures[{index}].output_sha256 must be SHA-256")
    if status == "published":
        warnings.append("Only a human may set published; automated validation cannot attest authorization")
    return CheckResult(path, tuple(errors), tuple(warnings))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--espresso-repo", type=Path)
    args = parser.parse_args()
    repos = {"puckworks": ROOT}
    if args.espresso_repo:
        repos["espresso-whole-pull"] = args.espresso_repo.resolve()
    return max(print_result(validate(path, repos)) for path in args.paths)


if __name__ == "__main__":
    raise SystemExit(main())
