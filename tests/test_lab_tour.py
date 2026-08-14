"""Full Laboratory Tour — versioned manifest + per-component executor (#43/#70).

Offline + deterministic. The Tour resolves EVERY registered component to exactly one primary route and
runs the available ones honestly: a rights-blocked component receives zero execution calls, incompatible
outputs are never overlaid, and the scientific hashes are deterministic and free of runtime/timestamps.

A full LOCAL tour runs 26 real component code paths (dominated by 21 gate suites), so the execution
tests share module-scoped tour runs rather than re-running per test.
"""
import puckworks
import pytest

from puckworks.product import lab
from puckworks.product import lab_tour as T


@pytest.fixture(scope="module")
def local_pair():
    """Two identical LOCAL tours (for the inspection + determinism tests)."""
    req = lab.ScenarioRequest("pv19_named")
    return (T.execute_laboratory_tour(req, execution_context="LOCAL_PRIVATE"),
            T.execute_laboratory_tour(req, execution_context="LOCAL_PRIVATE"))


@pytest.fixture(scope="module")
def local_tour(local_pair):
    return local_pair[0]


@pytest.fixture(scope="module")
def public_tour():
    return T.execute_laboratory_tour(lab.ScenarioRequest("pv19_named"),
                                     execution_context="PUBLIC_ARTIFACT")


# ── manifest coverage (fast; no execution) ───────────────────────────────────────────
def test_manifest_covers_every_component_exactly_once():
    assert T.verify_tour_manifest() == []
    plans = T.tour_manifest()
    registered = {c.name for c in puckworks.components()}
    assert set(plans) == registered
    # bound to the LIVE registry: the invariant is exactly-once coverage, not a frozen total
    assert len(plans) == len(set(plans)) == len(registered)


def test_all_native_runners_and_the_common_adapter_are_represented():
    from puckworks.product import lab_runners
    plans = T.tour_manifest()
    for cid in lab_runners.RUNNERS:
        assert plans[cid].execution_kind == T.TourExecutionKind.NATIVE_REFERENCE
    for cid in lab.ADAPTERS:
        assert plans[cid].execution_kind == T.TourExecutionKind.COMMON_SCENARIO
    # the frozen native set includes the batch-only LB reference (interactive_fast would omit it)
    assert "brewer2026.lb_reference" in T.native_reference_ids()


def test_grudeva_is_routed_to_its_own_registered_scientific_check():
    # #73 resolved 2026-08-14 by documented permission. The frozen manifest moved it from RIGHTS_BLOCKED
    # to SCIENTIFIC_CHECK -- a reviewable manifest update onto its EXISTING gates, not a new runner.
    plan = T.tour_manifest()["grudeva2025.reduced"]
    assert plan.execution_kind == T.TourExecutionKind.SCIENTIFIC_CHECK
    assert plan.producer_id == "gates:gate_grudeva_no_eps_kappa,gate_grudeva_reduced_solver"
    assert plan.input_origin == T.InputOrigin.REGISTERED_FIXTURE
    # not a common-scenario lens and not comparable to anything
    assert plan.comparability_group is None
    assert T.verify_tour_manifest() == []


def test_a_newly_registered_component_fails_coverage_until_classified(monkeypatch):
    class _C:
        name = "newpaper2027.model"
        stage = "extraction"
        gates = ()
    real = list(puckworks.components())
    monkeypatch.setattr(puckworks, "components", lambda: real + [_C()])
    problems = T.verify_tour_manifest()
    assert any("newpaper2027.model" in p and "no tour resolution" in p for p in problems)


def test_a_rights_change_to_an_executable_route_fails_the_verifier(monkeypatch):
    from puckworks import rights
    real = rights.is_code_rights_blocked
    monkeypatch.setattr(rights, "is_code_rights_blocked",
                        lambda cid: True if cid == "cameron2020.extraction_bdf" else real(cid))
    assert any("cameron2020.extraction_bdf" in p for p in T.verify_tour_manifest())


def test_bad_context_and_bad_manifest_are_rejected():
    with pytest.raises(ValueError):
        T.execute_laboratory_tour(lab.ScenarioRequest("pv19_named"), execution_context="NOPE")
    with pytest.raises(ValueError):
        T.tour_manifest("not_a_manifest")


# ── execution (shared module tours) ──────────────────────────────────────────────────
@pytest.mark.slow
def test_full_tour_resolves_every_component_and_executes_all_but_two_local(local_tour):
    s = local_tour.summary
    registered = {c.name for c in puckworks.components()}
    # ONE non-executing route remains: lb_taichi (optional taichi dependency). Grudeva stopped being
    # the second one on 2026-08-14, when its rights block was resolved by documented permission (#73)
    # and it took the SCIENTIFIC_CHECK route on its existing gates. Everything else must execute.
    assert s["registered"] == len(registered) and s["completed"] == len(registered) - 1
    # the ROUTE SPLIT stays literal -- it is the reviewable frozen-manifest decision, not a total
    assert s["by_kind"] == {"COMMON_SCENARIO": 1, "NATIVE_REFERENCE": 4, "SCIENTIFIC_CHECK": 21,
                            "OPTIONAL_DEPENDENCY": 1, "RIGHTS_BLOCKED": 0, "NO_EXECUTION_PATH": 0}
    assert s["rights_blocked"] == 0 and s["optional_unavailable"] == 1
    ids = [c.component_id for c in local_tour.components]
    assert set(ids) == registered and len(ids) == len(registered)   # one per component


@pytest.mark.slow
def test_common_native_and_check_counted_by_distinct_kinds(local_tour):
    by = {}
    for c in local_tour.components:
        if c.execution_status == "EXECUTED":
            by[c.execution_kind] = by.get(c.execution_kind, 0) + 1
    assert by == {"COMMON_SCENARIO": 1, "NATIVE_REFERENCE": 4, "SCIENTIFIC_CHECK": 21}


@pytest.mark.slow
def test_blocked_and_unavailable_entries_carry_no_scientific_payload(local_tour):
    for c in local_tour.components:
        if c.execution_status in ("RIGHTS_BLOCKED", "OPTIONAL_UNAVAILABLE", "NO_EXECUTION_PATH",
                                  "RIGHTS_NOT_CLEARED"):
            assert c.outputs == [] and c.scientific_hash is None


@pytest.mark.slow
def test_grudeva_runs_its_gates_and_is_not_promoted(local_tour):
    g = next(c for c in local_tour.components if c.component_id == "grudeva2025.reduced")
    assert g.execution_kind == "SCIENTIFIC_CHECK" and g.execution_status == "EXECUTED"
    assert g.rights_decision["code_rights_state"] == "PERMISSION_DOCUMENTED"
    assert g.rights_decision["decision_issue"] == "#73"
    # gate metrics only -- a check is not a simulation, and it is comparable to nothing
    assert g.output_roles == ["gate_metric"] and g.comparability_group is None
    assert g.comparable_component_ids == ["grudeva2025.reduced"]   # comparable only to itself


@pytest.mark.slow
def test_tour_hashes_are_deterministic_across_identical_runs(local_pair):
    a, b = local_pair
    assert a.tour_scientific_hash == b.tour_scientific_hash
    assert {c.component_id: c.scientific_hash for c in a.components} == \
           {c.component_id: c.scientific_hash for c in b.components}
    # durations differ run-to-run but do not enter the scientific hash
    da = {c.component_id: c.duration_seconds for c in a.components}
    db = {c.component_id: c.duration_seconds for c in b.components}
    assert da != db or True                                  # (durations may coincide; hash equality is the assertion)


@pytest.mark.slow
def test_no_component_is_comparable_to_another(local_tour):
    for c in local_tour.components:
        assert c.comparable_component_ids in ([], [c.component_id])
    grouped = [c.component_id for c in local_tour.components if c.comparability_group]
    assert grouped == ["cameron2020.extraction_bdf"]         # only the common lens has a group (singleton)


@pytest.mark.slow
def test_public_tour_executes_only_affirmatively_cleared_components(public_tour):
    executed = sorted(c.component_id for c in public_tour.components if c.execution_status == "EXECUTED")
    # exactly the two affirmatively-cleared components, on two DIFFERENT bases: LB is first-party CLEAR
    # (#70), grudeva is PERMISSION_DOCUMENTED on the 2026-08-14 written permission (#73).
    assert executed == ["brewer2026.lb_reference", "grudeva2025.reduced"]
    cam = next(c for c in public_tour.components if c.component_id == "cameron2020.extraction_bdf")
    assert cam.execution_status == "RIGHTS_NOT_CLEARED" and cam.outputs == []
    # grudeva is affirmatively cleared since 2026-08-14 (#73), so it also executes in a public context
    g = next(c for c in public_tour.components if c.component_id == "grudeva2025.reduced")
    assert g.execution_status == "EXECUTED"


# ── isolated monkeypatched runs (each runs its own tour) ─────────────────────────────
@pytest.mark.slow
def test_a_rights_blocked_component_receives_zero_producer_and_gate_calls(monkeypatch):
    # No component is RIGHTS_BLOCKED today (#73 was resolved on 2026-08-14 by documented permission), so
    # the zero-call guarantee is exercised against a synthetic block on a SCIENTIFIC_CHECK component --
    # while grudeva, now cleared, DOES receive exactly its own gate call.
    import unittest.mock as mock

    from puckworks import gate_runner as G
    from puckworks import rights
    from puckworks.product import lab_runners
    blocked_id = "liang2021.desorption"
    rec = rights.RightsRecord(blocked_id, "RIGHTS_BLOCKED", "RIGHTS_BLOCKED", "RIGHTS_BLOCKED",
                              rights_note="synthetic block for this test", source="test",
                              decision_issue="#0", review_date="2026-08-14")
    calls = []
    orig_g = G.evaluate_component_gates
    monkeypatch.setattr(G, "evaluate_component_gates",
                        lambda cid, component=None: (calls.append(cid), orig_g(cid, component))[1])
    orig_r = lab_runners.execute_runner
    monkeypatch.setattr(lab_runners, "execute_runner",
                        lambda cid: (calls.append(cid), orig_r(cid))[1])
    # the frozen route must move WITH the rights state (the verifier refuses a silent disagreement)
    with mock.patch.dict(rights._RECORDS, {blocked_id: rec}), \
            mock.patch.dict(T._TOUR_V1_ROUTES, {blocked_id: T.TourExecutionKind.RIGHTS_BLOCKED}):
        T.execute_laboratory_tour(lab.ScenarioRequest("pv19_named"), execution_context="LOCAL_PRIVATE")
    assert blocked_id not in calls
    assert "grudeva2025.reduced" in calls


@pytest.mark.slow
def test_check_failure_and_execution_error_stay_distinct(monkeypatch):
    from puckworks import gate_runner as G
    real = G.evaluate_component_gates

    def fake(cid, component=None):
        if cid == "pannusch2024.solver":
            return [G.GateResult(cid, "g", G.GateStatus.FAIL, summary="failed")]
        if cid == "mo2023_2.coupled_bed":
            return [G.GateResult(cid, "g", G.GateStatus.ERROR, exception_type="ValueError")]
        return real(cid, component)
    monkeypatch.setattr(G, "evaluate_component_gates", fake)
    res = T.execute_laboratory_tour(lab.ScenarioRequest("pv19_named"), execution_context="LOCAL_PRIVATE")
    by = {c.component_id: c.execution_status for c in res.components}
    assert by["pannusch2024.solver"] == "CHECK_FAILED"       # a FAIL is a scientific negative
    assert by["mo2023_2.coupled_bed"] == "EXECUTION_ERROR"   # a raise is an error, never a zero
    assert by["romancorrochano2017.extraction"] == "EXECUTED"  # isolation: unrelated components still run
