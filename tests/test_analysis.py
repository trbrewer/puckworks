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


def test_cross_pressure_full_precision_from_raw():
    """review MAJ-12: the 'full precision' cross-pressure mean must be computed from
    UNROUNDED per-pressure RMSEs, so it can differ from the mean of the 3-dp display
    values. Guards against re-introducing the averaging-of-rounded-values bug."""
    import numpy as np
    from puckworks.harness import cross_pressure_discrimination
    r = cross_pressure_discrimination()
    fp = r["conditional_transfer_mean_full_precision"]
    per = r["per_pressure"]; oos = [p for p in per if p != 9.0]
    for m in ("static", "phi", "rc3b"):
        mean_of_rounded = float(np.nanmean([per[p][m] for p in oos]))
        # equal only by coincidence; assert the field is a plain float in range
        assert 0.0 < fp[m] < 5.0
    # at least one mechanism's full-precision value differs from the rounded-mean
    assert any(abs(fp[m] - float(np.nanmean([per[p][m] for p in oos]))) > 1e-9
               for m in ("static", "phi", "rc3b"))


def test_rsm_refit_covariance_panel():
    """The RSM refit exposes a coefficient-covariance / residual panel (owed §7):
    per-coefficient SEs, a residual std, leverages, and the raw-scale design
    condition number that flags the coefficients as numerically unstable (so the
    interpretation stays shape/vertex, not individual coefficients or magnitude)."""
    from puckworks.harness import schmieder_rsm_refit
    r = schmieder_rsm_refit("tds", "1/2")
    d = r["diagnostics"]
    assert d is not None
    assert len(d["coef_se"]) == 7                      # 6 predictors + intercept
    assert d["residual_std"] > 0.0 and 0.0 < d["max_leverage"] <= 1.0
    assert d["raw_scale_ill_conditioned"]              # raw-scale collinearity flagged
    # review MAJ-06: kappa2(X) and kappa2(XtX) correctly named and distinct (~square)
    assert d["gram_condition_number_kappa2_XtX"] > d["design_matrix_condition_number_kappa2_X"]
    assert "loo_q2" not in d                           # correct Q2 lives in lopo_cv
    # review MAJ-05: vertex-validity fractions reported
    assert 0.0 <= r["bootstrap_concave_fraction"] <= 1.0
    assert 0.0 <= r["bootstrap_vertex_in_dial_domain_fraction"] <= 1.0


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
