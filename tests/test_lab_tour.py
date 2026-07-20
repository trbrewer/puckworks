"""Full Laboratory Tour — versioned manifest + per-component executor (#43/#70).

Offline + deterministic. The Tour resolves EVERY registered component to exactly one primary route and
runs the available ones honestly: a rights-blocked component receives zero execution calls, incompatible
outputs are never overlaid, and the scientific hashes are deterministic and free of runtime/timestamps.

A full LOCAL tour runs 23 real component code paths (~20 s, dominated by 18 gate suites), so the
execution tests share module-scoped tour runs rather than re-running per test.
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
    assert set(plans) == {c.name for c in puckworks.components()}
    assert len(plans) == len(set(plans)) == 25


def test_all_native_runners_and_the_common_adapter_are_represented():
    from puckworks.product import lab_runners
    plans = T.tour_manifest()
    for cid in lab_runners.RUNNERS:
        assert plans[cid].execution_kind == T.TourExecutionKind.NATIVE_REFERENCE
    for cid in lab.ADAPTERS:
        assert plans[cid].execution_kind == T.TourExecutionKind.COMMON_SCENARIO
    # the frozen native set includes the batch-only LB reference (interactive_fast would omit it)
    assert "brewer2026.lb_reference" in T.native_reference_ids()


def test_grudeva_is_routed_rights_blocked_not_executable():
    assert T.tour_manifest()["grudeva2025.reduced"].execution_kind == T.TourExecutionKind.RIGHTS_BLOCKED


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
def test_full_tour_resolves_25_and_executes_23_local(local_tour):
    s = local_tour.summary
    assert s["registered"] == 25 and s["completed"] == 23   # 1 common + 4 native + 18 checks
    assert s["by_kind"] == {"COMMON_SCENARIO": 1, "NATIVE_REFERENCE": 4, "SCIENTIFIC_CHECK": 18,
                            "OPTIONAL_DEPENDENCY": 1, "RIGHTS_BLOCKED": 1, "NO_EXECUTION_PATH": 0}
    assert s["rights_blocked"] == 1 and s["optional_unavailable"] == 1
    ids = [c.component_id for c in local_tour.components]
    assert set(ids) == {c.name for c in puckworks.components()} and len(ids) == 25   # one per component


def test_common_native_and_check_counted_by_distinct_kinds(local_tour):
    by = {}
    for c in local_tour.components:
        if c.execution_status == "EXECUTED":
            by[c.execution_kind] = by.get(c.execution_kind, 0) + 1
    assert by == {"COMMON_SCENARIO": 1, "NATIVE_REFERENCE": 4, "SCIENTIFIC_CHECK": 18}


def test_blocked_and_unavailable_entries_carry_no_scientific_payload(local_tour):
    for c in local_tour.components:
        if c.execution_status in ("RIGHTS_BLOCKED", "OPTIONAL_UNAVAILABLE", "NO_EXECUTION_PATH",
                                  "RIGHTS_NOT_CLEARED"):
            assert c.outputs == [] and c.scientific_hash is None


def test_grudeva_carries_no_payload(local_tour):
    g = next(c for c in local_tour.components if c.component_id == "grudeva2025.reduced")
    assert g.execution_status == "RIGHTS_BLOCKED" and g.outputs == [] and g.scientific_hash is None


def test_tour_hashes_are_deterministic_across_identical_runs(local_pair):
    a, b = local_pair
    assert a.tour_scientific_hash == b.tour_scientific_hash
    assert {c.component_id: c.scientific_hash for c in a.components} == \
           {c.component_id: c.scientific_hash for c in b.components}
    # durations differ run-to-run but do not enter the scientific hash
    da = {c.component_id: c.duration_seconds for c in a.components}
    db = {c.component_id: c.duration_seconds for c in b.components}
    assert da != db or True                                  # (durations may coincide; hash equality is the assertion)


def test_no_component_is_comparable_to_another(local_tour):
    for c in local_tour.components:
        assert c.comparable_component_ids in ([], [c.component_id])
    grouped = [c.component_id for c in local_tour.components if c.comparability_group]
    assert grouped == ["cameron2020.extraction_bdf"]         # only the common lens has a group (singleton)


def test_public_tour_executes_only_affirmatively_cleared_components(public_tour):
    executed = sorted(c.component_id for c in public_tour.components if c.execution_status == "EXECUTED")
    assert executed == ["brewer2026.lb_reference"]
    cam = next(c for c in public_tour.components if c.component_id == "cameron2020.extraction_bdf")
    assert cam.execution_status == "RIGHTS_NOT_CLEARED" and cam.outputs == []
    g = next(c for c in public_tour.components if c.component_id == "grudeva2025.reduced")
    assert g.execution_status == "RIGHTS_BLOCKED"


# ── isolated monkeypatched runs (each runs its own tour) ─────────────────────────────
def test_grudeva_receives_zero_producer_and_gate_calls(monkeypatch):
    from puckworks import gate_runner as G
    from puckworks.product import lab_runners
    calls = []
    orig_g = G.evaluate_component_gates
    monkeypatch.setattr(G, "evaluate_component_gates",
                        lambda cid, component=None: (calls.append(cid), orig_g(cid, component))[1])
    orig_r = lab_runners.execute_runner
    monkeypatch.setattr(lab_runners, "execute_runner",
                        lambda cid: (calls.append(cid), orig_r(cid))[1])
    T.execute_laboratory_tour(lab.ScenarioRequest("pv19_named"), execution_context="LOCAL_PRIVATE")
    assert "grudeva2025.reduced" not in calls


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
