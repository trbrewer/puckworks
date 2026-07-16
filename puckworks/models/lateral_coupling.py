"""WP6 — MINIMAL conservative lateral-coupling models (feasibility phase only).

Card-first feasibility ladder for the physical lateral-coupling question
(docs/cards/lateral_coupling_feasibility.md). NOT a Paper-4 model. Two smallest conservative
members:

  Model 0  — two UNCOUPLED axial Darcy paths (parallel tubes).
  Model 1  — the same two paths joined at a mid-depth node by a PHYSICAL transverse conductance
             ``G_lat`` (a real lateral Darcy exchange, NOT numerical diffusion or ad-hoc state
             mixing). Steady linear 2-node network; solved exactly.

Gauge: ``P_out = 0`` (fixed; not generalized here). ``q1``/``q2`` are the BOTTOM/OUTLET flows.

SIGN CONVENTION (canonical): ``q_lat_1to2 > 0`` means physical flow FROM path 1 TO path 2,
i.e. ``q_lat_1to2 = G_lat * (p1 - p2)`` (positive when p1 > p2). Node balances use this sign.
"""
from __future__ import annotations

import numpy as np


def _finite(x, name):
    if not np.isfinite(x):
        raise ValueError("%s must be finite, got %r" % (name, x))


def _positive_conductance(g, name):
    _finite(g, name)
    if g <= 0:
        raise ValueError("%s must be > 0, got %r" % (name, g))


def g_series(g_top, g_bot):
    """One-path equivalent end-to-end SERIES conductance = g_top*g_bot / (g_top + g_bot)."""
    _positive_conductance(g_top, "g_top")
    _positive_conductance(g_bot, "g_bot")
    return float(g_top * g_bot / (g_top + g_bot))


def g_axial_reference(g1_top, g1_bot, g2_top, g2_bot):
    """Reference axial conductance for the feasibility sweep: the MEAN of the two uncoupled
    end-to-end series conductances. Lambda = G_lat / g_axial_reference (WP6.3). For the mirror
    case (3,1,1,3) both series conductances are 0.75, so g_axial_reference = 0.75."""
    return float((g_series(g1_top, g1_bot) + g_series(g2_top, g2_bot)) / 2.0)


def model0_uncoupled(P_in, g_top, g_bot):
    """One axial path, two half-segments in series. Returns mid-node pressure and the (equal,
    steady) through-flow. P_out = 0."""
    _finite(P_in, "P_in")
    if P_in < 0:
        raise ValueError("P_in must be >= 0 under the P_out=0 gauge, got %r" % P_in)
    _positive_conductance(g_top, "g_top")
    _positive_conductance(g_bot, "g_bot")
    p_mid = g_top * P_in / (g_top + g_bot)
    q = g_bot * p_mid                      # = g_top*(P_in - p_mid): series continuity
    return {"p_mid": float(p_mid), "q": float(q)}


def strong_coupling_limit(P_in, g1_top, g1_bot, g2_top, g2_bot):
    """Exact G_lat -> infinity limit (mid-node pressures equalize):
        p_inf = P_in*(g1_top+g2_top) / (g1_top+g2_top+g1_bot+g2_bot);  Q_inf = (g1_bot+g2_bot)*p_inf."""
    _finite(P_in, "P_in")
    if P_in < 0:
        raise ValueError("P_in must be >= 0 under the P_out=0 gauge, got %r" % P_in)
    for nm, g in (("g1_top", g1_top), ("g1_bot", g1_bot), ("g2_top", g2_top), ("g2_bot", g2_bot)):
        _positive_conductance(g, nm)
    p_inf = P_in * (g1_top + g2_top) / (g1_top + g2_top + g1_bot + g2_bot)
    return {"p_inf": float(p_inf), "Q_inf": float((g1_bot + g2_bot) * p_inf)}


def equalization_number(G_lat, g1_top, g1_bot, g2_top, g2_bot):
    """Exact two-node pressure-equalization group Xi = G_lat*(1/A1 + 1/A2), with the per-path
    axial conductance sums A1 = g1_top+g1_bot, A2 = g2_top+g2_bot. For ANY nonzero uncoupled
    mid-node pressure gap the closed-form gap ratio is exactly ``gap/gap0 = 1/(1+Xi)`` (derived:
    gap = (A2*b1 - A1*b2)/det, gap0 = (A2*b1 - A1*b2)/(A1*A2), det = A1*A2 + G_lat*(A1+A2)).
    Xi is the physically exact equalization control; the axial-conductance-ratio Lambda (WP6.3)
    is a separate, legacy nominal grouping and is NOT this closed form."""
    _finite(G_lat, "G_lat")
    if G_lat < 0:
        raise ValueError("G_lat must be >= 0, got %r" % G_lat)
    for nm, g in (("g1_top", g1_top), ("g1_bot", g1_bot), ("g2_top", g2_top), ("g2_bot", g2_bot)):
        _positive_conductance(g, nm)
    A1 = g1_top + g1_bot
    A2 = g2_top + g2_bot
    return float(G_lat) * (1.0 / A1 + 1.0 / A2)


def gap_remaining_fraction(Xi):
    """Closed-form residual pressure-gap fraction gap/gap0 = 1/(1+Xi) (Xi = equalization_number)."""
    _finite(Xi, "Xi")
    if Xi < 0:
        raise ValueError("Xi must be >= 0, got %r" % Xi)
    return 1.0 / (1.0 + Xi)


# Xi thresholds are the EXACT images of the 5% / 95% gap-reduction cutoffs under 1/(1+Xi):
#   reduction < 5%  <=> Xi < 1/0.95 - 1 ;  reduction >= 95% <=> Xi >= 1/0.05 - 1 = 19.
XI_UNCHANGED = 1.0 / 0.95 - 1.0     # 0.05263157894736836
XI_HOMOGENIZED = 1.0 / 0.05 - 1.0   # 19.0


def equalization_regime(Xi, lo=XI_UNCHANGED, hi=XI_HOMOGENIZED):
    """Physical pressure-equalization label from the EXACT Xi (not the legacy Lambda):
    Xi < lo -> 'pressure_gap_unchanged'; lo <= Xi < hi -> 'pressure_gap_transition';
    Xi >= hi -> 'pressure_gap_homogenized'. Only meaningful when the uncoupled gap is nonzero."""
    _finite(Xi, "Xi")
    if Xi < 0:
        raise ValueError("Xi must be >= 0, got %r" % Xi)
    if Xi < lo:
        return "pressure_gap_unchanged"
    if Xi >= hi:
        return "pressure_gap_homogenized"
    return "pressure_gap_transition"


def model1_two_path(P_in, g1_top, g1_bot, g2_top, g2_bot, G_lat):
    """Two axial paths joined at their mid-nodes by a physical transverse conductance G_lat.
    Solves the 2-node steady Darcy network exactly. ``q1``/``q2`` are BOTTOM/OUTLET flows;
    ``q1_in``/``q2_in`` the TOP/INLET flows; ``q_lat_1to2 = G_lat*(p1-p2)`` (>0 = flow 1->2)."""
    _finite(P_in, "P_in")
    if P_in < 0:
        raise ValueError("P_in must be >= 0 under the P_out=0 gauge, got %r" % P_in)
    for nm, g in (("g1_top", g1_top), ("g1_bot", g1_bot), ("g2_top", g2_top), ("g2_bot", g2_bot)):
        _positive_conductance(g, nm)
    _finite(G_lat, "G_lat")
    if G_lat < 0:
        raise ValueError("G_lat must be >= 0, got %r" % G_lat)

    # 2x2 SPD network [[a,-G],[-G,d]] p = [b1,b2] solved ANALYTICALLY (pure float ops, so the
    # result is IEEE-754 deterministic across platforms — no BLAS/ULP noise in the artifacts).
    a = g1_top + g1_bot + G_lat
    d = g2_top + g2_bot + G_lat
    det = a * d - G_lat * G_lat            # > 0 for positive conductances (SPD)
    b1 = g1_top * P_in
    b2 = g2_top * P_in
    p1 = (d * b1 + G_lat * b2) / det
    p2 = (G_lat * b1 + a * b2) / det

    q1_in = g1_top * (P_in - p1)
    q2_in = g2_top * (P_in - p2)
    q1 = g1_bot * p1                       # bottom / outlet flows
    q2 = g2_bot * p2
    q12 = G_lat * (p1 - p2)                # CANONICAL: > 0 means flow path 1 -> path 2
    Q = q1 + q2
    q_in = q1_in + q2_in

    # effective (two-terminal) conductance is P_in-independent (linear network); at P_in==0
    # derive it from the unit-inlet solution instead of dividing by zero.
    if P_in > 0:
        eff = Q / P_in
    else:
        pu1 = (d * g1_top + G_lat * g2_top) / det
        pu2 = (G_lat * g1_top + a * g2_top) / det
        eff = g1_bot * pu1 + g2_bot * pu2

    # condition number of the symmetric 2x2 (analytic eigenvalues — deterministic)
    tr = a + d
    disc = (tr * tr - 4.0 * det) ** 0.5
    cond = abs((tr + disc) / (tr - disc))

    return {
        "p1": float(p1), "p2": float(p2),
        "q1": float(q1), "q2": float(q2), "Q": float(Q), "q_in": float(q_in),
        "q1_in": float(q1_in), "q2_in": float(q2_in),
        "q_lat_1to2": float(q12),
        "node1_residual": float(q1_in - q1 - q12),
        "node2_residual": float(q2_in + q12 - q2),
        "global_residual": float(q_in - Q),
        "effective_conductance": float(eff),
        "condition_number": float(cond),
    }


def coupling_number(G_lat, g_axial):
    """Nondimensional Lambda = transverse conductance / axial conductance (WP6.3)."""
    _finite(G_lat, "G_lat")
    _finite(g_axial, "g_axial")
    if G_lat < 0:
        raise ValueError("G_lat must be >= 0, got %r" % G_lat)
    if g_axial <= 0:
        raise ValueError("g_axial must be > 0, got %r" % g_axial)
    return float(G_lat) / float(g_axial)


def regime(Lambda, lo=0.05, hi=5.0):
    """LEGACY / PROVISIONAL NOMINAL labels on the axial-conductance-ratio Lambda (WP6.3). These
    are NOT the exact equalization control (use ``equalization_number`` / ``equalization_regime``
    on Xi for that) and the Lambda=0.05 and Lambda=5 boundaries are neither validated nor
    universal — they are nominal grouping cutoffs kept only for continuity:
    Lambda < lo -> uncoupled; lo <= Lambda <= hi -> transitional; Lambda > hi -> homogenized.
    Equality at lo and hi belongs to 'transitional'."""
    _finite(Lambda, "Lambda")
    if Lambda < 0:
        raise ValueError("Lambda must be >= 0, got %r" % Lambda)
    _finite(lo, "lo")
    _finite(hi, "hi")
    if lo < 0:
        raise ValueError("lo must be >= 0, got %r" % lo)
    if hi <= lo:
        raise ValueError("hi must be > lo, got lo=%r hi=%r" % (lo, hi))
    if Lambda < lo:
        return "uncoupled"
    if Lambda > hi:
        return "homogenized"
    return "transitional"
