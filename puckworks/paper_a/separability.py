"""Local inventory–rate separability of an observation design.

Scientific-pivot plan §5. The paper's prediction factorises exactly,

    yhat_i(I, k) = I * f_i(k),

with `I` the extractable-inventory level and `k` the rate multiplier. That exactness is what makes
a *local* design criterion available in closed form rather than by simulation study.

Write the log-parameters ``a = log I``, ``b = log k`` and the local log-rate sensitivity

    s_i = d log f_i(k) / d log k.

On a relative (or log) response scale the sensitivity row of observation *i* is ``[1, s_i]`` — the
level enters every observation identically, which is precisely the structural reason the two
parameters compete. For nonnegative weights ``w_i`` the local Gram matrix is

    G = S^T W S = [[sum w,      sum w s   ],
                   [sum w s,    sum w s^2 ]]

and its determinant collapses to a variance:

    det(G) = (sum w) * sum w (s_i - sbar_w)^2 = (sum w)^2 * Var_w(s).

So, in this parameterisation, **all local rate information after profiling the level is carried by
the spread of the observations' log-rate sensitivities**. If every observation responds to the rate
in the same proportional way, the two columns of S are collinear and the rate is locally
inseparable from the level however many observations are collected. This is the formal version of
the collinearity paragraph the manuscript currently states qualitatively.

Reported quantities:

    RSI       = sqrt(Var_w(s))              how NON-REDUNDANT the design is, per observation
    RSI_total = sqrt(sum w (s - sbar)^2)    how much separation information the whole design carries

The two answer different questions and the plan requires both: adding many observations with nearly
identical ``s_i`` raises RSI_total while leaving RSI unchanged, which is exactly the failure mode
("more data, no better identified") the paper is about.

**Scope, stated because it is easy to overclaim.** This is a *local, model-based* diagnostic at a
declared rate. It is:

* not a Fisher information matrix — no noise model is assumed. Calling it one would require
  declaring an error distribution the source does not support;
* not a global identifiability result — the model is nonlinear in `k`, so a design with healthy
  local separability can still have a broad or boundary-censored nonlinear profile;
* not an uncertainty interval, and must never be reported as one.

The nonlinear profile remains the empirical check. :func:`agreement_with_profiles` is the honest
comparison, and a disagreement is a finding about the limits of local geometry, not a bug.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

#: Default centred finite-difference step in log k. The rate grid used by the paper's profiles is
#: `np.geomspace(0.15, 6.5, 18)`, whose log spacing is ~0.22; the plan asks for a quarter to a half
#: of that, chosen BEFORE looking at which design wins.
DEFAULT_LOG_STEP = 0.08

#: Step multipliers for the convergence check (§5.3 steps 3–4): half, nominal, double.
STEP_MULTIPLIERS = (0.5, 1.0, 2.0)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# The exact local relation
# ─────────────────────────────────────────────────────────────────────────────────────────────


def gram(s: np.ndarray, w: np.ndarray | None = None) -> np.ndarray:
    """Local Gram matrix ``S^T W S`` for sensitivity rows ``[1, s_i]``."""
    s = np.asarray(s, float)
    w = np.ones_like(s) if w is None else np.asarray(w, float)
    if np.any(w < 0):
        raise ValueError("weights must be nonnegative")
    S = np.column_stack([np.ones_like(s), s])
    return S.T @ (w[:, None] * S)


def weighted_mean(s: np.ndarray, w: np.ndarray | None = None) -> float:
    s = np.asarray(s, float)
    w = np.ones_like(s) if w is None else np.asarray(w, float)
    return float(np.sum(w * s) / np.sum(w))


def separability(s: np.ndarray, w: np.ndarray | None = None) -> dict:
    """RSI, total RSI and the matrix diagnostics for one design at one rate.

    ``det_identity_residual`` re-derives det(G) both ways and reports the discrepancy. It is
    carried in the result rather than only asserted in a test, so an archived record shows the
    algebra held for the numbers actually published.
    """
    s = np.asarray(s, float)
    w = np.ones_like(s) if w is None else np.asarray(w, float)
    G = gram(s, w)

    sw = float(np.sum(w))
    sbar = weighted_mean(s, w)
    scatter = float(np.sum(w * (s - sbar) ** 2))          # sum w (s - sbar)^2

    det_direct = float(np.linalg.det(G))
    det_identity = sw * scatter
    singular = np.linalg.svd(G, compute_uv=False)

    # Angle between the two columns of the weighted design; 1.0 means exactly collinear.
    root_w = np.sqrt(w)
    c0, c1 = root_w * np.ones_like(s), root_w * s
    n0, n1 = np.linalg.norm(c0), np.linalg.norm(c1)
    cosine = float(abs(c0 @ c1) / (n0 * n1)) if n0 > 0 and n1 > 0 else float("nan")

    return {
        "n_observations": int(s.size),
        "sum_weights": sw,
        "mean_sensitivity": sbar,
        "sensitivity_scatter": scatter,
        "rsi": float(np.sqrt(scatter / sw)) if sw > 0 else float("nan"),
        "rsi_total": float(np.sqrt(scatter)),
        "det_gram": det_direct,
        "det_from_variance_identity": det_identity,
        "det_identity_residual": abs(det_direct - det_identity),
        "smallest_singular_value": float(singular.min()),
        "condition_number": (float(singular.max() / singular.min())
                             if singular.min() > 0 else float("inf")),
        "column_cosine": cosine,
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Sensitivities from a response function
# ─────────────────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SensitivityResult:
    """Log-rate sensitivities with their finite-difference convergence evidence."""

    rate: float
    step: float
    s: np.ndarray = field(repr=False)
    max_step_change: float
    per_step: dict = field(repr=False, default_factory=dict)

    @property
    def converged(self) -> bool:
        """Sensitivities stable to halving and doubling the step, relative to their own spread.

        The tolerance is relative to the spread rather than to |s| because the spread is the
        quantity that carries the information; an offset common to all observations cancels in the
        variance and cannot affect RSI.
        """
        spread = float(np.std(self.s))
        return self.max_step_change <= 0.05 * max(spread, 1e-12)


def log_rate_sensitivities(response, rate: float, step: float = DEFAULT_LOG_STEP,
                           multipliers=STEP_MULTIPLIERS) -> SensitivityResult:
    """``d log f_i / d log k`` by centred difference, with a step-convergence check.

    `response` maps a rate to the vector of unit-inventory predictions ``f_i(k)``. The difference is
    taken in log-rate because the parameter is a positive multiplier and the paper's rate grid is
    geometric; a linear step would sample the grid non-uniformly across the domain.
    """
    log_k = np.log(float(rate))
    per_step = {}
    for mult in multipliers:
        h = step * mult
        up = np.asarray(response(float(np.exp(log_k + h))), float)
        dn = np.asarray(response(float(np.exp(log_k - h))), float)
        if np.any(up <= 0) or np.any(dn <= 0):
            raise ValueError("non-positive response; log sensitivity undefined")
        per_step[h] = (np.log(up) - np.log(dn)) / (2.0 * h)

    nominal = per_step[step]
    max_change = max(float(np.max(np.abs(v - nominal))) for h, v in per_step.items() if h != step)
    return SensitivityResult(rate=float(rate), step=float(step), s=nominal,
                             max_step_change=max_change,
                             per_step={round(h, 6): v.tolist() for h, v in per_step.items()})


def design_separability(response, rate: float, weights=None,
                        step: float = DEFAULT_LOG_STEP) -> dict:
    """Convenience: sensitivities plus their separability summary for one design."""
    sens = log_rate_sensitivities(response, rate, step=step)
    out = separability(sens.s, weights)
    out.update({
        "rate": sens.rate,
        "log_step": sens.step,
        "max_step_change": sens.max_step_change,
        "step_converged": sens.converged,
        "sensitivities": sens.s.tolist(),
    })
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Validating the local diagnostic against the nonlinear profile
# ─────────────────────────────────────────────────────────────────────────────────────────────


def agreement_with_profiles(rsi_by_design: dict, width_by_design: dict) -> dict:
    """Does a higher RSI actually go with a narrower nonlinear rate profile?

    Plan §5.6 makes this the admission test for the whole diagnostic. Reported as a rank
    correlation over designs, because the claim is ordinal — RSI screens designs, it does not
    predict a width — and with the count of designs so a reader can see how thin the evidence is.

    A negative Spearman coefficient (more separability, narrower profile) is the expected sign.
    """
    designs = sorted(set(rsi_by_design) & set(width_by_design))
    if len(designs) < 3:
        return {"n_designs": len(designs), "spearman": None,
                "note": "too few designs for a rank correlation"}

    x = np.array([rsi_by_design[d] for d in designs], float)
    y = np.array([width_by_design[d] for d in designs], float)

    def _ranks(v):
        order = np.argsort(v)
        r = np.empty(len(v), float)
        r[order] = np.arange(len(v), dtype=float)
        # average ties so exact duplicates do not create a spurious ordering
        for value in np.unique(v):
            tie = v == value
            if tie.sum() > 1:
                r[tie] = r[tie].mean()
        return r

    rx, ry = _ranks(x), _ranks(y)
    if np.std(rx) == 0 or np.std(ry) == 0:
        return {"n_designs": len(designs), "spearman": None,
                "note": "no variation in one of the rankings"}
    rho = float(np.corrcoef(rx, ry)[0, 1])
    return {
        "n_designs": len(designs),
        "designs": designs,
        "spearman": round(rho, 4),
        "expected_sign": "negative (higher separability -> narrower profile)",
        "consistent_with_expectation": rho < 0,
    }


def is_not_merely_observation_count(rsi_by_design: dict, n_by_design: dict) -> dict:
    """Guard against the diagnostic being a repackaged count of observations (plan §5.6).

    If RSI simply tracked how many observations a design has, it would be useless for design
    selection — the interesting recommendation is *fewer, better-separated* measurements.
    """
    designs = sorted(set(rsi_by_design) & set(n_by_design))
    if len(designs) < 3:
        return {"n_designs": len(designs), "spearman": None}
    x = np.array([rsi_by_design[d] for d in designs], float)
    y = np.array([float(n_by_design[d]) for d in designs], float)
    if np.std(x) == 0 or np.std(y) == 0:
        return {"n_designs": len(designs), "spearman": None}
    rho = float(np.corrcoef(x, y)[0, 1])
    return {"n_designs": len(designs), "pearson_with_count": round(rho, 4),
            "note": "RSI is normalised by total weight, so a strong correlation here would be a "
                    "finding about the designs compared, not an identity"}
