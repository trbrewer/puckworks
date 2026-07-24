"""Tests for the Paper A P0-5 uncertainty helpers (review MC4).

Offline + deterministic. Exercises the two PURE functions (no PDE solves) that the slow
analysis relies on: the objective-family profiler `_profile_objectives` and the dependence-aware
`paired_clustered_bootstrap`. The slow PDE-backed callers (identifiability_panel /
transfer_skill_vs_baselines) are hand-run, not in CI.
"""
import importlib
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
AB = importlib.import_module("puckworks.validation.slow.angeloni_bracket")


# ── _profile_objectives ───────────────────────────────────────────────────────────
def test_objective_family_structure_and_keys():
    rates = np.geomspace(0.15, 6.5, 18)
    m = np.array([5.0, 6.0, 4.5, 5.5, 6.2, 4.8, 5.1, 5.9, 4.9])
    # NON-degenerate F: the predicted SHAPE varies with rate (not just a scale), so the level
    # cannot fully compensate -> the objectives have a genuine positive minimum with structure.
    F = np.abs(np.array([m * (1.0 + 0.3 * np.sin(0.5 * i + np.arange(len(m))))
                         for i in range(len(rates))])) + 0.1
    fam = AB._profile_objectives(rates, F, m)
    for obj in ("sse", "relative_l2", "huber"):
        assert obj in fam
        for t in ("2pct", "5pct", "10pct", "20pct"):
            s = fam[obj]["sets"][t]
            assert set(s) == {"frac_within", "rate_lo", "rate_hi", "log_width",
                              "lower_censored", "upper_censored"}
            assert 0.0 <= s["frac_within"] <= 1.0
    assert fam["huber_delta"] > 0


def test_degenerate_valley_persists_across_objectives():
    # The inventory-rate degeneracy with a POSITIVE floor: a FIXED shape (m+offset) scaled by
    # 1/L_i, so the level compensates the rate exactly at every point -> the objective is flat
    # at a constant positive misfit across the whole grid (a positive floor, not zero, so the
    # 10%-of-min threshold is well posed).
    rates = np.geomspace(0.15, 6.5, 18)
    m = np.array([5.0, 6.0, 4.5, 5.5, 6.2, 4.8, 5.1, 5.9, 4.9])
    offset = np.array([0.2, -0.15, 0.1, -0.1, 0.2, -0.2, 0.1, -0.1, 0.15])
    L = np.linspace(1.0, 3.0, len(rates))
    F = np.array([(m + offset) / L[i] for i in range(len(rates))])
    fam = AB._profile_objectives(rates, F, m)
    for obj in ("sse", "relative_l2", "huber"):
        s10 = fam[obj]["sets"]["10pct"]
        assert s10["frac_within"] == 1.0                  # flat everywhere
        assert s10["lower_censored"] and s10["upper_censored"]   # right-censored both ends


def test_sharp_objective_localizes():
    # A sharp case: m equals the prediction at exactly one rate; objective rises away from it.
    rates = np.geomspace(0.15, 6.5, 18)
    base = np.array([5.0, 6.0, 4.5, 5.5, 6.2, 4.8, 5.1, 5.9, 4.9])
    i_true = 9
    # shape that changes with rate so the level cannot compensate everywhere
    F = np.array([base * (1.0 + 0.4 * (i - i_true) / len(rates)) ** 2 for i in range(len(rates))])
    m = base * (1.0 + 0.4 * 0.0) ** 2                     # == F[i_true] shape at unit level
    fam = AB._profile_objectives(rates, F, m)
    s10 = fam["sse"]["sets"]["10pct"]
    assert s10["frac_within"] < 1.0                        # NOT flat everywhere
    assert not fam["sse"]["at_boundary"] or fam["sse"]["rate_at_min"] > 0


# ── paired_clustered_bootstrap ────────────────────────────────────────────────────
def _recs(deltas, groups=None, conds=None):
    n = len(deltas)
    groups = groups or ["Arabica:caffeine"] * n
    conds = conds or [(90.0, 9.0)] * n
    return [dict(group=groups[i], grind="C" if i % 2 else "F",
                 T=conds[i][0], p=conds[i][1], delta=float(deltas[i])) for i in range(n)]


def test_zero_delta_ci_brackets_zero():
    recs = _recs([0.0] * 12,
                 groups=["Arabica:caffeine"] * 6 + ["Robusta:caffeine"] * 6,
                 conds=[(88, 6), (88, 6), (93, 9), (93, 9), (98, 12), (98, 12)] * 2)
    for unit in ("cond_in_group", "group"):
        r = AB.paired_clustered_bootstrap(recs, B=500, seed=1, unit=unit)
        assert r["observed_mean_delta_pp"] == 0.0
        assert r["ci95_pp"][0] <= 0.0 <= r["ci95_pp"][1]
        assert r["excludes_zero"] is False


def test_constant_positive_delta_excludes_zero():
    recs = _recs([2.0] * 12,
                 groups=["Arabica:caffeine"] * 6 + ["Robusta:caffeine"] * 6,
                 conds=[(88, 6), (88, 6), (93, 9), (93, 9), (98, 12), (98, 12)] * 2)
    r = AB.paired_clustered_bootstrap(recs, B=500, seed=1, unit="cond_in_group")
    assert r["observed_mean_delta_pp"] == 2.0
    assert r["ci95_pp"] == [2.0, 2.0]               # every resample is 2.0
    assert r["excludes_zero"] is True
    assert r["frac_boot_model_worse"] == 1.0


def test_bootstrap_deterministic_and_units_differ_shape():
    rng = np.random.default_rng(0)
    deltas = rng.normal(-0.4, 3.0, 36)
    groups = sum(([f"g{k}"] * 6 for k in range(6)), [])
    conds = [(88, 6), (88, 6), (93, 9), (93, 9), (98, 12), (98, 12)] * 6
    recs = _recs(deltas, groups=groups, conds=conds)
    a1 = AB.paired_clustered_bootstrap(recs, B=800, seed=7, unit="cond_in_group")
    a2 = AB.paired_clustered_bootstrap(recs, B=800, seed=7, unit="cond_in_group")
    assert a1 == a2                                  # deterministic given seed
    g = AB.paired_clustered_bootstrap(recs, B=800, seed=7, unit="group")
    assert g["unit"] == "group" and g["n_points"] == 36
    # both report the same observed mean (only the resampling unit differs)
    assert a1["observed_mean_delta_pp"] == g["observed_mean_delta_pp"]


def test_bad_unit_raises():
    import pytest
    with pytest.raises(ValueError):
        AB.paired_clustered_bootstrap(_recs([1.0, 2.0]), unit="nonsense")


# ── _oob_coverage_bootstrap (P0-5 sub-analysis C, pure core) ──────────────────────
def test_oob_coverage_perfect_fit_is_zero():
    # every rate predicts m exactly at unit level -> in-bag fit is perfect, OOB error 0.
    m = np.array([5.0, 6.0, 4.5, 5.5, 6.2, 4.8, 5.1, 5.9, 4.9])
    F = np.tile(m, (18, 1))
    r = AB._oob_coverage_bootstrap([(F, m)], 9, n_boot=100, seed=0)
    assert r["oob_pooled_mape_point"] == 0.0
    assert r["coverage_interval95"] == [0.0, 0.0]
    assert r["n_boot_effective"] > 0


def test_oob_coverage_deterministic_and_positive():
    rng = np.random.default_rng(1)
    m = 5.0 + rng.normal(0, 0.5, 9)
    # shape varies with rate so the level cannot fit all conditions -> positive OOB error
    F = np.abs(np.array([m * (1 + 0.2 * np.sin(0.4 * k + np.arange(9))) for k in range(18)])) + 0.1
    a = AB._oob_coverage_bootstrap([(F, m)], 9, n_boot=200, seed=3)
    b = AB._oob_coverage_bootstrap([(F, m)], 9, n_boot=200, seed=3)
    assert a == b                                        # deterministic given seed
    assert a["oob_pooled_mape_point"] > 0
    lo, hi = a["coverage_interval95"]
    assert 0.0 <= lo <= hi
    assert a["n_skipped_empty_oob"] >= 0
