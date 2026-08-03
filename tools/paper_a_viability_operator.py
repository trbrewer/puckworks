#!/usr/bin/env python3
"""Part B — observation-operator comparison on the Schmieder campaign (EXPLORATORY).

    EXPLORATORY_SAME_CAMPAIGN_VIABILITY_SCREEN
    NOT_A_FROZEN_P0_GATE_RESULT

Do temporal fraction observations localise the common mass-transfer-rate multiplier more strongly
than cumulative cup observations, on the same shots and the same model?

Three arms, all read from the SAME model integration per (shot, solute, κ) — only the observation
subset differs, which is what makes the comparison an operator comparison rather than a model
comparison:

    ARM F  FRACTION_6    six measured interval concentrations, fractions 1,2,3,5,7,10
    ARM C  CUP_CURVE_3   three cumulative cup concentrations, brew ratios 1/1, 1/2, 1/3
    ARM E  CUP_FINAL_1   the final cumulative cup concentration only, brew ratio 1/3

`CUP_FINAL_1` is an analytical negative control: one observation and one free level per shot makes
the profile flat by construction. That is proved and tested, not presented as a finding.

**Same-campaign.** The model parameters were originally fitted in this source lineage. This is an
observation-operator study, not independent physical validation.

CLI::

    python tools/paper_a_viability_operator.py --predict     # build the prediction cache
    python tools/paper_a_viability_operator.py --write       # analyse and write outputs
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import pickle
import platform
import sys
import warnings

import numpy as np

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

DATA_DIR = _REPO / "puckworks" / "data" / "schmieder2023"
FRACTIONS = DATA_DIR / "raw_fractions.csv"
CUPS = DATA_DIR / "cup_masses.csv"
OUT_DIR = _REPO / "docs" / "paper1_resource" / "exploratory"
OUT_JSON = OUT_DIR / "PAPER_A_VIABILITY_OBSERVATION_OPERATOR_V1.json"
MANIFEST = OUT_DIR / "PAPER_A_VIABILITY_MATCHED_DATA_MANIFEST_V1.json"
CACHE = _REPO / ".viability_operator_cache.pkl"

STATUS = "EXPLORATORY_SAME_CAMPAIGN_VIABILITY_SCREEN"
NOT_GATE = "NOT_A_FROZEN_P0_GATE_RESULT"

#: Source dose and brew-ratio definition: BR 1/n means n x dose grams of beverage.
DOSE_G = 20.0
BREW_RATIOS = (("1/1", 1), ("1/2", 2), ("1/3", 3))
MEASURED_FRACTIONS = (1, 2, 3, 5, 7, 10)

#: Solute key mapping between the two source tables and the solver's parameter block.
SOLUTES = (
    ("caffeine", "c_caffeine_mg_g", "caffeine"),
    ("trigonelline", "c_trigonelline_mg_g", "trigonelline"),
    ("5CQA", "c_5cqa_mg_g", "5-CQA"),
)

#: The kappa domain, unchanged from the accepted architecture.
KAPPA_LO, KAPPA_HI = 0.15, 500.0
KAPPA_N = 64

#: Only the centre grind has declared grain parameters in this port; see `grind_policy`.
DECLARED_GRIND_LEVEL = 1.7

ARMS = ("FRACTION_6", "CUP_CURVE_3", "CUP_FINAL_1")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Matched evidence unit
# ─────────────────────────────────────────────────────────────────────────────────────────────


def _f(row, key):
    v = row[key].strip()
    return float(v) if v else None


def build_matched_unit():
    """The exact experiment x replicate x solute intersection, with exclusions recorded.

    A shot is admitted only when it carries all six measured fractions with all three solute
    concentrations AND all three brew ratios with all three solute concentrations. Nothing is
    imputed.
    """
    frac_rows = list(csv.DictReader(FRACTIONS.open(encoding="utf-8")))
    cup_rows = list(csv.DictReader(CUPS.open(encoding="utf-8")))

    frac_by_shot, frac_incomplete = {}, {}
    for r in frac_rows:
        shot = (_f(r, "exp"), _f(r, "rep"))
        need = ["mass_fraction_g", "mass_accumulated_g"] + [c for _, c, _ in SOLUTES]
        missing = [k for k in need if _f(r, k) is None]
        if missing:
            frac_incomplete.setdefault(shot, []).append(
                {"fraction": _f(r, "fraction"), "missing": missing})
            continue
        frac_by_shot.setdefault(shot, {})[int(_f(r, "fraction"))] = {
            "fraction": int(_f(r, "fraction")),
            "mass_fraction_g": _f(r, "mass_fraction_g"),
            "mass_midpoint_g": _f(r, "mass_accumulated_g"),
            **{s: _f(r, c) for s, c, _ in SOLUTES},
        }

    cup_by_shot, cup_meta, cup_incomplete = {}, {}, {}
    for r in cup_rows:
        shot = (_f(r, "exp"), _f(r, "rep"))
        comp = r["component"]
        if comp == "TDS":
            continue
        if _f(r, "conc_in_cup") is None or _f(r, "grind_level") is None:
            cup_incomplete.setdefault(shot, []).append(
                {"component": comp, "brew_ratio": r["brew_ratio"]})
            continue
        cup_by_shot.setdefault(shot, {})[(comp, r["brew_ratio"])] = _f(r, "conc_in_cup")
        cup_meta[shot] = {
            "scale_flow_ml_s": _f(r, "scale_flow_ml_s"),
            "target_flow_ml_s": _f(r, "target_flow_ml_s"),
            "decent_temp_C": _f(r, "decent_temp_C"),
            "target_temp_C": _f(r, "target_temp_C"),
            "grind_level": _f(r, "grind_level"),
            "doe_role": r["doe_role"],
        }

    need_cup = {(src, br) for _, _, src in SOLUTES for br, _ in BREW_RATIOS}
    shots, exclusions = [], []
    for shot in sorted(set(frac_by_shot) | set(cup_by_shot)):
        f = frac_by_shot.get(shot, {})
        c = cup_by_shot.get(shot, {})
        why = []
        if set(f) != set(MEASURED_FRACTIONS):
            why.append("fraction set %s != %s" % (sorted(f), list(MEASURED_FRACTIONS)))
        if not need_cup <= set(c):
            why.append("incomplete cup grid")
        if shot not in cup_meta:
            why.append("no run metadata")
        elif cup_meta[shot]["scale_flow_ml_s"] is None or cup_meta[shot]["decent_temp_C"] is None:
            why.append("missing measured flow or temperature")
        if why:
            exclusions.append({"exp": shot[0], "rep": shot[1], "reasons": why,
                               "fraction_rows_incomplete": frac_incomplete.get(shot, []),
                               "cup_rows_incomplete": cup_incomplete.get(shot, [])})
            continue
        meta = cup_meta[shot]
        windows = []
        for k in MEASURED_FRACTIONS:
            row = f[k]
            m, mid = row["mass_fraction_g"], row["mass_midpoint_g"]
            windows.append({"fraction": k, "mass_g": m,
                            "start_g": mid - m / 2.0, "end_g": mid + m / 2.0,
                            **{s: row[s] for s, _, _ in SOLUTES}})
        shots.append({
            "exp": shot[0], "rep": shot[1], **meta,
            "windows": windows,
            "cup": {"%s|%s" % (src, br): c[(src, br)]
                    for _, _, src in SOLUTES for br, _ in BREW_RATIOS},
            "cup_targets_g": {br: DOSE_G * n for br, n in BREW_RATIOS},
        })
    return shots, exclusions


def grind_policy():
    """Why the primary analysis restricts to the centre grind.

    `puckworks/models/pannusch2024/solver.py` states that `psi`/`d_s2` are fitted per grind
    (1.4/1.7/2.0) but that the per-experiment assignment lives in the source's opaque parameter
    list, so the port carries the centre grind only, as a documented approximation. Declared grain
    parameters therefore exist for GL 1.7 and for no other level.

    Primary: GL 1.7 shots, where the declared parameters ARE the actual grind's parameters.
    Sensitivity: all shots under the port's documented centre-grind approximation.
    """
    return {
        "declared_grind_level": DECLARED_GRIND_LEVEL,
        "primary": "shots at GL 1.7 only; declared grain parameters match the actual grind",
        "sensitivity": ("all admitted shots under the port's documented centre-grind approximation "
                        "(solver.py: psi/d_s2 vary <15% across grinds, effect on MAPE second order)"),
        "why": ("the per-experiment grind assignment is opaque in the source, so no declared "
                "parameter set exists for GL 1.4 or GL 2.0. Using GL 1.7 parameters for those "
                "shots is an approximation, not a measurement, and is reported as a sensitivity "
                "rather than as the primary result."),
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Model predictions — one integration per (shot, solute, kappa) serves all three arms
# ─────────────────────────────────────────────────────────────────────────────────────────────


def kappa_grid():
    return np.geomspace(KAPPA_LO, KAPPA_HI, KAPPA_N)


def _boundaries(shot):
    """Sorted unique beverage-mass boundaries, and the index of each observable."""
    marks = {0.0}
    for w in shot["windows"]:
        marks.add(round(w["start_g"], 9))
        marks.add(round(w["end_g"], 9))
    for br, _ in BREW_RATIOS:
        marks.add(round(shot["cup_targets_g"][br], 9))
    return sorted(marks)


def predict_shot(shot, solute, kappa):
    """Unit-inventory predictions for every observable of one shot, from ONE integration.

    Returns `(fraction_avgs, cup_concs)` in the solver's concentration units at `c_s0 = 1`.
    Interval averages and cumulative concentrations both come from the same cumulative solute mass
    and cumulative beverage mass, which is why the three arms are genuinely the same model.
    """
    from puckworks.models.pannusch2024 import solver as ps

    flow = shot["scale_flow_ml_s"]
    T = shot["decent_temp_C"]
    sp = dict(ps._solute_params()[solute])
    sp["A1"] = sp["A1"] * kappa
    sp["A2"] = sp["A2"] * kappa
    sp["c_s0"] = 1.0

    masses = _boundaries(shot)
    times = [m / flow for m in masses]                 # source treats the flow number as g/s
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        avgs = ps.simulate_fractions(T, flow, times, sp, cl1=1.0)

    d_mass = np.diff(np.asarray(masses, float))
    m_inc = np.asarray(avgs, float) * d_mass           # solute mass per interval
    m_cum = np.concatenate([[0.0], np.cumsum(m_inc)])

    idx = {round(m, 9): i for i, m in enumerate(masses)}
    frac = []
    for w in shot["windows"]:
        i0, i1 = idx[round(w["start_g"], 9)], idx[round(w["end_g"], 9)]
        frac.append((m_cum[i1] - m_cum[i0]) / (masses[i1] - masses[i0]))
    cup = {}
    for br, _ in BREW_RATIOS:
        i = idx[round(shot["cup_targets_g"][br], 9)]
        cup[br] = m_cum[i] / masses[i]
    return np.array(frac), cup


def build_predictions(shots, progress=True):
    """Prediction table over (shot, solute, kappa). Cached to disk; this is the only slow step."""
    grid = kappa_grid()
    table = {}
    total = len(shots) * len(SOLUTES) * len(grid)
    done = 0
    for shot in shots:
        key0 = (shot["exp"], shot["rep"])
        for solute, _, _ in SOLUTES:
            for k in grid:
                f, c = predict_shot(shot, solute, float(k))
                table[(key0, solute, float(k))] = (f, c)
                done += 1
            if progress:
                print("    %s exp %g rep %g %-13s %d/%d"
                      % ("predicted", key0[0], key0[1], solute, done, total), flush=True)
    return table


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Objectives — exact level profiling, shots weighted equally
# ─────────────────────────────────────────────────────────────────────────────────────────────


def profile_level_mape(pred, obs):
    """Exact MAPE-minimising level for one shot, and the resulting per-shot MAPE."""
    pred = np.asarray(pred, float)
    obs = np.asarray(obs, float)
    r = obs / pred
    w = pred / obs
    o = np.argsort(r)
    r, w = r[o], w[o]
    cw = np.cumsum(w)
    k = int(np.searchsorted(cw, 0.5 * cw[-1]))
    level = float(r[min(k, len(r) - 1)])
    return level, float(np.mean(np.abs(level * pred - obs) / obs) * 100.0)


def profile_level_logrmse(pred, obs):
    """Exact log-RMSE-minimising level: the geometric-mean ratio."""
    pred = np.asarray(pred, float)
    obs = np.asarray(obs, float)
    level = float(np.exp(np.mean(np.log(obs / pred))))
    resid = np.log(level * pred) - np.log(obs)
    return level, float(np.sqrt(np.mean(resid ** 2)))


OBJECTIVES = {"mape": profile_level_mape, "log_rmse": profile_level_logrmse}


def arm_observations(shot, solute, arm, table, kappa):
    """(prediction, observation) vectors for one shot, solute and arm."""
    src = dict((s, src) for s, _, src in SOLUTES)[solute]
    f, c = table[((shot["exp"], shot["rep"]), solute, float(kappa))]
    if arm == "FRACTION_6":
        obs = np.array([w[solute] for w in shot["windows"]], float)
        return np.asarray(f, float), obs
    if arm == "CUP_CURVE_3":
        brs = [br for br, _ in BREW_RATIOS]
        return (np.array([c[br] for br in brs], float),
                np.array([shot["cup"]["%s|%s" % (src, br)] for br in brs], float))
    if arm == "CUP_FINAL_1":
        return (np.array([c["1/3"]], float),
                np.array([shot["cup"]["%s|1/3" % src]], float))
    raise ValueError(arm)


def positivity_ok(shots, solute, arm, table, kappa):
    """Protocol positivity precondition: every prediction and observation must be strictly positive.

    At high kappa the bed is exhausted before the late fractions, and the late interval-average
    predictions fall to zero and then slightly below it. That is a HARD FAILURE at that kappa, not a
    value to be quietly clipped or logged away: it is recorded, the kappa is excluded from the
    profile, and the excluded range is reported.
    """
    for s in shots:
        pred, obs = arm_observations(s, solute, arm, table, kappa)
        if np.any(np.asarray(pred) <= 0) or np.any(np.asarray(obs) <= 0):
            return False
    return True


def shot_balanced_objective(shots, solute, arm, table, kappa, objective="mape",
                            level_policy="per_shot"):
    """Mean over shots of the per-shot objective, so every shot carries equal weight.

    Six fraction rows must not give a shot six times the influence of a three-point cup curve;
    averaging per-shot scores rather than pooling rows is what enforces that.
    """
    fn = OBJECTIVES[objective]
    if level_policy == "per_shot":
        scores = []
        for s in shots:
            pred, obs = arm_observations(s, solute, arm, table, kappa)
            scores.append(fn(pred, obs)[1])
        return float(np.mean(scores))

    # common level per solute across shots, profiled exactly on the pooled ratios
    preds, obss, sizes = [], [], []
    for s in shots:
        pred, obs = arm_observations(s, solute, arm, table, kappa)
        preds.append(pred)
        obss.append(obs)
        sizes.append(len(pred))
    allp, allo = np.concatenate(preds), np.concatenate(obss)
    # shot-balanced weights so a six-row shot does not dominate the level
    wts = np.concatenate([np.full(n, 1.0 / n) for n in sizes])
    if objective == "mape":
        r, w = allo / allp, (allp / allo) * wts
        o = np.argsort(r)
        r, w = r[o], w[o]
        cw = np.cumsum(w)
        level = float(r[min(int(np.searchsorted(cw, 0.5 * cw[-1])), len(r) - 1)])
    else:
        level = float(np.exp(np.sum(wts * np.log(allo / allp)) / np.sum(wts)))
    scores = []
    for pred, obs in zip(preds, obss):
        if objective == "mape":
            scores.append(float(np.mean(np.abs(level * pred - obs) / obs) * 100.0))
        else:
            resid = np.log(level * pred) - np.log(obs)
            scores.append(float(np.sqrt(np.mean(resid ** 2))))
    return float(np.mean(scores))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Localisation metrics
# ─────────────────────────────────────────────────────────────────────────────────────────────


def accepted_set(kappa, J, threshold):
    """Connected components of {kappa : J(kappa) <= T}, with edges refined by log-linear interp.

    Only grid predictions exist (each off-grid kappa would be a fresh integration), so component
    edges are interpolated between bracketing grid points rather than root-solved. The grid is
    64 log-spaced points over 3.52 decades, i.e. 0.055 decades per step, which bounds the edge error.
    """
    kappa = np.asarray(kappa, float)
    J = np.asarray(J, float)
    lk = np.log10(kappa)
    inside = J <= threshold
    if not inside.any():
        return {"components": [], "log10_width": 0.0, "status": "empty",
                "left_censored": False, "right_censored": False, "n_components": 0}

    def edge(i, j):
        if J[j] == J[i]:
            return lk[j]
        return lk[i] + (threshold - J[i]) * (lk[j] - lk[i]) / (J[j] - J[i])

    comps, start = [], None
    for i, v in enumerate(inside):
        if v and start is None:
            start = i
        if (not v or i == len(inside) - 1) and start is not None:
            end = i if v else i - 1
            lo = lk[0] if start == 0 else edge(start - 1, start)
            hi = lk[-1] if end == len(inside) - 1 else edge(end + 1, end)
            comps.append((float(lo), float(hi)))
            start = None

    left = comps[0][0] <= lk[0] + 1e-12
    right = comps[-1][1] >= lk[-1] - 1e-12
    width = float(sum(hi - lo for lo, hi in comps))
    if left and right:
        status = "doubly_censored"
    elif left:
        status = "left_censored"
    elif right:
        status = "right_censored"
    elif len(comps) > 1:
        status = "disconnected"
    else:
        status = "finite"
    return {"components": [[float(10 ** lo), float(10 ** hi)] for lo, hi in comps],
            "log10_width": width, "status": status,
            "left_censored": bool(left), "right_censored": bool(right),
            "n_components": len(comps)}


def localisation(shots, solute, arm, table, objective="mape", level_policy="per_shot"):
    """kappa profile and its accepted sets for one solute/arm/policy."""
    grid = kappa_grid()
    valid = np.array([positivity_ok(shots, solute, arm, table, float(k)) for k in grid])
    if not valid.any():
        return {"positivity": {"valid_fraction": 0.0}, "kappa": [], "J": [],
                "kappa_minimiser": None, "J_min": None, "profile_is_flat": None,
                "accepted_rel10": {"status": "no_valid_kappa"}, "accepted_abs25": None,
                "accepted_log10_width_rel10": None}
    gv = grid[valid]
    J = np.array([shot_balanced_objective(shots, solute, arm, table, float(k), objective,
                                          level_policy) for k in gv])
    i = int(np.argmin(J))
    J_min = float(J[i])
    flat = bool(np.ptp(J) <= 1e-12 * max(1.0, abs(J_min)))
    rel10 = accepted_set(gv, J, J_min * 1.10)
    abs25 = accepted_set(gv, J, J_min + 0.25) if objective == "mape" else None

    # the accepted set is only trustworthy if it lies strictly inside the positivity-valid range
    hi_valid = float(gv[-1])
    contained = all(hi <= hi_valid * (1 + 1e-12) for _, hi in
                    [tuple(c) for c in rel10.get("components", [])])
    return {
        "kappa": [float(k) for k in gv], "J": [float(v) for v in J],
        "kappa_minimiser": float(gv[i]), "J_min": J_min,
        "profile_is_flat": flat,
        "accepted_rel10": rel10, "accepted_abs25": abs25,
        "accepted_log10_width_rel10": (None if flat else rel10["log10_width"]),
        "grid_resolution_decades": float(np.log10(KAPPA_HI / KAPPA_LO) / (KAPPA_N - 1)),
        "positivity": {
            "rule": "every prediction and observation strictly positive (protocol 1.1)",
            "n_grid": int(len(grid)), "n_valid": int(valid.sum()),
            "valid_fraction": float(valid.mean()),
            "valid_kappa_range": [float(gv[0]), float(gv[-1])],
            "first_violating_kappa": (float(grid[~valid][0]) if (~valid).any() else None),
            "why": ("at high kappa the bed is exhausted before the late fractions, so late "
                    "interval-average predictions reach zero and then go slightly negative. Those "
                    "kappa are EXCLUDED and recorded, never clipped."),
            "accepted_set_inside_valid_range": bool(contained),
            "minimiser_decades_below_first_violation": (
                float(np.log10(grid[~valid][0] / gv[i])) if (~valid).any() else None),
        },
    }


def negative_control_proof():
    """Why CUP_FINAL_1 must be flat, before any number is computed.

    With one observation `y` and one free positive level `I`, the exact MAPE minimiser is
    `I* = y / f(kappa)` for every `kappa`, so `|I* f(kappa) - y| = 0` identically and the per-shot
    MAPE is exactly zero at every `kappa`. The profile therefore carries NO information about the
    rate: it is flat by construction, not by an empirical accident, and it is not evidence that the
    fraction arm "won".
    """
    return {
        "arm": "CUP_FINAL_1",
        "claim": "the rate profile is exactly flat for every kappa",
        "proof": ("one observation y and one free level I give the exact MAPE minimiser "
                  "I* = y/f(kappa); then |I* f(kappa) - y| = 0 identically, so the per-shot MAPE "
                  "is 0 at every kappa and the profile is constant"),
        "status": "analytic; verified numerically in the results",
        "consequence": "carries no rate information and is not counted as evidence for any arm",
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Leave-one-experiment-out held-out prediction
# ─────────────────────────────────────────────────────────────────────────────────────────────


def _anchor_and_score(shot, solute, arm, table, kappa):
    """Anchor the level on the FIRST observation only, then score the remaining observations."""
    pred, obs = arm_observations(shot, solute, arm, table, kappa)
    if len(pred) < 2:
        return None, None
    level = float(obs[0] / pred[0])
    rest_p, rest_o = pred[1:], obs[1:]
    return level, float(np.mean(np.abs(level * rest_p - rest_o) / rest_o) * 100.0)


def leave_one_experiment_out(shots, solute, arm, table, objective="mape"):
    """Fit kappa on training experiments; predict held-out temporal shape from a first-point anchor."""
    if arm == "CUP_FINAL_1":
        return {"applicable": False,
                "why": "no observation remains after the level anchor, so no held-out score exists"}
    grid = kappa_grid()
    exps = sorted({s["exp"] for s in shots})
    folds, scores, boundary_hits, failures = [], [], 0, 0
    for e in exps:
        train = [s for s in shots if s["exp"] != e]
        test = [s for s in shots if s["exp"] == e]
        if not train or not test:
            continue
        J = np.array([shot_balanced_objective(train, solute, arm, table, float(k), objective)
                      for k in grid])
        k_hat = float(grid[int(np.argmin(J))])
        if k_hat >= KAPPA_HI * (1 - 1e-9):
            boundary_hits += 1
        fold_scores = []
        for s in test:
            _, sc = _anchor_and_score(s, solute, arm, table, k_hat)
            if sc is None:
                failures += 1
            else:
                fold_scores.append(sc)
        if fold_scores:
            folds.append({"held_out_exp": e, "kappa": k_hat,
                          "heldout_mape": float(np.mean(fold_scores)), "n_shots": len(fold_scores)})
            scores.extend(fold_scores)
    ks = [f["kappa"] for f in folds]
    return {
        "applicable": True, "folds": folds,
        "fold_kappa": ks,
        "median_log10_kappa": float(np.median(np.log10(ks))) if ks else None,
        "range_log10_kappa": ([float(np.min(np.log10(ks))), float(np.max(np.log10(ks)))]
                              if ks else None),
        "spread_log10_kappa": (float(np.ptp(np.log10(ks))) if ks else None),
        "heldout_mape": float(np.mean(scores)) if scores else None,
        "right_boundary_hits": boundary_hits, "failed_fits": failures,
        "n_folds": len(folds),
    }


def material_improvement(frac, cup, loeo_frac, loeo_cup):
    """The declared rule: 0.5 decades narrower, or censored -> finite, without paying >0.5 pp."""
    wf = frac["accepted_log10_width_rel10"]
    wc = cup["accepted_log10_width_rel10"]
    narrower = (wf is not None and wc is not None and (wc - wf) >= 0.5)
    censor_fixed = (cup["accepted_rel10"]["status"] in ("right_censored", "doubly_censored")
                    and frac["accepted_rel10"]["status"] == "finite")
    hf = loeo_frac.get("heldout_mape")
    hc = loeo_cup.get("heldout_mape")
    not_paid = (hf is not None and hc is not None and (hf - hc) <= 0.5)
    return {
        "width_fraction": wf, "width_cup": wc,
        "width_reduction_decades": (None if (wf is None or wc is None) else wc - wf),
        "at_least_half_decade_narrower": bool(narrower),
        "censored_to_finite": bool(censor_fixed),
        "heldout_mape_fraction": hf, "heldout_mape_cup": hc,
        "heldout_penalty_pp": (None if (hf is None or hc is None) else hf - hc),
        "not_worse_by_more_than_half_pp": bool(not_paid),
        "materially_more_localising": bool((narrower or censor_fixed) and not_paid),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--predict", action="store_true", help="build the prediction cache")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--all-grinds", action="store_true",
                    help="sensitivity: include every admitted shot, not only GL 1.7")
    args = ap.parse_args(argv)

    shots, exclusions = build_matched_unit()
    primary = [s for s in shots if s["grind_level"] == DECLARED_GRIND_LEVEL]
    use = shots if args.all_grinds else primary
    print("matched shots: %d admitted, %d excluded; GL1.7 primary set: %d"
          % (len(shots), len(exclusions), len(primary)))
    for e in exclusions:
        print("  excluded exp %g rep %g: %s" % (e["exp"], e["rep"], "; ".join(e["reasons"])))

    if args.predict:
        print("building predictions for %d shots x %d solutes x %d kappa..."
              % (len(use), len(SOLUTES), KAPPA_N), flush=True)
        table = build_predictions(use)
        with open(CACHE, "wb") as fh:
            pickle.dump({"table": table, "shots": use, "exclusions": exclusions}, fh)
        print("cached %d predictions -> %s" % (len(table), CACHE.name))
        return 0

    if args.write:
        with open(CACHE, "rb") as fh:
            cached = pickle.load(fh)
        table = cached["table"]
        result = analyse(use, table, exclusions, all_grinds=args.all_grinds)
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
        MANIFEST.write_text(json.dumps(matched_manifest(use, exclusions), indent=1) + "\n",
                            encoding="utf-8")
        print("wrote %s" % OUT_JSON.relative_to(_REPO))
        print("wrote %s" % MANIFEST.relative_to(_REPO))
    return 0


def matched_manifest(shots, exclusions):
    """Row-level provenance for the matched unit, with source hashes."""
    return {
        "status": STATUS, "not_a_gate": NOT_GATE, "gate_binding": None,
        "sources": {
            "raw_fractions.csv": {
                "path": "puckworks/data/schmieder2023/raw_fractions.csv",
                "sha256": hashlib.sha256(FRACTIONS.read_bytes()).hexdigest()},
            "cup_masses.csv": {
                "path": "puckworks/data/schmieder2023/cup_masses.csv",
                "sha256": hashlib.sha256(CUPS.read_bytes()).hexdigest()},
        },
        "matching_rule": ("experiment x replicate x solute; a shot is admitted only with all six "
                          "measured fractions and all three brew ratios for all three solutes. "
                          "Nothing is imputed."),
        "window_derivation": ("raw_fractions.mass_accumulated_g is the interval MIDPOINT mass "
                              "(verified: fraction 1 midpoint = mass/2), so the window is "
                              "[mid - mass/2, mid + mass/2] in cumulative beverage grams; time "
                              "follows from the measured flow, which the source treats as g/s. "
                              "Measured fractions are 1,2,3,5,7,10 and are NOT contiguous."),
        "cup_targets": {"1/1": DOSE_G, "1/2": 2 * DOSE_G, "1/3": 3 * DOSE_G,
                        "dose_g": DOSE_G},
        "n_admitted": len(shots), "n_excluded": len(exclusions),
        "exclusions": exclusions,
        "shots": [{"exp": s["exp"], "rep": s["rep"], "grind_level": s["grind_level"],
                   "scale_flow_ml_s": s["scale_flow_ml_s"], "decent_temp_C": s["decent_temp_C"],
                   "doe_role": s["doe_role"],
                   "windows_g": [[w["fraction"], w["start_g"], w["end_g"]] for w in s["windows"]]}
                  for s in shots],
    }


def residual_shape(shots, solute, arm, table, kappa):
    """Mean signed relative residual per observation index, at a given kappa.

    This separates two very different explanations for a poor fit: a model that cannot reproduce the
    TEMPORAL SHAPE leaves a structured residual pattern, whereas an observation operator that simply
    carries less information about the rate does not.
    """
    R = []
    for s in shots:
        pred, obs = arm_observations(s, solute, arm, table, kappa)
        level, _ = profile_level_mape(pred, obs)
        R.append((level * np.asarray(pred) - np.asarray(obs)) / np.asarray(obs) * 100.0)
    R = np.asarray(R)
    labels = ([("fraction_%d" % f) for f in MEASURED_FRACTIONS] if arm == "FRACTION_6"
              else [("brew_ratio_%s" % b) for b, _ in BREW_RATIOS])
    return {"kappa": float(kappa),
            "mean_signed_relative_residual_pct": dict(zip(labels, [float(v) for v in R.mean(0)])),
            "worst_abs_mean_residual_pct": float(np.abs(R.mean(0)).max())}


def analyse(shots, table, exclusions, all_grinds=False):
    """Every arm, solute, objective and level policy, plus LOEO and the decision rule."""
    solute_names = [s for s, _, _ in SOLUTES]
    out_solutes, profiles, loeo_all = [], {}, {}

    for solute in solute_names:
        arms = {}
        for arm in ARMS:
            loc = localisation(shots, solute, arm, table, "mape", "per_shot")
            profiles[(solute, arm)] = {"kappa": loc["kappa"], "J": loc["J"]}
            lo = leave_one_experiment_out(shots, solute, arm, table, "mape")
            loeo_all[(solute, arm)] = lo
            arms[arm] = {
                "primary_mape_per_shot_level": {k: v for k, v in loc.items() if k != "kappa"},
                "sensitivity_log_rmse": {
                    k: v for k, v in localisation(shots, solute, arm, table,
                                                  "log_rmse", "per_shot").items()
                    if k not in ("kappa", "J")},
                "sensitivity_common_level_per_solute": {
                    k: v for k, v in localisation(shots, solute, arm, table,
                                                  "mape", "common_per_solute").items()
                    if k not in ("kappa", "J")},
                "leave_one_experiment_out": lo,
                "kappa_minimiser": loc["kappa_minimiser"], "J_min": loc["J_min"],
                "accepted_log10_width_rel10": loc["accepted_log10_width_rel10"],
                "accepted_rel10_status": loc["accepted_rel10"]["status"],
                "accepted_abs25_status": (loc["accepted_abs25"]["status"]
                                          if loc["accepted_abs25"] else None),
                "accepted_log10_width_abs25": (loc["accepted_abs25"]["log10_width"]
                                               if loc["accepted_abs25"] else None),
                "profile_is_flat": loc["profile_is_flat"],
                "residual_shape_at_best_kappa": (
                    residual_shape(shots, solute, arm, table, loc["kappa_minimiser"])
                    if loc["kappa_minimiser"] is not None and arm != "CUP_FINAL_1" else None),
            }
        rule = material_improvement(arms["FRACTION_6"]["primary_mape_per_shot_level"],
                                    arms["CUP_CURVE_3"]["primary_mape_per_shot_level"],
                                    loeo_all[(solute, "FRACTION_6")],
                                    loeo_all[(solute, "CUP_CURVE_3")])
        out_solutes.append({"solute": solute, "arms": arms, "material_improvement": rule})
        print("  %-13s F width=%s C width=%s -> materially_more_localising=%s"
              % (solute, rule["width_fraction"], rule["width_cup"],
                 rule["materially_more_localising"]), flush=True)

    n_material = sum(1 for r in out_solutes if r["material_improvement"]
                     ["materially_more_localising"])
    return {
        "status": STATUS, "not_a_gate": NOT_GATE, "gate_binding": None,
        "date": "2026-08-03",
        "question": ("Do temporal fraction observations localise the common mass-transfer-rate "
                     "multiplier more strongly than cumulative cup observations, on the same "
                     "shots and the same model?"),
        "same_campaign_caveat": ("The model parameters were originally fitted in this source "
                                 "lineage. This is a same-campaign observation-operator study, "
                                 "NOT independent physical validation."),
        "arms": list(ARMS),
        "arm_definitions": {
            "FRACTION_6": "six measured interval concentrations, fractions 1,2,3,5,7,10",
            "CUP_CURVE_3": "three cumulative cup concentrations, brew ratios 1/1, 1/2, 1/3",
            "CUP_FINAL_1": "final cumulative cup concentration only, brew ratio 1/3",
        },
        "negative_control": negative_control_proof(),
        "grind_policy": grind_policy(),
        "shot_set": {"n_shots": len(shots), "all_grinds": bool(all_grinds),
                     "experiments": sorted({s["exp"] for s in shots}),
                     "grind_levels": sorted({s["grind_level"] for s in shots})},
        "kappa_domain": [KAPPA_LO, KAPPA_HI], "kappa_grid_points": KAPPA_N,
        "objectives": {"primary": "shot-balanced MAPE with exact per-shot level profiling",
                       "sensitivity": "shot-balanced log-RMSE",
                       "weighting": ("shots weighted equally, so six fraction rows do not give a "
                                     "shot six times the influence of a three-point cup curve")},
        "solutes": out_solutes,
        "n_solutes_materially_improved": n_material,
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": __import__("scipy").__version__},
        "hashes": {
            "producer_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
            "raw_fractions_sha256": hashlib.sha256(FRACTIONS.read_bytes()).hexdigest(),
            "cup_masses_sha256": hashlib.sha256(CUPS.read_bytes()).hexdigest(),
        },
        "_profiles": {"%s|%s" % k: v for k, v in profiles.items()},
        "_loeo": {"%s|%s" % k: v for k, v in loeo_all.items()},
    }


if __name__ == "__main__":
    raise SystemExit(main())
