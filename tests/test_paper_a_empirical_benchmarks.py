"""Domain-referee Major finding 1: the equal-information benchmark panel.

The referee ran this calculation independently, from the raw Angeloni table, and published every
intermediate value in Appendix A. Reproducing those numbers exactly is the strongest validation
available for a new comparator — two implementations, written without sight of each other, agreeing
to the last reported digit.

The referee's figures, pinned below:

    empirical  macro 8.691 %   coarse 11.012 %   fine 6.370 %
    constant   macro 8.832 %   coarse 11.187 %   fine 6.478 %

    Arabica caffeine      pressure       8.744
    Arabica trigonelline  constant       6.454
    Arabica 5-CQA         pressure      13.216
    Robusta caffeine      constant       7.483
    Robusta trigonelline  temperature    7.302
    Robusta 5-CQA         constant       8.946

The holdout contract is what makes the panel meaningful, so it is tested directly rather than
assumed: no coarse/fine concentration may influence either family selection or coefficient fitting.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.paper_a import empirical_benchmarks as EB  # noqa: E402
from puckworks.paper_a import source_schema as SS  # noqa: E402


@pytest.fixture(scope="module")
def result():
    return EB.panel()


# ── 1. exact agreement with the referee's independent calculation ────────────────────────────
@pytest.mark.parametrize("arm,key,expected", [
    ("empirical", "macro_cf_mape", 8.691),
    ("empirical", "macro_coarse_mape", 11.012),
    ("empirical", "macro_fine_mape", 6.370),
    ("level_only_constant", "macro_cf_mape", 8.832),
    ("level_only_constant", "macro_coarse_mape", 11.187),
    ("level_only_constant", "macro_fine_mape", 6.478),
])
def test_reproduces_the_referees_macro_figures(result, arm, key, expected):
    assert result[arm][key] == pytest.approx(expected, abs=5e-4), (arm, key)


@pytest.mark.parametrize("group,family,cf_mape", [
    ("Arabica:caffeine", "pressure", 8.744),
    ("Arabica:trigonelline", "constant", 6.454),
    ("Arabica:5CQA", "pressure", 13.216),
    ("Robusta:caffeine", "constant", 7.483),
    ("Robusta:trigonelline", "temperature", 7.302),
    ("Robusta:5CQA", "constant", 8.946),
])
def test_reproduces_the_referees_group_selections(result, group, family, cf_mape):
    got = next(g for g in result["groups"] if g["group"] == group)
    assert got["family"] == family, (group, got["family"])
    assert got["cf_mape"] == pytest.approx(cf_mape, abs=5e-4)


def test_the_constant_reproduces_the_published_comparator(result):
    """8.83 % is the manuscript's headline comparator. A panel that could not recover it from the
    raw table would not be scoring on the same footing as the published arm."""
    assert round(result["level_only_constant"]["macro_cf_mape"], 2) == 8.83


def test_the_empirical_panel_beats_the_constant_and_narrows_the_margin(result):
    """The finding itself: a low-degree response with NO mechanism closes part of the gap."""
    empirical = result["empirical"]["macro_cf_mape"]
    constant = result["level_only_constant"]["macro_cf_mape"]
    assert empirical < constant
    model = 8.44                                    # published mechanistic pooled MAPE
    assert round(constant - model, 3) == pytest.approx(0.392, abs=0.005)
    assert round(empirical - model, 3) == pytest.approx(0.251, abs=0.005)


# ── 2. the holdout contract, tested rather than asserted ─────────────────────────────────────
def test_no_coarse_or_fine_record_can_influence_selection_or_fitting():
    """Perturb every held-out concentration and confirm the frozen predictor is unchanged.

    This is the property the whole panel rests on. If a C/F value could reach the fit, the
    comparison would be a resubstitution score wearing a holdout's name.
    """
    rows = SS.parse_rows()
    rng = np.random.default_rng(0)

    class Perturbed:
        """A row whose HELD-OUT analyte cells are corrupted; optimal-grind rows untouched."""

        def __init__(self, row):
            self._row = row
            if row.granulometry in EB.HELD_OUT_GRINDS:
                raw = dict(row.raw)
                for _solute, column in EB.SOLUTE_COLUMNS:
                    raw[column] = str(float(raw[column]) * float(rng.uniform(2.0, 5.0)))
                self.raw = raw
            else:
                self.raw = row.raw

        def __getattr__(self, name):
            return getattr(self._row, name)

    perturbed = [Perturbed(r) for r in rows]
    for variety in EB.VARIETIES:
        for solute, column in EB.SOLUTE_COLUMNS:
            clean = EB.select_and_score(rows, variety, solute, column)
            dirty = EB.select_and_score(perturbed, variety, solute, column)
            assert dirty.family == clean.family, (variety, solute, "family leaked")
            assert dirty.train_mape == pytest.approx(clean.train_mape), (variety, solute, "fit leaked")
            # …and the SCORES must move, or the perturbation did not reach the scoring path.
            assert dirty.cf_mape != pytest.approx(clean.cf_mape)


def test_training_support_is_exactly_the_nine_on_grid_optimal_conditions(result):
    assert all(g["n_train"] == 9 for g in result["groups"]), \
        "the panel must train on the nine optimal-grind conditions and nothing else"


# ── 3. the estimator itself ──────────────────────────────────────────────────────────────────
def test_the_constant_family_is_the_exact_weighted_median_minimiser():
    """Not least squares, and not a grid search: MAPE over a level has a closed-form minimiser, and
    production already uses it. The LP path must reduce to the same estimator."""
    y = np.array([3.13, 3.37, 3.53, 3.20, 3.12, 3.19, 3.23, 2.99, 3.39])
    beta = EB.fit_mape(np.ones((len(y), 1)), y)
    grid = np.linspace(y.min(), y.max(), 20001)
    best = grid[np.argmin([np.mean(np.abs(c - y) / y) for c in grid])]
    assert float(beta[0]) == pytest.approx(best, abs=1e-3)


def test_the_lp_fit_minimises_mape_not_squared_error():
    """A single large outlier separates the two objectives; least squares would chase it."""
    T = np.array([88.0, 93.4, 98.0, 88.0, 93.4, 98.0, 88.0, 93.4, 98.0])
    y = np.array([1.0, 1.1, 1.2, 1.0, 1.1, 1.2, 1.0, 1.1, 30.0])
    X = EB._design("temperature", T, np.zeros_like(T))
    lp = EB.fit_mape(X, y)
    ls = np.linalg.lstsq(X, y, rcond=None)[0]
    assert EB.mape(X @ lp, y) < EB.mape(X @ ls, y)


def test_a_tie_selects_the_simpler_family():
    """With nine points, selection is unstable; a tie must not be decided by iteration order."""
    assert EB.FAMILIES[0] == "constant"
    T = np.full(9, 93.4)
    p = np.full(9, 9.0)                              # no variation: every family fits identically
    y = np.linspace(3.0, 3.4, 9)
    scores = {f: EB.mape(EB._design(f, T, p) @ EB.fit_mape(EB._design(f, T, p), y), y)
              for f in ("constant", "temperature")}
    assert scores["constant"] == pytest.approx(scores["temperature"], abs=1e-6)


# ── 4. the remaining asymmetry is recorded, not hidden ───────────────────────────────────────
def test_the_residual_hydraulic_asymmetry_is_stated(result):
    note = result["hydraulic_note"]
    assert "hydraulic" in note and "does not close it" in note, \
        "the panel narrows the information gap but does not close it, and must say so"


# ── 5. the refit-aware tool must reproduce the published headline before it is trusted ────────
def test_the_refit_pipeline_reproduces_the_published_arms():
    """The no-fold-dropped case of the refit tool must recover 8.44 / 8.83 / 8.691.

    This validation caught a real bug. The first draft of `paper_a_refit_aware_comparison` never
    applied the rate multiplier when building the unit-inventory prediction, so `f` was identical
    for every candidate rate, the level absorbed everything, and the mechanistic arm silently became
    a RATE-FREE model scoring 8.281 % — close enough to 8.44 % to look plausible in a table of fold
    results, and wrong. Nothing else in the chain would have noticed, because the tool writes its
    own archive.

    Marked slow: it runs the PDE over the full corpus (~1 min).
    """
    from tools import paper_a_refit_aware_comparison as R

    per_group = R._fit_fold(R._rows(), drop=(-1.0, -1.0), empirical=True)
    for arm, coarse, fine, pooled in (("model", 10.17, 6.71, 8.44),
                                      ("const", 11.19, 6.48, 8.83),
                                      ("emp", 11.012, 6.370, 8.691)):
        C = R._macro(per_group, "%s_C" % arm)
        F = R._macro(per_group, "%s_F" % arm)
        assert C == pytest.approx(coarse, abs=0.01), (arm, "coarse")
        assert F == pytest.approx(fine, abs=0.01), (arm, "fine")
        assert (C + F) / 2 == pytest.approx(pooled, abs=0.01), (arm, "pooled")


test_the_refit_pipeline_reproduces_the_published_arms = pytest.mark.slow(
    test_the_refit_pipeline_reproduces_the_published_arms)
