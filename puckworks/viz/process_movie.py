"""The whole-process piece — PV-09 multi-lens MONTAGE (not a mega-model).

Implements PV-09's contract verbatim: PARALLEL LABELLED LENSES on one shared shot
clock, each lens keeping its OWN component + badge + evidence on screen. The shared
clock synchronizes DISPLAY only — no cross-lens physical coupling is implied or
computed. The committed artefact is a static montage still (thumb.png); the scrubbed
video is assembled with imageio behind --video and is gitignored (heavy).
"""
from __future__ import annotations
import os

from ..figures import _plt, INK, NULL
from .palette import BADGE_COLORS, STAGE_FILL, STAGE_EDGE
from .registry import stamp_fig, producer_data, save_figure


# the lenses that make up the movie, each its own component + badge
_LENS_ORDER = ["grind", "packing", "machine", "infiltration", "flow",
               "extraction", "bed_dynamics", "observables"]


def _montage(spec, playhead=None):
    """Draw the parallel-lens montage grid. Returns the matplotlib figure."""
    plt = _plt()
    stages = producer_data(spec)["stages"]
    by = {s["stage"]: s for s in stages}
    lenses = [by[k] for k in _LENS_ORDER if k in by]
    ncol = 4
    nrow = (len(lenses) + ncol - 1) // ncol
    fig, axes = plt.subplots(nrow, ncol, figsize=(11.5, 2.7 * nrow + 0.8))
    axes = axes.ravel()
    for ax, st in zip(axes, lenses):
        ax.axis("off")
        bc = BADGE_COLORS.get(st["badge"], NULL)
        ax.add_patch(plt.Rectangle((0.04, 0.14), 0.92, 0.74, facecolor=STAGE_FILL,
                                   edgecolor=STAGE_EDGE, lw=1.4,
                                   transform=ax.transAxes))
        ax.text(0.5, 0.74, st["stage"], transform=ax.transAxes, ha="center",
                fontsize=11, fontweight="bold", color=INK)
        ax.text(0.5, 0.55, st["label"], transform=ax.transAxes, ha="center",
                fontsize=6.4, color=INK, wrap=True)
        ax.text(0.5, 0.40, st["component"], transform=ax.transAxes, ha="center",
                fontsize=5.6, color=NULL, style="italic")
        # every lens keeps its OWN badge + evidence on screen (PV-09)
        ax.add_patch(plt.Rectangle((0.04, 0.14), 0.92, 0.10, facecolor=bc,
                                   edgecolor="none", transform=ax.transAxes))
        ax.text(0.5, 0.19, f"{st['badge']} · {st['evidence']}", transform=ax.transAxes,
                ha="center", fontsize=5.2, color="white", fontweight="bold")
    for ax in axes[len(lenses):]:
        ax.axis("off")
    clock = "shared shot clock (DISPLAY ONLY — no cross-lens coupling)"
    if playhead is not None:
        clock += f"   ▸ t = {playhead:.1f} s"
    fig.suptitle("The hidden puck — parallel labelled lenses, NOT a mega-model\n" + clock,
                 fontsize=11, y=0.99)
    fig.subplots_adjust(top=0.86, hspace=0.15, wspace=0.08)
    return fig


def draw_hidden_puck_movie(spec, outdir, with_3d=False, video=False):
    """Static montage still (committed thumb); optional scrubbed video (gitignored)."""
    os.makedirs(outdir, exist_ok=True)
    thumb = save_figure(_montage(spec), spec, outdir)   # stamps + thumb (+ hi-res if --hires)
    outputs = ["thumb.png"]
    if video:
        outputs += _assemble_video(spec, outdir)
    return {"id": spec.id, "thumb": thumb, "outputs": outputs}


def _assemble_video(spec, outdir, n_frames=24, shot_len_s=30.0):
    """Scrub the shared clock across the montage and assemble frames -> mp4 (heavy,
    gitignored). Skipped with a note if imageio is absent."""
    try:
        import imageio.v2 as imageio
    except ModuleNotFoundError:
        print(f"[{spec.id}] video skipped: install the [viz] extra (imageio).")
        return []
    import matplotlib.pyplot as plt
    frames_dir = os.path.join(outdir, "frames")
    os.makedirs(frames_dir, exist_ok=True)
    paths = []
    for i in range(n_frames):
        t = shot_len_s * i / (n_frames - 1)
        fig = _montage(spec, playhead=t)
        stamp_fig(fig, spec)
        fp = os.path.join(frames_dir, f"frame_{i:03d}.png")
        fig.savefig(fp, dpi=90, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        paths.append(fp)
    mp4 = os.path.join(outdir, "hidden_puck.mp4")
    with imageio.get_writer(mp4, fps=8) as w:
        for fp in paths:
            w.append_data(imageio.imread(fp))
    return ["frames/", "hidden_puck.mp4"]
