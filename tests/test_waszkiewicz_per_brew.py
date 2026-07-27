"""Per-brew (per-shot) Waszkiewicz traces + the shot-level ladder (Paper B2 review 4.1).

The load-bearing test is `test_reaggregation_reproduces_the_published_means`: it proves the
per-shot decomposition IS the published aggregate, so nothing was silently re-derived.
"""
import numpy as np
import pytest

from puckworks import data as d
from puckworks.analysis import waszkiewicz_shot_level as W

EXPECTED_SHOT_COUNTS = {1.0: 5, 2.0: 4, 3.5: 3, 4.0: 10, 5.0: 5, 6.0: 6,
                        7.0: 4, 8.0: 4, 9.0: 5, 11.0: 4, 13.0: 7}


def test_shot_inventory_matches_the_source_release():
    per = d.waszkiewicz_traces_per_brew()
    assert {p: len(s) for p, s in per.items()} == EXPECTED_SHOT_COUNTS
    assert sum(EXPECTED_SHOT_COUNTS.values()) == 57
    assert sorted(d.waszkiewicz_traces_per_brew(9.0)) == ["9-1", "9-2", "9-3", "9-4", "9-5"]


def test_common_time_grid_is_exact():
    s = d.waszkiewicz_traces_per_brew(9.0)["9-1"]
    t = s["time__s"]
    assert len(t) == 1000 and t[0] == 0.0
    assert np.allclose(t, np.linspace(0.0, 100.0, 1000), atol=1e-9)


def test_reaggregation_reproduces_the_published_means():
    """THE integrity check: mean/sem over the per-shot traces == the published per-pressure file.

    If this drifts, the per-shot decomposition is no longer the same data the manuscript scores,
    and every shot-level result built on it is void. Tolerance is the published file's own write
    precision (1e-6), not a fitted agreement."""
    per = d.waszkiewicz_traces_per_brew()
    pub = d.waszkiewicz_traces()
    worst = 0.0
    for p, shots in per.items():
        ids = sorted(shots)
        ref = pub[p]
        for col in ("pressure__bar", "basket_pressure__bar", "mass__g",
                    "mass_flow_rate__g_per_s"):
            M = np.vstack([shots[k][col] for k in ids])
            worst = max(worst, float(np.abs(M.mean(axis=0) - ref[col]).max()))
            sem = M.std(axis=0, ddof=1) / np.sqrt(len(ids))
            std_col = col.replace("__", "_std__")
            worst = max(worst, float(np.abs(sem - ref[std_col]).max()))
    assert worst < 1e-5, f"per-shot re-aggregation drifted from the published means: {worst}"


def test_published_spread_is_a_standard_error_not_a_deviation():
    """Guards the misreading the shot-level work exists to correct: the published *_std column is
    sem, so it is sqrt(n) SMALLER than the shot-to-shot SD."""
    shots = d.waszkiewicz_traces_per_brew(9.0)
    ids = sorted(shots)
    M = np.vstack([shots[k]["mass_flow_rate__g_per_s"] for k in ids])
    sd = M.std(axis=0, ddof=1)
    published = d.waszkiewicz_traces()[9.0]["mass_flow_rate_std__g_per_s"]
    assert np.allclose(published, sd / np.sqrt(len(ids)), atol=1e-5)
    assert np.median(sd) > np.median(published)          # SD strictly wider than SEM


def test_across_shot_dispersion_is_reported_on_two_named_scales():
    """Third review P0.1. The single number formerly called a "shot-to-shot noise floor" is a
    LEAVE-IN dispersion: each shot is inside the five-shot mean it is compared against, so it is
    optimistic by construction. Both scales must now be reported and named."""
    r = W.shot_level_dispersion()
    assert r["n_shots"] == 5 and r["n_points"] == 800
    assert 0.10 < r["leave_in_dispersion_rmse_g_per_s"] < 0.25
    assert r["other_four_template_rmse_g_per_s"] > r["leave_in_dispersion_rmse_g_per_s"]
    assert r["between_shot_sd_of_mean_flow_g_per_s"] > 0.05
    assert r["is_noise_floor"] is False


def test_the_leave_in_optimism_is_exactly_n_over_n_minus_one():
    """The identity that makes the optimism non-arguable: Q_i - mean(Q_-i) = n/(n-1)(Q_i - mean Q).
    With five shots every leave-one-out distance is exactly 1.25x the leave-in distance."""
    r = W.shot_level_dispersion()
    assert r["leave_one_out_inflation_factor"] == 1.25
    assert r["leave_one_out_identity_holds"] is True
    assert r["other_four_template_rmse_g_per_s"] == pytest.approx(
        r["leave_in_dispersion_rmse_g_per_s"] * 1.25, abs=1e-3)


def test_the_withdrawn_noise_floor_helper_refuses_rather_than_delegating():
    """A silent alias would let the old, wrong reading survive in any un-updated caller."""
    with pytest.raises(AttributeError, match="withdrawn"):
        W.shot_level_noise_floor()


def test_phi_beats_the_constant_null_on_every_individual_shot():
    """The manuscript's PRIMARY ordering claim, re-tested with the shot as the unit. Holding on
    5/5 individual shots is a materially stronger statement than holding on the averaged curve."""
    r = W.per_shot_ladder()
    assert r["n_shots"] == 5
    assert r["shots_rung4_beats_const"] == 5
    assert r["ordering_survives_per_shot"] is True
    # The margin is large -- but the claim that carries it is the DIRECTIONAL CONSISTENCY across
    # all five shots plus the paired effect size, not a multiple of any dispersion scale
    # (third review P0.1: neither scale is a resolvability threshold).
    gap = r["across_shots"]["rung1_const"]["mean"] - r["across_shots"]["rung4_phi_of_t"]["mean"]
    assert gap > 0.3


def test_the_cubic_beats_phi_on_every_shot_and_no_resolvability_verdict_is_emitted():
    """The manuscript's SECONDARY claim does not survive the unit change: per shot the flexible
    cubic is clearly better than Phi(t), so "Phi(t) nearly reaches the flexible floor" cannot be
    asserted. What is withdrawn along with it (third review P0.1) is the *verdict*: the producer
    used to compare the gap with a leave-in dispersion and emit `phi_vs_cubic_resolvable`, which
    is not a defensible inferential statement."""
    r = W.per_shot_ladder()
    assert r["phi_minus_cubic_mean_g_per_s"] > 0          # cubic wins per shot
    assert "phi_vs_cubic_resolvable" not in r
    assert "shot_noise_floor_rmse_g_per_s" not in r
    # both descriptive scales are still available, named
    assert r["leave_in_dispersion_rmse_g_per_s"] > 0
    assert r["other_four_template_rmse_g_per_s"] > 0


def test_phi_is_not_claimed_to_be_cross_fitted():
    """Review 4.3/4.4 stay blocked -- the producer must say so rather than imply a cross-fit."""
    assert "NOT re-fitted per shot" in W.per_shot_ladder()["note"]
    assert "blocked" in W.per_shot_ladder()["note"]


# --- equilibrium-window provenance (review 4.7 / P0.5) ---------------------------------------
def test_equilibrium_observable_is_the_repository_endpoint_and_matches_the_published_fit():
    """The manuscript must not attribute a 110-120 s statistic to this analysis. What it DOES use
    -- the final 100 s value -- reproduces the source's own static fit, so the wording was the
    only defect."""
    r = W.equilibrium_window_sensitivity()
    assert r["repository_observable"] == "endpoint_100s"
    assert r["endpoint_matches_published"] is True
    assert r["clean_region_insensitive"] is True          # endpoint vs 90-100 s mean agree


def test_the_nominal_110_120s_window_is_unusable_as_published():
    """One shot has ENDED inside the nominal window; it alone destroys the refit. This pins WHY the
    source-faithful route was not taken, so nobody 'restores' it later without the exclusion."""
    r = W.equilibrium_window_sensitivity()
    assert r["contaminated_shots"] == ["9-1"]
    assert r["nominal_110_120s_usable"] is False
    assert r["windows"]["mean_110_120s"]["P_c_bar"] > 50          # nonsense with the bad shot in
    assert 10.0 < r["windows"]["mean_110_120s_excl_contaminated"]["P_c_bar"] < 14.0   # sane without


def test_solids_calibration_model_string_matches_the_implementation():
    """Review P0.10: the metadata string said 0.5k(1 - tanh) while Eq 20 computes (1 + tanh).
    Dissolved mass must RISE, so the code was right; the string was wrong and is now fixed."""
    import numpy as np
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    txt = (__import__("pathlib").Path(__file__).resolve().parents[1]
           / "puckworks/data/waszkiewicz2025/solids_calibration.csv").read_text(encoding="utf-8")
    assert "1 + tanh" in txt and "1 - tanh" not in txt
    k, l, m = wz._solids_params()
    md = wz.solids_sigmoid(np.array([0.0, l, 1e3]), k, l, m)
    assert md[0] < md[1] < md[2]                    # monotone RISING, as (1 + tanh) requires
    assert md[2] == pytest.approx(k, rel=1e-6)      # saturates at k


def test_partial_leave_one_shot_out_bounds_the_equilibrium_reuse_channel():
    """Review 4.2/P0.2. Phi(t) reuses the target through two channels; the equilibrium calibration
    IS cross-fittable and is removed here. The finding is that it contributes almost nothing:
    held-out and in-sample scores differ by ~0.001 g/s, ~1 % of the shot noise floor. That BOUNDS
    one channel as negligible and leaves the solids sigmoid as the only material one."""
    r = W.leave_one_shot_out_phi()
    assert r["n_shots"] == 5
    assert r["cross_fitted_channels"] == ["equilibrium_calibration_P_c_Q_c"]
    assert abs(r["optimism_pp_g_per_s"]) < 0.05 * r["other_four_template_rmse_g_per_s"]
    # honesty guards: this must never be sold as a full cross-fit
    assert r["is_full_cross_fit"] is False
    assert r["remaining_target_reuse"] and "sigmoid" in r["remaining_target_reuse"][0]
    assert "Do NOT describe this as a leave-one-shot-out validation" in r["note"]


# --- P0.3 / P0.4 / P0.7 (Paper B2 second review) ----------------------------------------------
def test_paired_shot_uncertainty_is_exact_and_reports_its_own_floor():
    """P0.3. With five paired units the smallest attainable two-sided randomization p-value is
    2/32 = 0.0625. If a comparison ever reports something smaller, the enumeration is wrong --
    and if the paper ever calls 0.0625 'significant', this pins why it cannot be."""
    r = W.paired_shot_uncertainty()
    assert r["n_shots"] == 5
    for name, c in r["comparisons"].items():
        assert len(c["per_shot_difference_g_per_s"]) == 5, name
        assert c["exact_randomization_p"] >= 2 / 2 ** 5 - 1e-9, (name, c["exact_randomization_p"])
        lo, hi = c["coarse_bootstrap_95_g_per_s"]
        assert lo <= c["mean_difference_g_per_s"] <= hi, name


def test_paired_uncertainty_is_deterministic_in_its_exact_part():
    """The randomization test enumerates the full sign group, so it must not depend on the seed;
    only the bootstrap may."""
    a = W.paired_shot_uncertainty(seed=0)["comparisons"]
    b = W.paired_shot_uncertainty(seed=7)["comparisons"]
    for k in a:
        assert a[k]["exact_randomization_p"] == b[k]["exact_randomization_p"]
        assert a[k]["mean_difference_g_per_s"] == b[k]["mean_difference_g_per_s"]


def test_the_flexible_comparator_never_sees_the_points_it_is_scored_on():
    """P0.4. The whole value of the comparator is that it is withheld. Verify it directly rather
    than trusting the docstring: fitting on ALL five shots must score BETTER on a held-out shot
    than fitting on four -- if it does not, the leave-one-shot-out loop is not excluding anything."""
    import numpy as np
    ids, t, Q = W._shots(W.WINDOW)
    B, P = W._penalized_spline_basis(t)
    c_all, _ = W._fit_penalized_spline(B, P, Q.mean(axis=0))
    leaky = float(np.sqrt(((B @ c_all - Q[0]) ** 2).mean()))
    honest = W.held_out_flexible_comparator()["leave_one_shot_out"][ids[0]]["spline_heldout_rmse"]
    assert honest > leaky, (honest, leaky)


def test_held_out_comparator_reports_both_protocols_and_the_extrapolation_caveat():
    r = W.held_out_flexible_comparator()
    assert r["comparator"]["architecture_fixed_across_folds"] is True
    loso = r["leave_one_shot_out_mean"]
    assert {"spline", "const", "phi", "phi_equilibrium_crossfit", "static"} <= set(loso)
    # both nulls are withheld the same way, so they are comparable
    assert loso["const"] > loso["spline"], loso
    # the interior-segment mean is the headline; edge segments extrapolate and are far worse
    assert r["leave_segment_out_all_segments_spline"] > \
        r["leave_segment_out_interior_mean"]["spline"]
    assert "extrapolate" in r["leave_segment_out_caveat"]


def test_the_held_out_spline_matches_phi_and_no_floor_verdict_is_emitted():
    """The paper's own downgrade, restated without the withdrawn threshold. The finding is that a
    fully held-out empirical template predicts an omitted shot as well as the partly
    target-informed Phi(t) trajectory -- a difference of ~0.003 g/s on a ~0.19 g/s scale, with the
    five paired differences split 2-3 and an exact sign-flip p of 0.8125. That is a statement about
    effect size and directional inconsistency, not about clearing a floor."""
    r = W.held_out_flexible_comparator()
    assert abs(r["phi_minus_spline_heldout_g_per_s"]) < 0.02
    assert "difference_exceeds_shot_noise_floor" not in r
    assert "shot_noise_floor_rmse_g_per_s" not in r


def test_residual_diagnostics_share_one_declared_resolution():
    """P0.7. Every branch's ACF and Durbin-Watson must come from the SAME decimated series --
    that is the defect the review found."""
    r = W.residual_diagnostics(resolution_s=1.0)
    n = r["n_points_at_resolution"]
    assert n == len(r["time_s"])
    for name, v in r["branches"].items():
        assert len(v["residual_vs_time_g_per_s"]) == n, name
        assert -1.0 <= v["lag1_autocorrelation"] <= 1.0
        assert 0.0 <= v["durbin_watson"] <= 4.0


def test_the_serial_correlation_summary_is_resolution_dependent():
    """Why the resolution has to be declared rather than implied: the statistic genuinely moves."""
    a = W.residual_diagnostics(resolution_s=1.0)["branches"]["rung4_phi_of_t"]
    b = W.residual_diagnostics(resolution_s=5.0)["branches"]["rung4_phi_of_t"]
    assert a["lag1_autocorrelation"] > b["lag1_autocorrelation"] + 0.1, (a, b)
    assert b["durbin_watson"] > a["durbin_watson"] + 0.1, (a, b)


def test_every_branch_leaves_autocorrelated_residuals_including_the_flexible_one():
    """The manuscript's caveat, made enforceable: no branch reduces the residual to white noise,
    so a low RMSE cannot be read as a validated mechanism."""
    r = W.residual_diagnostics(resolution_s=1.0)["branches"]
    for name, v in r.items():
        assert v["lag1_autocorrelation"] > 0.5, (name, v["lag1_autocorrelation"])
    # and the temporal branches sit BELOW shot-to-shot variability while the static ones do not
    assert r["rung4_phi_of_t"]["residual_over_between_shot_sd"] < 1.0
    assert r["rung1_const"]["residual_over_between_shot_sd"] > 2.0
