from __future__ import annotations

import argparse
import os
import re
from datetime import datetime
from pathlib import Path

import yaml

from tools.publishing.common import (
    ARCHETYPES, CheckResult, EVIDENCE_LEVELS, FULL_SHA, ROOT, ValidationError,
    git_object_exists, parse_frontmatter, print_result, sha256_file,
)
from tools.publishing.validate_evidence import validate_ledger, validate_trigger

SOURCES_HEADING = "Sources and technical notes"
FORBIDDEN_HEADINGS = (
    "Evidence box", "Claims-to-evidence table", "Agent self-review",
    "How to reproduce or inspect the result",
)
INTERNAL_BODY_PATTERNS = (
    (r"\b[0-9a-f]{40}\b", "full Git SHA"),
    (r"\bPW-PUB-\d{4}-\d{3}\b", "publication trigger ID"),
    (r"\bSCI_[A-Z0-9_]{12,}\b", "internal scientific disposition"),
    (r"content/triggers/", "trigger path"),
    (r"content/evidence/", "evidence path"),
    (r"docs/status/current\.json", "project-state path"),
    (r"\bgit (?:clone|checkout|show)\b", "Git reproduction command"),
    (r"\bpytest\b", "test command"),
    (r"python -m tools\.publishing", "publishing validation command"),
    (r"\bclaim ceiling\b", "claim-ceiling terminology"),
    (r"\bevidence ledger\b", "evidence-ledger terminology"),
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


def validate(
    path: Path, repositories: dict[str, Path] | None = None, *, content_root: Path = ROOT
) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    repos = repositories or repository_paths()
    try:
        meta, body = parse_frontmatter(path)
    except (OSError, ValidationError) as exc:
        return CheckResult(path, (str(exc),))
    if meta.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    for field in (
        "title", "subtitle", "slug", "created_at", "updated_at", "author",
        "target_platforms", "primary_platform", "target_length_words", "uncertainty",
        "practical_implication", "ai_assistance", "cross_posting", "review", "reader_contract",
    ):
        if field not in meta:
            errors.append(f"{field} is required")
    if meta.get("author") != "Tim Brewer" or meta.get("primary_platform") != "substack":
        errors.append("author must be Tim Brewer and primary_platform must be substack")
    if meta.get("archetype") not in ARCHETYPES:
        errors.append("archetype is invalid")
    platform = meta.get("platform")
    filename_platform = next(
        (candidate for candidate in ("substack", "medium") if path.name.endswith(f".{candidate}.md")),
        None,
    )
    if filename_platform and platform != filename_platform:
        errors.append("variant platform metadata must match its filename")
    effective_platform = filename_platform or platform
    ledger_stem = (
        path.name.removesuffix(f".{effective_platform}.md")
        if effective_platform in {"substack", "medium"}
        else path.stem
    )
    status = meta.get("status")
    if status not in {"draft", "evidence_review", "human_review", "ready", "published", "withdrawn"}:
        errors.append("status is invalid")
    source_event = meta.get("source_event", {})
    trigger_id = source_event.get("trigger_id") if isinstance(source_event, dict) else None
    if not isinstance(trigger_id, str):
        errors.append("source_event.trigger_id is required")
    else:
        trigger_path = content_root / "content/triggers" / f"{trigger_id}.yml"
        if not trigger_path.exists():
            errors.append(f"source trigger does not exist: {trigger_path}")
        else:
            trigger_result = validate_trigger(trigger_path, repos)
            errors.extend(f"source trigger: {error}" for error in trigger_result.errors)
            try:
                trigger = yaml.safe_load(trigger_path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError):
                trigger = {}
        ledger_path = content_root / "content/evidence" / f"{ledger_stem}.yml"
        if not ledger_path.exists():
            errors.append(f"evidence ledger does not exist: {ledger_path}")
        else:
            ledger_result = validate_ledger(ledger_path, repos)
            errors.extend(f"evidence ledger: {error}" for error in ledger_result.errors)
            try:
                ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError):
                ledger = {}
            if isinstance(ledger, dict) and ledger.get("trigger_id") != trigger_id:
                errors.append("evidence ledger trigger_id does not match the draft")
    ceiling = meta.get("claim_ceiling", {})
    if not isinstance(ceiling, dict) or not FULL_SHA.fullmatch(str(ceiling.get("commit_sha", ""))):
        errors.append("claim_ceiling.commit_sha must be a full SHA")
    elif not ceiling.get("path") or not ceiling.get("exact_status"):
        errors.append("claim_ceiling path and exact_status are required")
    else:
        ceiling_repo = repos.get(str(ceiling.get("repository")))
        if ceiling_repo is None or not git_object_exists(
            ceiling_repo, str(ceiling["commit_sha"]), str(ceiling["path"])
        ):
            errors.append("claim_ceiling path does not exist at its exact repository commit")
        if "trigger" in locals() and isinstance(trigger, dict):
            state = trigger.get("scientific_state", {})
            bound = [
                artifact for artifact in trigger.get("artifacts", [])
                if artifact.get("repository") == ceiling.get("repository")
                and artifact.get("path") == ceiling.get("path")
                and artifact.get("commit_sha") == ceiling.get("commit_sha")
            ]
            if state.get("claim_ceiling_path") != ceiling.get("path") or len(bound) != 1:
                errors.append("draft claim ceiling does not exactly match the trigger control artifact")
    evidence = meta.get("source_artifacts")
    evidence_ids: set[str] = set()
    first_evidence_index: dict[str, int] = {}
    validated_artifact_ids: set[str] = set()
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
            elif str(evidence_id) in first_evidence_index:
                errors.append(
                    f"duplicate evidence_id {evidence_id}: first index "
                    f"{first_evidence_index[str(evidence_id)]}, duplicate index {index}"
                )
            else:
                first_evidence_index[str(evidence_id)] = index
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
                elif not item.get("path") or not git_object_exists(repo, str(item["commit_sha"]), str(item["path"])):
                    errors.append(f"source_artifacts[{index}] path does not exist at commit")
                else:
                    validated_artifact_ids.add(str(evidence_id))
            if item.get("repository") == "external-paper" and not item.get("paper_citation"):
                errors.append(f"source_artifacts[{index}].paper_citation is required")
    claims = meta.get("claims")
    claim_ids: set[str] = set()
    first_claim_index: dict[str, int] = {}
    quantitative_text = ""
    if not isinstance(claims, list) or not claims:
        errors.append("claims must not be empty")
    else:
        for index, claim in enumerate(claims):
            if not isinstance(claim, dict) or not re.fullmatch(r"C\d+", str(claim.get("claim_id", ""))):
                errors.append(f"claims[{index}].claim_id is invalid")
                continue
            claim_id = str(claim["claim_id"])
            if claim_id in first_claim_index:
                errors.append(
                    f"duplicate claim_id {claim_id}: first index "
                    f"{first_claim_index[claim_id]}, duplicate index {index}"
                )
            else:
                first_claim_index[claim_id] = index
                claim_ids.add(claim_id)
            cited = claim.get("evidence_ids")
            if not isinstance(cited, list) or not cited:
                errors.append(f"claims[{index}] has no evidence_ids")
            elif missing := set(map(str, cited)) - evidence_ids:
                errors.append(f"claims[{index}] cites unknown evidence: {sorted(missing)}")
            for field in ("text", "conditions", "evidence_level", "applicability", "caveat"):
                if not claim.get(field):
                    errors.append(f"claims[{index}].{field} is required")
            if claim.get("evidence_level") not in EVIDENCE_LEVELS:
                errors.append(f"claims[{index}].evidence_level is invalid")
            if not isinstance(claim.get("quantitative"), bool):
                errors.append(f"claims[{index}].quantitative must be boolean")
            elif claim["quantitative"]:
                quantitative_text += " " + str(claim.get("text", ""))
    heading_matches = list(re.finditer(r"^##\s+(.+)$", body, re.M))
    headings = [match.group(1).strip().casefold() for match in heading_matches]
    source_indices = [i for i, heading in enumerate(headings) if heading == SOURCES_HEADING.casefold()]
    if len(source_indices) != 1:
        errors.append(f"exactly one second-level section is required: {SOURCES_HEADING}")
        narrative = body
        sources_and_end = ""
    else:
        source_match = heading_matches[source_indices[0]]
        narrative = body[:source_match.start()]
        sources_and_end = body[source_match.end():]
        next_heading = re.search(r"^##\s+(.+)$", sources_and_end, re.M)
        source_text = sources_and_end[:next_heading.start()] if next_heading else sources_and_end
        source_text = source_text.replace("[PLATFORM DISCLOSURE]", "").strip()
        if not source_text:
            errors.append("Sources and technical notes must not be empty")
        if next_heading and next_heading.group(1).strip().casefold() not in {
            "ai-assistance disclosure", "ai assistance disclosure"
        }:
            errors.append("only the AI disclosure may follow Sources and technical notes")
    for forbidden in FORBIDDEN_HEADINGS:
        if forbidden.casefold() in headings:
            errors.append(f"forbidden public section: {forbidden}")
    if re.search(r"^\|\s*C\d+\s*\|", body, re.M | re.I):
        errors.append("public tables must not expose internal claim IDs")
    if "ledger" in locals() and isinstance(ledger, dict):
        ledger_evidence = {str(item.get("evidence_id")) for item in ledger.get("artifacts", [])}
        ledger_claims = {str(item.get("claim_id")) for item in ledger.get("claims", [])}
        if ledger_evidence != evidence_ids or ledger_claims != claim_ids:
            errors.append("draft evidence/claim IDs must exactly match the evidence ledger")
    def normalize(value: object) -> str:
        return " ".join(str(value).casefold().split())

    normalized_narrative = normalize(narrative)
    for claim in claims if isinstance(claims, list) else []:
        if isinstance(claim, dict) and normalize(claim.get("text")) not in normalized_narrative:
            errors.append(f"claim {claim.get('claim_id')} exact text is missing from the public narrative")
    reader_contract = meta.get("reader_contract", {})
    if not isinstance(reader_contract, dict) or any(
        not reader_contract.get(field) for field in ("question", "answer", "takeaway")
    ):
        errors.append("reader_contract must define question, answer, and takeaway")
    else:
        answer = normalize(reader_contract["answer"])
        claim_texts = {
            normalize(claim.get("text")) for claim in claims or [] if isinstance(claim, dict)
        }
        if answer not in claim_texts:
            errors.append("reader_contract.answer must exactly match a frontmatter claim")
        opening_words = list(re.finditer(r"\b[^\W_]+(?:[’'-][^\W_]+)*\b", narrative, re.UNICODE))
        opening = narrative[:opening_words[249].end()] if len(opening_words) > 250 else narrative
        if answer not in normalize(opening):
            errors.append("reader_contract.answer must appear within the first 250 narrative words")
        takeaway = normalize(reader_contract["takeaway"])
        if takeaway not in normalized_narrative:
            errors.append("reader_contract.takeaway is missing from the public narrative")
        practical = meta.get("practical_implication", {})
        if isinstance(practical, dict) and practical.get("supported") is True and takeaway != normalize(practical.get("text")):
            errors.append("reader_contract.takeaway must exactly match practical_implication.text")
    for pattern, label in INTERNAL_BODY_PATTERNS:
        if re.search(pattern, body, re.I):
            errors.append(f"public body contains forbidden internal mechanics: {label}")
    if re.search(r"```\s*(?:sh|bash|shell|console)\b.*?```", body, re.I | re.S):
        errors.append("public body contains a fenced shell reproduction block")
    for term in ("repository", "validator", "governance", "workflow", "schema", "commit"):
        if re.search(rf"\b{term}\b", narrative, re.I):
            warnings.append(f"reader-facing prose uses internal process term: {term}")
    number_body = re.sub(r"```.*?```|`[^`]+`", "", narrative, flags=re.S)
    number_body = re.sub(r"https?://\S+|\bdoi:\s*\S+", "", number_body, flags=re.I)
    numbers = set(re.findall(r"(?<![A-Za-z])\d+(?:\.\d+)?", number_body))
    unsupported_numbers = sorted(number for number in numbers if number not in quantitative_text)
    if unsupported_numbers:
        errors.append(f"numbers missing from quantitative claim text: {unsupported_numbers}")
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
    uncertainty = meta.get("uncertainty", {})
    uncertainty_fields = (
        "numerical", "measurement", "parameter", "model_form", "identifiability",
        "external_validity", "largest_remaining_uncertainty", "next_discriminating_measurement",
    )
    if not isinstance(uncertainty, dict) or any(field not in uncertainty for field in uncertainty_fields):
        errors.append("uncertainty must contain every governed uncertainty field")
    review = meta.get("review", {})
    ai = meta.get("ai_assistance", {})
    if status in {"ready", "published"}:
        required_review = ("evidence_gate_passed", "style_gate_passed", "platform_gate_passed", "human_approved")
        if not isinstance(review, dict) or any(review.get(field) is not True for field in required_review):
            errors.append("ready requires every review gate and human_approved")
        checks = ("scientific_claims_checked", "numbers_checked", "citations_checked", "figures_checked")
        if not isinstance(ai, dict) or ai.get("human_reviewer") != "Tim Brewer" or any(ai.get(field) is not True for field in checks):
            errors.append("ready requires Tim Brewer and all human scientific checks")
        if not review.get("approved_at"):
            errors.append("ready requires review.approved_at")
        if effective_platform == "medium" and ai.get("substantive_human_rewrite_medium") is not True:
            errors.append("ready Medium variant requires substantive_human_rewrite_medium: true")
    figures = meta.get("figures", [])
    if isinstance(figures, list):
        first_figure_index: dict[str, int] = {}
        publishing_repo = repos.get("puckworks")
        for index, figure in enumerate(figures):
            if not isinstance(figure, dict):
                errors.append(f"figures[{index}] must be a mapping")
                continue
            figure_id = str(figure.get("figure_id", ""))
            if not re.fullmatch(r"F\d+", figure_id):
                errors.append(f"figures[{index}].figure_id is invalid")
            elif figure_id in first_figure_index:
                errors.append(
                    f"duplicate figure_id {figure_id}: first index "
                    f"{first_figure_index[figure_id]}, duplicate index {index}"
                )
            else:
                first_figure_index[figure_id] = index
            if figure.get("hand_edited") is not False:
                errors.append(f"figures[{index}].hand_edited must be false")
            if not re.fullmatch(r"[0-9a-f]{64}", str(figure.get("output_sha256", ""))):
                errors.append(f"figures[{index}].output_sha256 must be SHA-256")
            for field in ("figure_id", "source_script", "source_data", "output_path", "caption", "alt_text", "evidence_ids", "regenerated_at"):
                if not figure.get(field):
                    errors.append(f"figures[{index}].{field} is required")
            try:
                regenerated = datetime.fromisoformat(str(figure.get("regenerated_at", "")).replace("Z", "+00:00"))
                if regenerated.tzinfo is None:
                    raise ValueError
            except ValueError:
                errors.append(f"figures[{index}].regenerated_at must be a timezone-aware timestamp")
            output_path = content_root / str(figure.get("output_path", ""))
            relative_output = Path(str(figure.get("output_path", "")))
            if relative_output.is_absolute() or ".." in relative_output.parts:
                errors.append(f"figures[{index}].output_path must stay within the repository")
            elif not output_path.is_file():
                errors.append(f"figures[{index}].output_path does not exist")
            elif sha256_file(output_path) != figure.get("output_sha256"):
                errors.append(f"figures[{index}] output SHA-256 does not match the file")
            raw_figure_evidence = figure.get("evidence_ids", [])
            figure_evidence = set(map(str, raw_figure_evidence)) if isinstance(raw_figure_evidence, list) else set()
            if not figure_evidence or figure_evidence - evidence_ids:
                errors.append(f"figures[{index}].evidence_ids contains missing or unknown IDs")
            source_data = figure.get("source_data")
            if not isinstance(source_data, list) or not source_data:
                errors.append(f"figures[{index}].source_data must contain at least one path")
                source_data = []

            def safe_relative(value: object) -> Path | None:
                candidate = Path(str(value or ""))
                if not value or candidate.is_absolute() or ".." in candidate.parts:
                    return None
                return candidate

            script_relative = safe_relative(figure.get("source_script"))
            if script_relative is None:
                errors.append(f"figures[{index}].source_script must be a safe repository-relative path")
            elif publishing_repo is None:
                errors.append(f"figures[{index}].source_script repository is unavailable")
            elif not (publishing_repo / script_relative).resolve().is_relative_to(publishing_repo.resolve()) or not (publishing_repo / script_relative).is_file():
                errors.append(f"figures[{index}].source_script does not exist in the checked-out puckworks repository")
            for data_index, source in enumerate(source_data):
                relative = safe_relative(source)
                if relative is None:
                    errors.append(f"figures[{index}].source_data[{data_index}] must be a safe repository-relative path")
                    continue
                local = publishing_repo is not None and (publishing_repo / relative).resolve().is_relative_to(publishing_repo.resolve()) and (publishing_repo / relative).is_file()
                historical = any(
                    isinstance(item, dict)
                    and str(item.get("evidence_id")) in figure_evidence
                    and str(item.get("evidence_id")) in validated_artifact_ids
                    and item.get("path") == str(source)
                    for item in evidence or []
                )
                if not local and not historical:
                    errors.append(f"figures[{index}].source_data[{data_index}] has no checked-out file or cited exact artifact")
            bound_commits = [
                str(item.get("commit_sha")) for item in evidence or []
                if isinstance(item, dict) and item.get("evidence_id") in figure_evidence
                and FULL_SHA.fullmatch(str(item.get("commit_sha", "")))
            ]
            if not bound_commits and FULL_SHA.fullmatch(str(ceiling.get("commit_sha", ""))):
                bound_commits = [str(ceiling["commit_sha"])]
            caption = str(figure.get("caption", ""))
            if str(figure.get("source_script", "")) not in caption or not any(
                commit in caption for commit in bound_commits
            ):
                errors.append(f"figures[{index}].caption must name its source script and exact commit")
    ai = meta.get("ai_assistance", {})
    if not isinstance(ai, dict) or ai.get("used") is not True:
        errors.append("ai_assistance.used must be true for generated drafts")
    else:
        for field in ("disclosure_substack", "disclosure_medium"):
            if not ai.get(field):
                errors.append(f"ai_assistance.{field} is required")
    disclosures = (
        "[PLATFORM DISCLOSURE]", "Drafting note: I used AI assistance",
        "Disclosure: I used an AI writing tool",
    )
    if not any(disclosure in body for disclosure in disclosures):
        errors.append("AI-assistance disclosure text or platform placeholder is missing")
    if re.search(r"H1 (?:is|has been) confirmed", body, re.I) and "confirmed" not in str(ceiling.get("exact_status", "")).casefold():
        errors.append("H1 confirmation exceeds the recorded claim ceiling")
    if status == "published":
        record = content_root / "content/published" / f"{ledger_stem}.yml"
        if not record.exists():
            errors.append("published status requires a publication record")
        else:
            try:
                published = yaml.safe_load(record.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError) as exc:
                errors.append(f"invalid publication record: {exc}")
            else:
                if not isinstance(published, dict) or published.get("published_by") != "Tim Brewer":
                    errors.append("publication record must name Tim Brewer as publisher")
                elif published.get("schema_version") != 1 or not published.get("substack_url") or not published.get("published_at"):
                    errors.append("publication record requires schema, Substack URL, and published_at")
                elif published.get("medium_url") and (
                    published.get("canonical_url") != published.get("substack_url")
                    or published.get("canonical_verified") is not True
                ):
                    errors.append("published Medium record requires verified exact Substack canonical")
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
