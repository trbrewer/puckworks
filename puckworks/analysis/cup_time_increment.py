"""Frozen PW-CUP-TIME-INCREMENT-001 observation and descriptive statistics.

First-party analysis code. Grudeva-derived outputs require Dr. Yoana Grudeva
attribution and docs/permissions/grudeva2025.md (PERMISSION_DOCUMENTED,
no SPDX licence, not relicensed under MIT).
"""

from dataclasses import dataclass

import numpy as np
from scipy.stats import t as student_t


ENDPOINTS = (19.8, 9.90, 14.85)
VARIANTS = (
    ("primary", 19.8, "linear", False),
    ("time_u2", 19.8, "u2", False),
    ("time_sqrt", 19.8, "sqrt", False),
    ("conserving_interpolation", 19.8, "linear", True),
    ("secondary_0.5", 9.90, "linear", False),
    ("secondary_0.75", 14.85, "linear", False),
)
DRAWS = 2000
SEED = 20261104


def linear_integral(midpoints, values, start, end):
    """Exact piecewise-linear integral, with constant edge extension."""
    x, q = np.asarray(midpoints, float), np.asarray(values, float)
    if (x.ndim != 1 or len(x) == 0 or q.shape != x.shape
            or not np.isfinite(x).all() or not np.isfinite(q).all()
            or np.any(np.diff(x) <= 0) or not np.isfinite([start, end]).all()
            or end < start):
        raise ValueError("invalid interpolation coordinates")
    knots = np.r_[start, x[(x > start) & (x < end)], end]
    heights = np.interp(knots, x, q)
    return float(np.sum(np.diff(knots) * (heights[:-1] + heights[1:]) / 2))


def crossing_solute(mass, concentration, start, end, u, midpoints, values):
    """Conserve the measured crossing-vial solute under correction C."""
    if not 0 <= u <= 1 or mass <= 0 or end <= start or concentration < 0:
        raise ValueError("invalid crossing vial")
    if concentration == 0:
        return 0.0
    denominator = linear_integral(midpoints, values, start, end)
    if not np.isfinite(denominator) or denominator <= 0:
        raise ValueError(f"nonpositive interpolation denominator: {denominator!r}")
    numerator = linear_integral(midpoints, values, start, start + (end - start) * u)
    return mass * concentration / 100 * numerator / denominator


def prefix_observation(rows, mass, timing="linear", interpolate=False):
    """One collected-prefix outcome; rows are unchanged CLOCK observations."""
    if mass not in ENDPOINTS or timing not in ("linear", "u2", "sqrt"):
        raise ValueError("outside frozen endpoints/timing conventions")
    if interpolate and timing != "linear":
        raise ValueError("sensitivity families cannot be combined")
    solute = 0.0
    for r in rows:
        if r["mass_g"] == 0:
            continue
        if r["solute_g"] is None:
            raise ValueError("positive-mass chemistry gap in selected shot")
        if r["b_start_g"] < mass <= r["b_end_g"]:
            u = (mass - r["b_start_g"]) / r["mass_g"]
            progress = {"linear": u, "u2": u * u, "sqrt": np.sqrt(u)}[timing]
            duration = r["t_start_s"] + 2 * progress
            if interpolate:
                positive = [v for v in rows if v["mass_g"] > 0]
                mids = [(v["t_start_s"] + v["t_end_s"]) / 2 for v in positive]
                concentrations = [v["tds_pct"] for v in positive]
                try:
                    part = crossing_solute(r["mass_g"], r["tds_pct"], r["t_start_s"],
                                           r["t_end_s"], u, mids, concentrations)
                except ValueError as exc:
                    raise ValueError(f"shot {r['shot']}, vial {r['vial']}: {exc}") from exc
            else:
                part = (mass - r["b_start_g"]) * r["tds_pct"] / 100
            return dict(mass_g=mass, duration_s=float(duration),
                        concentration_tds_pp=100 * (solute + part) / mass,
                        prefix_solute_g=solute + part, crossing_vial=r["vial"],
                        within_vial_mass_fraction=u)
        solute += r["solute_g"]
    raise ValueError("frozen endpoint exceeds regular-window mass")


class Unfit(ValueError):
    """Declared insufficient training support, retained in draw records."""


@dataclass(frozen=True)
class Fit:
    alpha: float
    beta: float

    def predict(self, duration):
        return self.alpha + self.beta * np.log(np.asarray(duration) / 20.0)


def fit_ols(duration, outcome, weights, slope):
    duration, y, w = (np.asarray(v, float) for v in (duration, outcome, weights))
    if (duration.shape != y.shape or y.shape != w.shape or duration.ndim != 1
            or not np.isfinite(duration).all() or not np.isfinite(y).all()
            or not np.isfinite(w).all() or np.any(duration <= 0) or np.any(w < 0)):
        raise ValueError("invalid OLS inputs")
    keep = w > 0
    if not np.any(keep):
        raise Unfit("EMPTY_TRAINING")
    duration, y, w = duration[keep], y[keep], w[keep]
    mean_y = float(np.average(y, weights=w))
    if not slope:
        return Fit(mean_y, 0.0)
    if len(np.unique(duration)) < 2:
        raise Unfit("FEWER_THAN_TWO_DISTINCT_TRAINING_DURATIONS")
    x = np.log(duration / 20.0)
    mean_x = float(np.average(x, weights=w))
    xx = x - mean_x
    beta = float(np.sum(w * xx * (y - mean_y)) / np.sum(w * xx * xx))
    return Fit(mean_y - beta * mean_x, beta)


def loso(duration, outcome, weights=None):
    """One fold per unique physical index; remove all its copies before fitting."""
    t, y = np.asarray(duration, float), np.asarray(outcome, float)
    w = np.ones(len(t)) if weights is None else np.asarray(weights, float)
    if len(t) != len(y) or w.shape != t.shape or np.any(w < 0) or w.sum() <= 0:
        raise ValueError("invalid grouped sample")
    active = np.flatnonzero(w > 0)
    folds = []
    for held in active:
        train = active[active != held]
        record = dict(held_index=int(held), held_copies=int(w[held]),
                      training_unique=len(train), training_copies=int(w[train].sum()),
                      training_distinct_durations=len(np.unique(t[train])))
        for arm, slope in (("A0", False), ("A1", True)):
            try:
                # Only projected training chemistry crosses the fitter boundary.
                fitted = fit_ols(t[train], y[train], w[train], slope)
                prediction = float(fitted.predict(t[held]))
                values = (fitted.alpha, fitted.beta, prediction, y[held] - prediction, "DEFINED")
            except Unfit as exc:
                values = (np.nan, np.nan, np.nan, np.nan, str(exc))
            for key, value in zip(("alpha", "beta", "prediction_pp", "error_pp", "status"),
                                  values):
                record[f"{arm}_{key}"] = value
        record["paired_squared_error_difference_pp2"] = (
            record["A1_error_pp"] ** 2 - record["A0_error_pp"] ** 2)
        folds.append(record)
    metrics = {}
    for arm in ("A0", "A1"):
        errors = np.array([f[f"{arm}_error_pp"] for f in folds])
        # Any undefined held fold invalidates the entire arm's draw RMSE.
        metrics[f"rmse_{arm}_pp"] = float(np.sqrt(np.sum(w[active] * errors**2) / w.sum()))
    metrics["delta_pp"] = metrics["rmse_A1_pp"] - metrics["rmse_A0_pp"]
    metrics["unfit_slope_folds"] = sum(f["training_distinct_durations"] < 2 for f in folds)
    metrics["empty_training_folds"] = sum(f["training_unique"] == 0 for f in folds)
    return metrics, folds


def point_analysis(duration, outcome):
    t, y = np.asarray(duration, float), np.asarray(outcome, float)
    metrics, folds = loso(t, y)
    x = np.log(t / 20)
    centered = x - x.mean()
    sxx = float(centered @ centered)
    for arm, slope in (("A0", False), ("A1", True)):
        fit = fit_ols(t, y, np.ones(len(t)), slope)
        leverage = np.full(len(t), 1 / len(t))
        if slope:
            leverage += centered**2 / sxx
        residual = y - fit.predict(t)
        press = residual / (1 - leverage)
        direct = np.array([f[f"{arm}_error_pp"] for f in folds])
        discrepancy = float(np.max(np.abs(press - direct)))
        if not np.isfinite(discrepancy) or discrepancy > 1e-10:
            raise ValueError(f"{arm} closed-form LOSO mismatch: {discrepancy!r}")
        metrics[f"{arm}_press_max_abs_difference_pp"] = discrepancy
        metrics[f"{arm}_all_alpha"] = fit.alpha
        for i, fold in enumerate(folds):
            fold[f"{arm}_h_ii"] = float(leverage[i])
            fold[f"{arm}_press_error_pp"] = float(press[i])
        if slope:
            beta_se = float(np.sqrt((residual @ residual) / (len(t) - 2) / sxx))
            half = float(student_t.ppf(0.975, len(t) - 2)) * beta_se
            metrics.update(beta=fit.beta, descriptive_all_beta_t_low=fit.beta - half,
                           descriptive_all_beta_t_high=fit.beta + half,
                           descriptive_all_beta_se=beta_se, descriptive_all_df=len(t) - 2,
                           implied_change_pp=fit.beta * np.log(t.max() / t.min()))
    metrics.update(duration_min_s=float(t.min()), duration_median_s=float(np.median(t)),
                   duration_max_s=float(t.max()),
                   shots_A1_better=sum(f["paired_squared_error_difference_pp2"] < 0 for f in folds))
    for key in ("A0_h_ii", "A1_h_ii", "A1_beta", "A0_error_pp", "A1_error_pp",
                "paired_squared_error_difference_pp2"):
        metrics[f"{key}_min"] = min(f[key] for f in folds)
        metrics[f"{key}_max"] = max(f[key] for f in folds)
    return metrics, folds


def resampling_indices(n=11):
    bootstrap_seed, permutation_seed = np.random.SeedSequence(SEED).spawn(2)
    rng_b = np.random.Generator(np.random.PCG64(bootstrap_seed))
    rng_p = np.random.Generator(np.random.PCG64(permutation_seed))
    multiplicities = np.array([np.bincount(rng_b.integers(n, size=n), minlength=n)
                               for _ in range(DRAWS)])
    permutations = np.array([rng_p.permutation(n) for _ in range(DRAWS)])
    return multiplicities, permutations


def bootstrap_draw(duration, outcome, multiplicity):
    metrics, _ = loso(duration, outcome, multiplicity)
    try:
        metrics["beta"] = fit_ols(duration, outcome, multiplicity, True).beta
        metrics["beta_status"] = "DEFINED"
    except Unfit as exc:
        metrics["beta"] = np.nan
        metrics["beta_status"] = str(exc)
    metrics["implied_change_pp"] = metrics["beta"] * np.log(max(duration) / min(duration))
    metrics["unique_shots"] = int(np.count_nonzero(multiplicity))
    metrics["status"] = "UNDEFINED_LOSO" if metrics["unfit_slope_folds"] else "DEFINED"
    return metrics


def resample_analysis(duration, outcome, multiplicities, permutations):
    boots = [dict(draw=i + 1, **bootstrap_draw(duration, outcome, w))
             for i, w in enumerate(multiplicities)]
    t = np.asarray(duration, float)
    perms = [dict(draw=i + 1, **loso(t[p], outcome)[0]) for i, p in enumerate(permutations)]
    return boots, perms


def uncertainty_summary(point, boots, permutations):
    summary = dict(bootstrap_requested=len(boots), permutation_requested=len(permutations))
    for name in ("rmse_A0_pp", "rmse_A1_pp", "delta_pp", "beta", "implied_change_pp"):
        values = np.array([r[name] for r in boots])
        values = values[np.isfinite(values)]
        low, high = np.quantile(values, [0.025, 0.975], method="linear") if len(values) else (
            np.nan, np.nan)
        summary.update({f"{name}_boot_low": float(low), f"{name}_boot_high": float(high),
                        f"{name}_boot_defined": len(values),
                        f"{name}_boot_undefined": len(boots) - len(values)})
    summary["bootstrap_unfit_slope_draws"] = sum(r["unfit_slope_folds"] > 0 for r in boots)
    summary["bootstrap_unfit_slope_folds"] = sum(r["unfit_slope_folds"] for r in boots)
    summary["bootstrap_empty_training_draws"] = sum(r["empty_training_folds"] > 0 for r in boots)
    delta = np.array([r["delta_pp"] for r in permutations])
    if not np.isfinite(delta).all():
        raise ValueError("undefined permutation reference; retain draw evidence")
    summary["permutation_delta_less"] = int(np.sum(delta < point["delta_pp"]))
    summary["permutation_delta_ties"] = int(np.sum(delta == point["delta_pp"]))
    summary["permutation_percentile"] = 100 * (
        summary["permutation_delta_less"] + 0.5 * summary["permutation_delta_ties"]
    ) / len(permutations)
    return summary


def vocabulary(summary):
    low, high = summary["delta_pp_boot_low"], summary["delta_pp_boot_high"]
    direction = "reduction" if summary["delta_pp"] < 0 else (
        "increase" if summary["delta_pp"] > 0 else "no change")
    delta = "resolved held-out error reduction" if high < 0 else (
        "resolved held-out error increase" if low > 0 else "prediction difference unresolved")
    beta = "resolved" if (summary["beta_boot_low"] > 0 or summary["beta_boot_high"] < 0
                          ) else "unresolved"
    return direction, delta, beta
