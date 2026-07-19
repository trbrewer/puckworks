"""Centralized component-rights registry + Grudeva containment tests (issue #73).

Offline + deterministic. Verifies one authoritative rights record per registered component (NOT_REVIEWED
fallback, never a silent CLEAR), that code/data/output rights are distinct, that the Lab / runners /
adapters refuse a rights-blocked component, that README governance rejects an "Executable model" label
for it, that the release-readiness guard flags it, and that v0.3.0 history + model numerics are untouched.
"""
import subprocess
from pathlib import Path

import pytest

import puckworks
from puckworks import rights
from puckworks.product import lab, lab_runners

_ROOT = Path(__file__).resolve().parents[1]


def test_exactly_one_record_per_component_with_not_reviewed_fallback():
    records = rights.all_rights()
    ids = [r.component_id for r in records]
    assert ids == sorted(ids)
    assert set(ids) == {c.name for c in puckworks.components()}
    assert len(ids) == len(set(ids))
    # an unreviewed component is NOT_REVIEWED, never a silent CLEAR
    cam = rights.rights_record("cameron2020.extraction_bdf")
    assert cam.code_rights_state == "NOT_REVIEWED"
    for r in records:
        for s in (r.code_rights_state, r.data_rights_state, r.output_redistribution_state):
            assert s in rights.RIGHTS_STATES


def test_grudeva_is_code_rights_blocked_with_separate_dimensions():
    g = rights.rights_record("grudeva2025.reduced")
    assert g.code_rights_state == "RIGHTS_BLOCKED"
    # code rights are NOT the article rights: distinct fields, code blocked, data under review
    assert g.data_rights_state == "RIGHTS_REVIEW_REQUIRED"
    assert g.output_redistribution_state == "RIGHTS_BLOCKED"
    assert g.decision_issue == "#73"
    assert "cc-by" in g.rights_note.lower() and "not" in g.rights_note.lower()  # article != code
    assert rights.blocked_components() == ["grudeva2025.reduced"]


def test_article_and_code_rights_cannot_be_conflated():
    # a record with a CC-BY article does not make its solver code CLEAR
    r = rights.RightsRecord("x", code_rights_state="RIGHTS_BLOCKED", data_rights_state="CLEAR",
                            output_redistribution_state="RIGHTS_BLOCKED")
    assert r.is_code_blocked and not r.code_rights_state == r.data_rights_state
    with pytest.raises(ValueError):
        rights.RightsRecord("y", code_rights_state="not_a_state", data_rights_state="CLEAR",
                            output_redistribution_state="CLEAR")


def test_lab_matrix_consumes_centralized_rights_and_blocks_grudeva():
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named"))
    m = {r["component_id"]: r for r in lab.build_matrix(ex)}
    g = m["grudeva2025.reduced"]
    assert g["rights_state"] == "RIGHTS_BLOCKED" == g["code_rights_state"]
    assert g["disposition"] == "RIGHTS_BLOCKED"
    assert g["native_runner_state"] == "RIGHTS_BLOCKED"
    assert g["common_scenario_adapter_state"] == "RIGHTS_BLOCKED"
    # non-reviewed components read NOT_REVIEWED (not the old over-claimed "clear")
    assert m["cameron2020.extraction_bdf"]["rights_state"] == "NOT_REVIEWED"
    # the product-local rights dictionary is gone
    assert not hasattr(lab, "_RIGHTS_BLOCKED")


def test_native_runners_cannot_register_a_rights_blocked_component():
    assert "grudeva2025.reduced" not in lab_runners.RUNNERS
    lab_runners._assert_no_rights_blocked_runners()          # passes today
    # a rights-blocked runner registration fails loudly
    monkeyed = dict(lab_runners.RUNNERS)
    monkeyed["grudeva2025.reduced"] = (lab_runners.RunnerSpec("x", "1", "grudeva2025.reduced",
                                                              "interactive-fast"), lambda: {})
    import unittest.mock as mock
    with mock.patch.object(lab_runners, "RUNNERS", monkeyed):
        with pytest.raises(RuntimeError):
            lab_runners._assert_no_rights_blocked_runners()


def test_readme_governance_rejects_executable_label_for_rights_blocked(tmp_path, monkeypatch):
    import importlib
    rg = importlib.import_module("tools.readme_governance")
    bad = ("| Extraction | `grudeva2025.reduced` | Executable model (separate) | ... |\n"
           "text with the LIVE interactives and env markers so only the rights check trips")
    monkeypatch.setattr(rg, "README", tmp_path / "R.md")
    (tmp_path / "R.md").write_text(bad, encoding="utf-8")
    problems = rg.check_readme(components=list(puckworks.components()))
    assert any("rights-blocked" in p and "grudeva2025.reduced" in p for p in problems)


def test_release_readiness_flags_blocked_component_in_the_package():
    from puckworks import release
    problems = release.rights_release_problems(_ROOT)
    assert any("grudeva2025.reduced" in p and "#73" in p for p in problems)


def test_release_main_blocks_on_rights_without_building(monkeypatch):
    import unittest.mock as mock

    from puckworks import release
    built = {"called": False}
    monkeypatch.setattr(release, "build", lambda *a, **k: built.__setitem__("called", True))
    monkeypatch.setattr(release, "twine_check", lambda *a, **k: None)
    monkeypatch.setattr(release, "release_manifest", lambda *a, **k: {})
    rc = release.main(["build"])
    assert rc == 2 and built["called"] is False        # blocked before build, no artifact produced
    # the authorized-removal override path still builds
    with mock.patch.object(release, "rights_release_problems", return_value=[]):
        built["called"] = False
        monkeypatch.setattr(release, "release_manifest", lambda *a, **k: {"commit": "x", "dirty": False,
                                                                          "python": "3", "artifacts": {}})
        monkeypatch.setattr("pathlib.Path.write_text", lambda *a, **k: None)
        assert release.main(["build"]) == 0


def test_v030_history_and_model_numerics_untouched():
    # the component is still registered and gated (no deregistration; numerics unchanged)
    comp = next(c for c in puckworks.components() if c.name == "grudeva2025.reduced")
    assert comp.execution_role == "runtime" and len(comp.gates) == 2
    # the v0.3.0 tag content is only present in a full checkout (CI quick lanes are shallow); when it
    # is available, confirm history was NOT rewritten (the tag tree carries no session rights banner).
    have_tag = subprocess.run(["git", "-C", str(_ROOT), "cat-file", "-e", "v0.3.0^{}"],
                              capture_output=True).returncode == 0
    if not have_tag:
        pytest.skip("v0.3.0 tag content not present in this (shallow) checkout")
    old = subprocess.check_output(
        ["git", "-C", str(_ROOT), "show", "v0.3.0^{}:puckworks/models/grudeva2025/reduced.py"],
        text=True)
    assert "RIGHTS STATUS" not in old
    peel = subprocess.check_output(["git", "-C", str(_ROOT), "rev-parse", "v0.3.0^{}"], text=True).strip()
    assert peel == "c5ab770b76ea2fb876c348ca48d802d604c112ca"


def test_grudeva2025_still_imports_and_runs_its_gate():
    # the module still imports and its no-eps kappa gate still passes (numerics unchanged by the banner)
    from puckworks.validation import gates as G
    assert G.gate_grudeva_no_eps_kappa()["passed"] is True
