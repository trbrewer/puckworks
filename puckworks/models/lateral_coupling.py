"""WP6 / PR10 — MINIMAL conservative lateral-coupling models (feasibility phase only).

This is the card-first feasibility ladder for the physical lateral-coupling question
(docs/cards/lateral_coupling_feasibility.md), NOT the full Paper-4 model. It provides the two
smallest conservative members needed for a go/no-go decision:

  Model 0  — two UNCOUPLED axial Darcy paths (parallel tubes).
  Model 1  — the same two paths joined at a mid-depth node by a TRANSVERSE conductance
             ``G_lat`` (a physical lateral Darcy exchange, NOT numerical diffusion or ad-hoc
             state mixing). Steady linear network; solved exactly.

Both satisfy: local + global mass conservation; the correct zero-coupling limit
(Model 1 -> Model 0 as G_lat -> 0); and the correct strong-coupling tendency (mid-node
pressures equalize as G_lat -> infinity). The nondimensional group ``Lambda = G_lat / g_axial``
places a configuration on the uncoupled -> transitional -> homogenized regime map.
"""
from __future__ import annotations

import numpy as np


def model0_uncoupled(P_in, g_top, g_bot):
    """One axial path, two half-segments in series (top+bottom Darcy conductances). Returns the
    mid-node pressure and the (equal, steady) through-flow. P_out = 0."""
    p_mid = g_top * P_in / (g_top + g_bot)
    q = g_bot * p_mid                     # = g_top*(P_in - p_mid): series continuity
    return {"p_mid": float(p_mid), "q": float(q)}


def model1_two_path(P_in, g1_top, g1_bot, g2_top, g2_bot, G_lat):
    """Two axial paths joined at their mid-nodes by a transverse conductance G_lat. Solves the
    2-node steady Darcy network exactly. Returns mid-node pressures, per-path outflow, total
    flow, and the inflow (which must equal total outflow by conservation). P_out = 0."""
    # node i: g_i,top (P_in - p_i) - g_i,bot p_i + G_lat (p_j - p_i) = 0
    A = np.array([[g1_top + g1_bot + G_lat, -G_lat],
                  [-G_lat, g2_top + g2_bot + G_lat]], float)
    b = np.array([g1_top * P_in, g2_top * P_in], float)
    p1, p2 = np.linalg.solve(A, b)
    q1, q2 = g1_bot * p1, g2_bot * p2                  # per-path outflow
    q_in = g1_top * (P_in - p1) + g2_top * (P_in - p2)  # total inflow
    q_lat = G_lat * (p2 - p1)                            # transverse flux 1->2
    return {"p1": float(p1), "p2": float(p2), "q1": float(q1), "q2": float(q2),
            "Q": float(q1 + q2), "q_in": float(q_in), "q_lat_1to2": float(q_lat)}


def coupling_number(G_lat, g_axial):
    """Nondimensional Lambda = transverse conductance / axial conductance (WP6.3)."""
    return float(G_lat) / float(g_axial)


def regime(Lambda, lo=0.05, hi=5.0):
    """Regime map: below `lo` lateral coupling is negligible (paths independent); above `hi`
    it homogenizes the paths; between, it is a measurable TRANSITION — the only regime where
    a physical lateral model is distinguishable from the uncoupled proxy."""
    if Lambda < lo:
        return "uncoupled"
    if Lambda > hi:
        return "homogenized"
    return "transitional"
