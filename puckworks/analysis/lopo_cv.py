"""Cross-validation for two DISTINCT models (they are not the same dataset).

CC's investigation established the crossing that must not be conflated:
  * schmieder2023 RSM  -> factors F/G/T, response cup mass; pressure is NOT a
    factor, so leave-one-PRESSURE-out is meaningless here. Held-out unit is a
    DESIGN POINT (a distinct F,G,T condition) or an experiment id.
  * waszkiewicz2025    -> cross-pressure flow test, 11 distinct pressures; this
    is where leave-one-PRESSURE-out is the natural CV.

This module provides BOTH, each to its own schema. Neither invents data; both
reuse the committed loaders and the same retained-term / fit paths the repo
already uses (harness.schmieder_rsm_refit term set; poroelastic.fit_static).

CONSISTENCY/DIAGNOSTIC strength, not a new validation gate: with 15 experiment
settings (RSM) and 11 pressures (waszkiewicz), these CV scores are small-sample
diagnostics of predictive stability, NOT power-backed validations. Report the
number of held-out units alongside every score so the reader can weight it.
"""
import numpy as np
from puckworks import data as d


# ----------------------------------------------------------------------------
# TARGET 1 — schmieder RSM: leave-one-DESIGN-POINT-out (NOT pressure)
# ----------------------------------------------------------------------------
_SCHM_COMPONENT = {"tds": "TDS", "trigonelline": "trigonelline",
                   "caffeine": "caffeine", "5cqa": "5-CQA"}
_CENTER = dict(flow_ml_s=2.0, temp_C=89.0, g=1.7)   # mirrors harness._SCHM_CENTER


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _schm_design_rows(component="tds", brew_ratio="1/2", predictors="achieved"):
    """Run-level (F,G,T,y,exp) rows for one component x brew_ratio. Uses the source's
    ACHIEVED flow/temperature by default (review MAJ-10) to match the RSM contract."""
    comp = _SCHM_COMPONENT.get(component.lower(), component)
    fcol, tcol = (("scale_flow_ml_s", "decent_temp_C") if predictors == "achieved"
                  else ("target_flow_ml_s", "target_temp_C"))
    out = []
    for r in d.schmieder_cup_masses():
        if r.get("component") != comp or r.get("brew_ratio") != brew_ratio:
            continue
        F, G, T, y = (_f(r.get(fcol)), _f(r.get("grind_level")),
                      _f(r.get(tcol)), _f(r.get("mass_in_cup")))
        if None not in (F, G, T, y):
            out.append((F, G, T, y, r.get("exp")))
    return out


def _design_matrix(F, G, T):
    """Retained TDS-1/2 terms, identical to harness.schmieder_rsm_refit."""
    return np.column_stack([np.ones_like(F), F, G, T, G**2, T**2, F*G])


def lopo_rsm_design_point(component="tds", brew_ratio="1/2", predictors="achieved"):
    """Leave-one-SETTING-out CV of the schmieder RSM refit (review MAJ-10).

    The held-out unit is one of the **15 experiment IDs** (a nominal design setting),
    with ALL its repetitions held out together, so a held-out setting never appears in
    the training fold. The design matrix uses the source's ACHIEVED flow/temperature
    (matching `schmieder_rsm_refit(predictors='achieved')`). Refit on the other
    settings, predict the held-out setting's mean, score predicted-vs-observed-mean.

    Returns Q^2 (1 - PRESS/TSS on setting means), RMSE_cv, and per-setting residuals.
    """
    rows = _schm_design_rows(component, brew_ratio, predictors)
    o = np.asarray([(F, G, T, y) for F, G, T, y, _ in rows], float)
    F, G, T, y = o[:, 0], o[:, 1], o[:, 2], o[:, 3]
    exps = np.array([e for *_, e in rows])
    # group by EXPERIMENT ID (nominal setting); all reps of a setting travel together
    settings = sorted(set(exps))
    set_mean = {s: float(np.mean(y[exps == s])) for s in settings}
    ybar = np.mean([set_mean[s] for s in settings])
    press, resids = 0.0, {}
    for held in settings:
        tr = exps != held                              # drop ALL reps of the held setting
        coef, *_ = np.linalg.lstsq(_design_matrix(F[tr], G[tr], T[tr]), y[tr], rcond=None)
        # predict the held setting at its OWN mean achieved (F,G,T)
        fh, gh, th = (float(np.mean(F[exps == held])), float(np.mean(G[exps == held])),
                      float(np.mean(T[exps == held])))
        pred = float(_design_matrix(np.array([fh]), np.array([gh]), np.array([th]))[0] @ coef)
        r = set_mean[held] - pred
        resids[held] = r; press += r ** 2
    tss = sum((set_mean[s] - ybar) ** 2 for s in settings)
    q2 = 1.0 - press / tss if tss > 0 else float("nan")
    rmse_cv = float(np.sqrt(press / len(settings)))
    return dict(target="schmieder_rsm", held_out_unit="experiment_setting",
                component=component, brew_ratio=brew_ratio, predictors=predictors,
                n_settings=len(settings), n_run_rows=len(F),
                Q2_predictive=round(q2, 4), RMSE_cv_g=round(rmse_cv, 4),
                worst_residual_g=round(max(resids.values(), key=abs), 4),
                caveat="15 settings held out with all reps together; achieved predictors; "
                       "small n, diagnostic not power-backed; pressure is NOT an RSM factor")


# ----------------------------------------------------------------------------
# TARGET 2 — waszkiewicz: leave-one-PRESSURE-out (the meaningful one here)
# ----------------------------------------------------------------------------
def lopo_waszkiewicz_pressure():
    """Leave-one-PRESSURE-out CV of the Eq.16 static (P_c,Q_c) calibration.

    The 11-point equilibrium curve (one long-run point per reference pressure)
    is the static fit's input. Drop each pressure in turn, refit (P_c,Q_c) on the
    other 10 via poroelastic.fit_static, predict Q at the held-out pressure,
    score. This directly tests whether the static characteristic generalizes
    across the pressure axis rather than interpolating its own fit points.
    """
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    P, Q = wz.steady_state_curve()                      # 11 pts, sorted
    order = np.argsort(P)
    P, Q = P[order], Q[order]
    press, preds, resids = 0.0, [], []
    for i in range(len(P)):
        mask = np.arange(len(P)) != i
        try:
            (P_c, Q_c), _ = wz.fit_static(P[mask], Q[mask])
        except Exception as e:
            return dict(target="waszkiewicz_pressure", error=str(e),
                        note="fit_static failed on a fold; inspect held pt")
        pred = float(wz.q_static(P[i], P_c, Q_c))
        r = Q[i] - pred
        preds.append(pred); resids.append(r); press += r**2
    resids = np.asarray(resids)
    tss = float(np.sum((Q - np.mean(Q))**2))
    q2 = 1.0 - press/tss if tss > 0 else float("nan")
    return dict(target="waszkiewicz_pressure", held_out_unit="pressure_level",
                n_pressures=len(P),
                pressures_bar=[round(float(p), 2) for p in P],
                Q2_predictive=round(q2, 4),
                RMSE_cv_g_per_s=round(float(np.sqrt(press/len(P))), 4),
                worst_residual_g_per_s=round(float(resids[np.argmax(abs(resids))]), 4),
                worst_at_bar=round(float(P[np.argmax(abs(resids))]), 2),
                caveat="edge pressures (1 and 13 bar) are extrapolation folds; "
                       "expect larger held-out error there, not model failure")


if __name__ == "__main__":
    import json
    print("== RSM leave-one-design-point-out (TDS 1/2) ==")
    print(json.dumps(lopo_rsm_design_point("tds", "1/2"), indent=2))
    print("\n== Waszkiewicz leave-one-pressure-out ==")
    print(json.dumps(lopo_waszkiewicz_pressure(), indent=2))
