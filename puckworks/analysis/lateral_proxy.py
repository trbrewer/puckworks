"""WP6 — the streamtube share-homogenization operator as a pure helper + the FROZEN UNCOUPLED
SHARE-PROXY COMPLETION adapter for matched comparison against the physical lateral model. This
comparator is the frozen uncoupled completion of the share operator, NOT the complete dynamic
streamtube model.

The proxy is a SHARE/relative-flow homogenizer: ``w <- (1-alpha)*w + alpha`` (alpha in [0,1]).
It is NOT a pressure network — it has no p1/p2, no G_lat, no transverse pressure gradient, no
q_lat, and one share through a path's whole depth. Those physical quantities are reported as
UNAVAILABLE (None), never as a fabricated 0. ``alpha`` and the physical ``Lambda`` are treated
as INDEPENDENT parameters (no alpha = f(Lambda) mapping is invented).
"""
from __future__ import annotations

import numpy as np

from puckworks.models.lateral_coupling import g_series


def homogenize_relative_flow(relative_flow, alpha):
    """The exact ntube proxy operator on unit-mean relative flows: ``(1-alpha)*rf + alpha``.
    Validates finite, nonnegative ``relative_flow`` and ``alpha in [0,1]``. Preserves shape and
    does NOT normalize (callers normalize to shares explicitly if they need to)."""
    rf = np.asarray(relative_flow, dtype=float)
    if not np.all(np.isfinite(rf)):
        raise ValueError("relative_flow must be finite")
    if np.any(rf < 0):
        raise ValueError("relative_flow must be nonnegative")
    if not np.isfinite(alpha):
        raise ValueError("alpha must be finite, got %r" % (alpha,))
    if not (0.0 <= alpha <= 1.0):
        raise ValueError("alpha must be in [0, 1], got %r" % (alpha,))
    return (1.0 - alpha) * rf + alpha


def frozen_two_path_proxy(P_in, g1_top, g1_bot, g2_top, g2_bot, alpha):
    """Frozen-state share proxy for the two-path matched comparison.

    Uses the two paths' UNCOUPLED end-to-end conductances to form unit-mean relative flows,
    applies the exact ntube homogenizer, and reports normalized shares. Under the labelled
    ``proxy_uncoupled_completion`` the two axial paths stay INDEPENDENT: total flow is retained
    at the uncoupled value (Q/Q0 = 1) and each path carries ONE share through its whole depth,
    so ``proxy_inlet_share == proxy_outlet_share`` (share transfer is identically 0). Physical
    observables a share proxy cannot produce are None with ``physical_observables_available``
    False — not zero."""
    if not np.isfinite(P_in):
        raise ValueError("P_in must be finite, got %r" % (P_in,))
    if P_in < 0:
        raise ValueError("P_in must be >= 0 under the P_out=0 gauge, got %r" % (P_in,))
    g_eq = np.array([g_series(g1_top, g1_bot), g_series(g2_top, g2_bot)], float)
    q0 = P_in * g_eq
    w = g_eq / g_eq.mean()                      # unit-mean relative flows
    w_proxy = homogenize_relative_flow(w, alpha)
    s0 = w / w.sum()                            # original normalized shares
    s_proxy = w_proxy / w_proxy.sum()           # homogenized normalized shares
    return {
        "alpha": float(alpha),
        "is_frozen_share_proxy": True,
        "completion": "proxy_uncoupled_completion",
        "uncoupled_equivalent_conductances": [float(x) for x in g_eq],
        "uncoupled_flows": [float(x) for x in q0],
        "original_shares": [float(x) for x in s0],
        "homogenized_shares": [float(x) for x in s_proxy],
        "Q_over_Q0": 1.0,                       # total flow retained at the uncoupled value
        "proxy_inlet_share_1": float(s_proxy[0]),
        "proxy_outlet_share_1": float(s_proxy[0]),   # one share through the whole depth
        "proxy_share_transfer_1": 0.0,               # inlet == outlet by construction
        "physical_observables_available": False,
        "physical_observables": {                    # a share proxy has no pressure law
            "p1": None, "p2": None, "mid_depth_pressure_gap": None,
            "q_lat_1to2": None, "distinct_inlet_vs_outlet_share": None,
            "physical_effective_conductance": None,
        },
    }
