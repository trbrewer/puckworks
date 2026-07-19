"""Deterministic tests for the research intake + registry-impact tooling (issue #46, channel B).

Offline. Exercises the intake schema/validator, DOI->arXiv->title identity + dedup, the delta
detections (card/registry mismatch, card-no-implementation, component-no-gate, rights-unresolved,
Waszkiewicz journal identity, WBC rights-pending, Grudeva disposition), deterministic JSON/Markdown,
the no-implementation-authorization contract, and the no-full-text/no-private-locator guard. PyYAML
is a dev/radar extra (not core), so the module is imported lazily and skipped where absent.
"""
import importlib
from pathlib import Path

import pytest

pytest.importorskip("yaml")                       # tools/research_impact needs pyyaml (dev/radar extra)

import sys
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
RI = importlib.import_module("tools.research_impact")

INTAKE = _ROOT / "docs" / "research" / "intake"


# ── identity + dedup ─────────────────────────────────────────────────────────────
def test_identity_prefers_doi_then_arxiv_then_title():
    assert RI.record_identity({"doi": "10.1/AbC", "arxiv_id": "1", "title": "x"}) == "doi:10.1/abc"
    assert RI.record_identity({"doi": None, "arxiv_id": "2512.21528", "title": "x"}) == "arxiv:2512.21528"
    assert RI.record_identity({"title": "Hello,  World!"}) == "title:hello world"


def test_dedupe_preserves_all_provenance_and_reports_duplicates():
    a = {"stable_id": "a", "doi": "10.1/x", "title": "A"}
    b = {"stable_id": "b", "doi": "10.1/X", "title": "B"}       # same DOI (case-insensitive)
    c = {"stable_id": "c", "doi": "10.9/z", "title": "C"}
    unique, dups = RI.dedupe([a, b, c])
    assert len(unique) == 2
    assert "doi:10.1/x" in dups and len(dups["doi:10.1/x"]) == 2   # both provenance rows kept


# ── schema validation ────────────────────────────────────────────────────────────
def test_committed_intake_records_are_valid():
    records = RI.load_intake(INTAKE)
    problems = [p for r in records for p in r["_problems"]]
    assert problems == [], "\n".join(problems)
    assert len(records) >= 3


def test_validator_rejects_bad_state_and_unknown_field():
    schema = RI.load_schema()
    bad = {"stable_id": "x_bad", "title": "T", "source_type": "article",
           "access_state": "totally_made_up", "redistribution_state": "rights_pending",
           "disposition": "metadata_only", "surprise": 1}
    probs = RI.validate_record(bad, schema, source="bad")
    assert any("access_state" in p for p in probs)
    assert any("unknown field 'surprise'" in p for p in probs)


def test_validator_rejects_private_locator_and_full_text_tokens():
    schema = RI.load_schema()
    rec = {"stable_id": "leak_x", "title": "T", "source_type": "article",
           "access_state": "metadata_only", "redistribution_state": "not_applicable",
           "disposition": "metadata_only", "url": "https://x/file?token=SECRET"}
    probs = RI.validate_record(rec, schema, source="leak")
    assert any("forbidden private/full-text token" in p for p in probs)


def test_rights_and_disposition_vocabularies_are_closed():
    assert "rights_pending" in RI._REDIST_STATES and "metadata_only" in RI._ACCESS_STATES
    assert "implement-candidate" in RI._DISPOSITIONS and "already-carded" in RI._DISPOSITIONS


# ── status-token parsing (prose must not trigger false matches) ────────────────────
def test_status_token_ignores_prose():
    assert RI.status_token("card-only — the component is already registered and gated") == "card-only"
    assert RI.status_token("gated (recorded-pressure closed form)") == "gated"
    assert RI.status_token("proposed → skip") == "proposed"
    assert RI.status_token("implemented (2026-07-15)") == "implemented"


# ── the impact report over the live registry + cards + committed intake ────────────
@pytest.fixture(scope="module")
def report():
    return RI.build_report()


def test_report_is_deterministic():
    a = RI.canonical_json(RI.build_report())
    b = RI.canonical_json(RI.build_report())
    assert a == b


def test_report_never_authorizes_implementation(report):
    assert report["authorizes_implementation"] is False
    blob = RI.canonical_json(report).lower()
    assert "authorizes_implementation" in blob
    # no finding is phrased as an action/authorization
    for f in report["findings"]:
        assert "authoriz" not in f["category"]


def test_component_no_gate_is_detected(report):
    # every registered component with an empty gate tuple must be surfaced
    import puckworks
    gateless = {c.name for c in puckworks.components() if not c.gates}
    flagged = {f["subject"] for f in report["findings"] if f["category"] == "component_no_gate"}
    assert gateless == flagged


def test_card_registry_status_drift_is_detected(report):
    # a registered/executable component whose card still says proposed/card-only is surfaced
    stale = {f["subject"] for f in report["findings"]
             if f["category"] == "component_card_status_stale"}
    assert "pannusch2024.solver" in stale       # known drift (card 'card-only', component gated)


def test_waszkiewicz_card_no_longer_drifts(report):
    # the fixed Waszkiewicz card must NOT be flagged as stale any more
    stale = {f["subject"] for f in report["findings"]
             if f["category"] == "component_card_status_stale"}
    assert "waszkiewicz2025.poroelastic" not in stale


def test_grudeva_is_card_no_implementation(report):
    cats = {(f["subject"], f["category"]) for f in report["findings"]}
    assert ("grudeva2026_2", "card_no_implementation") in cats
    assert ("grudeva2026_infiltration_extraction", "card_no_implementation_intake") in cats


def test_wbc_rights_are_unresolved(report):
    rights = {f["subject"] for f in report["findings"] if f["category"] == "rights_unresolved"}
    assert "wbc2025_in_numbers" in rights


def test_waszkiewicz_journal_identity_recorded():
    records = {r["stable_id"]: r for r in RI.load_intake(INTAKE)}
    w = records["waszkiewicz2025_poroelastic"]
    assert w["doi"] == "10.1063/5.0319611"
    assert w["published_date"] == "2026-06-23"
    assert w["redistribution_state"] == "redistribution_prohibited"    # AIP article, cite-only
    # and the card carries the journal DOI + gated status
    card = (_ROOT / "docs" / "cards" / "waszkiewicz2025.md").read_text(encoding="utf-8")
    assert "10.1063/5.0319611" in card
    assert card.lower().count("card-only") == 0 or "status:** gated" in card.lower()


def test_markdown_report_is_stable_and_readable(report):
    md = RI.render_markdown(report)
    assert md == RI.render_markdown(report)                # deterministic
    assert "research registry-impact report" in md.lower()
    assert "not** an implementation authorization" in md.lower()


def test_report_has_no_network_or_wall_clock(report):
    blob = RI.canonical_json(report)
    # no timestamp/date fields in the canonical report (deterministic hashing)
    for bad in ("timestamp", "generated_at", "datetime", "wall_clock"):
        assert bad not in blob
