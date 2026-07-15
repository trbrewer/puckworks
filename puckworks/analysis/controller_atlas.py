"""P2 commanded-vs-achieved atlas — PRESSURE FIRST (WP1.4).

Pressure is the cleanest first tranche because its quantity semantics are unambiguous
(`pressure__Pa` achieved vs `pressure_goal__Pa` commanded, both SI). Per-shot tracking
metrics are summarized as DISTRIBUTIONS (not machine rankings), aggregated by source family
and with a one-shot-per-user sensitivity. Flow tracking is deliberately NOT here: proxy/
volumetric/mass flow must not be pooled until the quantity dictionary resolves them.
"""
import numpy as np

from puckworks.data import visualizer_store as vs
from puckworks.analysis import product_envelope
from puckworks.analysis.visualizer_eligibility import is_included

_BAR = 1.0e5   # Pa per bar (report metrics in bar for readability)

_ACHIEVED = "pressure__Pa"
_GOAL = "pressure_goal__Pa"

# fail fast if these are ever changed to ambiguous channels (P0.4 guardrail)
assert vs.is_pooling_safe(_ACHIEVED) and vs.is_pooling_safe(_GOAL)

_METRICS = ("coverage_s", "n_goal_transitions", "rmse_bar", "nrmse",
            "median_abs_err_bar", "p90_abs_err_bar", "mean_signed_err_bar",
            "max_overshoot_bar")

_METRIC_DEFS = {
    "coverage_s": "time span over samples where time, pressure, and goal are all present",
    "n_goal_transitions": "count of changes in the commanded pressure goal",
    "rmse_bar": "RMS(achieved - goal) in bar",
    "nrmse": "rmse / (goal max-min); null when the goal is ~constant",
    "median_abs_err_bar": "median |achieved - goal| in bar",
    "p90_abs_err_bar": "90th-percentile |achieved - goal| in bar",
    "mean_signed_err_bar": "mean(achieved - goal) in bar (tracking bias)",
    "max_overshoot_bar": "max(achieved - goal, 0) in bar (peak overshoot)",
}


def pressure_tracking_metrics(shot):
    """Per-shot pressure commanded-vs-achieved metrics, or None if the shot lacks aligned
    time/pressure/goal samples. Values are in bar / seconds."""
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
    T = np.asarray(T); A = np.asarray(A); G = np.asarray(G)
    err = (A - G) / _BAR                      # bar
    goal_bar = G / _BAR
    goal_range = float(goal_bar.max() - goal_bar.min())
    rmse = float(np.sqrt(np.mean(err ** 2)))
    return {
        "coverage_s": float(T[-1] - T[0]),
        "n_goal_transitions": int(np.count_nonzero(np.diff(G) != 0)),
        "rmse_bar": rmse,
        "nrmse": (rmse / goal_range) if goal_range > 1e-9 else None,
        "median_abs_err_bar": float(np.median(np.abs(err))),
        "p90_abs_err_bar": float(np.percentile(np.abs(err), 90)),
        "mean_signed_err_bar": float(np.mean(err)),
        "max_overshoot_bar": float(max(np.max(err), 0.0)),
    }


def _summarize(per_shot):
    """count + median + IQR for each metric over a list of per-shot metric dicts."""
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
    return out


def pressure_atlas(snapshot):
    """Build the pressure tracking atlas over eligible shots. Aggregates overall, by source
    family, and one-shot-per-user. Returns a deterministic product envelope; describe the
    output as tracking-BEHAVIOR distributions, not machine rankings."""
    by_source, all_shots, first_per_user = {}, [], []
    seen_users = set()
    for shot in snapshot.latest():
        if is_included(shot, "pressure_tracking_valid") is not None:
            continue
        m = pressure_tracking_metrics(shot)
        if m is None:
            continue
        src = (shot.get("context") or {}).get("integration_source") or "unknown"
        m = dict(m, _source=src)
        all_shots.append(m)
        by_source.setdefault(src, []).append(m)
        hu = shot.get("hashed_user")
        if hu is None or hu not in seen_users:
            if hu is not None:
                seen_users.add(hu)
            first_per_user.append(m)
    results = {
        "overall": _summarize(all_shots),
        "by_source_family": {src: _summarize(v) for src, v in sorted(by_source.items())},
        "one_shot_per_user": _summarize(first_per_user),
    }
    return product_envelope(
        snapshot, "pressure_tracking_atlas", results,
        config={"eligibility": "pressure_tracking_valid",
                "achieved_channel": _ACHIEVED, "goal_channel": _GOAL},
        metric_defs=_METRIC_DEFS)
