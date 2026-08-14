"""Centralized component-rights registry + the Grudeva permission determination (issue #73).

Offline + deterministic. Verifies one authoritative rights record per registered component (NOT_REVIEWED
fallback, never a silent CLEAR), that code/data/output rights are distinct, that the Grudeva record is
exactly PERMISSION_DOCUMENTED on the 2026-08-14 direct written permission (with public-safe metadata and
no private evidence), that the GENERIC rights rules still refuse a rights-blocked component everywhere
(Lab / runners / adapters / README governance / release guard), and that v0.3.0 history + model numerics
are untouched.
"""
import json
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


def test_grudeva_states_are_exactly_permission_documented():
    # #73 resolved 2026-08-14 by DIRECT WRITTEN PERMISSION covering code AND data. PERMISSION_DOCUMENTED,
    # never CLEAR: permission is on record, a formal licence is not.
    g = rights.rights_record("grudeva2025.reduced")
    assert g.code_rights_state == "PERMISSION_DOCUMENTED"
    assert g.data_rights_state == "PERMISSION_DOCUMENTED"
    assert g.output_redistribution_state == "PERMISSION_DOCUMENTED"
    assert "CLEAR" not in (g.code_rights_state, g.data_rights_state, g.output_redistribution_state)
    assert g.decision_issue == "#73" and g.review_date == "2026-08-14"
    # the article's CC-BY is still tracked separately and is NOT the recorded basis
    assert "cc-by" in g.rights_note.lower() and "not" in g.rights_note.lower()
    # no component is rights-blocked today; the blocked-set machinery still exists
    assert rights.blocked_components() == []


def test_grudeva_permission_metadata_is_complete_and_public_safe():
    p = rights.rights_record("grudeva2025.reduced").permission
    assert p, "PERMISSION_DOCUMENTED requires permission metadata"
    blob = json.dumps(rights.rights_record("grudeva2025.reduced").to_dict()).lower()
    for needed in ("dr. yoana grudeva", "2026-08-14", "linkedin direct message"):
        assert needed in blob, needed
    assert p["grantor"] == "Dr. Yoana Grudeva"
    assert p["permission_date"] == "2026-08-14"
    assert p["channel"] == "LinkedIn direct message"
    # scope covers BOTH code and data
    assert "code" in p["scope"].lower() and "data" in p["scope"].lower()
    # the evidence is private and stays private
    assert "privately" in p["evidence_status"].lower() or "private" in p["evidence_status"].lower()
    # NO formal licence was supplied
    assert p["spdx_identifier"] is None
    assert "none supplied" in p["formal_license"].lower()
    assert p["public_record"] == "docs/permissions/grudeva2025.md"
    # public metadata carries no email address, screenshot path, or attachment reference
    assert "@" not in blob, "no email address may appear in public permission metadata"
    for leak in (".png", ".jpg", ".jpeg", ".pdf", "screenshot", "attachment", "mailto"):
        assert leak not in blob, leak


def test_grudeva_permission_record_and_notices_agree_with_the_registry():
    p = rights.rights_record("grudeva2025.reduced").permission
    rec = (_ROOT / p["public_record"]).read_text(encoding="utf-8")
    notices = (_ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for text, label in ((rec, "permission record"), (notices, "third-party notices")):
        assert "Dr. Yoana Grudeva" in text, label
        assert "2026-08-14" in text, label
        assert "LinkedIn" in text, label
        low = text.lower()
        assert "no formal" in low or "none supplied" in low, label          # no SPDX licence claimed
        assert "@" not in text, f"{label} must carry no email address"
    # the notices must not claim MIT/CC-BY/public-domain/open-source status for the upstream material
    assert "not** MIT" in notices or "**not** MIT" in notices
    # the article/thesis CC-BY provenance stays visible and separate
    assert "CC-BY" in notices and "grudeva_params.csv" in notices


def test_article_and_code_rights_cannot_be_conflated():
    # a record with a CC-BY article does not make its solver code CLEAR (reviewed => needs source+date;
    # RIGHTS_BLOCKED => needs decision_issue + reason)
    r = rights.RightsRecord("x", code_rights_state="RIGHTS_BLOCKED", data_rights_state="CLEAR",
                            output_redistribution_state="RIGHTS_BLOCKED", rights_note="blocked port",
                            source="module header", decision_issue="#73", review_date="2026-07-19")
    assert r.is_code_blocked and not r.code_rights_state == r.data_rights_state
    with pytest.raises(ValueError):                      # unknown/lowercase vocabulary rejected
        rights.RightsRecord("y", code_rights_state="not_a_state", data_rights_state="CLEAR",
                            output_redistribution_state="CLEAR")


def test_lab_matrix_consumes_centralized_rights_and_grudeva_is_no_longer_blocked():
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named"))
    m = {r["component_id"]: r for r in lab.build_matrix(ex)}
    g = m["grudeva2025.reduced"]
    assert g["rights_state"] == "PERMISSION_DOCUMENTED" == g["code_rights_state"]
    # the remaining limit is TECHNICAL, stated in the repo's own vocabulary — never RIGHTS_BLOCKED
    assert g["disposition"] == "ADAPTER_REQUIRED"
    assert g["common_scenario_adapter_state"] == "ADAPTER_REQUIRED"
    assert g["native_runner_state"] == "NOT_IMPLEMENTED"          # no runner was invented
    for field in ("disposition", "native_runner_state", "common_scenario_adapter_state", "rights_state"):
        assert g[field] != "RIGHTS_BLOCKED"
    # non-reviewed components read NOT_REVIEWED (not the old over-claimed "clear")
    assert m["cameron2020.extraction_bdf"]["rights_state"] == "NOT_REVIEWED"
    # the product-local rights dictionary is gone
    assert not hasattr(lab, "_RIGHTS_BLOCKED")


def test_native_runners_cannot_register_a_rights_blocked_component():
    # no runner was invented for Grudeva by the permission correction
    assert "grudeva2025.reduced" not in lab_runners.RUNNERS
    lab_runners._assert_no_rights_blocked_runners()          # passes today
    # the GENERIC guard still fires: a rights-blocked runner registration fails loudly
    import unittest.mock as mock
    blocked_id = "cameron2020.extraction_bdf"
    blocked_rec = rights.RightsRecord(blocked_id, "RIGHTS_BLOCKED", "NOT_REVIEWED", "RIGHTS_BLOCKED",
                                      rights_note="synthetic block for this test", source="test",
                                      decision_issue="#0", review_date="2026-08-14")
    monkeyed = dict(lab_runners.RUNNERS)
    monkeyed[blocked_id] = (lab_runners.RunnerSpec("x", "1", blocked_id, "interactive-fast"), lambda: {})
    with mock.patch.object(lab_runners, "RUNNERS", monkeyed), \
            mock.patch.dict(rights._RECORDS, {blocked_id: blocked_rec}):
        with pytest.raises(RuntimeError):
            lab_runners._assert_no_rights_blocked_runners()


def test_readme_governance_rejects_executable_label_for_rights_blocked(tmp_path, monkeypatch):
    # the GENERIC rule is unchanged; Grudeva is no longer blocked, so a still-blocked component is
    # synthesized to exercise it (the rule must never become vacuous).
    import importlib
    import unittest.mock as mock
    rg = importlib.import_module("tools.readme_governance")
    blocked_id = "cameron2020.extraction_bdf"
    bad = (f"| Extraction | `{blocked_id}` | Executable model (separate) | ... |\n"
           "text with the LIVE interactives and env markers so only the rights check trips")
    monkeypatch.setattr(rg, "README", tmp_path / "R.md")
    (tmp_path / "R.md").write_text(bad, encoding="utf-8")
    with mock.patch.object(rights, "blocked_components", return_value=[blocked_id]):
        problems = rg.check_readme(components=list(puckworks.components()))
    assert any("rights-blocked" in p and blocked_id in p for p in problems)


def test_live_readme_governance_is_clean_for_grudeva():
    # the real README: Grudeva is no longer rights-blocked, so no rights-label problem is raised for it
    # (the whole-file governance run is a separate validation command).
    import importlib
    rg = importlib.import_module("tools.readme_governance")
    problems = rg.check_readme(components=list(puckworks.components()))
    assert not any("rights-blocked" in p and "grudeva2025.reduced" in p for p in problems)


def test_release_readiness_no_longer_flags_grudeva_and_still_flags_a_blocked_component():
    import unittest.mock as mock

    from puckworks import release
    assert release.rights_release_problems(_ROOT) == []
    # the guard itself is intact: a genuinely blocked, packaged component is still flagged
    blocked_id = "cameron2020.extraction_bdf"
    blocked_rec = rights.RightsRecord(blocked_id, "RIGHTS_BLOCKED", "NOT_REVIEWED", "RIGHTS_BLOCKED",
                                      rights_note="synthetic block for this test", source="test",
                                      decision_issue="#0", review_date="2026-08-14")
    with mock.patch.dict(rights._RECORDS, {blocked_id: blocked_rec}):
        problems = release.rights_release_problems(_ROOT)
    assert any(blocked_id in p for p in problems)


def test_release_main_blocks_on_rights_without_building(monkeypatch):
    import unittest.mock as mock

    from puckworks import release
    from pathlib import Path
    built = {"called": False}
    def _fake_build(*a, **k):                       # build() now returns {'wheel','sdist'} paths
        built["called"] = True
        return {"wheel": Path("w.whl"), "sdist": Path("s.tar.gz")}
    monkeypatch.setattr(release, "build", _fake_build)
    monkeypatch.setattr(release, "twine_check", lambda *a, **k: None)
    monkeypatch.setattr(release, "release_manifest", lambda *a, **k: {})
    # a code-rights-blocked component still hard-blocks the build before any artifact is produced
    with mock.patch.object(release, "rights_release_problems",
                           return_value=["code-rights-blocked component 'x' would enter the release"]):
        rc = release.main(["build"])
    assert rc == 2 and built["called"] is False        # blocked before build, no artifact produced
    # with no blocked component (the state today, Grudeva included) the build proceeds
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


def test_grudeva2025_gate_results_are_numerically_unchanged():
    # the rights correction touched only the module DOCSTRING. Both registered gates must still pass
    # with the values recorded in ROADMAP §7.1 for 2026-07-11, unchanged.
    from puckworks.validation import gates as G
    g0 = G.gate_grudeva_no_eps_kappa()
    assert g0["passed"] is True
    assert g0["kappa_eq614"] == pytest.approx(2.2747487722826092e-15, rel=1e-9)
    assert g0["B"] == pytest.approx(0.5154, abs=5e-5)
    g1 = G.gate_grudeva_reduced_solver()
    assert g1["passed"] is True
    assert (g1["total_g"], g1["exp_total_g"]) == (2.92, 2.95)
    assert g1["vials_within_1sd"] == "9/13"
    assert g1["sd_inv_1"] == pytest.approx(2.8, abs=1e-9)


def test_grudeva_reduced_module_executable_lines_are_unchanged():
    """A rights edit may change the header docstring and NOTHING else in the model source."""
    import ast
    src = (_ROOT / "puckworks" / "models" / "grudeva2025" / "reduced.py").read_text(encoding="utf-8")
    old = subprocess.run(["git", "-C", str(_ROOT), "show", "origin/main:puckworks/models/grudeva2025/"
                          "reduced.py"], capture_output=True, text=True)
    if old.returncode != 0:
        pytest.skip("origin/main not available in this checkout")
    def _stripped(text):
        tree = ast.parse(text)
        tree.body = [n for n in tree.body]          # drop the module docstring only
        if (tree.body and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)):
            tree.body = tree.body[1:]
        return ast.dump(tree)
    assert _stripped(src) == _stripped(old.stdout), (
        "the executable body of reduced.py changed — a rights correction must not touch numerics")


def test_grudeva_csv_contents_are_unchanged():
    """No numerical data cell may move in a rights correction."""
    import hashlib
    for rel in ("puckworks/data/grudeva2025/exp13_per_vial_stats.csv",
                "puckworks/data/grudeva2025/grudeva_params.csv"):
        old = subprocess.run(["git", "-C", str(_ROOT), "show", f"origin/main:{rel}"],
                             capture_output=True)
        if old.returncode != 0:
            pytest.skip("origin/main not available in this checkout")
        now = (_ROOT / rel).read_bytes()
        assert hashlib.sha256(now).hexdigest() == hashlib.sha256(old.stdout).hexdigest(), rel


def test_the_rights_correction_promoted_no_scientific_label():
    comp = next(c for c in puckworks.components() if c.name == "grudeva2025.reduced")
    assert comp.evidence_strength == "post_fit_reconstruction"
    assert comp.provenance_class == "published_port"
    assert comp.execution_role == "runtime" and comp.kind == "runtime"
    card = (_ROOT / "docs" / "cards" / "grudeva2025.md").read_text(encoding="utf-8").lower()
    # the card must not claim the permission validated anything
    for overclaim in ("independently validated", "independently reproduced", "now validated",
                      "now gated", "permission validates"):
        assert overclaim not in card, overclaim
    # the card's own ceiling is intact
    assert "post-fit reconstruction" in card and "verification-gated" in card
    assert "upgrade to `gated + independent` blocked" in card


def test_pw_rgt_003_review_date_is_semantically_validated():
    # PW-RGT-003: a shape-only regex accepted impossible calendar dates.
    from puckworks.rights import RightsRecord
    for bad in ("2026-99-99", "2026-13-45", "2026-02-30", "2026-00-10", "not-a-date"):
        with pytest.raises(ValueError):
            RightsRecord("x", "NOT_REVIEWED", "NOT_REVIEWED", "NOT_REVIEWED", review_date=bad)
    # a real date is accepted
    RightsRecord("x", "NOT_REVIEWED", "NOT_REVIEWED", "NOT_REVIEWED", review_date="2026-02-28")


def test_pw_rgt_003_permission_is_deep_immutable_and_defends_caller_mutation():
    from puckworks.rights import RightsRecord
    src = {"grant": "email", "conditions": ["attribution"]}
    r = RightsRecord("x", "PERMISSION_DOCUMENTED", "NOT_REVIEWED", "NOT_REVIEWED",
                     rights_note="n", source="s", decision_issue="#1", review_date="2026-07-14",
                     permission=src)
    # mutating the caller's original dict cannot change the record
    src["grant"] = "TAMPERED"; src["conditions"].append("x")
    assert r.permission["grant"] == "email" and list(r.permission["conditions"]) == ["attribution"]
    # the record's own permission is read-only at top and nested levels
    with pytest.raises(TypeError):
        r.permission["grant"] = "y"
    # to_dict returns plain, JSON-serializable containers
    import json
    d = r.to_dict()
    assert isinstance(d["permission"], dict) and json.dumps(d)
