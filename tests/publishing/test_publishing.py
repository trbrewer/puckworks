from __future__ import annotations

import subprocess
import sys
import json
from copy import deepcopy
from datetime import date
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.publishing.build_variants import build
from tools.publishing.check_canonical import canonical_from_html
from tools.publishing.common import ValidationError, parse_frontmatter, sha256_file
from tools.publishing.generate_editorial_digest import generate
from tools.publishing.sync_editorial_issues import (
    MANAGED_END, MANAGED_START, apply_actions, main as reminder_main, merge_managed,
    plan_actions, reminder_block, reminder_is_due, reminder_managed, synchronize,
)
from tools.publishing.validate_draft import validate as validate_draft
from tools.publishing.validate_evidence import validate_ledger, validate_trigger
from tools.publishing.validate_schedule import validate as validate_schedule

def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")


@pytest.fixture
def publication_fixture(tmp_path: Path) -> dict[str, object]:
    repo = tmp_path / "repo"; repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "fixture@example.test"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Fixture"], check=True)
    (repo / "control.txt").write_text("synthetic control\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "control.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "synthetic fixture"], check=True)
    sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    root = tmp_path / "publication"
    for name in ("triggers", "evidence", "drafts", "variants", "published"):
        (root / "content" / name).mkdir(parents=True)
    trigger_id = "PW-PUB-2026-001"
    artifact = {"repository": "puckworks", "path": "control.txt", "commit_sha": sha, "issue_number": None, "pull_request_number": None, "release_tag": None, "run_id": None, "sha256": None, "purpose": "Synthetic validator fixture only"}
    trigger = {
        "schema_version": 1, "trigger_id": trigger_id, "publication_trigger": True,
        "source": {"repository": "puckworks", "event_type": "public_explainer", "identifier": f"commit:{sha}", "source_url": None, "detected_at": "2026-08-28T12:00:00Z"},
        "scientific_state": {"disposition": "SYNTHETIC_FIXTURE_ONLY", "claim_ceiling_path": "control.txt", "project_state_path": "control.txt", "evidence_level": "qualitative", "hypothesis_ids": [], "changes_claim_ceiling": False},
        "recommended_content": {"archetype": "behind_model", "provisional_title": "Synthetic fixture", "public_value_summary": "Exercises tooling only", "urgency": "routine", "target_platforms": ["substack", "medium"]},
        "artifacts": [artifact], "stop_reasons": [], "owner_notes": "Synthetic test fixture",
    }
    trigger_path = root / "content/triggers" / f"{trigger_id}.yml"; dump(trigger_path, trigger)
    evidence_item = {"evidence_id": "E1", "repository": "puckworks", "path": "control.txt", "commit_sha": sha, "paper_citation": None, "evidence_level": "qualitative", "establishes": "Synthetic fixture behavior", "does_not_establish": "Any scientific result"}
    claim = {"claim_id": "C1", "text": "This is a synthetic fixture.", "evidence_ids": ["E1"], "conditions": "Test process only", "evidence_level": "qualitative", "applicability": "Tool tests", "caveat": "Not scientific evidence", "quantitative": False}
    stem = "2026-08-28-synthetic-fixture"
    dump(root / "content/evidence" / f"{stem}.yml", {"schema_version": 1, "trigger_id": trigger_id, "draft_slug": "synthetic-fixture", "assembled_at": "2026-08-28T12:00:00Z", "artifacts": [evidence_item], "claims": [claim]})
    metadata = {
        "schema_version": 1, "title": "Synthetic fixture", "subtitle": "Tooling only", "slug": "synthetic-fixture", "archetype": "behind_model", "status": "draft", "created_at": "2026-08-28T12:00:00Z", "updated_at": "2026-08-28T12:00:00Z", "author": "Tim Brewer", "target_platforms": ["substack", "medium"], "primary_platform": "substack", "target_length_words": {"minimum": 1, "preferred": 1, "maximum": 10},
        "source_event": {"trigger_id": trigger_id, "repository": "puckworks", "event_type": "public_explainer", "identifier": f"commit:{sha}"}, "claim_ceiling": {"repository": "puckworks", "path": "control.txt", "commit_sha": sha, "exact_status": "SYNTHETIC_FIXTURE_ONLY"}, "source_artifacts": [evidence_item], "figures": [], "claims": [claim],
        "uncertainty": {field: "Synthetic fixture" for field in ("numerical", "measurement", "parameter", "model_form", "identifiability", "external_validity", "largest_remaining_uncertainty", "next_discriminating_measurement")}, "practical_implication": {"supported": False, "text": "", "conditions": "", "prohibited_overreach": "No science"},
        "ai_assistance": {"used": True, "tool_role": ["draft"], "human_reviewer": None, "scientific_claims_checked": False, "numbers_checked": False, "citations_checked": False, "figures_checked": False, "substantive_human_rewrite_medium": False, "disclosure_substack": "Drafting note: I used AI assistance to prepare and edit this article from the linked repository materials. I checked every scientific claim, number, citation, and figure before publication.", "disclosure_medium": "Disclosure: I used an AI writing tool to help draft and edit this article from the linked repository materials. I personally checked every scientific claim, number, citation, and figure."},
        "cross_posting": {"substack": {"planned": True, "send_email": True, "publication_date": None, "url": None}, "medium": {"planned": True, "publication_name": None, "publication_date": None, "publish_not_before": "2026-09-04", "url": None}, "canonical_url": None, "canonical_verified": False}, "review": {"evidence_gate_passed": False, "style_gate_passed": False, "platform_gate_passed": False, "human_approved": False, "approved_at": None},
    }
    headings = ("Result or question in one sentence", "Why this matters", "Question or hypothesis", "Evidence box", "Method", "Result", "Interpretation", "What this does not show", "Uncertainty and limitations", "What evidence would change the conclusion", "How to reproduce or inspect the result")
    body = "\n\n".join(f"## {heading}\n\nSynthetic fixture text." for heading in headings)
    body += "\n\n## Claims-to-evidence table\n\n| Claim ID | Exact claim | Evidence IDs | Evidence level | Conditions/applicability | Caveat |\n|---|---|---|---|---|---|\n| C1 | This is a synthetic fixture. | E1 | qualitative | Tool tests | Not scientific evidence |"
    body += "\n\n## AI-assistance disclosure\n\n[PLATFORM DISCLOSURE]\n\n## Agent self-review\n\nSynthetic fixture only.\n"
    draft_path = root / "content/drafts" / f"{stem}.md"
    draft_path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---\n" + body, encoding="utf-8")
    return {"root": root, "repo": repo, "sha": sha, "trigger": trigger, "trigger_path": trigger_path, "draft": draft_path}


def test_initial_schedule_is_valid_and_complete() -> None:
    result = validate_schedule(ROOT / "content/schedule.yml")
    assert result.ok, result.errors
    assert len(yaml.safe_load((ROOT / "content/schedule.yml").read_text())["items"]) == 12


@pytest.mark.parametrize("mutation", ["timezone", "duplicate", "delivery", "lag", "published"])
def test_schedule_adverse_paths(tmp_path: Path, mutation: str) -> None:
    schedule = yaml.safe_load((ROOT / "content/schedule.yml").read_text())
    if mutation == "timezone": schedule["timezone"] = "UTC"
    if mutation == "duplicate": schedule["items"][1]["id"] = schedule["items"][0]["id"]
    if mutation == "delivery": schedule["items"][0]["platforms"]["substack"]["send_email"] = False
    if mutation == "lag": schedule["items"][0]["platforms"]["medium"]["publish_not_before"] = date(2026, 9, 9)
    if mutation == "published": schedule["items"][0]["status"] = "published"
    path = tmp_path / "schedule.yml"; dump(path, schedule)
    assert not validate_schedule(path).ok


def test_trigger_and_ledger_success(publication_fixture: dict[str, object]) -> None:
    repos = {"puckworks": publication_fixture["repo"]}
    assert validate_trigger(publication_fixture["trigger_path"], repos).ok
    ledger = publication_fixture["root"] / "content/evidence/2026-08-28-synthetic-fixture.yml"
    assert validate_ledger(ledger, repos).ok


@pytest.mark.parametrize("mutation", ["short_sha", "missing_path", "stop", "bad_archetype", "bad_target"])
def test_trigger_adverse_paths(publication_fixture: dict[str, object], mutation: str, tmp_path: Path) -> None:
    trigger = deepcopy(publication_fixture["trigger"])
    if mutation == "short_sha": trigger["artifacts"][0]["commit_sha"] = "abc"
    if mutation == "missing_path": trigger["artifacts"][0]["path"] = "missing.txt"
    if mutation == "stop": trigger["stop_reasons"] = ["ambiguous disposition"]
    if mutation == "bad_archetype": trigger["recommended_content"]["archetype"] = "marketing"
    if mutation == "bad_target": trigger["recommended_content"]["target_platforms"] = ["medium"]
    path = tmp_path / "trigger.yml"; dump(path, trigger)
    assert not validate_trigger(path, {"puckworks": publication_fixture["repo"]}).ok


def test_draft_success(publication_fixture: dict[str, object]) -> None:
    result = validate_draft(publication_fixture["draft"], {"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"])
    assert result.ok, result.errors


@pytest.mark.parametrize("needle", ["missing_trigger", "ready", "number", "h1", "table", "banned"])
def test_draft_adverse_paths(publication_fixture: dict[str, object], needle: str) -> None:
    path = publication_fixture["draft"]; text = path.read_text()
    if needle == "missing_trigger": (publication_fixture["root"] / "content/triggers/PW-PUB-2026-001.yml").rename(publication_fixture["root"] / "content/triggers/moved.yml")
    if needle == "ready": text = text.replace("status: draft", "status: ready")
    if needle == "number": text = text.replace("Synthetic fixture text.", "Synthetic fixture text with 42 units.", 1)
    if needle == "h1": text = text.replace("Synthetic fixture text.", "H1 is confirmed.", 1)
    if needle == "table": text = text.replace("| C1 | This is", "| C2 | This is")
    if needle == "banned": text = text.replace("Synthetic fixture text.", "This is groundbreaking.", 1)
    path.write_text(text, encoding="utf-8")
    assert not validate_draft(path, {"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"]).ok


def test_substack_variant_and_overwrite_guard(publication_fixture: dict[str, object]) -> None:
    options = {"repositories": {"puckworks": publication_fixture["repo"]}, "content_root": publication_fixture["root"]}
    output = build(publication_fixture["draft"], publication_fixture["root"] / "content/variants", "substack", **options)
    with pytest.raises(ValidationError, match="overwrite"): build(publication_fixture["draft"], output.parent, "substack", **options)
    assert build(publication_fixture["draft"], output.parent, "substack", force=True, **options) == output


def test_medium_generation_precedes_canonical_verification(publication_fixture: dict[str, object]) -> None:
    path = publication_fixture["draft"]
    text = path.read_text().replace("url: null\n  medium:", "url: https://example.test/substack\n  medium:", 1).replace("canonical_url: null", "canonical_url: https://example.test/substack")
    path.write_text(text, encoding="utf-8")
    output = build(path, publication_fixture["root"] / "content/variants", "medium", repositories={"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"])
    assert "Human rewrite required" in output.read_text()


def test_medium_rejects_missing_substack_url(publication_fixture: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="published Substack URL"): build(publication_fixture["draft"], publication_fixture["root"] / "content/variants", "medium", repositories={"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"])


@pytest.mark.parametrize("when, expected", [
    (date(2026, 8, 26), False), (date(2026, 8, 27), True),
    (date(2026, 8, 28), True), (date(2026, 9, 1), True),
    (date(2026, 9, 2), True), (date(2026, 9, 3), True),
    (date(2026, 9, 5), True), (date(2026, 9, 8), True),
    (date(2026, 9, 9), True), (date(2027, 9, 9), True),
])
def test_reminder_window_recovers_overdue_items(when: date, expected: bool) -> None:
    item = {"draft_due": "2026-09-03", "publish_date": "2026-09-08"}
    assert reminder_is_due(item, when, [7, 2]) is expected


class FakeIssues:
    def __init__(self, data: list[dict[str, object]] | None = None) -> None: self.data, self.calls = data or [], []
    def ensure_labels(self) -> None: self.calls.append(("LABELS", "", None))
    def issues(self) -> list[dict[str, object]]: return self.data
    def request(self, method: str, path: str, payload: object | None = None) -> object: self.calls.append((method, path, payload)); return {}


def test_dry_run_makes_no_writes() -> None:
    api = FakeIssues(); actions = synchronize(api, ROOT / "content/schedule.yml", date(2026, 8, 28), ROOT, dry_run=True)
    assert actions and api.calls == []


def test_issue_dedup_and_terminal_close(tmp_path: Path) -> None:
    schedule = yaml.safe_load((ROOT / "content/schedule.yml").read_text()); schedule["items"][0]["status"] = "cancelled"
    path = tmp_path / "schedule.yml"; dump(path, schedule)
    actions = plan_actions([{"number": 17, "body": "<!-- publishing-schedule-id: launch-01 -->"}], path, date(2026, 8, 28), ROOT)
    matching = [action for action in actions if action.path == "/issues/17"]
    assert len(matching) == 1 and matching[0].payload["state"] == "closed"


def test_monday_digest_and_diagnostics() -> None:
    digest = generate(ROOT / "content/schedule.yml", date(2026, 8, 31), ROOT)
    assert digest.startswith("<!-- publishing-editorial-digest: 2026-08-31 -->")
    for heading in ("Posts due in the next 14 days", "Trigger diagnostics", "Draft diagnostics", "Evidence-ledger diagnostics", "Schedule diagnostics"): assert heading in digest


def test_canonical_parser_requires_exactly_one() -> None:
    assert canonical_from_html('<link href="https://example.test/source" rel="alternate canonical">') == "https://example.test/source"
    assert canonical_from_html('<link rel="canonical" href="a"><link rel="canonical" href="b">') is None


def test_workflow_dispatch_is_dry_run_by_default() -> None:
    workflow = (ROOT / ".github/workflows/editorial-reminders.yml").read_text()
    assert "apply_changes:" in workflow and "default: false" in workflow
    assert "args=(--apply)" in workflow
    assert "vars.ENABLE_EDITORIAL_REMINDERS == 'true'" in workflow
    assert 'github.event_name }}" == "schedule"' in workflow
    assert 'vars.ENABLE_EDITORIAL_REMINDERS }}" == "true"' in workflow
    assert 'inputs.apply_changes }}" == "true"' in workflow


def test_evidence_ledger_must_match_draft(publication_fixture: dict[str, object]) -> None:
    ledger_path = publication_fixture["root"] / "content/evidence/2026-08-28-synthetic-fixture.yml"
    ledger = yaml.safe_load(ledger_path.read_text()); ledger["claims"][0]["claim_id"] = "C9"
    dump(ledger_path, ledger)
    result = validate_draft(publication_fixture["draft"], {"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"])
    assert not result.ok and any("exactly match" in error for error in result.errors)


def test_trigger_requires_exact_control_artifacts(publication_fixture: dict[str, object]) -> None:
    trigger = deepcopy(publication_fixture["trigger"])
    trigger["scientific_state"]["project_state_path"] = "unlisted-state.txt"
    path = publication_fixture["root"] / "bad-control.yml"; dump(path, trigger)
    result = validate_trigger(path, {"puckworks": publication_fixture["repo"]})
    assert not result.ok and any("project_state_path" in error for error in result.errors)


def test_draft_claim_ceiling_must_match_trigger_binding(publication_fixture: dict[str, object]) -> None:
    path = publication_fixture["draft"]
    text = path.read_text().replace("path: control.txt\n  commit_sha:", "path: other.txt\n  commit_sha:", 1)
    path.write_text(text, encoding="utf-8")
    result = validate_draft(path, {"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"])
    assert not result.ok and any("claim ceiling" in error or "claim_ceiling" in error for error in result.errors)


def test_identifier_must_be_closed_by_artifact(publication_fixture: dict[str, object]) -> None:
    trigger = deepcopy(publication_fixture["trigger"]); trigger["source"]["identifier"] = "run:RUN-1"
    path = publication_fixture["root"] / "run-trigger.yml"; dump(path, trigger)
    assert not validate_trigger(path, {"puckworks": publication_fixture["repo"]}).ok
    trigger["artifacts"][0]["run_id"] = "RUN-1"; dump(path, trigger)
    assert validate_trigger(path, {"puckworks": publication_fixture["repo"]}).ok


def test_ready_medium_requires_substantive_human_rewrite(publication_fixture: dict[str, object]) -> None:
    path = publication_fixture["draft"]
    text = path.read_text().replace("url: null\n  medium:", "url: https://example.test/substack\n  medium:", 1).replace("canonical_url: null", "canonical_url: https://example.test/substack")
    path.write_text(text, encoding="utf-8")
    output = build(path, publication_fixture["root"] / "content/variants", "medium", repositories={"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"])
    meta, body = parse_frontmatter(output); meta["status"] = "ready"
    meta["ai_assistance"].update({"human_reviewer": "Tim Brewer", "scientific_claims_checked": True, "numbers_checked": True, "citations_checked": True, "figures_checked": True})
    meta["review"].update({"evidence_gate_passed": True, "style_gate_passed": True, "platform_gate_passed": True, "human_approved": True, "approved_at": "2026-08-28T13:00:00Z"})
    output.write_text("---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n" + body, encoding="utf-8")
    result = validate_draft(output, {"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"])
    assert not result.ok and any("substantive_human_rewrite_medium" in error for error in result.errors)
    meta["ai_assistance"]["substantive_human_rewrite_medium"] = True
    output.write_text("---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n" + body, encoding="utf-8")
    assert validate_draft(output, {"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"]).ok


def add_valid_figure(publication_fixture: dict[str, object]) -> tuple[Path, dict[str, object], str, Path]:
    repo = publication_fixture["repo"]
    for name, text in (("figure.py", "print('fixture')\n"), ("data.csv", "x,y\n")):
        (repo / name).write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "figure.py", "data.csv"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "figure fixture"], check=True)
    sha = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    path = publication_fixture["draft"]; meta, body = parse_frontmatter(path)
    items = []
    for index, name in enumerate(("figure.py", "data.csv"), 2):
        items.append({"evidence_id": f"E{index}", "repository": "puckworks", "path": name, "commit_sha": sha, "paper_citation": None, "evidence_level": "qualitative", "establishes": "Synthetic figure provenance", "does_not_establish": "Science"})
    meta["source_artifacts"].extend(items)
    ledger_path = publication_fixture["root"] / "content/evidence/2026-08-28-synthetic-fixture.yml"
    ledger = yaml.safe_load(ledger_path.read_text()); ledger["artifacts"].extend(items); dump(ledger_path, ledger)
    output = publication_fixture["root"] / "figure.png"; output.write_bytes(b"synthetic figure")
    meta["figures"] = [{"figure_id": "F1", "source_script": "figure.py", "source_data": ["data.csv"], "output_path": "figure.png", "output_sha256": sha256_file(output), "caption": f"Synthetic result generated by figure.py at commit {sha}; synthetic-data limitation.", "alt_text": "Line chart with synthetic axes, trend, and no uncertainty.", "evidence_ids": ["E2", "E3"], "regenerated_at": "2026-08-28T13:00:00Z", "hand_edited": False}]
    path.write_text("---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n" + body, encoding="utf-8")
    return path, meta, body, output


def test_figure_requires_exact_sources_output_and_checksum(publication_fixture: dict[str, object]) -> None:
    path, _, _, output = add_valid_figure(publication_fixture)
    repo = publication_fixture["repo"]
    assert validate_draft(path, {"puckworks": repo}, content_root=publication_fixture["root"]).ok
    output.write_bytes(b"tampered")
    assert not validate_draft(path, {"puckworks": repo}, content_root=publication_fixture["root"]).ok


def test_figure_output_must_exist(publication_fixture: dict[str, object]) -> None:
    path, _, _, output = add_valid_figure(publication_fixture)
    output.unlink()
    result = validate_draft(path, {"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"])
    assert any("output_path does not exist" in error for error in result.errors)


def test_historical_figure_data_requires_cited_exact_artifact(publication_fixture: dict[str, object]) -> None:
    path, meta, body, _ = add_valid_figure(publication_fixture)
    repo = publication_fixture["repo"]
    (repo / "data.csv").unlink()
    assert validate_draft(path, {"puckworks": repo}, content_root=publication_fixture["root"]).ok
    meta["figures"][0]["evidence_ids"] = ["E2"]
    path.write_text("---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n" + body, encoding="utf-8")
    result = validate_draft(path, {"puckworks": repo}, content_root=publication_fixture["root"])
    assert any("no checked-out file or cited exact artifact" in error for error in result.errors)


@pytest.mark.parametrize("field,value", [
    ("source_script", "/tmp/figure.py"),
    ("source_script", "../figure.py"),
    ("source_script", "missing.py"),
    ("source_data", ["/tmp/data.csv"]),
    ("source_data", ["../data.csv"]),
    ("source_data", ["missing.csv"]),
])
def test_figure_input_path_adverse_cases(publication_fixture: dict[str, object], field: str, value: object) -> None:
    path, meta, body, _ = add_valid_figure(publication_fixture)
    meta["figures"][0][field] = value
    path.write_text("---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n" + body, encoding="utf-8")
    assert not validate_draft(path, {"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"]).ok


def test_sync_defaults_to_no_writes() -> None:
    api = FakeIssues()
    assert synchronize(api, ROOT / "content/schedule.yml", date(2026, 8, 28), ROOT)
    assert api.calls == []


def test_sync_requires_explicit_apply_for_writes() -> None:
    api = FakeIssues()
    actions = synchronize(
        api, ROOT / "content/schedule.yml", date(2026, 8, 28), ROOT, dry_run=False
    )
    assert actions
    assert api.calls[0][0] == "LABELS"
    assert any(call[0] == "POST" and call[1] == "/issues" for call in api.calls)


def test_managed_issue_update_preserves_human_text() -> None:
    item = {"id": "launch-01", "title": "Fixture", "status": "planned", "draft_due": "2026-09-03", "publish_date": "2026-09-08"}
    old = "<!-- publishing-schedule-id: launch-01 -->\nHuman note: keep this.\n"
    marker = "<!-- publishing-schedule-id: launch-01 -->"
    first = merge_managed(old, reminder_managed(item, date(2026, 8, 28)), marker)
    first += "Human footer: keep this too.\n"
    second = merge_managed(first, reminder_managed(item, date(2026, 8, 29)), marker)
    assert "Human note: keep this." in second
    assert "Human footer: keep this too." in second
    assert second.count(MANAGED_START) == second.count(MANAGED_END) == 1
    assert "2026-08-29" in second


def test_managed_region_rejects_single_marker() -> None:
    with pytest.raises(ValidationError, match="malformed"):
        merge_managed(MANAGED_START, f"{MANAGED_START}\nx\n{MANAGED_END}", "<!-- publishing-schedule-id: x -->")


def test_unchanged_issue_plans_no_patch(tmp_path: Path) -> None:
    schedule = yaml.safe_load((ROOT / "content/schedule.yml").read_text())
    schedule["items"] = [schedule["items"][0]]
    path = tmp_path / "schedule.yml"; dump(path, schedule)
    item = schedule["items"][0]
    issue = {"number": 1, "title": f"Editorial reminder: {item['title']}",
             "body": reminder_block(item, date(2026, 8, 28)), "state": "open",
             "labels": [{"name": "editorial"}, {"name": "publish-reminder"}]}
    assert plan_actions([issue], path, date(2026, 8, 28), ROOT) == []
    assert plan_actions([issue], path, date(2026, 8, 28), ROOT) == []
    issue["body"] = str(issue["body"]).replace("2026-08-28", "2026-08-27")
    actions = plan_actions([issue], path, date(2026, 8, 28), ROOT)
    assert len(actions) == 1 and set(actions[0].payload) == {"body"}


def test_terminal_reminder_creation_and_closure(tmp_path: Path) -> None:
    schedule = yaml.safe_load((ROOT / "content/schedule.yml").read_text())
    schedule["items"] = [schedule["items"][0]]
    schedule["items"][0]["status"] = "cancelled"
    path = tmp_path / "schedule.yml"; dump(path, schedule)
    assert plan_actions([], path, date(2026, 9, 9), ROOT) == []
    item = schedule["items"][0]
    issue = {"number": 1, "title": f"Editorial reminder: {item['title']}",
             "body": reminder_block(item, date(2026, 9, 9)), "state": "open",
             "labels": ["editorial", "publish-reminder"]}
    actions = plan_actions([issue], path, date(2026, 9, 9), ROOT)
    assert len(actions) == 1 and actions[0].payload == {"state": "closed"}
    issue["state"] = "closed"
    assert plan_actions([issue], path, date(2026, 9, 9), ROOT) == []


def test_cli_default_and_explicit_dry_run_are_credential_free(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False); monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    class MustNotConstruct:
        def __init__(self, *_: object) -> None: raise AssertionError("network client constructed")
    for args in (["--date", "2026-08-31"], ["--dry-run", "--date", "2026-08-31"],
                 ["--date", "2026-08-31", "--issues-json", str(ROOT / "tests/publishing/fixtures/editorial_issues.json")]):
        assert reminder_main(args, client_factory=MustNotConstruct) == 0
        captured = capsys.readouterr()
        assert isinstance(json.loads(captured.out), list)
        if "--issues-json" not in args:
            assert "remote deduplication was not evaluated" in captured.err


def test_cli_apply_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False); monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    with pytest.raises(SystemExit) as exc:
        reminder_main(["--apply", "--date", "2026-08-31"])
    assert exc.value.code == 2


def test_fake_client_apply_performs_only_planned_writes() -> None:
    api = FakeIssues()
    actions = plan_actions([], ROOT / "content/schedule.yml", date(2026, 8, 28), ROOT)
    apply_actions(api, actions)
    writes = [call for call in api.calls if call[0] in {"POST", "PATCH"} and call[1].startswith("/issues")]
    assert len(writes) == len(actions)


def test_cli_explicit_apply_uses_fake_client(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "synthetic-token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "example/repository")
    instances: list[FakeIssues] = []
    class Factory(FakeIssues):
        def __init__(self, repository: str, token: str) -> None:
            assert (repository, token) == ("example/repository", "synthetic-token")
            super().__init__(); instances.append(self)
    assert reminder_main(["--apply", "--date", "2026-08-28"], client_factory=Factory) == 0
    actions = json.loads(capsys.readouterr().out)
    assert instances and len([call for call in instances[0].calls if call[0] == "POST" and call[1] == "/issues"]) == len(actions)


@pytest.mark.parametrize("section,id_key", [("source_artifacts", "evidence_id"), ("claims", "claim_id"), ("figures", "figure_id")])
def test_duplicate_draft_ids_rejected(publication_fixture: dict[str, object], section: str, id_key: str) -> None:
    path = publication_fixture["draft"]; meta, body = parse_frontmatter(path)
    if section == "figures":
        meta[section] = [{"figure_id": "F1"}, {"figure_id": "F1"}]
    else:
        meta[section].append(deepcopy(meta[section][0]))
    path.write_text("---\n" + yaml.safe_dump(meta, sort_keys=False) + "---\n" + body, encoding="utf-8")
    result = validate_draft(path, {"puckworks": publication_fixture["repo"]}, content_root=publication_fixture["root"])
    assert any(f"duplicate {id_key}" in error for error in result.errors)


def test_duplicate_ledger_claim_id_rejected(publication_fixture: dict[str, object]) -> None:
    path = publication_fixture["root"] / "content/evidence/2026-08-28-synthetic-fixture.yml"
    ledger = yaml.safe_load(path.read_text()); ledger["claims"].append(deepcopy(ledger["claims"][0])); dump(path, ledger)
    result = validate_ledger(path, {"puckworks": publication_fixture["repo"]})
    assert any("duplicate claim_id C1" in error for error in result.errors)
