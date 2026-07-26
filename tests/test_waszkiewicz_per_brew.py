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


def test_noise_floor_is_the_scale_ladder_gaps_are_judged_on():
    r = W.shot_level_noise_floor()
    assert r["n_shots"] == 5 and r["n_points"] == 800
    # a single shot sits ~0.15 g/s from the mean curve the manuscript scores
    assert 0.10 < r["noise_floor_rmse_g_per_s"] < 0.25
    assert r["between_shot_sd_of_mean_flow_g_per_s"] > 0.05


def test_phi_beats_the_constant_null_on_every_individual_shot():
    """The manuscript's PRIMARY ordering claim, re-tested with the shot as the unit. Holding on
    5/5 individual shots is a materially stronger statement than holding on the averaged curve."""
    r = W.per_shot_ladder()
    assert r["n_shots"] == 5
    assert r["shots_rung4_beats_const"] == 5
    assert r["ordering_survives_per_shot"] is True
    # and the margin is comfortably outside shot noise: gap ~0.39 g/s vs a ~0.15 g/s floor (~2.6x)
    gap = r["across_shots"]["rung1_const"]["mean"] - r["across_shots"]["rung4_phi_of_t"]["mean"]
    assert gap > 2 * r["shot_noise_floor_rmse_g_per_s"]


def test_phi_vs_cubic_is_not_resolvable_at_shot_level():
    """The manuscript's SECONDARY claim does not survive the unit change: per shot the flexible
    cubic is clearly better than Phi(t), and the gap is inside the shot-to-shot noise floor, so
    'Phi(t) nearly reaches the flexible floor' cannot be asserted from five shots."""
    r = W.per_shot_ladder()
    assert r["phi_minus_cubic_mean_g_per_s"] > 0          # cubic wins per shot
    assert r["phi_vs_cubic_resolvable"] is False
    assert abs(r["phi_minus_cubic_mean_g_per_s"]) < r["shot_noise_floor_rmse_g_per_s"]


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
    assert abs(r["optimism_pp_g_per_s"]) < 0.05 * r["shot_noise_floor_rmse_g_per_s"]
    # honesty guards: this must never be sold as a full cross-fit
    assert r["is_full_cross_fit"] is False
    assert r["remaining_target_reuse"] and "sigmoid" in r["remaining_target_reuse"][0]
    assert "Do NOT describe this as a leave-one-shot-out validation" in r["note"]
