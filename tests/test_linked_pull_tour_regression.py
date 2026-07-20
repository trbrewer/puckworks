"""Regression: the Espresso Model Relay must NOT change the Full Laboratory Tour (separate product)."""
import pytest

# frozen baseline captured before the relay landed (pv19_named, LOCAL_PRIVATE)
_BASELINE_TOUR_HASH = "2054b04d651bb440bbe56de26de6bc95014ed021512b9e88860365b02fd785d1"


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
