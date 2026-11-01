"""C3b checks use committed CSV inputs/witnesses; no external files or fits."""
import hashlib
import re

import numpy as np
from numpy.testing import assert_allclose
import pytest
from scipy.integrate import quad

from puckworks.analysis import pressure_peak_stage_c3b as C


@pytest.fixture(scope="module")
def rows():
    return C.read_table()


def one(rows, kind):
    return next(r for r in rows if r["record_type"] == kind)


def test_scope_and_completion(rows):
    p = one(rows, "provenance")
    assert p["fit_count"] == 12 and p["start_count"] == 48 and p["bootstrap_count"] == 0
    assert p["cumulative_wall_seconds"] < p["cap_seconds"] == 7200
    assert all(r["claim"] == C.CLAIM for r in rows)
    assert p["module_sha256"] == hashlib.sha256(C.Path(C.__file__).read_bytes()).hexdigest()
    assert all(not r.get("successor_authorized", False) for r in rows)
    summary = (C.OUT / "SUMMARY.md").read_text()
    assert "In-sample fits can mislead and point LOCO does not replace paired refits." in summary
    assert "\u2014" not in summary
    assert not re.search(r"\b(?:MEETS|NEAR|MISSES|PASS)\b", summary)


@pytest.mark.parametrize("index", range(9))
def test_crossing_witnesses_and_edge_cases(rows, index):
    case = one(rows, "numerical_fixtures")["crossings"][index]
    t, q = np.array(case["t"]), np.array(case["q"])
    r = C.crossing_observer(t, q, case["tw"], case["end"])
    for key in ("censored", "criterion", "drop_back", "followup_complete"):
        assert r[key] == case["expected"][key]
    assert_allclose(r["predicted_onset_s"], case["expected"]["predicted_onset_s"], rtol=1e-12)
    expected = {"mass": (False, "mass"), "flow": (False, "flow"), "tie": (False, "tie"),
                "strict equality": (True, "censored"), "wet after end": (True, "censored"),
                "mass at end": (True, "censored")}
    if case["name"] in expected:
        assert (r["censored"], r["criterion"]) == expected[case["name"]]
    if case["name"] == "drop back":
        assert r["drop_back"]
    if case["name"] == "short followup":
        assert not r["followup_complete"] and not r["censored"]
    if case["name"] == "beyond 100":
        assert_allclose(r["predicted_onset_s"], 132.5, rtol=1e-12)
    if r["t_mass_s"] is not None:
        end = r["t_mass_s"]
        points = t[(t > case["tw"]) & (t < end)]
        mass = quad(lambda s: np.interp(s, t, q), case["tw"], end, points=points,
                    epsabs=1e-12, epsrel=1e-12)[0]
        assert_allclose(mass, .5, rtol=1e-12, atol=1e-13)


def test_finite_difference_smooth_switch_and_plateau(rows):
    f = one(rows, "numerical_fixtures")
    case = f["crossings"][0]
    t = np.array(case["t"])

    def evaluate(z):
        r = C.crossing_observer(t, np.full(len(t), z[0]), z[1], case["end"])
        return np.array([r["predicted_onset_s"]]), [r]

    jac, _ = C.finite_jac(evaluate, np.array([.2, 1.]), np.array([0., 0.]), np.array([1., 20.]))
    assert_allclose(jac, [[-.5/.2**2, 1.]], rtol=3e-7, atol=1e-10)
    jac, audit = C.finite_jac(evaluate, np.array([.01, 1.]), np.array([0., 0.]), np.array([1., 20.]))
    assert_allclose(jac, 0., rtol=0, atol=0)
    assert audit["flat_censored_entries"] == 2
    _, audit = C.finite_jac(evaluate, np.array([.1, 1.]), np.array([0., 0.]), np.array([1., 20.]))
    assert audit["branch_switches"] > 0


def test_c2_flow_and_constant_onset_identity(rows):
    f = one(rows, "numerical_fixtures")
    p, t, pressure, mc = np.array(f["parameters"]), np.array(f["t"]), np.array(f["pressure"]), f["mc"]
    assert_allclose(C.flow(p, pressure, t, mc), f["reference_flow"], rtol=1e-12, atol=0)
    assert_allclose(C.flow(p, pressure, t, mc), C.C1.flow_curve(p[:4], pressure, t, mc)[0], rtol=1e-12, atol=0)
    for pressure, expected in zip(f["constant_pressures_bar"], f["constant_onsets_s"]):
        onset = C.constant_onset(p, pressure, mc)
        assert_allclose(onset, expected, rtol=1e-12)
        tw = float(C.wetting(p, pressure))
        capacity = p[0]*np.exp(-pressure/p[1])*p[3]*(-np.expm1(-max(pressure-p[2], 0)/p[3]))
        def q(s):
            return capacity*np.exp(-np.exp(-C.A.delivered_state(np.array(capacity*s/mc))))
        mass = quad(q, tw, onset, epsabs=1e-11, epsrel=1e-11)[0]
        assert mass >= .5-1e-10
        assert float(q(onset)) >= .1-1e-12
        assert abs(mass-.5) < 1e-9 or abs(float(q(onset))-.1) < 1e-12


@pytest.mark.parametrize("name", ["T2-F", "T2 joint (capped)"])
def test_parent_objective_and_metric_replays(rows, name):
    r = next(r for r in rows if r["record_type"] == "parent_replay" and r["candidate"] == name)
    inputs = one(rows, "inputs")
    p = C.C1.flow_parameters(r["parameters"])
    t = np.array(inputs["fit_times_s"])
    mask = np.array(inputs["fit_mask"])
    assert np.array_equal(mask, (t[None, :] >= np.array(inputs["observed_onsets_s"])[:, None]+2) &
                          (t[None, :] <= np.array(inputs["clean_ends_s"])[:, None]))
    q = C.flow(p, np.array(inputs["fit_pressure"]), t, r["parameters"]["Mc_fixed_g"])
    mse = ((q-np.array(inputs["fit_observed_flow"]))**2*mask).sum(axis=1)/mask.sum(axis=1)
    assert_allclose(mse, r["brew_trace_mse"], rtol=1e-12, atol=0)
    jf = np.dot(r["weights"], mse)
    jo = np.dot(r["weights"], np.array(r["onset_errors_s"])**2)
    j = jf if name == "T2-F" else jf/.437**2+jo/4.534**2
    assert_allclose(j, r["saved_objective"], rtol=1e-12, atol=0)
    assert_allclose(j, r["recomputed_objective"], rtol=1e-12, atol=0)
    calculated = C.metrics(r["brew_predictions"])
    for key, expected in r["saved_metrics"].items():
        assert_allclose(calculated[key], expected, rtol=1e-12, atol=0)


FOLDS = ["DESCRIPTIVE_ALL", *[f"HYD-LOCO-{p}" for p in (1., 2., 3.5, 4., 5., 6., 7., 8., 9., 11., 13.)]]


@pytest.mark.parametrize("fold", FOLDS)
def test_fold_training_separation_all_starts_and_censoring(rows, fold):
    r = next(r for r in rows if r["record_type"] == "fit" and r["fold"] == fold)
    data = one(rows, "inputs")
    conditions = np.array(data["conditions_bar"])
    training = np.array([i for i, name in enumerate(data["brew_ids"]) if name in r["training_brews"]])
    if fold != "DESCRIPTIVE_ALL":
        assert np.all(conditions[training] != float(fold.removeprefix("HYD-LOCO-")))
    assert_allclose(r["P0o_cap_bar"], min(5., min(np.array(data["early_pressure_bar"])[training])-.01), rtol=1e-12)
    assert_allclose(r["Mc_fixed_g"], data["saved_mc_by_fold"][fold], rtol=1e-12, atol=0)
    assert len(r["starts"]) == 4
    for index, s in enumerate(r["starts"]):
        expected = C.physical(np.clip(C.coordinates(C.STARTS[index]), np.array(r["lower_coordinates"])+1e-10,
                                    np.array(r["upper_coordinates"])-1e-10))
        assert_allclose([s["initial_parameters"][k] for k in C.FIELDS], expected, rtol=1e-12, atol=0)
        for phase in ("initial", "final"):
            p = np.array([s[phase+"_parameters"][k] for k in C.FIELDS])
            records = C.observe(p, np.array(data["observer_times_s"]), np.array(data["observer_pressure"])[training],
                np.array(data["early_pressure_bar"])[training], np.array(data["raw_ends_s"])[training], r["Mc_fixed_g"])
            assert C.condition_counts(records, conditions[training]) == s[phase+"_training_counts"]
    training_records = [b for b in r["brew_predictions"] if b["role"] == "training"]
    held = [b for b in r["brew_predictions"] if b["role"] == "held_out"]
    assert len(training_records)+len(held) == 56
    assert not any(b["floor_used"] for b in training_records)
    assert r["plateau_label"] == ("possible plateau artefact" if any(b["censored"] for b in training_records) else "none")
    if r["plateau_label"] != "none":
        assert fold in (C.OUT / "SUMMARY.md").read_text()
    assert C.condition_counts(held, np.array([b["condition_bar"] for b in held])) == r["held_out_counts"]
    p = np.array([r["parameters"][k] for k in C.FIELDS])
    predictions = C.observe(p, np.array(data["observer_times_s"]), np.array(data["observer_pressure"]),
        np.array(data["early_pressure_bar"]), np.array(data["raw_ends_s"]), r["Mc_fixed_g"])
    for a, b in zip(predictions, r["brew_predictions"]):
        assert_allclose(a["predicted_onset_s"], b["predicted_onset_s"], rtol=1e-12, atol=0)
        assert (a["criterion"], a["censored"], a["drop_back"]) == (b["criterion"], b["censored"], b["drop_back"])
    assert_allclose(r["objective"], r["flow_objective_component"]+r["onset_objective_component"], rtol=1e-12, atol=0)
    times = np.array(data["fit_times_s"])
    mask = np.array(data["fit_mask"])[training]
    q = C.flow(p, np.array(data["fit_pressure"])[training], times, r["Mc_fixed_g"])
    mse = ((q-np.array(data["fit_observed_flow"])[training])**2*mask).sum(axis=1)/mask.sum(axis=1)
    onset_error = np.array([b["predicted_onset_s"]-b["observed_onset_s"] for b in training_records])
    assert_allclose(np.dot(r["training_weights"], mse)/.437**2, r["flow_objective_component"], rtol=1e-12, atol=0)
    assert_allclose(np.dot(r["training_weights"], onset_error**2)/4.534**2, r["onset_objective_component"], rtol=1e-12, atol=0)
    e = r["extrema"]
    assert_allclose(e["analytic_capacity_peak_bar"], p[2]+p[3]*np.log1p(p[1]/p[3]), rtol=1e-12)
    assert_allclose(e["analytic_wetting_minimum_bar"], p[4]+p[3], rtol=1e-12)
    assert_allclose(e["flow_peak_bar"], e["grid_bar"][np.argmax(e["flow_grid_g_s"])], rtol=1e-12)
    onset_grid = [np.inf if v is None else v for v in e["observer_onset_grid_s"]]
    assert_allclose(e["observer_onset_minimum_bar"], e["grid_bar"][np.argmin(onset_grid)], rtol=1e-12)
    if not r.get("fallback"):
        best = min(s["objective"] for s in r["starts"] if s["success"])
        assert_allclose(best, r["objective"], rtol=1e-12, atol=0)


def test_loco_aggregates_and_predeclared_reading(rows):
    fits = [r for r in rows if r["record_type"] == "fit"]
    assert len(fits) == 12
    held = [b for r in fits for b in r["brew_predictions"] if b["role"] == "held_out"]
    assert len(held) == len({b["brew"] for b in held}) == 56
    r = one(rows, "reading")
    assert r["predeclared_reading"] == C.READING
    expected = C.result_reading(fits)
    assert r["outcome"] == expected["outcome"]
    for key, value in expected["metrics"].items():
        assert_allclose(r["metrics"][key], value, rtol=1e-12, atol=0)
    assert len(r["held_out_1bar_predictions"]) == 5
    assert len(r["metrics"]["endpoint_residuals_g_s"]) == 11
    assert_allclose(r["loco_median_flow_peak_bar"], expected["loco_median_flow_peak_bar"], rtol=1e-12)
