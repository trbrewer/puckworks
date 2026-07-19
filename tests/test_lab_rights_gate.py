"""Rights preflight at the public Laboratory boundary (Phase 2, #73).

Offline + deterministic. Public execution and public output publication must be rights-gated BEFORE any
producer runs. These tests prove the finite execution-context vocabulary, that public contexts consult
affirmative code/output clearance while local contexts follow may_execute_locally, that a blocked public
request invokes ZERO scientific producers and emits only a rights decision (no scientific output), that
local and public contexts cannot be confused, that an unknown component fails distinctly, and that
Grudeva stays blocked with no generic bypass.
"""
import importlib
import json

import pytest

import puckworks.product as prod
from puckworks.product import lab
from puckworks.product import lab_rights_gate as gate


def _req(**kw):
    kw.setdefault("reference_selection_policy", "none")
    return lab.ScenarioRequest("pv19_named", **kw)


# ── context vocabulary + preflight verdicts ─────────────────────────────────────────
def test_context_vocabulary_is_finite():
    for ctx in gate.EXECUTION_CONTEXTS:
        assert gate.preflight(_req(), ctx)["context"] == ctx
    with pytest.raises(ValueError):
        gate.preflight(_req(), "SOMETHING_ELSE")


def test_local_contexts_run_cameron_but_public_contexts_block_not_reviewed():
    assert gate.preflight(_req(), "LOCAL_PRIVATE")["blocked"] is False
    assert gate.preflight(_req(), "CI_VERIFICATION_NO_PUBLISH")["blocked"] is False
    for ctx in ("PUBLIC_BATCH", "PUBLIC_ARTIFACT"):
        v = gate.preflight(_req(), ctx)
        assert v["blocked"] is True
        row = {r["component_id"]: r for r in v["requested"]}["cameron2020.extraction_bdf"]
        assert row["code_rights_state"] == "NOT_REVIEWED" and row["blocked"] is True


def test_public_artifact_additionally_requires_output_clearance():
    # PUBLIC_BATCH checks code; PUBLIC_ARTIFACT additionally requires output publication clearance
    batch_rows = {r["component_id"]: r for r in gate.preflight(_req(), "PUBLIC_BATCH")["requested"]}
    art_rows = {r["component_id"]: r for r in gate.preflight(_req(), "PUBLIC_ARTIFACT")["requested"]}
    assert batch_rows["cameron2020.extraction_bdf"]["output_publication_required"] is False
    assert art_rows["cameron2020.extraction_bdf"]["output_publication_required"] is True


def test_grudeva_stays_blocked_even_locally():
    v = gate.preflight(lab.ScenarioRequest(
        "pv19_named", lens_selection_policy="selected", requested_lens_ids=("grudeva2025.reduced",),
        reference_selection_policy="none"), "LOCAL_PRIVATE")
    assert v["blocked"] is True
    row = {r["component_id"]: r for r in v["requested"]}["grudeva2025.reduced"]
    assert row["code_rights_state"] == "RIGHTS_BLOCKED"


def test_unknown_component_fails_distinctly():
    v = gate.preflight(lab.ScenarioRequest(
        "pv19_named", reference_selection_policy="selected",
        requested_reference_runner_ids=("not.a.component",)), "PUBLIC_ARTIFACT")
    assert v["blocked"] is True
    assert any(r.get("unknown") and "unknown reference id" in r["blocker"] for r in v["requested"])


def test_native_reference_outputs_are_not_cleared_for_public_publication():
    # the native runners are NOT_REVIEWED -> their outputs cannot be published in a PUBLIC_ARTIFACT
    v = gate.preflight(lab.ScenarioRequest("pv19_named"), "PUBLIC_ARTIFACT")   # default interactive_fast
    ref_rows = [r for r in v["requested"] if r.get("use_kind") == "native_reference"]
    assert ref_rows and all(r["blocked"] for r in ref_rows)


# ── the batch enforces the gate before any producer ─────────────────────────────────
@pytest.fixture
def count_producer(monkeypatch):
    calls = {"n": 0}
    real = prod.simulate_pull
    monkeypatch.setattr(prod, "simulate_pull", lambda *a, **k: calls.__setitem__("n", calls["n"] + 1)
                        or real(*a, **k))
    return calls


def test_public_batch_block_invokes_zero_producers(tmp_path, count_producer):
    lb = importlib.import_module("tools.lab_batch")
    final = tmp_path / "out"
    with pytest.raises(RuntimeError, match="rights preflight blocked"):
        lb.run({"LAB_OUT_DIR": str(final), "LAB_EXECUTION_CONTEXT": "PUBLIC_ARTIFACT",
                "LAB_REFERENCE_SELECTION_POLICY": "none"})
    assert count_producer["n"] == 0                              # NO scientific producer ran
    assert not final.exists()                                   # no scientific output directory


def test_blocked_preflight_file_contains_no_scientific_output(tmp_path):
    lb = importlib.import_module("tools.lab_batch")
    final = tmp_path / "out"
    with pytest.raises(RuntimeError):
        lb.run({"LAB_OUT_DIR": str(final), "LAB_EXECUTION_CONTEXT": "PUBLIC_ARTIFACT",
                "LAB_REFERENCE_SELECTION_POLICY": "none"})
    pf = tmp_path / "out.rights_preflight.json"
    assert pf.exists()
    v = json.loads(pf.read_text())
    blob = json.dumps(v)
    assert v["report"] == "puckworks-lab-rights-preflight"
    for forbidden in ("executed_lenses", "scientific_payload_sha256", "observables", "traces"):
        assert forbidden not in blob                            # rights decision only, no science


def test_local_context_still_runs_the_batch(tmp_path, count_producer):
    pytest.importorskip("matplotlib")
    lb = importlib.import_module("tools.lab_batch")
    final = tmp_path / "out"
    lb.run({"LAB_OUT_DIR": str(final), "LAB_EXECUTION_CONTEXT": "LOCAL_PRIVATE",
            "LAB_REFERENCE_SELECTION_POLICY": "none"})
    assert (final / "guided_pull_lab.json").exists() and count_producer["n"] >= 1


def test_default_context_is_local_and_permits_execution(tmp_path, count_producer):
    pytest.importorskip("matplotlib")
    lb = importlib.import_module("tools.lab_batch")
    final = tmp_path / "out"
    lb.run({"LAB_OUT_DIR": str(final), "LAB_REFERENCE_SELECTION_POLICY": "none"})   # no context env
    assert (final / "guided_pull_lab.json").exists()


def test_no_generic_bypass_of_the_public_gate():
    src = open(gate.__file__).read()
    assert "allow" not in src.lower().replace("allowed", "") or "bypass" not in src.lower()
    # the public path has no boolean override; the only way to pass is affirmative clearance
    v = gate.preflight(_req(), "PUBLIC_ARTIFACT")
    assert v["blocked"] is True
