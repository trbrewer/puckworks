"""Shared layout + typography for the Full Laboratory Tour's educational figures (#43, ROADMAP §8).

The tour figures had a structural collision: each draw called ``tight_layout()`` and the badge/footer
were then stamped with ``fig.text`` at y≈0.978 / y≈0.006 over already-packed axes, so the badge landed on
the title and the 5.2 pt footer landed on the x-axis labels. This module fixes the *architecture* rather
than the symptom: every tour figure is built from three stacked matplotlib **subfigures** —

    ┌─────────────────────────────── header band (badge, optional standalone title, reference key)
    │  plotting area (the axes)                    ← the only band that owns Axes
    └─────────────────────────────── footer band (provenance line + wrapped ``Scope:`` paragraph)

The header/footer bands never contain Axes, so header/footer text can never overlap a plot, an axis
label, or a tick label. Heights are reserved up front (the footer is sized from the *wrapped* scope line
count, not assumed to be one line). Typography is a fixed local scale — no process-wide ``rcParams`` are
touched, so unrelated repository figures are unaffected.

``stamp_fig`` (in ``registry``) detects the reserved bands via ``fig._tour_layout`` and draws the badge +
footer into them; it is idempotent. Non-tour figures keep the ordinary ``fig.text`` stamp.
"""
from __future__ import annotations

import dataclasses
import textwrap

from .palette import INK

# ── local typography scale (points) — never set as rcParams ───────────────────────────────
FS_FIG_TITLE = 13.0        # standalone figure title
FS_PANEL_TITLE = 11.0      # panel title inside a multi-panel figure
FS_AXIS_LABEL = 10.5       # axis label
FS_TICK = 9.0              # tick label
FS_LEGEND = 9.0            # legend
FS_ANNOTATION = 9.0        # in-axes annotation
FS_BADGE = 9.0             # evidence badge
FS_FOOTER = 8.0            # provenance / fidelity footer
MIN_VISIBLE_FS = 8.0       # nothing visible in a tour figure may be smaller than this

# ── colours (share the accessible house palette; colour is never the sole encoding) ───────
LINE = "#0e7490"
REF = "#b91c1c"
WALL = "#6b7280"
MARKERS = ["o", "s", "^", "D", "v", "P", "X"]
GRID = dict(alpha=0.25, linewidth=0.6)


@dataclasses.dataclass(frozen=True)
class TourFigureNarrative:
    """Structured novice explanation — one calm section each, so the notebook renders short normal
    paragraphs instead of one italic wall of text. Every number in these fields is recomputed from the
    producer by the draw function (never hand-typed)."""
    setup: str                       # "What changes"
    finding: str                     # "What the model shows"
    mechanism: str                   # "Why this happens"
    scope: str                       # "Scope" (plain-language limitation)
    takeaway: str | None = None      # "What is interesting" (optional)

    def to_caption(self) -> str:
        """Backwards-compatible Markdown composition for any caller still reading a flat caption."""
        parts = [f"**What changes.** {self.setup}",
                 f"**What the model shows.** {self.finding}",
                 f"**Why this happens.** {self.mechanism}"]
        if self.takeaway:
            parts.append(f"**What is interesting.** {self.takeaway}")
        parts.append(f"**Scope.** {self.scope}")
        return "\n\n".join(parts)


def _plt():
    import matplotlib.pyplot as plt
    return plt


def _footer_wrap_width(fig_w_in: float) -> int:
    """Characters per footer line at FS_FOOTER across the figure width (left-aligned)."""
    return max(70, int(fig_w_in * 15.0))


def wrap_scope(ceiling: str, fig_w_in: float) -> list[str]:
    """Wrap the fidelity ceiling into a ``Scope:``-prefixed paragraph sized to the figure width."""
    return textwrap.wrap("Scope: " + " ".join(str(ceiling).split()),
                         width=_footer_wrap_width(fig_w_in)) or ["Scope: —"]


def reserve_footer_inches(ceiling: str, fig_w_in: float) -> float:
    """Footer band height (inches) = one provenance line + the wrapped scope lines + padding."""
    n_lines = 1 + len(wrap_scope(ceiling, fig_w_in))
    return 0.16 + n_lines * (FS_FOOTER / 72.0) * 1.5


def tour_figure(nrows=1, ncols=1, *, figsize, ceiling="", presentation="notebook",
                title="", has_reference_key=False, sharex=False, sharey=False,
                width_ratios=None, height_ratios=None):
    """Build a tour figure with reserved header/plot/footer bands (see module docstring).

    Returns ``(fig, axes)`` where ``axes`` is always a 2-D numpy object array. The header/footer
    subfigures are stored on ``fig._tour_layout`` for the (idempotent) stamp step to find.
    """
    import numpy as np
    plt = _plt()
    fig_w, fig_h = figsize
    # header holds the badge and, for standalone, a title; a reference key adds a little height
    header_in = 0.40 + (0.34 if (presentation == "standalone" and title) else 0.0)
    footer_in = reserve_footer_inches(ceiling, fig_w)
    plot_in = max(1.0, fig_h - header_in - footer_in)
    fig = plt.figure(figsize=(fig_w, plot_in + header_in + footer_in),
                     constrained_layout=True, facecolor="white")
    header_fig, plot_fig, footer_fig = fig.subfigures(
        3, 1, height_ratios=[header_in, plot_in, footer_in])
    header_fig.set_facecolor("white")
    plot_fig.set_facecolor("white")
    footer_fig.set_facecolor("white")
    axes = plot_fig.subplots(nrows, ncols, squeeze=False, sharex=sharex, sharey=sharey,
                             gridspec_kw=dict(width_ratios=width_ratios, height_ratios=height_ratios))
    axes = np.array(axes, dtype=object).reshape(nrows, ncols)
    fig._tour_layout = {"header": header_fig, "plot": plot_fig, "footer": footer_fig,
                        "fig_w_in": fig_w, "presentation": presentation, "title": title,
                        "has_reference_key": has_reference_key, "stamped": False}
    if presentation == "standalone" and title:
        header_fig.text(0.5, 0.20, title, ha="center", va="bottom", fontsize=FS_FIG_TITLE,
                        color=INK, fontweight="bold")
    return fig, axes


def style_axis(ax, *, xlabel=None, ylabel=None, title=None):
    """One consistent axis style: readable fonts, subtle grid, light spines."""
    if xlabel is not None:
        ax.set_xlabel(xlabel, fontsize=FS_AXIS_LABEL)
    if ylabel is not None:
        ax.set_ylabel(ylabel, fontsize=FS_AXIS_LABEL)
    if title is not None:
        ax.set_title(title, fontsize=FS_PANEL_TITLE)
    ax.tick_params(labelsize=FS_TICK)
    ax.grid(True, **GRID)
    for sp in ax.spines.values():
        sp.set_linewidth(0.8)
    return ax


def plot_curve(ax, x, y, *, marker="o", label=None, color=LINE, ls="-"):
    return ax.plot(x, y, marker=marker, linestyle=ls, color=color, markersize=5, lw=1.7, label=label)


def mark_reference(ax, x, y, ref_x, *, label=None):
    """Star the reference-condition point. Returns a proxy handle (for a figure-level key) or None."""
    xs = list(x)
    if ref_x is None or ref_x not in xs:
        return None
    i = xs.index(ref_x)
    ax.plot([xs[i]], [y[i]], marker="*", color=REF, markersize=15, zorder=6, linestyle="none")
    if label:
        from matplotlib.lines import Line2D
        return Line2D([0], [0], marker="*", color=REF, markersize=13, linestyle="none", label=label)
    return None


def shared_xlabel(fig, text):
    """One figure-level x label under the whole plot grid (scoped to the plot subfigure, so it sits
    above the footer band and is never repeated per panel)."""
    fig._tour_layout["plot"].supxlabel(text, fontsize=FS_AXIS_LABEL)


def reference_key(fig, handles, labels=None):
    """One reference-condition legend for the whole figure, in the reserved header band."""
    handles = [h for h in handles if h is not None]
    if not handles:
        return
    header = fig._tour_layout["header"]
    header.legend(handles=handles, loc="center right", bbox_to_anchor=(0.995, 0.5),
                  fontsize=FS_LEGEND, frameon=False, handletextpad=0.4, borderaxespad=0.2)


def sci_formatter(ax, axis="y"):
    """Readable numeric ticks with ONE visible scale factor — never a column of six-decimal near-zeros."""
    from matplotlib.ticker import ScalarFormatter
    fmt = ScalarFormatter(useMathText=True)
    fmt.set_powerlimits((-2, 3))
    getattr(ax, f"{axis}axis").set_major_formatter(fmt)
    getattr(ax, f"{axis}axis").offsetText.set_fontsize(FS_TICK)


def annotate_inside(ax, text, xy, xytext, *, color=REF):
    """In-axes annotation with an arrow, clamped inside the axes so it is never left-clipped."""
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=FS_ANNOTATION, color=color,
                ha="left", va="center", annotation_clip=False,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.2),
                bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor=color, alpha=0.9))
