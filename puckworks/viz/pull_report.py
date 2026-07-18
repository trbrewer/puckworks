"""Guided Espresso Pull — stage-by-stage visual report (issue #48, Milestone B).

A CONSUMING layer (CLAUDE.md rule 1 / ONBOARDING §6): it renders an already-completed
``puckworks.product.PullRun`` and asserts nothing beyond it. It NEVER calls ``simulate_pull``, never
mutates the run, and never recomputes a scientific value — every number comes from ``run.traces`` and
``run.final_observables``. matplotlib is imported LAZILY (this module imports cleanly without it), so
``puckworks`` / ``puckworks.product`` stay matplotlib-free.

Every figure carries the honesty furniture PUBLIC_EXPERIENCE §7 / PUBLIC_VALUE §6 require: a title, an
EXPLORATORY_SIMULATION badge drawn INTO the graphic, direct series labels with explicit units, the
component id, the fidelity ceiling, a plain-language scope line, and grayscale-readable line
styles/markers (status is never color-only). A static text equivalent is written alongside every
figure (``guided_pull_captions.txt`` + the Markdown report).
"""
from __future__ import annotations

import os

from ..product._pull import PullReportArtifacts, pull_run_to_json, pull_run_to_markdown
from .palette import BADGE_COLORS, BADGE_TEXT_COLOR
from ..figures import INK, NULL, GOOD, ACCENT, BAD

_VIZ_HINT = ("Guided pull figures require the `puckworks[viz]` optional dependencies: "
             "pip install -e '.[viz]'")
_BADGE = "EXPLORATORY_SIMULATION"


def _plt():
    """Lazy matplotlib import with the guided-pull install hint + the house style."""
    try:
        from ..figures import _plt as _house_plt
        return _house_plt()
    except ModuleNotFoundError as e:  # pragma: no cover - exercised via the missing-extra test
        raise ModuleNotFoundError(_VIZ_HINT) from e


def _trace(run, tid):
    for t in run.traces:
        if t.trace_id == tid:
            return t
    raise KeyError(f"trace {tid!r} not in run")


def _series(trace, sid):
    for s in trace.series:
        if s.series_id == sid:
            return s
    raise KeyError(f"series {sid!r} not in trace {trace.trace_id!r}")


def _stamp(fig, ax, component_id, ceiling, scope):
    """Draw the EXPLORATORY_SIMULATION badge into the graphic + a component/ceiling footer, so the
    honesty survives grayscale and screenshots (badge in the graphic, not the caption)."""
    fill = BADGE_COLORS.get(_BADGE, NULL)
    fig.text(0.008, 0.975, f" {_BADGE} ", ha="left", va="top", fontsize=7.0,
             color=BADGE_TEXT_COLOR, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.25", facecolor=fill, edgecolor="none"))
    # Component id + scope on one line, the fidelity ceiling below it — both left-aligned so long
    # strings never overlap. The render may not exceed the ceiling.
    fig.text(0.008, 0.030, f"{component_id} · scope: {scope}", ha="left", va="bottom",
             fontsize=6.0, color=NULL)
    fig.text(0.008, 0.006, "ceiling: " + (ceiling[:150] + "…" if len(ceiling) > 150 else ceiling),
             ha="left", va="bottom", fontsize=5.4, color=NULL)


def _process_strip(fig, run):
    """A numbered, labelled Recipe→…→Cup strip. Stages are numbered and named in words (never
    color-only), and unsupported slots are marked explicitly rather than omitted."""
    ax = fig.add_axes([0.03, 0.60, 0.94, 0.34])
    ax.axis("off")
    slots = [("1 Recipe", "input"), ("2 Grind", "run"), ("3 Bed", "assumed"),
             ("4 Machine", "prescribed"), ("5 Wetting", "not modeled"), ("6 Flow", "derived"),
             ("7 Extraction", "run"), ("8 Cup", "output")]
    n = len(slots)
    for i, (name, kind) in enumerate(slots):
        x = i / n
        face = {"run": GOOD, "input": INK, "output": INK, "derived": ACCENT,
                "prescribed": NULL, "assumed": NULL, "not modeled": BAD}.get(kind, NULL)
        ax.add_patch(_rect(x + 0.005, 0.35, 1 / n - 0.01, 0.5, face))
        ax.text(x + (1 / n) / 2, 0.60, name, ha="center", va="center", color="white",
                fontsize=6.6, fontweight="bold")
        ax.text(x + (1 / n) / 2, 0.20, kind, ha="center", va="center", color=INK, fontsize=5.6)
        if i < n - 1:
            ax.annotate("", xy=(x + 1 / n, 0.60), xytext=(x + 1 / n - 0.004, 0.60),
                        arrowprops=dict(arrowstyle="->", color=INK, lw=0.8))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)


def _rect(x, y, w, h, face):
    import matplotlib.patches as mpatches
    return mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.002",
                                   facecolor=face, edgecolor="white", linewidth=1.2)


# ─────────────────────────────── figures ─────────────────────────────────────────
def _fig_summary(run, path):
    plt = _plt()
    obs = run.final_observables
    fig = plt.figure(figsize=(8.4, 5.4))
    _process_strip(fig, run)
    ax = fig.add_axes([0.06, 0.10, 0.88, 0.42]); ax.axis("off")
    n_warn = len(run.warnings)
    lines = [
        f"Guided Espresso Pull — configuration `{run.config.config_id}`  (run {run.run_id})",
        "",
        f"Recipe: {run.recipe.dose_g:g} g in → {run.recipe.target_beverage_g:g} g out · "
        f"{run.recipe.pressure_bar:g} bar · {run.recipe.grinder_model} dial "
        f"{run.recipe.grind_setting:g} · profile {run.recipe.coffee_profile}",
        f"Temperature {run.recipe.brew_temperature_c:g} °C is RECORDED-ONLY (no thermal transient in v0.3.0).",
        "",
        f"Extraction yield: {obs['extraction_yield_pct']['value']} %      "
        f"TDS: {obs['tds_pct']['value']} %      "
        f"Shot duration: {obs['shot_duration_s']['value']} s",
        f"Beverage mass: {obs['beverage_mass_g']['value']} g      "
        f"Dissolved (extracted) mass: {obs['extracted_mass_g']['value']} g",
        "",
        "First drip / puck wetting: NOT MODELED (the primary model begins from a saturated bed).",
        "Pressure is a prescribed constant input, not a predicted profile. Composition, not flavor.",
        f"Domain warnings: {n_warn}" + (": " + "; ".join(run.warnings) if n_warn else "  (none)"),
    ]
    ax.text(0.0, 1.0, "\n".join(lines), ha="left", va="top", fontsize=8.2, color=INK,
            family="monospace")
    if n_warn:
        # Warning state marked by an explicit boxed word + hatch, never color alone.
        ax.text(0.0, -0.02, "⚠ EXTRAPOLATION — outside the validated evidence range", ha="left",
                va="top", fontsize=8.0, color=INK, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor=INK, hatch="///"))
    fig.suptitle("Result summary — exploratory simulation, not a taste prediction",
                 y=0.995, fontsize=10.5, fontweight="bold")
    _stamp(fig, ax, run.stages[0].component_id, _trace(run, "extraction_time").fidelity_ceiling,
           "exploratory simulation")
    return _save(fig, path)


def _fig_pressure_flow(run, path):
    plt = _plt()
    tr = _trace(run, "machine_flow_time")
    t = tr.axis_values
    p = _series(tr, "prescribed_pressure_bar")
    q = _series(tr, "flow_g_s")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(t, p.values, color=NULL, lw=2.0, ls="--", marker="s", markevery=max(1, len(t) // 10),
            ms=4, label=f"prescribed pressure [{p.unit}] — INPUT, not predicted")
    ax.set_xlabel("time [s]"); ax.set_ylabel(f"pressure [{p.unit}]", color=NULL)
    ax.set_ylim(0, max(p.values) * 1.6 + 1)
    ax2 = ax.twinx()
    ax2.plot(t, q.values, color=ACCENT, lw=2.0, ls="-", marker="o", markevery=max(1, len(t) // 10),
             ms=4, label=f"model flow [{q.unit}] — simulated")
    ax2.set_ylabel(f"flow [{q.unit}]", color=ACCENT)
    ax2.set_ylim(0, max(q.values) * 1.6 + 0.1)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper center", fontsize=7.6)
    ax.set_title("Machine & flow — prescribed constant pressure, constant model flow")
    ax.text(0.02, 0.06, "Pressure is prescribed (a constant model input), NOT a predicted dynamic "
            "profile.\nFlow is the model's constant Darcy flux. No channeling / preinfusion transient.",
            transform=ax.transAxes, fontsize=6.8, color=NULL, va="bottom")
    _stamp(fig, ax, tr.component_id, tr.fidelity_ceiling, "prescribed input + simulated flow")
    return _save(fig, path)


def _fig_cup_progress(run, path):
    plt = _plt()
    mf = _trace(run, "machine_flow_time")
    ex = _trace(run, "extraction_time")
    bev = _series(mf, "cumulative_beverage_g")
    diss = _series(ex, "cumulative_extracted_g")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(mf.axis_values, bev.values, color=GOOD, lw=2.0, ls="-", marker="o",
            markevery=max(1, len(bev.values) // 10), ms=4,
            label=f"cumulative beverage mass [{bev.unit}] — DERIVED from model flow")
    ax.set_xlabel("time [s]"); ax.set_ylabel(f"beverage mass [{bev.unit}]", color=GOOD)
    ax2 = ax.twinx()
    ax2.plot(ex.axis_values, diss.values, color=ACCENT, lw=2.0, ls="--", marker="^",
             markevery=max(1, len(diss.values) // 10), ms=4,
             label=f"cumulative dissolved mass [{diss.unit}] — SIMULATED")
    ax2.set_ylabel(f"dissolved mass [{diss.unit}]", color=ACCENT)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=7.6)
    ax.set_title("Cup progress — beverage accumulates, solute dissolves")
    ax.text(0.98, 0.04, "Beverage mass is DERIVED from the model's constant flow (not measured).",
            transform=ax.transAxes, fontsize=6.8, color=NULL, va="bottom", ha="right")
    _stamp(fig, ax, ex.component_id, ex.fidelity_ceiling, "derived + simulated")
    return _save(fig, path)


def _fig_extraction_progress(run, path):
    plt = _plt()
    ex = _trace(run, "extraction_time")
    ey = _series(ex, "extraction_yield_pct")
    cl = _series(ex, "outlet_concentration")
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.plot(ex.axis_values, ey.values, color=ACCENT, lw=2.0, ls="-", marker="o",
            markevery=max(1, len(ey.values) // 10), ms=4,
            label=f"cumulative extraction yield [{ey.unit}] — DERIVED")
    ax.set_xlabel("time [s]"); ax.set_ylabel(f"extraction yield [{ey.unit}]", color=ACCENT)
    ax2 = ax.twinx()
    ax2.plot(ex.axis_values, cl.values, color=GOOD, lw=2.0, ls=":", marker="D",
             markevery=max(1, len(cl.values) // 10), ms=4,
             label=f"outlet concentration [{cl.unit}] — SIMULATED")
    ax2.set_ylabel(f"outlet conc. [{cl.unit}]", color=GOOD)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="lower right", fontsize=7.6)
    ax.set_title("Extraction progress — yield and outlet concentration")
    ax.text(0.02, 0.96, "EY is derived from the simulated dissolved mass; concentration is a "
            "modeled single soluble pool (composition, not flavor).",
            transform=ax.transAxes, fontsize=6.8, color=NULL, va="top")
    _stamp(fig, ax, ex.component_id, ex.fidelity_ceiling, "derived + simulated")
    return _save(fig, path)


def _save(fig, path):
    import matplotlib.pyplot as plt
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


# ─────────────────────────────── captions (static text equivalent) ───────────────
def _captions(run) -> str:
    obs = run.final_observables
    return "\n".join([
        "Guided Espresso Pull — figure captions and alt text (static text equivalent).",
        f"Configuration {run.config.config_id}; run id {run.run_id}; badge {_BADGE}.",
        "",
        "guided_pull_summary.png — Process strip Recipe→Grind→Bed→Machine→Wetting→Flow→Extraction→"
        f"Cup with each slot's execution status, plus recipe and final observables. EY "
        f"{obs['extraction_yield_pct']['value']}%, TDS {obs['tds_pct']['value']}%, shot "
        f"{obs['shot_duration_s']['value']} s. First drip and puck wetting are NOT modeled; pressure "
        "is a prescribed constant; temperature is recorded-only.",
        "",
        "pressure_flow.png — Prescribed constant pump pressure (dashed, squares) on the left axis and "
        "the model's constant flow (solid, circles) on the right axis versus time. Pressure is an "
        "input, not a predicted profile.",
        "",
        "cup_progress.png — Cumulative beverage mass (solid, circles; derived from model flow) and "
        "cumulative dissolved mass (dashed, triangles; simulated) versus time. Beverage mass is not "
        "measured.",
        "",
        "extraction_progress.png — Cumulative extraction yield (solid, circles; derived) and outlet "
        "liquid concentration (dotted, diamonds; simulated) versus time. Composition, not flavor.",
        "",
        "Component coverage: only cameron2020.extraction_bdf is executed (primary chain); all other "
        "components are calibration-only, eligible-but-not-executed separate lenses, or excluded. "
        "None are averaged into a consensus.",
    ]) + "\n"


# ─────────────────────────────── entry point ─────────────────────────────────────
_OWNED = ("guided_pull_results.json", "guided_pull_report.md", "guided_pull_summary.png",
          "pressure_flow.png", "cup_progress.png", "extraction_progress.png",
          "guided_pull_captions.txt")


def render(run, out_dir, *, overwrite: bool = False) -> PullReportArtifacts:
    """Render the full report from a completed :class:`~puckworks.product.PullRun`.

    Reads only ``run`` — never re-simulates and never mutates it. Creates ``out_dir`` explicitly and
    writes the deterministic file set. With ``overwrite=False`` (default) it refuses to clobber an
    existing owned file it did not just create this call.
    """
    out_dir = os.fspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    if not overwrite:
        clashes = [f for f in _OWNED if os.path.exists(os.path.join(out_dir, f))]
        if clashes:
            raise FileExistsError(
                f"refusing to overwrite existing report files in {out_dir}: {clashes} "
                "(pass overwrite=True)")

    def path(name):
        return os.path.join(out_dir, name)

    # Text/data exports first (no matplotlib needed) — the static text equivalent.
    with open(path("guided_pull_results.json"), "w", encoding="utf-8") as f:
        f.write(pull_run_to_json(run))
    with open(path("guided_pull_report.md"), "w", encoding="utf-8") as f:
        f.write(pull_run_to_markdown(run))
    with open(path("guided_pull_captions.txt"), "w", encoding="utf-8") as f:
        f.write(_captions(run))

    # Figures (lazy matplotlib).
    _fig_summary(run, path("guided_pull_summary.png"))
    _fig_pressure_flow(run, path("pressure_flow.png"))
    _fig_cup_progress(run, path("cup_progress.png"))
    _fig_extraction_progress(run, path("extraction_progress.png"))

    files = tuple(path(n) for n in _OWNED)
    return PullReportArtifacts(
        out_dir=out_dir, results_json=path("guided_pull_results.json"),
        report_md=path("guided_pull_report.md"), summary_png=path("guided_pull_summary.png"),
        pressure_flow_png=path("pressure_flow.png"), cup_progress_png=path("cup_progress.png"),
        extraction_progress_png=path("extraction_progress.png"),
        captions_txt=path("guided_pull_captions.txt"), files=files)
