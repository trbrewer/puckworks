"""Figures for the Full Laboratory Tour's per-component cards (#43).

Offline. The plotter renders REAL tour output (never fabricates), returns a plain caption, and returns
None for blocked/optional/no-output components. Fast tests drive synthetic result dicts; one @slow test
renders every card from a real tour.
"""
import matplotlib
import pytest

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


def test_gate_metrics_make_a_scorecard_figure():
    r = _result(cid="c.check", kind="SCIENTIFIC_CHECK",
                outputs=[{"gate_id": "g1", "status": "PASS", "metrics": {"ratio": 0.9, "ok": True}},
                         {"gate_id": "g2", "status": "PASS", "metrics": {"series": [0.24, 0.23, 0.22]}}])
    fig, caption = P.component_figure(r)
    assert "check" in caption.lower()
    plt.close(fig)


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


@pytest.mark.slow
def test_every_executed_component_renders_and_blocked_do_not():
    from puckworks.product import lab, lab_tour
    import io
    t = lab_tour.execute_laboratory_tour(lab.ScenarioRequest("pv19_named"),
                                         execution_context="LOCAL_PRIVATE").to_dict()
    rendered = skipped = 0
    for c in t["components"]:
        res = P.component_figure(c)
        if res is None:
            assert c["execution_status"] in ("RIGHTS_BLOCKED", "OPTIONAL_UNAVAILABLE")
            skipped += 1
        else:
            fig, cap = res
            assert cap
            fig.savefig(io.BytesIO(), format="png"); plt.close(fig)
            rendered += 1
    assert rendered == 23 and skipped == 2      # 23 executed render; grudeva + lb_taichi do not
