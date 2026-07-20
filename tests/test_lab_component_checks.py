"""Rights-aware, Laboratory-facing component-check runner (#43/#70).

Offline + deterministic. `run_component_checks` runs SELECTED components' registered gate(s) with rights
resolved FIRST — a rights-blocked component receives zero gate calls — reuses the authoritative
gate_runner (no copied thresholds), isolates failures per-component, and keeps FAIL / ERROR / BLOCKED /
NOT_CLEARED / NO-GATE / NOT-SELECTED distinct.
"""
import pytest

from puckworks.product import lab_component_checks as CC

# fast single-gate check components (avoid the 6-7 gate ones in loops)
FAST = ["brewer2026.streamtube", "brewer2026.pack_generator", "moroney2016.surrogate"]


def test_explicit_context_is_required():
    with pytest.raises(ValueError):
        CC.run_component_checks(FAST, execution_context="NOPE")


def test_local_private_runs_not_reviewed_components():
    res = CC.run_component_checks(FAST, execution_context="LOCAL_PRIVATE")
    assert [r.component_id for r in res] == sorted(FAST)
    for r in res:
        assert r.execution_status == "EXECUTED" and r.gates and r.scientific_hash
        assert r.rights_state == "NOT_REVIEWED"             # inspectable locally under existing policy
        assert "not experimental validation" in r.fidelity_ceiling.lower()   # never called a full simulation


def test_rights_blocked_component_gets_zero_gate_calls(monkeypatch):
    from puckworks import gate_runner as G
    calls = []
    orig = G.evaluate_component_gates
    monkeypatch.setattr(G, "evaluate_component_gates",
                        lambda cid, component=None: (calls.append(cid), orig(cid, component))[1])
    r = CC.run_component_checks(["grudeva2025.reduced"], execution_context="LOCAL_PRIVATE")[0]
    assert r.execution_status == "RIGHTS_BLOCKED"
    assert "grudeva2025.reduced" not in calls               # gates NEVER evaluated for a blocked component
    assert r.gates == [] and r.scientific_hash is None and r.blocker


def test_public_contexts_retain_affirmative_clearance():
    # a NOT_REVIEWED component is RIGHTS_NOT_CLEARED in a public context (no broadening), with zero science
    r = CC.run_component_checks(["brewer2026.streamtube"], execution_context="PUBLIC_ARTIFACT")[0]
    assert r.execution_status == "RIGHTS_NOT_CLEARED"
    assert r.gates == [] and r.scientific_hash is None
    # the affirmatively-cleared LB component clears public execution (but it is a native runner, not a
    # gate-only check — it still resolves cleanly here without a rights block)
    lb = CC.run_component_checks(["brewer2026.lb_reference"], execution_context="PUBLIC_ARTIFACT")[0]
    assert lb.execution_status in ("EXECUTED", "NO_GATE_ACKNOWLEDGED")


def test_unknown_id_fails_distinctly():
    with pytest.raises(ValueError, match="unknown component id"):
        CC.run_component_checks(["not.a.component"], execution_context="LOCAL_PRIVATE")


def test_check_failure_and_execution_error_are_distinct(monkeypatch):
    from puckworks import gate_runner as G
    real = G.evaluate_component_gates

    def fake(cid, component=None):
        if cid == "brewer2026.streamtube":
            return [G.GateResult(cid, "g", G.GateStatus.FAIL, summary="fail")]
        if cid == "brewer2026.pack_generator":
            return [G.GateResult(cid, "g", G.GateStatus.ERROR, exception_type="ValueError")]
        return real(cid, component)
    monkeypatch.setattr(G, "evaluate_component_gates", fake)
    res = {r.component_id: r for r in CC.run_component_checks(FAST, execution_context="LOCAL_PRIVATE")}
    assert res["brewer2026.streamtube"].execution_status == "CHECK_FAILED"       # a gate FAIL
    assert res["brewer2026.pack_generator"].execution_status == "EXECUTION_ERROR"  # a gate raise
    assert res["moroney2016.surrogate"].execution_status == "EXECUTED"           # isolation: others still run
    # a numerical error is an ERROR result, never a scientific zero
    assert res["brewer2026.pack_generator"].gates[0]["metrics"] == {}


def test_per_component_failure_isolation(monkeypatch):
    from puckworks import gate_runner as G
    real = G.evaluate_component_gates

    def boom(cid, component=None):
        if cid == "brewer2026.pack_generator":
            raise RuntimeError("boom")
        return real(cid, component)
    monkeypatch.setattr(G, "evaluate_component_gates", boom)
    res = {r.component_id: r for r in CC.run_component_checks(FAST, execution_context="LOCAL_PRIVATE")}
    assert res["brewer2026.pack_generator"].execution_status == "EXECUTION_ERROR"
    assert res["brewer2026.streamtube"].execution_status == "EXECUTED"           # unrelated component still ran


def test_deterministic_scientific_hash():
    a = CC.run_component_checks(["brewer2026.streamtube"], execution_context="LOCAL_PRIVATE")[0]
    b = CC.run_component_checks(["brewer2026.streamtube"], execution_context="LOCAL_PRIVATE")[0]
    assert a.scientific_hash == b.scientific_hash and a.scientific_hash is not None


def test_gate_output_carries_id_status_metrics_and_units():
    r = CC.run_component_checks(["brewer2026.lb_reference"], execution_context="LOCAL_PRIVATE")[0]
    # lb_reference has one gate (gate_lb_channel) reporting err_pct -> unit 'percent'
    assert r.gates and all({"gate_id", "status", "metrics", "units"} <= set(g) for g in r.gates)
    g = r.gates[0]
    assert g["gate_id"] == "gate_lb_channel" and "err_pct" in g["metrics"]
    assert g["units"].get("err_pct") == "percent"


def test_not_selected_is_reported_when_all_ids_given():
    res = {r.component_id: r for r in CC.run_component_checks(
        ["brewer2026.streamtube"], execution_context="LOCAL_PRIVATE",
        all_component_ids=["brewer2026.streamtube", "moroney2016.surrogate"])}
    assert res["brewer2026.streamtube"].execution_status == "EXECUTED"
    assert res["moroney2016.surrogate"].execution_status == "NOT_SELECTED"       # never silently dropped
    assert res["moroney2016.surrogate"].gates == [] and res["moroney2016.surrogate"].scientific_hash is None


def test_duplicate_ids_run_once():
    res = CC.run_component_checks(["brewer2026.streamtube", "brewer2026.streamtube"],
                                 execution_context="LOCAL_PRIVATE")
    assert [r.component_id for r in res] == ["brewer2026.streamtube"]


def test_lab_does_not_expose_unfiltered_evaluate_all_gates():
    # the Laboratory surface consumes the rights-aware runner, not an unfiltered evaluate_all_gates() CALL
    # (a docstring may mention it to explain the exclusion; a dotted/import call would be the violation)
    for mod in ("lab_tour", "lab_service", "lab_component_checks", "lab_explorer"):
        src = open(f"puckworks/product/{mod}.py").read()
        assert ".evaluate_all_gates(" not in src, f"{mod} calls the unfiltered evaluate_all_gates"
        assert "import evaluate_all_gates" not in src


def test_the_tour_delegates_check_routes_to_this_runner():
    src = open("puckworks/product/lab_tour.py").read()
    assert "lab_component_checks" in src and "run_component_checks" in src
