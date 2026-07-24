"""Regression: the Full Laboratory Tour's CLEAN-process result is stable and import-order invariant.

The frozen hash was corrected in the post-merge stabilization pass. The previous value
(``2054b04d…``) captured IMPORT-ORDER POLLUTION: importing ``brewer2026.streamtube`` used to mutate
``cameron2020.extraction_bdf.C_S0`` (118 -> 118/PHI_S = 142.65) as an import side effect, so the tour's
Cameron common-scenario and the liang/romancorrochano extraction lenses ran on streamtube's inflated
soluble ceiling — the tour reported Cameron EY = 17.06 % instead of Cameron's own declared value of
14.11 % (C_S0 = 118, extraction_bdf.py). That model-level defect is now fixed (streamtube passes its own
``c_s0`` into ``simulate_shot`` instead of mutating the global), so every tour component uses its intended
basis and the result is byte-identical regardless of import order. The new hash is the CLEAN, intended,
import-order-invariant value — not a concealment of the change (see stabilization changelog).

**2026-07-23 baseline update (1c1434ef… -> 1b5e4505…): added gates, NOT changed model numerics.**
The tour runs many components via SCIENTIFIC_CHECK, whose per-component ``scientific_hash`` covers the
``gate_metric`` outputs. A per-component diff of the tour result (baseline commit 608a203 vs HEAD) shows
NO component added/removed and EXACTLY TWO per-component hashes changed — ``moroney2016.surrogate`` and
``sourcing2026.g10_liquor_rheology`` — both still SCIENTIFIC_CHECK/EXECUTED, only their gate-metric hash.
Every other component (incl. the Cameron common-scenario and all extraction lenses) is byte-identical, so
no model numerics moved. Those two components each gained validation gates this session
(moroney2016.surrogate: the moroney2015/2019 solver + kappa-anchor gates; sourcing2026.g10: the sobolik
density + closures + four-source + gagne gates), which is why their gate-metric payload — and thus the
tour hash — changed. Legitimate, intended drift; the models are unchanged. (This slow test is not in the
quick CI lane, which is why the earlier gate PRs didn't flag the drift — worth wiring into CI separately.)
"""
import pytest

# CLEAN, import-order-invariant baseline (pv19_named, LOCAL_PRIVATE): streamtube C_S0 fix + the
# 2026-07-23 SCIENTIFIC_CHECK gate additions to moroney2016.surrogate / sourcing2026.g10 (see above).
_BASELINE_TOUR_HASH = "1b5e45052afca29d63e36416deeecde9a6d4f98f5dc14846832306673080f802"


def test_tour_manifest_unchanged():
    from puckworks.product import lab_tour
    assert lab_tour.FULL_LABORATORY_TOUR_V1 == "full_laboratory_tour_v1"
    assert lab_tour.verify_tour_manifest() == []


@pytest.mark.slow
def test_frozen_reference_request_reproduces_the_baseline_scientific_hash():
    from puckworks.product import lab, lab_tour
    t = lab_tour.execute_laboratory_tour(lab.ScenarioRequest("pv19_named"),
                                         execution_context="LOCAL_PRIVATE").to_dict()
    assert t["tour_scientific_hash"] == _BASELINE_TOUR_HASH


def test_full_tour_does_not_import_or_run_the_relay():
    import inspect

    from puckworks.product import lab_tour, lab_tour_insights
    for mod in (lab_tour, lab_tour_insights):
        src = inspect.getsource(mod)
        assert "linked_pull" not in src, f"{mod.__name__} must not reference the relay"
