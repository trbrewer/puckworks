"""screen_i024_common_state.py — Insight Foundry cheap screen for candidate I-024.

    CHEAP_SCIENTIFIC_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Question (generated, verbatim from the candidate):

    Under one shared hydraulic and transport state, do the per-species residuals show
    structure that a single kinetic story cannot absorb?

CORRECTED 2026-08-04. The first version made two unsupported claims and this module removes
both:

  1. "C3 is scale-free in the assumed RSD." IT IS NOT. Changing the bioactive RSD changes the
     weight of the three bioactives RELATIVE to total solids, whose per-condition RSD is
     measured and fixed. That reweighting REFITS the shared model, and the selected shared rate
     is observed to CHANGE across the band — at discrete breakpoints, since the selection is an
     argmin over a finite grid, not a continuous optimum. (The specific rates depend on the grid
     the run ends with, so they are reported in `result.json` rather than quoted here.) A
     uniform rescale of already-computed z values (what the old test did) is not that
     perturbation, and asserting scale-freeness from it was vacuous.
  2. "The verdict is invariant across the band." That was inferred from TWO endpoints. Two
     points cannot establish a property of an interval when the model is refitted inside it.

Both are replaced by an EXACT finite-grid argument, which the structure of the problem happens
to support (see `sweep`):

  * write x = (100/RSD)^2. Each species' training SSE at a fixed rate is EXACTLY linear in x
    (bioactives: x * a_s; total solids: constant b), because the fitted LEVEL is x-independent
    -- the x factor cancels in the weighted-least-squares ratio.
  * the shared rate is therefore argmin over the grid of a family of STRAIGHT LINES in x. Its
    selection changes only at the finitely many breakpoints where the lower envelope switches.
  * the independent per-species rates do NOT depend on x at all (a common factor cannot move an
    argmin), so they are constant across the whole band.
  * on any interval where the selection is fixed, Z^2 = (x*D + E)/N, so C1 is monotone in x and
    C3 (a ratio of two such) is a Moebius function of x and therefore also monotone -- their
    extrema are at the interval endpoints. C2's between-species spread is the square root of a
    QUADRATIC in u = sqrt(x), so its extremum can be interior and the vertex is evaluated too.

Evaluating both band endpoints, both sides of every breakpoint, and each interval's C2 vertex
therefore bounds every criterion EXACTLY over the continuous band -- not merely at sampled
points.

RATE-DOMAIN ROBUSTNESS. A decisive optimum sitting on the rate-grid boundary is a censored
answer, not an answer. The grid is expanded in that direction and everything refitted until the
decisive optima are interior or C3 converges within a predeclared tolerance (see
`grid_robustness`).

EVIDENCE UNIT: the angeloni2023 campaign ONLY.

Run:  python -m puckworks.analysis.screen_i024_common_state
"""
from __future__ import annotations

import json
import pathlib

import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CANDIDATE_ID = "I-024"
SPECIES = ("caffeine", "trigonelline", "5CQA", "tds")
BIOACTIVES = ("caffeine", "trigonelline", "5CQA")
VARIETIES = ("Arabica", "Robusta")

SPECIES_COLUMN = {"caffeine": ("CF", 1.0, "g/L"), "trigonelline": ("TR", 1.0, "g/L"),
                  "5CQA": ("5CQA", 1.0, "g/L"), "tds": ("TS", 0.1, "g/100 mL")}

EXCLUDED_EVIDENCE = {
    "maille2024.phi_closure / maille2024.two_regime":
        "batch fits on a different campaign; scoring them would mix campaigns and the "
        "candidate's own INCONCLUSIVE clause is about exactly that confound",
    "ellero2019/fig4_caffeine_content":
        "digitised SIMULATION output, not measurement — it cannot carry a residual",
    "khamitova2020/tamping":
        "a different rig and design (tamping force); reference strength only",
    "pannusch2024.solver / pannusch2024.closures as EVIDENCE":
        "used here as the MODEL, never as evidence. Its own fit target (schmieder kinetics) is "
        "post-fit and is not scored",
    "angeloni2023/lipids":
        "not a species the model produces; never scored",
}

# ------------------------------------------------------------------------------------------
# PREDECLARED — unchanged by the correction
# ------------------------------------------------------------------------------------------
TRAIN_P_BAR = (6.0, 12.0)
HELD_OUT_P_BAR = (9.0,)
SPLIT_RATIONALE = ("Held out the INTERIOR pressure (9 bar), training on 6 and 12 bar, at every "
                   "temperature and in both varieties. Interpolation rather than extrapolation, "
                   "and 9 bar is the reference espresso condition. Predeclared before any fit.")

#: The rate grid the screen STARTS from. It is expanded by `grid_robustness` whenever a decisive
#: optimum lands on a boundary — a censored optimum is not an answer.
BASE_RATE_GRID = tuple(float(v) for v in np.geomspace(0.15, 6.5, 15))

#: Predeclared expansion policy.
GRID_EXPANSION_FACTOR = 4.0        # multiply the offending bound by this each round
GRID_EXPANSION_POINTS = 5          # new log-spaced points added per round
GRID_MAX_ROUNDS = 4
GRID_C3_TOLERANCE = 0.01           # |ratio| change between rounds that counts as converged

BIOACTIVE_RSD_BAND_PCT = (0.3, 19.7)
BIOACTIVE_RSD_BAND_SOURCE = ("angeloni2023/bioactives MANIFEST uncertainty cell, verbatim: "
                             "'%RSD 0.3-19.7 (in card, not per-cell)'")
TDS_RSD_SOURCE = "angeloni2023/total_solids per-condition RSD_pct column (measured)"

C1_Z_THRESHOLD = 1.0
C2_SPREAD_THRESHOLD = 1.0
C3_REDUCTION_FACTOR = 0.7
CRITERION_STATEMENT = (
    "SURVIVE iff C1 and C2 and C3, all in units of retained measurement uncertainty. "
    "C1: RMS standardised held-out residual under the shared state > %.1f. "
    "C2: SD across species of the per-species mean standardised held-out residual > %.1f "
    "(species-specific rather than a shared model-form problem). "
    "C3: RMS standardised held-out residual under independent per-species fits "
    "<= %.2f x the shared-state value. Thresholds predeclared before any fit was computed and "
    "unchanged by the 2026-08-04 correction."
    % (C1_Z_THRESHOLD, C2_SPREAD_THRESHOLD, C3_REDUCTION_FACTOR))


# ------------------------------------------------------------------------------------------
# Data
# ------------------------------------------------------------------------------------------
def conditions():
    from puckworks import data as d
    bio = d.angeloni_bioactives()
    ts = {(r["variety"], r["T_degC"], r["p_bar"]): r for r in d.angeloni_total_solids()}
    out = []
    for r in sorted((x for x in bio
                     if x["granulometry"] == "O" and x["on_grid"] == "True"),
                    key=lambda x: (x["variety"], x["T_degC"], x["p_bar"])):
        key = (r["variety"], r["T_degC"], r["p_bar"])
        meas = {s: float(r[SPECIES_COLUMN[s][0]]) for s in BIOACTIVES}
        meas["tds"] = float(ts[key]["TS_g_100mL"])
        out.append(dict(variety=r["variety"], T_degC=r["T_degC"], p_bar=r["p_bar"],
                        held_out=r["p_bar"] in HELD_OUT_P_BAR, measured=meas,
                        tds_rsd_pct=float(ts[key]["RSD_pct"])))
    return out


class UnitPredictions:
    """Cache of unit-level (c_s0 = 1) predictions, keyed by rate value.

    The solver is EXACTLY linear in c_s0 (verified to ~1e-6), so a level never needs a re-solve
    and a grid expansion only costs the rates it actually adds.
    """

    def __init__(self, conds):
        self.conds = conds
        self._rows = {}
        self.n_solves = 0

    def row(self, rate):
        key = round(float(rate), 10)
        if key in self._rows:
            return self._rows[key]
        from puckworks.models.pannusch2024 import solver as ps
        from puckworks.validation.slow import angeloni_bracket as AB
        params = ps._solute_params()
        row = {}
        for c in self.conds:
            flow = AB._flow_darcy(c["p_bar"], c["T_degC"])
            bounds = AB._matched_bounds(flow)
            for s in SPECIES:
                sp = dict(params[s])
                sp["A1"] = sp["A1"] * key
                sp["A2"] = sp["A2"] * key
                sp["c_s0"] = 1.0
                row[(c["variety"], c["T_degC"], c["p_bar"], s)] = float(
                    ps.simulate_fractions(c["T_degC"], flow, bounds, sp, cl1=1.0)[0]
                ) * SPECIES_COLUMN[s][1]
                self.n_solves += 1
        self._rows[key] = row
        return row


# ------------------------------------------------------------------------------------------
# The x-decomposition — this is what makes the exact argument possible
# ------------------------------------------------------------------------------------------
def rsd_to_x(rsd_pct):
    """x = (100 / RSD)^2 — the inverse-variance weight factor carried by every bioactive."""
    return (100.0 / float(rsd_pct)) ** 2


def x_to_rsd(x):
    return 100.0 / float(np.sqrt(x))


def _level(row, conds, variety, species, train_only=True):
    """Weighted-least-squares level. INDEPENDENT of the bioactive RSD, by cancellation.

    For a bioactive every weight carries the same factor x, so it cancels in num/den. For total
    solids the weights are the measured per-condition RSDs and carry no x at all.
    """
    num = den = 0.0
    for c in conds:
        if c["variety"] != variety or (train_only and c["held_out"]):
            continue
        f = row[(variety, c["T_degC"], c["p_bar"], species)]
        m = c["measured"][species]
        w = 1.0 / (m * (c["tds_rsd_pct"] if species == "tds" else 1.0) / 100.0) ** 2 \
            if species == "tds" else 1.0 / m ** 2
        num += w * f * m
        den += w * f * f
    return num / den if den > 0 else float("nan")


def coefficients(pred, conds, rates):
    """Per (variety, rate): the fitted levels, and the training-SSE decomposition in x.

    Returns for each variety and rate index:
        levels[s]      the WLS level (x-independent)
        a[s]           bioactive training coefficient: SSE_s = x * a[s]
        b              total-solids training SSE (x-independent)
        A = sum_bio a  the shared model's x-slope
    """
    out = {}
    for v in VARIETIES:
        per_rate = []
        for rate in rates:
            row = pred.row(rate)
            levels, a, b = {}, {}, 0.0
            for s in SPECIES:
                L = _level(row, conds, v, s)
                levels[s] = L
                acc = 0.0
                for c in conds:
                    if c["variety"] != v or c["held_out"]:
                        continue
                    f = row[(v, c["T_degC"], c["p_bar"], s)]
                    m = c["measured"][s]
                    r2 = (L * f - m) ** 2 / m ** 2
                    if s == "tds":
                        acc += r2 / (c["tds_rsd_pct"] / 100.0) ** 2
                    else:
                        acc += r2
                if s == "tds":
                    b = acc
                else:
                    a[s] = acc
            per_rate.append(dict(rate=float(rate), levels=levels, a=a, b=b,
                                 A=float(sum(a.values()))))
        out[v] = per_rate
    return out


def lower_envelope_breakpoints(coefs, x_lo, x_hi):
    """Exact breakpoints of argmin_ri [ x*A(ri) + B(ri) ] on [x_lo, x_hi], per variety.

    The objective is a family of straight lines in x, so the selection is piecewise constant and
    changes only where the lower envelope switches. Returns the sorted interior breakpoints.
    """
    out = {}
    for v, per_rate in coefs.items():
        A = np.array([p["A"] for p in per_rate], float)
        B = np.array([p["b"] for p in per_rate], float)

        def argmin_at(x):
            return int(np.argmin(x * A + B))

        # scan candidate crossings between every pair, keep those where the envelope changes
        xs = set()
        for i in range(len(A)):
            for j in range(i + 1, len(A)):
                if A[i] == A[j]:
                    continue
                xc = (B[j] - B[i]) / (A[i] - A[j])
                if x_lo < xc < x_hi:
                    xs.add(float(xc))
        bps = []
        for xc in sorted(xs):
            lo = argmin_at(xc * (1 - 1e-9))
            hi = argmin_at(xc * (1 + 1e-9))
            if lo != hi:
                bps.append(dict(x=xc, rsd_pct=x_to_rsd(xc), rate_index_below=lo,
                                rate_index_above=hi,
                                rate_below=per_rate[lo]["rate"],
                                rate_above=per_rate[hi]["rate"]))
        out[v] = bps
    return out


def independent_selection(coefs):
    """argmin per (variety, species). Provably x-INDEPENDENT — a common factor cannot move it."""
    out = {}
    for v, per_rate in coefs.items():
        sel = {}
        for s in SPECIES:
            vals = [(p["a"][s] if s != "tds" else p["b"]) for p in per_rate]
            i = int(np.argmin(vals))
            sel[s] = dict(rate_index=i, rate=per_rate[i]["rate"],
                          at_grid_edge=bool(i in (0, len(per_rate) - 1)))
        out[v] = sel
    return out


# ------------------------------------------------------------------------------------------
# Held-out residual decomposition, and the criteria as functions of x
# ------------------------------------------------------------------------------------------
def residual_parts(pred, conds, coefs, shared_idx, indep_sel, rates):
    """Per held-out point: d (relative residual, bioactive) or e (standardised, tds).

    For a bioactive, z = d * sqrt(x). For total solids, z = e, fixed. Returned for both models.
    """
    held = [c for c in conds if c["held_out"]]
    parts = []
    for c in held:
        v = c["variety"]
        for s in SPECIES:
            m = c["measured"][s]
            ri_s = shared_idx[v]
            ri_i = indep_sel[v][s]["rate_index"]
            fs = pred.row(rates[ri_s])[(v, c["T_degC"], c["p_bar"], s)]
            fi = pred.row(rates[ri_i])[(v, c["T_degC"], c["p_bar"], s)]
            Ls = coefs[v][ri_s]["levels"][s]
            Li = coefs[v][ri_i]["levels"][s]
            rel_s = (Ls * fs - m) / m
            rel_i = (Li * fi - m) / m
            if s == "tds":
                k = 100.0 / c["tds_rsd_pct"]
                parts.append(dict(variety=v, T_degC=c["T_degC"], p_bar=c["p_bar"], species=s,
                                  scales_with_x=False,
                                  z_shared_fixed=rel_s * k, z_independent_fixed=rel_i * k,
                                  d_shared=0.0, d_independent=0.0,
                                  measured=m, pred_shared=Ls * fs, pred_independent=Li * fi))
            else:
                parts.append(dict(variety=v, T_degC=c["T_degC"], p_bar=c["p_bar"], species=s,
                                  scales_with_x=True,
                                  z_shared_fixed=0.0, z_independent_fixed=0.0,
                                  d_shared=rel_s, d_independent=rel_i,
                                  measured=m, pred_shared=Ls * fs, pred_independent=Li * fi))
    return parts


def criteria_at(parts, x):
    """C1, C2, C3 at one x, from the residual decomposition. Exact, no refit needed."""
    u = float(np.sqrt(x))
    zs, zi, by_sp = [], [], {s: [] for s in SPECIES}
    for p in parts:
        a = p["d_shared"] * u if p["scales_with_x"] else p["z_shared_fixed"]
        b = p["d_independent"] * u if p["scales_with_x"] else p["z_independent_fixed"]
        zs.append(a)
        zi.append(b)
        by_sp[p["species"]].append(a)
    Zs = float(np.sqrt(np.mean(np.square(zs))))
    Zi = float(np.sqrt(np.mean(np.square(zi))))
    means = [float(np.mean(by_sp[s])) for s in SPECIES]
    spread = float(np.std(means, ddof=1))
    ratio = Zi / Zs if Zs > 0 else float("inf")
    c1 = bool(Zs > C1_Z_THRESHOLD)
    c2 = bool(spread > C2_SPREAD_THRESHOLD)
    c3 = bool(ratio <= C3_REDUCTION_FACTOR)
    return dict(x=x, rsd_pct=x_to_rsd(x), Z_shared=Zs, Z_independent=Zi, reduction_ratio=ratio,
                per_species_mean_z_shared=dict(zip(SPECIES, means)),
                between_species_spread=spread,
                C1_exceeds_noise=c1, C2_species_specific=c2, C3_reduced_by_species_fits=c3,
                survive=bool(c1 and c2 and c3))


def c2_vertex_x(parts, x_lo, x_hi):
    """The interior extremum of the between-species spread, if any.

    Per-species mean z is  u * mbar_s  for a bioactive and a constant for total solids, so the
    spread SQUARED is a quadratic in u = sqrt(x) and its vertex may be interior. C1 and C3 are
    monotone on a fixed selection, so this is the only interior extremum that can exist.
    """
    mb, const = {}, {}
    for s in SPECIES:
        vals = [p for p in parts if p["species"] == s]
        if vals[0]["scales_with_x"]:
            mb[s] = float(np.mean([p["d_shared"] for p in vals]))
        else:
            const[s] = float(np.mean([p["z_shared_fixed"] for p in vals]))
    n = len(SPECIES)
    M = sum(mb.values())
    C = sum(const.values())
    alpha, beta = [], []
    for s in SPECIES:
        if s in mb:
            alpha.append(mb[s] - M / n)
            beta.append(-C / n)
        else:
            alpha.append(-M / n)
            beta.append(const[s] - C / n)
    sa = float(np.dot(alpha, alpha))
    sab = float(np.dot(alpha, beta))
    if sa <= 0:
        return None
    u_star = -sab / sa
    if u_star <= 0:
        return None
    x_star = u_star ** 2
    return float(x_star) if x_lo < x_star < x_hi else None


# ------------------------------------------------------------------------------------------
# The exact sweep
# ------------------------------------------------------------------------------------------
def sweep(pred, conds, rates):
    """Exact evaluation of C1/C2/C3 over the whole declared RSD band.

    Evaluates both band endpoints, BOTH SIDES of every shared-rate breakpoint, and each fixed-
    selection interval's C2 vertex. Because C1 and C3 are monotone on a fixed selection and C2's
    only interior extremum is that vertex, these points bound every criterion exactly.
    """
    x_hi = rsd_to_x(BIOACTIVE_RSD_BAND_PCT[0])      # 0.3 % -> large x (most demanding)
    x_lo = rsd_to_x(BIOACTIVE_RSD_BAND_PCT[1])      # 19.7 % -> small x
    coefs = coefficients(pred, conds, rates)
    bps = lower_envelope_breakpoints(coefs, x_lo, x_hi)
    indep = independent_selection(coefs)

    xs = sorted({x_lo, x_hi} | {b["x"] for v in bps for b in bps[v]})
    # build the fixed-selection intervals
    intervals = []
    for lo, hi in zip(xs[:-1], xs[1:]):
        mid = float(np.sqrt(lo * hi))
        sel = {}
        for v in VARIETIES:
            A = np.array([p["A"] for p in coefs[v]], float)
            B = np.array([p["b"] for p in coefs[v]], float)
            sel[v] = int(np.argmin(mid * A + B))
        parts = residual_parts(pred, conds, coefs, sel, indep, rates)
        pts = [lo, hi]
        vx = c2_vertex_x(parts, lo, hi)
        if vx is not None:
            pts.append(vx)
        evals = [criteria_at(parts, x) for x in sorted(pts)]
        intervals.append(dict(
            x_lo=lo, x_hi=hi, rsd_hi_pct=x_to_rsd(lo), rsd_lo_pct=x_to_rsd(hi),
            shared_rate_index={v: sel[v] for v in VARIETIES},
            shared_rate={v: coefs[v][sel[v]]["rate"] for v in VARIETIES},
            shared_rate_at_grid_edge={v: bool(sel[v] in (0, len(rates) - 1))
                                      for v in VARIETIES},
            c2_vertex_x=vx, evaluations=evals,
            ratio_min=min(e["reduction_ratio"] for e in evals),
            ratio_max=max(e["reduction_ratio"] for e in evals),
            any_survive=any(e["survive"] for e in evals),
            all_survive=all(e["survive"] for e in evals)))
    return dict(coefficients_summary={v: [dict(rate=p["rate"], A=p["A"], b=p["b"])
                                          for p in coefs[v]] for v in VARIETIES},
                breakpoints=bps, independent_selection=indep, intervals=intervals,
                x_range=[x_lo, x_hi], rsd_range_pct=list(BIOACTIVE_RSD_BAND_PCT),
                n_evaluated_points=sum(len(i["evaluations"]) for i in intervals),
                coefs=coefs, indep=indep)


def _decisive_edge_flags(sw, rates):
    """Which decisive optima sit on a rate-grid boundary (shared per interval + independent)."""
    edges = []
    for iv in sw["intervals"]:
        for v in VARIETIES:
            if iv["shared_rate_at_grid_edge"][v]:
                edges.append(dict(kind="shared", variety=v, rate=iv["shared_rate"][v],
                                  rate_index=iv["shared_rate_index"][v]))
    for v, sel in sw["indep"].items():
        for s, d in sel.items():
            if d["at_grid_edge"]:
                edges.append(dict(kind="independent", variety=v, species=s, rate=d["rate"],
                                  rate_index=d["rate_index"]))
    upper = [e for e in edges if e["rate_index"] == len(rates) - 1]
    lower = [e for e in edges if e["rate_index"] == 0]
    return dict(edges=edges, n_edges=len(edges), hits_upper=bool(upper), hits_lower=bool(lower))


def grid_robustness(pred, conds):
    """Expand the rate grid until decisive optima are interior or C3 converges.

    A decisive optimum on a grid boundary is a censored answer. Predeclared policy: multiply the
    offending bound by GRID_EXPANSION_FACTOR, add GRID_EXPANSION_POINTS log-spaced points,
    refit everything, and stop when no decisive optimum is on a boundary, or when the worst-case
    C3 ratio moves by less than GRID_C3_TOLERANCE between rounds, or after GRID_MAX_ROUNDS.
    """
    rates = list(BASE_RATE_GRID)
    rounds = []
    prev_metric = None
    sw = None
    for k in range(GRID_MAX_ROUNDS + 1):
        sw = sweep(pred, conds, rates)
        flags = _decisive_edge_flags(sw, rates)
        metric = min(iv["ratio_min"] for iv in sw["intervals"])
        converged = (prev_metric is not None
                     and abs(metric - prev_metric) < GRID_C3_TOLERANCE)
        rounds.append(dict(round=k, n_rates=len(rates),
                           rate_min=min(rates), rate_max=max(rates),
                           n_decisive_optima_at_edge=flags["n_edges"],
                           edges=flags["edges"],
                           worst_case_C3_ratio=metric,
                           c3_change_vs_previous=(None if prev_metric is None
                                                  else abs(metric - prev_metric)),
                           converged_by_tolerance=bool(converged),
                           stopped=bool(flags["n_edges"] == 0 or converged
                                        or k == GRID_MAX_ROUNDS)))
        if flags["n_edges"] == 0:
            rounds[-1]["stop_reason"] = "all decisive optima interior"
            break
        if converged:
            rounds[-1]["stop_reason"] = ("C3 converged within %.3f across an expansion"
                                         % GRID_C3_TOLERANCE)
            break
        if k == GRID_MAX_ROUNDS:
            rounds[-1]["stop_reason"] = "max rounds reached"
            break
        prev_metric = metric
        if flags["hits_upper"]:
            hi = max(rates)
            rates += list(np.geomspace(hi * (GRID_EXPANSION_FACTOR ** (1 / GRID_EXPANSION_POINTS)),
                                       hi * GRID_EXPANSION_FACTOR, GRID_EXPANSION_POINTS))
        if flags["hits_lower"]:
            lo = min(rates)
            rates = list(np.geomspace(lo / GRID_EXPANSION_FACTOR,
                                      lo / (GRID_EXPANSION_FACTOR ** (1 / GRID_EXPANSION_POINTS)),
                                      GRID_EXPANSION_POINTS)) + rates
        rates = sorted(set(float(r) for r in rates))
    return dict(rounds=rounds, final_rates=[float(r) for r in rates],
                base_rates=list(BASE_RATE_GRID),
                policy=dict(expansion_factor=GRID_EXPANSION_FACTOR,
                            points_per_round=GRID_EXPANSION_POINTS,
                            max_rounds=GRID_MAX_ROUNDS,
                            c3_tolerance=GRID_C3_TOLERANCE)), sw, rates


# ------------------------------------------------------------------------------------------
# Amplitude term (the "level") — corrected metric and corrected language
# ------------------------------------------------------------------------------------------
def amplitude_diagnostic(pred, conds, coefs, shared_idx, rates, x):
    """How much the free AMPLITUDE term reduces the RMS standardised residual.

    The metric is  1 - RMS_fitted / RMS_fixed  — a REDUCTION IN RMS STANDARDISED-RESIDUAL
    MAGNITUDE. It is NOT "a fraction of the raw residual"; the first version mislabelled it.

    The amplitude is a per-(species, variety) multiplicative scale on the prediction. It may
    represent a solid inventory difference, an assay calibration scale, or any multiplicative
    model error; this screen cannot distinguish those, and does not try.
    """
    from puckworks.models.pannusch2024 import solver as ps
    table2 = {s: v["c_s0"] for s, v in ps._solute_params().items()}
    u = float(np.sqrt(x))
    held = [c for c in conds if c["held_out"]]
    fixed, fitted = [], []
    for c in held:
        v = c["variety"]
        ri = shared_idx[v]
        row = pred.row(rates[ri])
        for s in SPECIES:
            f = row[(v, c["T_degC"], c["p_bar"], s)]
            m = c["measured"][s]
            L = coefs[v][ri]["levels"][s]
            k = (100.0 / c["tds_rsd_pct"]) if s == "tds" else u
            fixed.append((table2[s] * f - m) / m * k)
            fitted.append((L * f - m) / m * k)
    rf = float(np.sqrt(np.mean(np.square(fixed))))
    rt = float(np.sqrt(np.mean(np.square(fitted))))
    return dict(rsd_pct=x_to_rsd(x),
                RMS_z_amplitude_fixed_at_pannusch_table2=rf,
                RMS_z_amplitude_fitted=rt,
                rms_reduction_fraction=(1.0 - rt / rf) if rf > 0 else None,
                metric_definition="1 - RMS(z_fitted) / RMS(z_fixed), where z is the standardised "
                                  "held-out residual and 'fixed' holds the amplitude at "
                                  "pannusch Table 2 c_s0. A REDUCTION IN RMS STANDARDISED-"
                                  "RESIDUAL MAGNITUDE, not a fraction of raw residual.",
                interpretation="The amplitude is a condition-independent multiplicative scale. "
                               "It may represent solid inventory, assay calibration scale, or "
                               "multiplicative model error; this screen cannot separate them.")


def amplitude_vs_table7(coefs, shared_idx, rates, rsd_pct=None, shared_rates=None,
                        all_selections=None):
    """Compare the fitted amplitude against angeloni Table 7, with the matching qualified.

    The fitted amplitude depends on which shared rate was selected, which in turn depends on the
    assumed bioactive RSD. The comparison is therefore SETTING-DEPENDENT and its provenance is
    recorded: the RSD it was evaluated at and the shared rates in force. `all_selections`, when
    given, is the list of distinct shared-rate selections across the band; the count is then also
    reported over every one of them so no setting-independent claim is implied.
    """
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    table2 = {s: v["c_s0"] for s, v in ps._solute_params().items()}
    inv = {(r["variety"], r["species"]): r["C0_s_mg_L"] / 1000.0
           for r in d.angeloni_inventories()}
    inv_col = {"caffeine": "CF", "trigonelline": "TR"}      # species-matched ONLY
    rows, closer, matched = [], 0, 0
    for v in VARIETIES:
        ri = shared_idx[v]
        for s in SPECIES:
            L = coefs[v][ri]["levels"][s]
            rec = dict(variety=v, species=s, amplitude_fitted=round(L, 4),
                       amplitude_pannusch_table2=round(table2[s], 4))
            if s in inv_col:
                t7 = inv[(v, inv_col[s])]
                matched += 1
                is_closer = abs(L - t7) < abs(table2[s] - t7)
                closer += int(is_closer)
                rec.update(species_matched=True, angeloni_table7_g_L=round(t7, 4),
                           fitted_closer_to_table7_than_pannusch=bool(is_closer),
                           note="species-matched")
            elif s == "5CQA":
                rec.update(species_matched=False,
                           angeloni_table7_g_L=round(inv[(v, "CQA")], 4),
                           fitted_closer_to_table7_than_pannusch=None,
                           note="angeloni Table 7 reports TOTAL CQA, which is NOT a "
                                "species-matched 5CQA inventory — no comparison is made")
            else:
                rec.update(species_matched=False, angeloni_table7_g_L=None,
                           fitted_closer_to_table7_than_pannusch=None,
                           note="no Table 7 inventory exists for the aggregate total-solids "
                                "proxy")
            rows.append(rec)
    across = None
    if all_selections:
        counts = []
        for sel in all_selections:
            c = 0
            for v in VARIETIES:
                ri = sel[v]
                for sp, col in inv_col.items():
                    L = coefs[v][ri]["levels"][sp]
                    t7 = inv[(v, col)]
                    c += int(abs(L - t7) < abs(table2[sp] - t7))
            counts.append(c)
        across = dict(n_distinct_shared_selections=len(all_selections),
                      counts_closer_per_selection=counts,
                      min_closer=min(counts), max_closer=max(counts),
                      constant_across_selections=bool(len(set(counts)) == 1))
    return dict(rows=rows, n_species_matched_cells=matched,
                n_species_matched_cells_fitted_closer=closer,
                evaluated_at_rsd_pct=rsd_pct,
                evaluated_at_shared_rates=shared_rates,
                setting_dependence=across,
                claim="At the recorded evaluation setting (bioactive RSD %s %%, shared rates %s): "
                      "of the %d SPECIES-MATCHED cells (caffeine and trigonelline, both "
                      "varieties), %d have a fitted amplitude closer to angeloni Table 7 than "
                      "pannusch Table 2. 5CQA and total solids are NOT species-matched and are "
                      "excluded from that count. The amplitude depends on the selected shared "
                      "rate, so this count is setting-dependent; %s"
                      % (("%.3f" % rsd_pct) if rsd_pct is not None else "unrecorded",
                         shared_rates, matched, closer,
                         ("across all %d distinct shared-rate selections on the band the count is "
                          "%s (min %d, max %d)%s"
                          % (across["n_distinct_shared_selections"],
                             "constant" if across["constant_across_selections"] else "NOT constant",
                             across["min_closer"], across["max_closer"],
                             "" if across["constant_across_selections"]
                             else " — do not quote a single figure as setting-independent"))
                         if across else "the cross-setting count was not computed"))


# ------------------------------------------------------------------------------------------
# Screen
# ------------------------------------------------------------------------------------------
def screen():
    conds = conditions()
    pred = UnitPredictions(conds)
    robustness, sw, rates = grid_robustness(pred, conds)

    any_survive = any(iv["any_survive"] for iv in sw["intervals"])
    all_survive = all(iv["all_survive"] for iv in sw["intervals"])
    c3_ever = any(e["C3_reduced_by_species_fits"]
                  for iv in sw["intervals"] for e in iv["evaluations"])
    worst_ratio = min(iv["ratio_min"] for iv in sw["intervals"])

    if all_survive:
        decision = "SURVIVE"
        why = ("Reproducible species-specific held-out residual structure remains beyond "
               "uncertainty and is materially reduced by per-species fits at every evaluated "
               "point of the declared RSD band.")
    elif any_survive:
        decision = "NEEDS_NEW_DATA"
        why = ("The verdict CHANGES inside the declared 0.3-19.7 %% bioactive RSD band, so it is "
               "not determined by the retained uncertainty. Solute-specific replicate RSD for "
               "caffeine, trigonelline and CGA is the missing evidence.")
    else:
        decision = "RETIRE"
        why = ("The shared-state hypothesis is not refuted anywhere in the declared RSD band. "
               "C3 never holds: the smallest held-out RMS ratio achieved anywhere on the band, "
               "over the exact breakpoint sweep and after rate-grid expansion, is %.4f against "
               "a %.2f threshold — per-species rate freedom does not improve held-out "
               "prediction at any admissible uncertainty setting." % (worst_ratio,
                                                                      C3_REDUCTION_FACTOR))

    # amplitude diagnostics at BOTH retained endpoints (and every interval boundary)
    coefs, indep = sw["coefs"], sw["indep"]
    amp = []
    for iv in sw["intervals"]:
        for x in (iv["x_lo"], iv["x_hi"]):
            amp.append(amplitude_diagnostic(pred, conds, coefs, iv["shared_rate_index"],
                                            rates, x))
    seen, amp_unique = set(), []
    for a in amp:
        k = round(a["rsd_pct"], 6)
        if k not in seen:
            seen.add(k)
            amp_unique.append(a)

    last = sw["intervals"][-1]
    seen_sel, distinct = set(), []
    for iv in sw["intervals"]:
        key = tuple(sorted(iv["shared_rate_index"].items()))
        if key not in seen_sel:
            seen_sel.add(key)
            distinct.append(iv["shared_rate_index"])
    t7 = amplitude_vs_table7(
        coefs, last["shared_rate_index"], rates,
        rsd_pct=x_to_rsd(last["x_hi"]),
        shared_rates={v: round(last["shared_rate"][v], 4) for v in VARIETIES},
        all_selections=distinct)

    slim_intervals = [{k: v for k, v in iv.items()} for iv in sw["intervals"]]
    return dict(
        screen=CANDIDATE_ID,
        disposition=["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                     "NOT_A_MODEL_VALIDATION_UPGRADE"],
        correction_note=(
            "CORRECTED 2026-08-04. The superseded version claimed C3 was scale-free in the "
            "assumed RSD and inferred whole-band invariance from two endpoints. Neither was "
            "supported: changing the bioactive RSD reweights the bioactives against the "
            "MEASURED total-solids weights and refits the shared model (its selected rate "
            "demonstrably moves). Both claims are replaced by an exact finite-grid breakpoint "
            "argument plus rate-grid expansion. The evidence unit, the split, the free "
            "amplitude in both models, the held-out comparison and the C1/C2/C3 thresholds are "
            "unchanged."),
        evidence_unit=dict(
            campaign="angeloni2023 only (bioactives + total_solids), granulometry O, on-grid",
            manifest_validation_strength_verbatim=(
                "independent (different machine/coffee/basket than pannusch fit or cameron "
                "calibration)"),
            n_conditions=len(conds),
            n_train=sum(1 for c in conds if not c["held_out"]),
            n_held_out=sum(1 for c in conds if c["held_out"]),
            species=list(SPECIES), varieties=list(VARIETIES),
            excluded_evidence=EXCLUDED_EVIDENCE),
        predeclared=dict(train_p_bar=list(TRAIN_P_BAR), held_out_p_bar=list(HELD_OUT_P_BAR),
                         split_rationale=SPLIT_RATIONALE,
                         base_rate_grid=[round(r, 6) for r in BASE_RATE_GRID],
                         criterion=CRITERION_STATEMENT,
                         C1_z_threshold=C1_Z_THRESHOLD,
                         C2_spread_threshold=C2_SPREAD_THRESHOLD,
                         C3_reduction_factor=C3_REDUCTION_FACTOR),
        uncertainty=dict(
            bioactive_rsd_band_pct=list(BIOACTIVE_RSD_BAND_PCT),
            bioactive_rsd_band_source=BIOACTIVE_RSD_BAND_SOURCE,
            tds_rsd_source=TDS_RSD_SOURCE,
            solute_specific_rsd_recovered=False,
            scale_free_claim_withdrawn=(
                "C3 is NOT scale-free under this perturbation. Changing the bioactive RSD "
                "changes their weight relative to the MEASURED per-condition total-solids "
                "weights, which refits the shared model. The selected shared rate is observed to "
                "move across the band."),
            method="exact finite-grid breakpoint sweep in x = (100/RSD)^2, plus each interval's "
                   "C2 vertex; C1 and C3 are monotone on a fixed selection so their extrema are "
                   "at interval endpoints"),
        rate_grid_robustness=robustness,
        sweep=dict(x_range=sw["x_range"], rsd_range_pct=sw["rsd_range_pct"],
                   breakpoints=sw["breakpoints"],
                   n_breakpoints=sum(len(v) for v in sw["breakpoints"].values()),
                   independent_selection=sw["independent_selection"],
                   independent_selection_is_x_independent=True,
                   n_evaluated_points=sw["n_evaluated_points"],
                   intervals=slim_intervals),
        worst_case_C3_ratio=worst_ratio,
        C3_ever_satisfied=c3_ever,
        any_point_survives=any_survive, all_points_survive=all_survive,
        amplitude_diagnostic=amp_unique,
        amplitude_vs_table7=t7,
        n_pde_solves=pred.n_solves,
        decision=decision, decision_reasoning=why)


# ------------------------------------------------------------------------------------------
# Primary figure
# ------------------------------------------------------------------------------------------
_INK, _MUTED, _GRID = "#1a1a1a", "#5a5a5a", "#d9d9d9"
_C_SHARED, _C_INDEP, _C_C3 = "#0072b2", "#e69f00", "#cc79a7"


def figure(path=None, result=None):
    """Three panels: the exact band sweep, the grid-expansion evidence, and the residuals."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})
    r = result or screen()

    conds = conditions()
    pred = UnitPredictions(conds)
    rates = [float(v) for v in r["rate_grid_robustness"]["final_rates"]]
    sw = sweep(pred, conds, rates)

    fig = plt.figure(figsize=(13.6, 8.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.0, 1.05], hspace=0.42, wspace=0.30)

    # ---- panel A: C3 across the band ------------------------------------------------------
    axA = fig.add_subplot(gs[0, 0:2])
    for iv in sw["intervals"]:
        xs = [e["rsd_pct"] for e in iv["evaluations"]]
        ys = [e["reduction_ratio"] for e in iv["evaluations"]]
        o = np.argsort(xs)
        axA.plot(np.array(xs)[o], np.array(ys)[o], "-", color=_C_C3, lw=1.8, zorder=3)
        axA.plot(xs, ys, "o", color=_C_C3, ms=4.2, zorder=4)
    n_bp = 0
    for _v, bl in sw["breakpoints"].items():
        for b in bl:
            axA.axvline(b["rsd_pct"], color=_MUTED, lw=0.8, ls=":", alpha=0.75, zorder=1)
            n_bp += 1
    axA.axhline(C3_REDUCTION_FACTOR, color="#d55e00", lw=1.6, ls="--", zorder=2)
    axA.text(BIOACTIVE_RSD_BAND_PCT[1], C3_REDUCTION_FACTOR * 0.93,
             "C3 threshold %.2f — per-species fits must get BELOW this line"
             % C3_REDUCTION_FACTOR, fontsize=7.4, color="#d55e00", ha="right", va="top")
    axA.set_xscale("log")
    axA.set_xlim(*BIOACTIVE_RSD_BAND_PCT)
    axA.set_ylim(0.0, max(1.25, min(2.0, max(iv["ratio_max"] for iv in sw["intervals"]) * 1.15)))
    axA.set_xlabel("assumed bioactive replicate RSD  [%]  (the campaign retains only this RANGE)",
                   fontsize=8)
    axA.set_ylabel("C3 statistic\nZ_independent / Z_shared", fontsize=8.4)
    axA.grid(True, color=_GRID, lw=0.5)
    axA.set_axisbelow(True)
    axA.text(0.015, 0.96, "dotted lines: the %d shared-rate breakpoints — where the selected "
             "rate switches.\nC1 and C3 are monotone between them, so the plotted points bound "
             "each interval exactly." % n_bp,
             transform=axA.transAxes, fontsize=7.0, color=_MUTED, va="top", linespacing=1.5)
    axA.set_title("A — exact sweep of C3 across the declared RSD band",
                  fontsize=8.8, color=_INK, pad=7)

    # ---- panel B: grid expansion ----------------------------------------------------------
    axB = fig.add_subplot(gs[0, 2])
    rounds = r["rate_grid_robustness"]["rounds"]
    xs = [q["round"] for q in rounds]
    axB.plot(xs, [q["worst_case_C3_ratio"] for q in rounds], "o-", color=_C_C3, lw=1.8, ms=6)
    axB.axhline(C3_REDUCTION_FACTOR, color="#d55e00", lw=1.4, ls="--")
    for q in rounds:
        axB.annotate("%d rates\nmax %.1f\n%d edge optima"
                     % (q["n_rates"], q["rate_max"], q["n_decisive_optima_at_edge"]),
                     (q["round"], q["worst_case_C3_ratio"]), textcoords="offset points",
                     xytext=(6, -22), fontsize=6.4, color=_MUTED)
    axB.set_xticks(xs)
    axB.set_xlim(-0.45, max(xs) + 0.75)
    axB.set_xlabel("rate-grid expansion round", fontsize=8)
    axB.set_ylabel("worst-case (smallest) C3 ratio\nanywhere on the band", fontsize=8)
    axB.grid(True, color=_GRID, lw=0.5)
    axB.set_axisbelow(True)
    axB.set_ylim(0.0, max(1.25, max(q["worst_case_C3_ratio"] for q in rounds) * 1.15))
    axB.set_title("B — rate-grid robustness\nstopped: %s" % rounds[-1].get("stop_reason", ""),
                  fontsize=8.6, color=_INK, pad=7)

    # ---- panel C: held-out standardised residuals at both retained endpoints --------------
    for j, which in enumerate(("hi", "lo")):
        axC = fig.add_subplot(gs[1, j])
        x = rsd_to_x(BIOACTIVE_RSD_BAND_PCT[0] if which == "hi" else BIOACTIVE_RSD_BAND_PCT[1])
        iv = min(sw["intervals"], key=lambda q: abs(np.log(q["x_lo"]) - np.log(x))
                 if which == "lo" else abs(np.log(q["x_hi"]) - np.log(x)))
        parts = residual_parts(pred, conds, sw["coefs"], iv["shared_rate_index"],
                               sw["indep"], rates)
        u = float(np.sqrt(x))
        keys = sorted({(p["variety"], p["T_degC"]) for p in parts})
        i = 0
        ticks, labels = [], []
        for v, T in keys:
            for s in SPECIES:
                p = [q for q in parts if q["variety"] == v and q["T_degC"] == T
                     and q["species"] == s][0]
                zs = p["d_shared"] * u if p["scales_with_x"] else p["z_shared_fixed"]
                zi = p["d_independent"] * u if p["scales_with_x"] else p["z_independent_fixed"]
                axC.plot([i, i], [0, zs], color=_C_SHARED, lw=1.0, alpha=0.4, zorder=1)
                axC.plot(i - 0.16, zs, "o", ms=4.6, color=_C_SHARED, zorder=3)
                axC.plot(i + 0.16, zi, "s", ms=4.2, color=_C_INDEP, zorder=3)
                ticks.append(i)
                labels.append("%s %s %.0f°C" % (s, v[:3], T))
                i += 1
        axC.axhspan(-1, 1, color="#6b6b6b", alpha=0.11, zorder=0)
        axC.axhline(0, color=_INK, lw=0.9, zorder=2)
        axC.set_xticks(ticks)
        axC.set_xticklabels(labels, fontsize=5.4, rotation=90)
        axC.set_yscale("symlog", linthresh=2.0)
        axC.grid(True, axis="y", color=_GRID, lw=0.5)
        axC.set_axisbelow(True)
        ev = criteria_at(parts, x)
        axC.set_title("C%d — held-out residuals at RSD = %.1f %%\nZ_sh %.2f  Z_in %.2f  "
                      "ratio %.3f  spread %.2f  →  %s"
                      % (j + 1, x_to_rsd(x), ev["Z_shared"], ev["Z_independent"],
                         ev["reduction_ratio"], ev["between_species_spread"],
                         "SURVIVE" if ev["survive"] else "not survived"),
                      fontsize=8.2, color=_INK, pad=6)
        if j == 0:
            axC.set_ylabel("standardised held-out residual z\nsymlog, linear within ±2",
                           fontsize=8)

    # ---- panel D: amplitude diagnostic -----------------------------------------------------
    axD = fig.add_subplot(gs[1, 2])
    amp = r["amplitude_diagnostic"]
    xs = [a["rsd_pct"] for a in amp]
    ys = [100.0 * (a["rms_reduction_fraction"] or 0.0) for a in amp]
    o = np.argsort(xs)
    axD.plot(np.array(xs)[o], np.array(ys)[o], "o-", color="#0072b2", lw=1.8, ms=5)
    axD.set_xscale("log")
    axD.set_xlabel("assumed bioactive RSD  [%]", fontsize=8)
    axD.set_ylabel("reduction in RMS standardised residual\nfrom fitting the amplitude  [%]",
                   fontsize=7.8)
    axD.grid(True, color=_GRID, lw=0.5)
    axD.set_axisbelow(True)
    axD.set_title("D — the free AMPLITUDE term\n1 − RMS(z_fitted)/RMS(z_fixed), at every "
                  "evaluated setting", fontsize=8.6, color=_INK, pad=7)

    handles = [plt.Line2D([], [], ls="none", marker="o", color=_C_SHARED, ms=5,
                          label="shared state — one rate per variety, all species"),
               plt.Line2D([], [], ls="none", marker="s", color=_C_INDEP, ms=4.6,
                          label="independent per-species fits — one rate per species"),
               plt.Rectangle((0, 0), 1, 1, fc="#6b6b6b", alpha=0.11,
                             label="±1 measurement σ")]

    fig.suptitle("I-024 — can one shared transport state explain every measured species at "
                 "once?   Held-out = 9 bar (interior pressure), predeclared",
                 fontsize=11.5, y=1.005, x=0.005, ha="left", weight="bold")
    fig.text(0.005, 0.968,
             "CHEAP_SCIENTIFIC_SCREEN · NOT_A_PUBLICATION_RESULT · "
             "NOT_A_MODEL_VALIDATION_UPGRADE     angeloni2023 ONLY.     A per-species amplitude "
             "is free in BOTH models.     C3 is NOT scale-free in the assumed RSD — the shared "
             "model is refitted as the weighting changes, which is why panel A is a sweep and "
             "not two points.",
             fontsize=7.0, color=_MUTED, style="italic", ha="left")
    fig.tight_layout()
    fig.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.005), ncol=3,
               fontsize=7.4, frameon=False)
    t7 = r["amplitude_vs_table7"]
    fig.text(0.005, -0.065, va="top", ha="left", fontsize=7.1, color=_MUTED, linespacing=1.6,
             s="Predeclared criterion (units of measurement σ): C1 Z_shared > 1 · C2 "
               "between-species spread > 1 · C3 Z_independent ≤ 0.70 × Z_shared. SURVIVE iff "
               "C1 ∧ C2 ∧ C3.\n"
               "Exact band coverage: %d shared-rate breakpoint(s), %d evaluated points across "
               "%d fixed-selection interval(s). The independent per-species rates are provably "
               "x-independent and do not move across the band.\n"
               "Amplitude: a condition-independent multiplicative scale — it may be solid "
               "inventory, assay calibration scale, or multiplicative model error, and this "
               "screen cannot separate them. %s\n"
               "DECISION  %s — %s"
               % (r["sweep"]["n_breakpoints"], r["sweep"]["n_evaluated_points"],
                  len(r["sweep"]["intervals"]), t7["claim"],
                  r["decision"], r["decision_reasoning"]))

    path = path or (REPO_ROOT / "docs/insights/screens/I-024/figures/primary.png")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main(argv=None):
    r = screen()
    out = REPO_ROOT / "docs/insights/screens/I-024/result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2, default=float) + "\n", encoding="utf-8")
    print("conditions: %d train / %d held out   (%d PDE solves)"
          % (r["evidence_unit"]["n_train"], r["evidence_unit"]["n_held_out"],
             r["n_pde_solves"]))
    print("rate-grid robustness:")
    for q in r["rate_grid_robustness"]["rounds"]:
        print("  round %d  n_rates=%-3d max=%8.2f  edge optima=%-2d  worst C3=%.4f  %s"
              % (q["round"], q["n_rates"], q["rate_max"],
                 q["n_decisive_optima_at_edge"], q["worst_case_C3_ratio"],
                 q.get("stop_reason", "")))
    print("band sweep: %d breakpoint(s), %d interval(s), %d evaluated points"
          % (r["sweep"]["n_breakpoints"], len(r["sweep"]["intervals"]),
             r["sweep"]["n_evaluated_points"]))
    for iv in r["sweep"]["intervals"]:
        print("  RSD %7.3f-%7.3f %%  shared rates %s  ratio %.4f-%.4f  survive_any=%s"
              % (iv["rsd_lo_pct"], iv["rsd_hi_pct"],
                 {k: round(v, 3) for k, v in iv["shared_rate"].items()},
                 iv["ratio_min"], iv["ratio_max"], iv["any_survive"]))
    print("worst-case C3 ratio anywhere on the band: %.4f  (threshold %.2f)"
          % (r["worst_case_C3_ratio"], C3_REDUCTION_FACTOR))
    print("amplitude RMS reduction: %s"
          % ", ".join("%.1f %% @ RSD %.2f %%" % (100 * a["rms_reduction_fraction"],
                                                 a["rsd_pct"]) for a in
                      r["amplitude_diagnostic"]))
    print("DECISION: %s" % r["decision"])
    fig_path = figure(result=r)
    print("wrote %s" % out.relative_to(REPO_ROOT))
    print("wrote %s" % fig_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
