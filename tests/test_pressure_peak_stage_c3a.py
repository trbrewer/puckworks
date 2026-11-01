"""C3a scientific checks consume committed CSV fields, without raw-data access."""
import re

import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy.integrate import quad

from puckworks.analysis import pressure_peak_stage_c3a as C


@pytest.fixture(scope="module")
def rows():
    return C.read_table()


def select(rows, kind):
    return [r for r in rows if r["record_type"] == kind]


def test_labels_and_artifact_scope(rows):
    assert all(r["claim"] == C.CLAIM for r in rows)
    assert len(select(rows, "detector_brew")) == 56
    assert len(select(rows, "detector_condition")) == 11
    assert len(select(rows, "onset_fit")) == 24
    assert len(select(rows, "screen")) == 4
    assert len(select(rows, "restart_replay")) == 2
    for r in rows:
        assert not any("grade" in key for key in r)
    provenance = select(rows, "provenance")[0]
    assert provenance["cumulative_wall_seconds"] < provenance["cap_seconds"]
    assert provenance["refit_count"] == 0
    assert len(provenance["source_sha256"]) == 68
    summary = (C.OUT / "SUMMARY.md").read_text()
    assert "In-sample screens can mislead and do not replace LOCO + refits." in summary
    assert "\u2014" not in summary
    assert not re.search(r"\b(?:MEETS|NEAR|MISSES|PASS)\b", summary)
    assert summary.index("0.0719361259858887") < summary.index("T3-D")


def test_detector_witness_and_condition_counts(rows):
    brews = select(rows, "detector_brew")
    for r in brews:
        f, m = [r["criterion_witness"][k] for k in ("flow", "mass")]
        for witness in (f, m):
            assert witness["value"] > witness["threshold"]
            assert witness["run_min"] > witness["threshold"]
            if witness["previous_value"] is not None:
                assert witness["previous_value"] <= witness["threshold"]
                assert witness["previous_s"] < witness["crossing_s"]
        last = "flow" if f["crossing_s"] > m["crossing_s"] else (
            "mass" if m["crossing_s"] > f["crossing_s"] else "simultaneous")
        assert r["last_criterion"] == last
        assert_allclose(max(f["crossing_s"], m["crossing_s"]), r["onset_x1_s"], rtol=1e-12)
        assert_allclose(r["criterion_gap_s"], abs(f["crossing_s"]-m["crossing_s"]), rtol=1e-12)
        assert_allclose(r["flow_at_onset_g_s"], f["onset_value"], rtol=1e-12)
        assert r["qualifying_end_s"]-r["onset_x1_s"] >= 2.
        assert_allclose(r["onset_endpoint_ratio"], r["flow_at_onset_g_s"]/r["endpoint_g_s"], rtol=1e-12)
        assert r["onset_x05_s"] <= r["onset_x1_s"]
        if "onset_x15_s" in r:
            assert r["onset_x1_s"] <= r["onset_x15_s"]
        for kind in ("flow", "mass"):
            values = list(r[f"first_{kind}_crossings_s"].values())
            found = [x for x in values if x is not None]
            assert all(a <= b for a, b in zip(found[:-1], found[1:]))
        assert_allclose(r["shift_x1_minus_x05_s"], r["onset_x1_s"]-r["onset_x05_s"], rtol=1e-12)
    conditions = select(rows, "detector_condition")
    for c in conditions:
        group = [r for r in brews if r["condition_bar"] == c["condition_bar"]]
        assert len(group) == c["n"]
        assert c["last_counts"] == {k: sum(r["last_criterion"] == k for r in group)
                                    for k in ("flow", "mass", "simultaneous")}
        for field, stats in c["statistics"].items():
            if field.startswith("first_"):
                _, kind, threshold, _ = field.split("_")
                values = [r[f"first_{kind}_crossings_s"][threshold] for r in group]
            else:
                values = [r.get(field) for r in group]
            found = [v for v in values if v is not None]
            assert stats["detected"] == len(found)
            assert stats["undetected"] == len(group)-len(found)
            if found:
                assert_allclose([stats[k] for k in ("mean", "median", "minimum", "maximum")],
                                [np.mean(found), np.median(found), min(found), max(found)], rtol=1e-12)
    low = conditions[0]
    carry = low["last_counts"]["flow"] > low["n"]/2 and all(
        low["statistics"]["shift_x1_minus_x05_s"]["mean"] >
        c["statistics"]["shift_x1_minus_x05_s"]["mean"] for c in conditions[1:])
    reading = select(rows, "detector_reading")[0]
    assert reading["T3O"] == ("carry into C3" if carry else "drop")
    assert reading["predeclared_reading"] == C.DETECTOR_READING
    assert not reading["successor_authorized"]


@pytest.mark.parametrize("scale", [.5, 1.5])
def test_onset_training_separation_floor_and_plugin(rows, scale):
    fits = [r for r in select(rows, "onset_fit") if r["threshold_scale"] == scale]
    assert len(fits) == 12
    for r in fits:
        p = r["parameters"]
        training = [b for b in r["brew_predictions"] if b["role"] == "training"]
        held = [b for b in r["brew_predictions"] if b["role"] == "held_out"]
        assert {b["brew"] for b in training} == set(r["training_brews"])
        assert all(b["observed_onset_s"] is not None for b in training)
        if r["fold"] != "DESCRIPTIVE_ALL":
            pressure = float(r["fold"].removeprefix("HYD-LOCO-"))
            assert all(b["condition_bar"] != pressure for b in training)
            assert all(b["condition_bar"] == pressure for b in held)
        cap = min(5., min(b["Pe_bar"] for b in training)-.01)
        assert_allclose(r["P0_cap_bar"], cap, rtol=1e-12, atol=0)
        assert p["P0_bar"] <= cap
        assert min(b["margin_bar"] for b in training) >= .01
        assert r["training_floor_uses"] == 0
        assert r["held_out_floor_uses"] == sum(b["floor_used"] for b in held)
        for b in r["brew_predictions"]:
            expected = p["t0_s"]+p["b_s_bar"]*np.exp(b["Pe_bar"]/p["Pd_bar"])/max(b["Pe_bar"]-p["P0_bar"], .01)
            assert_allclose(b["predicted_onset_s"], expected, rtol=1e-12, atol=0)
            assert_allclose(b["margin_bar"], b["Pe_bar"]-p["P0_bar"], rtol=1e-12, atol=0)
        residual = np.array([b["predicted_onset_s"]-b["observed_onset_s"] for b in training])
        assert_allclose(p["objective_sum_squares"], np.dot(r["training_weights"], residual**2), rtol=1e-12)
        assert_allclose(r["onset_minimum_bar"], p["P0_bar"]+p["Pd_bar"], rtol=1e-12)
        assert_allclose(r["plugin_peak_bar"], r["plugin_saved_P0f_bar"]+p["Pd_bar"]*
                        np.log1p(r["plugin_saved_Pstar_bar"]/p["Pd_bar"]), rtol=1e-12)


def test_parent_objective_and_tau_zero_replay(rows):
    r = select(rows, "T2F_replay")[0]
    assert_allclose(r["recomputed_objective"], r["saved_objective"], rtol=1e-12, atol=0)
    assert_allclose(np.dot(r["weights"], r["brew_trace_mse"]), r["saved_objective"], rtol=1e-12, atol=0)
    times = np.array(r["fit_times_s"])
    mask = ((times[None, :] >= np.array(r["primary_onset_s"])[:, None]+2) &
            (times[None, :] <= np.array(r["clean_end_s"])[:, None]))
    assert_allclose(mask.sum(axis=1), r["mask_count"], rtol=0, atol=0)
    f = r["numerical_fixture"]
    p, t, coef = np.array(f["pressure"]), np.array(f["t"]), f["parameters"]
    q = C.flow_r([*coef[:3], 0.], p, t, f["mc"], coef[3])
    assert_allclose(q, f["reference_flow"], rtol=1e-12, atol=0)
    # Independently exercise the new capacity/inversion path, not just dispatch.
    q = C.mass_flow(C.capacity_r([*coef[:3], 0.], p, p, coef[3]), t, f["mc"])[0]
    assert_allclose(q, f["reference_flow"], rtol=1e-12, atol=0)
    qd = C.mass_flow(C.capacity_d([coef[0], coef[1], 0., coef[3]], p), t, f["mc"])[0]
    expected = C.C1.flow_curve([coef[0], coef[1], 0., coef[3]], p, t, f["mc"])[0]
    assert_allclose(qd, expected, rtol=1e-12, atol=0)


def test_threshold_series_against_integral_and_saved_limits(rows):
    r = select(rows, "numerical_checks")[0]
    pd = r["pd"]
    p = np.array(r["pressure"])
    for lam in (pd, pd*(1-1e-8), pd*(1+1e-8), pd/2, 2*pd):
        h, hp = C.threshold_factor(p, lam, pd)
        integral = [quad(lambda u: -np.expm1(-(v-u)/pd)*np.exp(-u/lam)/lam,
                         0., v, epsabs=1e-24, epsrel=1e-12)[0] for v in p]
        assert_allclose(h, integral, rtol=1e-12, atol=1e-25)
        assert np.all(h >= 0)
        assert np.all(hp >= 0)
    h, hp = C.threshold_factor(p, pd, pd)
    assert_allclose(h, r["equal_lambda_factor"], rtol=1e-12, atol=0)
    assert_allclose(hp, p*np.exp(-p/pd)/pd**2, rtol=1e-12, atol=0)
    assert_allclose(r["tiny_lambda_capacity"], r["zero_lambda_capacity"], rtol=2e-8, atol=1e-14)


def test_raw_ramp_relaxation_has_no_stable_reset(rows):
    f = select(rows, "numerical_checks")[0]["ramp_fixture"]
    t, p, tau = np.array(f["t"]), np.array(f["pressure"]), f["tau"]
    state = C.relaxation_native(t, p, tau)
    expected = []
    for end in t:
        expected.append(sum(quad(lambda u: np.exp(-(end-u)/tau)*np.interp(u, t, p)/tau,
                                 left, min(right, end), epsabs=1e-13)[0]
                            for left, right in zip(t[:-1], t[1:]) if left < end))
    assert_allclose(state, expected, rtol=1e-12, atol=1e-14)
    assert_allclose(state, f["state"], rtol=1e-12, atol=0)
    assert state[np.flatnonzero(t == 0)[0]] > 0
    assert_allclose(f["constant_state"], f["constant_pressure"]*(-np.expm1(-(t-t[0])/tau)), rtol=1e-12, atol=0)


def test_screen_objectives_residuals_starts_and_peaks(rows):
    for r in select(rows, "screen"):
        p, brews = r["parameters"], r["brew_metrics"]
        assert len(brews) == 56
        assert r["parameter_count"] == len(r["bounds"])
        assert len(r["starts"]) == 3
        for key, (lower, upper) in r["bounds"].items():
            assert lower <= p[key] <= upper
        objective = sum(b["weight"]*b["trace_mse"] for b in brews)
        assert_allclose(r["objective_sum_squares"], objective, rtol=1e-12, atol=0)
        residuals = []
        for condition in r["conditions_bar"]:
            group = [b for b in brews if b["condition_bar"] == condition]
            residuals.append(np.mean([b["predicted_endpoint_g_s"]-b["observed_endpoint_g_s"] for b in group]))
        assert_allclose(r["condition_residuals_g_s"], residuals, rtol=1e-12, atol=1e-15)
        assert_allclose(r["low_bias_g_s"], np.mean(residuals[:3]), rtol=1e-12, atol=0)
        assert_allclose(r["low_mean_absolute_residual_g_s"], np.mean(np.abs(residuals[:3])), rtol=1e-12)
        high = np.array(r["conditions_bar"]) >= 9
        x = np.array(r["condition_endpoint_line_pressure_bar"])[high]
        y = np.array(r["condition_endpoint_predicted_g_s"])[high]
        assert_allclose(r["slope_ge9_g_s_bar"], np.polyfit(x, y, 1)[0], rtol=1e-12, atol=1e-15)
        assert_allclose(r["onset_flow_difference_g_s"],
                        np.array(r["onset_flow_g_s"])-r["T2F_onset_flow_g_s"], rtol=1e-12, atol=1e-15)
        grid = r["constant_pressure_grid_bar"]
        assert_allclose(r["flow_peak_bar"], grid[np.argmax(r["constant_pressure_endpoint_g_s"])], rtol=1e-12)
        costs = [s["objective_sum_squares"] for s in r["starts"]]
        disagree = max(costs)-min(costs) > 1e-6*max(1., min(costs))
        if r["model"] == "R":
            taus = [s["parameters"]["tau_s"] for s in r["starts"]]
            disagree |= max(taus)/min(taus)-1 > .1
        assert r["start_disagreement"] == disagree
        if r["model"] == "D":
            pressures = np.array([.1, 1., 3., 6., 9., 13.])
            factor = C.threshold_factor(pressures, p["lam_bar"], p["Pd_bar"])[0]
            integral = [quad(lambda u: -np.expm1(-(v-u)/p["Pd_bar"])*
                             np.exp(-u/p["lam_bar"])/p["lam_bar"], 0., v,
                             epsabs=1e-14, epsrel=1e-12)[0] for v in pressures]
            assert_allclose(factor, integral, rtol=1e-12, atol=1e-14)
            h, hp = C.threshold_factor(r["analytic_capacity_peak_bar"], p["lam_bar"], p["Pd_bar"])
            assert_allclose(p["Pstar_bar"]*hp, h, rtol=1e-10, atol=1e-12)
            if p["lam_bar"] < p["Pd_bar"]:
                assert_allclose(r["P0_eff_bar"], -p["Pd_bar"]*np.log1p(-p["lam_bar"]/p["Pd_bar"]), rtol=1e-12)
            else:
                assert "P0_eff_bar" not in r
    plugin = next(r for r in select(rows, "screen") if r["candidate"] == "T3-D x0.5 Pd")
    half = next(r for r in select(rows, "onset_fit") if r["threshold_scale"] == .5 and r["fold"] == "DESCRIPTIVE_ALL")
    assert_allclose(plugin["parameters"]["Pd_bar"], half["parameters"]["Pd_bar"], rtol=1e-12)
    assert "sensitivity detection" in plugin["plugin_label"]


def check_ols(stats):
    assert_allclose(stats["slope"], stats["sum_centered_t_y"]/stats["sum_centered_t_squared"], rtol=1e-12, atol=1e-13)


def test_restart_observation_and_pause_sufficient_statistics(rows):
    episodes = select(rows, "restart_episode")
    assert episodes[0]["source_lines"][0] == 1
    assert episodes[-1]["source_lines"][1] == 1818
    for a, b in zip(episodes[:-1], episodes[1:]):
        assert a["source_lines"][1]+1 == b["source_lines"][0]
        assert a["flowing"] != b["flowing"]
        assert a["end_s"] < b["start_s"]
    first = next(r["last5_mass_slope_g_s"] for r in episodes if r["flowing"])
    for r in episodes:
        assert_allclose(r["duration_s"], r["end_s"]-r["start_s"], rtol=1e-12, atol=0)
        assert_allclose(r["mass_change_g"], r["mass_end_relative_g"]-r["mass_start_relative_g"], rtol=1e-12, atol=1e-13)
        assert_allclose(r["mean_mass_slope_g_s"], r["mass_change_g"]/r["duration_s"], rtol=1e-12, atol=0)
        if r["flowing"]:
            assert r["pressure_min_bar"] > 6.
            check_ols(r["last5_stats"])
            assert_allclose(r["last5_stats"]["time_window_s"][1], r["end_s"], rtol=1e-12)
            assert r["last5_stats"]["time_window_s"][0] >= r["end_s"]-5
            assert_allclose(r["observed_ratio"], r["last5_mass_slope_g_s"]/first, rtol=1e-12)
            if "within_flow_stats" in r:
                check_ols(r["within_flow_stats"])


def test_restart_replay_needed_tau_bounds_and_ratios(rows):
    for r in select(rows, "restart_replay"):
        slopes = np.array(r["fitted_last5_slopes_g_s"])
        for stats in r["fitted_last5_stats"]:
            check_ols(stats)
        assert_allclose(slopes, [s["slope"] for s in r["fitted_last5_stats"]], rtol=1e-12)
        assert_allclose(r["fitted_ratios"], slopes[1:]/slopes[0], rtol=1e-12, atol=0)
        assert_allclose(r["pause_max_abs_predicted_flow"], 0., rtol=1e-12, atol=0)
        assert_allclose(r["pause_max_abs_mass_increment"], 0., rtol=1e-12, atol=0)
        assert_allclose([r["profile_tau_s"][0], r["profile_tau_s"][-1]], [.1, 1000.], rtol=1e-12)
        profile = np.array(r["profile_min_max_ratios"])
        for k, needed in enumerate(r["needed_tau"]):
            env = r["attainable_ratio_envelopes"][k]
            assert env["maximum_ratio"] >= np.max(profile[:, k])-1e-12
            assert env["minimum_ratio"] <= np.min(profile[:, k])+1e-12
            if needed["solutions"]:
                for root in needed["solutions"]:
                    assert_allclose(root["predicted_ratio"], needed["target_ratio"], rtol=1e-12, atol=0)
                    assert root["bracket_tau_s"][0] <= root["tau_s"] <= root["bracket_tau_s"][1]
            else:
                assert needed["target_ratio"] > env["maximum_ratio"] or needed["target_ratio"] < env["minimum_ratio"]
        if r["off_state"] == "line":
            assert "bound, not a model of the pause" in r["pause_interpretation"]
