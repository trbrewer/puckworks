"""Educational insight figures for the Full Laboratory Tour (#43).

Offline. `component_figures` returns 0/1/many VizSpec-governed educational figures per component from real
authoritative producers, obeys the component's tour rights decision (no producer call for a non-executed
component), and never plots gate numbers. matplotlib is a viz extra, so the module is import-skipped where
it is absent.
"""
import pytest

pytest.importorskip("matplotlib")
import io  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from puckworks.product import lab_tour_insights as I  # noqa: E402

_SCEN = {"preset_id": "pv19_named", "overrides": {"pressure_bar": 9.0}, "domain_policy": "warn"}


def _result(cid, kind="NATIVE_REFERENCE", status="EXECUTED"):
    return {"component_id": cid, "stage": "flow", "execution_kind": kind, "execution_status": status,
            "outputs": [], "message": "ran"}


def _render_ok(figs):
    for f in figs:
        b = io.BytesIO(); f.figure.savefig(b, format="png"); plt.close(f.figure)
        assert b.getbuffer().nbytes > 1000


@pytest.mark.slow
def test_cameron_returns_three_educational_figures():
    figs = I.component_figures(_result("cameron2020.extraction_bdf", "COMMON_SCENARIO"),
                               scenario=_SCEN, execution_context="LOCAL_PRIVATE")
    assert len(figs) == 3
    assert {f.viz_spec_id for f in figs} == {"cameron_shot_timeseries", "cameron_pressure_sweep",
                                             "cameron_beverage_sweep"}
    for f in figs:
        assert f.question and f.caption and f.headline
        assert f.evidence_badge and f.evidence_strength and f.fidelity_ceiling and f.producer_ref
        assert f.varied_input and isinstance(f.fixed_inputs, dict)
        assert "cameron2020.extraction_bdf" not in f.headline    # public hook, not the raw id
    _render_ok(figs)


@pytest.mark.slow
def test_five_other_components_each_yield_a_figure():
    others = ["foster2025.infiltration", "brewer2026.lb_reference", "brewer2026.pack_generator",
              "fasano2000_partI.fines_migration", "brewer2026.streamtube"]
    for cid in others:
        figs = I.component_figures(_result(cid), scenario=_SCEN, execution_context="LOCAL_PRIVATE")
        assert len(figs) >= 1, cid
        _render_ok(figs)


def test_scientific_check_alone_yields_no_figure_with_a_reason():
    r = {"component_id": "romancorrochano2017.extraction", "stage": "extraction",
         "execution_kind": "SCIENTIFIC_CHECK", "execution_status": "EXECUTED",
         "outputs": [{"gate_id": "g", "status": "PASS", "metrics": {"ratio": 0.9}}]}
    assert I.component_figures(r, execution_context="LOCAL_PRIVATE") == []
    assert I.no_figure_reason(r) == "NO_DEFENSIBLE_PUBLIC_RELATIONSHIP_YET"


def test_blocked_and_optional_call_no_producer(monkeypatch):
    from puckworks.viz import producers as P
    calls = []
    for name in ("cameron_pressure_sweep", "wetting_front", "stokes_channel_field"):
        orig = getattr(P, name)
        monkeypatch.setattr(P, name, lambda *a, _n=name, _o=orig, **k: (calls.append(_n), _o(*a, **k))[1])
    g = _result("grudeva2025.reduced", "RIGHTS_BLOCKED", "RIGHTS_BLOCKED")
    o = _result("brewer2026.lb_taichi", "OPTIONAL_DEPENDENCY", "OPTIONAL_UNAVAILABLE")
    assert I.component_figures(g, scenario=_SCEN, execution_context="LOCAL_PRIVATE") == []
    assert I.component_figures(o, scenario=_SCEN, execution_context="LOCAL_PRIVATE") == []
    assert calls == []                                          # zero educational producer calls
    assert I.no_figure_reason(g) == "RIGHTS_BLOCKED"
    assert I.no_figure_reason(o) == "OPTIONAL_DEPENDENCY_UNAVAILABLE"


def test_public_context_cameron_gives_no_figures():
    # obey the tour rights decision: a not-cleared cameron result gets zero educational figures
    r = _result("cameron2020.extraction_bdf", "COMMON_SCENARIO", "RIGHTS_NOT_CLEARED")
    assert I.component_figures(r, scenario=_SCEN, execution_context="PUBLIC_ARTIFACT") == []
    assert I.no_figure_reason(r) == "RIGHTS_BLOCKED"


def test_every_insight_references_a_valid_vizspec_and_producer():
    import importlib
    from puckworks.viz import registry as R
    for cid, insights in I._INSIGHTS.items():
        for spec_id, headline, question, draw_name, _kw in insights:
            spec = R.viz_by_id(spec_id)                        # resolves or raises
            fn = getattr(importlib.import_module(spec.producer.module), spec.producer.function)
            assert callable(fn)
            from puckworks.viz import tour_insight_draw as D
            assert callable(getattr(D, draw_name))
            assert headline and question


@pytest.mark.slow
def test_captions_are_scoped_and_avoid_prohibited_sensory_certainty():
    figs = I.component_figures(_result("cameron2020.extraction_bdf", "COMMON_SCENARIO"),
                               scenario=_SCEN, execution_context="LOCAL_PRIVATE")
    joined = " ".join(f.caption.lower() for f in figs)
    assert "in this model" in joined and "scope" in joined
    for bad in ("guaranteed", "proves your", "will taste", "best recipe", "universal"):
        assert bad not in joined


def test_no_figure_reason_is_finite_vocabulary():
    for cid, kind, status in [("x.check", "SCIENTIFIC_CHECK", "EXECUTED"),
                              ("grudeva2025.reduced", "RIGHTS_BLOCKED", "RIGHTS_BLOCKED"),
                              ("brewer2026.lb_taichi", "OPTIONAL_DEPENDENCY", "OPTIONAL_UNAVAILABLE"),
                              ("waszkiewicz2025.poroelastic", "NATIVE_REFERENCE", "REFERENCE_ONLY")]:
        assert I.no_figure_reason(_result(cid, kind, status)) in I.NO_FIGURE_REASONS
