"""C3c numerical and committed-evidence checks; no fits or external data in CI."""
import hashlib
import re
import time

import numpy as np
from numpy.testing import assert_allclose
import pytest

from puckworks.analysis import pressure_peak_stage_c3c as C


def deadline():
    return C.C0.Deadline(time.monotonic()+120)


@pytest.mark.parametrize("p0", [-.5, 0., 1., 2.])
def test_numerical_nested_flow_and_memory_derivatives(p0):
    t = np.array([0., .5, 1., 2., 5., 20., 100.])
    pressure = np.array([[0., .5, 1., 1.1, 1.4, 2., 2.5], [2., 3., 4., 5., 7., 9., 13.]])
    p = np.array([1.2, 12.2, 1., p0])
    q, jac = C.flow(p, pressure, t, 4., 28.7)
    ref, refjac = C.C1.flow_curve([p[0], p[1], p0, 4.], pressure, t, 28.7)
    assert_allclose(q, ref, rtol=1e-12, atol=0)
    assert_allclose(jac[..., [0, 1, 3]], refjac[..., [0, 1, 2]], rtol=1e-12, atol=0)
    if p0 == 0:
        assert_allclose(q, C.flow(p[:3], pressure, t, 4., 28.7)[0], rtol=1e-12, atol=0)
    _, mass, cap = C.flow(p, pressure, t, 4., 28.7, False)
    assert_allclose(mass[:, 0], 0., rtol=1e-12, atol=0)
    assert_allclose(q, cap*np.exp(-np.exp(-mass/28.7)), rtol=1e-12, atol=0)


def test_numerical_power_zero_limits_and_large_powers():
    h, hn, hx = C.opening(np.array([0., .5, 1., 2., 1e200]), 4.)
    assert np.isfinite(np.array([h, hn, hx])).all()
    assert_allclose([h[0], hn[0], hx[0]], 0., rtol=1e-12, atol=0)
    assert_allclose([h[-1], hn[-1], hx[-1]], [1., 0., 0.], rtol=1e-12, atol=0)
    assert_allclose(h[2], -np.expm1(-1.), rtol=1e-12, atol=0)
    assert_allclose(hn[2], 0., rtol=1e-12, atol=0)
    assert_allclose(hx[2], 4/np.e, rtol=1e-12, atol=0)
    assert np.all(h >= 0) and np.all(h <= 1)
    cases = C.numerical_fixtures(deadline())["cases"]
    smooth = next(r for r in cases if r["name"] == "smooth")["diagnostic"]
    assert smooth["half_absolute_error"] < smooth["full_absolute_error"]
    nested = next(r for r in cases if r["name"] == "nested")["diagnostic"]
    assert nested["full_branch_switches"] > 0


def test_numerical_censor_counts_distinguish_structural_and_underflow():
    mask = np.array([[False, True, True]]*3)
    pressure = np.array([[2., .2, .3], [.2, .8, 1.2], [2., .1, .4]])
    counts = C.zero_capacity([1., 12., 2., .5], pressure, mask, 4., np.array([1., 1., 2.]), ["a", "b", "c"])
    assert counts["total"] == counts["structural"] == 2 and counts["numerical"] == 0
    assert counts["brew_ids"] == ["a", "c"]
    safeguard = C.zero_capacity([1.5, 30., 2., 0.], pressure, mask, 4., np.array([1., 1., 2.]), ["a", "b", "c"])
    assert safeguard["total"] == 0
    tiny = C.zero_capacity([1., 12., 4., 0.], np.full((1, 3), 1e-200), mask[:1], 4., np.array([1.]), ["tiny"])
    assert tiny["numerical"] == tiny["total"] == 1 and tiny["structural"] == 0


def test_numerical_materiality_is_form_specific_and_keeps_zero_clause():
    w3 = C.dependence(.3, .4, .1)
    w4 = C.dependence(.11, .21, .1)
    assert not w3["material"] and w4["material"]
    assert_allclose([w3["baseline_g_s"], w4["baseline_g_s"]], [.2, .01], rtol=1e-12, atol=0)
    assert C.dependence(.1, .2, .1)["material"]
    assert not C.dependence(.1, .1, .1)["material"]


def test_numerical_designs_and_start_schedule():
    condition = np.repeat(C.CONDITIONS, 2)
    saved = dict(a_g_s_bar=1.2, Pstar_bar=12.2, P0_bar=1.28)
    total = 0
    for form in ("W3", "W4"):
        for fold in (*C.STANDARD, *C.OMITTED):
            source, train, held, omitted = C.design(condition, fold)
            assert not set(train) & set(held)
            if fold in C.OMITTED:
                assert np.all(condition[omitted] == 3.5)
                assert 3.5 not in condition[train]
                assert len(held) == 2 and len(omitted) == 2
                assert source in ("HYD-LOCO-1.0", "HYD-LOCO-2.0")
            starts = C.start_values(form, saved)
            total += len(starts)
            assert_allclose(starts[1], [1.5, 30., 2.] + ([0.] if form == "W4" else []), rtol=1e-12, atol=0)
    assert total == 98
    assert np.isinf(C.bounds("W4")[1][2])


@pytest.fixture(scope="module")
def rows():
    return C.read_table()


@pytest.fixture(scope="module")
def data(rows):
    r = next(r for r in rows if r["record_type"] == "inputs")
    keys = ("conditions_bar", "early_pressure_bar", "observed_onsets_s", "clean_ends_s",
            "fit_times_s", "fit_pressure", "fit_observed_flow", "fit_mask", "fine_times_s",
            "fine_pressure", "fine_observed_flow", "fine_mask", "late_weights", "observed_late_trend",
            "endpoint_times_s", "endpoint_pressure", "endpoint_observed_g_s")
    return {k: np.array(v) if k in keys else v for k, v in r.items()}


def test_committed_scope_sources_and_plan_identity(rows):
    p = next(r for r in rows if r["record_type"] == "provenance")
    assert p["fit_count"] == 28 and p["start_count"] == 98
    assert p["bootstrap_count"] == p["onset_refits"] == 0
    assert p["cumulative_wall_seconds"] < p["cap_seconds"] == 7200
    assert p["plan_fix_commit"] == C.FIX_COMMIT
    assert p["plan_sha256"] == C.PLAN_SHA256
    assert all(r["claim"] == C.CLAIM for r in rows)
    for name, expected in p["source_sha256"].items():
        if not name.startswith("external/"):
            assert hashlib.sha256((C.ROOT / name).read_bytes()).hexdigest() == expected
    summary = (C.OUT / "SUMMARY.md").read_text()
    assert "\u2014" not in summary
    assert not re.search(r"\b(?:MEETS|NEAR|MISSES|PASS)\b", summary)
    assert "In-sample screens can mislead and point LOCO does not replace paired refits." in summary
    assert not p["successor_authorized"]


def check_parts(parts, condition, mse):
    weights = C.D.condition_weights(condition)
    objective = float(weights@mse)
    assert_allclose(parts["weights"], weights, rtol=1e-12, atol=0)
    assert_allclose(parts["brew_mse"], mse, rtol=1e-12, atol=0)
    assert_allclose(parts["objective"], objective, rtol=1e-12, atol=0)
    assert [r["condition_bar"] for r in parts["conditions"]] == list(np.unique(condition))
    for row in parts["conditions"]:
        use = condition == row["condition_bar"]
        value = float(np.sum((weights*mse)[use]))
        assert row["n"] == sum(use)
        assert_allclose(row["contribution"], value, rtol=1e-12, atol=0)
        assert_allclose(row["share"], value/objective, rtol=1e-12, atol=0)
    assert_allclose(sum(r["share"] for r in parts["conditions"]), 1., rtol=1e-12, atol=0)


@pytest.mark.parametrize("fold", [*C.STANDARD, *C.OMITTED])
def test_reference_objective_replays_and_components(rows, data, fold):
    r = next(r for r in rows if r["record_type"] == "reference" and r["fold"] == fold)
    source, train, held, omitted = C.design(data["conditions_bar"], fold)
    saved = data["saved_parameters_by_fold"][source]
    q = C.C1.flow_curve(C.C1.flow_parameters(saved), data["fit_pressure"][train], data["fit_times_s"], saved["Mc_fixed_g"])[0]
    mse = C.trace_mse(q, data["fit_observed_flow"][train], data["fit_mask"][train])
    check_parts(r["objective"], data["conditions_bar"][train], mse)
    if fold in C.STANDARD:
        assert_allclose(r["objective"]["objective"], saved["objective_sum_squares"], rtol=1e-12, atol=0)
    else:
        assert r["reference_kind"] == "reduced-training plug-in; not refitted"
    if fold == "DESCRIPTIVE_ALL":
        assert_allclose(r["objective"]["objective"], .0719361259858887, rtol=1e-12, atol=0)
    assert r["training_indices"] == list(train)
    assert r["held_out_indices"] == list(held)
    assert r["omitted_indices"] == list(omitted)


@pytest.mark.parametrize("form,fold", [(f, h) for f in ("W3", "W4") for h in (*C.STANDARD, *C.OMITTED)])
def test_fit_evidence_training_starts_predictions_and_diagnostics(rows, data, form, fold):
    r = next(r for r in rows if r["record_type"] == "fit" and r["candidate"] == form and r["fold"] == fold)
    source, train, held, omitted = C.design(data["conditions_bar"], fold)
    saved = data["saved_parameters_by_fold"][source]
    assert r["training_indices"] == list(train) and r["held_out_indices"] == list(held)
    assert r["omitted_indices"] == list(omitted)
    assert r["onset_parameters"] == saved["onset_parameters"]
    assert r["onset_bank_training_indices"] == list(C.design(data["conditions_bar"], source)[1])
    assert_allclose([r["Pd_fixed_bar"], r["Mc_fixed_g"]], [saved["Pd_bar"], saved["Mc_fixed_g"]], rtol=1e-12, atol=0)
    assert r["onset_audit"]["training_floor_active_count"] == 0
    ids = [data["brew_ids"][i] for i in train]
    lower, upper = C.bounds(form)
    starts = C.start_values(form, saved)
    assert len(starts) == len(r["starts"])
    for original, start in zip(starts, r["starts"]):
        z = np.clip(C.coordinates(original), lower+1e-10, upper-1e-10)
        assert_allclose(start["initial_coordinates"], z, rtol=1e-12, atol=0)
        for phase in ("initial", "final"):
            p = C.parameters(start[phase+"_parameters"], form)
            assert C.zero_capacity(p, data["fit_pressure"][train], data["fit_mask"][train], saved["Pd_bar"],
                data["conditions_bar"][train], ids) == start[phase+"_training_counts"]
            assert C.kink_counts(p, data["fit_pressure"][train], data["fit_mask"][train], ids) == start[phase+"_kink_counts"]
        if form == "W4" and original[2] == 1.:
            assert "initial_jacobian_check" in start
    assert r["starts"][1]["initial_training_counts"]["total"] == 0
    attempts = r["starts"] + ([r["fallback"]] if r.get("fallback") else [])
    selected = attempts[r["selected_start"]]
    assert selected["success"]
    assert_allclose(selected["objective"], min(s["objective"] for s in attempts if s["success"]), rtol=1e-12, atol=0)
    p = C.parameters(r["parameters"], form)
    assert_allclose(p, C.parameters(selected["final_parameters"], form), rtol=1e-12, atol=0)
    for prefix in ("fit", "fine"):
        q = C.flow(p, data[prefix+"_pressure"][train], data[prefix+"_times_s"], saved["Pd_bar"], saved["Mc_fixed_g"], False)[0]
        mse = C.trace_mse(q, data[prefix+"_observed_flow"][train], data[prefix+"_mask"][train])
        check_parts(r["objective" if prefix == "fit" else "fine_objective"], data["conditions_bar"][train], mse)
    endpoint, mass, cap = C.flow(p, data["endpoint_pressure"], data["endpoint_times_s"], saved["Pd_bar"], saved["Mc_fixed_g"], False)
    fine = C.flow(p, data["fine_pressure"], data["fine_times_s"], saved["Pd_bar"], saved["Mc_fixed_g"], False)[0]
    mse = C.trace_mse(fine, data["fine_observed_flow"], data["fine_mask"])
    trends = (fine*data["late_weights"]).sum(axis=1)
    onset = C.C0.onset_curve(C.C1.onset_parameters(saved["onset_parameters"]), data["early_pressure_bar"])[0]
    for i, brew in enumerate(r["brew_predictions"]):
        assert brew["brew"] == data["brew_ids"][i]
        assert brew["role"] == ("training" if i in train else "held_out" if i in held else "omitted")
        assert_allclose([brew["endpoint_prediction_g_s"], brew["hydraulic_mass_100_g"], brew["capacity_100_g_s"],
                         brew["trace_mse"], brew["predicted_late_trend_g_s_s"], brew["predicted_onset_s"]],
                        [endpoint[i, -1], mass[i, -1], cap[i, -1], mse[i], trends[i], onset[i]], rtol=1e-12, atol=0)
        assert_allclose(brew["endpoint_residual_g_s"], endpoint[i, -1]-data["endpoint_observed_g_s"][i], rtol=1e-12, atol=0)
    assert r["selected_training_counts"] == selected["final_training_counts"]
    reference = next(v for v in rows if v["record_type"] == "reference" and v["fold"] == fold)
    gain = reference["objective"]["objective"]-r["objective"]["objective"]
    fine_gain = reference["fine_objective"]["objective"]-r["fine_objective"]["objective"]
    assert_allclose([r["coarse_gain_vs_T2F"], r["fine_gain_vs_T2F"]], [gain, fine_gain], rtol=1e-12, atol=0)
    assert r["grid_gain_unresolved"] == (gain > 0 and (fine_gain <= 0 or abs(gain-fine_gain) >= gain))
    e = r["extrema"]
    assert 1. <= e["analytic_capacity_peak_bar"] <= 13.
    assert_allclose(e["flow_peak_bar"], e["grid_bar"][np.argmax(e["flow_grid_g_s"])], rtol=1e-12, atol=0)
    at_peak = C.capacity(p, np.array(e["analytic_capacity_peak_bar"]), saved["Pd_bar"])[0]
    sampled = C.capacity(p, np.array(e["grid_bar"]), saved["Pd_bar"])[0]
    assert at_peak >= max(sampled)


def test_readings_exclude_extra_folds_and_use_form_specific_materiality(rows, data):
    for form in ("W3", "W4", "T2-F"):
        r = next(r for r in rows if r["record_type"] == "reading" and r["candidate"] == form)
        fits = [f for f in rows if f["record_type"] == ("reference" if form == "T2-F" else "fit")
                and f["candidate"] == form and f["fold"] in C.STANDARD]
        held = [b for f in fits for b in f["brew_predictions"] if b["role"] == "held_out"]
        assert len(held) == len({b["brew"] for b in held}) == 56
        calculated = C.O.metrics(held)
        for field in ("endpoint_residuals_g_s", "endpoint_rmse_g_s", "trace_rmse_g_s", "onset_rmse_s", "slope_g_s_bar", "low_bias_g_s", "low_mae_g_s"):
            assert_allclose(r["metrics"][field], calculated[field], rtol=1e-12, atol=0)
        peaks = [f["extrema"]["analytic_capacity_peak_bar"] for f in fits if f["fold"] != "DESCRIPTIVE_ALL"]
        assert_allclose(r["analytic_peak_fold_median_bar"], np.median(peaks), rtol=1e-12, atol=0)
        if form == "T2-F":
            saved = next(v for v in rows if v["record_type"] == "saved_comparator" and v["candidate"] == form)
            for key in ("endpoint_rmse_g_s", "trace_rmse_g_s", "onset_rmse_s", "slope_g_s_bar"):
                assert_allclose(r["metrics"][key], saved[key], rtol=1e-12, atol=0)
            continue
        assert len(r["n_by_fold"]) == 14
        for d in r["omission_dependence"]:
            h = d["condition_bar"]
            fold = f"HYD-LOCO-{h}"
            get = lambda kind, name, ff: next(v for v in rows if v["record_type"] == kind and v["candidate"] == name and v["fold"] == ff)
            standard = get("fit", form, fold)["held_out_metrics"]["endpoint_residuals_g_s"][0]
            omitted = get("fit", form, fold+"-OMIT-3.5")["held_out_metrics"]["endpoint_residuals_g_s"][0]
            reference = get("reference", "T2-F", fold)["held_out_metrics"]["endpoint_residuals_g_s"][0]
            baseline = abs(standard-reference)
            assert_allclose(d["baseline_g_s"], baseline, rtol=1e-12, atol=0)
            assert d["material"] == (abs(omitted-standard) > baseline)


def test_pressure_audit_and_mask_fixtures(rows, data):
    audits = [r for r in rows if r["record_type"] == "pressure_audit"]
    assert len(audits) == 9
    for r in audits:
        p, t = np.array(r["native_pressure_through_100_bar"]), np.array(r["native_times_through_100_s"])
        assert np.all(t >= 0) and np.all(t <= 100)
        assert_allclose([r["min_pressure_bar"], r["max_pressure_bar"], r["early_pressure_bar"]],
                        [min(p), max(p), np.median(p[t <= 2])], rtol=1e-12, atol=0)
        a, b, c = r["machine_coefficients"]
        q = r["endpoint_observed_g_s"]
        assert_allclose(r["basket_endpoint_bar"], r["endpoint_pressure_bar"]-(a*q*q+b*q+c), rtol=1e-12, atol=0)
    for prefix in ("fit", "fine"):
        expected = ((data[prefix+"_times_s"][None, :] >= data["observed_onsets_s"][:, None]+2) &
                    (data[prefix+"_times_s"][None, :] <= data["clean_ends_s"][:, None]))
        assert np.array_equal(data[prefix+"_mask"], expected)
