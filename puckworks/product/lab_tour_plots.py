"""Figures for the Full Laboratory Tour's per-component novice cards (#43).

`component_figure(result, *, trace_panels=None)` renders ONE matplotlib figure from a component's ACTUAL
tour output — never fabricated — plus a plain-language caption describing what the figure shows. It handles
the output shapes the tour actually produces:

* common-scenario time series (via `trace_panels` from `lab.render_data`) — one line per trace, split by
  unit so incompatible units are never on one axis;
* numeric value outputs (native references + the common lens's final observables) — a labelled bar chart,
  including a measured-vs-reference comparison where the component reports both;
* a first-drip bracket (an observed value inside a predicted range);
* registered-gate metrics — the numeric metric(s), coloured by PASS/FAIL, with any numeric series drawn as
  a small line.

Blocked / optional / no-output components return ``None`` (the card shows a status note, not a fake plot).
Matplotlib/pyplot is imported lazily and the backend is NOT forced here — so in a notebook the figures
embed inline, and in a headless script matplotlib auto-selects a non-interactive backend.
"""
from __future__ import annotations

_ROLE_COLOR = {"simulated": "#0e7490", "analytic_reference": "#b45309", "reference": "#b45309",
               "fitted": "#0e7490", "derived": "#6b7280", "prescribed": "#9ca3af", "measured": "#0e7490",
               "predicted": "#7c3aed"}
_PASS_COLOR = "#15803d"
_FAIL_COLOR = "#b91c1c"


def _fig():
    # do NOT force a backend: a notebook keeps its inline backend (figures embed); a headless script
    # falls back to matplotlib's auto-selected non-interactive backend.
    import matplotlib.pyplot as plt
    return plt


def _numeric_value_outputs(outputs):
    out = []
    for o in outputs:
        v = o.get("value")
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            continue
        out.append((o["name"], float(v), o.get("unit", ""), o.get("role", "")))
    return out


def _bracket(outputs):
    """(observed, lo, hi, unit) for a first-drip-style card, else None."""
    obs = lo = hi = unit = None
    for o in outputs:
        v = o.get("value")
        if isinstance(v, (int, float)) and not isinstance(v, bool) and "observed" in o["name"]:
            obs, unit = float(v), o.get("unit", unit)
        if isinstance(v, list) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
            lo, hi = float(v[0]), float(v[1])
            unit = o.get("unit", unit)
    if obs is not None and lo is not None:
        return obs, lo, hi, unit or ""
    return None


def _time_series_figure(panels, title):
    plt = _fig()
    n = len(panels)
    fig, axes = plt.subplots(n, 1, figsize=(7.2, 2.4 * n), squeeze=False)
    for ax, panel in zip(axes[:, 0], panels):
        for s in panel["series"]:
            style = "--" if s.get("role") == "prescribed_input" else "-"
            ax.plot(panel["x"], s["y"], style, label=f"{s['label']}")
        ax.set_xlabel(panel["x_label"])
        ax.set_ylabel(panel["y_label"])
        ax.legend(fontsize=7, loc="best")
    axes[0, 0].set_title(title, fontsize=10)
    fig.tight_layout()
    units = ", ".join(sorted({p["unit"] for p in panels}))
    caption = (f"How the shot develops over time ({units}). Each panel keeps one unit on its axis; "
               f"prescribed inputs are dashed, model outputs solid. Reading left to right is the timeline "
               f"of the pull.")
    return fig, caption


def _bracket_figure(obs, lo, hi, unit, title):
    plt = _fig()
    fig, ax = plt.subplots(figsize=(7.2, 1.9))
    ax.hlines(0, lo, hi, color="#7c3aed", lw=8, alpha=0.35)
    ax.plot([lo, hi], [0, 0], "|", color="#7c3aed", markersize=16)
    ax.plot([obs], [0], "o", color="#0e7490", markersize=11, zorder=3)
    ax.annotate(f"observed {obs:g} {unit}", (obs, 0), textcoords="offset points", xytext=(0, 12),
                ha="center", fontsize=9)
    ax.annotate(f"predicted {lo:g}–{hi:g} {unit}", ((lo + hi) / 2, 0), textcoords="offset points",
                xytext=(0, -18), ha="center", fontsize=8, color="#7c3aed")
    ax.set_yticks([])
    ax.set_xlabel(unit)
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    inside = lo <= obs <= (hi if hi is not None else obs)
    caption = (f"The observed value ({obs:g} {unit}) falls {'inside' if inside else 'outside'} the model's "
               f"predicted range ({lo:g}–{hi:g} {unit}) — a compatibility check, not an exact prediction.")
    return fig, caption


def _values_figure(numeric, title):
    plt = _fig()
    names = [n for n, _, _, _ in numeric]
    vals = [v for _, v, _, _ in numeric]
    colors = [_ROLE_COLOR.get(r, "#0e7490") for _, _, _, r in numeric]
    fig, ax = plt.subplots(figsize=(7.2, max(2.0, 0.55 * len(numeric) + 1.0)))
    ax.barh(range(len(numeric)), vals, color=colors)
    ax.set_yticks(range(len(numeric)))
    ax.set_yticklabels([f"{n}" for n in names], fontsize=8)
    for i, (_, v, u, _) in enumerate(numeric):
        ax.annotate(f" {v:g} {u}".rstrip(), (v, i), va="center", fontsize=8)
    ax.invert_yaxis()
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    roles = sorted({r for _, _, _, r in numeric if r})
    caption = ("The model's output values" + (f" ({', '.join(roles)})" if roles else "")
               + ". Bars sharing a colour share a role (e.g. a simulated value next to its reference).")
    return fig, caption


def _gate_figure(gate_outputs, title):
    plt = _fig()
    # collect scalar numeric metrics (with their pass/fail) and the first numeric series, across gates
    bars = []          # (label, value, passed)
    series = None      # (label, [values])
    for g in gate_outputs:
        passed = g.get("status") == "PASS"
        for k, v in (g.get("metrics") or {}).items():
            if isinstance(v, bool):
                continue
            if isinstance(v, (int, float)):
                bars.append((f"{k}", float(v), passed))
            elif isinstance(v, list) and v and all(isinstance(x, (int, float)) for x in v) and series is None:
                series = (f"{g['gate_id']}: {k}", [float(x) for x in v])
    if not bars and not series:
        return None
    rows = 1 + (1 if (bars and series) else 0)
    fig, axes = plt.subplots(rows, 1, figsize=(7.2, 2.2 * rows), squeeze=False)
    ax_i = 0
    if bars:
        ax = axes[ax_i, 0]
        bars = bars[:8]
        ax.barh(range(len(bars)), [v for _, v, _ in bars],
                color=[_PASS_COLOR if p else _FAIL_COLOR for _, _, p in bars])
        ax.set_yticks(range(len(bars)))
        ax.set_yticklabels([lab for lab, _, _ in bars], fontsize=8)
        for i, (_, v, _) in enumerate(bars):
            ax.annotate(f" {v:g}", (v, i), va="center", fontsize=8)
        ax.invert_yaxis()
        ax.set_title(title, fontsize=10)
        ax_i += 1
    if series:
        ax = axes[ax_i, 0]
        ax.plot(range(len(series[1])), series[1], "-o", color="#0e7490")
        ax.set_title(series[0], fontsize=9)
        ax.set_xlabel("condition index")
    fig.tight_layout()
    caption = ("The model's registered scientific-check numbers (green = the check passed, red = failed). "
               "These are consistency/self-check metrics, not measured cup outcomes.")
    return fig, caption


def component_figure(result: dict, *, trace_panels=None):
    """(matplotlib Figure, caption) for a component's tour result, or None when there is nothing real to
    plot (blocked / optional / no numeric output). Never fabricates data."""
    status = result.get("execution_status")
    if status not in ("EXECUTED", "CHECK_FAILED"):
        return None
    cid = result["component_id"]
    title = f"{result.get('stage', '').replace('_', ' ')}: {cid}"
    if trace_panels:
        return _time_series_figure(trace_panels, title)
    outputs = result.get("outputs", [])
    br = _bracket(outputs)
    if br:
        return _bracket_figure(*br, title)
    numeric = _numeric_value_outputs(outputs)
    if numeric:
        return _values_figure(numeric, title)
    gate_outputs = [o for o in outputs if "gate_id" in o]
    if gate_outputs:
        return _gate_figure(gate_outputs, title)
    return None
