#!/usr/bin/env python3
"""Temporal-model-discrepancy screen (EXPLORATORY).

    EXPLORATORY_SCIENTIFIC_SCREEN
    NOT_A_FORMAL_P0_GATE_RESULT

Does validation against cumulative/integrated extraction metrics understate temporal model
discrepancy, and does one minimal mechanistic extension resolve it?

Three models, all scored against RAW fraction observations:

    BASE        the current two-grain mechanistic solver
    SLOW_TAIL   BASE plus one slow-accessible inventory subpopulation
    BIEXP       a flexible positive two-timescale empirical benchmark (form fixed before fitting)
    SRC_EXP     the source's single-exponential kinetics, the lineage baseline

The cumulative "cup" targets are NOT independent measurements. They are the analytic integral of
each replicate's own fitted single exponential (§ lineage audit), so they are a smoothed functional
of the same fraction campaign and cannot be used as the principal model-selection score.

CLI::

    python tools/paper_a_temporal_discrepancy.py --lineage      # Phase 1
    python tools/paper_a_temporal_discrepancy.py --predict      # model prediction cache
    python tools/paper_a_temporal_discrepancy.py --analyse      # Phases 2-3 + decision inputs
"""
from __future__ import annotations

import argparse
import csv
import functools
import hashlib
import json
import math
import pathlib
import pickle
import platform
import sys
import warnings

import numpy as np

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

DATA = _REPO / "puckworks" / "data" / "schmieder2023"
FRACTIONS = DATA / "raw_fractions.csv"
CUPS = DATA / "cup_masses.csv"
KFIT = DATA / "kinetics_fit_params_reps.csv"
OUT_DIR = _REPO / "docs" / "paper1_resource" / "exploratory" / "temporal_discrepancy"
FIG_DIR = OUT_DIR / "figures"
CACHE = _REPO / ".temporal_prediction_cache.pkl"

STATUS = "EXPLORATORY_SCIENTIFIC_SCREEN"
NOT_GATE = "NOT_A_FORMAL_P0_GATE_RESULT"

BREW_RATIOS = (("1/1", 20.0), ("1/2", 40.0), ("1/3", 60.0))
MEASURED_FRACTIONS = (1, 2, 3, 5, 7, 10)
LATE_FRACTIONS = (7, 10)
SOLUTES = (("caffeine", "c_caffeine_mg_g", "caffeine"),
           ("trigonelline", "c_trigonelline_mg_g", "trigonelline"),
           ("5CQA", "c_5cqa_mg_g", "5-CQA"))
DECLARED_GRIND_LEVEL = 1.7

#: Parameter grids, declared before fitting.
KAPPA_GRID = np.geomspace(0.3, 30.0, 12)
ALPHA_GRID = np.array([0.05, 0.10, 0.20, 0.35, 0.50])
RATIO_GRID = np.array([0.5, 0.2, 0.1, 0.05, 0.02])

BOOTSTRAP_B = 4000
BOOTSTRAP_SEED = 0


def _f(row, key):
    v = row[key].strip()
    return float(v) if v else None


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Phase 1 — cup-target lineage
# ─────────────────────────────────────────────────────────────────────────────────────────────


def lineage_audit():
    """Reconstruct the published cup targets from the per-replicate fitted kinetics.

    The source's extraction-kinetics form is a single exponential in cumulative beverage mass,
    `c(m) = c0 · exp(−m/λ)`, fitted per replicate and per component (Table S2). The published cup
    component mass at brew ratio `M` is reproduced by the ANALYTIC INTEGRAL of that fitted curve:

        mass_in_cup(M) = ∫₀^M c0 exp(−m/λ) dm = c0 · λ · (1 − exp(−M/λ))

    with no measured first-fraction term. `conc_in_cup = mass_in_cup / M` exactly.
    """
    kp = list(csv.DictReader(KFIT.open(encoding="utf-8")))
    cm = list(csv.DictReader(CUPS.open(encoding="utf-8")))
    fit = {(_f(r, "exp"), _f(r, "rep"), r["component"]):
           (_f(r, "c0"), _f(r, "lambda_g"), _f(r, "adj_r2")) for r in kp}

    rows, deviations = [], []
    conc_mismatch = 0
    for r in cm:
        comp = r["component"]
        if comp == "TDS" or _f(r, "mass_in_cup") is None:
            continue
        key = (_f(r, "exp"), _f(r, "rep"), comp)
        if key not in fit or fit[key][0] is None:
            continue
        c0, lam, r2 = fit[key]
        M = dict(BREW_RATIOS)[r["brew_ratio"]]
        recon = c0 * lam * (1.0 - math.exp(-M / lam))
        pub = _f(r, "mass_in_cup")
        rel = (recon - pub) / pub * 100.0
        rows.append({"exp": key[0], "rep": key[1], "component": comp,
                     "brew_ratio": r["brew_ratio"], "published_mg": pub,
                     "reconstructed_mg": recon, "rel_error_pct": rel})
        if abs(rel) > 0.01:
            deviations.append(rows[-1] | {"adj_r2": r2})
        if _f(r, "conc_in_cup") is not None and abs(pub / M - _f(r, "conc_in_cup")) > 1e-6 * max(
                1.0, abs(_f(r, "conc_in_cup"))):
            conc_mismatch += 1

    # cause of the deviations: duplicated published cells in the source table
    seen = {}
    dups = {}
    for r in cm:
        if r["component"] == "TDS" or _f(r, "mass_in_cup") is None:
            continue
        k = (r["component"], r["brew_ratio"], round(_f(r, "mass_in_cup"), 4))
        seen.setdefault(k, []).append((_f(r, "exp"), _f(r, "rep")))
    for k, v in seen.items():
        if len(v) > 1:
            dups["%s|%s|%.4f" % k] = [{"exp": e, "rep": p} for e, p in v]

    err = np.array([abs(r["rel_error_pct"]) for r in rows])
    abs_err = np.array([abs(r["reconstructed_mg"] - r["published_mg"]) for r in rows])
    dev_in_dup = sum(1 for d in deviations
                     if any((d["exp"], d["rep"]) in [(x["exp"], x["rep"]) for x in g]
                            for kk, g in dups.items()
                            if kk.startswith("%s|%s|" % (d["component"], d["brew_ratio"]))))
    return {
        "status": STATUS, "not_a_gate": NOT_GATE,
        "label": ["DERIVED_FROM_FITTED_KINETICS", "NOT_AN_INDEPENDENT_CUP_MEASUREMENT"],
        "reconstruction_formula": "mass_in_cup(M) = c0 * lambda * (1 - exp(-M/lambda))",
        "note": ("The directive described the construction as a measured first-fraction "
                 "contribution PLUS the integral of the fitted curve over the remainder. Tested "
                 "directly, that form leaves a constant absolute offset per cell. The published "
                 "values are reproduced by the PURE analytic integral from zero, with no measured "
                 "first-fraction term. The lineage conclusion is unchanged and in fact stronger: "
                 "no part of the cup target is an independent measurement."),
        "rows_reproduced": len(rows),
        "max_abs_error_mg": float(abs_err.max()),
        "max_rel_error_pct": float(err.max()),
        "mean_rel_error_pct": float(err.mean()),
        "median_rel_error_pct": float(np.median(err)),
        "rows_within_0p01pct": int((err <= 0.01).sum()),
        "conc_in_cup_equals_mass_over_M_mismatches": conc_mismatch,
        "deviations": deviations,
        "deviation_cause": {
            "explanation": ("every deviating row carries a published mass that is DUPLICATED "
                            "across replicates in the source table, i.e. a transcription "
                            "duplication in Table S3, not a different construction"),
            "duplicated_published_values": dups,
            "deviating_rows_inside_a_duplicate_group": dev_in_dup,
            "deviating_rows_total": len(deviations),
        },
        "consequence": ("The cumulative cup targets are a smoothed, fitted functional of the same "
                        "fraction campaign. They are not an independent observation operator, and "
                        "held-out error against them is not comparable with held-out error against "
                        "raw interval concentrations."),
    }


def smoothing_audit(shots):
    """How much of the low cumulative error is attributable to source smoothing and aggregation."""
    kp = list(csv.DictReader(KFIT.open(encoding="utf-8")))
    fit = {(_f(r, "exp"), _f(r, "rep"), r["component"]):
           (_f(r, "c0"), _f(r, "lambda_g")) for r in kp}
    out = {}
    for solute, _, src in SOLUTES:
        raw_res, cum_res, cum_vals = [], [], []
        for s in shots:
            key = (s["exp"], s["rep"], src)
            if key not in fit or fit[key][0] is None:
                continue
            c0, lam = fit[key]
            # raw: fitted single exponential against each measured interval average
            for w in s["windows"]:
                a, b = w["start_g"], w["end_g"]
                pred = c0 * lam * (math.exp(-a / lam) - math.exp(-b / lam)) / (b - a)
                raw_res.append((pred - w[solute]) / w[solute] * 100.0)
            # cumulative: the same curve integrated, against the published derived target
            row = []
            for br, M in BREW_RATIOS:
                pred = c0 * lam * (1.0 - math.exp(-M / lam)) / M
                obs = s["cup"]["%s|%s" % (src, br)]
                cum_res.append((pred - obs) / obs * 100.0)
                row.append(obs)
            cum_vals.append(row)
        cum_vals = np.array(cum_vals)
        corr = np.corrcoef(cum_vals.T) if len(cum_vals) > 2 else np.full((3, 3), np.nan)
        out[solute] = {
            "raw_fraction_residual_sd_pct": float(np.std(raw_res)),
            "derived_cumulative_residual_sd_pct": float(np.std(cum_res)),
            "variance_attenuation_ratio": float(np.var(raw_res) / max(np.var(cum_res), 1e-30)),
            "sd_attenuation_ratio": float(np.std(raw_res) / max(np.std(cum_res), 1e-30)),
            "correlation_among_three_cumulative_targets": [[float(x) for x in r] for r in corr],
            "why_correlated": ("all three brew ratios are generated by integrating ONE fitted "
                               "curve per replicate, so they share both the fit and its error and "
                               "are near-perfectly correlated by construction"),
        }
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Matched unit (reuses the audited Part B builder)
# ─────────────────────────────────────────────────────────────────────────────────────────────


def matched_shots(primary_only=True):
    from tools import paper_a_viability_operator as OP
    shots, exclusions = OP.build_matched_unit()
    if primary_only:
        shots = [s for s in shots if s["grind_level"] == DECLARED_GRIND_LEVEL]
    return shots, exclusions


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────────────────────


@functools.lru_cache(maxsize=4096)
def _base_params(solute, kappa, T_C, flow):
    """The production parameter block at unit inventory, for a measured flow and temperature."""
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.models.pannusch2024 import closures as pc

    sp = dict(ps._solute_params()[solute])
    sp["A1"] = sp["A1"] * kappa
    sp["A2"] = sp["A2"] * kappa
    nz = ps.NZ
    T = T_C + 273.15
    q = flow / 1000.0 / ps.RHO / ps.ACS
    grind = ps.GRIND_17
    psi, d_s2, d_s1 = grind["psi"], grind["d_s2"], ps.D1_FINE
    d32 = 6.0 / (psi * 6.0 / d_s1 + (1 - psi) * 6.0 / d_s2)
    h1 = float(pc.sherwood_h(T, q, sp["A1"], sp["B1"], sp["solute"], d32))
    h2 = float(pc.sherwood_h(T, q, sp["A2"], sp["B2"], sp["solute"], d32))
    K = float(pc.vant_hoff_K(T, sp["K_ref"], sp["gamma"]))
    alpha_s1 = psi * (1 - ps.ALPHA_L)
    alpha_s2 = (1 - psi) * (1 - ps.ALPHA_L)
    return dict(
        nz=nz, K=K, cs0=1.0, cl1=1.0, v_l=q / ps.ALPHA_L,
        D1z=ps.five_point_biased_upwind(nz, 1.0 / (nz - 1), q),
        m1=(6 * h1 * alpha_s1) / (ps.ALPHA_L * d_s1) * ps.TC,
        m2=(6 * h2 * alpha_s2) / (ps.ALPHA_L * d_s2) * ps.TC,
        f1=(6 * h1) / d_s1 * ps.TC, f2=(6 * h2) / (ps.PHI_V2 * d_s2) * ps.TC,
        dVol=q * (math.pi / 4 * ps.DBED ** 2) * ps.TC * 1e6,
        # grams of beverage per unit dimensionless time: tau = mass / tau_per_gram
        tau_per_gram=flow * ps.TC,
    )


def _rhs_ext(c, p, alpha_slow, rate_ratio):
    """Extended right-hand side, mirroring the production `_rhs` term for term.

    State `[c_l, c_s1b, c_s2b, (c_s1s, c_s2s,) m_cum]`. The slow subpopulation shares the transport
    structure exactly; it holds a fraction `alpha_slow` of the initial solute inventory — carried
    through the solid volume fractions in `m1`/`m2` — and its interphase-transfer coefficients are
    scaled by `rate_ratio`, so `kappa_slow = rate_ratio · kappa_base`. Total initial inventory is
    unchanged, which is what makes the extension mass-conserving rather than a new source of solute.

    `cl[0]` is zeroed before it is used ANYWHERE, exactly as the production RHS does — that is the
    Dirichlet inlet condition, and applying it only to the derivative row (rather than to every term
    that reads the liquid vector) is a 2.8 % error at the late fractions.
    """
    from puckworks.models.pannusch2024 import solver as ps

    nz = p["nz"]
    two = alpha_slow > 0.0
    n = (5 * nz + 1) if two else (3 * nz + 1)
    cl = c[0:nz].copy()
    cl[0] = 0.0
    cs1b, cs2b = c[nz:2 * nz], c[2 * nz:3 * nz]
    K, wb, ws, r = p["K"], 1.0 - alpha_slow, alpha_slow, rate_ratio
    cz = p["D1z"] @ cl
    ct = np.zeros(n)
    ct[0:nz] = (-p["v_l"] * ps.TC / ps.L * cz
                + wb * p["m1"] * (K * cs1b - cl)
                + wb * p["m2"] * (K * cs2b - cl))
    ct[nz:2 * nz] = -p["f1"] * (K * cs1b - cl)
    ct[2 * nz:3 * nz] = -p["f2"] * (K * cs2b - cl)
    if two:
        cs1s, cs2s = c[3 * nz:4 * nz], c[4 * nz:5 * nz]
        ct[0:nz] += ws * r * p["m1"] * (K * cs1s - cl) + ws * r * p["m2"] * (K * cs2s - cl)
        ct[3 * nz:4 * nz] = -r * p["f1"] * (K * cs1s - cl)
        ct[4 * nz:5 * nz] = -r * p["f2"] * (K * cs2s - cl)
    ct[n - 1] = cl[nz - 1] * p["dVol"]
    return ct


def build_operator_by_columns(p, alpha_slow=0.0, rate_ratio=1.0):
    """Reference build: read the operator column-by-column from `_rhs_ext`.

    The system is linear, so `A[:, j] = rhs(e_j) − rhs(0)`. This is the technique already used
    in-repo and it is the ground truth for `build_operator`, which is the same matrix assembled
    analytically. It costs `n` RHS evaluations, so it is used for verification, not in the fit loop.
    """
    nz = p["nz"]
    n = (5 * nz + 1) if alpha_slow > 0.0 else (3 * nz + 1)
    f0 = _rhs_ext(np.zeros(n), p, alpha_slow, rate_ratio)
    A = np.empty((n, n))
    e = np.zeros(n)
    for j in range(n):
        e[j] = 1.0
        A[:, j] = _rhs_ext(e, p, alpha_slow, rate_ratio) - f0
        e[j] = 0.0
    return A, _initial_state(p, n)


def _initial_state(p, n):
    nz = p["nz"]
    z0 = np.ones(n)
    z0[0] = 0.0
    z0[1:nz] = p["K"]
    z0[n - 1] = 0.0
    return z0


def build_operator(p, alpha_slow=0.0, rate_ratio=1.0):
    """Analytic assembly of the same operator, verified bit-identical to the column read.

    `_rhs` zeroes `cl[0]` before using the liquid vector ANYWHERE, so column 0 of the operator is
    identically zero — that is the Dirichlet inlet, and it is the one term that is easy to get wrong
    by hand. Everything else is a direct transcription of the production right-hand side.
    """
    nz = p["nz"]
    two = alpha_slow > 0.0
    n = (5 * nz + 1) if two else (3 * nz + 1)
    K, wb, ws, r = p["K"], 1.0 - alpha_slow, alpha_slow, rate_ratio
    A = np.zeros((n, n))
    I = np.eye(nz)
    from puckworks.models.pannusch2024 import solver as ps

    A[0:nz, 0:nz] = (-p["v_l"] * ps.TC / ps.L) * p["D1z"] - I * (wb * (p["m1"] + p["m2"]))
    A[0:nz, nz:2 * nz] = I * (wb * p["m1"] * K)
    A[0:nz, 2 * nz:3 * nz] = I * (wb * p["m2"] * K)
    A[nz:2 * nz, nz:2 * nz] = -I * (p["f1"] * K)
    A[nz:2 * nz, 0:nz] = I * p["f1"]
    A[2 * nz:3 * nz, 2 * nz:3 * nz] = -I * (p["f2"] * K)
    A[2 * nz:3 * nz, 0:nz] = I * p["f2"]
    if two:
        A[0:nz, 0:nz] -= I * (ws * r * (p["m1"] + p["m2"]))
        A[0:nz, 3 * nz:4 * nz] = I * (ws * r * p["m1"] * K)
        A[0:nz, 4 * nz:5 * nz] = I * (ws * r * p["m2"] * K)
        A[3 * nz:4 * nz, 3 * nz:4 * nz] = -I * (r * p["f1"] * K)
        A[3 * nz:4 * nz, 0:nz] = I * (r * p["f1"])
        A[4 * nz:5 * nz, 4 * nz:5 * nz] = -I * (r * p["f2"] * K)
        A[4 * nz:5 * nz, 0:nz] = I * (r * p["f2"])
    A[n - 1, :] = 0.0
    A[n - 1, nz - 1] = p["dVol"]
    A[:, 0] = 0.0                       # cl[0] is zeroed before use everywhere in `_rhs`
    return A, _initial_state(p, n)


#: Uniform time-grid resolution for the propagator. `expm_multiply` returns the exact solution at
#: every grid point, and cumulative extracted mass is smooth and monotone, so cubic interpolation at
#: the observation marks is accurate. Interval averages are DIFFERENCES of cumulative values,
#: which amplifies interpolation error, so the resolution is set from that: 128 points give
#: 1.9e-4 relative on the shortest late fraction, 256 give 1.2e-6. Verified against direct
#: `expm` at every mark.
PROPAGATOR_POINTS = 256


def simulate(p, masses, alpha_slow=0.0, rate_ratio=1.0):
    """Cumulative extracted solute mass at each cumulative beverage MASS, exact in time.

    Mass maps to dimensionless time through the FLOW, `tau = mass / (flow · TC)`, exactly as the
    production path does (`_matched_bounds` returns `t = mass / flow` in seconds, which
    `simulate_fractions` then divides by `TC`).

    It does NOT map through `dVol`. `dVol` is a VOLUME rate and the model carries `RHO = 980`, so
    volume in mL and mass in g differ by 2 %; routing the time mapping through `dVol` made every
    horizon 2 % short and moved the late fractions by up to 2.8 %.
    """
    from scipy.interpolate import CubicSpline
    from scipy.sparse import csc_matrix
    from scipy.sparse.linalg import expm_multiply

    A, z0 = build_operator(p, alpha_slow, rate_ratio)
    taus = np.asarray(masses, float) / p["tau_per_gram"]
    tmax = float(taus.max())
    if tmax <= 0:
        return np.zeros_like(taus)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        grid = np.linspace(0.0, tmax, PROPAGATOR_POINTS)
        Y = expm_multiply(csc_matrix(A), z0, start=0.0, stop=tmax,
                          num=PROPAGATOR_POINTS, endpoint=True)
    mcum = CubicSpline(grid, np.asarray(Y)[:, -1])(taus)
    return np.where(taus > 0, mcum, 0.0)


def observables(p, shot, alpha_slow=0.0, rate_ratio=1.0):
    """Interval-average fraction concentrations and cumulative cup concentrations."""
    marks = sorted({0.0} | {round(w["start_g"], 9) for w in shot["windows"]}
                   | {round(w["end_g"], 9) for w in shot["windows"]}
                   | {round(M, 9) for _, M in BREW_RATIOS})
    mcum = simulate(p, marks, alpha_slow, rate_ratio)
    idx = {round(m, 9): i for i, m in enumerate(marks)}
    frac = np.array([(mcum[idx[round(w["end_g"], 9)]] - mcum[idx[round(w["start_g"], 9)]])
                     / (w["end_g"] - w["start_g"]) for w in shot["windows"]])
    cup = {br: mcum[idx[round(M, 9)]] / M for br, M in BREW_RATIOS}
    return frac, cup, mcum


def src_exp_observables(c0, lam, shot):
    """The source single-exponential benchmark, evaluated as the same two operators."""
    frac = np.array([c0 * lam * (math.exp(-w["start_g"] / lam) - math.exp(-w["end_g"] / lam))
                     / (w["end_g"] - w["start_g"]) for w in shot["windows"]])
    cup = {br: c0 * lam * (1.0 - math.exp(-M / lam)) / M for br, M in BREW_RATIOS}
    return frac, cup


def biexp_observables(theta, shot):
    """Positive two-timescale empirical benchmark, form fixed before fitting.

        c(m) = c0 · [ (1−w)·exp(−m/λ₁) + w·exp(−m/λ₂) ],  0 ≤ w ≤ 1, λ₂ > λ₁ > 0

    Strictly positive and monotone non-increasing by construction; no per-fraction parameters.
    """
    c0, lam1, w, lam2 = theta
    def integ(a, b):
        return c0 * ((1 - w) * lam1 * (math.exp(-a / lam1) - math.exp(-b / lam1))
                     + w * lam2 * (math.exp(-a / lam2) - math.exp(-b / lam2)))
    frac = np.array([integ(wd["start_g"], wd["end_g"]) / (wd["end_g"] - wd["start_g"])
                     for wd in shot["windows"]])
    cup = {br: integ(0.0, M) / M for br, M in BREW_RATIOS}
    return frac, cup


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Prediction cache
# ─────────────────────────────────────────────────────────────────────────────────────────────


def build_prediction_cache(shots):
    """Predictions for BASE and every (alpha, ratio) of SLOW_TAIL, over the declared kappa grid.

    One pass; every later analysis (residuals, level policies, leave-one-experiment-out) is then
    pure arithmetic on this table.
    """
    table, done = {}, 0
    combos = [(0.0, 1.0)] + [(float(a), float(r)) for a in ALPHA_GRID for r in RATIO_GRID]
    total = len(shots) * len(SOLUTES) * len(KAPPA_GRID) * len(combos)
    for shot in shots:
        key0 = (shot["exp"], shot["rep"])
        for solute, _, _ in SOLUTES:
            for kappa in KAPPA_GRID:
                p = _base_params(solute, float(kappa), shot["decent_temp_C"],
                                 shot["scale_flow_ml_s"])
                for a, r in combos:
                    frac, cup, _ = observables(p, shot, a, r)
                    table[(key0, solute, float(kappa), a, r)] = (frac, cup)
                    done += 1
            print("    %s exp%g rep%g %-13s %d/%d" % ("predicted", key0[0], key0[1], solute,
                                                      done, total), flush=True)
    return table


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Level policies and residuals
# ─────────────────────────────────────────────────────────────────────────────────────────────


def level_mape(pred, obs):
    """Exact MAPE-minimising level: the weighted median of obs/pred with weights pred/obs."""
    pred, obs = np.asarray(pred, float), np.asarray(obs, float)
    r, w = obs / pred, pred / obs
    o = np.argsort(r)
    r, w = r[o], w[o]
    cw = np.cumsum(w)
    return float(r[min(int(np.searchsorted(cw, 0.5 * cw[-1])), len(r) - 1)])


def apply_level(pred, obs, policy, common=None):
    """`full_profile` | `first_fraction` | `common_per_solute`."""
    if policy == "full_profile":
        return level_mape(pred, obs)
    if policy == "first_fraction":
        return float(obs[0] / pred[0])
    if policy == "common_per_solute":
        return float(common)
    raise ValueError(policy)


def common_level(shots, solute, predict, policy_obs):
    """One level per solute across shots, profiled exactly on shot-balanced pooled ratios."""
    ratios, weights = [], []
    for s in shots:
        pred, obs = predict(s), policy_obs(s, solute)
        ratios.append(obs / pred)
        weights.append(np.full(len(pred), 1.0 / len(pred)) * (pred / obs))
    r, w = np.concatenate(ratios), np.concatenate(weights)
    o = np.argsort(r)
    r, w = r[o], w[o]
    cw = np.cumsum(w)
    return float(r[min(int(np.searchsorted(cw, 0.5 * cw[-1])), len(r) - 1)])


def observed_fractions(shot, solute):
    return np.array([w[solute] for w in shot["windows"]], float)


def residual_matrix(shots, solute, predict, policy="full_profile"):
    """Signed relative residuals (%) per shot x fraction, under one level policy."""
    common = None
    if policy == "common_per_solute":
        common = common_level(shots, solute, predict, observed_fractions)
    R = []
    for s in shots:
        pred, obs = predict(s), observed_fractions(s, solute)
        lvl = apply_level(pred, obs, policy, common)
        R.append((lvl * pred - obs) / obs * 100.0)
    return np.array(R)


def cluster_bootstrap(values_by_exp, b=BOOTSTRAP_B, seed=BOOTSTRAP_SEED):
    """Percentile interval for the mean, resampling EXPERIMENTS with replacement.

    Clustering is by experiment, not by fraction row: rows within a shot and shots within an
    experiment are not independent, and resampling rows would understate the interval.
    """
    rng = np.random.default_rng(seed)
    exps = sorted(values_by_exp)
    if len(exps) < 2:
        return {"mean": float(np.mean(np.concatenate(list(values_by_exp.values())))),
                "ci95": [None, None], "n_experiments": len(exps),
                "note": "fewer than two clusters; no interval"}
    pooled = np.concatenate([values_by_exp[e] for e in exps])
    means = np.empty(b)
    for i in range(b):
        pick = rng.choice(len(exps), size=len(exps), replace=True)
        means[i] = np.mean(np.concatenate([values_by_exp[exps[j]] for j in pick]))
    lo, hi = np.percentile(means, [2.5, 97.5])
    return {"mean": float(pooled.mean()), "ci95": [float(lo), float(hi)],
            "n_experiments": len(exps), "b": b, "seed": seed,
            "excludes_zero_negative": bool(hi < 0.0)}


def late_tail_robustness(shots, solute, predict, policy="full_profile"):
    """The declared robust late-tail criterion, computed per solute."""
    R = residual_matrix(shots, solute, predict, policy)
    fr = list(MEASURED_FRACTIONS)
    late_idx = [fr.index(f) for f in LATE_FRACTIONS]

    per_fraction = {}
    for j, f in enumerate(fr):
        by_exp = {}
        for s, row in zip(shots, R):
            by_exp.setdefault(s["exp"], []).append(row[j])
        by_exp = {k: np.array(v) for k, v in by_exp.items()}
        per_fraction["fraction_%d" % f] = {
            "mean_signed_pct": float(R[:, j].mean()),
            "median_signed_pct": float(np.median(R[:, j])),
            "mean_absolute_pct": float(np.abs(R[:, j]).mean()),
            "negative_shot_fraction": float((R[:, j] < 0).mean()),
            "cluster_bootstrap": cluster_bootstrap(by_exp),
        }

    late = R[:, late_idx]
    by_exp_late = {}
    for s, row in zip(shots, late):
        by_exp_late.setdefault(s["exp"], []).extend(row.tolist())
    by_exp_late = {k: np.array(v) for k, v in by_exp_late.items()}
    boot = cluster_bootstrap(by_exp_late)
    neg_shot = float(np.mean([(r < 0).any() for r in late]))
    mean_abs = float(np.abs(late).mean())
    crit = {
        "at_least_70pct_shots_negative_at_f7_or_f10": bool(neg_shot >= 0.70),
        "bootstrap_excludes_zero_negative": bool(boot.get("excludes_zero_negative", False)),
        "mean_absolute_late_residual_at_least_2pp": bool(mean_abs >= 2.0),
    }
    return {
        "level_policy": policy, "n_shots": len(shots),
        "per_fraction": per_fraction,
        "late_joint": {"mean_signed_pct": float(late.mean()),
                       "median_signed_pct": float(np.median(late)),
                       "mean_absolute_pct": mean_abs,
                       "shot_fraction_negative_at_f7_or_f10": neg_shot,
                       "cluster_bootstrap": boot},
        "criterion": crit,
        "robust": bool(all(crit.values())),
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Benchmarks
# ─────────────────────────────────────────────────────────────────────────────────────────────


def src_exp_fits():
    kp = list(csv.DictReader(KFIT.open(encoding="utf-8")))
    return {(_f(r, "exp"), _f(r, "rep"), r["component"]): (_f(r, "c0"), _f(r, "lambda_g"))
            for r in kp}


def fit_biexp(shots, solute, src, seed=0):
    """Fit the shared two-timescale shape; the per-shot level stays the exact MAPE profile.

    Shape parameters `(lam1, w, lam2)` are shared across shots within a solute — no per-shot and no
    per-fraction shape freedom. `c0` is absorbed into the profiled level.
    """
    from scipy.optimize import minimize

    obs = [observed_fractions(s, solute) for s in shots]

    def score(theta):
        lam1, logit_w, ratio = theta
        lam1 = abs(lam1) + 1e-6
        w = 1.0 / (1.0 + math.exp(-logit_w))
        lam2 = lam1 * (1.0 + abs(ratio))
        tot = []
        for s, o in zip(shots, obs):
            pred, _ = biexp_observables((1.0, lam1, w, lam2), s)
            if np.any(pred <= 0):
                return 1e6
            lvl = level_mape(pred, o)
            tot.append(np.mean(np.abs(lvl * pred - o) / o) * 100.0)
        return float(np.mean(tot))

    best, best_x = np.inf, None
    rng = np.random.default_rng(seed)
    for _ in range(12):
        x0 = np.array([rng.uniform(5.0, 30.0), rng.uniform(-2.0, 2.0), rng.uniform(0.2, 5.0)])
        res = minimize(score, x0, method="Nelder-Mead",
                       options={"maxiter": 800, "xatol": 1e-4, "fatol": 1e-6})
        if res.fun < best:
            best, best_x = float(res.fun), res.x
    lam1 = abs(best_x[0]) + 1e-6
    w = 1.0 / (1.0 + math.exp(-best_x[1]))
    lam2 = lam1 * (1.0 + abs(best_x[2]))
    _ = src
    return {"lam1": lam1, "w": w, "lam2": lam2, "train_mape": best}


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Model fitting and leave-one-experiment-out
# ─────────────────────────────────────────────────────────────────────────────────────────────


def predictor(table, kappa, alpha=0.0, ratio=1.0, solute=None):
    def f(shot):
        return np.asarray(table[((shot["exp"], shot["rep"]), solute, float(kappa),
                                 float(alpha), float(ratio))][0], float)
    return f


def fit_grid(shots, solute, table, slow=False):
    """Shot-balanced MAPE over the declared grid; shared parameters, per-shot exact level."""
    combos = ([(float(k), float(a), float(r)) for k in KAPPA_GRID
               for a in ALPHA_GRID for r in RATIO_GRID] if slow
              else [(float(k), 0.0, 1.0) for k in KAPPA_GRID])
    best, arg = np.inf, None
    for k, a, r in combos:
        pred = predictor(table, k, a, r, solute)
        sc = []
        for s in shots:
            pr, ob = pred(s), observed_fractions(s, solute)
            if np.any(pr <= 0):
                sc = None
                break
            sc.append(np.mean(np.abs(level_mape(pr, ob) * pr - ob) / ob) * 100.0)
        if sc is None:
            continue
        m = float(np.mean(sc))
        if m < best:
            best, arg = m, (k, a, r)
    return {"kappa": arg[0], "alpha_slow": arg[1], "rate_ratio": arg[2], "train_mape": best}


def score_heldout(shot, solute, pred_fn, cup_pred=None, src=None):
    """Anchor the level on fraction 1, then score fractions 2,3,5,7,10 and the derived cup targets."""
    pred, obs = pred_fn(shot), observed_fractions(shot, solute)
    if np.any(pred <= 0):
        return None
    lvl = float(obs[0] / pred[0])
    rest_p, rest_o = lvl * pred[1:], obs[1:]
    fr = list(MEASURED_FRACTIONS)
    late = [fr.index(f) for f in LATE_FRACTIONS]
    out = {
        "all_fraction_mape": float(np.mean(np.abs(rest_p - rest_o) / rest_o) * 100.0),
        "late_fraction_mape": float(np.mean(np.abs(lvl * pred[late] - obs[late])
                                            / obs[late]) * 100.0),
        "late_signed_pct": float(np.mean((lvl * pred[late] - obs[late]) / obs[late]) * 100.0),
        "positivity_ok": bool(np.all(pred > 0)),
    }
    if cup_pred is not None and src is not None:
        cp = cup_pred(shot)
        errs = [abs(lvl * cp[br] - shot["cup"]["%s|%s" % (src, br)])
                / shot["cup"]["%s|%s" % (src, br)] * 100.0 for br, _ in BREW_RATIOS]
        out["derived_cumulative_mape"] = float(np.mean(errs))
    return out


def loeo(shots, solute, table, src, model="BASE"):
    """Leave-one-experiment-out: fit shared parameters on training, predict held-out shape."""
    exps = sorted({s["exp"] for s in shots})
    folds, fails = [], 0
    for e in exps:
        train = [s for s in shots if s["exp"] != e]
        test = [s for s in shots if s["exp"] == e]
        if not train or not test:
            continue
        if model in ("BASE", "SLOW_TAIL"):
            fit = fit_grid(train, solute, table, slow=(model == "SLOW_TAIL"))
            pf = predictor(table, fit["kappa"], fit["alpha_slow"], fit["rate_ratio"], solute)
            cf = (lambda sh, f=fit: table[((sh["exp"], sh["rep"]), solute, float(f["kappa"]),
                                           float(f["alpha_slow"]), float(f["rate_ratio"]))][1])
            params = {k: fit[k] for k in ("kappa", "alpha_slow", "rate_ratio")}
        elif model == "BIEXP":
            fit = fit_biexp(train, solute, src)
            th = (1.0, fit["lam1"], fit["w"], fit["lam2"])
            pf = lambda sh, t=th: biexp_observables(t, sh)[0]
            cf = lambda sh, t=th: biexp_observables(t, sh)[1]
            params = {k: fit[k] for k in ("lam1", "w", "lam2")}
        elif model == "SRC_EXP":
            params = {}
            pf = None
        scores = []
        for sh in test:
            if model == "SRC_EXP":
                key = (sh["exp"], sh["rep"], src)
                if key not in FITS or FITS[key][0] is None:
                    fails += 1
                    continue
                c0, lam = FITS[key]
                pf = lambda s2, c=c0, l=lam: src_exp_observables(c, l, s2)[0]
                cf = lambda s2, c=c0, l=lam: src_exp_observables(c, l, s2)[1]
            sc = score_heldout(sh, solute, pf, cf, src)
            if sc is None:
                fails += 1
            else:
                scores.append(sc)
        if scores:
            folds.append({"held_out_exp": e, "params": params, "n_shots": len(scores),
                          **{k: float(np.mean([x[k] for x in scores]))
                             for k in ("all_fraction_mape", "late_fraction_mape",
                                       "late_signed_pct")},
                          "derived_cumulative_mape": float(np.mean(
                              [x["derived_cumulative_mape"] for x in scores
                               if "derived_cumulative_mape" in x])) if scores else None})
    agg = {k: float(np.mean([f[k] for f in folds])) for k in
           ("all_fraction_mape", "late_fraction_mape", "late_signed_pct",
            "derived_cumulative_mape")} if folds else {}
    return {"model": model, "folds": folds, "failed_fits": fails, "n_folds": len(folds), **agg,
            "parameter_stability": {k: [f["params"].get(k) for f in folds]
                                    for k in (folds[0]["params"] if folds else {})}}


FITS = src_exp_fits()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--lineage", action="store_true")
    ap.add_argument("--predict", action="store_true")
    ap.add_argument("--analyse", action="store_true")
    args = ap.parse_args(argv)

    shots, exclusions = matched_shots()
    print("primary GL %.1f set: %d shots, %d experiments (%d excluded overall)"
          % (DECLARED_GRIND_LEVEL, len(shots), len({s["exp"] for s in shots}), len(exclusions)))

    if args.lineage:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        rec = lineage_audit()
        rec["smoothing_and_aggregation"] = smoothing_audit(shots)
        rec["hashes"] = {
            "cup_masses_sha256": hashlib.sha256(CUPS.read_bytes()).hexdigest(),
            "kinetics_fit_params_reps_sha256": hashlib.sha256(KFIT.read_bytes()).hexdigest(),
            "raw_fractions_sha256": hashlib.sha256(FRACTIONS.read_bytes()).hexdigest(),
            "producer_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        }
        rec["environment"] = {"python": platform.python_version(), "numpy": np.__version__,
                              "scipy": __import__("scipy").__version__}
        (OUT_DIR / "PAPER_A_CUP_TARGET_LINEAGE_AUDIT_V1.json").write_text(
            json.dumps(rec, indent=1) + "\n", encoding="utf-8")
        print("  reproduced %d/%d rows within 0.01%%; max rel %.4f%%; deviations %d (all inside "
              "duplicated source cells: %d)"
              % (rec["rows_within_0p01pct"], rec["rows_reproduced"], rec["max_rel_error_pct"],
                 len(rec["deviations"]), rec["deviation_cause"]["deviating_rows_inside_a_duplicate_group"]))
        print("  wrote PAPER_A_CUP_TARGET_LINEAGE_AUDIT_V1.json")

    if args.predict:
        table = build_prediction_cache(shots)
        with open(CACHE, "wb") as fh:
            pickle.dump({"table": table, "shots": shots, "exclusions": exclusions}, fh)
        print("cached %d predictions" % len(table))
        return 0

    if args.analyse:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        with open(CACHE, "rb") as fh:
            table = pickle.load(fh)["table"]
        rob = robustness_report(shots, table)
        (OUT_DIR / "PAPER_A_TEMPORAL_RESIDUAL_ROBUSTNESS_V1.json").write_text(
            json.dumps(rob, indent=1) + "\n", encoding="utf-8")
        print("wrote PAPER_A_TEMPORAL_RESIDUAL_ROBUSTNESS_V1.json")
        comp = comparison_report(shots, table)
        (OUT_DIR / "PAPER_A_TEMPORAL_MODEL_COMPARISON_V1.json").write_text(
            json.dumps(comp, indent=1) + "\n", encoding="utf-8")
        print("wrote PAPER_A_TEMPORAL_MODEL_COMPARISON_V1.json")
        (OUT_DIR / "PAPER_A_TEMPORAL_MATCHED_DATA_MANIFEST_V1.json").write_text(
            json.dumps(matched_manifest(shots, exclusions), indent=1) + "\n", encoding="utf-8")
        print("wrote PAPER_A_TEMPORAL_MATCHED_DATA_MANIFEST_V1.json")
    return 0


def matched_manifest(shots, exclusions):
    return {
        "status": STATUS, "not_a_gate": NOT_GATE,
        "primary_set": "GL %.1f only; declared grain parameters match the actual grind"
                       % DECLARED_GRIND_LEVEL,
        "n_shots": len(shots), "experiments": sorted({s["exp"] for s in shots}),
        "n_excluded_overall": len(exclusions), "exclusions": exclusions,
        "measured_fractions": list(MEASURED_FRACTIONS),
        "late_fractions": list(LATE_FRACTIONS),
        "sources": {"raw_fractions.csv": hashlib.sha256(FRACTIONS.read_bytes()).hexdigest(),
                    "cup_masses.csv": hashlib.sha256(CUPS.read_bytes()).hexdigest(),
                    "kinetics_fit_params_reps.csv": hashlib.sha256(KFIT.read_bytes()).hexdigest()},
        "shots": [{"exp": s["exp"], "rep": s["rep"], "grind_level": s["grind_level"],
                   "scale_flow_ml_s": s["scale_flow_ml_s"], "decent_temp_C": s["decent_temp_C"],
                   "windows_g": [[w["fraction"], w["start_g"], w["end_g"]] for w in s["windows"]]}
                  for s in shots],
    }


def robustness_report(shots, table):
    """Phase 2: shot-level residuals and the robust late-tail criterion, under three level policies."""
    out = {"status": STATUS, "not_a_gate": NOT_GATE,
           "n_shots": len(shots), "experiments": sorted({s["exp"] for s in shots}),
           "bootstrap": {"clustered_by": "experiment", "B": BOOTSTRAP_B, "seed": BOOTSTRAP_SEED,
                         "note": "exploratory decision thresholds, not inferential confidence limits"},
           "criterion": {"negative_shot_fraction_at_f7_or_f10": 0.70,
                         "bootstrap_excludes_zero_negative": True,
                         "mean_absolute_late_residual_pp": 2.0,
                         "survives_when_met_for_at_least": 2},
           "solutes": {}}
    for solute, _, _ in SOLUTES:
        fit = fit_grid(shots, solute, table, slow=False)
        pred = predictor(table, fit["kappa"], 0.0, 1.0, solute)
        by_policy = {}
        for policy in ("full_profile", "first_fraction", "common_per_solute"):
            by_policy[policy] = late_tail_robustness(shots, solute, pred, policy)
        out["solutes"][solute] = {"base_fit": fit, "by_level_policy": by_policy,
                                  "robust_under_all_policies":
                                      bool(all(v["robust"] for v in by_policy.values()))}
        print("  %-13s BASE kappa=%.3g  robust: %s" % (
            solute, fit["kappa"],
            {k: v["robust"] for k, v in by_policy.items()}), flush=True)
    n = sum(1 for v in out["solutes"].values()
            if v["by_level_policy"]["full_profile"]["robust"])
    out["n_solutes_robust_full_profile"] = n
    out["n_solutes_robust_all_policies"] = sum(
        1 for v in out["solutes"].values() if v["robust_under_all_policies"])
    out["late_tail_lead_survives"] = bool(n >= 2)
    return out


def comparison_report(shots, table):
    """Benchmarks and the one mechanistic extension, by leave-one-experiment-out."""
    out = {"status": STATUS, "not_a_gate": NOT_GATE,
           "models": {"BASE": "current two-grain mechanistic solver",
                      "SLOW_TAIL": "BASE + one slow-accessible inventory subpopulation",
                      "BIEXP": "positive two-timescale empirical benchmark, shape shared per solute",
                      "SRC_EXP": "source single-exponential kinetics (lineage baseline)"},
           "principal_score": "held-out RAW fraction error; the derived cumulative metric is "
                              "secondary and is NOT used for model selection",
           "solutes": {}}
    for solute, _, src in SOLUTES:
        res = {}
        for model in ("SRC_EXP", "BASE", "BIEXP", "SLOW_TAIL"):
            res[model] = loeo(shots, solute, table, src, model)
            print("  %-13s %-10s all=%.3f late=%.3f signed=%+.3f cum=%.3f" % (
                solute, model, res[model].get("all_fraction_mape", float("nan")),
                res[model].get("late_fraction_mape", float("nan")),
                res[model].get("late_signed_pct", float("nan")),
                res[model].get("derived_cumulative_mape", float("nan"))), flush=True)
        b, sl = res["BASE"], res["SLOW_TAIL"]
        rel = (b["late_fraction_mape"] - sl["late_fraction_mape"]) / b["late_fraction_mape"] * 100.0
        absd = b["late_fraction_mape"] - sl["late_fraction_mape"]
        alphas = sl["parameter_stability"].get("alpha_slow", [])
        ratios = sl["parameter_stability"].get("rate_ratio", [])
        pinned = sum(1 for a in alphas if a in (float(ALPHA_GRID[0]), float(ALPHA_GRID[-1])))
        res["improvement_rule"] = {
            "late_mape_relative_reduction_pct": rel,
            "late_mape_absolute_reduction_pp": absd,
            "meets_30pct_relative": bool(rel >= 30.0),
            "meets_2pp_absolute": bool(absd >= 2.0),
            "all_fraction_improves": bool(sl["all_fraction_mape"] < b["all_fraction_mape"]),
            "derived_cumulative_worsens_by_pp":
                sl["derived_cumulative_mape"] - b["derived_cumulative_mape"],
            "cumulative_within_0p5pp": bool(
                sl["derived_cumulative_mape"] - b["derived_cumulative_mape"] <= 0.5),
            "alpha_slow_boundary_pinned_folds": pinned,
            "alpha_slow_by_fold": alphas, "rate_ratio_by_fold": ratios,
            "boundary_pinned_in_most_folds": bool(pinned > len(alphas) / 2 if alphas else True),
        }
        out["solutes"][solute] = res
    return out





if __name__ == "__main__":
    raise SystemExit(main())
