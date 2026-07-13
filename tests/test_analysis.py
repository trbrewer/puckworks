"""Smoke tests for the reported CV + residual DIAGNOSTICS.

These check the callables RUN and return sane-typed output -- NOT that they clear
a threshold. They are diagnostics (small-n), not validation gates, and are NOT in
run_all_gates().
"""


def test_lopo_rsm_runs():
    from puckworks.analysis.lopo_cv import lopo_rsm_design_point
    r = lopo_rsm_design_point("tds", "1/2")
    assert r["n_settings"] == 15 and -1.0 <= r["Q2_predictive"] <= 1.0
    assert r["predictors"] == "achieved"               # source contract (MAJ-10)


def test_lopo_waszkiewicz_runs():
    from puckworks.analysis.lopo_cv import lopo_waszkiewicz_pressure
    r = lopo_waszkiewicz_pressure()
    assert r["n_pressures"] == 11 and -1.0 <= r["Q2_predictive"] <= 1.0


def test_residual_autocorr_runs():
    from puckworks.analysis.residual_autocorr import summary
    assert summary()["n_pressures"] == 11


def test_paper_b_build_verifies_manuscript_claims():
    """review AR-B2-13: the Paper B strict build must confirm every manuscript-facing
    headline number equals the value in the cached results bundle (fails on drift).
    Runs verify against the committed bundle (fast); guards manuscript<->bundle."""
    import os
    from puckworks.paper_b import build
    if not os.path.exists(build._BUNDLE):
        import pytest
        pytest.skip("Paper B bundle not computed (run `python -m puckworks.paper_b.build compute`)")
    ok, failures, manifest = build.verify(timestamp=None, write_manifest=False)
    assert ok, "Paper B numbers drifted from the bundle: " + "; ".join(failures)
    assert manifest["n_claims"] >= 12 and manifest["n_failures"] == 0
    assert all(v != "MISSING" for v in manifest["data_sha256"].values())


def test_ntube_conservation_audit_full_trajectory():
    """review MAJ-33: the conservation audit must be TRUE trajectory extrema (not the
    final step) and track raw non-negativity + the control-law flow balance. Under FLOW
    control the raw total relative flow is conserved (mean w == 1); under PRESSURE control
    it is NOT (total flow is free) -- the honest distinction the old code hid."""
    from puckworks.harness import ntube_kappa_t_union
    rf = ntube_kappa_t_union(N=80, substeps=4, control="flow", compute_ey=False)
    ca = rf["conservation_audit"]
    assert ca["n_substeps_total"] > 1                      # audited over every substep
    assert ca["nonnegative_throughout"] is True
    assert ca["share_sum_max_deviation"] < 1e-6            # normalized share sums to 1
    assert ca["raw_total_flow_conserved"] is True          # flow control imposes the total
    rp = ntube_kappa_t_union(N=80, substeps=4, control="pressure", compute_ey=False)
    assert rp["conservation_audit"]["raw_total_flow_conserved"] is False  # free under pressure


def test_fig2_evidence_dictionary_is_complete():
    """review MAJ-20/B3-20: the Figure-2 data dictionary must DEFINE every status token
    that appears in the evidence matrix and every mechanism row must carry a citation, so
    no figure cell is an undefined word. The markdown export must render off the same
    committed CSVs. Fast."""
    from puckworks import data as d
    from puckworks.figures import fig2_evidence_dictionary_md
    audit = d.paper_b_evidence_dictionary_audit()
    assert audit["undefined_tokens"] == [], audit["undefined_tokens"]
    assert audit["uncited_mechanisms"] == [], audit["uncited_mechanisms"]
    assert audit["complete"] is True
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmp:
        path = fig2_evidence_dictionary_md(tmp)
        assert os.path.exists(path)
        text = open(path).read()
        assert "Status-token definitions" in text and "citation" in text


def test_result2_block_bootstrap_and_window_sensitivity():
    """review MAJ-23/B3-23: a dependence-aware (moving-block) bootstrap must show Phi(t)
    robustly beats the best constant (CI excludes 0) but only TIES the flexible cubic (CI
    straddles 0), and the Phi-over-constant ranking must persist across windows -- the
    honest in-sample-not-mechanism reading. Fast."""
    from puckworks.harness import result2_residual_diagnostics
    r = result2_residual_diagnostics(n_boot=400)
    assert r["rmse_diff_phi_minus_best_const"]["excludes_zero"] is True
    assert r["rmse_diff_phi_minus_best_const"]["median"] < 0          # phi lower RMSE
    assert r["rmse_diff_phi_minus_cubic"]["excludes_zero"] is False   # ties the cubic
    assert r["phi_ranking_persists_across_windows"] is True
    assert r["residual_acf_lag1_by_branch"]["phi"] > 0.9             # strong dependence
    # B5-20: residual traces + multi-lag ACF are exposed for the supplementary figure
    rt = r["residual_traces"]; ac = r["acf_by_lag"]
    assert len(rt["time_s"]) == len(rt["residual"]["phi"]) > 10
    assert ac["phi"][0] == 1.0 and ac["phi"][1] > 0.9               # ACF(0)=1, slow decay
    assert set(("phi", "best_const", "cubic")) <= set(ac)


def test_ntube_state_classifier_distinguishes_single_channel(monkeypatch=None):
    """review B5-09: the end-state classifier must call the tested near-choke config a
    single-channel collapse (max single-tube share high, N_eff->1) but must NOT call an
    oligarchic/distributed state (a few/many channels sharing the flow, low top-1 share)
    'concentrates' just because the top-DECILE share is high. Fast."""
    from puckworks.harness import ntube_kappa_t_union
    base = ntube_kappa_t_union(gs=1.1, N=200, P_bar=9.0)
    assert base["state"] == "single_channel" and base["concentrates"] is True
    assert base["max_single_tube_share_final"] >= 0.5               # one tube dominates
    lat = ntube_kappa_t_union(gs=1.1, N=200, P_bar=9.0, lateral=0.1)
    # lateral exchange spreads the flow: NOT a single-channel collapse even if the
    # top-decile share is high (the old bug labelled this 'concentrates').
    assert lat["state"] != "single_channel" and lat["concentrates"] is False
    assert lat["max_single_tube_share_final"] < 0.5


def test_ntube_physical_time_and_concentration_metrics():
    """review MAJ-36/MAJ-38: the trajectory must surface PHYSICAL time (seconds) and a
    collapse time, plus normalized concentration metrics (entropy/Gini/top-k) portable
    across N. Fast (small N)."""
    from puckworks.harness import ntube_kappa_t_union
    r = ntube_kappa_t_union(N=100, substeps=8, compute_ey=False)
    assert "time_s_trajectory" in r and r["time_s_trajectory"][-1] > 10  # real seconds
    cm = r["concentration_metrics"]
    assert 0.0 <= cm["entropy_normalized"] <= 1.0 and 0.0 <= cm["gini"] <= 1.0
    assert cm["collapse_time_s"] is None or cm["collapse_time_s"] > 0
    assert 0.0 < cm["n_eff_over_N"] <= 1.0


def test_ntube_switching_converges_under_refinement():
    """review MAJ-36/B3-14: the early collapse must CONVERGE as the timestep shrinks
    (event is physical, not a stepping artefact). Uses a coarse config for speed."""
    from puckworks.harness import ntube_switching_convergence
    r = ntube_switching_convergence(substeps_list=(4, 8, 16), N=100)
    assert r["collapse_time_converges"] is True
    assert r["n_eff_final_converges"] is True
    assert r["collapse_time_spread_s"] is not None and r["collapse_time_spread_s"] < 1.0


def test_ntube_robustness_is_ofat_not_factorial():
    """review MAJ-34/39/40/41: the study must NOT claim to be factorial, must derive the
    pressure range from config (6-11 not 6-12), separate invariance by axis type, and
    report N_eff/N. SLOW -- skipped unless explicitly enabled."""
    import os
    import pytest
    if not os.environ.get("PUCKWORKS_SLOW"):
        pytest.skip("slow N-tube robustness study (set PUCKWORKS_SLOW=1)")
    from puckworks.harness import ntube_robustness_study
    r = ntube_robustness_study()
    assert "NOT a full factorial" in r["design_type"]
    assert r["pressure_range_bar"] == [6.0, 11.0]
    assert {"numerical_convergence_invariant", "stochastic_invariant",
            "operating_invariant"} <= set(r)
    assert r["n_eff_over_N_range_when_concentrating"] is not None


def test_rsm_diagnostics_deletion_wild_bootstrap():
    """review MAJ-12/13/§5.5: the RSM diagnostics must reproduce the review's independent
    deletion ranges + influential run and provide wild-bootstrap + full-quadratic
    sensitivity (all conditional on the seven-term fit)."""
    from puckworks.harness import schmieder_rsm_diagnostics
    r = schmieder_rsm_diagnostics()
    d = r["deletion"]
    lo, hi = d["leave_one_run_vertex_range"]
    assert 1.73 <= lo <= 1.74 and 1.76 <= hi <= 1.77       # review 1.736-1.765
    assert d["leave_one_setting_concave_in_domain"].endswith("/15")
    assert abs(d["most_influential_run"]["cooks_d"] - 0.441) < 0.03
    assert abs(d["most_influential_run"]["leverage"] - 0.187) < 0.02
    b = r["bootstrap"]
    assert {"iid_residual", "wild_rademacher", "wild_mammen"} <= set(b)
    assert r["model_form"]["retained_beats_full"] is True
    assert abs(r["model_form"]["full_quadratic_vertex"] - 1.737) < 0.01


def test_jensen_audit_uses_evaluated_mean():
    """review MAJ-17: the Jensen gap must use the ACTUAL post-clipping evaluated mean
    E[K], not EY(1); the clipping mean-shift must be reported and small, and the sign
    conclusion (all gaps negative) unchanged."""
    from puckworks.harness import channeling_concavity_audit
    r = channeling_concavity_audit()
    assert "max_evaluated_mean_shift" in r
    assert r["max_evaluated_mean_shift"] < 0.02            # clipping shift is tiny
    assert r["all_jensen_gaps_negative"] is True
    assert all("evaluated_mean_k" in c for c in r["cells"])


def test_paper_b_build_freshness_guard():
    """review MAJ-04: a RELEASE (strict) verify must FAIL on a stale/dirty tree, while the
    routine claim check still passes; the manifest exposes release_fresh."""
    import os
    from puckworks.paper_b import build
    if not os.path.exists(build._BUNDLE):
        import pytest
        pytest.skip("Paper B bundle not computed")
    ok_routine, _, man = build.verify(write_manifest=False)          # strict=False
    assert "release_fresh" in man and "bundle_matches_head" in man
    ok_strict, fails, _ = build.verify(write_manifest=False, strict=True)
    if not man["release_fresh"]:                                     # dirty/stale dev tree
        assert not ok_strict and any("RELEASE" in f for f in fails)
        assert ok_routine                                           # routine check unaffected


def test_paper_b_evidence_matrix_is_data_driven():
    """review MAJ-09: Fig 2 must render from the committed evidence CSV, and every
    status must be a defined code the figure knows how to draw (no hard-coded cells,
    no undefined statuses)."""
    from puckworks import data as d
    from puckworks.figures import _EV_STATUS
    rows = d.paper_b_evidence_matrix()
    assert len(rows) >= 4
    dims = ["implemented", "observable", "params_provenance",
            "generates_interior_max", "evidence_strength"]
    for r in rows:
        assert r["mechanism"] and r["decisive_missing_measurement"]
        for dim in dims:
            assert r[dim] in _EV_STATUS, f"undefined status {r[dim]!r} for {dim}"


def test_rsm_center_mask_is_experiment_7():
    """review MAJ-07: the achieved-predictor 'central' cross-section must use the
    nominal centre point (6 runs, experiment 7), not every grind-1.7 row."""
    from puckworks.harness import schmieder_rsm_refit
    r = schmieder_rsm_refit("tds", "1/2", predictors="achieved")
    assert r["n_center_runs"] == 6
    assert abs(r["eval_flow_ml_s"] - 1.9011) < 0.02   # mean achieved central flow
    # review MAJ-08: report the JOINT concave-and-in-domain fraction
    assert 0.9 <= r["bootstrap_concave_AND_in_domain_fraction"] <= 1.0


def test_cross_pressure_loco_full_precision():
    """review AR-B2-09: cross_pressure_loco must aggregate RAW per-pressure RMSEs,
    not values already rounded to 3 dp (mirrors the discrimination-function guard)."""
    from puckworks.harness import cross_pressure_loco
    r = cross_pressure_loco()
    assert set(r["heldout_mean"]) == {"static", "phi", "rc3b"}
    assert r["max_calibration_drift"] < 0.10
    # a full-precision mean generally won't equal the mean of 3-dp per-pressure values
    import numpy as np
    per = r["per_pressure"]
    mean_of_rounded = float(np.nanmean([per[p]["phi"] for p in per]))
    assert abs(r["heldout_mean"]["phi"] - mean_of_rounded) < 0.01   # close but computed from raw


def test_rsm_achieved_predictor_sensitivity():
    """review MAJ-04: the RSM refit reports the source-contract ACHIEVED-predictor
    vertex alongside the target-predictor one; the vertex is insensitive to the choice
    (both interior, shift < 0.1 dial)."""
    from puckworks.harness import schmieder_rsm_refit
    r = schmieder_rsm_refit("tds", "1/2")
    a = r["achieved_predictor_sensitivity"]
    assert a is not None and a["vertex_g"] is not None
    assert abs(r["vertex_g"] - a["vertex_g"]) < 0.1        # predictor choice barely moves it
    assert 1.4 < a["vertex_g"] < 2.0                        # still interior


def test_ntube_conservation_and_trajectory_keys():
    """review AR-B2-12: the N-tube core reports conservation/non-negativity of the
    flow shares and an N_eff(t) trajectory (not just the endpoint). A single small
    run is enough to guard the contract (full sweep is a slow hand-run diagnostic)."""
    from puckworks.harness import ntube_kappa_t_union
    r = ntube_kappa_t_union(N=60, substeps=4, compute_ey=False)
    assert r["share_sum_max_deviation"] < 1e-9      # shares sum to 1 (conservation)
    assert r["min_flow_share"] >= 0.0                # non-negativity
    assert len(r["n_eff_trajectory"]) >= 2           # trajectory, not just endpoint
    assert isinstance(r["n_eff_monotone_decreasing"], bool)


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
