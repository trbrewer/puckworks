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
"""
import pytest

# CLEAN, import-order-invariant baseline (pv19_named, LOCAL_PRIVATE) after the streamtube C_S0 fix.
_BASELINE_TOUR_HASH = "1c1434ef1bfd930fefe37feab4b7841d161eea525fffef952c7ad4a2c8b3dddc"


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
