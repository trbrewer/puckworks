"""Strictly-truthful component execution accounting for the Espresso Model Relay (§7, §15.2).

A component is 'executed' only when an authoritative callable it owns actually ran. Pannusch's registered
solver is not counted unless the solver runs; fast-mode LB is 'not selected', not a missing dependency;
Taichi is never represented by a reference-solver call; grudeva gets zero calls.
"""
import pytest

from puckworks.product.linked_pull import RelayRequest, execute_illustrative_linked_pull

# Frozen expected fast-mode reference-run sets (derived from the audited reference result). A drift here
# is a real accounting change that must be reviewed, not silently accepted.
EXPECTED_FAST_AUTHORITATIVE_EXECUTIONS = frozenset({
    "wadsworth2026.grindmap", "wadsworth2026.permeability", "brewer2026.pack_generator",
    "foster2025.machine_mode", "foster2025.infiltration", "wadsworth2026.inertial",
    "sourcing2026.g10_liquor_rheology", "cameron2020.extraction_bdf", "waszkiewicz2025.poroelastic",
    "brewer2026.coupled_kappa_t", "mo2023_2.swelling", "fasano2000_partI.fines_migration",
    "brewer2026.streamtube", "pannusch2024.closures", "romancorrochano2017.extraction",
    "moroney2016.surrogate", "mo2023_2.coupled_bed", "liang2021.desorption",
})
EXPECTED_FAST_NOT_SELECTED = frozenset({
    "pannusch2024.solver", "brewer2026.lb_reference", "brewer2026.lb_taichi",
})
EXPECTED_FAST_REFERENCE_ONLY = frozenset({
    "sourcing2026.g3_pump_characteristic", "sourcing2026.g1_glassbead_analog", "lee2023.feedback",
})
EXPECTED_FAST_RIGHTS_BLOCKED = frozenset({"grudeva2025.reduced"})
EXPECTED_FAST_EXECUTED_COUNT = 18
EXPECTED_FAST_HANDOFF_COUNT = 10


@pytest.fixture(scope="module")
def result():
    return execute_illustrative_linked_pull(RelayRequest(mode="fast"))


def _by_status(result, statuses):
    return frozenset(s["component_id"] for s in result["stages"]
                     if s["status"] in statuses and s["component_id"] != "recipe")


def test_exact_authoritative_execution_set(result):
    got = _by_status(result, {"EXECUTED", "EXECUTED_WITH_ASSUMPTIONS", "ADAPTED_SCENARIO"})
    assert got == EXPECTED_FAST_AUTHORITATIVE_EXECUTIONS
    assert len(got) == EXPECTED_FAST_EXECUTED_COUNT


def test_exact_not_selected_set(result):
    assert _by_status(result, {"NOT_SELECTED"}) == EXPECTED_FAST_NOT_SELECTED


def test_exact_reference_only_and_rights_blocked_sets(result):
    assert _by_status(result, {"REFERENCE_ONLY"}) == EXPECTED_FAST_REFERENCE_ONLY
    assert _by_status(result, {"RIGHTS_BLOCKED"}) == EXPECTED_FAST_RIGHTS_BLOCKED


def test_counts_match_the_audited_reference(result):
    c = result["counts"]
    assert c["components_executed"] == EXPECTED_FAST_EXECUTED_COUNT
    assert c["cross_component_handoffs"] == EXPECTED_FAST_HANDOFF_COUNT


def test_pannusch_solver_not_counted_without_solver_execution(result):
    solver = next(s for s in result["stages"] if s["component_id"] == "pannusch2024.solver")
    assert solver["status"] == "NOT_SELECTED"
    # the release-clock diagnostic is owned by the CLOSURES, which did execute
    closures = next(s for s in result["stages"] if s["component_id"] == "pannusch2024.closures")
    assert closures["status"] == "EXECUTED"
    assert any("release_timescale" in o["name"] for o in closures["outputs"])


def test_fast_mode_lb_is_not_selected_not_a_missing_dependency(result):
    for cid in ("brewer2026.lb_reference", "brewer2026.lb_taichi"):
        s = next(x for x in result["stages"] if x["component_id"] == cid)
        assert s["status"] == "NOT_SELECTED"                 # a slow optional path, deliberately not run
        assert "OPTIONAL_DEPENDENCY_UNAVAILABLE" != s["status"]


def test_no_executed_with_assumptions_lacks_assumption_ids(result):
    for s in result["stages"]:
        if s["status"] == "EXECUTED_WITH_ASSUMPTIONS":
            assert s["assumption_ids"], f"{s['component_id']} claims assumptions but records none"


def test_grudeva_zero_calls_still_holds(result):
    g = next(s for s in result["stages"] if s["component_id"] == "grudeva2025.reduced")
    assert g["status"] == "RIGHTS_BLOCKED" and not g["outputs"] and not g["inputs"]
    for link in result["links"]:
        assert "grudeva2025.reduced" not in (link["source_component_id"], link["target_component_id"])


@pytest.mark.slow
def test_extended_mode_runs_lb_reference_once_and_taichi_is_honest():
    r = execute_illustrative_linked_pull(RelayRequest(mode="extended"))
    lb = next(s for s in r["stages"] if s["component_id"] == "brewer2026.lb_reference")
    assert lb["status"] in ("EXECUTED", "EXECUTED_WITH_ASSUMPTIONS")
    taichi = next(s for s in r["stages"] if s["component_id"] == "brewer2026.lb_taichi")
    # Taichi is never represented by the reference solve: without the wired backend it is unavailable
    assert taichi["status"] in ("OPTIONAL_DEPENDENCY_UNAVAILABLE", "EXECUTED", "EXECUTED_WITH_ASSUMPTIONS")
    if taichi["status"].startswith("EXECUTED"):
        assert any("backend" in o["name"].lower() or "taichi" in str(o.get("basis", "")).lower()
                   for o in taichi["outputs"])
