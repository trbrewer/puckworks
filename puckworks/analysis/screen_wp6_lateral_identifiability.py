"""screen_wp6_lateral_identifiability.py — WP6-LC-IDENT cheap screen.

    HUMAN_SELECTED_POST_SNAPSHOT
    CHEAP_SCIENTIFIC_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Question (frozen in docs/insights/screens/WP6-LC-IDENT/PROTOCOL.md before this module existed):

    In the controlled isoresistive-mirror two-path geometry already used by the lateral-coupling
    discrimination harness, is the mapping from physical lateral coupling to the pair
    (total-flow ratio R = Q/Q0, separate outlet-flow share s = q1/Q) one-to-one, so that Xi can
    be recovered without separately measuring k_lat and w?

THE PRIMARY RESULT CONCERNS Xi -- the EXACT pressure-equalization number
Xi = G_lat*(1/A1 + 1/A2) -- and never the legacy provisional Lambda regime labels, which appear
nowhere in this screen's output.

SCOPE. This module executes the frozen protocol and nothing else. It is the exact steady two-path
Darcy network only (models.lateral_coupling.model1_two_path); no N-path network, no PDE, no
extraction clock, no time dependence, no real data, no fitted parameter, no k_lat and no w. It
adds no Foundry lens, no candidate generator, no scoring, and touches neither
docs/insights/ID_REGISTRY.json nor docs/insights/generated/.

THE PROXY ADVERSARY IS REUSED, NOT DUPLICATED: analysis.lateral_coupling_discrimination.
physical_row is CALLED, so the frozen share proxy gets its own strongest admissible continuous
alpha fit as that module computes it. No alpha = f(Xi) law is invented here or anywhere.

Run:
    python -m puckworks.analysis.screen_wp6_lateral_identifiability --write
    python -m puckworks.analysis.screen_wp6_lateral_identifiability --verify
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib

import numpy as np

from puckworks.models import lateral_coupling as lc
from puckworks.analysis import lateral_coupling_discrimination as lcd

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

SCREEN_ID = "WP6-LC-IDENT"
SCHEMA_VERSION = 1
BASE_COMMIT = "f77d0e328496dc1e85bf00fdb06ccdc52d8b2108"
PROTOCOL_PATH = "docs/insights/screens/WP6-LC-IDENT/PROTOCOL.md"
BUNDLE_REL = "docs/insights/screens/WP6-LC-IDENT"

INPUT_FILES = (
    PROTOCOL_PATH,
    "puckworks/models/lateral_coupling.py",
    "puckworks/analysis/lateral_coupling_discrimination.py",
    "puckworks/analysis/lateral_proxy.py",
    "docs/cards/lateral_coupling_feasibility.md",
)

# ---- frozen scenario (PROTOCOL §4, §6) ----------------------------------------------------
P_IN = lcd.P_IN                       # 9.0e5 — the harness inlet pressure, not re-chosen here
A_PRIMARY = 4.0                       # A = a + b; with c = 0.5 this is exactly (a, b) = (3, 1)
C_PRIMARY = 0.5
A_SCALED = 40.0                       # x10 conductance-scaling control
C_GRID = (-0.90, -0.75, -0.50, -0.25, -0.10, 0.10, 0.25, 0.50, 0.75, 0.90)
XI_LOG_GRID = tuple(float(10.0 ** e) for e in np.linspace(-4.0, 3.0, 22))
XI_GRID = (0.0,) + XI_LOG_GRID
XI_SCENARIO_SET = (0.05, 0.1875, 0.75, 1.0, 5.0, 19.0)   # 0.1875 and 19 are the card's own values
PERTURB_LEVELS = (0.01, 0.02, 0.05)                       # mirror-imperfection SCENARIOS
PRECISION_FLOORS = tuple(lcd.PRECISION_FLOORS)            # 1%/2%/5%, reused, not re-invented

# ---- software tolerances (reproducibility bounds, NOT scientific uncertainties) ------------
TOL_MAP = 1e-12          # analytic forward map vs the exact network
TOL_C = 1e-9             # recovered signed contrast
TOL_XI_REL = 1e-6        # recovered Xi, relative
DEGENERATE_ATOL = 1e-12  # |R-1| and |s-0.5| below this are float-indistinguishable from the
#                          degenerate point. The smallest nondegenerate signal on the frozen grid
#                          (c = 0.10, Xi = 1e-4) is |R-1| ~ 1.0e-6 — six orders above this.
_RECORD_DP = 12          # recorded floats are rounded to 12 dp so artifacts are byte-stable


# ==========================================================================================
# geometry, forward map, inverse
# ==========================================================================================

def mirror_conductances(A, c):
    """The isoresistive-mirror construction: (g1_top, g1_bot, g2_top, g2_bot) = (a, b, b, a),
    with a = A(1+c)/2, b = A(1-c)/2 so that a + b = A and (a-b)/(a+b) = c."""
    a = A * (1.0 + c) / 2.0
    b = A * (1.0 - c) / 2.0
    return (a, b, b, a)


def g_lat_from_xi(A, Xi):
    """Mirror case has A1 = A2 = A, so Xi = G_lat*(1/A1 + 1/A2) = 2*G_lat/A."""
    return Xi * A / 2.0


def forward_map_analytic(c, Xi):
    """Hand-derived mirror forward map (PROTOCOL §5). t = 1/(1+Xi).

        R = (1 - c^2 t)/(1 - c^2)
        s = (1-c)(1 + Xi + c) / (2(1 + Xi - c^2))
    """
    t = 1.0 / (1.0 + Xi)
    R = (1.0 - c * c * t) / (1.0 - c * c)
    s = (1.0 - c) * (1.0 + Xi + c) / (2.0 * (1.0 + Xi - c * c))
    return R, s


def observables_exact(A, c, Xi, P_in=P_IN):
    """BOUNDARY observables from the exact network. Nothing interior is read: the blocked run
    supplies Q0, the open run supplies q1 and q2, and R and s are formed from those three."""
    g = mirror_conductances(A, c)
    G = g_lat_from_xi(A, Xi)
    open_ = lc.model1_two_path(P_in, *g, G)
    blocked = lc.model1_two_path(P_in, *g, 0.0)
    q1, q2, Q0 = open_["q1"], open_["q2"], blocked["Q"]
    Q = q1 + q2
    return {"g": g, "G_lat": G, "q1": q1, "q2": q2, "Q": Q, "Q0": Q0,
            "R": Q / Q0, "s": q1 / Q, "open": open_, "blocked": blocked}


def invert(R, s):
    """Candidate mirror inverse (PROTOCOL §5). Returns a status, never a regularised number.

        c_hat  = (R - 1) / [R (1 - 2s)]
        t_hat  = [1 - R (1 - c_hat^2)] / c_hat^2
        Xi_hat = 1/t_hat - 1
    """
    out = {"R": R, "s": s, "c_hat": None, "t_hat": None, "Xi_hat": None}
    if abs(R - 1.0) <= DEGENERATE_ATOL and abs(s - 0.5) <= DEGENERATE_ATOL:
        out["status"] = "degenerate_no_information"
        return out
    den = R * (1.0 - 2.0 * s)
    if den == 0.0:
        out["status"] = "undefined_zero_share_departure"
        return out
    c_hat = (R - 1.0) / den
    out["c_hat"] = c_hat
    if c_hat == 0.0 or not (-1.0 < c_hat < 1.0):
        out["status"] = "nonphysical_contrast"
        return out
    t_hat = (1.0 - R * (1.0 - c_hat * c_hat)) / (c_hat * c_hat)
    out["t_hat"] = t_hat
    if not (0.0 < t_hat <= 1.0):
        out["status"] = "nonphysical_gap_fraction"
        return out
    out["Xi_hat"] = 1.0 / t_hat - 1.0
    out["status"] = "ok"
    return out


def cross_product_gap_driver(g):
    """X = g1_top*g2_bot - g2_top*g1_bot.

    X is the STRUCTURAL driver of the whole calibrated inversion, and it is zero exactly when the
    two uncoupled mid-node pressures coincide: p_i(G=0) = g_i_top*P/(g_i_top + g_i_bot), so
    p1 = p2  <=>  g1t(g2t+g2b) = g2t(g1t+g1b)  <=>  g1t*g2b = g2t*g1b  <=>  X = 0.
    With no uncoupled pressure gap there is no lateral driving pressure at any G_lat, hence no
    lateral flow and no dependence of Q on G_lat."""
    g1t, g1b, g2t, g2b = g
    return g1t * g2b - g2t * g1b


def dQdG_numerator(g):
    """Numerator of d(Q/P)/dG for the general two-node network. Derived, then recorded:

        Q/P = (N0 + G*M)/(A1*A2 + G*S)
        d(Q/P)/dG = [M*A1*A2 - N0*S] / (A1*A2 + G*S)^2
                  = (g1_top*g2_bot - g2_top*g1_bot)^2 / (A1*A2 + G*S)^2

    Two consequences, both used below: the derivative is a SQUARE, so Q is non-decreasing in
    G_lat for every admissible geometry; and it vanishes IFF X = 0, which is the structural
    degeneracy, not an algebraic accident."""
    g1t, g1b, g2t, g2b = g
    A1, A2 = g1t + g1b, g2t + g2b
    N0 = g1t * g1b * A2 + g2t * g2b * A1
    M = (g1t + g2t) * (g1b + g2b)
    S = A1 + A2
    return M * A1 * A2 - N0 * S


# NUMERICAL RESOLUTION / CONDITIONING threshold — NOT a structural-degeneracy threshold.
#
# The structural condition is EXACT: X == 0 and nothing else. A small nonzero X is still
# mathematically one-to-one; it is merely too ill-conditioned (dG/d(Q/P) ~ 1/X^2) for a
# dependable floating-point inversion. Conflating the two would assert exact equality of the
# uncoupled mid-node pressures in cases where they are provably unequal, so the two are reported
# under DIFFERENT statuses. The value is deliberately conservative; it bounds when this
# implementation declines to return a number, never when the mathematics degenerates.
_NUMERICAL_RESOLUTION_REL = 1e-12


def invert_G_from_known_axials(g, R):
    """One-parameter inversion for G_lat when the FOUR axial conductances are independently
    known (the calibrated-apparatus case). Exact, not a fit: for the general two-node network

        Q/P = (N0 + G*M) / (A1*A2 + G*S),   N0 = g1t*g1b*A2 + g2t*g2b*A1,
                                            M  = (g1t+g2t)(g1b+g2b),  S = A1 + A2

    is a Mobius function of G. It is strictly monotone — hence one-to-one — **iff**

        X = g1_top*g2_bot - g2_top*g1_bot != 0,

    because d(Q/P)/dG = X^2/(A1*A2 + G*S)^2 (see ``dQdG_numerator``).

    **This routine assumes no mirror symmetry, but it is NOT valid for "any geometry".** Three
    outcomes, kept strictly apart:

    * ``X == 0`` EXACTLY -> ``structurally_degenerate_no_information``. The two uncoupled mid-node
      pressures are equal, no lateral pressure drives the bridge at any G_lat, and Q is exactly
      independent of G_lat. This is the ONLY structural no-information case.
    * ``X != 0`` but below the NUMERICAL resolution threshold ->
      ``numerically_unresolved_near_degenerate``. The map is still mathematically INJECTIVE and Q
      is NOT independent of G_lat; the inversion is simply too ill-conditioned
      (dG/d(Q/P) ~ 1/X^2) for a dependable floating-point estimate here. No number is returned,
      and no claim of exact equality is made.
    * otherwise -> the exact inversion, unchanged.
    """
    g1t, g1b, g2t, g2b = g
    A1, A2 = g1t + g1b, g2t + g2b
    N0 = g1t * g1b * A2 + g2t * g2b * A1
    M = (g1t + g2t) * (g1b + g2b)
    S = A1 + A2
    X = cross_product_gap_driver(g)
    scale = (A1 * A2) ** 2                       # X^2 has the units of (conductance)^4
    out = {"cross_product_X": X, "dQdG_numerator": X * X,
           "condition_scale_X2_over_A1A2_squared": (X * X) / scale,
           "structurally_degenerate": X == 0.0}
    if X == 0.0:                                 # EXACT — the only structural no-information case
        out.update(G_lat_hat=None, status="structurally_degenerate_no_information",
                   why="g1_top*g2_bot == g2_top*g1_bot EXACTLY: the uncoupled mid-node pressures "
                       "are equal, so no lateral pressure drives the bridge and Q is exactly "
                       "independent of G_lat.")
        return out
    if X * X <= _NUMERICAL_RESOLUTION_REL * scale:
        out.update(G_lat_hat=None, status="numerically_unresolved_near_degenerate",
                   why="X != 0, so the map IS mathematically injective and Q is NOT independent "
                       "of G_lat -- but dG/d(Q/P) ~ 1/X^2 is too ill-conditioned at this X for a "
                       "dependable floating-point inversion, so no estimate is returned. This is "
                       "a NUMERICAL resolution limit of this implementation, NOT a structural "
                       "degeneracy, and it asserts NO equality of the uncoupled mid-node "
                       "pressures.")
        return out
    QP = R * N0 / (A1 * A2)                      # = Q/P_in
    den = M - QP * S
    if den == 0.0:                               # only reachable as Q/P -> the G->inf asymptote
        out.update(G_lat_hat=None, status="singular_at_infinite_coupling")
        return out
    G = (QP * A1 * A2 - N0) / den
    out.update(G_lat_hat=G, status="ok" if G >= 0.0 else "nonphysical_negative")
    return out


def _bisect_G(g, Q_target, P_in=P_IN, hi_max=1e18):
    """Independent bracketed cross-check of invert_G_from_known_axials — no closed form used."""
    def Q(G):
        return lc.model1_two_path(P_in, *g, G)["Q"]
    lo, hi = 0.0, 1.0
    q_lo = Q(lo)
    if abs(Q_target - q_lo) <= 1e-15 * max(1.0, abs(q_lo)):
        return 0.0
    up = Q(hi)
    n = 0
    while (up - q_lo) * (Q_target - q_lo) < 0 or abs(Q_target - q_lo) > abs(up - q_lo):
        hi *= 10.0
        up = Q(hi)
        n += 1
        if hi > hi_max:
            return None
    for _ in range(400):
        mid = 0.5 * (lo + hi)
        if (Q(mid) - Q_target) * (Q(lo) - Q_target) <= 0.0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


# ==========================================================================================
# Arm A/B — analytic derivation cross-checked against the exact network, and recovery
# ==========================================================================================

def arm_b_recovery():
    rows, errs_map, errs_c, errs_xi = [], [], [], []
    for c in C_GRID:
        for Xi in XI_GRID:
            o = observables_exact(A_PRIMARY, c, Xi)
            R_a, s_a = forward_map_analytic(c, Xi)
            e_map = max(abs(R_a - o["R"]), abs(s_a - o["s"]))
            inv = invert(o["R"], o["s"])
            degenerate = (Xi == 0.0)
            if degenerate:
                ok_c = ok_xi = None
                e_c = e_xi = None
            else:
                e_c = abs(inv["c_hat"] - c) if inv["c_hat"] is not None else float("inf")
                e_xi = (abs(inv["Xi_hat"] - Xi) / Xi) if inv["Xi_hat"] is not None else float("inf")
                ok_c, ok_xi = e_c <= TOL_C, e_xi <= TOL_XI_REL
                errs_c.append(e_c)
                errs_xi.append(e_xi)
            errs_map.append(e_map)
            rows.append({"c": c, "Xi": Xi, "R": o["R"], "s": o["s"],
                         "R_analytic": R_a, "s_analytic": s_a, "map_abs_err": e_map,
                         "map_ok": e_map <= TOL_MAP, "inverse_status": inv["status"],
                         "c_hat": inv["c_hat"], "Xi_hat": inv["Xi_hat"],
                         "c_abs_err": e_c, "Xi_rel_err": e_xi,
                         "c_ok": ok_c, "Xi_ok": ok_xi, "degenerate_by_construction": degenerate})

    live = [r for r in rows if not r["degenerate_by_construction"]]
    pts = np.array([[r["R"], r["s"]] for r in live], float)
    d = np.hypot(pts[:, None, 0] - pts[None, :, 0], pts[:, None, 1] - pts[None, :, 1])
    np.fill_diagonal(d, np.inf)
    i, j = np.unravel_index(int(np.argmin(d)), d.shape)
    # NUMERICAL WORDING: the recorded value is rounded to 12 dp, so a machine-precision residual
    # records as 0.0. That is FLOATING-POINT AGREEMENT, not an algebraic-identity claim -- the
    # identity claim is the derivation, which is separate. Keep a stable bound on the live value.
    live_map_err = max(errs_map)
    # recorded as an INTEGER exponent: the value itself (order 1e-14) would round to 0.0 at the
    # artifact's 12 dp, which is precisely the confusion this field exists to prevent.
    ceil10 = None if live_map_err <= 0.0 else int(math.ceil(math.log10(live_map_err)))
    return {
        "n_grid_points": len(rows), "n_nondegenerate": len(live),
        "rows": rows,
        "forward_map_max_abs_error": live_map_err,
        "forward_map_max_abs_error_log10_upper_bound": ceil10,
        "forward_map_error_is_floating_point_not_algebraic": (
            "The analytic map and the network solve are the SAME algebra, so their difference is "
            "pure floating-point rounding: the live maximum is of order 1e-14 (7.99e-15 in the "
            "reference environment) and records as 0.0 only after this artifact's 12-decimal "
            "rounding. Read it as 'agrees to machine precision', never as 'exactly zero'."),
        "forward_map_tolerance": TOL_MAP,
        "forward_map_agrees_with_exact_network": max(errs_map) <= TOL_MAP,
        "c_max_abs_error": max(errs_c), "c_tolerance": TOL_C,
        "Xi_max_rel_error": max(errs_xi), "Xi_tolerance_rel": TOL_XI_REL,
        "recovery_passes_everywhere": bool(all(r["c_ok"] and r["Xi_ok"] for r in live)),
        "failures": [{"c": r["c"], "Xi": r["Xi"], "c_abs_err": r["c_abs_err"],
                      "Xi_rel_err": r["Xi_rel_err"], "status": r["inverse_status"]}
                     for r in live if not (r["c_ok"] and r["Xi_ok"])],
        "injectivity_empirical": {
            "min_pairwise_Rs_distance": float(d[i, j]),
            "closest_pair": [{"c": live[i]["c"], "Xi": live[i]["Xi"]},
                             {"c": live[j]["c"], "Xi": live[j]["Xi"]}],
            "distinct": bool(d[i, j] > 0.0),
            "note": "Every nondegenerate grid point maps to a DISTINCT (R, s). This is the "
                    "empirical companion to the algebraic argument, not a substitute for it.",
        },
        "scale_invariance_check": _scale_check(),
    }


def _scale_check():
    """x10 conductance scaling with G_lat scaled likewise, so Xi is held fixed."""
    out = []
    for Xi in XI_SCENARIO_SET:
        o1 = observables_exact(A_PRIMARY, C_PRIMARY, Xi)
        o2 = observables_exact(A_SCALED, C_PRIMARY, Xi)
        i1, i2 = invert(o1["R"], o1["s"]), invert(o2["R"], o2["s"])
        out.append({
            "Xi": Xi,
            "flow_scale_factor_Q": o2["Q"] / o1["Q"],
            "flow_scale_factor_Q0": o2["Q0"] / o1["Q0"],
            "R_delta": abs(o2["R"] - o1["R"]), "s_delta": abs(o2["s"] - o1["s"]),
            "c_hat_delta": abs(i2["c_hat"] - i1["c_hat"]),
            "Xi_hat_delta": abs(i2["Xi_hat"] - i1["Xi_hat"]),
            "dimensional_flows_scale_x10": abs(o2["Q"] / o1["Q"] - 10.0) <= 1e-12,
            "dimensionless_invariant": (abs(o2["R"] - o1["R"]) <= 1e-12
                                        and abs(o2["s"] - o1["s"]) <= 1e-12
                                        and abs(i2["Xi_hat"] - i1["Xi_hat"]) <= 1e-9 * max(1.0, Xi)),
        })
    return {"rows": out, "passes": all(r["dimensional_flows_scale_x10"]
                                       and r["dimensionless_invariant"] for r in out)}


# ==========================================================================================
# Arm C — the minimum-observable test (load-bearing)
# ==========================================================================================

def arm_c_minimum_observable():
    """1. Q alone is confounded: for an observed R > 1 the exact solution set is the continuum
          {(c, Xi(c)) : sqrt(1 - 1/R) < |c| < 1}, BOTH signs of c admissible.
       2. Adding s collapses it, and the collapse is exact rather than numerical: along a
          fixed-R family the model satisfies  s - 1/2 = -(R - 1)/(2 R c)  identically, which is
          strictly monotone in c on each sign branch and sign-separated across them."""
    families = []
    for Xi_true in XI_SCENARIO_SET:
        o = observables_exact(A_PRIMARY, C_PRIMARY, Xi_true)
        R_obs, s_obs = o["R"], o["s"]
        c_min = math.sqrt(1.0 - 1.0 / R_obs)
        members = []
        for k in range(12):
            frac = (k + 1) / 13.0
            c_mag = c_min + (0.999 - c_min) * frac
            for sgn in (+1.0, -1.0):
                c_m = sgn * c_mag
                t_m = (1.0 - R_obs * (1.0 - c_m * c_m)) / (c_m * c_m)
                Xi_m = 1.0 / t_m - 1.0
                om = observables_exact(A_PRIMARY, c_m, Xi_m)
                members.append({
                    "c": c_m, "Xi": Xi_m,
                    "R_reproduced": om["R"], "R_abs_err": abs(om["R"] - R_obs),
                    "reproduces_R": abs(om["R"] - R_obs) <= 1e-9 * max(1.0, R_obs),
                    "s": om["s"], "s_matches_observed": abs(om["s"] - s_obs) <= 1e-9,
                    "identity_s_minus_half": -(R_obs - 1.0) / (2.0 * R_obs * c_m),
                })
        # exact identity check along the family
        id_err = max(abs((m["s"] - 0.5) - m["identity_s_minus_half"]) for m in members)
        pos = sorted([m for m in members if m["c"] > 0], key=lambda m: m["c"])
        neg = sorted([m for m in members if m["c"] < 0], key=lambda m: m["c"])
        mono_pos = all(pos[k + 1]["s"] > pos[k]["s"] for k in range(len(pos) - 1))
        mono_neg = all(neg[k + 1]["s"] > neg[k]["s"] for k in range(len(neg) - 1))
        sign_sep = (max(m["s"] for m in pos) < 0.5 < min(m["s"] for m in neg))
        n_match = sum(1 for m in members if m["s_matches_observed"])
        families.append({
            "Xi_true": Xi_true, "c_true": C_PRIMARY, "R_observed": R_obs, "s_observed": s_obs,
            "c_magnitude_lower_bound": c_min,
            "n_family_members": len(members),
            "all_members_reproduce_R": all(m["reproduces_R"] for m in members),
            "max_R_abs_err_in_family": max(m["R_abs_err"] for m in members),
            "n_members_also_matching_s": n_match,
            "s_identity_max_abs_err": id_err,
            "s_strictly_monotone_in_c_positive_branch": mono_pos,
            "s_strictly_monotone_in_c_negative_branch": mono_neg,
            "s_sign_separates_the_two_branches": sign_sep,
            "members": members,
        })
    return {
        "claim_stated_exactly": "When the signed axial contrast c is NOT independently known, "
                                "total flow alone cannot JOINTLY identify (c, Xi); adding the "
                                "separate outlet share identifies both in the exact nondegenerate "
                                "mirror design.",
        "not_the_claim": "'Total flow alone is not enough' without that qualifier is wrong: if a "
                         "nonzero mirror c IS independently known, R alone identifies Xi (see "
                         "observable_hierarchy).",
        "Q_only_is_confounded": all(f["all_members_reproduce_R"] and f["n_family_members"] > 1
                                    for f in families),
        "Q_only_confounding_is_for_JOINT_inference_of_c_and_Xi": True,
        "Q_plus_share_is_unique": all(f["n_members_also_matching_s"] == 0
                                      and f["s_strictly_monotone_in_c_positive_branch"]
                                      and f["s_strictly_monotone_in_c_negative_branch"]
                                      and f["s_sign_separates_the_two_branches"]
                                      for f in families),
        "exact_identity": "s - 1/2 = -(R - 1) / (2 R c) holds identically along any fixed-R "
                          "family, so s determines c given R, and (c, Xi) follows.",
        "R_depends_on_c_only_through_c_squared": True,
        "observable_hierarchy": _observable_hierarchy(),
        "note": "A continuum of distinct (c, Xi) states -- of BOTH signs of c -- reproduces one "
                "R exactly. None of them reproduces the observed s. The extra measurement is "
                "demonstrated necessary from the observables, NOT asserted from the model having "
                "an internal state.",
        "families": families,
    }


def _observable_hierarchy():
    """What each information state buys. Four rungs, each demonstrated on the exact model."""
    Xi_true = 0.75
    o = observables_exact(A_PRIMARY, C_PRIMARY, Xi_true)
    # rung 1 -- c known and nonzero: R alone inverts, since R = (1 - c^2 t)/(1 - c^2)
    t_from_R = (1.0 - o["R"] * (1.0 - C_PRIMARY ** 2)) / (C_PRIMARY ** 2)
    Xi_from_R_only = 1.0 / t_from_R - 1.0
    # rung 2 -- c unknown, mirror construction assumed: R + s invert
    inv = invert(o["R"], o["s"])
    # rung 3 -- four calibrated nondegenerate axials: pressure-normalised total flow inverts
    cal = invert_G_from_known_axials(o["g"], o["R"])
    return [
        {"rung": 1, "known": "the mirror contrast c, independently and nonzero",
         "observables": ["R"], "identifies": ["Xi"],
         "demonstrated_Xi_hat": Xi_from_R_only,
         "rel_err": abs(Xi_from_R_only - Xi_true) / Xi_true,
         "note": "R alone IS sufficient here. This is why the confounding claim must always "
                 "carry its 'c not independently known' qualifier."},
        {"rung": 2, "known": "only that the fixture is built as an exact mirror",
         "observables": ["R", "s"], "identifies": ["c", "Xi"],
         "demonstrated_c_hat": inv["c_hat"], "demonstrated_Xi_hat": inv["Xi_hat"],
         "rel_err": abs(inv["Xi_hat"] - Xi_true) / Xi_true,
         "note": "the frozen primary result."},
        {"rung": 3, "known": "all four axial conductances, independently calibrated, "
                             "NONDEGENERATE (g1_top*g2_bot != g2_top*g1_bot)",
         "observables": ["pressure-normalised total flow (Q/dP), open and blocked"],
         "identifies": ["G_lat"],
         "demonstrated_G_lat_hat": cal["G_lat_hat"],
         "rel_err": abs(cal["G_lat_hat"] - o["G_lat"]) / o["G_lat"],
         "note": "no symmetry assumed; fails structurally when the cross product X = 0."},
        {"rung": 4, "known": "nothing beyond the boundary measurements (general geometry)",
         "observables": ["q1, q2 blocked", "q1, q2 open"], "identifies": [],
         "note": "INSUFFICIENT. 5 unknowns, 4 boundary numbers; a one-parameter family spanning "
                 "x8 in Xi matches all four exactly (see the counting diagnostic)."},
    ]


# ==========================================================================================
# Arm D — existing physical-vs-proxy adversary, reused
# ==========================================================================================

def arm_d_proxy_adversary():
    """Calls lcd.physical_row on the harness's own isoresistive_mirror case. The proxy gets its
    strongest admissible CONTINUOUS alpha fit as that module computes it. No alpha=f(Xi) map."""
    case = [c for c in lcd.CASES if c.case_id == "isoresistive_mirror"][0]
    gax = lc.g_axial_reference(*case.g)
    rows = []
    for Xi in XI_SCENARIO_SET:
        G = g_lat_from_xi(case.g1_top + case.g1_bot, Xi)
        Lambda = G / gax
        r = lcd.physical_row(case, Lambda)
        rows.append({
            "Xi_requested": Xi, "Xi_reported_by_harness": r["Xi"],
            "lambda_used_only_as_harness_input": Lambda,
            "Q_over_Q0": r["Q_over_Q0"], "outlet_share_1": r["outlet_share_1"],
            "uncoupled_proxy_share_1": r["uncoupled_proxy_share_1"],
            "proxy_share_alpha_invariant": r["proxy_share_alpha_invariant"],
            "alpha_star_continuous": r["alpha_star_continuous"],
            "continuous_share_match_possible": r["continuous_share_match_possible"],
            "completion_Q_matchable": r["completion_Q_matchable"],
            "joint_match_possible": r["joint_match_possible"],
            "mathematically_distinguishable": r["mathematically_distinguishable"],
        })
    return {
        "comparator": "analysis.lateral_proxy.frozen_two_path_proxy via "
                      "analysis.lateral_coupling_discrimination.physical_row (CALLED, not "
                      "reimplemented). It is the frozen UNCOUPLED share-proxy completion, NOT "
                      "the complete dynamic streamtube model.",
        "no_alpha_to_Xi_law_invented": True,
        "no_proxy_reproduces_joint_signature": all(r["mathematically_distinguishable"]
                                                   for r in rows),
        "why": "For the mirror the uncoupled proxy share s0 is exactly 0.5, so s_proxy(alpha) = "
               "0.5 for EVERY alpha; and the frozen completion holds Q/Q0 = 1 while physical "
               "coupling raises it. The proxy misses BOTH observables at once, structurally.",
        "rows": rows,
    }


# ==========================================================================================
# Arm E — controls
# ==========================================================================================

def arm_e_controls():
    # 1. identical paths (c = 0)
    ident = []
    for Xi in XI_SCENARIO_SET:
        o = observables_exact(A_PRIMARY, 0.0, Xi)
        inv = invert(o["R"], o["s"])
        ident.append({"Xi": Xi, "R": o["R"], "s": o["s"],
                      "q_lat_1to2": o["open"]["q_lat_1to2"],
                      "pressure_gap": abs(o["open"]["p1"] - o["open"]["p2"]),
                      "inverse_status": inv["status"], "Xi_hat": inv["Xi_hat"]})
    # 2. path swap  c -> -c
    swap = []
    for Xi in XI_SCENARIO_SET:
        a = observables_exact(A_PRIMARY, C_PRIMARY, Xi)
        b = observables_exact(A_PRIMARY, -C_PRIMARY, Xi)
        ia, ib = invert(a["R"], a["s"]), invert(b["R"], b["s"])
        swap.append({
            "Xi": Xi,
            "R_preserved": abs(a["R"] - b["R"]) <= 1e-12,
            "R_delta": abs(a["R"] - b["R"]),
            "share_departure_reverses_sign": abs((a["s"] - 0.5) + (b["s"] - 0.5)) <= 1e-12,
            "s_forward": a["s"], "s_swapped": b["s"],
            "c_hat_reverses": abs(ia["c_hat"] + ib["c_hat"]) <= 1e-9,
            "c_hat_forward": ia["c_hat"], "c_hat_swapped": ib["c_hat"],
            "Xi_hat_unchanged": abs(ia["Xi_hat"] - ib["Xi_hat"]) <= 1e-9 * max(1.0, Xi),
            "Xi_hat_forward": ia["Xi_hat"], "Xi_hat_swapped": ib["Xi_hat"],
        })
    # 4/5. zero- and strong-coupling limits
    zero = observables_exact(A_PRIMARY, C_PRIMARY, 0.0)
    zero_inv = invert(zero["R"], zero["s"])
    g = mirror_conductances(A_PRIMARY, C_PRIMARY)
    lim = lc.strong_coupling_limit(P_IN, *g)
    XI_STRONG = 1e6                     # see conditioning probe below for why not 1e12
    big = lc.model1_two_path(P_IN, *g, g_lat_from_xi(A_PRIMARY, XI_STRONG))
    R_sat_analytic = 1.0 + C_PRIMARY ** 2 / (1.0 - C_PRIMARY ** 2)
    s_sat_analytic = (1.0 - C_PRIMARY) / 2.0
    o_big = observables_exact(A_PRIMARY, C_PRIMARY, XI_STRONG)
    # 6. conservation and canonical sign
    cons = []
    for c in (-0.9, -0.5, 0.1, C_PRIMARY, 0.9):
        for Xi in XI_SCENARIO_SET:
            o = observables_exact(A_PRIMARY, c, Xi)
            r = o["open"]
            cons.append({"c": c, "Xi": Xi,
                         "node1_residual": r["node1_residual"],
                         "node2_residual": r["node2_residual"],
                         "global_residual": r["global_residual"],
                         "q_lat_1to2": r["q_lat_1to2"],
                         "p1_minus_p2": r["p1"] - r["p2"],
                         "sign_convention_holds":
                             (r["q_lat_1to2"] > 0) == (r["p1"] - r["p2"] > 0)
                             or abs(r["q_lat_1to2"]) <= 1e-9})
    max_res = max(max(abs(x["node1_residual"]), abs(x["node2_residual"]),
                      abs(x["global_residual"])) for x in cons)
    return {
        "identical_paths_negative_control": {
            "rows": ident,
            "reports_no_information": all(r["inverse_status"] == "degenerate_no_information"
                                          and r["Xi_hat"] is None for r in ident),
            "no_lateral_flow": all(abs(r["q_lat_1to2"]) <= 1e-9 for r in ident),
        },
        "path_swap": {"rows": swap,
                      "passes": all(r["R_preserved"] and r["share_departure_reverses_sign"]
                                    and r["c_hat_reverses"] and r["Xi_hat_unchanged"]
                                    for r in swap)},
        "zero_coupling_limit": {
            "R": zero["R"], "s": zero["s"], "inverse_status": zero_inv["status"],
            "Xi_hat": zero_inv["Xi_hat"],
            "correctly_reports_no_information":
                zero_inv["status"] == "degenerate_no_information" and zero_inv["Xi_hat"] is None,
        },
        "strong_coupling_limit": {
            "Xi_evaluated": XI_STRONG,
            "Q_inf_from_model_limit": lim["Q_inf"], "Q_at_Xi": big["Q"],
            "matches_analytic_limit": abs(big["Q"] - lim["Q_inf"]) <= 1e-5 * abs(lim["Q_inf"]),
            "R_saturation_analytic": R_sat_analytic, "R_at_Xi": o_big["R"],
            "s_saturation_analytic": s_sat_analytic, "s_at_Xi": o_big["s"],
            # The residual at finite Xi is the PHYSICAL O(1/Xi) approach to saturation, not
            # numerical error, so it is checked against its exact closed form rather than 0:
            #   R_sat - R = c^2/((1-c^2)(1+Xi));  s - s_sat = c(1-c^2)/(2(1+Xi-c^2))
            "R_approach_exact": C_PRIMARY ** 2 / ((1 - C_PRIMARY ** 2) * (1 + XI_STRONG)),
            "R_approach_observed": R_sat_analytic - o_big["R"],
            "s_approach_exact": (C_PRIMARY * (1 - C_PRIMARY ** 2)
                                 / (2 * (1 + XI_STRONG - C_PRIMARY ** 2))),
            "s_approach_observed": o_big["s"] - s_sat_analytic,
            "saturation_matches": (
                abs((R_sat_analytic - o_big["R"])
                    - C_PRIMARY ** 2 / ((1 - C_PRIMARY ** 2) * (1 + XI_STRONG))) <= 1e-12
                and abs((o_big["s"] - s_sat_analytic)
                        - C_PRIMARY * (1 - C_PRIMARY ** 2)
                        / (2 * (1 + XI_STRONG - C_PRIMARY ** 2))) <= 1e-12),
        },
        "numerical_conditioning_of_the_existing_model": _conditioning_probe(),
        "conservation_and_sign": {"rows": cons, "max_abs_residual": max_res,
                                  "passes": max_res <= 1e-6
                                  and all(x["sign_convention_holds"] for x in cons)},
    }


def _conditioning_probe():
    """Where does the EXISTING model's float arithmetic stop reproducing the analytic map?

    model1_two_path forms det = a*d - G_lat^2 with a = d = A + G_lat. For G_lat >> A this is a
    catastrophic cancellation: the leading G_lat^2 terms cancel and only 2*A*G_lat + A^2 should
    survive, so roughly log10(G_lat/A) significant digits are lost. This is a NUMERICAL property
    of the implementation, not a physical defect and not a model error. The probe records where
    the loss becomes visible so the screen can state that its own grid sits well inside the
    sound region.
    """
    rows, first_bad = [], None
    for e in range(0, 15):
        Xi = 10.0 ** e
        o = observables_exact(A_PRIMARY, C_PRIMARY, Xi)
        R_a, s_a = forward_map_analytic(C_PRIMARY, Xi)
        err = max(abs(R_a - o["R"]) / abs(R_a), abs(s_a - o["s"]) / abs(s_a))
        rows.append({"Xi": Xi, "max_rel_deviation_from_analytic": err})
        if first_bad is None and err > 1e-9:
            first_bad = Xi
    return {
        "finding": "The exact-network solve loses ~log10(G_lat/A) significant digits to "
                   "cancellation in det = a*d - G_lat^2 as G_lat grows. It is a floating-point "
                   "conditioning limit of models.lateral_coupling.model1_two_path, NOT a physical "
                   "defect, NOT a model error, and it is not a defect that invalidates this "
                   "screen's inference.",
        "first_Xi_with_rel_deviation_above_1e_9": first_bad,
        "screen_grid_max_Xi": max(XI_GRID),
        "screen_grid_is_inside_the_sound_region": bool(first_bad is None
                                                       or max(XI_GRID) < first_bad),
        "rows": rows,
    }


# ==========================================================================================
# Arm F — mirror-imperfection adversarial check
# ==========================================================================================

def arm_f_mirror_imperfection():
    nominal = mirror_conductances(A_PRIMARY, C_PRIMARY)
    levels = []
    for d in PERTURB_LEVELS:
        corners = []
        for mask in range(16):
            signs = [(+1.0 if (mask >> k) & 1 else -1.0) for k in range(4)]
            gp = tuple(nominal[k] * (1.0 + signs[k] * d) for k in range(4))
            A1, A2 = gp[0] + gp[1], gp[2] + gp[3]
            per_xi = []
            for Xi_nom in XI_SCENARIO_SET:
                G = g_lat_from_xi(A_PRIMARY, Xi_nom)          # the SAME physical bridge
                Xi_true = lc.equalization_number(G, *gp)      # the model's exact Xi for THIS geometry
                open_ = lc.model1_two_path(P_IN, *gp, G)
                blocked = lc.model1_two_path(P_IN, *gp, 0.0)
                q1, q2, Q0 = open_["q1"], open_["q2"], blocked["Q"]
                Q = q1 + q2
                R, s = Q / Q0, q1 / Q
                s0_blocked = blocked["q1"] / Q0     # POST-HOC DIAGNOSTIC (see below)
                inv = invert(R, s)                            # IDEAL MIRROR inverse, misapplied
                cal = invert_G_from_known_axials(gp, R)       # calibrated-axials inversion
                bis = _bisect_G(gp, Q)
                Xi_cal = (lc.equalization_number(cal["G_lat_hat"], *gp)
                          if cal["G_lat_hat"] is not None and cal["G_lat_hat"] >= 0 else None)
                per_xi.append({
                    "Xi_nominal": Xi_nom, "Xi_true_perturbed": Xi_true,
                    "R": R, "s": s, "s0_blocked": s0_blocked,
                    "blocked_share_departure": abs(s0_blocked - 0.5),
                    "mirror_inverse_status": inv["status"],
                    "Xi_hat_mirror": inv["Xi_hat"], "c_hat_mirror": inv["c_hat"],
                    "Xi_bias_rel_mirror": (None if inv["Xi_hat"] is None
                                           else (inv["Xi_hat"] - Xi_true) / Xi_true),
                    "c_bias_abs_mirror": (None if inv["c_hat"] is None
                                          else inv["c_hat"] - C_PRIMARY),
                    "G_lat_true": G,
                    "G_lat_hat_calibrated": cal["G_lat_hat"],
                    "G_lat_calibrated_rel_err": (None if cal["G_lat_hat"] is None
                                                 else abs(cal["G_lat_hat"] - G) / G),
                    "G_lat_hat_bisection": bis,
                    "bisection_agrees": (bis is not None and cal["G_lat_hat"] is not None
                                         and abs(bis - cal["G_lat_hat"]) <= 1e-6 * max(1.0, G)),
                    "Xi_hat_calibrated": Xi_cal,
                    "Xi_calibrated_rel_err": (None if Xi_cal is None
                                              else abs(Xi_cal - Xi_true) / Xi_true),
                })
            corners.append({"signs": signs, "g_perturbed": list(gp), "rows": per_xi})
        flat = [r for cn in corners for r in cn["rows"]]
        mir = [abs(r["Xi_bias_rel_mirror"]) for r in flat if r["Xi_bias_rel_mirror"] is not None]
        cal = [r["Xi_calibrated_rel_err"] for r in flat if r["Xi_calibrated_rel_err"] is not None]
        blk = [r["blocked_share_departure"] for r in flat]
        levels.append({
            "perturbation_level": d,
            "n_corners": len(corners), "n_rows": len(flat),
            "blocked_share_departure_max": max(blk),
            "blocked_share_departure_min": min(blk),
            "n_corners_with_blocked_share_exactly_half": sum(1 for x in blk if x <= 1e-12),
            "blocked_share_flags_exactly_the_biasing_corners": all(
                (r["blocked_share_departure"] <= 1e-12)
                == (abs(r["Xi_bias_rel_mirror"]) <= 1e-12)
                for r in flat if r["Xi_bias_rel_mirror"] is not None),
            "n_corners_still_exact_mirrors": sum(
                1 for cn in corners
                if abs(cn["g_perturbed"][0] - cn["g_perturbed"][3]) <= 1e-12
                and abs(cn["g_perturbed"][1] - cn["g_perturbed"][2]) <= 1e-12),
            "mirror_inverse_max_abs_Xi_rel_bias": max(mir) if mir else None,
            "mirror_inverse_median_abs_Xi_rel_bias": float(np.median(mir)) if mir else None,
            "mirror_inverse_max_abs_c_bias": max(abs(r["c_bias_abs_mirror"]) for r in flat
                                                 if r["c_bias_abs_mirror"] is not None),
            "mirror_inverse_n_nonphysical": sum(1 for r in flat
                                                if r["mirror_inverse_status"] != "ok"),
            "calibrated_max_Xi_rel_err": max(cal) if cal else None,
            "calibrated_all_exact": bool(cal and max(cal) <= 1e-9),
            "bisection_cross_check_passes": all(r["bisection_agrees"] for r in flat),
            "worst_bias_by_Xi": {
                str(x): max([abs(r["Xi_bias_rel_mirror"]) for r in flat
                             if r["Xi_nominal"] == x and r["Xi_bias_rel_mirror"] is not None]
                            or [None])
                for x in XI_SCENARIO_SET},
            "corners": corners,
        })
    return {
        "alternative_explanation": "The inverse is an artifact of exact mirror symmetry and will "
                                   "return a misleading Xi when a real apparatus is only "
                                   "approximately mirrored.",
        "perturbation_design": "Deterministic 16 sign corners of (a,b,b,a)*(1 +/- delta) at each "
                               "level. NOT a random sample.",
        "levels_are_sensitivity_scenarios_not_manufacturing_tolerances": True,
        "three_things_distinguished": {
            "structural_identifiability_of_the_ideal_design": "Arm B — exact in the designed "
                                                              "geometry.",
            "bias_from_assuming_unverified_symmetry": "This arm — the ideal mirror inverse "
                                                      "applied to a geometry that is not one.",
            "recoverability_with_calibrated_axial_segments": "invert_G_from_known_axials — exact "
                                                             "for any NONDEGENERATE calibrated "
                                                             "geometry having a nonzero uncoupled "
                                                             "mid-node pressure gap "
                                                             "(g1_top*g2_bot != g2_top*g1_bot). "
                                                             "No mirror symmetry is assumed, but "
                                                             "this is NOT 'any geometry' — see "
                                                             "calibrated_inversion_degeneracy.",
        },
        "calibrated_inversion_degeneracy": _calibrated_degeneracy(),
        "levels": levels,
        "post_hoc_diagnostics": {
            "label": "POST_HOC_DIAGNOSTIC_NOT_IN_DECISION",
            "why_reported": "Neither of these feeds any clause of the frozen decision rule, and "
                            "neither was used to select a threshold. They are reported because "
                            "the decisive-experiment specification would be misleading without "
                            "them: they bound WHERE the licensed claim applies.",
            "blocked_bridge_outlet_share": {
                "observation": "With the bridge BLOCKED the two outlet flows are separately "
                               "measurable, and s0 = q1_blocked/Q0 is exactly 0.5 for a true "
                               "mirror. Every perturbed corner at every level departs from 0.5, "
                               "so this is a direct pre-test of the symmetry the ideal inverse "
                               "assumes -- taken with the SAME fixture, before any coupled run.",
                "departure_by_level": {str(lv["perturbation_level"]):
                                       {"max": lv["blocked_share_departure_max"],
                                        "min": lv["blocked_share_departure_min"],
                                        "n_rows_indistinguishable_from_mirror":
                                            lv["n_corners_with_blocked_share_exactly_half"],
                                        "n_corners_still_exact_mirrors":
                                            lv["n_corners_still_exact_mirrors"],
                                        "flags_exactly_the_biasing_corners":
                                            lv["blocked_share_flags_exactly_the_biasing_corners"]}
                                       for lv in levels},
                "on_this_corner_set": "At every level the 4 of 16 sign corners that remain EXACT "
                                      "mirrors (g1_top = g2_bot, g1_bot = g2_top) are precisely "
                                      "the 4 with zero blocked-share departure AND zero Xi bias; "
                                      "all 12 that break the mirror show both. On this corner "
                                      "set the test is exact -- but see the counting diagnostic "
                                      "below, which exhibits a whole family it cannot see.",
            },
            "unconstrained_geometry_non_identifiability": _post_hoc_counting(),
        },
    }


def _calibrated_degeneracy():
    """The structural exception to the calibrated-axials route, demonstrated rather than asserted.

    CORRECTION (2026-08-09): an earlier wording claimed the calibrated inversion recovers G_lat
    for "any geometry". That is false in exactly one structural case, recorded here.
    """
    rows = []
    for label, g in (("mirror_primary", (3.0, 1.0, 1.0, 3.0)),
                     ("asymmetric_nondegenerate", (4.0, 0.8, 1.5, 2.5)),
                     ("proportional_paths_degenerate", (2.0, 1.0, 4.0, 2.0)),
                     ("proportional_paths_degenerate_2", (1.0, 3.0, 2.0, 6.0)),
                     ("near_degenerate_resolved", (2.0, 1.0, 4.0, 2.02)),
                     ("near_degenerate_unresolved", (2.0, 1.0, 4.0, 2.000001))):
        X = cross_product_gap_driver(g)
        blocked = lc.model1_two_path(P_IN, *g, 0.0)
        gap0 = abs(blocked["p1"] - blocked["p2"])
        qs, invs = [], []
        for G in (0.0, 0.5, 5.0, 500.0):
            r = lc.model1_two_path(P_IN, *g, G)
            qs.append(r["Q"])
            cal = invert_G_from_known_axials(g, r["Q"] / blocked["Q"])
            invs.append({"G_lat_true": G, "status": cal["status"],
                         "G_lat_hat": cal["G_lat_hat"],
                         "rel_err": (None if cal["G_lat_hat"] is None or G == 0.0
                                     else abs(cal["G_lat_hat"] - G) / G)})
        q_span = (max(qs) - min(qs)) / max(qs)
        rows.append({
            "label": label, "g": list(g),
            "cross_product_X": X, "dQdG_numerator": dQdG_numerator(g),
            "identity_holds": abs(dQdG_numerator(g) - X * X) <= 1e-9 * max(1.0, X * X),
            "uncoupled_mid_node_gap": gap0,
            "Q_relative_span_over_G_lat": q_span,
            "Q_exactly_independent_of_G_lat": q_span == 0.0,
            # THREE classes, never two. structurally_degenerate is EXACT (X == 0); a small
            # nonzero X is mathematically injective but numerically unresolved here.
            "structurally_degenerate": X == 0.0,
            "numerically_unresolved": (X != 0.0
                                       and X * X <= _NUMERICAL_RESOLUTION_REL
                                       * (blocked_A1A2 := (g[0] + g[1]) * (g[2] + g[3])) ** 2),
            "mathematically_injective": X != 0.0,
            "inversions": invs,
        })
    return {
        "correction_note": "An earlier wording of this screen claimed the calibrated-axials "
                           "inversion recovers G_lat for 'any geometry'. That is FALSE in one "
                           "structural case and is corrected here. The valid statement is: any "
                           "NONDEGENERATE calibrated geometry having a nonzero uncoupled mid-node "
                           "pressure gap.",
        "derivative_identity": "d(Q/P)/dG = [M*A1*A2 - N0*S]/(A1*A2 + G*S)^2 "
                               "= (g1_top*g2_bot - g2_top*g1_bot)^2 / (A1*A2 + G*S)^2",
        "nondegeneracy_condition": "g1_top*g2_bot != g2_top*g1_bot",
        "equivalent_physical_condition": "the two UNCOUPLED mid-node pressures differ, so a "
                                         "lateral pressure exists to drive the bridge",
        "monotonicity": "the derivative is a SQUARE, so Q is non-decreasing in G_lat for every "
                        "admissible geometry; it is STRICTLY increasing iff X != 0",
        "conditioning": "dG/d(Q/P) ~ 1/X^2, so the inversion degrades continuously as X -> 0; "
                        "the near_degenerate row shows this rather than asserting it",
        "three_classes_never_two": {
            "structural_no_information": "X == 0 EXACTLY. Uncoupled mid-node pressures equal; Q "
                                         "exactly independent of G_lat. The ONLY structural case.",
            "numerically_unresolved": "X != 0, so the map is mathematically INJECTIVE and Q is "
                                      "NOT independent of G_lat -- but this implementation "
                                      "declines to return a number because dG/d(Q/P) ~ 1/X^2 is "
                                      "too ill-conditioned. A limit of the arithmetic, not of "
                                      "the mathematics.",
            "resolved": "the exact inversion runs unchanged.",
        },
        "identity_verified_on_all_rows": all(r["identity_holds"] for r in rows),
        "structurally_degenerate_rows_report_no_information": all(
            all(i["status"] == "structurally_degenerate_no_information" for i in r["inversions"])
            for r in rows if r["structurally_degenerate"]),
        "numerically_unresolved_rows_report_that_and_not_degeneracy": all(
            all(i["status"] == "numerically_unresolved_near_degenerate" for i in r["inversions"])
            for r in rows if r["numerically_unresolved"]),
        "no_row_is_both": not any(r["structurally_degenerate"] and r["numerically_unresolved"]
                                  for r in rows),
        # the resolved-but-near-degenerate row is EXCLUDED from the exactness aggregate on
        # purpose: it exists to show the 1/X^2 conditioning decay, and lumping it in would hide it
        "well_conditioned_rows_recover_exactly": all(
            all(i["rel_err"] is None or i["rel_err"] <= 1e-9 for i in r["inversions"])
            for r in rows if not r["structurally_degenerate"] and not r["numerically_unresolved"]
            and r["label"] != "near_degenerate_resolved"),
        "near_degenerate_conditioning_decay": {
            "row": "near_degenerate_resolved",
            "X": next(r["cross_product_X"] for r in rows
                      if r["label"] == "near_degenerate_resolved"),
            "max_rel_err": max(
                i["rel_err"] for r in rows if r["label"] == "near_degenerate_resolved"
                for i in r["inversions"] if i["rel_err"] is not None),
            "well_conditioned_max_rel_err": max(
                [i["rel_err"] for r in rows
                 if not r["structurally_degenerate"] and not r["numerically_unresolved"]
                 and r["label"] != "near_degenerate_resolved"
                 for i in r["inversions"] if i["rel_err"] is not None] or [0.0]),
            "interpretation": "X drops from 8 to 0.04 (X^2 by ~4e4) and the recovery error grows "
                              "by a comparable factor. The inversion does not fail abruptly at "
                              "X = 0; it degrades continuously as 1/X^2, which is why a real "
                              "fixture needs a MARGIN on the uncoupled mid-node pressure gap, "
                              "not merely a nonzero one.",
        },
        "rows": rows,
    }


def _post_hoc_counting():
    """POST_HOC_DIAGNOSTIC_NOT_IN_DECISION.

    Parameter counting for an apparatus whose geometry is NOT assumed mirrored. Unknowns:
    g1t, g1b, g2t, g2b, G_lat = 5. Boundary numbers at known P_in: q1_blocked, q2_blocked,
    q1_open, q2_open = 4. Generically 1-dimensionally deficient -- so boundary flows alone do
    NOT identify Xi for an arbitrary two-lane apparatus.

    Demonstrated, not asserted: the blocked run fixes only the two end-to-end SERIES
    conductances, leaving each lane's top/bottom split free. Parameterising lane i by
    u_i = g_series_i / g_it (so g_it = g_series_i/u_i, g_ib = g_series_i/(1-u_i)), we scan u1,
    solve u2 by bisection so the open-run share matches, take G_lat from the exact
    known-axials inversion so the open-run total matches, and report the resulting Xi.
    """
    Xi_ref = 0.75
    g_ref = mirror_conductances(A_PRIMARY, C_PRIMARY)
    G_ref = g_lat_from_xi(A_PRIMARY, Xi_ref)
    open_ref = lc.model1_two_path(P_IN, *g_ref, G_ref)
    blk_ref = lc.model1_two_path(P_IN, *g_ref, 0.0)
    gs1 = lc.g_series(g_ref[0], g_ref[1])
    gs2 = lc.g_series(g_ref[2], g_ref[3])
    Q_ref, Q0_ref = open_ref["q1"] + open_ref["q2"], blk_ref["Q"]
    R_ref, s_ref = Q_ref / Q0_ref, open_ref["q1"] / Q_ref

    def build(u1, u2):
        return (gs1 / u1, gs1 / (1.0 - u1), gs2 / u2, gs2 / (1.0 - u2))

    def s_of(u1, u2):
        g = build(u1, u2)
        cal = invert_G_from_known_axials(g, R_ref)
        if cal["G_lat_hat"] is None or cal["G_lat_hat"] < 0.0:
            return None, None, None
        r = lc.model1_two_path(P_IN, *g, cal["G_lat_hat"])
        return r["q1"] / (r["q1"] + r["q2"]), cal["G_lat_hat"], g

    sols = []
    for u1 in (0.20, 0.225, 0.25, 0.275, 0.30):
        # deterministic coarse scan over the ADMISSIBLE u2 (where G_lat >= 0), then bisect the
        # first sign change. A narrower a-priori bracket misses the family entirely.
        scan = []
        for k in range(1, 200):
            f = s_of(u1, k / 200.0)[0]
            scan.append((k / 200.0, None if f is None else f - s_ref))
        # ONLY adjacent admissible grid points may form a bracket. Pairing across a gap in the
        # admissible (G_lat >= 0) region manufactures a sign change that is not a root.
        br = next(((scan[k][0], scan[k + 1][0]) for k in range(len(scan) - 1)
                   if scan[k][1] is not None and scan[k + 1][1] is not None
                   and scan[k][1] * scan[k + 1][1] <= 0.0), None)
        if br is None:
            continue
        lo, hi = br
        f_lo = s_of(u1, lo)[0] - s_ref
        f_hi = s_of(u1, hi)[0] - s_ref
        if abs(f_lo) <= 1e-15:                 # the scan landed exactly on the root
            u2 = lo
        elif abs(f_hi) <= 1e-15:
            u2 = hi
        else:
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                r_mid = s_of(u1, mid)
                if r_mid[0] is None:
                    break
                fm = r_mid[0] - s_ref
                if fm == 0.0:
                    lo = hi = mid
                    break
                if fm * f_lo < 0.0:
                    hi = mid
                else:
                    lo, f_lo = mid, fm
            u2 = 0.5 * (lo + hi)
        s_got, G_got, g_got = s_of(u1, u2)
        if s_got is None:
            continue
        rr = lc.model1_two_path(P_IN, *g_got, G_got)
        bb = lc.model1_two_path(P_IN, *g_got, 0.0)
        sols.append({
            "u1": u1, "u2": u2, "g": list(g_got), "G_lat": G_got,
            "Xi": lc.equalization_number(G_got, *g_got),
            "blocked_outlet_share": bb["q1"] / bb["Q"],
            "q1_blocked_err": abs(bb["q1"] - blk_ref["q1"]),
            "q2_blocked_err": abs(bb["q2"] - blk_ref["q2"]),
            "q1_open_err": abs(rr["q1"] - open_ref["q1"]),
            "q2_open_err": abs(rr["q2"] - open_ref["q2"]),
        })
    tol = 1e-6 * Q_ref
    matching = [x for x in sols if max(x["q1_blocked_err"], x["q2_blocked_err"],
                                       x["q1_open_err"], x["q2_open_err"]) <= tol]
    xis = [x["Xi"] for x in matching]
    return {
        "label": "POST_HOC_DIAGNOSTIC_NOT_IN_DECISION",
        "unknowns": 5, "boundary_numbers": 4, "generic_deficiency": 1,
        "reference": {"Xi": Xi_ref, "R": R_ref, "s": s_ref,
                      "conductances": list(g_ref)},
        "match_tolerance_abs_flow": tol,
        "n_solutions_found": len(matching),
        "Xi_range_over_matching_solutions": [min(xis), max(xis)] if xis else None,
        "Xi_spread_factor": (max(xis) / min(xis)) if xis and min(xis) > 0 else None,
        "all_solutions_have_blocked_share_one_half": all(
            abs(x["blocked_outlet_share"] - 0.5) <= 1e-12 for x in matching),
        "solutions": matching,
        "conclusion": "A one-parameter family of DIFFERENT geometries, each with a different Xi, "
                      "reproduces all four boundary flows exactly. Boundary flows alone therefore "
                      "do NOT identify Xi for an arbitrary two-lane apparatus. The mirror "
                      "CONSTRUCTION is what closes the system -- and it is a design assumption "
                      "about the fixture, not a measurement of k_lat or w.",
        "and_the_blocked_share_test_does_not_catch_this_family": "Every member holds the two "
            "end-to-end SERIES conductances equal, so the blocked-bridge outlet share is exactly "
            "0.5 for all of them. The blocked share tests lane BALANCE, not the top/bottom SPLIT "
            "arrangement, which no blocked measurement can see. So the blocked-run share is a "
            "NECESSARY but NOT SUFFICIENT check on the mirror assumption: the split must be "
            "controlled by construction (layer depths and materials built to the same nominal "
            "values), not verified after the fact from boundary flows.",
    }


# ==========================================================================================
# §7 — practical resolution scenarios (hypothetical; NOT an instrument model)
# ==========================================================================================

def sensitivity_envelopes():
    rows = []
    c = C_PRIMARY
    for Xi in XI_LOG_GRID:
        o = observables_exact(A_PRIMARY, c, Xi)
        R, s, q1, q2, Q0 = o["R"], o["s"], o["q1"], o["q2"], o["Q0"]
        dR = (c * c / (1.0 - c * c)) * Xi / (1.0 + Xi) ** 2
        ds = -(c / 2.0) * Xi * (1.0 - c * c) / (1.0 + Xi - c * c) ** 2
        # central-difference cross-check of the closed-form derivatives. h = 1e-4 balances
        # O(h^2) truncation against the subtractive round-off floor of (R+ - R-) near R ~ 1;
        # at h = 1e-6 the round-off floor alone is ~1e-6 relative, which is why 1e-5 is the
        # right agreement tolerance for a DIFFERENCE QUOTIENT and not a claim about the model.
        h = 1e-4
        Rp, sp = forward_map_analytic(c, Xi * math.exp(h))
        Rm, sm = forward_map_analytic(c, Xi * math.exp(-h))
        scen = {}
        for f in PRECISION_FLOORS:
            hats, bad = [], 0
            for e1 in (-f, 0.0, f):
                for e2 in (-f, 0.0, f):
                    for e0 in (-f, 0.0, f):
                        Qp = q1 * (1 + e1) + q2 * (1 + e2)
                        Rp_ = Qp / (Q0 * (1 + e0))
                        sp_ = q1 * (1 + e1) / Qp
                        iv = invert(Rp_, sp_)
                        if iv["Xi_hat"] is None or iv["Xi_hat"] <= 0.0:
                            bad += 1
                        else:
                            hats.append(iv["Xi_hat"])
            lo = min(hats) if hats else None
            hi = max(hats) if hats else None
            within2 = bool(bad == 0 and lo is not None
                           and hi / Xi <= 2.0 and Xi / lo <= 2.0)
            scen["%dpct" % int(round(f * 100))] = {
                "floor": f, "n_scenario_points": 27, "n_nonphysical_or_undefined": bad,
                "Xi_hat_min": lo, "Xi_hat_max": hi,
                "Xi_hat_min_over_true": (lo / Xi) if lo else None,
                "Xi_hat_max_over_true": (hi / Xi) if hi else None,
                "recovered_within_factor_two": within2,
                "R_departure_exceeds_floor": abs(R - 1.0) > f,
                "share_departure_exceeds_floor": abs(s - 0.5) > f,
            }
        rows.append({"Xi": Xi, "R": R, "s": s,
                     "abs_R_minus_1": abs(R - 1.0), "abs_s_minus_half": abs(s - 0.5),
                     "dR_dlnXi": dR, "ds_dlnXi": ds,
                     "dR_dlnXi_numeric": (Rp - Rm) / (2 * h),
                     "ds_dlnXi_numeric": (sp - sm) / (2 * h),
                     "derivative_cross_check_ok": (abs(dR - (Rp - Rm) / (2 * h)) <= 1e-5 * max(1e-9, abs(dR))
                                                   and abs(ds - (sp - sm) / (2 * h)) <= 1e-5 * max(1e-9, abs(ds))),
                     "scenarios": scen})
    windows = {}
    for f in PRECISION_FLOORS:
        key = "%dpct" % int(round(f * 100))
        ok = [r["Xi"] for r in rows if r["scenarios"][key]["recovered_within_factor_two"]]
        drop = [r["Xi"] for r in rows if r["scenarios"][key]["n_nonphysical_or_undefined"] > 0]
        windows[key] = {"floor": f, "n_grid_points_recoverable": len(ok),
                        "Xi_min": min(ok) if ok else None, "Xi_max": max(ok) if ok else None,
                        "contiguous_on_grid": (bool(ok) and
                                               [r["Xi"] for r in rows
                                                if min(ok) <= r["Xi"] <= max(ok)] ==
                                               sorted(ok)),
                        # NO SILENT CAPS: the reported [Xi_hat_min, Xi_hat_max] interval spans
                        # only the scenario corners that returned a PHYSICAL inverse. Where
                        # corners returned none, the true spread is WORSE than the interval
                        # shown, so both the count and the affected Xi are recorded here and
                        # marked on the figure rather than dropped.
                        "n_grid_points_with_unrecoverable_corners": len(drop),
                        "Xi_with_unrecoverable_corners": drop,
                        "interval_is_optimistic_where_corners_were_dropped": bool(drop)}
    best = max(rows, key=lambda r: abs(r["ds_dlnXi"]))
    bestR = max(rows, key=lambda r: r["dR_dlnXi"])
    continuous = _post_hoc_window_boundaries()
    return {
        "these_are_hypothetical_resolution_scenarios": True,
        "not_instrument_accuracies": True,
        "not_experimental_uncertainty": True,
        "no_apparatus_feasibility_claim_is_earned": True,
        "scenario_definition": "Each independently measured flow (q1, q2, Q0) carries a relative "
                               "floor f. The perturbation set is the deterministic 3-level full "
                               "factorial {-f, 0, +f}^3 (27 points, containing the 8 sign corners "
                               "and the unperturbed point).",
        "case": {"A": A_PRIMARY, "c": C_PRIMARY, "conductances": list(mirror_conductances(A_PRIMARY, C_PRIMARY))},
        "peak_dR_dlnXi": {"Xi": bestR["Xi"], "value": bestR["dR_dlnXi"],
                          "analytic_peak_at_Xi": 1.0,
                          "analytic_peak_value": (C_PRIMARY ** 2 / (1 - C_PRIMARY ** 2)) / 4.0},
        "peak_abs_ds_dlnXi": {"Xi": best["Xi"], "value": best["ds_dlnXi"],
                              "analytic_peak_at_Xi": 1.0 - C_PRIMARY ** 2,
                              "analytic_peak_value": -C_PRIMARY / 8.0},
        "well_conditioned_windows": windows,
        "frozen_grid_note": "The frozen Xi grid has 22 nonzero points. A window's Xi_min/Xi_max "
                            "are the smallest and largest PASSING GRID POINTS -- they are NOT a "
                            "continuous boundary estimate and must never be quoted as one. The "
                            "continuous crossings are located separately in "
                            "continuous_window_post_hoc.",
        "continuous_window_post_hoc": continuous,
        "derivative_cross_check_passes": all(r["derivative_cross_check_ok"] for r in rows),
        "rows": rows,
    }


def _within_factor_two(Xi, f, c=C_PRIMARY, A=A_PRIMARY):
    """The frozen 27-corner rule evaluated at an ARBITRARY Xi -- same exact map, same inverse,
    same rule. Used only by the post-hoc boundary solve."""
    o = observables_exact(A, c, Xi)
    q1, q2, Q0 = o["q1"], o["q2"], o["Q0"]
    lo = hi = None
    for e1 in (-f, 0.0, f):
        for e2 in (-f, 0.0, f):
            for e0 in (-f, 0.0, f):
                Qp = q1 * (1 + e1) + q2 * (1 + e2)
                iv = invert(Qp / (Q0 * (1 + e0)), q1 * (1 + e1) / Qp)
                if iv["Xi_hat"] is None or iv["Xi_hat"] <= 0.0:
                    return False
                lo = iv["Xi_hat"] if lo is None else min(lo, iv["Xi_hat"])
                hi = iv["Xi_hat"] if hi is None else max(hi, iv["Xi_hat"])
    return bool(hi / Xi <= 2.0 and Xi / lo <= 2.0)


def _post_hoc_window_boundaries():
    """POST_HOC_DIAGNOSTIC_NOT_IN_DECISION.

    The frozen grid can only report WHICH OF 22 POINTS pass. This locates the continuous
    factor-of-two crossings with a bounded bisection in log10(Xi) over the same exact map,
    inverse and 27-corner rule. No new dependency, no new model, no new threshold. It feeds no
    clause of the frozen decision rule -- a test asserts that -- and the frozen grid result is
    reported unchanged alongside it.
    """
    out = {"label": "POST_HOC_DIAGNOSTIC_NOT_IN_DECISION",
           "method": "bounded bisection in log10(Xi) on the frozen 27-corner "
                     "recovered_within_factor_two predicate; 60 scan decades-steps then 60 "
                     "bisection halvings per crossing; tolerance 1e-6 in log10(Xi)",
           "feeds_no_decision_clause": True, "floors": {}}
    LO, HI, NSCAN, NBIS = -4.0, 3.0, 700, 60
    for f in PRECISION_FLOORS:
        key = "%dpct" % int(round(f * 100))
        # deterministic dense scan of the predicate, then bisect each sign change
        xs = [LO + (HI - LO) * k / NSCAN for k in range(NSCAN + 1)]
        ok = [_within_factor_two(10.0 ** x, f) for x in xs]
        crossings = []
        for k in range(NSCAN):
            if ok[k] != ok[k + 1]:
                a, b = xs[k], xs[k + 1]
                fa = ok[k]
                for _ in range(NBIS):
                    m = 0.5 * (a + b)
                    if _within_factor_two(10.0 ** m, f) == fa:
                        a = m
                    else:
                        b = m
                crossings.append({"log10_Xi": 0.5 * (a + b), "Xi": 10.0 ** (0.5 * (a + b)),
                                  "direction": "enter" if ok[k + 1] else "exit"})
        n_ok = sum(1 for v in ok if v)
        out["floors"][key] = {
            "floor": f,
            "n_scan_points": len(xs), "n_passing_scan_points": n_ok,
            "continuous_passing_interval_exists": bool(n_ok > 0),
            "n_crossings": len(crossings), "crossings": crossings,
            "Xi_lower": crossings[0]["Xi"] if len(crossings) == 2 else None,
            "Xi_upper": crossings[1]["Xi"] if len(crossings) == 2 else None,
            "single_contiguous_interval": bool(len(crossings) == 2 and n_ok > 0),
            "scan_bounds_log10": [LO, HI],
        }
    return out


# ==========================================================================================
# decision — the frozen seven-clause rule, applied unrevised
# ==========================================================================================

def decide(b, c_arm, d_arm, e_arm, f_arm, sens):
    clauses = [
        {"id": 1, "text": "the mirror forward map and inverse are algebraically valid",
         "passes": bool(b["forward_map_agrees_with_exact_network"]
                        and b["recovery_passes_everywhere"]),
         "evidence": "max |analytic - network| = %g (tol %g); recovery passes at all %d "
                     "nondegenerate grid points"
                     % (b["forward_map_max_abs_error"], TOL_MAP, b["n_nondegenerate"])},
        {"id": 2, "text": "the map (signed c, Xi) -> (R, s) is one-to-one over the nondegenerate "
                          "domain",
         "passes": bool(b["injectivity_empirical"]["distinct"]),
         "evidence": "algebraic: the inverse is a single-valued function of (R, s) built from "
                     "divisions by (1-c), (1+c), c, R, all nonzero on the domain. empirical: "
                     "min pairwise (R,s) distance = %g over %d points"
                     % (b["injectivity_empirical"]["min_pairwise_Rs_distance"],
                        b["n_nondegenerate"])},
        {"id": 3, "text": "numerical recovery passes over the predeclared grid",
         "passes": bool(b["recovery_passes_everywhere"]),
         "evidence": "max |c_hat - c| = %g (tol %g); max |Xi_hat - Xi|/Xi = %g (tol %g)"
                     % (b["c_max_abs_error"], TOL_C, b["Xi_max_rel_error"], TOL_XI_REL)},
        {"id": 4, "text": "path swap and scale controls recover the same Xi",
         "passes": bool(e_arm["path_swap"]["passes"] and b["scale_invariance_check"]["passes"]),
         "evidence": "swap: R preserved, share departure reverses, c_hat reverses, Xi_hat "
                     "unchanged. scale: flows x10, R/s/c_hat/Xi_hat invariant"},
        {"id": 5, "text": "the identical-path and Xi=0 cases correctly report no information",
         "passes": bool(e_arm["identical_paths_negative_control"]["reports_no_information"]
                        and e_arm["zero_coupling_limit"]["correctly_reports_no_information"]),
         "evidence": "both return status degenerate_no_information with Xi_hat = None; nothing "
                     "is regularised, clipped or epsilon-shifted"},
        {"id": 6, "text": "Q-only inference is confounded while Q plus outlet share removes the "
                          "confounding",
         "passes": bool(c_arm["Q_only_is_confounded"] and c_arm["Q_plus_share_is_unique"]),
         "evidence": "a 24-member family of distinct (c, Xi), both signs of c, reproduces each "
                     "observed R exactly; none reproduces the observed s; s - 1/2 = -(R-1)/(2Rc) "
                     "is strictly monotone on each branch and sign-separated across them"},
        {"id": 7, "text": "no continuous-alpha proxy reproduces the joint physical signature in "
                          "the primary mirror case",
         "passes": bool(d_arm["no_proxy_reproduces_joint_signature"]),
         "evidence": "s0 = 0.5 makes the proxy share alpha-invariant while the frozen completion "
                     "holds Q/Q0 = 1; both observables are missed at once"},
    ]
    survive = all(cl["passes"] for cl in clauses)
    resolution_specified = any(w["n_grid_points_recoverable"] > 0
                               for w in sens["well_conditioned_windows"].values())
    if survive and resolution_specified:
        decision, arm = "SURVIVE", "all seven frozen clauses evaluate true"
    elif survive:
        decision, arm = ("NEEDS_NEW_DATA",
                         "structurally identifiable but no finite resolution requirement could "
                         "be calculated")
    else:
        decision, arm = "RETIRE", "a frozen clause failed"
    return {
        "decision": decision, "arm": arm, "clauses": clauses,
        "resolution_requirement_specified_without_new_empirical_input": resolution_specified,
        "needs_new_data_not_used_merely_because_no_apparatus_exists": True,
        "licensed_claim": (
            "In the exact two-path mirror design, effective lateral coupling Xi is structurally "
            "identifiable from blocked/open total-flow measurements and separate outlet-flow "
            "share. Separate k_lat and w measurements are not mathematically necessary to infer "
            "Xi, although they remain necessary to decompose or physically interpret the "
            "effective conductance.") if decision == "SURVIVE" else None,
    }


# ==========================================================================================
# assembly
# ==========================================================================================

def _sha(rel):
    p = REPO_ROOT / rel
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def _round(o, nd=_RECORD_DP):
    if isinstance(o, dict):
        return {k: _round(v, nd) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_round(v, nd) for v in o]
    if isinstance(o, bool) or o is None:
        return o
    if isinstance(o, (int, np.integer)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        v = float(o)
        if not math.isfinite(v):
            return "non_finite:%r" % v
        return round(v, nd)
    return o


def screen():
    b = arm_b_recovery()
    c_arm = arm_c_minimum_observable()
    d_arm = arm_d_proxy_adversary()
    e_arm = arm_e_controls()
    f_arm = arm_f_mirror_imperfection()
    sens = sensitivity_envelopes()
    dec = decide(b, c_arm, d_arm, e_arm, f_arm, sens)

    doc = {
        "schema_version": SCHEMA_VERSION,
        "screen": SCREEN_ID,
        "labels": ["HUMAN_SELECTED_POST_SNAPSHOT", "CHEAP_SCIENTIFIC_SCREEN",
                   "NOT_A_PUBLICATION_RESULT", "NOT_A_MODEL_VALIDATION_UPGRADE"],
        "identity_note": "Human-selected from docs/cards/lateral_coupling_feasibility.md after "
                         "the generated candidate snapshot. No I- number is minted. "
                         "docs/insights/ID_REGISTRY.json and docs/insights/candidates/ are "
                         "BYTE-UNCHANGED, and the Foundry code (lenses, generators, scoring) "
                         "is unchanged. docs/insights/generated/** WAS REGENERATED through "
                         "`python -m puckworks.insights write` and never hand-edited: in the "
                         "complete candidate and tension payloads only source_commit/commit "
                         "provenance moved, and in snapshot_manifest.json the snapshot "
                         "commit, the corrected card's input hash and the derived output "
                         "hashes moved, with all other normalised manifest structure and "
                         "content equal, and in corpus_map.json the corrected card's own entity attrs (card_sha256, section_names, section_hashes) moved -- the map recording the card it is supposed to record, with no other entity, relation, warning or count touched. The 90 candidates were not scored, ranked or "
                         "inspected.",
        "source_commit": BASE_COMMIT,
        "protocol": {"path": PROTOCOL_PATH, "sha256": _sha(PROTOCOL_PATH)},
        "load_bearing_source_hashes": {f: _sha(f) for f in INPUT_FILES},
        "question": "In the controlled isoresistive-mirror two-path geometry, is the mapping from "
                    "physical lateral coupling to (Q/Q0, outlet share s1) one-to-one, so that Xi "
                    "can be recovered without separately measuring k_lat and w?",
        "primary_quantity": "Xi = G_lat*(1/A1 + 1/A2), the EXACT pressure-equalization number. "
                            "The legacy provisional Lambda regime labels are not used.",
        "model_domain": "puckworks.models.lateral_coupling.model1_two_path — exact steady "
                        "two-path Darcy network, P_out = 0 gauge, canonical "
                        "q_lat_1to2 = G_lat*(p1-p2).",
        "observables": ["Q0 (bridge blocked)", "q1 (bridge open)", "q2 (bridge open)",
                        "R = (q1+q2)/Q0", "s = q1/(q1+q2)"],
        "geometry": {
            "construction": "g1_top=a, g1_bot=b, g2_top=b, g2_bot=a (isoresistive mirror)",
            "a_of": "a = A(1+c)/2", "b_of": "b = A(1-c)/2",
            "c_definition": "c = (a-b)/(a+b)",
            "Xi_definition": "Xi = 2*G_lat/A for the mirror (A1 = A2 = A)",
            "primary_case": {"A": A_PRIMARY, "c": C_PRIMARY,
                             "conductances": list(mirror_conductances(A_PRIMARY, C_PRIMARY)),
                             "matches_harness_isoresistive_mirror": list(
                                 mirror_conductances(A_PRIMARY, C_PRIMARY)) == [3.0, 1.0, 1.0, 3.0]},
            "scaled_case": {"A": A_SCALED, "c": C_PRIMARY,
                            "conductances": list(mirror_conductances(A_SCALED, C_PRIMARY))},
            "P_in": P_IN,
        },
        "grids": {"c": list(C_GRID), "Xi": list(XI_GRID),
                  "Xi_definition": "0 plus 10**linspace(-4, 3, 22)",
                  "Xi_scenario_set": list(XI_SCENARIO_SET),
                  "perturbation_levels": list(PERTURB_LEVELS),
                  "precision_floors": list(PRECISION_FLOORS)},
        "software_tolerances": {
            "forward_map_abs": TOL_MAP, "c_abs": TOL_C, "Xi_rel": TOL_XI_REL,
            "degenerate_atol": DEGENERATE_ATOL, "recorded_decimal_places": _RECORD_DP,
            "note": "Reproducibility bounds on exact floating-point arithmetic. They are NOT "
                    "scientific uncertainties and were not retuned after seeing output. Recorded "
                    "floats are rounded to %d dp, so residuals below ~5e-%d record as 0.0."
                    % (_RECORD_DP, _RECORD_DP + 1)},
        "analytic_derivation": {
            "forward_R": "R = (1 - c^2/(1+Xi)) / (1 - c^2)",
            "forward_s": "s = (1-c)(1 + Xi + c) / (2(1 + Xi - c^2))",
            "consequence_R": "R - 1 = [c^2/(1-c^2)] * [Xi/(1+Xi)]  (>= 0)",
            "consequence_s": "s - 1/2 = -c*Xi / (2(1 + Xi - c^2))",
            "inverse_c": "c_hat = (R - 1) / [R (1 - 2s)]",
            "inverse_t": "t_hat = [1 - R(1 - c_hat^2)] / c_hat^2",
            "inverse_Xi": "Xi_hat = 1/t_hat - 1",
            "degenerate_fibre": "R = 1 <=> s = 1/2 <=> c*(t-1) = 0, i.e. exactly "
                                "{Xi = 0, any c} union {c = 0, any Xi}",
            "verified_against_exact_network": bool(b["forward_map_agrees_with_exact_network"]),
        },
        "degeneracy_classification": {
            "Xi_zero": {"R": 1.0, "s": 0.5,
                        "classification": "no coupling signature; inverse observationally "
                                          "degenerate for every c",
                        "reported_as": "degenerate_no_information",
                        "regularised": False},
            "c_zero": {"R": 1.0, "s": 0.5,
                       "classification": "identical paths; no mid-node pressure difference "
                                         "drives lateral flow, so Xi is unidentifiable",
                       "reported_as": "degenerate_no_information", "regularised": False},
            "Xi_to_infinity": {
                "R_limit": 1.0 + C_PRIMARY ** 2 / (1 - C_PRIMARY ** 2),
                "s_limit": (1 - C_PRIMARY) / 2.0,
                "classification": "structural identifiability persists (the inverse stays "
                                  "single-valued) while dR/dlnXi and ds/dlnXi -> 0, so practical "
                                  "sensitivity deteriorates",
                "structurally_identifiable": True},
            "Xi_small_nonzero": {
                "classification": "the exact inverse exists but both signals vanish linearly in "
                                  "Xi, so the measurement requirement diverges as 1/Xi",
                "structurally_identifiable": True},
        },
        "arm_b_forward_and_recovery": b,
        "arm_c_minimum_observable": c_arm,
        "arm_d_proxy_adversary": d_arm,
        "arm_e_controls": e_arm,
        "arm_f_mirror_imperfection": f_arm,
        "sensitivity_envelopes": sens,
        "decision": dec["decision"],
        "decision_record": dec,
        "evidence_labels_unchanged": True,
        "foundry_infrastructure_unchanged": {
            "lens_added_or_changed": False, "generator_added_or_changed": False,
            "scoring_added": False,
            "candidate_portfolio_content_changed": False,
            "candidate_added_or_removed": False, "candidate_scored": False,
            "id_registry_changed": False, "generated_artifacts_hand_edited": False,
            "generated_artifacts_regenerated": True,
            "regeneration_note": "docs/insights/generated/** WAS regenerated with "
                                 "`python -m puckworks.insights write` -- required, because the "
                                 "card correction this screen earned is an input the corpus map "
                                 "hashes, and `insights verify` fails on a stale input. It was "
                                 "never hand-edited. The only field that moved anywhere is "
                                 "source_commit: all 90 candidates, all 171 tension rows, every "
                                 "ID, every SEED status and every (empty) score are identical. "
                                 "ID_REGISTRY.json and docs/insights/candidates/ are byte-"
                                 "unchanged.",
        },
        "paper_4_authorized": False,
        "claim_ceiling": (
            "A cheap scientific screen, human-selected and post-snapshot. It is SYNTHETIC / "
            "MATHEMATICAL identifiability in the exact steady two-path Darcy network under a "
            "controlled mirror geometry -- NOT empirical validation of anything. It promotes no "
            "evidence rung. It produces NO real-puck Xi estimate and no k_lat estimate. It makes "
            "no claim that espresso occupies the transition regime or any regime. The 1/2/5 % "
            "figures are hypothetical resolution scenarios reusing the existing floor "
            "convention; they are not instrument accuracies, not experimental uncertainty, and "
            "no apparatus is shown able to attain the required precision. Paper 4 is NOT "
            "authorized."),
    }
    doc = _round(doc)
    blob = json.dumps(doc, sort_keys=True, ensure_ascii=False)
    doc["content_sha256"] = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return doc


# ==========================================================================================
# figure — ONE figure, three panels. Not a viz-registry entry (screen provenance, not a
# mechanism render with a fidelity ceiling).
# ==========================================================================================

def figure(result=None, path=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})
    r = result or screen()
    R_C, S_C, ACC, OK, GREY = "#2f6f8f", "#7a5195", "#b4472a", "#3d7a4e", "#666666"
    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.7))

    # ---- (a) the two boundary signatures vs Xi, with the sensitivity scenarios marked -----
    ax = axes[0]
    rows = r["sensitivity_envelopes"]["rows"]
    xi = [x["Xi"] for x in rows]
    ax.loglog(xi, [x["abs_R_minus_1"] for x in rows], "o-", color=R_C, ms=3.2, lw=1.6,
              label="$|Q/Q_0-1|$  (total flow)")
    ax.loglog(xi, [x["abs_s_minus_half"] for x in rows], "s-", color=S_C, ms=3.0, lw=1.6,
              label="$|s-1/2|$  (outlet share)")
    for f, ls in zip(r["grids"]["precision_floors"], (":", "-.", "--")):
        ax.axhline(f, color=ACC, linestyle=ls, lw=1.1)
        ax.text(xi[0] * 1.4, f * 1.12, "%d%% scenario" % round(f * 100), color=ACC, fontsize=6.4)
    ax.set_xlabel("$\\Xi$  (exact equalization number)")
    ax.set_ylabel("boundary signature magnitude")
    ax.set_title("(a)  What the boundary sees\n(mirror $a{=}3,b{=}1$; $c=0.5$)",
                 loc="left", fontweight="bold", fontsize=8.6)
    ax.legend(fontsize=6.9, loc="lower right", framealpha=0.95)
    ax.grid(alpha=0.25, which="both", lw=0.5)

    # ---- (b) Q-only confounding vs Q+share ------------------------------------------------
    ax = axes[1]
    fam = [f for f in r["arm_c_minimum_observable"]["families"] if f["Xi_true"] == 0.75]
    fam = fam[0] if fam else r["arm_c_minimum_observable"]["families"][0]
    for br, lab in ((+1.0, "all $(c,\\Xi)$ with the SAME $Q/Q_0$"), (-1.0, None)):
        mem = sorted([m for m in fam["members"] if m["c"] * br > 0], key=lambda m: m["c"])
        ax.semilogy([m["c"] for m in mem], [m["Xi"] for m in mem], "o-", color=GREY, lw=2.2,
                    ms=3.0, label=lab)
    ax.plot([fam["c_true"]], [fam["Xi_true"]], "*", color=OK, ms=17, zorder=5,
            label="the one $(c,\\Xi)$ that also\nmatches the outlet share $s$")
    for sgn in (+1.0, -1.0):
        ax.axvline(sgn * fam["c_magnitude_lower_bound"], color=ACC, ls="--", lw=1.1)
    ax.text(fam["c_magnitude_lower_bound"], ax.get_ylim()[1], "  $|c|>\\sqrt{1-1/R}$",
            color=ACC, fontsize=6.8, va="top")
    ax.set_xlim(-1.0, 1.0)
    ax.set_xlabel("signed axial contrast  $c$"); ax.set_ylabel("$\\Xi$")
    ax.set_title("(b)  With $c$ unknown, $Q$ alone can't identify\n$(c,\\Xi)$ jointly; "
                 "$Q$ + outlet share can",
                 loc="left", fontweight="bold", fontsize=8.6)
    ax.text(0.03, 0.04, "$Q/Q_0$ observed = %.6f\n%d family members reproduce it exactly\n"
                        "(both signs of $c$ — $R$ depends on $c^2$)\n%d of them also match $s$"
            % (fam["R_observed"], fam["n_family_members"], fam["n_members_also_matching_s"]),
            transform=ax.transAxes, fontsize=6.6, va="bottom", color=ACC, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=ACC))
    ax.legend(fontsize=6.4, loc="upper center", framealpha=0.95)
    ax.grid(alpha=0.25, which="both", lw=0.5)

    # ---- (c) worst-case recovered-Xi envelope per scenario ---------------------------------
    ax = axes[2]
    cols = {"1pct": "#2f6f8f", "2pct": "#7a5195", "5pct": "#c8862a"}
    ax.axhspan(0.5, 2.0, color=OK, alpha=0.12, zorder=0)
    for key, col in cols.items():
        lo = [x["scenarios"][key]["Xi_hat_min_over_true"] for x in rows]
        hi = [x["scenarios"][key]["Xi_hat_max_over_true"] for x in rows]
        good = [(x, l, h) for x, l, h in zip(xi, lo, hi) if l is not None and h is not None]
        if good:
            ax.fill_between([g[0] for g in good], [g[1] for g in good], [g[2] for g in good],
                            color=col, alpha=0.16, lw=1.2, edgecolor=col,
                            label="%s floor" % key.replace("pct", " %"))
    # NO SILENT CAPS: mark where the band is built from a SUBSET of the 27 scenario corners
    # because the rest returned no physical inverse. There the true spread is worse than drawn.
    for n, (key, col) in enumerate(cols.items()):
        drop = [x["Xi"] for x in rows
                if x["scenarios"][key]["n_nonphysical_or_undefined"] > 0]
        if drop:
            y = (46.0, 36.0, 28.0)[n]
            ax.plot(drop, [y] * len(drop), "x", color=col, ms=3.4, mew=1.0,
                    label=("some corners had NO physical $\\hat{\\Xi}$\n(band below is optimistic)"
                           if n == 0 else None))
    cont = r["sensitivity_envelopes"]["continuous_window_post_hoc"]["floors"]
    for n, (key, col) in enumerate(cols.items()):
        w = r["sensitivity_envelopes"]["well_conditioned_windows"][key]
        cw = cont[key]
        y = (0.042, 0.027, 0.0175)[n]
        if cw["Xi_lower"] is not None:
            # the BAR is the continuous crossing interval (post-hoc); the DOTS are the frozen
            # grid points that pass. Quoting the dots' min/max as the interval would be wrong.
            ax.plot([cw["Xi_lower"], cw["Xi_upper"]], [y, y], "-", color=col, lw=4.0,
                    solid_capstyle="butt", alpha=0.55)
            ax.plot([x["Xi"] for x in rows
                     if x["scenarios"][key]["recovered_within_factor_two"]],
                    [y] * w["n_grid_points_recoverable"], "o", color=col, ms=3.6)
            ax.text(cw["Xi_upper"] * 1.6, y, " within 2x @ %s: %.2f–%.2f (post-hoc);\n %d frozen"
                                             " grid pts (dots)"
                    % (key.replace("pct", " %"), cw["Xi_lower"], cw["Xi_upper"],
                       w["n_grid_points_recoverable"]),
                    color=col, fontsize=5.9, va="center", fontweight="bold")
        else:
            ax.text(xi[0] * 1.3, y, "no $\\Xi$ recoverable within 2x @ %s"
                    % key.replace("pct", " %"), color=col, fontsize=6.2, va="center",
                    fontweight="bold")
    ax.axhline(1.0, color="black", lw=0.9)
    ax.axhline(2.0, color=OK, ls="--", lw=1.0)
    ax.axhline(0.5, color=OK, ls="--", lw=1.0)
    ax.text(xi[0] * 1.3, 2.3, "factor-of-two band", color=OK, fontsize=6.8, fontweight="bold")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_ylim(0.012, 60.0)
    ax.set_xlabel("true $\\Xi$"); ax.set_ylabel("recovered $\\hat{\\Xi}\\,/\\,\\Xi$")
    ax.set_title("(c)  Worst-case recovery under the\nhypothetical resolution scenarios",
                 loc="left", fontweight="bold", fontsize=8.6)
    ax.legend(fontsize=6.8, loc="upper right", framealpha=0.95)
    ax.grid(alpha=0.25, which="both", lw=0.5)

    fig.suptitle("WP6-LC-IDENT — HUMAN_SELECTED_POST_SNAPSHOT / CHEAP_SCIENTIFIC_SCREEN / "
                 "NOT_A_PUBLICATION_RESULT / NOT_A_MODEL_VALIDATION_UPGRADE\n"
                 "Exact steady two-path Darcy network, controlled mirror geometry. Synthetic "
                 "mathematical identifiability — NOT empirical validation, and no real-puck "
                 "$\\Xi$. Panel (c) shows hypothetical resolution scenarios, not instrument "
                 "accuracies.", fontsize=8.6, y=1.06)
    fig.tight_layout()
    out = path or str(REPO_ROOT / BUNDLE_REL / "figures/primary.png")
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


# ==========================================================================================
# CLI
# ==========================================================================================

def _result_path():
    return REPO_ROOT / BUNDLE_REL / "result.json"


def _payload(doc):
    return json.dumps(doc, indent=2, sort_keys=True) + "\n"


def write():
    doc = screen()
    p = _result_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(_payload(doc), encoding="utf-8")
    fig = figure(doc)
    return doc, str(p), fig


def verify():
    """Deterministic: recompute and byte-compare result.json. The figure is NOT byte-compared
    (matplotlib output is renderer/version dependent); its existence is checked instead."""
    doc = screen()
    p = _result_path()
    stale = []
    if not p.exists():
        stale.append("result.json (missing)")
    elif p.read_text(encoding="utf-8") != _payload(doc):
        stale.append("result.json (drift)")
    figp = REPO_ROOT / BUNDLE_REL / "figures/primary.png"
    if not figp.exists():
        stale.append("figures/primary.png (missing)")
    return stale, doc


def main(argv=None):
    ap = argparse.ArgumentParser(prog="puckworks.analysis.screen_wp6_lateral_identifiability")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.write:
        doc, p, fig = write()
    else:
        stale, doc = verify()
        if stale:
            print("STALE (run --write):", stale)
            return 1
        p = fig = None

    b = doc["arm_b_forward_and_recovery"]
    print("screen:               %s  (%s)" % (doc["screen"], ", ".join(doc["labels"])))
    print("protocol sha256:      %s" % doc["protocol"]["sha256"])
    print("grid:                 %d points (%d nondegenerate)"
          % (b["n_grid_points"], b["n_nondegenerate"]))
    print("forward map vs net:   agrees to machine precision (live max <= 1e%d; records as %g "
          "after 12-dp rounding; tol %g)"
          % (b["forward_map_max_abs_error_log10_upper_bound"],
             b["forward_map_max_abs_error"], TOL_MAP))
    print("recovery:             max |dc| %g ; max |dXi|/Xi %g"
          % (b["c_max_abs_error"], b["Xi_max_rel_error"]))
    print("injectivity:          min pairwise (R,s) distance %g"
          % b["injectivity_empirical"]["min_pairwise_Rs_distance"])
    print("Q-only confounded:    %s" % doc["arm_c_minimum_observable"]["Q_only_is_confounded"])
    print("Q+share unique:       %s" % doc["arm_c_minimum_observable"]["Q_plus_share_is_unique"])
    print("proxy adversary:      distinguishable=%s"
          % doc["arm_d_proxy_adversary"]["no_proxy_reproduces_joint_signature"])
    for lv in doc["arm_f_mirror_imperfection"]["levels"]:
        print("mirror imperfection:  %.0f%% -> max |dXi|/Xi (ideal inverse) %.4g ; "
              "calibrated max rel err %.3g"
              % (lv["perturbation_level"] * 100, lv["mirror_inverse_max_abs_Xi_rel_bias"],
                 lv["calibrated_max_Xi_rel_err"]))
    cont = doc["sensitivity_envelopes"]["continuous_window_post_hoc"]["floors"]
    for k, w in doc["sensitivity_envelopes"]["well_conditioned_windows"].items():
        cw = cont[k]
        print("window %-5s          frozen grid: %d of %d points pass %s | continuous "
              "(post-hoc): %s"
              % (k, w["n_grid_points_recoverable"], len(doc["sensitivity_envelopes"]["rows"]),
                 [r["Xi"] for r in doc["sensitivity_envelopes"]["rows"]
                  if r["scenarios"][k]["recovered_within_factor_two"]],
                 ("Xi in [%.4g, %.4g]" % (cw["Xi_lower"], cw["Xi_upper"])
                  if cw["Xi_lower"] is not None else "no passing interval")))
    print("DECISION:             %s — %s" % (doc["decision"], doc["decision_record"]["arm"]))
    print("content sha256:       %s" % doc["content_sha256"])
    if p:
        print("wrote %s\nwrote %s" % (p, fig))
    else:
        print("bundle artifacts are up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
