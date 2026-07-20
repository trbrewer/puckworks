"""Drawing primitives for the tour's educational insight figures (#43, ROADMAP §8).

Each ``figure_*`` is a PURE draw: it consumes a producer's output dict (never recomputes physics) + the
relationship analyzer and returns ``(matplotlib.Figure, TourFigureNarrative)`` where every number in the
narrative is recomputed from the data. Layout, typography, and the reserved badge/scope bands come from
``tour_style`` — the draw never calls ``tight_layout()`` and never stamps text over an Axes. Small
multiples keep one unit per axis (never a dual y-axis), markers + line styles (colour is never the sole
encoding), units on every axis, and the reference scenario marked with an explained key.

Presentation:
  * ``presentation="notebook"`` — the notebook already prints the headline + question, so the figure does
    NOT repeat them (only concise panel titles remain); this is what ``component_figures`` requests.
  * ``presentation="standalone"`` — a concise title is drawn in the reserved header (gallery/thumbnails).

The ``render_*`` wrappers give the gallery the standard ``(spec, outdir, ...)`` signature and stamp/save
via the registry, so the gallery and the notebook draw with the SAME primitive.
"""
from __future__ import annotations

from . import tour_style as TS
from .relationship import classify_relationship, describe
from .tour_style import TourFigureNarrative


# ── Cameron hero figures ──────────────────────────────────────────────────────────────────
def figure_cameron_pressure_sweep(data: dict, *, presentation="notebook", ceiling="", title=""):
    P = data["pressure_bar"]
    ref = data["reference_pressure_bar"]
    f = data["fixed"]
    tgt = f["target_beverage_g"]
    fig, ax = TS.tour_figure(2, 2, figsize=(9.6, 6.4), ceiling=ceiling, presentation=presentation,
                             title=title, has_reference_key=True, sharex=True)
    key = None
    TS.plot_curve(ax[0, 0], P, data["mean_flow_g_s"], marker="o")
    TS.style_axis(ax[0, 0], ylabel="Mean beverage flow (g/s)", title="Mean flow")
    key = TS.mark_reference(ax[0, 0], P, data["mean_flow_g_s"], ref,
                            label=f"Your selected pressure: {ref:g} bar")
    TS.plot_curve(ax[0, 1], P, data["shot_duration_s"], marker="s")
    TS.style_axis(ax[0, 1], ylabel=f"Time to reach {tgt:g} g (s)", title="Time to target mass")
    TS.mark_reference(ax[0, 1], P, data["shot_duration_s"], ref)
    TS.plot_curve(ax[1, 0], P, data["extraction_yield_pct"], marker="^")
    TS.style_axis(ax[1, 0], ylabel="Extraction yield (%)", title="Extraction yield")
    TS.mark_reference(ax[1, 0], P, data["extraction_yield_pct"], ref)
    TS.plot_curve(ax[1, 1], P, data["tds_pct"], marker="D")
    TS.style_axis(ax[1, 1], ylabel="Strength (TDS, %)", title="Strength")
    TS.mark_reference(ax[1, 1], P, data["tds_pct"], ref)
    for a in ax[0, :]:
        a.tick_params(labelbottom=False)
    TS.shared_xlabel(fig, "Pressure (bar)")
    TS.reference_key(fig, [key])

    flow = classify_relationship(P, data["mean_flow_g_s"])
    ey = classify_relationship(P, data["extraction_yield_pct"])
    tds = classify_relationship(P, data["tds_pct"])
    skipped = (f" Pressures outside the model's range were skipped: {data['domain_skipped_bar']}."
               if data.get("domain_skipped_bar") else "")
    nar = TourFigureNarrative(
        setup=(f"Pressure changes from {P[0]:g} to {P[-1]:g} bar. Dose ({f['dose_g']:g} g), grind "
               f"({f['grind_setting']:g}), and target beverage mass ({tgt:g} g) stay fixed."),
        finding=(f"In this model {describe(flow, 'mean flow', 'pressure', 'g/s')}; "
                 f"{describe(ey, 'extraction yield', 'pressure', '%')}; and "
                 f"{describe(tds, 'strength', 'pressure', '%')}."),
        mechanism=(f"Higher pressure pushes water through faster, so the fixed {tgt:g} g cup is reached in "
                   f"less time — and less contact time means less dissolved coffee, not more."),
        takeaway=("'More pressure' does not mean 'stronger' here: reaching the same target mass faster "
                  "shortens the time available for extraction."),
        scope=("An exploratory saturated-bed simulation of extraction-yield and strength trends only — not "
               "a flavour, wetting, channeling, or thermal prediction, and not every real machine." +
               skipped))
    return fig, nar


def figure_cameron_beverage_sweep(data: dict, *, presentation="notebook", ceiling="", title=""):
    B = data["target_beverage_g"]
    ref = data["reference_beverage_g"]
    f = data["fixed"]
    fig, ax = TS.tour_figure(1, 3, figsize=(10.6, 4.0), ceiling=ceiling, presentation=presentation,
                             title=title, has_reference_key=True)
    TS.plot_curve(ax[0, 0], B, data["extraction_yield_pct"], marker="^")
    TS.style_axis(ax[0, 0], ylabel="Extraction yield (%)", title="Extraction yield")
    key = TS.mark_reference(ax[0, 0], B, data["extraction_yield_pct"], ref,
                            label=f"Your selected beverage mass: {ref:g} g")
    TS.plot_curve(ax[0, 1], B, data["tds_pct"], marker="D")
    TS.style_axis(ax[0, 1], ylabel="Strength (TDS, %)", title="Strength")
    TS.mark_reference(ax[0, 1], B, data["tds_pct"], ref)
    TS.plot_curve(ax[0, 2], B, data["extracted_mass_g"], marker="o")
    TS.style_axis(ax[0, 2], ylabel="Soluble coffee extracted (g)", title="Extracted mass")
    TS.mark_reference(ax[0, 2], B, data["extracted_mass_g"], ref)
    TS.shared_xlabel(fig, "Target beverage mass (g)")
    TS.reference_key(fig, [key])

    ey = classify_relationship(B, data["extraction_yield_pct"])
    tds = classify_relationship(B, data["tds_pct"])
    br = data.get("brew_ratio", [B[0] / f["dose_g"], B[-1] / f["dose_g"]])
    nar = TourFigureNarrative(
        setup=(f"The target beverage mass changes from {B[0]:g} to {B[-1]:g} g (brew ratio "
               f"{br[0]:.1f}–{br[-1]:.1f}). Dose ({f['dose_g']:g} g), pressure ({f['pressure_bar']:g} bar), "
               f"and grind ({f['grind_setting']:g}) stay fixed."),
        finding=(f"In this model {describe(ey, 'extraction yield', 'beverage mass', '%')}, while "
                 f"{describe(tds, 'strength', 'beverage mass', '%')}; the total soluble coffee extracted "
                 f"keeps rising."),
        mechanism=("Running more water keeps pulling soluble coffee out of the grounds (yield rises), but "
                   "that same extra water dilutes what is already in the cup (strength falls)."),
        takeaway=("The core extraction-versus-dilution trade-off: a bigger drink can be more extracted yet "
                  "less concentrated at the same time."),
        scope=("An exploratory saturated-bed simulation of yield and strength only — not a taste "
               "prediction; the soluble ceiling is Cameron's, distinct from other models' ceilings."))
    return fig, nar


def figure_cameron_shot_timeseries(data: dict, *, presentation="notebook", ceiling="", title=""):
    panels = data["panels"]
    n = len(panels)
    f = data["fixed"]
    fig, ax = TS.tour_figure(n, 1, figsize=(7.8, 1.7 * n + 1.9), ceiling=ceiling,
                             presentation=presentation, title=title, has_reference_key=True)
    col = ax[:, 0]
    # share the TIME axis among the time-based panels (all but any spatial-profile panel)
    time_idx = [i for i, p in enumerate(panels) if p["x_label"].startswith("time")]
    for i in time_idx[1:]:
        col[i].sharex(col[time_idx[0]])
    for i, (a, p) in enumerate(zip(col, panels)):
        s = p["series"][0]
        dashed = "prescribed" in s.get("role", "")
        TS.plot_curve(a, p["x"], s["y"], marker="", ls="--" if dashed else "-")
        TS.style_axis(a, ylabel=p["unit"], title=s["label"])
        # time label only on the last time panel; the spatial panel keeps its own label
        if i in time_idx and i != time_idx[-1]:
            a.tick_params(labelbottom=False)
        elif i == time_idx[-1]:
            a.set_xlabel("Time (s)", fontsize=TS.FS_AXIS_LABEL)
        else:
            a.set_xlabel(p["x_label"].capitalize(), fontsize=TS.FS_AXIS_LABEL)
    from matplotlib.lines import Line2D
    TS.reference_key(fig, [
        Line2D([0], [0], color=TS.LINE, lw=1.7, ls="-", label="Simulated output"),
        Line2D([0], [0], color=TS.LINE, lw=1.7, ls="--", label="Prescribed input")])

    nar = TourFigureNarrative(
        setup=(f"At {f['dose_g']:g} g dose, {f['target_beverage_g']:g} g out, {f['pressure_bar']:g} bar, "
               f"each panel keeps one unit on its own axis across the whole shot."),
        finding=("Prescribed inputs (pump pressure, target cup) are dashed; simulated outputs (flow, "
                 "dissolved mass, extraction yield, outlet concentration) are solid. Some quantities are "
                 "instantaneous, such as flow; others are cumulative, such as dissolved mass and yield, "
                 "and only ever rise."),
        mechanism=("The bed starts already wet, so flow and extraction build smoothly from the first "
                   "moment rather than waiting for the puck to soak."),
        scope=("An exploratory, already-saturated-bed simulation — it does not show puck wetting, a "
               "physical first drip, a dynamic pressure profile, a thermal transient, channeling, or "
               "flavour."))
    return fig, nar


# ── reused-VizSpec educational draws (consume the EXISTING light producers) ────────────────
def figure_wetting_front(data: dict, *, presentation="notebook", ceiling="", title=""):
    """foster2025.infiltration: wetting-front depth s(t), windowed to the event so it is visible."""
    t = list(data["t_s"])
    front = list(data["front_mm"])
    L = data["params"].get("L_mm", data.get("L_mm"))
    ts = data.get("t_saturate_s")
    fig, ax = TS.tour_figure(1, 1, figsize=(7.4, 4.0), ceiling=ceiling, presentation=presentation,
                             title=title)
    a = ax[0, 0]
    TS.plot_curve(a, t, front, marker="o")
    a.axhline(L, color=TS.WALL, ls=":", lw=1.2)
    a.text(0.98, L, f"full bed depth ({L:g} mm)", transform=a.get_yaxis_transform(),
           ha="right", va="bottom", fontsize=TS.FS_ANNOTATION, color=TS.WALL)
    # event-focused window: zero through several saturation times (never past the trace)
    if ts is not None and ts > 0:
        import numpy as np
        xmax = min(max(t), max(0.6, 10.0 * ts))
        a.set_xlim(0, xmax)
        y_at_ts = float(np.interp(ts, t, front))          # land the arrow on the curve
        TS.annotate_inside(a, f"puck full ≈ {ts:.2f} s", xy=(ts, y_at_ts),
                           xytext=(xmax * 0.34, L * 0.42))
    TS.style_axis(a, xlabel="Time (s)", ylabel="Wetting-front depth (mm)")

    st = f"{ts:.2f}" if ts is not None else "—"
    nar = TourFigureNarrative(
        setup="Water enters a dry puck; the model advances a sharp wetting front down through the bed.",
        finding=(f"In this model the front reaches the full {L:g} mm bed depth in about {st} s, then stays "
                 f"at full depth for the rest of the shot (only the early window is shown)."),
        mechanism=("Early flow rushes into dry, empty pore space, so the wetting boundary sweeps down the "
                   "puck almost immediately."),
        takeaway="Even, complete wetting before flow builds is what lets the whole puck extract together.",
        scope=("The front is a SHARP binary boundary — the model says nothing about partial saturation "
               "behind it or dry-pocket channeling; fine grind, CT-validated; a reconstruction, not your "
               "machine."))
    return fig, nar


def figure_stokes_profile(data: dict, *, presentation="notebook", ceiling="", title=""):
    """brewer2026.lb_reference: velocity profile across the channel, shown on a novice-readable scale."""
    import numpy as np
    u = np.asarray(data["u_profile"], float)
    z = np.asarray(data["z"], float)
    umax = data["u_max"]
    un = u / umax if umax else u
    zn = (z - z.min()) / (z.max() - z.min()) if z.max() > z.min() else z
    fig, ax = TS.tour_figure(1, 1, figsize=(7.2, 4.2), ceiling=ceiling, presentation=presentation,
                             title=title)
    a = ax[0, 0]
    a.plot(un, zn, marker="o", color=TS.LINE, markersize=4, lw=1.7)
    a.set_yticks([0.0, 0.5, 1.0])
    a.set_yticklabels(["lower wall", "centre", "upper wall"])
    a.set_xlim(-0.05, 1.12)
    TS.style_axis(a, xlabel="Flow speed (fraction of maximum)", ylabel="Position across channel")
    a.annotate("no slip", xy=(0.0, 0.0), xytext=(0.18, 0.08), fontsize=TS.FS_ANNOTATION, color=TS.WALL,
               arrowprops=dict(arrowstyle="->", color=TS.WALL, lw=1.0))
    a.annotate("no slip", xy=(0.0, 1.0), xytext=(0.18, 0.92), fontsize=TS.FS_ANNOTATION, color=TS.WALL,
               arrowprops=dict(arrowstyle="->", color=TS.WALL, lw=1.0))
    a.annotate("fastest flow", xy=(1.0, 0.5), xytext=(0.55, 0.62), fontsize=TS.FS_ANNOTATION,
               color=TS.REF, arrowprops=dict(arrowstyle="->", color=TS.REF, lw=1.0))

    err = data["lb_err_pct_vs_analytic"]
    nar = TourFigureNarrative(
        setup=("Water flows down a clean, straight verification channel; the model reports the speed at "
               "every height across it (shown as a fraction of the peak speed)."),
        finding=(f"Speed is zero at both walls (no slip) and highest at the centre — a parabola. The "
                 f"lattice-Boltzmann solver matches the exact analytic profile to {err:.2g}%. "
                 f"(The true peak speed is {umax:.2e} lattice units.)"),
        mechanism=("Friction at the walls holds the water back, so the middle of the channel carries most "
                   "of the flow."),
        scope=("This is VERIFICATION geometry (a clean channel), not the flow in your puck, and "
               "Stokes-regime only."))
    return fig, nar


def figure_pack_slice(data: dict, *, presentation="notebook", ceiling="", title=""):
    """brewer2026.pack_generator: compact landscape — solid/pore slice + heterogeneity field."""
    import numpy as np
    from matplotlib.patches import Patch
    solid = np.asarray(data["solid_slice"]).T
    hetero = np.asarray(data["hetero_slice"]).T
    fig, ax = TS.tour_figure(1, 2, figsize=(9.2, 4.4), ceiling=ceiling, presentation=presentation,
                             title=title)
    aL, aR = ax[0, 0], ax[0, 1]
    aL.imshow(solid, origin="lower", cmap="Greys", interpolation="nearest", aspect="equal")
    aL.set_title("Solid coffee and pore space", fontsize=TS.FS_PANEL_TITLE)
    aL.set_xticks([]); aL.set_yticks([])
    aL.legend(handles=[Patch(facecolor="black", label="solid coffee"),
                       Patch(facecolor="white", edgecolor="#999", label="pore space")],
              loc="lower center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=TS.FS_LEGEND,
              frameon=False)
    from .palette import FIELD_SEQUENTIAL
    im = aR.imshow(hetero, origin="lower", cmap=FIELD_SEQUENTIAL,
                   interpolation="nearest", aspect="equal")
    aR.set_title("Sub-voxel heterogeneity field", fontsize=TS.FS_PANEL_TITLE)
    aR.set_xticks([]); aR.set_yticks([])
    cbar = fig._tour_layout["plot"].colorbar(im, ax=aR, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=TS.FS_TICK)
    cbar.set_label("field value (a.u.)", fontsize=TS.FS_TICK)

    nar = TourFigureNarrative(
        setup=(f"A 2-D slice through the model's synthetic packing at solid fraction "
               f"{data['phis']:.2f} (dark is solid coffee, light is pore space)."),
        finding=("The right panel is the sub-voxel heterogeneity FIELD — a statistical stand-in for "
                 "fine-scale variation, NOT resolved fine particles."),
        mechanism=("Where the packing is looser, water finds easier paths; weak spots concentrate flow "
                   "and cause uneven extraction."),
        scope=("SYNTHETIC Boolean-sphere geometry, not a scan of a real puck; the heterogeneity field is "
               "a field, never imaged coffee or resolved fines."))
    return fig, nar


def figure_fines_qinf(data: dict, *, presentation="notebook", ceiling="", title=""):
    """fasano2000_partI.fines_migration: long-time flow q∞ vs driving pressure p0."""
    p0, q = list(data["p0_bar"]), list(data["q_inf"])
    fig, ax = TS.tour_figure(1, 1, figsize=(7.4, 4.0), ceiling=ceiling, presentation=presentation,
                             title=title)
    a = ax[0, 0]
    TS.plot_curve(a, p0, q, marker="o")
    rel = classify_relationship(p0, q)
    if rel.turning_x is not None:
        a.plot([rel.turning_x], [rel.y_turning], marker="*", color=TS.REF, markersize=15, zorder=6,
               linestyle="none")
        TS.annotate_inside(a, f"turning point ≈ {rel.turning_x:g} bar",
                           xy=(rel.turning_x, rel.y_turning),
                           xytext=(p0[0] + 0.15 * (p0[-1] - p0[0]), rel.y_turning))
    TS.style_axis(a, xlabel="Driving pressure p₀ (bar)", ylabel="Long-time flow q∞ (model units)")

    nar = TourFigureNarrative(
        setup=(f"Only the driving pressure p₀ changes ({p0[0]:g}–{p0[-1]:g} bar); the model reports the "
               f"long-run flow once mobile fines have settled."),
        finding=f"In this model {describe(rel, 'the long-time flow', 'driving pressure')}.",
        mechanism=("Higher pressure both drives flow and packs mobile fines into a tighter, more resistant "
                   "layer — two effects that can oppose each other."),
        takeaway="A non-monotonic response would mean more pressure is not always more flow.",
        scope=("A MECHANISM ILLUSTRATION — the closures are Puckworks', not the paper's, with zero "
               "identified coffee parameters; not a coffee fit."))
    return fig, nar


def figure_channeling(data: dict, *, presentation="notebook", ceiling="", title=""):
    """brewer2026.streamtube / N-tube: flow concentration over time (one configuration)."""
    t = list(data["time_s"])
    share = list(data["max_share"])
    fig, ax = TS.tour_figure(1, 1, figsize=(7.4, 4.0), ceiling=ceiling, presentation=presentation,
                             title=title)
    a = ax[0, 0]
    a.plot(t, share, color=TS.LINE, lw=1.9)
    ct = data.get("collapse_time_s")
    if ct is not None:
        a.axvline(ct, color=TS.REF, ls="--", lw=1.2)
        TS.annotate_inside(a, f"flow collapses to one path ≈ {ct:g} s", xy=(ct, 0.5),
                           xytext=(t[0] + 0.05 * (t[-1] - t[0]), 0.6))
    a.set_ylim(0, 1.05)
    TS.style_axis(a, xlabel="Time (s)", ylabel="Largest single-path flow share")

    cfg = data.get("config", {})
    nar = TourFigureNarrative(
        setup=(f"One fixed configuration ({cfg}); the model tracks the largest single path's share of the "
               f"total flow over the shot."),
        finding=(f"In this model the largest path's share of the flow climbs over the shot, and the "
                 f"effective number of active paths falls to N_eff/N ≈ {data['n_eff_over_N']:.2g}."),
        mechanism=("A slightly faster path extracts and opens further, pulling in still more water — a "
                   "run-away that starves the rest."),
        takeaway="This is channeling: over-extracted fast lanes and under-extracted slow ones.",
        scope=("ONE configuration, an exploratory result under flow control — NOT a proven general "
               "instability."))
    return fig, nar


# ── gallery render_fn wrappers (same (spec, outdir, ...) signature the registry expects) ───
def _render(spec, outdir, pure_fn):
    from .registry import producer_data, save_figure
    fig, _nar = pure_fn(producer_data(spec), presentation="standalone",
                        ceiling=spec.fidelity_ceiling, title=spec.title)
    thumb = save_figure(fig, spec, outdir)
    return {"id": spec.id, "thumb": thumb}


def render_cameron_pressure_sweep(spec, outdir, with_3d=False, video=False):
    return _render(spec, outdir, figure_cameron_pressure_sweep)


def render_cameron_beverage_sweep(spec, outdir, with_3d=False, video=False):
    return _render(spec, outdir, figure_cameron_beverage_sweep)


def render_cameron_shot_timeseries(spec, outdir, with_3d=False, video=False):
    return _render(spec, outdir, figure_cameron_shot_timeseries)
