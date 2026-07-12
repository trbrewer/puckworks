"""Smoke tests for the reported CV + residual DIAGNOSTICS.

These check the callables RUN and return sane-typed output -- NOT that they clear
a threshold. They are diagnostics (small-n), not validation gates, and are NOT in
run_all_gates().
"""


def test_lopo_rsm_runs():
    from puckworks.analysis.lopo_cv import lopo_rsm_design_point
    r = lopo_rsm_design_point("tds", "1/2")
    assert r["n_design_points"] >= 10 and -1.0 <= r["Q2_predictive"] <= 1.0


def test_lopo_waszkiewicz_runs():
    from puckworks.analysis.lopo_cv import lopo_waszkiewicz_pressure
    r = lopo_waszkiewicz_pressure()
    assert r["n_pressures"] == 11 and -1.0 <= r["Q2_predictive"] <= 1.0


def test_residual_autocorr_runs():
    from puckworks.analysis.residual_autocorr import summary
    assert summary()["n_pressures"] == 11
