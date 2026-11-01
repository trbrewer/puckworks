"""C3d numerical checks and committed CSV twins; no fitting or raw data in CI."""
import copy
import hashlib
import time
from types import SimpleNamespace

import numpy as np
from numpy.testing import assert_allclose
import pytest

from puckworks.analysis import pressure_peak_stage_c3d as S


def budget():
    return S.C.C0.Deadline(time.monotonic()+120)


def assert_values(actual, expected):
    """CSV omits null cells; numerical replays use the declared tolerance."""
    if isinstance(expected, dict):
        for key, value in expected.items():
            assert_values(actual.get(key), value)
    elif isinstance(expected, (list, tuple)):
        assert len(actual) == len(expected)
        for a, b in zip(actual, expected):
            assert_values(a, b)
    elif isinstance(expected, float):
        assert_allclose(actual, expected, rtol=1e-12, atol=0)
    else:
        assert actual == expected


def test_numerical_nested_identities_and_halving():
    fixture = S.numerical_fixtures(budget())
    assert fixture["nested_replays"]
    j = fixture["smooth_jacobian"]
    assert j["half_absolute_error"] < j["full_absolute_error"]
    assert j["full_branch_switches"] == j["half_branch_switches"] == 0
    for n in (1., 2., 2.5, 4.):
        p = np.array([1.2, 12.2, n, 4.])
        c, dc = S.capacity(p, np.array([0., .5, 4., 12.]), "A")
        x = np.array([0., .5, 4., 12.])/4.
        u = x**n
        analytic = p[0]*p[3]*np.exp(-4*x/p[1])*(-np.expm1(-u)-n*u*np.exp(-u))
        assert_allclose(dc[..., 3], analytic, rtol=1e-12, atol=0)
        assert_allclose(c[0], 0., rtol=1e-12, atol=0)
        assert_allclose(dc[0], 0., rtol=1e-12, atol=0)


def test_numerical_bounds_starts_and_exact_scope():
    saved = dict(a_g_s_bar=1.2, Pstar_bar=12.2, P0_bar=1.28, Pd_bar=7.37)
    assert len(S.SCHEDULE) == 13
    assert sum(len(S.start_values(arm, saved)) for arm, _ in S.SCHEDULE) == 58
    assert sum(fold == "DESCRIPTIVE_ALL" for _, fold in S.SCHEDULE) == 1
    starts = S.start_values("A", saved)
    assert [group for group, _ in starts] == ["saved_onset_Pd", "4.0_bar"]*3
    assert_allclose([p[3] for _, p in starts], [7.37, 4.]*3, rtol=1e-12, atol=0)
    assert_allclose(S.start_values("B-W4", saved)[-1][1], [1.2, 12.2, 1., 1.28],
                    rtol=1e-12, atol=0)
    lo, hi = S.bounds("A")
    assert_allclose(np.exp([lo[3], hi[3]]), [.1, 100.], rtol=1e-12, atol=0)
    assert np.isinf(hi[2])
    for arm in ("A", "B-W3", "B-W4"):
        for _, p in S.start_values(arm, saved):
            assert_allclose(S.physical(S.coordinates(p, arm), arm), p, rtol=1e-12, atol=0)


def test_numerical_helps_is_strict_and_seed_ties_are_not_dependence():
    assert S.helps(.1, -.2, .3)["helps"]
    assert not S.helps(.2, -.2, .3)["helps"]
    assert not S.helps(.2, -.3, .1)["helps"]
    assert S.helps(np.nextafter(.2, 0), -.2, .3)["helps"]
    attempts = [dict(label=str(i), seed_group=g, success=True, objective=j,
                     final_parameters=dict(Pd_bar=pd, n=n))
                for i, (g, j, pd, n) in enumerate([
                    ("saved_onset_Pd", .1, 5., 2.), ("4.0_bar", .1+1e-10, 7., 3.)])]
    audit = S.seed_groups(attempts, 0)
    assert not audit["rule4_start_dependence"]
    assert audit["groups"]["4.0_bar"]["reaches_selected"]
    attempts[1]["objective"] = .1+2e-6
    assert S.seed_groups(attempts, 0)["rule4_start_dependence"]
    attempts[1]["success"] = False
    audit = S.seed_groups(attempts, 0)
    assert audit["rule4_start_dependence"]
    assert audit["groups"]["4.0_bar"]["failed_labels"] == ["1"]


def synthetic_context():
    conditions = np.repeat(S.C.CONDITIONS, 2)
    t = np.array([0., 1., 2., 4., 8.])
    pressure = np.tile(np.array([0., .5, 1., 1.5, 2.]), (len(conditions), 1))
    g = SimpleNamespace(t=t, pressure=pressure, flow=np.ones_like(pressure),
                        mask=np.ones_like(pressure, dtype=bool))
    saved = {fold: dict(Mc_fixed_g=28., Pd_bar=7., a_g_s_bar=1., Pstar_bar=12., P0_bar=1.2)
             for fold in S.FOLDS if "-OMIT-" not in fold}
    return SimpleNamespace(brews=SimpleNamespace(condition=conditions), coarse=g, saved=saved,
                           delays=np.zeros((len(conditions), 3)), early=np.ones(len(conditions)))


@pytest.mark.parametrize("fold", S.HELD)
def test_numerical_training_isolation(fold):
    ctx = synthetic_context()
    source, train, held, omitted = S.C.design(ctx.brews.condition, fold)
    e1 = S.training_evaluator(ctx, "A", fold, budget())
    z = S.coordinates([1., 12., 2., 4.], "A")
    before = e1(z)
    altered = copy.deepcopy(ctx)
    unused = np.r_[held, omitted]
    altered.coarse.flow[unused] = np.nan
    altered.coarse.pressure[unused] = np.nan
    altered.coarse.mask[unused] = False
    altered.delays[:] = np.nan
    altered.early[:] = np.nan
    altered.saved[source]["onset_parameters"] = {"unusable": np.nan}
    e2 = S.training_evaluator(altered, "A", fold, budget())
    for left, right in zip(before, e2(z)):
        assert_allclose(left, right, rtol=1e-12, atol=0)
    assert e2.pressure.shape[0] == len(train)
    assert not set(train) & set(unused)


def test_numerical_nonfinite_evaluation_stops():
    ctx = synthetic_context()
    ctx.coarse.flow[:] = np.nan
    e = S.training_evaluator(ctx, "A", "HYD-LOCO-1.0", budget())
    with pytest.raises(FloatingPointError, match="Nonfinite evaluation"):
        e(S.coordinates([1., 12., 2., 4.], "A"))


@pytest.fixture(scope="module")
def rows():
    return S.read_table()


@pytest.fixture(scope="module")
def data(rows):
    raw = next(r for r in rows if r["record_type"] == "inputs")
    keys = ("conditions_bar", "fit_times_s", "fit_pressure", "fit_observed_flow", "fit_mask",
            "fine_times_s", "fine_pressure", "fine_observed_flow", "fine_mask",
            "endpoint_times_s", "endpoint_pressure", "endpoint_observed_g_s")
    return {k: np.array(v) if k in keys else v for k, v in raw.items()}


def check_parts(saved, condition, mse):
    calculated = S.C.objective_parts(condition, mse)
    for key in ("objective", "weights", "brew_mse"):
        assert_allclose(saved[key], calculated[key], rtol=1e-12, atol=0)
    assert len(saved["conditions"]) == len(calculated["conditions"])
    for a, b in zip(saved["conditions"], calculated["conditions"]):
        assert_allclose(list(a.values()), list(b.values()), rtol=1e-12, atol=0)


def test_committed_scope_sources_and_exposure(rows):
    p = next(r for r in rows if r["record_type"] == "provenance")
    assert p["fit_count"] == 13 and p["start_count"] == 58
    assert p["bootstrap_count"] == p["onset_refits"] == 0
    assert p["cumulative_wall_seconds"] < p["cap_seconds"] == 7200
    assert p["plan_sha256"] == S.PLAN_SHA256
    for name, digest in p["source_sha256"].items():
        if not name.startswith("external/"):
            assert hashlib.sha256((S.ROOT / name).read_bytes()).hexdigest() == digest
    fits = [r for r in rows if r["record_type"] == "fit"]
    assert [(r["candidate"], r["fold"]) for r in fits] == list(S.SCHEDULE)
    assert all(r["status"] == "complete" for r in fits)
    assert all("TARGET_EXPOSED" in r["exposure"] for r in fits)
    assert all("held-out onset times" in r["exposure"] for r in fits if r["candidate"] != "A")
    assert all("onset_parameters" not in r for r in fits)
    assert all("predicted_onset_s" not in b for r in fits for b in r["brew_predictions"])
    summary = (S.OUT / "SUMMARY.md").read_text()
    assert "\u2014" not in summary
    assert "in-sample" in summary and "PHYSICAL_VALIDATION=NOT_ESTABLISHED" in summary


@pytest.mark.parametrize("fold", S.FOLDS)
def test_committed_reference_replay(rows, data, fold):
    row = next(r for r in rows if r["record_type"] == "reference" and r["fold"] == fold)
    source, train, held, omitted = S.C.design(data["conditions_bar"], fold)
    saved = data["saved_parameters_by_fold"][source]
    for prefix in ("fit", "fine"):
        q = S.C1.flow_curve(S.C1.flow_parameters(saved), data[prefix+"_pressure"][train],
                            data[prefix+"_times_s"], saved["Mc_fixed_g"])[0]
        mse = S.C.trace_mse(q, data[prefix+"_observed_flow"][train], data[prefix+"_mask"][train])
        check_parts(row["objective" if prefix == "fit" else "fine_objective"],
                    data["conditions_bar"][train], mse)
    if fold not in S.C.OMITTED:
        assert_allclose(row["objective"]["objective"], saved["objective_sum_squares"], rtol=1e-12, atol=0)
    else:
        assert "plug-in" in row["reference_kind"]
    if fold == "DESCRIPTIVE_ALL":
        assert_allclose(row["objective"]["objective"], .0719361259858887, rtol=1e-12, atol=0)
    assert row["training_indices"] == list(train)
    assert row["held_out_indices"] == list(held) and row["omitted_indices"] == list(omitted)


@pytest.mark.parametrize("arm,fold", S.SCHEDULE)
def test_committed_fit_inputs_starts_losses_predictions(rows, data, arm, fold):
    row = next(r for r in rows if r["record_type"] == "fit" and r["candidate"] == arm and r["fold"] == fold)
    source, train, held, omitted = S.C.design(data["conditions_bar"], fold)
    saved = data["saved_parameters_by_fold"][source]
    assert row["training_indices"] == list(train)
    assert row["held_out_indices"] == list(held) and row["omitted_indices"] == list(omitted)
    assert_allclose(row["Mc_fixed_g"], saved["Mc_fixed_g"], rtol=1e-12, atol=0)
    if arm != "A":
        assert_allclose(row["parameters"]["Pd_bar"], S.FIXED_PD, rtol=1e-12, atol=0)
    ids = [data["brew_ids"][i] for i in train]
    lo, hi = S.bounds(arm)
    for (group, original), start in zip(S.start_values(arm, saved), row["starts"]):
        assert start["seed_group"] == group
        assert_allclose(start["original_start_coordinates"], S.coordinates(original, arm), rtol=1e-12, atol=0)
        assert_allclose(start["initial_coordinates"], np.clip(S.coordinates(original, arm), lo+1e-10, hi-1e-10),
                        rtol=1e-12, atol=0)
        for phase in ("initial", "final"):
            p = S.parameters(start[phase+"_parameters"], arm)
            shape, pd = S.split(p, arm)
            counts = S.C.zero_capacity(shape, data["fit_pressure"][train], data["fit_mask"][train],
                                       pd, data["conditions_bar"][train], ids)
            assert counts == start[phase+"_training_counts"]
            assert S.C.kink_counts(shape, data["fit_pressure"][train], data["fit_mask"][train], ids) == start[phase+"_kink_counts"]
            q = S.flow(p, data["fit_pressure"][train], data["fit_times_s"], saved["Mc_fixed_g"], arm, False)[0]
            loss = S.D.condition_weights(data["conditions_bar"][train]) @ S.C.trace_mse(
                q, data["fit_observed_flow"][train], data["fit_mask"][train])
            assert_allclose(start["initial_objective" if phase == "initial" else "objective"],
                            loss, rtol=1e-12, atol=0)
    attempts = row["starts"]+([row["fallback"]] if row.get("fallback") else [])
    selected = attempts[row["selected_start"]]
    assert selected["success"]
    assert_allclose(selected["objective"], min(r["objective"] for r in attempts if r["success"]),
                    rtol=1e-12, atol=0)
    if arm == "A":
        assert_values(row["seed_audit"], S.seed_groups(attempts, row["selected_start"]))
    p = S.parameters(row["parameters"], arm)
    for prefix in ("fit", "fine"):
        q = S.flow(p, data[prefix+"_pressure"][train], data[prefix+"_times_s"], saved["Mc_fixed_g"], arm, False)[0]
        mse = S.C.trace_mse(q, data[prefix+"_observed_flow"][train], data[prefix+"_mask"][train])
        check_parts(row["objective" if prefix == "fit" else "fine_objective"], data["conditions_bar"][train], mse)
    q, mass, cap = S.flow(p, data["endpoint_pressure"], data["endpoint_times_s"], saved["Mc_fixed_g"], arm, False)
    for i, brew in enumerate(row["brew_predictions"]):
        assert brew["role"] == ("training" if i in train else "held_out" if i in held else "omitted")
        assert_allclose([brew["endpoint_prediction_g_s"], brew["hydraulic_mass_100_g"], brew["capacity_100_g_s"],
                         brew["endpoint_residual_g_s"]],
                        [q[i, -1], mass[i, -1], cap[i, -1], q[i, -1]-data["endpoint_observed_g_s"][i]],
                        rtol=1e-12, atol=0)
    assert_values(row["condition_predictions"], S.condition_records(row["brew_predictions"]))
    ref = next(r for r in rows if r["record_type"] == "reference" and r["fold"] == fold)
    gain = ref["objective"]["objective"]-row["objective"]["objective"]
    fine_gain = ref["fine_objective"]["objective"]-row["fine_objective"]["objective"]
    assert row["grid_gain_unresolved"] == (gain > 0 and (fine_gain <= 0 or abs(gain-fine_gain) >= gain))
    e = S.Evaluator(data["fit_pressure"][train], data["fit_times_s"], data["fit_observed_flow"][train],
                    data["fit_mask"][train], data["conditions_bar"][train], saved["Mc_fixed_g"], arm, budget())
    diag = S.jacobian_diagnostic(e, np.array(selected["final_coordinates"]), lo, hi)
    assert_allclose(diag["analytic_norm"], row["jacobian_check"]["analytic_norm"], rtol=1e-12, atol=0)
    # FD error norms subtract nearly equal floats. Replay the declared halving
    # comparison and branch counts, without inventing a cross-platform band
    # for the tiny cancellation remainder itself.
    for key in ("full_branch_switches", "half_branch_switches", "half_step_error_decreases"):
        assert diag[key] == row["jacobian_check"][key]
    for key in ("full_absolute_error", "half_absolute_error", "half_step_absolute_change"):
        assert np.isfinite(diag[key]) and diag[key] >= 0


def test_committed_fd_ratios(rows):
    """Check saved arithmetic only; no additional FD evaluation or tolerance."""
    checks = [r["smooth_jacobian"] for r in rows if r["record_type"] == "numerical_fixtures"]
    for row in rows:
        if row["record_type"] != "fit":
            continue
        checks.append(row["jacobian_check"])
        attempts = row["starts"]+([row["fallback"]] if row.get("fallback") else [])
        checks.extend(s["initial_jacobian_check"] for s in attempts if "initial_jacobian_check" in s)
    assert checks
    for check in checks:
        norm = check["analytic_norm"]
        for relative, absolute in (
            ("full_relative_error", "full_absolute_error"),
            ("half_relative_error", "half_absolute_error"),
            ("half_step_relative_change", "half_step_absolute_change"),
        ):
            if norm:
                assert_allclose(check[relative], check[absolute]/norm, rtol=1e-12, atol=0)
            else:
                assert check[relative] is None
        assert check["half_step_error_decreases"] == (
            check["half_absolute_error"] < check["full_absolute_error"])


def test_committed_comparators_and_unpooled_helps(rows):
    fits = [r for r in rows if r["record_type"] == "fit"]
    references = [r for r in rows if r["record_type"] == "reference"]
    prior = [r for r in rows if r["record_type"] == "comparator"]
    expected_prior = S.comparators()
    assert len(prior) == len(expected_prior)
    for saved, expected in zip(prior, expected_prior):
        assert_values(saved, expected)
    expected = S.reading(fits, references, prior)
    actual = [r for r in rows if r["record_type"] in ("held_out_comparison", "interpretation")]
    assert len(actual) == len(expected) == 7
    for saved, calculated in zip(actual, expected):
        assert_values(saved, calculated)
    flags = actual[-1]["fixes_by_arm"]
    for arm in flags:
        r = [v for v in actual[:-1] if v["candidate"] == arm]
        assert len(r) == 2 and flags[arm] == all(v["helps"] for v in r)
