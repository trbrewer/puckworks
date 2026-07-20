"""Drawing primitives for the tour's educational insight figures (#43, ROADMAP §8).

Each `figure_*` is a PURE draw: it consumes a producer's output dict (never recomputes physics) + the
relationship analyzer and returns ``(matplotlib.Figure, caption)`` where every number in the caption is
recomputed from the data. Small multiples (one unit per axis, never a dual y-axis), markers + line styles
(colour is never the sole encoding), units on every axis, and the reference scenario marked. The
`render_*` wrappers give the gallery the standard ``(spec, outdir, ...)`` signature and stamp/save via the
registry, so the gallery and the notebook draw with the SAME primitive.
"""
from __future__ import annotations

from .relationship import classify_relationship, describe

_REF = "#b91c1c"       # reference-scenario marker
_LINE = "#0e7490"
_MARKERS = ["o", "s", "^", "D", "v"]


def _plt():
    import matplotlib.pyplot as plt
    return plt


def _panel(ax, x, y, xlabel, ylabel, ref_x=None, marker="o"):
    ax.plot(x, y, marker + "-", color=_LINE, markersize=5, lw=1.6)
    if ref_x is not None and ref_x in x:
        i = x.index(ref_x)
        ax.plot([x[i]], [y[i]], "*", color=_REF, markersize=15, zorder=5)
    ax.set_xlabel(xlabel, fontsize=8)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.tick_params(labelsize=7)
    ax.grid(True, alpha=0.25)


def figure_cameron_pressure_sweep(data: dict):
    plt = _plt()
    P = data["pressure_bar"]
    fig, axes = plt.subplots(2, 2, figsize=(7.4, 5.0))
    _panel(axes[0, 0], P, data["mean_flow_g_s"], "pressure (bar)", "mean flow (g/s)",
           data["reference_pressure_bar"], "o")
    _panel(axes[0, 1], P, data["shot_duration_s"], "pressure (bar)", "shot time (s)",
           data["reference_pressure_bar"], "s")
    _panel(axes[1, 0], P, data["extraction_yield_pct"], "pressure (bar)", "extraction yield (%)",
           data["reference_pressure_bar"], "^")
    _panel(axes[1, 1], P, data["tds_pct"], "pressure (bar)", "strength / TDS (%)",
           data["reference_pressure_bar"], "D")
    fig.suptitle("Does more pressure make a stronger espresso? (Cameron model)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    flow = classify_relationship(P, data["mean_flow_g_s"])
    ey = classify_relationship(P, data["extraction_yield_pct"])
    tds = classify_relationship(P, data["tds_pct"])
    f = data["fixed"]
    skipped = (f" Pressures outside the model's range were skipped: {data['domain_skipped_bar']}."
               if data.get("domain_skipped_bar") else "")
    caption = (
        f"**Question — does more pressure make a stronger, more-extracted shot?** We vary only pressure "
        f"({P[0]:g}–{P[-1]:g} bar) at fixed dose {f['dose_g']:g} g, grind {f['grind_setting']:g}, and "
        f"{f['target_beverage_g']:g} g beverage. **In this model:** {describe(flow, 'flow', 'pressure', 'g/s')}; "
        f"{describe(ey, 'extraction yield', 'pressure', '%')}; and {describe(tds, 'strength/TDS', 'pressure', '%')}. "
        f"**Why:** higher pressure pushes water through faster, so the fixed cup mass is reached in less "
        f"time — and less contact time means less dissolved coffee, not more. **The surprising part:** "
        f"'more pressure' does NOT mean 'stronger' here — because reaching the same 40 g faster shortens "
        f"the time available for extraction.{skipped} This is an exploratory saturated-bed simulation of "
        f"extraction-yield/strength trends only; it is not a flavour, wetting, channeling, or thermal "
        f"prediction, and does not represent every real machine.")
    return fig, caption


def figure_cameron_beverage_sweep(data: dict):
    plt = _plt()
    B = data["target_beverage_g"]
    fig, axes = plt.subplots(1, 3, figsize=(9.6, 3.2))
    _panel(axes[0], B, data["extraction_yield_pct"], "beverage mass (g)", "extraction yield (%)",
           data["reference_beverage_g"], "^")
    _panel(axes[1], B, data["tds_pct"], "beverage mass (g)", "strength / TDS (%)",
           data["reference_beverage_g"], "D")
    _panel(axes[2], B, data["extracted_mass_g"], "beverage mass (g)", "extracted soluble mass (g)",
           data["reference_beverage_g"], "o")
    fig.suptitle("Why can collecting more coffee raise extraction yet weaken the drink? (Cameron model)",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    ey = classify_relationship(B, data["extraction_yield_pct"])
    tds = classify_relationship(B, data["tds_pct"])
    f = data["fixed"]
    caption = (
        f"**Question — if we collect more liquid, do we get more coffee or a weaker drink?** We vary only "
        f"the target beverage mass ({B[0]:g}–{B[-1]:g} g, brew ratio {B[0]/f['dose_g']:.1f}–"
        f"{B[-1]/f['dose_g']:.1f}) at fixed dose {f['dose_g']:g} g, {f['pressure_bar']:g} bar, grind "
        f"{f['grind_setting']:g}. **In this model:** {describe(ey, 'extraction yield', 'beverage mass', '%')}, "
        f"while {describe(tds, 'strength/TDS', 'beverage mass', '%')}. **Why:** running more water keeps "
        f"pulling soluble coffee out of the grounds (yield rises), but that extra water also dilutes what "
        f"is already in the cup (strength falls). **Why it matters:** this is the core extraction-vs-"
        f"dilution trade-off — a bigger drink can be *more extracted yet less concentrated* at the same "
        f"time. Exploratory saturated-bed simulation of yield/strength only; not a taste prediction, and "
        f"the soluble ceiling is Cameron's, distinct from other models' ceilings.")
    return fig, caption


def figure_cameron_shot_timeseries(data: dict):
    plt = _plt()
    panels = data["panels"]
    n = len(panels)
    fig, axes = plt.subplots(n, 1, figsize=(7.2, 1.9 * n), squeeze=False)
    for ax, panel in zip(axes[:, 0], panels):
        for j, s in enumerate(panel["series"]):
            style = "--" if "prescribed" in s.get("role", "") else "-"
            ax.plot(panel["x"], s["y"], style, marker=_MARKERS[j % len(_MARKERS)], markersize=3,
                    label=s["label"])
        ax.set_xlabel(panel["x_label"], fontsize=8)
        ax.set_ylabel(panel["y_label"], fontsize=8)
        ax.legend(fontsize=6, loc="best")
        ax.tick_params(labelsize=7)
        ax.grid(True, alpha=0.25)
    axes[0, 0].set_title("The whole simulated shot over time (Cameron model)", fontsize=10)
    fig.tight_layout()
    f = data["fixed"]
    caption = (
        f"**Question — what does the whole simulated shot look like moment to moment?** At {f['dose_g']:g} g "
        f"dose, {f['target_beverage_g']:g} g out, {f['pressure_bar']:g} bar, each panel keeps ONE unit on "
        f"its axis (never mixing units). **Prescribed** inputs (pressure, target cup) are dashed; "
        f"**simulated** outputs (flow, outlet concentration, cumulative dissolved mass, extraction yield, "
        f"strength) are solid. **What to notice:** some quantities are instantaneous (flow, outlet "
        f"concentration) while others are cumulative (dissolved mass, yield) and only ever rise. **Scope:** "
        f"an exploratory, already-saturated-bed simulation — it begins with a wet puck, so it does NOT show "
        f"puck wetting, a physical first drip, a dynamic pressure profile, a thermal transient, channeling, "
        f"or flavour.")
    return fig, caption


# ── gallery render_fn wrappers (same (spec, outdir, ...) signature the registry expects) ──
def _render(spec, outdir, pure_fn):
    from .registry import producer_data, save_figure
    fig, _caption = pure_fn(producer_data(spec))
    thumb = save_figure(fig, spec, outdir)
    return {"id": spec.id, "thumb": thumb}


def render_cameron_pressure_sweep(spec, outdir, with_3d=False, video=False):
    return _render(spec, outdir, figure_cameron_pressure_sweep)


def render_cameron_beverage_sweep(spec, outdir, with_3d=False, video=False):
    return _render(spec, outdir, figure_cameron_beverage_sweep)


def render_cameron_shot_timeseries(spec, outdir, with_3d=False, video=False):
    return _render(spec, outdir, figure_cameron_shot_timeseries)


# ── reused-VizSpec educational draws (consume the EXISTING light producers) ──────────────
def figure_wetting_front(data: dict):
    """foster2025.infiltration: wetting-front position s(t) — how fast water soaks the dry puck."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.plot(data["t_s"], data["front_mm"], "-", color=_LINE, lw=1.8)
    ts = data.get("t_saturate_s")
    if ts is not None:
        ax.axvline(ts, color=_REF, ls="--", lw=1.2)
        ax.annotate(f"puck full ≈ {ts:.1f} s", (ts, data["front_mm"][-1] * 0.5),
                    fontsize=8, color=_REF, ha="right")
    ax.set_xlabel("time (s)"); ax.set_ylabel("wetting-front depth (mm)")
    ax.set_title("How fast does water soak through the dry puck? (Foster infiltration)", fontsize=10)
    ax.grid(True, alpha=0.25); fig.tight_layout()
    caption = (
        f"**Question — how quickly does water reach the bottom of a dry puck?** The model advances a sharp "
        f"wetting front from a recorded pressure history. **In this model** the front reaches the full "
        f"{data['params'].get('L_mm', data.get('L_mm'))} mm bed at about {ts:.1f} s. **Why it matters:** even, "
        f"complete wetting before flow starts is what lets the whole puck extract together. **Scope:** the "
        f"front is a SHARP binary boundary — the model says nothing about partial saturation behind it or "
        f"dry-pocket channeling; fine grind, CT-validated; a reconstruction, not your machine.")
    return fig, caption


def figure_stokes_profile(data: dict):
    """brewer2026.lb_reference: velocity profile across the verification channel."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.plot(data["u_profile"], data["z"], "-o", color=_LINE, markersize=3)
    ax.set_xlabel("flow speed (lattice units)"); ax.set_ylabel("position across channel (lattice nodes)")
    ax.set_title("Why is flow fastest in the middle and zero at the walls? (LB verification)", fontsize=10)
    ax.grid(True, alpha=0.25); fig.tight_layout()
    caption = (
        f"**Question — how does speed vary across a channel of flowing water?** **In this model** the speed "
        f"is zero at both walls (no-slip) and highest in the centre ({data['u_max']:.3g} lattice units) — a "
        f"parabola. **Why:** friction at the walls holds water back, so the middle carries most of the flow. "
        f"**Why it is trustworthy:** the lattice-Boltzmann solver matches the exact analytic profile to "
        f"{data['lb_err_pct_vs_analytic']:.2g}%. **Scope:** this is VERIFICATION geometry (a clean channel), "
        f"not the flow in your puck, and Stokes-regime only.")
    return fig, caption


def figure_pack_slice(data: dict):
    """brewer2026.pack_generator: a 2-D slice of the synthetic Boolean-sphere pack."""
    plt = _plt()
    import numpy as np
    fig, ax = plt.subplots(figsize=(4.8, 4.6))
    ax.imshow(np.array(data["solid_slice"]).T, origin="lower", cmap="Greys", interpolation="nearest")
    ax.set_xlabel("x (lattice)"); ax.set_ylabel("z (lattice)")
    ax.set_title("A synthetic coffee puck (Boolean spheres)", fontsize=10)
    fig.tight_layout()
    caption = (
        f"**Question — what does the model's 'puck' actually look like?** A 2-D slice through the synthetic "
        f"packing (solid coffee dark, pore space light), solid fraction {data['phis']:.2f}. **Why it "
        f"matters:** where the packing is looser, water finds easier paths — weak spots concentrate flow "
        f"and cause uneven extraction. **Scope:** SYNTHETIC Boolean-sphere geometry, not a scan of a real "
        f"puck; fines are a sub-voxel heterogeneity field, not resolved particles.")
    return fig, caption


def figure_fines_qinf(data: dict):
    """fasano2000_partI.fines_migration: long-time flow q∞ vs driving pressure p0 (may be non-monotonic)."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    p0, q = list(data["p0_bar"]), list(data["q_inf"])
    ax.plot(p0, q, "-o", color=_LINE, markersize=5)
    rel = classify_relationship(p0, q)
    if rel.turning_x is not None:
        ax.plot([rel.turning_x], [rel.y_turning], "*", color=_REF, markersize=15, zorder=5)
    ax.set_xlabel("driving pressure p₀ (bar)"); ax.set_ylabel("long-time flow q∞ (model units)")
    ax.set_title("Can more pressure eventually give LESS flow when fines compact? (Fasano-structured)",
                 fontsize=10)
    ax.grid(True, alpha=0.25); fig.tight_layout()
    caption = (
        f"**Question — does pushing harder always give more flow once fines can move?** **In this model** "
        f"{describe(rel, 'the long-time flow', 'driving pressure')}. **Why:** higher pressure both drives "
        f"flow and packs mobile fines into a tighter, more resistant layer — two effects that can oppose "
        f"each other. **Why it is interesting:** a non-monotonic response would mean more pressure is not "
        f"always more flow. **Scope:** a MECHANISM ILLUSTRATION — the closures are Puckworks', not the "
        f"paper's, with zero identified coffee parameters; not a coffee fit.")
    return fig, caption


def figure_channeling(data: dict):
    """brewer2026.streamtube / N-tube: flow concentration over time (one configuration)."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.plot(data["time_s"], data["max_share"], "-", color=_LINE, lw=1.8)
    ax.set_xlabel("time (s)"); ax.set_ylabel("largest single-path flow share")
    ax.set_title("Can uneven paths concentrate the flow? (one configuration)", fontsize=10)
    ax.grid(True, alpha=0.25); fig.tight_layout()
    cfg = data.get("config", {})
    caption = (
        f"**Question — when paths differ, does flow spread out or concentrate?** **In this model** the "
        f"largest single path's share of the flow climbs over the shot, and the effective number of active "
        f"paths falls to N_eff/N ≈ {data['n_eff_over_N']:.2g}. **Why:** a slightly faster path extracts and "
        f"opens further, pulling in still more water — a run-away that starves the rest. **Why it matters:** "
        f"this is channeling — over-extracted fast lanes and under-extracted slow ones. **Scope:** ONE "
        f"configuration ({cfg}), an exploratory result under flow control, NOT a proven general instability.")
    return fig, caption
