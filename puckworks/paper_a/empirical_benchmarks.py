"""Equal-information, optimal-grind-only empirical benchmarks for the cross-grind comparison.

Domain-referee Major finding 1. The headline comparison gives the two arms unequal information:

* the **mechanistic** predictor receives temperature, pressure and a target-grind hydraulic map;
* the **level-only constant** receives one fitted concentration per variety–solute group and no
  temperature, pressure, flow or kinetic response at all.

The constant is a valid *minimal ablation* — it answers "does the process model improve on
transferring only a level?", which matters because inventory is exactly multiplicative in this
model. It is not an adequate *sole* benchmark of mechanistic skill, because the comparison then
confounds the value of the mechanistic structure with the value of having **any** condition-
dependent response.

The referee demonstrated this by fitting low-degree empirical responses to the nine optimal-grind
conditions and scoring them on the same held-out corpus: macro-MAPE fell from 8.832 % (constant) to
8.691 %, narrowing the mechanistic margin from ~0.394 pp to ~0.25 pp — before equalising hydraulic
information, which would narrow it further.

This module implements that panel as a first-class, reproducible comparator.

**The holdout contract**, which is the whole point:

* training support is the nine on-grid **optimal-grind** records of each variety–solute group;
* neither candidate-family selection nor coefficient fitting may see any coarse/fine concentration;
* selection is by leave-one-optimal-condition-out cross-validation, then the chosen family is
  refitted on all nine and **frozen** before any C/F record is scored;
* scoring uses the same endpoint, loss, macro-averaging and corpus as the mechanistic arm.

No PDE is involved: these are closed-form fits to concentrations, so the panel is fast, testable in
CI, and independent of the ~26-minute science producer.

**What this is not.** The candidate family is small and was chosen after seeing the data, so the
panel is a locked, transparent *sensitivity analysis*, not a prospectively registered confirmatory
plan. It also does not yet consume the derived flow/shot-time variable the mechanistic arm gets;
:data:`HYDRAULIC_NOTE` records that remaining asymmetry rather than letting it pass silently.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

from puckworks.paper_a import source_schema as SS

#: The three named solutes, and the source column each is measured in. Declared here rather than
#: imported, for the same reason the resampling oracle declares its own: two implementations of
#: "which cell is this observation" must be able to disagree.
SOLUTE_COLUMNS = (("caffeine", "CF"), ("trigonelline", "TR"), ("5CQA", "5CQA"))

VARIETIES = ("Arabica", "Robusta")
HELD_OUT_GRINDS = ("C", "F")

#: The remaining information asymmetry, recorded so it cannot be forgotten when the result is read.
HYDRAULIC_NOTE = (
    "These baselines use temperature and pressure only. The mechanistic arm additionally receives a "
    "target-grind hydraulic (conductivity/shot-time) map, so this panel narrows the information gap "
    "but does not close it; a fully equal-information baseline would also receive the derived "
    "flow/shot-time variable.")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Candidate families
# ─────────────────────────────────────────────────────────────────────────────────────────────
#
# Deliberately low-degree. Nine training points leave no room for a large function library, and the
# referee's warning is explicit: too many interaction or polynomial terms will overfit.


def _design(name: str, T: np.ndarray, p: np.ndarray) -> np.ndarray:
    """Design matrix for one candidate family, columns in a fixed order."""
    one = np.ones_like(T)
    if name == "constant":
        return np.column_stack([one])
    if name == "temperature":
        return np.column_stack([one, T])
    if name == "pressure":
        return np.column_stack([one, p])
    if name == "temperature+pressure":
        return np.column_stack([one, T, p])
    if name == "temperature*pressure":
        return np.column_stack([one, T, p, T * p])
    raise ValueError("unknown candidate family %r" % name)


FAMILIES = ("constant", "temperature", "pressure", "temperature+pressure",
            "temperature*pressure")


def fit_mape(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Coefficients minimising mean |Xb − y| / y — a weighted L1 regression, solved as an LP.

    MAPE is ``mean_i |x_i·b − y_i| / y_i``, i.e. weighted L1 with weights ``1/y_i``. Least squares
    would minimise the wrong objective, and the constant case has an exact weighted-median solution
    that the production comparator already uses — this reduces to it, which the tests check.

    Falls back to that exact solution for the constant family, and to least squares only if the LP
    solver is unavailable or fails, in which case the caller is told rather than silently given a
    different estimator.
    """
    X = np.asarray(X, float)
    y = np.asarray(y, float)
    n, k = X.shape
    if k == 1:                                  # exact weighted median; matches production
        return np.array([_weighted_median_level(X[:, 0], y)])

    from scipy.optimize import linprog

    # minimise sum_i w_i t_i  s.t.  t_i >= ±(x_i·b − y_i);  variables [b (k), t (n)]
    w = 1.0 / y
    c = np.concatenate([np.zeros(k), w])
    A = np.block([[X, -np.eye(n)], [-X, -np.eye(n)]])
    b = np.concatenate([y, -y])
    bounds = [(None, None)] * k + [(0, None)] * n
    result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method="highs")
    if not result.success:                      # pragma: no cover - solver-dependent
        raise RuntimeError("MAPE fit failed to converge: %s" % result.message)
    return np.asarray(result.x[:k], float)


def _weighted_median_level(f: np.ndarray, m: np.ndarray) -> float:
    """The exact MAPE-optimal level, identical to the production comparator's estimator."""
    x, w = m / f, f / m
    order = np.argsort(x)
    x, w = x[order], w[order]
    cw = np.cumsum(w)
    k = int(np.searchsorted(cw, 0.5 * cw[-1]))
    return float(x[min(k, len(x) - 1)])


def mape(pred: np.ndarray, obs: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(pred, float) - obs) / obs) * 100.0)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Selection and scoring
# ─────────────────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GroupResult:
    """One variety–solute group's selected baseline and its held-out scores."""

    group: str
    family: str
    n_train: int
    train_mape: float
    cf_mape: float
    coarse_mape: float
    fine_mape: float
    cv_scores: dict

    def as_dict(self) -> dict:
        return {"group": self.group, "family": self.family, "n_train": self.n_train,
                "train_mape": round(self.train_mape, 3), "cf_mape": round(self.cf_mape, 3),
                "coarse_mape": round(self.coarse_mape, 3), "fine_mape": round(self.fine_mape, 3),
                "cv_scores": {k: round(v, 4) for k, v in sorted(self.cv_scores.items())}}


def _rows(path=None):
    parsed = SS.parse_rows(path=path)
    return [r for r in parsed if r.variety in VARIETIES]


def _cells(rows, column):
    T = np.array([float(r.temperature_degC) for r in rows])
    p = np.array([float(r.pressure_bar) for r in rows])
    y = np.array([float(r.raw[column]) for r in rows])
    return T, p, y


def select_and_score(rows, variety: str, solute: str, column: str) -> GroupResult:
    """Fit, select by leave-one-optimal-condition-out CV, freeze, then score on C/F."""
    train = [r for r in rows if r.variety == variety and r.is_optimal_grind and r.on_grid]
    heldout = [r for r in rows if r.variety == variety and r.granulometry in HELD_OUT_GRINDS]
    Tt, pt, yt = _cells(train, column)

    # ── selection: leave one optimal-grind CONDITION out ────────────────────────────────────
    cv = {}
    for family in FAMILIES:
        errors = []
        for i in range(len(yt)):
            keep = np.ones(len(yt), bool)
            keep[i] = False
            if keep.sum() <= _design(family, Tt, pt).shape[1]:
                errors = None                   # not enough points to identify this family
                break
            beta = fit_mape(_design(family, Tt[keep], pt[keep]), yt[keep])
            pred = _design(family, Tt[~keep], pt[~keep]) @ beta
            errors.append(abs(float(pred[0]) - yt[i]) / yt[i] * 100.0)
        if errors is not None:
            cv[family] = float(np.mean(errors))

    # Ties resolved toward the SIMPLER family, in declared order — with nine points, model
    # selection is unstable and a tie must not be broken by whichever came last.
    family = min(FAMILIES, key=lambda f: (cv.get(f, np.inf), FAMILIES.index(f)))

    # ── refit on all nine, freeze, and only now look at C/F ─────────────────────────────────
    beta = fit_mape(_design(family, Tt, pt), yt)
    train_mape = mape(_design(family, Tt, pt) @ beta, yt)

    scores = {}
    for grind in HELD_OUT_GRINDS:
        rows_g = [r for r in heldout if r.granulometry == grind]
        Tg, pg, yg = _cells(rows_g, column)
        scores[grind] = mape(_design(family, Tg, pg) @ beta, yg)
    Ta, pa, ya = _cells(heldout, column)
    return GroupResult(group="%s:%s" % (variety, solute), family=family, n_train=len(yt),
                       train_mape=train_mape, cf_mape=mape(_design(family, Ta, pa) @ beta, ya),
                       coarse_mape=scores["C"], fine_mape=scores["F"], cv_scores=cv)


def constant_baseline(rows, variety: str, column: str) -> dict:
    """The production level-only constant, recomputed here from the raw table.

    Present so the panel reproduces the published comparator from the same code path it scores the
    empirical families with — a panel that could not recover 8.832 % would not be comparable to it.
    """
    train = [r for r in rows if r.variety == variety and r.is_optimal_grind and r.on_grid]
    heldout = [r for r in rows if r.variety == variety and r.granulometry in HELD_OUT_GRINDS]
    _T, _p, yt = _cells(train, column)
    level = _weighted_median_level(np.ones(len(yt)), yt)
    out = {}
    for grind in HELD_OUT_GRINDS:
        rows_g = [r for r in heldout if r.granulometry == grind]
        _Tg, _pg, yg = _cells(rows_g, column)
        out[grind] = mape(np.full(len(yg), level), yg)
    _Ta, _pa, ya = _cells(heldout, column)
    out["all"] = mape(np.full(len(ya), level), ya)
    return out


def panel(path=None) -> dict:
    """The complete benchmark panel: per group, and macro-averaged as the paper reports."""
    rows = _rows(path)
    groups, constants = [], []
    for variety, (solute, column) in itertools.product(VARIETIES, SOLUTE_COLUMNS):
        groups.append(select_and_score(rows, variety, solute, column))
        constants.append(constant_baseline(rows, variety, column))

    def macro(values):
        return float(np.mean(values))

    return {
        "hydraulic_note": HYDRAULIC_NOTE,
        "groups": [g.as_dict() for g in groups],
        "empirical": {
            "macro_cf_mape": round(macro([g.cf_mape for g in groups]), 3),
            "macro_coarse_mape": round(macro([g.coarse_mape for g in groups]), 3),
            "macro_fine_mape": round(macro([g.fine_mape for g in groups]), 3),
        },
        "level_only_constant": {
            "macro_cf_mape": round(macro([c["all"] for c in constants]), 3),
            "macro_coarse_mape": round(macro([c["C"] for c in constants]), 3),
            "macro_fine_mape": round(macro([c["F"] for c in constants]), 3),
        },
    }
