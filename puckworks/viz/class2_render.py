"""Class-2 high-fidelity renders — 2D field maps now, 3D behind the `[viz3d]` extra.

Each draw takes (spec, outdir, with_3d, video) and returns {'id','thumb','outputs'};
it badge/provenance-stamps every output. 2D field maps use matplotlib (`[viz]`);
the 3D sphere pack uses pyvista (`[viz3d]`) and is SKIPPED with a clear note when
that extra is absent — it only RENDERS fields the solvers already produce, it does
not re-solve. Heavy stills/videos land under frames/ (gitignored); only thumb.png
is committed.
"""
from __future__ import annotations
import os

import numpy as np

from ..figures import _plt, INK, ACCENT, NULL, GOOD, BAD
from .palette import FIELD_SEQUENTIAL
from .registry import producer_data, save_figure


def _save_thumb(fig, spec, outdir, name="thumb.png"):
    return save_figure(fig, spec, outdir, name=name)


def draw_puck_flow_field(spec, outdir, with_3d=False, video=False):
    """Stokes channel VERIFICATION field: the analytic velocity map + profile, with
    the LB twin's measured agreement. 'Computed Stokes flow, verification geometry.'"""
    plt = _plt()
    d = producer_data(spec)
    field = np.array(d["u_field"], float)
    u = np.array(d["u_profile"], float)
    fig, (axf, axp) = plt.subplots(1, 2, figsize=(8.4, 3.6),
                                   gridspec_kw={"width_ratios": [2.0, 1.0]})
    im = axf.imshow(field, aspect="auto", cmap=FIELD_SEQUENTIAL, origin="lower")
    axf.set_title("Stokes channel |u| — verification geometry", fontsize=9, loc="left")
    axf.set_xlabel("across channel (z)"); axf.set_ylabel("span")
    fig.colorbar(im, ax=axf, label="velocity (LB units)", fraction=0.046)
    axp.plot(u, np.arange(len(u)), color=ACCENT, lw=2.0)
    axp.set_title("analytic profile", fontsize=9, loc="left")
    axp.set_xlabel("u"); axp.set_ylabel("z")
    axp.text(0.5, 0.02, f"LB twin vs analytic: {d['lb_err_pct_vs_analytic']:.2f}%",
             transform=axp.transAxes, ha="center", fontsize=7, color=NULL)
    fig.suptitle("NOT the flow in your puck — Stokes-only verification (§5.2)",
                 fontsize=8, color=BAD, x=0.5, y=1.02)
    return {"id": spec.id, "thumb": _save_thumb(fig, spec, outdir),
            "outputs": ["thumb.png"]}


def draw_grain_pack_3d(spec, outdir, with_3d=False, video=False):
    """A synthetic Boolean-sphere pack: 2D solid slice + the sub-voxel HETEROGENEITY
    FIELD (labelled as a field, never resolved fines). 3D turntable behind [viz3d]."""
    plt = _plt()
    d = producer_data(spec)
    solid = np.array(d["solid_slice"], float)
    het = np.array(d["hetero_slice"], float)
    fig, (axs, axh) = plt.subplots(1, 2, figsize=(8.0, 3.9))
    axs.imshow(solid, cmap="Greys", origin="lower")
    axs.set_title(f"Boolean-sphere grains (φ={d['phi']:.2f})", fontsize=9, loc="left")
    axs.set_xticks([]); axs.set_yticks([])
    im = axh.imshow(het, cmap=FIELD_SEQUENTIAL, origin="lower")
    axh.set_title("sub-voxel heterogeneity FIELD (not resolved fines)", fontsize=9,
                  loc="left")
    axh.set_xticks([]); axh.set_yticks([])
    fig.colorbar(im, ax=axh, label="heterogeneity (σ)", fraction=0.046)
    fig.suptitle("Synthetic packing — an idealization, not imaged coffee", fontsize=8,
                 color=NULL, y=1.02)
    outputs = ["thumb.png"]
    thumb = _save_thumb(fig, spec, outdir)
    if with_3d:
        made = _render_3d_pack(spec, outdir, video=video)
        outputs += made
    return {"id": spec.id, "thumb": thumb, "outputs": outputs}


def _render_3d_pack(spec, outdir, video=False):
    """pyvista 3D sphere pack coloured by local porosity ([viz3d]); heavy outputs to
    frames/ (gitignored). Returns [] with a note if pyvista is absent."""
    try:
        import pyvista as pv
    except ModuleNotFoundError:
        print(f"[{spec.id}] 3D skipped: install the [viz3d] extra (pyvista/vtk).")
        return []
    from ..models.brewer2026.pack_generator import make_pack
    solid, meta = make_pack(L=32, gs=1.3, seed=0)
    grid = pv.wrap(solid.astype(float))
    frames_dir = os.path.join(outdir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    pl = pv.Plotter(off_screen=True)
    pl.add_volume(grid, cmap=FIELD_SEQUENTIAL, opacity="sigmoid")
    still = os.path.join(frames_dir, "pack_3d.png")
    pl.screenshot(still)
    pl.close()
    return ["frames/pack_3d.png"]


def draw_wetting_front_sweep(spec, outdir, with_3d=False, video=False):
    """Infiltration front s(t) vs bed depth L — a reconstruction of the CT-validated
    Foster front (sharp BINARY front; no saturation gradient behind it)."""
    plt = _plt()
    d = producer_data(spec)
    t = np.array(d["t_s"], float); s = np.array(d["front_mm"], float)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.plot(t, s, color=ACCENT, lw=2.2, label="wetting front s(t)")
    ax.axhline(d["L_mm"], color=NULL, ls="--", lw=1.2, label=f"bed depth L={d['L_mm']:g} mm")
    if d.get("t_sat"):
        ax.axvline(d["t_sat"], color=GOOD, ls=":", lw=1.2,
                   label=f"saturation ≈ {d['t_sat']:.1f} s")
    ax.fill_between(t, 0, s, color=ACCENT, alpha=0.12)
    ax.set_xlabel("time [s]"); ax.set_ylabel("front position [mm]")
    ax.set_title("Wetting front — sharp binary front (no gradient behind; G1 open)",
                 loc="left", fontsize=9)
    ax.legend(fontsize=7, loc="lower right")
    return {"id": spec.id, "thumb": _save_thumb(fig, spec, outdir),
            "outputs": ["thumb.png"]}


def draw_channeling_concentration(spec, outdir, with_3d=False, video=False):
    """N-tube flow concentration: max share(t) → N_eff→1 collapse, ONE configuration
    (gs 1.1, 9 bar, N=200). Not a proven instability."""
    plt = _plt()
    d = producer_data(spec)
    t = np.array(d["time_s"], float); ms = np.array(d["max_share"], float)
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.plot(t, ms, color=BAD, lw=2.2, label="max single-tube flow share")
    if d.get("collapse_time_s"):
        ax.axvline(d["collapse_time_s"], color=NULL, ls=":", lw=1.2,
                   label=f"collapse ≈ {d['collapse_time_s']:.1f} s")
    ax.set_ylim(0, 1)
    ax.set_xlabel("time [s] (physical)"); ax.set_ylabel("max flow share")
    ax.set_title("Dynamic channel concentration — ONE configuration, not a general result",
                 loc="left", fontsize=9)
    ax.text(0.98, 0.06, f"N_eff/N = {d['n_eff_over_N']:.3g}", transform=ax.transAxes,
            ha="right", fontsize=8, color=INK)
    ax.legend(fontsize=7, loc="center right")
    return {"id": spec.id, "thumb": _save_thumb(fig, spec, outdir),
            "outputs": ["thumb.png"]}


def draw_fines_migration(spec, outdir, with_3d=False, video=False):
    """fasano-structured fines migration: compact-layer front s(t) + q(t), and the
    q∞(p₀) shape. Mechanism illustration — closures are ours, not a coffee fit."""
    plt = _plt()
    d = producer_data(spec)
    t = np.array(d["t_s"], float); q = np.array(d["q"], float)
    sfront = np.array(d["compact_front_s"], float)
    p0 = np.array(d["p0_bar"], float); qinf = np.array(d["q_inf"], float)
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(8.6, 3.8))
    axa.plot(t, q / q[0], color=ACCENT, lw=2.0, label="discharge q(t)/q₀")
    axa.plot(t, sfront, color=NULL, lw=1.6, ls="--", label="compact-layer front s(t)")
    axa.set_xlabel("time [s]"); axa.set_ylabel("normalized")
    axa.set_title("release → advection → compact layer", fontsize=9, loc="left")
    axa.legend(fontsize=7)
    axb.plot(p0, qinf, "o-", color=GOOD, lw=1.8)
    axb.set_xlabel("applied pressure p₀ [bar]"); axb.set_ylabel("q∞")
    axb.set_title("asymptotic discharge q∞(p₀)", fontsize=9, loc="left")
    fig.suptitle("MECHANISM ILLUSTRATION — closures are ours, not a coffee fit",
                 fontsize=8, color=BAD, y=1.02)
    return {"id": spec.id, "thumb": _save_thumb(fig, spec, outdir),
            "outputs": ["thumb.png"]}
