"""P2 commanded-vs-achieved atlas — PRESSURE FIRST, time-weighted (WP2).

Implements the committed pre-analysis spec (docs/analysis/PRESSURE_ATLAS_SPEC.md, hash
below). Headline error is integrated over TIME across the ACTIVE brewing interval, never
bridging gaps > threshold, in physical units (bar). Sample-weighted RMSE and any lag
correction are secondary diagnostics only — the primary metrics use the UNSHIFTED series so
controller delay is never optimized away into apparent perfect tracking. Per-shot metrics are
summarized as DISTRIBUTIONS, with a store-order-independent one-shot-per-user sensitivity.
Flow tracking stays out until quantity kinds resolve.
"""
import hashlib
import json

import numpy as np

from puckworks.data import visualizer_store as vs
from puckworks.analysis import product_envelope
from puckworks.analysis.visualizer_eligibility import is_included

_BAR = 1.0e5
_ACHIEVED = "pressure__Pa"
_GOAL = "pressure_goal__Pa"
assert vs.is_pooling_safe(_ACHIEVED) and vs.is_pooling_safe(_GOAL)   # P0.4 guardrail

# --- committed pre-analysis spec (hashed into every output) ---------------------------------
SPEC = {
    "spec_version": "pressure-atlas/v1",
    "gap_threshold_s": 2.0,
    "active_goal_bar": 1.0,
    "min_active_time_s": 1.0,   # QC floor: drop degenerate sub-second traces (real shots ~20s+)
    "transition_amplitude_bar": 0.5,
    "tolerances_bar": [0.5, 1.0],
}
SPEC_HASH = hashlib.sha256(json.dumps(SPEC, sort_keys=True).encode("utf-8")).hexdigest()[:16]

_METRICS = ("active_time_s", "tw_mae_bar", "tw_rmse_bar", "tw_signed_bias_bar",
            "frac_time_within_0p5bar", "frac_time_within_1bar",
            "p90_abs_err_bar", "max_overshoot_bar", "n_goal_transitions",
            "sample_rmse_bar", "lag_s", "lag_corrected_tw_mae_bar")

_METRIC_DEFS = {
    "active_time_s": "integrated active brewing time (goal>=1bar, gaps>2s excluded)",
    "tw_mae_bar": "PRIMARY: time-weighted mean |achieved-goal| in bar over active time",
    "tw_rmse_bar": "PRIMARY: time-weighted RMS(achieved-goal) in bar",
    "tw_signed_bias_bar": "PRIMARY: time-weighted mean(achieved-goal) in bar",
    "frac_time_within_0p5bar": "PRIMARY: fraction of active time with |err|<=0.5 bar",
    "frac_time_within_1bar": "PRIMARY: fraction of active time with |err|<=1.0 bar",
    "p90_abs_err_bar": "secondary: 90th-percentile |err| over active samples",
    "max_overshoot_bar": "secondary: max(achieved-goal,0) over active samples",
    "n_goal_transitions": "secondary: commanded-goal transitions (>=0.5 bar)",
    "sample_rmse_bar": "diagnostic ONLY: sample-weighted RMSE (not time-weighted)",
    "lag_s": "secondary: estimated controller lag (achieved behind goal), unshifted metrics are primary",
    "lag_corrected_tw_mae_bar": "secondary: tw_mae after removing lag_s (never the headline)",
}


def _command_shape(Gbar, active_mask, amp):
    """Coarse commanded-profile class over the active region (WP2.5)."""
    g = Gbar[active_mask]
    if g.size < 2:
        return "unknown"
    dg = np.diff(g)
    steps = np.abs(dg) >= amp
    n = int(np.count_nonzero(steps))
    if n == 0:
        return "constant"
    if np.all(dg[steps] < 0) and n >= 2:
        return "declining"
    if n == 1:
        # step (change in ~1 interval) vs ramp (change spread over many intervals)
        return "single_step"
    return "multi_step"


def pressure_tracking_metrics(shot):
    """Per-shot TIME-WEIGHTED pressure tracking metrics over the active brewing interval, or
    None if the shot lacks an eligible active interval (>= min_active_time_s). Bar / seconds."""
    hy = shot.get("hydraulic") or {}
    t, a, g = hy.get("time__s"), hy.get(_ACHIEVED), hy.get(_GOAL)
    if not (t and a and g):
        return None
    n = min(len(t), len(a), len(g))
    T, A, G = [], [], []
    for i in range(n):
        if t[i] is not None and a[i] is not None and g[i] is not None:
            T.append(float(t[i])); A.append(float(a[i])); G.append(float(g[i]))
    if len(T) < 2:
        return None
    T, A, G = np.asarray(T), np.asarray(A), np.asarray(G)
    Gbar, err = G / _BAR, (A - G) / _BAR

    gap, act = SPEC["gap_threshold_s"], SPEC["active_goal_bar"]
    # interval-level trapezoidal node weights, restricted to active brewing intervals with no
    # gap bridging: an interval counts only if dt in (0, gap] AND both ends are brewing.
    w = np.zeros(len(T))
    active_node = np.zeros(len(T), bool)
    for i in range(len(T) - 1):
        dt = T[i + 1] - T[i]
        if 0.0 < dt <= gap and Gbar[i] >= act and Gbar[i + 1] >= act:
            w[i] += dt / 2.0
            w[i + 1] += dt / 2.0
            active_node[i] = active_node[i + 1] = True
    W = float(w.sum())
    if W < SPEC["min_active_time_s"]:
        return None                                   # no eligible active interval

    def tw(x):
        return float(np.sum(w * x) / W)

    ae = np.abs(err)
    ea = err[active_node]
    tol = SPEC["tolerances_bar"]
    m = {
        "active_time_s": W,
        "tw_mae_bar": tw(ae),
        "tw_rmse_bar": float(np.sqrt(np.sum(w * err ** 2) / W)),
        "tw_signed_bias_bar": tw(err),
        "frac_time_within_0p5bar": tw((ae <= tol[0]).astype(float)),
        "frac_time_within_1bar": tw((ae <= tol[1]).astype(float)),
        "p90_abs_err_bar": float(np.percentile(np.abs(ea), 90)) if ea.size else None,
        "max_overshoot_bar": float(max(np.max(ea), 0.0)) if ea.size else None,
        "n_goal_transitions": int(np.count_nonzero(
            np.abs(np.diff(Gbar[active_node])) >= SPEC["transition_amplitude_bar"]))
            if active_node.sum() > 1 else 0,
        "sample_rmse_bar": float(np.sqrt(np.mean(ea ** 2))) if ea.size else None,
        "command_shape": _command_shape(Gbar, active_node, SPEC["transition_amplitude_bar"]),
    }
    # lag diagnostic (secondary): best integer-sample shift of achieved EARLIER (0..5),
    # minimizing sample-MAE on active nodes; report lag in seconds + lag-corrected tw_mae.
    idx = np.where(active_node)[0]
    if idx.size >= 4:
        dt_med = float(np.median(np.diff(T[idx]))) if idx.size > 1 else 0.0
        best_k, best_mae = 0, float(np.mean(np.abs(err[idx])))
        for k in range(1, 6):
            if idx.size - k < 3:
                break
            shifted = (A[idx][:-k] - G[idx][k:]) / _BAR    # achieved leads goal by k
            mae = float(np.mean(np.abs(shifted)))
            if mae < best_mae:
                best_mae, best_k = mae, k
        m["lag_s"] = best_k * dt_med
        m["lag_corrected_tw_mae_bar"] = best_mae
    else:
        m["lag_s"] = None
        m["lag_corrected_tw_mae_bar"] = None
    return m


def _summarize(per_shot):
    out = {"n_shots": len(per_shot)}
    for metric in _METRICS:
        vals = [s[metric] for s in per_shot if s.get(metric) is not None]
        if vals:
            arr = np.asarray(vals, float)
            out[metric] = {"n": len(vals), "median": float(np.median(arr)),
                           "p25": float(np.percentile(arr, 25)),
                           "p75": float(np.percentile(arr, 75))}
        else:
            out[metric] = {"n": 0, "median": None, "p25": None, "p75": None}
    # command-shape mix (categorical)
    shapes = {}
    for s in per_shot:
        shapes[s.get("command_shape", "unknown")] = shapes.get(s.get("command_shape", "unknown"), 0) + 1
    out["command_shape_counts"] = dict(sorted(shapes.items()))
    return out


def pressure_atlas(snapshot):
    """Time-weighted pressure tracking atlas over eligible shots: overall, by source family,
    and a STORE-ORDER-INDEPENDENT one-shot-per-user sensitivity (WP2.7 stopgap: the
    lexicographically-smallest shot id per user; seeded bootstrap in PR5). Tracking-BEHAVIOUR
    distributions, not machine rankings."""
    by_source, all_shots = {}, []
    per_user = {}          # key -> (shot_id, metrics) ; deterministic pick = min shot id
    n_excluded = 0
    for shot in snapshot.latest():
        if is_included(shot, "pressure_tracking_valid") is not None:
            n_excluded += 1
            continue
        m = pressure_tracking_metrics(shot)
        if m is None:
            n_excluded += 1
            continue
        src = (shot.get("context") or {}).get("integration_source") or "unknown"
        m = dict(m, _source=src)
        all_shots.append(m)
        by_source.setdefault(src, []).append(m)
        hu, sid = shot.get("hashed_user"), str(shot.get("id"))
        key = hu if hu is not None else ("__nouser__", sid)
        cur = per_user.get(key)
        if cur is None or sid < cur[0]:
            per_user[key] = (sid, m)
    one_per_user = [v[1] for v in per_user.values()]
    results = {
        "n_eligible": len(all_shots),
        "n_excluded": n_excluded,
        "overall": _summarize(all_shots),
        "by_source_family": {src: _summarize(v) for src, v in sorted(by_source.items())},
        "one_shot_per_user": _summarize(one_per_user),
    }
    return product_envelope(
        snapshot, "pressure_tracking_atlas", results,
        config={"eligibility": "pressure_tracking_valid",
                "achieved_channel": _ACHIEVED, "goal_channel": _GOAL,
                "spec_version": SPEC["spec_version"], "spec_hash": SPEC_HASH, "spec": SPEC},
        metric_defs=_METRIC_DEFS)
