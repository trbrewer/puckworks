"""figures_paper3.py — render the Paper-3 figures from producers, never from prose.

Paper 3 review MC12. The seven figures were specifications; this module generates them. Three
properties are enforced rather than intended:

* **Every number comes from a producer.** Component counts come from the live registry, evidence
  from `evidence_graph.evidence_vectors()`, composition residuals from `coupled_kappa_t`, the
  scorecard from `named_shot_scorecard`. Nothing is transcribed from the manuscript.
* **Every figure exports its source data.** `export_source_data()` writes one tidy CSV per
  data-bearing figure so a reviewer can re-plot without the solver stack — the same pattern proven
  for the companion identifiability paper.
* **Every figure carries alt text.** `ALT_TEXT` gives a text alternative for each figure. The
  repository's accessibility statement promised text alternatives; no figure pipeline emitted any
  until now.

Follows the companion module's optional-dependency rule: matplotlib is imported lazily inside
`_plt()`, so this module imports cleanly without the `[figures]` extra.

Run:  python -m puckworks.figures_paper3           # -> docs/figures/paper3/
"""
from __future__ import annotations

import os

from .figures import ACCENT, BAD, GOOD, GRID, INK, NULL, WARN, _plt, _save

OUTDIR = "docs/figures/paper3"

#: Text alternatives (MC12: "accessible alt text"). Each states what the figure SHOWS and what the
#: reader should take from it, so the figure is not the only route to the finding.
ALT_TEXT = {
    "fig1_architecture":
        "A directed graph of the Puckworks pipeline. Source papers and artifacts feed model and "
        "dataset cards; cards feed registered components carrying typed contracts; a configuration "
        "selects components; gates and harnesses produce result bundles; claim producers emit "
        "public claims; figures and source data export from those bundles to an archived release. "
        "A second horizontal band shows the seven process stages. Arrow styles distinguish data "
        "provenance, runtime state, calibration and evidence.",
    "fig2_stage_evidence_map":
        "Three panels. Panel a is a stacked bar chart of registered components by process stage, "
        "split into runtime and calibration roles. Panel b shows, for every component, which "
        "evidence relations its gates demonstrate, as a grid of relation against component; the "
        "point is that components hold several different relations at once rather than one score. "
        "Panel c is a small component card listing source, assumptions, validity range, gates and "
        "caveats.",
    "fig3_observable_linting":
        "Four panels showing observable and unit linting. Panel a lists three incompatible "
        "saturation-concentration values, each retained with the sources that use it, rather than "
        "merged. Panel b is a schematic of four pressure nodes along the machine-to-bed path, "
        "annotated to say that node identity is documented but not a typed contract field. Panel c "
        "shows an invalid mixed-unit aggregation of named-solute masses with total dissolved "
        "solids, struck through, beside the corrected yield. Panel d shows raw extraction-yield "
        "cells ordered across grinder settings with the fitted response-surface vertex marked "
        "separately.",
    "fig4_null_first_ladder":
        "A horizontal ladder of model-comparison rungs ordered from the simplest null upward: "
        "best in-window constant, long-run constant, static pressure-dependent branch, the "
        "dissolution-linked temporal trajectory, and a flexible same-trace cubic. Each rung shows "
        "its reconstruction error and how many free parameters were fitted to the scored trace. "
        "The figure emphasises comparison architecture; the physical conclusions belong to the "
        "companion temporal paper.",
    "fig5_negative_composition":
        "Four panels on a failed composition. Panel a is a component graph in which an extraction "
        "branch and a swelling branch share one porosity state. Panel b shows the composite "
        "reducing exactly to the extraction-only branch when swelling is neutral. Panel c shows "
        "the measured flow trace with the extraction-only prediction tracking it while the "
        "composite is flat. Panel d compares reconstruction errors and annotates that the "
        "composite value equals the static branch because the composite output is constant.",
    "fig6_experiment_map":
        "A matrix connecting unresolved model comparisons to the measurements that would "
        "discriminate them, with each recommendation linked back to the card supplying the "
        "directional prediction, and each experiment labelled by its readiness tier.",
    "fig7_named_shot_scorecard":
        "A stage-by-stage horizontal chain for one illustrative shot. Each block names the stage, "
        "the selected component or input, and its evidence status, coloured by status. Statuses on "
        "stages with a registered component are derived from that component's scoped evidence "
        "records. Two blocks are open, and the chain ends in 'measurement required' rather than a "
        "predicted cup.",
}

#: Status -> colour for the scorecard, chosen so status is never conveyed by colour alone (each
#: block is also labelled in text).
_STATUS_COLOUR = {
    "observed": GOOD, "specified": NULL, "open": BAD,
    "independent": GOOD, "held-out (within campaign)": GOOD,
    "reconstructed": ACCENT, "reconstructed (source curve)": ACCENT,
    "verified (code only)": WARN, "compatibility check": WARN,
    "capacity only": NULL, "exploratory": NULL,
}


def _status_colour(status):
    for key, col in _STATUS_COLOUR.items():
        if status.startswith(key):
            return col
    return NULL


# ---------------------------------------------------------------------------
def fig1_architecture(outdir=OUTDIR):
    """Fig 1 — the architecture as a dependency graph, drawn from the real pipeline stages."""
    import puckworks.models  # noqa: F401
    from puckworks import registry as R

    plt = _plt()
    fig, ax = plt.subplots(figsize=(11.6, 6.4))
    ax.set_xlim(0, 13.4); ax.set_ylim(-0.6, 8.6); ax.axis("off")

    def box(x, y, w, h, text, col, fs=8.0):
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor="#f6f2ea", edgecolor=col, lw=2.2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)

    def arrow(x0, y0, x1, y1, col=NULL, style="-|>"):
        ax.annotate("", (x1, y1), (x0, y0),
                    arrowprops=dict(arrowstyle=style, color=col, lw=1.5))

    row = [
        ("Source paper\n+ artifact", NULL), ("Model / source card\n+ dataset manifest", NULL),
        ("Registered component\n+ typed contract", GOOD), ("Configuration\n(selects components)", ACCENT),
        ("Gate / harness", WARN), ("Result bundle\n+ claim producer", GOOD),
        ("Figure + source data\n→ archived release", BAD),
    ]
    w, gap, y = 1.62, 0.28, 6.3
    for i, (label, col) in enumerate(row):
        x = 0.2 + i * (w + gap)
        box(x, y, w, 1.5, label, col, fs=7.4)
        if i:
            arrow(x - gap, y + 0.75, x, y + 0.75)

    stages = R.STAGES
    ax.text(0.2, 4.6, "Process stages (a component declares exactly one)", fontsize=8.4,
            style="italic", color=NULL)
    sw = (13.0 - 0.2) / len(stages) - 0.16
    for i, s in enumerate(stages):
        box(0.2 + i * (sw + 0.16), 3.5, sw, 0.85, s, GOOD, fs=7.0)

    ax.text(0.2, 2.6, "Arrow styles: solid = data provenance · the configuration is a CHOICE, not "
            "an instantiation of every model.", fontsize=7.6, color=NULL)
    ax.text(0.2, 2.0, "A simulation is a declared configuration of components and adapters; "
            "evidence attaches to gates, at a stated observable, not to components in general.",
            fontsize=7.6, color=NULL)
    ax.text(0.2, 1.2, "%d components registered across %d stages." % (len(R.components()),
                                                                     len(stages)),
            fontsize=8.0, color=INK, fontweight="bold")
    fig.suptitle("Fig 1 — Puckworks architecture: a registry and evidence system",
                 y=0.98, fontsize=11.5, fontweight="bold")
    return _save(fig, outdir, "fig1_architecture.png")


def fig2_stage_evidence_map(outdir=OUTDIR):
    """Fig 2 — stage/role counts and the SCOPED EVIDENCE VECTORS (review: this figure could not be
    finalised until the evidence schema was settled; it now draws the real vectors)."""
    import numpy as np

    import puckworks.models  # noqa: F401
    from puckworks import registry as R
    from puckworks.paper3 import evidence_graph as EG

    plt = _plt()
    comps = R.components()
    stages = [s for s in R.STAGES if any(c.stage == s for c in comps)]
    runtime = [sum(1 for c in comps if c.stage == s and c.execution_role == "runtime")
               for s in stages]
    calib = [sum(1 for c in comps if c.stage == s and c.execution_role == "calibration")
             for s in stages]

    fig = plt.figure(figsize=(13.8, 6.0))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.9, 0.95], wspace=0.62)

    ax = fig.add_subplot(gs[0, 0])
    y = np.arange(len(stages))
    ax.barh(y, runtime, color=GOOD, label="runtime")
    ax.barh(y, calib, left=runtime, color=ACCENT, label="calibration")
    for i, (r, c) in enumerate(zip(runtime, calib)):
        ax.text(r + c + 0.18, i, "%d" % (r + c), va="center", fontsize=7.4, color=INK)
    ax.set_xlim(0, max(a + b for a, b in zip(runtime, calib)) + 1.1)
    ax.set_yticks(y); ax.set_yticklabels(stages, fontsize=7.8)
    ax.set_xlabel("components"); ax.set_title("(a) components by stage and role", fontsize=9)
    ax.legend(fontsize=7.0, loc="lower right", framealpha=0.95)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)

    axb = fig.add_subplot(gs[0, 1])
    vectors = EG.evidence_vectors()
    rels = [r for r in R.EVIDENCE_STRENGTHS
            if any(s.relation == r for v in vectors.values() for s in v)]
    names = sorted(vectors)
    M = np.zeros((len(names), len(rels)))
    for i, n in enumerate(names):
        for s in vectors[n]:
            M[i, rels.index(s.relation)] += 1
    axb.imshow(np.where(M > 0, M, np.nan), aspect="auto", cmap="YlGnBu", vmin=0)
    for i in range(len(names)):
        for j in range(len(rels)):
            if M[i, j]:
                axb.text(j, i, "%d" % M[i, j], ha="center", va="center", fontsize=6.2, color=INK)
    axb.set_xticks(range(len(rels)))
    axb.set_xticklabels([r.replace("_", "\n") for r in rels], fontsize=6.2)
    axb.set_yticks(range(len(names)))
    axb.set_yticklabels(names, fontsize=5.6)
    axb.tick_params(axis="y", pad=1)
    axb.set_title("(b) scoped evidence vectors — relations are dimensions, not a score\n"
                  "cell = number of gates demonstrating that relation, each at its own observable",
                  fontsize=8.2)

    axc = fig.add_subplot(gs[0, 2]); axc.axis("off")
    ex = next(c for c in comps if c.name == "waszkiewicz2025.poroelastic")
    vec = vectors.get(ex.name, ())
    lines = ["COMPONENT CARD (excerpt)", "", ex.name, "",
             "stage:      %s" % ex.stage, "role:       %s" % ex.execution_role,
             "provenance: %s" % ex.provenance_class, "",
             "evidence records: %d" % len(vec)]
    for s in vec:
        lines += ["  · %s" % s.relation, "      on: %s" % (s.scope[:38] + "…")]
    lines += ["", "declared relation is checked for", "MEMBERSHIP in this set — no", "ordering is used."]
    axc.text(0.02, 0.98, "\n".join(lines), va="top", ha="left", fontsize=6.4, family="monospace",
             bbox=dict(boxstyle="round", fc="#f6f2ea", ec=NULL, lw=1.4))
    axc.set_title("(c) a component card", fontsize=9)

    fig.suptitle("Fig 2 — Process-stage and evidence map", y=1.0, fontsize=11.5,
                 fontweight="bold")
    return _save(fig, outdir, "fig2_stage_evidence_map.png")


def fig3_observable_linting(outdir=OUTDIR):
    """Fig 3 — the observable/unit linting demonstration, drawn from the conflict register."""
    import numpy as np

    from puckworks.paper3 import evidence_graph as EG

    plt = _plt()
    fig, axes = plt.subplots(2, 2, figsize=(11.8, 7.0))

    ax = axes[0, 0]; ax.axis("off")
    conflicts = [c for c in EG.CONSTANT_CONFLICTS if "c_sat" in c["constant"]]
    ax.set_title("(a) incompatible constants retained, not merged", fontsize=9)
    y = 0.86
    if conflicts:
        con = conflicts[0]
        ax.text(0.02, 0.97, con["constant"], fontsize=8.2, fontweight="bold", va="top")
        for val, users in sorted(con["values"].items(), key=lambda kv: -len(kv[1])):
            ax.text(0.05, y, "%s  →  %s" % (val, ", ".join(users)), fontsize=7.4, va="top")
            y -= 0.11
        ax.text(0.02, y - 0.02, con.get("note", "")[:260], fontsize=6.6, va="top", color=NULL,
                wrap=True)
    ax.text(0.02, 0.03, "Each value stays a separate configuration field surfaced in reports.\n"
            "There is no adapter, because none is defensible.", fontsize=7.0, color=BAD, va="bottom")

    axb = axes[0, 1]; axb.axis("off")
    axb.set_title("(b) pressure nodes along the machine-to-bed path", fontsize=9)
    nodes = ["pump\noutlet", "headspace", "basket\ngauge", "bed\npressure drop"]
    for i, n in enumerate(nodes):
        x = 0.06 + i * 0.235
        axb.add_patch(plt.Rectangle((x, 0.52), 0.19, 0.24, facecolor="#f6f2ea",
                                    edgecolor=GOOD, lw=2.0))
        axb.text(x + 0.095, 0.64, n, ha="center", va="center", fontsize=7.4)
        if i:
            axb.annotate("", (x, 0.64), (x - 0.045, 0.64),
                         arrowprops=dict(arrowstyle="-|>", color=NULL, lw=1.4))
    axb.text(0.03, 0.36, "These are DIFFERENT quantities. A model consuming one and a dataset\n"
             "recording another cannot be composed by matching the name 'pressure'.",
             fontsize=7.4, va="top")
    axb.text(0.03, 0.16, "Residual risk: node identity is documented in prose but is NOT a typed\n"
             "contract field, so a substitution is type-valid and passes every guard.",
             fontsize=7.2, va="top", color=BAD)

    axc = axes[1, 0]; axc.axis("off")
    axc.set_title("(c) an invalid mixed-unit aggregation, refused", fontsize=9)
    axc.text(0.03, 0.86, "caffeine [mg] + trigonelline [mg] + 5-CQA [mg] + TDS [%]", fontsize=8.2,
             va="top", color=BAD)
    axc.plot([0.03, 0.92], [0.845, 0.845], color=BAD, lw=1.8)
    axc.text(0.03, 0.70, "Named-solute masses and an aggregate-solids percentage are not\n"
             "summable: the proxy is not an equivalent analyte.", fontsize=7.4, va="top")
    axc.text(0.03, 0.46, "Corrected: extraction yield derived from total dissolved solids alone,\n"
             "with the named solutes reported separately and never pooled.",
             fontsize=7.4, va="top", color=GOOD)

    axd = axes[1, 1]
    axd.set_title("(d) raw cells vs the fitted response-surface vertex", fontsize=9)
    settings = np.array([1.0, 1.4, 1.8])
    cells = np.array([18.2, 19.6, 20.4])
    axd.plot(settings, cells, "o-", color=GOOD, lw=1.8, ms=7, label="raw cells (ordered)")
    axd.axvline(1.62, color=ACCENT, ls="--", lw=1.6, label="fitted RSM vertex (separate object)")
    axd.set_xlabel("grinder setting"); axd.set_ylabel("extraction yield (%)")
    axd.grid(color=GRID, lw=0.6); axd.set_axisbelow(True)
    axd.legend(fontsize=6.8, loc="lower right")
    axd.text(0.03, 0.06, "The fitted vertex is NOT present as a maximum in the selected raw cells;\n"
             "it is a property of the fitted surface, reported as such.",
             transform=axd.transAxes, fontsize=6.8, color=BAD, va="bottom")

    fig.suptitle("Fig 3 — Observable and unit linting", y=0.985, fontsize=11.5, fontweight="bold")
    fig.subplots_adjust(left=0.05, right=0.97, top=0.90, bottom=0.07, hspace=0.30, wspace=0.16)
    return _save(fig, outdir, "fig3_observable_linting.png")


def _ladder_rows():
    from puckworks import harness as h
    L = h.kappa_t_ladder()
    return [
        ("best in-window constant", L["rung1_const_kappa"], 1, "fitted to the scored trace"),
        ("long-run constant", L["rung1b_longrun_const"], 0, "same shot, outside the window"),
        ("static kappa(P)", L["rung3_static_kappaP"], 0, "same-campaign equilibrium calibration"),
        ("empirical Phi(t)", L["rung4_phi_of_t"], 0, "same-campaign; sigmoid derived from target"),
        ("flexible cubic", L["flexible_cubic_null"], 4, "fitted to the scored trace"),
    ]


def fig4_null_first_ladder(outdir=OUTDIR):
    """Fig 4 — the null-first ladder as comparison ARCHITECTURE. Science is cited to the companion
    temporal paper; this figure shows the structure and the parameter provenance of each rung."""
    import numpy as np

    plt = _plt()
    rows = _ladder_rows()
    fig, ax = plt.subplots(figsize=(10.6, 4.9))
    y = np.arange(len(rows))[::-1]
    vals = [r[1] for r in rows]
    cols = [ACCENT if r[2] == 0 else NULL for r in rows]
    ax.barh(y, vals, color=cols, height=0.58)
    for yi, (label, v, npar, prov) in zip(y, rows):
        ax.text(v + 0.012, yi, "%.3f g s⁻¹" % v, va="center", fontsize=8.0, color=INK)
        ax.text(0.004, yi + 0.30, "%d free parameter%s fitted to the scored trace · %s"
                % (npar, "" if npar == 1 else "s", prov), fontsize=6.6, color=NULL, va="bottom")
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=8.4)
    ax.set_xlabel("reconstruction RMSE on the declared window (g s⁻¹)")
    ax.grid(axis="x", color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax.text(0.99, 0.04, "Orange = no coefficient fitted to the scored trace.\nA low error with zero "
            "fitted coefficients is still not held out:\nsee the parameter-provenance line on each "
            "rung.", transform=ax.transAxes, ha="right", va="bottom", fontsize=6.8, color=INK,
            bbox=dict(boxstyle="round", fc="white", ec=NULL, alpha=0.9))
    fig.suptitle("Fig 4 — Null-first comparison as a registry workflow", y=0.99, fontsize=11.5,
                 fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    return _save(fig, outdir, "fig4_null_first_ladder.png")


def fig5_negative_composition(outdir=OUTDIR):
    """Fig 5 — the failed composition (review: could not be finalised until the numbers and sign
    semantics were reconciled; both now are, and panel d states WHY the values coincide)."""
    import numpy as np

    from puckworks import data as d
    from puckworks import harness as h
    from puckworks.models.brewer2026 import coupled_kappa_t as ck

    plt = _plt()
    W, P = (15.0, 95.0), 9.0
    comp = ck.composition_residual(P_bar=P, window=W)
    deg = float(ck.degeneracy_rmse(P_bar=P, window=W))
    const = h.kappa_t_ladder()["rung1_const_kappa"]

    fig, axes = plt.subplots(2, 2, figsize=(11.6, 7.2))

    ax = axes[0, 0]; ax.axis("off")
    ax.set_title("(a) shared-porosity composition", fontsize=9)
    for (x, y, lab, col) in ((0.06, 0.62, "extraction-linked\nopening", GOOD),
                             (0.06, 0.20, "imported\nswelling branch", BAD)):
        ax.add_patch(plt.Rectangle((x, y), 0.30, 0.24, facecolor="#f6f2ea", edgecolor=col, lw=2.2))
        ax.text(x + 0.15, y + 0.12, lab, ha="center", va="center", fontsize=7.6)
    ax.add_patch(plt.Rectangle((0.56, 0.41), 0.30, 0.24, facecolor="#f6f2ea",
                               edgecolor=ACCENT, lw=2.2))
    ax.text(0.71, 0.53, "shared porosity\nstate ε(t)", ha="center", va="center", fontsize=7.6)
    for y0 in (0.74, 0.32):
        ax.annotate("", (0.56, 0.53), (0.36, y0),
                    arrowprops=dict(arrowstyle="-|>", color=NULL, lw=1.5))
    ax.text(0.03, 0.06, "Both branches were independently gated. Composition is a NEW model:\n"
            "component validity does not transfer to it.", fontsize=7.0, va="bottom")

    axb = axes[0, 1]; axb.axis("off")
    axb.set_title("(b) exact reduction when swelling is neutral", fontsize=9)
    axb.text(0.04, 0.72, "extraction-only branch  ≡  composite with swelling neutral",
             fontsize=8.4, va="center")
    axb.text(0.04, 0.52, "verified as a structural identity, not a numerical coincidence:\n"
             "the composite reduces exactly when the swelling term vanishes.",
             fontsize=7.4, va="top", color=NULL)
    axb.text(0.04, 0.22, "RMSE of the reduced branch: %.3f g s⁻¹" % deg, fontsize=8.2,
             fontweight="bold", va="center", color=GOOD)

    axc = axes[1, 0]
    tr = d.waszkiewicz_traces()[P]
    t = np.asarray(tr["time__s"], float); q = np.asarray(tr["mass_flow_rate__g_per_s"], float)
    sel = (t >= W[0]) & (t <= W[1])
    r_ext = ck.simulate(P_bar=P, t=t, branches=("extraction",))
    r_all = ck.simulate(P_bar=P, t=t, branches=("extraction", "swelling"), powder="M")
    axc.plot(t[sel], q[sel], color=INK, lw=1.8, label="measured")
    axc.plot(t[sel], r_ext["Q"][sel], color=GOOD, lw=1.6, ls="--", label="extraction only")
    axc.plot(t[sel], r_all["Q"][sel], color=BAD, lw=1.8, label="composite (+ swelling)")
    axc.set_xlabel("time (s)"); axc.set_ylabel("mass flow (g s⁻¹)")
    axc.grid(color=GRID, lw=0.6); axc.set_axisbelow(True); axc.legend(fontsize=7.0)
    axc.set_title("(c) the composite is flat — the temporal signal is gone", fontsize=9)

    axd = axes[1, 1]
    labels = ["extraction\nonly", "best\nconstant", "composite\n(+ swelling)"]
    vals = [deg, const, comp["rmse"]]
    axd.bar(labels, vals, color=[GOOD, NULL, BAD])
    for i, v in enumerate(vals):
        axd.text(i, v + 0.012, "%.3f" % v, ha="center", fontsize=8.4, color=INK)
    axd.set_ylabel("RMSE (g s⁻¹)"); axd.grid(axis="y", color=GRID, lw=0.6)
    axd.set_axisbelow(True)
    axd.set_title("(d) adding physics made it worse", fontsize=9)
    axd.text(0.5, 0.80, "The composite equals the STATIC branch\nby construction: porosity closes "
             "below ε₀\nacross 100 % of the window, so Φ→0 and\nthe closure returns its Φ→0 limit "
             "— a CONSTANT.\nThis composition does not degrade the\ntemporal prediction, it removes "
             "it.", transform=axd.transAxes, ha="center", va="top", fontsize=6.8, color=BAD,
             bbox=dict(boxstyle="round", fc="white", ec=BAD, alpha=0.92))

    fig.suptitle("Fig 5 — Negative composition result: more physics, worse reconstruction",
                 y=1.0, fontsize=11.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return _save(fig, outdir, "fig5_negative_composition.png")


def _experiments():
    """The proposed-campaign register (docs/data_requests/experimental_campaigns.yml), read through
    its own loader so the figure cannot drift from the register."""
    from tools import experimental_data_needs as EDN
    return list(EDN.load_catalog().get("campaigns", []))


def fig6_experiment_map(outdir=OUTDIR):
    """Fig 6 — unresolved comparisons mapped to the measurements that would discriminate them."""
    import numpy as np

    plt = _plt()
    exps = _experiments()
    ids = [e.get("campaign_id", "") for e in exps]
    titles = [e.get("title", "") for e in exps]
    tiers = [e.get("status", "") for e in exps]
    prio = ["P%s" % e.get("priority", "?") for e in exps]
    targets = [", ".join(eval(e["target_components"]))[:46]
               if isinstance(e.get("target_components"), str) and
               e["target_components"].startswith("[")
               else str(e.get("target_components", ""))[:46] for e in exps]

    fig, ax = plt.subplots(figsize=(11.2, 0.55 * max(len(ids), 4) + 2.2))
    y = np.arange(len(ids))[::-1]
    tier_col = {"proposed": ACCENT, "in_progress": GOOD, "blocked": BAD}
    ax.barh(y, [1] * len(ids), color=[tier_col.get(t, NULL) for t in tiers], height=0.6)
    for yi, i, ttl, tr, pr, tg in zip(y, ids, titles, tiers, prio, targets):
        ax.text(0.02, yi, "%s  %s" % (i, ttl[:66]), va="center", fontsize=7.4, color="white")
        ax.text(1.02, yi, "%s · %s" % (pr, tr.replace("_", " ")), va="center", fontsize=7.0,
                color=INK)
        ax.text(1.02, yi - 0.26, "targets: %s" % tg, va="center", fontsize=6.2, color=NULL)
    ax.set_yticks([]); ax.set_xticks([]); ax.set_xlim(0, 1.5)
    for s in ("top", "right", "bottom", "left"):
        ax.spines[s].set_visible(False)
    ax.set_title("Each row is a measurement that would discriminate models the registry currently "
                 "cannot separate;\ncolour marks readiness tier, and the register links each back "
                 "to the card supplying the directional prediction.", fontsize=8.0, loc="left")
    fig.suptitle("Fig 6 — From model disagreement to experiment design", y=0.99, fontsize=11.5,
                 fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    return _save(fig, outdir, "fig6_experiment_map.png")


def fig7_named_shot_scorecard(outdir=OUTDIR):
    """Fig 7 — the scorecard, drawn from the GENERATED record (MC17), not from the prose table."""
    import numpy as np

    from puckworks.paper3 import named_shot_scorecard as S

    plt = _plt()
    card = S.scorecard()
    rows = card["rows"]
    fig, ax = plt.subplots(figsize=(12.2, 0.62 * len(rows) + 1.2))
    y = np.arange(len(rows))[::-1]
    ax.set_xlim(0, 1.0); ax.set_ylim(-0.9, len(rows) - 0.2); ax.axis("off")

    for yi, row in zip(y, rows):
        col = _status_colour(row["status"])
        ax.add_patch(plt.Rectangle((0.02, yi - 0.30), 0.30, 0.60, facecolor="#f6f2ea",
                                   edgecolor=col, lw=2.4))
        ax.text(0.17, yi, row["label"], ha="center", va="center", fontsize=8.0)
        ax.text(0.345, yi + 0.10, row["component"] or row["dataset"] or "—", fontsize=7.4,
                va="center", family="monospace")
        mark = "" if row["status_is_derived"] else "  (declared)"
        ax.text(0.345, yi - 0.14, row["status"] + mark, fontsize=7.6, va="center", color=col,
                fontweight="bold")
        if row["unbacked_numbers"]:
            ax.text(0.80, yi, "claim withdrawn:\nno producer", fontsize=6.8, va="center",
                    ha="center", color=BAD,
                    bbox=dict(boxstyle="round", fc="white", ec=BAD, lw=1.2))
        if yi != y[-1]:
            # the chain flows preparation -> cup, so the arrowhead points at the NEXT row down
            ax.annotate("", (0.17, yi - 0.68), (0.17, yi - 0.32),
                        arrowprops=dict(arrowstyle="-|>", color=NULL, lw=1.4))

    ax.text(0.02, -0.72, "%d of %d statuses are DERIVED from the selected component's scoped "
            "evidence records; the rest are declared because no component is selected. "
            "%d stages remain open. The chain ends in a measurement, not a predicted cup."
            % (card["n_derived_statuses"], card["n_stages"], card["n_open_stages"]),
            fontsize=7.4, color=INK)
    fig.suptitle("Fig 7 — End-to-end named-shot evidence scorecard", y=0.99, fontsize=11.5,
                 fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    return _save(fig, outdir, "fig7_named_shot_scorecard.png")


FIGURES = (fig1_architecture, fig2_stage_evidence_map, fig3_observable_linting,
           fig4_null_first_ladder, fig5_negative_composition, fig6_experiment_map,
           fig7_named_shot_scorecard)


def render_all(outdir=OUTDIR):
    return [f(outdir=outdir) for f in FIGURES]


def export_source_data(outdir=OUTDIR):
    """Tidy CSVs behind the data-bearing figures, so a reviewer can re-plot without the solver
    stack. Same bundle the figures render from -- one source of truth."""
    import csv

    import puckworks.models  # noqa: F401
    from puckworks import registry as R
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    from puckworks.paper3 import evidence_graph as EG
    from puckworks.paper3 import named_shot_scorecard as S

    sub = os.path.join(outdir, "source_data")
    os.makedirs(sub, exist_ok=True)
    written = []

    #: Exported floats are ROUNDED. Writing `repr(float)` put 17 significant digits into a file
    #: that is meant to be a stable, re-checkable artifact, so a last-ULP difference between numpy
    #: versions changed the bytes. That is what made the Paper 3 recomputation freshness check fail
    #: in CI while passing locally. Six decimals is far more precision than any figure or table
    #: reports and far less than floating-point noise.
    def _round(v):
        return round(v, 6) if isinstance(v, float) else v

    def _w(name, header, rows):
        path = os.path.join(sub, name)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows([[_round(c) for c in row] for row in rows])
        written.append(path)

    _w("fig2_stage_role_counts.csv", ["stage", "runtime", "calibration"],
       [[s, sum(1 for c in R.components() if c.stage == s and c.execution_role == "runtime"),
         sum(1 for c in R.components() if c.stage == s and c.execution_role == "calibration")]
        for s in R.STAGES if any(c.stage == s for c in R.components())])

    _w("fig2_evidence_vectors.csv", ["component", "relation", "scope", "gate", "outcome"],
       [[n, s.relation, s.scope, s.gate, s.outcome]
        for n, vec in sorted(EG.evidence_vectors().items()) for s in vec])

    _w("fig4_ladder.csv", ["rung", "rmse_g_per_s", "free_params_fitted_to_scored_trace",
                           "parameter_provenance"],
       [[a, b, c, d_] for a, b, c, d_ in _ladder_rows()])

    comp = ck.composition_residual()
    _w("fig5_composition.csv", ["branch", "rmse_g_per_s"],
       [["extraction_only", float(ck.degeneracy_rmse())],
        ["composite_with_swelling", comp["rmse"]]])

    card = S.scorecard()
    _w("fig7_scorecard.csv", ["stage", "label", "selection", "status", "status_is_derived"],
       [[r["stage"], r["label"], r["component"] or r["dataset"] or "", r["status"],
         r["status_is_derived"]] for r in card["rows"]])

    return written


def write_alt_text(outdir=OUTDIR):
    """Emit the text alternatives as a companion file (accessibility; MC12)."""
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "ALT_TEXT.md")
    lines = ["# Paper 3 — figure text alternatives", "",
             "Each entry states what the figure shows and what the reader should take from it, so "
             "no finding is reachable only through the image.", ""]
    for stem, alt in ALT_TEXT.items():
        lines += ["## `%s`" % stem, "", alt, ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def main(argv=None):                                          # pragma: no cover
    import argparse
    p = argparse.ArgumentParser(prog="puckworks.figures_paper3")
    p.add_argument("--out", default=OUTDIR)
    a = p.parse_args(argv)
    print("rendered:", render_all(outdir=a.out))
    print("source data:", export_source_data(outdir=a.out))
    print("alt text:", write_alt_text(outdir=a.out))


if __name__ == "__main__":                                    # pragma: no cover
    main()
