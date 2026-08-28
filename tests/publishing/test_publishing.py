from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from tools.publishing.check_canonical import canonical_from_html
from tools.publishing.generate_editorial_digest import generate
from tools.publishing.sync_editorial_issues import synchronize
from tools.publishing.validate_draft import validate as validate_draft
from tools.publishing.validate_evidence import validate_trigger
from tools.publishing.validate_schedule import validate as validate_schedule

ROOT = Path(__file__).resolve().parents[2]
START_SHA = "a67c5cd6018961d290f9e560b78e95074f7654ef"


def test_initial_schedule_is_valid_and_complete() -> None:
    path = ROOT / "content/schedule.yml"
    result = validate_schedule(path)
    assert result.ok, result.errors
    assert len(yaml.safe_load(path.read_text())["items"]) == 12


def test_trigger_requires_existing_artifact_at_full_commit(tmp_path: Path) -> None:
    trigger = {
        "schema_version": 1,
        "trigger_id": "PW-PUB-2026-001",
        "publication_trigger": True,
        "source": {"repository": "puckworks", "event_type": "public_explainer", "identifier": "commit:" + START_SHA},
        "scientific_state": {
            "disposition": "governance explainer only", "claim_ceiling_path": "docs/CURRENT.md",
            "project_state_path": "docs/status/current.json", "evidence_level": "qualitative",
            "hypothesis_ids": [], "changes_claim_ceiling": False,
        },
        "recommended_content": {"archetype": "behind_model"},
        "artifacts": [{"repository": "puckworks", "path": "docs/CURRENT.md", "commit_sha": START_SHA, "purpose": "Controls current repository state"}],
        "stop_reasons": [],
    }
    path = tmp_path / "trigger.yml"
    path.write_text(yaml.safe_dump(trigger), encoding="utf-8")
    assert validate_trigger(path, {"puckworks": ROOT}).ok
    trigger["artifacts"][0]["path"] = "does/not/exist"
    path.write_text(yaml.safe_dump(trigger), encoding="utf-8")
    assert not validate_trigger(path, {"puckworks": ROOT}).ok


def test_draft_cannot_self_approve(tmp_path: Path) -> None:
    body = "\n".join(f"## {heading}" for heading in (
        "Result or question in one sentence", "Why this matters", "Question or hypothesis",
        "Evidence box", "Method", "Result", "Interpretation", "What this does not show",
        "Uncertainty and limitations", "What evidence would change the conclusion",
        "How to reproduce or inspect the result", "Claims-to-evidence table",
        "AI-assistance disclosure", "Agent self-review",
    ))
    metadata = {
        "schema_version": 1, "title": "Synthetic fixture", "slug": "synthetic-fixture",
        "archetype": "behind_model", "status": "ready", "target_platforms": ["substack"],
        "claim_ceiling": {"path": "docs/CURRENT.md", "commit_sha": START_SHA, "exact_status": "fixture only"},
        "source_artifacts": [{"evidence_id": "E1", "repository": "puckworks", "path": "docs/CURRENT.md", "commit_sha": START_SHA, "evidence_level": "qualitative", "establishes": "fixture behavior", "does_not_establish": "science"}],
        "claims": [{"claim_id": "C1", "text": "Synthetic fixture.", "evidence_ids": ["E1"], "conditions": "test", "evidence_level": "qualitative", "applicability": "tests", "caveat": "not science", "quantitative": False}],
        "practical_implication": {"supported": False}, "figures": [],
        "ai_assistance": {"human_reviewer": None}, "review": {},
    }
    path = tmp_path / "draft.md"
    path.write_text("---\n" + yaml.safe_dump(metadata) + "---\n" + body, encoding="utf-8")
    result = validate_draft(path)
    assert not result.ok
    assert any("ready requires" in error for error in result.errors)


class FakeIssues:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, object | None]] = []
        self.data: list[dict[str, object]] = []

    def ensure_labels(self) -> None:
        self.calls.append(("LABELS", "", None))

    def issues(self) -> list[dict[str, object]]:
        return self.data

    def request(self, method: str, path: str, payload: object | None = None) -> object:
        self.calls.append((method, path, payload))
        return {}


def test_issue_sync_deduplicates_by_marker(tmp_path: Path) -> None:
    api = FakeIssues()
    api.data = [{"number": 17, "body": "<!-- publishing-schedule-id: launch-01 -->"}]
    synchronize(api, ROOT / "content/schedule.yml", date(2026, 8, 27), ROOT)
    changes = [call for call in api.calls if call[0] == "PATCH" and call[1] == "/issues/17"]
    assert len(changes) == 1
    assert not any(call[0] == "POST" and call[1] == "/issues" for call in api.calls)


def test_digest_sections_and_canonical_parser() -> None:
    digest = generate(ROOT / "content/schedule.yml", date(2026, 9, 1), ROOT)
    assert "Posts due in the next 14 days" in digest
    assert "Trigger diagnostics" in digest
    assert canonical_from_html('<link rel="canonical" href="https://example.test/source">') == "https://example.test/source"
