"""PR-04 — the exact weighted-median level profile, proved and property-tested.

Protocol V2 makes exact level profiling load-bearing for P0-G8, while the premise audit had it
recorded as implemented-but-unproved and deferred to P0-G6 — which is *downstream* of P0-G8. The
dependency was backwards, so the proposition is closed here, before the freeze.

**Proposition.** For fixed `κ`, with `y_i > 0` and `f_i(κ) > 0`,

    MAPE(I; κ) = (100/n)·Σ_i |y_i − I·f_i| / y_i
               = (100/n)·Σ_i w_i·|I − r_i|,      r_i = y_i/f_i,  w_i = f_i/y_i > 0.

This is a positive weighted absolute-deviation objective in `I`. Its minimiser set is exactly the
weighted-median interval

    {I : total weight strictly left of I ≤ W/2  and  total weight strictly right of I ≤ W/2}

which is a closed interval `[I_lower, I_upper]`, and the objective is **exactly constant** on it.

**Consequences, which are what the protocol needs.**

1. a deterministic lower weighted median may be used for serialisation;
2. the complete minimiser interval is archived;
3. the tie width is *inventory-level identification information*, **not objective error** — it is in
   inventory units while `J` is in percentage points, so adding it to a `J` budget is dimensionally
   invalid. Protocol V2 previously did exactly that;
4. the profiled value is continuous as positive `f` approaches positive `f_inf`, which is what lets
   the endpoint classification compare `J_inf` with a threshold at all.

The tests below are property-based against a direct convex reference, not against remembered numbers.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.validation.slow import angeloni_bracket as AB  # noqa: E402


def objective(level, f, m):
    """MAPE in percentage points at a given inventory level."""
    return float(np.mean(np.abs(level * np.asarray(f, float) - np.asarray(m, float))
                         / np.asarray(m, float)) * 100.0)


def minimiser_interval(f, m):
    """The complete weighted-median interval, computed directly from the definition."""
    f = np.asarray(f, float)
    m = np.asarray(m, float)
    r = m / f
    w = f / m
    order = np.argsort(r)
    r, w = r[order], w[order]
    total = w.sum()
    lower = upper = None
    for i in range(len(r)):
        left = w[:i].sum()                      # strictly left of r[i]
        right = w[i + 1:].sum()                 # strictly right of r[i]
        if left <= total / 2 + 1e-15 and right <= total / 2 + 1e-15:
            if lower is None:
                lower = r[i]
            upper = r[i]
    return float(lower), float(upper)


def brute_force_minimum(f, m, n=200001):
    """Direct convex reference: dense scan over the level."""
    r = np.asarray(m, float) / np.asarray(f, float)
    grid = np.linspace(r.min(), r.max(), n)
    vals = [objective(c, f, m) for c in grid]
    i = int(np.argmin(vals))
    return float(grid[i]), float(vals[i])


# ── the proposition ──────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("seed", range(12))
def test_production_level_attains_the_direct_convex_minimum(seed):
    rng = np.random.default_rng(seed)
    n = int(rng.integers(2, 14))
    f = rng.uniform(0.05, 3.0, n)
    m = rng.uniform(0.05, 6.0, n)

    level, mape = AB._mape_level(f, m)
    _grid_level, grid_mape = brute_force_minimum(f, m)
    assert mape <= grid_mape + 1e-9, (seed, mape, grid_mape)
    assert objective(level, f, m) == pytest.approx(mape, rel=1e-12)


@pytest.mark.parametrize("seed", range(8))
def test_the_objective_is_exactly_constant_across_the_minimiser_interval(seed):
    """Consequence 3: the tie is an inventory fact, not an objective uncertainty."""
    rng = np.random.default_rng(1000 + seed)
    n = 2 * int(rng.integers(1, 6))                     # even n makes flat intervals common
    f = rng.uniform(0.2, 2.0, n)
    m = rng.uniform(0.2, 4.0, n)

    lo, hi = minimiser_interval(f, m)
    if hi <= lo:
        # generic case; the constructed tie fixture covers the flat interval explicitly
        lo, hi = minimiser_interval(TIE_FIXTURE_F, TIE_FIXTURE_M)
        f, m = TIE_FIXTURE_F, TIE_FIXTURE_M
    for s in np.linspace(0.0, 1.0, 9):
        level = lo + s * (hi - lo)
        assert objective(level, f, m) == pytest.approx(objective(lo, f, m), rel=1e-12)


#: A tie is not generic here. Because `w_i = f_i/y_i` and `r_i = y_i/f_i`, weight and ratio are
#: inversely locked: `w_i = 1/r_i`. Small ratios therefore carry large weight, which pulls the
#: weighted median down and makes exact balance a measure-zero event. With n = 2 a tie would require
#: `w_1 = w_2`, hence `r_1 = r_2`, which is the degenerate case.
#:
#: An exact tie needs the weight at the lower group to equal the weight above it. The SMALLEST
#: non-degenerate instance is THREE observations, r = [1, 2, 2]: w = [1, ½, ½], so the weight at
#: r = 1 equals the total weight at r = 2 and every I in [1, 2] minimises. An earlier comment here
#: called the six-point r = [1,1,2,2,2,2] the smallest clean instance, which was false; both are
#: retained below, the three-point one as the primary fixture.
TIE_FIXTURE_F = np.ones(3)
TIE_FIXTURE_M = np.array([1.0, 2.0, 2.0])

#: The six-point instance, kept as a second witness rather than as "the smallest".
TIE_FIXTURE6_F = np.ones(6)
TIE_FIXTURE6_M = np.array([1.0, 1.0, 2.0, 2.0, 2.0, 2.0])


def test_the_weighted_median_is_generically_unique_for_this_objective():
    """A property of the coupling, and the reason flat intervals are rare rather than common."""
    rng = np.random.default_rng(23)
    ties = 0
    for _ in range(200):
        n = int(rng.integers(2, 9))
        f = rng.uniform(0.2, 2.0, n)
        m = rng.uniform(0.2, 4.0, n)
        lo, hi = minimiser_interval(f, m)
        ties += hi > lo + 1e-12
    assert ties == 0, "an exact tie on random draws would contradict w_i = 1/r_i coupling"


@pytest.mark.parametrize("f,m", [(TIE_FIXTURE_F, TIE_FIXTURE_M),
                                 (TIE_FIXTURE6_F, TIE_FIXTURE6_M)])
def test_a_constructed_tie_gives_an_exactly_flat_interval(f, m):
    lo, hi = minimiser_interval(f, m)
    assert lo == pytest.approx(1.0) and hi == pytest.approx(2.0)
    assert objective(lo, f, m) == pytest.approx(objective(hi, f, m), rel=1e-12)


def test_three_observations_suffice_for_a_tie():
    """The corrected minimality claim: n = 3 is enough, not n = 6."""
    lo, hi = minimiser_interval(np.ones(3), np.array([1.0, 2.0, 2.0]))
    assert hi > lo + 1e-12


def test_the_production_choice_is_inside_the_interval_and_deterministic():
    """Lower weighted median is a serialisation convention; it must not move the objective."""
    rng = np.random.default_rng(7)
    for _ in range(20):
        n = 2 * int(rng.integers(1, 5))
        f = rng.uniform(0.3, 2.0, n)
        m = rng.uniform(0.3, 3.0, n)
        level, _ = AB._mape_level(f, m)
        lo, hi = minimiser_interval(f, m)
        assert lo - 1e-12 <= level <= hi + 1e-12
        assert AB._mape_level(f, m)[0] == level          # deterministic


# ── invariances the protocol relies on ───────────────────────────────────────────────────────
def test_permutation_invariance():
    rng = np.random.default_rng(3)
    f = rng.uniform(0.2, 2.0, 9)
    m = rng.uniform(0.2, 4.0, 9)
    base = AB._mape_level(f, m)[1]
    for _ in range(5):
        p = rng.permutation(len(f))
        assert AB._mape_level(f[p], m[p])[1] == pytest.approx(base, rel=1e-12)


def test_a_single_observation_is_fitted_exactly():
    level, mape = AB._mape_level(np.array([2.0]), np.array([5.0]))
    assert level == pytest.approx(2.5)
    assert mape == pytest.approx(0.0, abs=1e-12)


def test_identical_ratios_give_a_zero_objective():
    f = np.array([1.0, 2.0, 4.0])
    m = 3.0 * f
    level, mape = AB._mape_level(f, m)
    assert level == pytest.approx(3.0)
    assert mape == pytest.approx(0.0, abs=1e-12)


def test_scaling_f_scales_the_level_inversely_and_leaves_the_objective_fixed():
    rng = np.random.default_rng(11)
    f = rng.uniform(0.3, 2.0, 7)
    m = rng.uniform(0.3, 3.0, 7)
    level, mape = AB._mape_level(f, m)
    for a in (0.25, 3.0, 17.0):
        lvl_a, mape_a = AB._mape_level(a * f, m)
        assert lvl_a == pytest.approx(level / a, rel=1e-10)
        assert mape_a == pytest.approx(mape, rel=1e-10)


def test_scaling_y_scales_the_level_and_leaves_the_objective_fixed():
    rng = np.random.default_rng(13)
    f = rng.uniform(0.3, 2.0, 7)
    m = rng.uniform(0.3, 3.0, 7)
    level, mape = AB._mape_level(f, m)
    for a in (0.4, 2.5, 9.0):
        lvl_a, mape_a = AB._mape_level(f, a * m)
        assert lvl_a == pytest.approx(a * level, rel=1e-10)
        assert mape_a == pytest.approx(mape, rel=1e-10)


def test_extreme_positive_weights_do_not_break_the_minimiser():
    f = np.array([1e-6, 1.0, 1e6])
    m = np.array([1.0, 1.0, 1.0])
    level, mape = AB._mape_level(f, m)
    _g, grid_mape = brute_force_minimum(f, m)
    assert mape <= grid_mape + 1e-9
    assert np.isfinite(level) and level > 0


# ── continuity, which the endpoint comparison depends on ─────────────────────────────────────
def test_a_uniform_scaling_of_f_leaves_the_objective_exactly_invariant():
    """Recorded because an earlier "continuity" test used exactly this perturbation and was VACUOUS.

    A common positive scaling `f -> (1+eps)f` is absorbed exactly by `I -> I/(1+eps)`, so the
    profiled objective is invariant to the last digit. A test built on it can never fail and proves
    nothing about continuity — it proves scale invariance, which is what this test now says.
    """
    rng = np.random.default_rng(5)
    f = rng.uniform(0.3, 2.0, 8)
    m = rng.uniform(0.3, 3.0, 8)
    base_level, base_value = AB._mape_level(f, m)
    for eps in (1e-3, 0.1, 0.5, 3.0):
        level, value = AB._mape_level(f * (1.0 + eps), m)
        assert value == pytest.approx(base_value, rel=1e-14)
        assert level == pytest.approx(base_level / (1.0 + eps), rel=1e-12)


@pytest.mark.parametrize("direction_seed", range(4))
@pytest.mark.parametrize("sign", (+1.0, -1.0))
def test_the_profiled_value_is_continuous_under_NONUNIFORM_perturbation(direction_seed, sign):
    """The real continuity test: perturb along a fixed NONCONSTANT direction, both signs.

    Continuity of the profiled minimum is what lets `J_inf` be compared with a threshold at all. It
    needs a perturbation the level cannot absorb, which a uniform scaling is not.
    """
    rng = np.random.default_rng(100 + direction_seed)
    f_inf = rng.uniform(0.5, 2.0, 9)
    m = rng.uniform(0.5, 3.0, 9)
    d = rng.uniform(-1.0, 1.0, 9)
    d = d - d.mean()                                  # nonconstant: not a common scaling
    d = d / np.abs(d).max()

    target = AB._mape_level(f_inf, m)[1]
    ratios = []
    for eps in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5):
        f_eps = f_inf * (1.0 + sign * eps * d)
        assert np.all(f_eps > 0), "perturbation must retain positivity"
        gap = abs(AB._mape_level(f_eps, m)[1] - target)
        ratios.append(gap / eps)
    # The mathematical content is the RATE: the profiled value is Lipschitz in the perturbation, so
    # gap/eps SETTLES to a finite constant. Two earlier attempts measured the wrong thing — an
    # absolute 1e-5 floor (failed on a gap of 1.007e-5, i.e. it measured the tolerance) and a cap of
    # r < 2 (arbitrary: the Lipschitz constant is data-dependent and runs from ~1 to ~15 across
    # draws). Convergence is evidenced by settling, not by a magnitude someone picked.
    assert all(np.isfinite(r) for r in ratios), ratios
    assert ratios[-1] == pytest.approx(ratios[-2], rel=0.01), (
        "the ratio must settle, or the convergence is not first order: %s" % ratios)


def test_continuity_holds_approaching_an_exact_tie():
    """A median switch is where a smooth surrogate would fail, so continuity must be shown there."""
    f, m = TIE_FIXTURE_F, TIE_FIXTURE_M
    target = AB._mape_level(f, m)[1]
    ratios = []
    for eps in (1e-1, 1e-2, 1e-3, 1e-4, 1e-5):
        f_eps = f * np.array([1.0 + eps, 1.0, 1.0 - eps])   # nonuniform, straddles the tie
        gap = abs(AB._mape_level(f_eps, m)[1] - target)
        ratios.append(gap / eps)
    assert all(np.isfinite(r) for r in ratios), ratios
    assert ratios[-1] == pytest.approx(ratios[-2], rel=0.01), (
        "a median switch must not break first-order convergence: %s" % ratios)


# ── the dimensional error the protocol has to stop making ────────────────────────────────────
def test_tie_width_is_in_inventory_units_not_objective_units():
    """The tie interval creates NO objective uncertainty, so it cannot enter a `J` error budget.

    Protocol V2 listed "weighted-median tie width" as a component added to `J_min` and `J_inf`. Tie
    width is a spread in inventory level; `J` is in percentage points; and the objective is exactly
    constant across the interval. Adding one to the other is dimensionally invalid.
    """
    f, m = TIE_FIXTURE_F, TIE_FIXTURE_M
    lo, hi = minimiser_interval(f, m)
    tie_width = hi - lo
    assert tie_width > 0
    spread_in_objective = abs(objective(hi, f, m) - objective(lo, f, m))
    assert spread_in_objective == pytest.approx(0.0, abs=1e-12), (
        "a nonzero objective spread would mean the tie really did carry J uncertainty")
