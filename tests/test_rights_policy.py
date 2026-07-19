"""Use-specific rights policy + record validation + release safety (issue #73, Phase 1).

Offline + deterministic. One rights state is never universally sufficient: a component may be inspectable
locally yet not cleared for public execution, output redistribution, or release inclusion. These tests
pin the use-specific decisions, the RightsRecord validation, the removal of the generic release bypass
(there is no --allow-rights-blocked flag), and that NOT_REVIEWED is a reported gap, never "clear".
"""
import subprocess
import sys
from pathlib import Path

import pytest

import puckworks
from puckworks import release, rights

_ROOT = Path(__file__).resolve().parents[1]


# ── use-specific policy ─────────────────────────────────────────────────────────────
def test_blocked_component_is_blocked_for_every_use():
    for fn in (rights.may_execute_locally, rights.may_execute_in_public_batch,
               rights.may_publish_outputs, rights.may_include_code_in_release):
        d = fn("grudeva2025.reduced")
        assert d.allowed is False and d.severity == "blocked"


def test_not_reviewed_is_inspectable_locally_but_not_public_or_output():
    cid = "cameron2020.extraction_bdf"       # the common lens, NOT_REVIEWED
    assert rights.rights_record(cid).code_rights_state == "NOT_REVIEWED"
    assert rights.may_execute_locally(cid).allowed is True          # dev inspection allowed
    assert rights.may_execute_locally(cid).severity == "gap"        # ...but a gap, not "clear"
    assert rights.may_execute_in_public_batch(cid).allowed is False  # not public without review
    assert rights.may_publish_outputs(cid).allowed is False
    # NOT_REVIEWED never reports as clear
    for d in (rights.may_execute_locally(cid), rights.may_execute_in_public_batch(cid)):
        assert d.severity != "clear"


def test_release_inclusion_hard_blocks_only_on_blocked_code():
    # NOT_REVIEWED code ships in the dev package as a reported gap (not a hard block)
    d = rights.may_include_code_in_release("cameron2020.extraction_bdf")
    assert d.allowed is True and d.severity == "gap"
    # blocked code is a hard block for release inclusion
    d2 = rights.may_include_code_in_release("grudeva2025.reduced")
    assert d2.allowed is False and d2.severity == "blocked"


def test_every_use_is_in_the_finite_vocabulary():
    for fn in (rights.may_execute_locally, rights.may_execute_in_public_batch,
               rights.may_publish_outputs, rights.may_include_code_in_release,
               rights.may_include_data_in_release):
        assert fn("cameron2020.extraction_bdf").use in rights.RIGHTS_USES


# ── RightsRecord validation ─────────────────────────────────────────────────────────
def test_reviewed_record_requires_source_and_iso_date():
    with pytest.raises(ValueError):                      # reviewed but no source/date
        rights.RightsRecord("c", code_rights_state="CLEAR", data_rights_state="CLEAR",
                            output_redistribution_state="CLEAR")
    with pytest.raises(ValueError):                      # bad date format
        rights.RightsRecord("c", code_rights_state="CLEAR", data_rights_state="CLEAR",
                            output_redistribution_state="CLEAR", source="s", review_date="2026/07/19")
    ok = rights.RightsRecord("c", code_rights_state="CLEAR", data_rights_state="CLEAR",
                             output_redistribution_state="CLEAR", source="s", review_date="2026-07-19")
    assert ok.code_rights_state == "CLEAR"


def test_blocked_requires_issue_and_reason():
    with pytest.raises(ValueError):
        rights.RightsRecord("c", code_rights_state="RIGHTS_BLOCKED", data_rights_state="NOT_REVIEWED",
                            output_redistribution_state="NOT_REVIEWED", source="s", review_date="2026-07-19")


def test_permission_documented_requires_metadata():
    with pytest.raises(ValueError):
        rights.RightsRecord("c", code_rights_state="PERMISSION_DOCUMENTED", data_rights_state="NOT_REVIEWED",
                            output_redistribution_state="NOT_REVIEWED", source="s", review_date="2026-07-19")
    ok = rights.RightsRecord("c", code_rights_state="PERMISSION_DOCUMENTED",
                             data_rights_state="NOT_REVIEWED", output_redistribution_state="NOT_REVIEWED",
                             source="s", review_date="2026-07-19",
                             permission={"grantor": "X", "date": "2026-07-19", "scope": "code"})
    assert ok.permission["grantor"] == "X"


def test_not_applicable_requires_reason():
    with pytest.raises(ValueError):
        rights.RightsRecord("c", code_rights_state="NOT_APPLICABLE", data_rights_state="NOT_REVIEWED",
                            output_redistribution_state="NOT_REVIEWED", source="s", review_date="2026-07-19")


def test_record_set_validation_catches_unknown_and_tombstone():
    assert rights.validate_records() == []               # the shipped set is clean
    reg = {c.name for c in puckworks.components()}
    bad = {"ghost.model": rights.RightsRecord("ghost.model", "NOT_REVIEWED", "NOT_REVIEWED",
                                              "NOT_REVIEWED")}
    probs = rights.validate_records(bad, reg)
    assert any("no registered component" in p for p in probs)
    # a tombstone record for a removed component is allowed
    tomb = {"ghost.model": rights.RightsRecord("ghost.model", "RIGHTS_BLOCKED", "NOT_REVIEWED",
                                               "RIGHTS_BLOCKED", rights_note="removed", source="s",
                                               decision_issue="#73", review_date="2026-07-19",
                                               tombstone=True)}
    assert rights.validate_records(tomb, reg) == []


def test_lowercase_local_vocabulary_is_rejected():
    with pytest.raises(ValueError):
        rights.RightsRecord("c", code_rights_state="clear", data_rights_state="clear",
                            output_redistribution_state="clear")


# ── review backlog ──────────────────────────────────────────────────────────────────
def test_review_backlog_surfaces_the_priority_reviews_without_asserting_clear():
    bl = rights.review_backlog(
        runner_ids=["waszkiewicz2025.poroelastic", "wadsworth2026.permeability", "foster2025.infiltration"],
        adapter_ids=["cameron2020.extraction_bdf"],
        data_fixtures=["de1_fixtureA.json"])
    # Cameron public execution + output publication are unreviewed gaps (priority-1 review)
    cam = [i for i in bl if i["component_id"] == "cameron2020.extraction_bdf"
           and i["use"] == "public_batch_execution"]
    assert cam and cam[0]["needs_review"] is True and cam[0]["governing_state"] == "NOT_REVIEWED"
    # nothing in the backlog is asserted CLEAR
    assert all(i["governing_state"] != "CLEAR" for i in bl)
    # the data fixture is present as a review item
    assert any(i["component_id"] == "de1_fixtureA.json" for i in bl)


# ── release safety: no generic bypass ───────────────────────────────────────────────
def test_release_guard_blocks_on_blocked_code_and_reports_gaps():
    problems = release.rights_release_problems(_ROOT)
    assert any("grudeva2025.reduced" in p for p in problems)
    gaps = release.rights_release_gaps(_ROOT)
    assert any("cameron2020.extraction_bdf" in g for g in gaps)     # NOT_REVIEWED reported, not silent


def test_no_generic_allow_rights_blocked_bypass_exists():
    src = (_ROOT / "puckworks" / "release.py").read_text(encoding="utf-8")
    assert "allow-rights-blocked" not in src and "allow_rights_blocked" not in src
    # the CLI must reject the removed flag rather than accept it
    proc = subprocess.run([sys.executable, "-m", "puckworks.release", "build", "--allow-rights-blocked"],
                          cwd=_ROOT, capture_output=True, text=True)
    assert proc.returncode != 0 and "unrecognized arguments" in (proc.stderr + proc.stdout).lower()


def test_release_main_blocks_without_building_and_no_flag_can_bypass(monkeypatch):
    import unittest.mock as mock
    built = {"called": False}
    monkeypatch.setattr(release, "build", lambda *a, **k: built.__setitem__("called", True))
    monkeypatch.setattr(release, "twine_check", lambda *a, **k: None)
    monkeypatch.setattr(release, "release_manifest", lambda *a, **k: {})
    assert release.main(["build"]) == 2 and built["called"] is False    # blocked before build
    # once the blocked module is absent (authorized removal), the guard passes with no flag
    with mock.patch.object(release, "rights_release_problems", return_value=[]):
        monkeypatch.setattr(release, "rights_release_gaps", lambda *a, **k: [])
        built["called"] = False
        monkeypatch.setattr(release, "release_manifest", lambda *a, **k: {"commit": "x", "dirty": False,
                                                                          "python": "3", "artifacts": {}})
        monkeypatch.setattr("pathlib.Path.write_text", lambda *a, **k: None)
        assert release.main(["build"]) == 0 and built["called"] is True
