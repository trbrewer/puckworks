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


def test_result1_design_aware_stats_runs():
    """Design-aware experiment-unit diagnostic for Result 1 (runs + sane-typed;
    NOT a threshold gate). Confirms the load-bearing structural facts: one
    experiment per dial, three dial cells, and the descriptive ordering."""
    from puckworks.harness import result1_design_aware_stats
    r = result1_design_aware_stats()
    assert [c["dial"] for c in r["cells"]] == [1.4, 1.7, 2.0]
    assert all(c["n_experiments"] == 1 for c in r["cells"])   # no between-exp reps
    assert set(r["pairwise"]) == {"dial_1.4_vs_1.7", "dial_1.7_vs_2.0"}
    assert isinstance(r["cell_means_ordered"], bool)
    assert isinstance(r["interior_maximum"], bool)
