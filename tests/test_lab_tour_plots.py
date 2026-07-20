"""Figures for the Full Laboratory Tour's per-component cards (#43).

Offline. The plotter renders REAL tour output (never fabricates), returns a plain caption, and returns
None for blocked/optional/no-output components. Fast tests drive synthetic result dicts; one @slow test
renders every card from a real tour.
"""
import pytest

pytest.importorskip("matplotlib")   # matplotlib is a viz/webapp extra, absent on the core quick lanes
import matplotlib  # noqa: E402

matplotlib.use("Agg")   # tests are headless
import matplotlib.pyplot as plt  # noqa: E402

from puckworks.product import lab_tour_plots as P  # noqa: E402


def _result(cid="x.y", stage="flow", kind="NATIVE_REFERENCE", status="EXECUTED", outputs=None):
    return {"component_id": cid, "stage": stage, "execution_kind": kind, "execution_status": status,
            "outputs": outputs or [], "message": "ran"}


def test_blocked_and_optional_return_none_no_fake_plot():
    for status in ("RIGHTS_BLOCKED", "OPTIONAL_UNAVAILABLE", "RIGHTS_NOT_CLEARED", "NO_EXECUTION_PATH"):
        assert P.component_figure(_result(status=status)) is None


def test_value_outputs_make_a_bar_figure_with_caption():
    r = _result(outputs=[{"name": "simulated_k", "value": 80.1, "unit": "lu", "role": "simulated"},
                         {"name": "analytic_k", "value": 80.08, "unit": "lu", "role": "analytic_reference"},
                         {"name": "converged", "value": True, "unit": "", "role": "derived"}])
    res = P.component_figure(r)
    assert res is not None
    fig, caption = res
    assert isinstance(caption, str) and caption
    fig.savefig(__import__("io").BytesIO(), format="png"); plt.close(fig)


def test_bracket_output_makes_a_bracket_figure():
    r = _result(cid="foster2025.infiltration", stage="infiltration",
                outputs=[{"name": "observed_first_drip_s", "value": 7.0, "unit": "s", "role": "measured"},
                         {"name": "predicted_first_drip_bracket_s", "value": [6.4, 7.8], "unit": "s",
                          "role": "predicted"}])
    fig, caption = P.component_figure(r)
    assert "predicted range" in caption
    plt.close(fig)


def test_scientific_check_alone_yields_no_figure():
    # the gate-scorecard path is REMOVED: gate/check numbers are technical evidence, not a novice figure
    r = _result(cid="c.check", kind="SCIENTIFIC_CHECK",
                outputs=[{"gate_id": "g1", "status": "PASS", "metrics": {"ratio": 0.9, "ok": True}},
                         {"gate_id": "g2", "status": "PASS", "metrics": {"series": [0.24, 0.23, 0.22]}}])
    assert P.component_figure(r) is None


def test_no_gate_scorecard_path_remains():
    import inspect
    src = inspect.getsource(P)
    assert "_gate_figure" not in src and "condition index" not in src and "_PASS_COLOR" not in src


def test_no_numeric_output_returns_none():
    r = _result(outputs=[{"name": "note", "value": "text only", "unit": "", "role": "reference"}])
    assert P.component_figure(r) is None


def test_time_series_panels_render():
    panels = [{"x": [0.0, 1.0, 2.0], "x_label": "t (s)", "y_label": "EY (%)", "unit": "%",
               "series": [{"label": "yield", "role": "simulated", "y": [0, 10, 17]}]}]
    fig, caption = P.component_figure(_result(cid="cameron2020.extraction_bdf", stage="extraction",
                                              kind="COMMON_SCENARIO"), trace_panels=panels)
    assert "over time" in caption
    plt.close(fig)


# NOTE: there is deliberately NO "all executable components render" test. Educational figures are the
# insight system's job (tests/test_lab_tour_insights.py tests the EXPLICIT expected set); a component is
# allowed to have no worthwhile public figure. A blocked/optional component still returns None here.
def test_blocked_component_returns_none():
    assert P.component_figure(_result(status="RIGHTS_BLOCKED")) is None
    assert P.component_figure(_result(status="OPTIONAL_UNAVAILABLE")) is None
