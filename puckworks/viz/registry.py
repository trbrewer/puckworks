"""VIZZES — the evidence-bound visual registry + the badge/provenance stamp.

Single source of truth for every visual: each `VizSpec` binds to a Producer,
carries a public badge + evidence-strength + fidelity ceiling, and names a
lazily-resolved `render_fn`. `stamp_fig` draws the badge + evidence + source
commit INTO every output. Badges/evidence/ceilings here are the ENCODED form of
the hand-authored acceptance seed (`docs/figures/viz/GALLERY.md`); the generated
gallery must reproduce it, and any residual divergence is recorded in ROADMAP
§7.1 (never silently reconciled).

No matplotlib at import time (drawing modules + matplotlib load lazily in the
render path), so this registry imports on the core install.
"""
from __future__ import annotations
import importlib
import subprocess

from .spec import VizSpec, FIDELITY_CEILINGS
from .palette import BADGE_COLORS, BADGE_TEXT_COLOR, INK
from ..public.schema import Producer

_P = "puckworks.viz.producers"
_H = "puckworks.harness"
_C1 = "puckworks.viz.class1_diagrams"
_C2 = "puckworks.viz.class2_render"

# ---------------------------------------------------------------------------
VIZZES = [
    # ===== Class 1 — functional 2D ========================================
    VizSpec(
        id="process_schematic", title="Espresso process map (6 stages, one lens each)",
        class_=1, composite=True,
        producer=Producer(module=_P, function="process_stages",
                          result_map={"stages": "stages"}),
        badge="EXPLORATORY_SIMULATION",   # composite: STRICTEST lens badge (Note 1)
        evidence_strength="reference",
        fidelity_ceiling=(
            "Depicts REGISTRY STRUCTURE (stages, components, kinds), not physics. "
            "Each stage lens carries its own badge inline; the diagram asserts "
            "nothing about mechanism fidelity."),
        render_fn=f"{_C1}:draw_process_schematic", components=["registry"],
        caption="Labelled grind→packing→machine→infiltration→flow→extraction→"
                "bed-dynamics map. Each stage carries its OWN component's badge — the "
                "composite is illustrative, not one mega-model.",
        outputs=["thumb.png", "full PNG/SVG"],
        used_in="ONBOARDING orientation; PV-08; PV-09 title card; Paper A/B "
                "Fig-1-style design figures"),
    VizSpec(
        id="shot_metric_frame", title="Annotated shot: P(t), Q(t), mass on a real trace",
        class_=1,
        producer=Producer(module=_P, function="shot_traces",
                          result_map={"t": "t_s", "P": "pressure_bar",
                                      "Q": "mass_flow_g_s", "m": "mass_g"}),
        badge="OBSERVED", evidence_strength="independent", evidence_scope="within-rig",
        fidelity_ceiling=(
            "Measured machine traces. Caveats rendered: fixture-A pressure-NODE "
            "identity is OPEN (§5.9); Waszkiewicz constants are rig/coffee/grind-"
            "specific; TDS fractions 5-s bins, first bin single replicate."),
        render_fn=f"{_C1}:draw_shot_metric_frame",
        components=["waszkiewicz2025", "de1_fixtureA"],
        caption="Measured pressure-controlled shot (one public rig). An OBSERVED "
                "trace, not a universal curve.",
        outputs=["thumb.png", "annotated frames", "optional video"],
        used_in="PV-01, PV-02, PV-19 scorecard; Paper B §3/§4 context panels"),
    VizSpec(
        id="kappa_t_ladder_fig", title="κ(t) null-first ladder (Paper B Fig 3)",
        class_=1,
        producer=Producer(module=_H, function="kappa_t_ladder",
                          result_map={"phi_rmse": "rung4_phi_of_t",
                                      "const_null": "rung1_const_kappa",
                                      "cubic": "flexible_cubic_null"}),
        badge="RECONSTRUCTED", evidence_strength="post-fit reconstruction",
        fidelity_ceiling=(
            "One rig, 15-95 s window. Φ(t) rung = '0 additional coefficients fitted "
            "to THIS trace' (m_d sigmoid is a same-rig 9-bar TDS calibration — soft "
            "circularity); flexible cubic = in-sample flexibility bound; swelling "
            "rung 5b = QUALITATIVE cross-rig sign check. Ladder shows 'time variation "
            "is needed', NOT 'a specific bed mechanism is proven'."),
        render_fn=f"{_C1}:draw_kappa_t_ladder",
        components=["waszkiewicz2025.poroelastic"],
        caption="Φ(t) reconstructs the 9-bar trace better than any constant null but "
                "TIES a flexible cubic — time variation needed, mechanism not identified.",
        outputs=["thumb.png", "PNG"], used_in="Paper B §4 Fig 3; PV-02; PV-06"),
    VizSpec(
        id="identifiability_valley_fig",
        title="Inventory↔kinetics SSE valley (Paper A Fig 2)", class_=1, slow=True,
        producer=Producer(module="puckworks.validation.slow.angeloni_bracket",
                          function="identifiability_panel",
                          result_map={"coupling": "local_curvature_coupling"},
                          slow=True),
        badge="RECONSTRUCTED", evidence_strength="post-fit reconstruction",
        fidelity_ceiling=(
            "SSE surface = a LOCAL-CURVATURE DIAGNOSTIC, not a likelihood; the "
            "coupling coefficient is NOT a correlation; matched-40 g endpoints; "
            "single-grind whole-cup fit — the valley shows NON-IDENTIFIABILITY, it "
            "does not localize a 'true' rate."),
        render_fn=f"{_C1}:draw_identifiability_valley",
        components=["identifiability"],
        caption="A flat SSE valley: inventory and kinetics trade off along a ridge — "
                "an identifiability diagnostic, not a localized true rate.",
        outputs=["thumb.png", "PNG"], used_in="Paper A §4 Fig 2; PV-03"),

    # ===== Class 2 — high-fidelity render =================================
    VizSpec(
        id="puck_flow_field", title="Stokes channel flow (verification geometry)",
        class_=2,
        producer=Producer(module=_P, function="stokes_channel_field",
                          result_map={"u_max": "u_max",
                                      "lb_err_pct": "lb_err_pct_vs_analytic"}),
        badge="EXPLORATORY_SIMULATION", evidence_strength="verification",
        fidelity_ceiling=(
            "'Computed Stokes-regime flow in a VERIFICATION geometry' — never 'the "
            "flow in your puck'. Stokes only (no inertia; DE1 tamped Fo_F ≈0.86-5.7 "
            "says real shots sit at/past inertial onset, §5.2); geometry is "
            "Boolean-sphere pack, untamped-validated k only."),
        render_fn=f"{_C2}:draw_puck_flow_field",
        components=["brewer2026.lb_reference", "brewer2026.lb_taichi"],
        caption="Computed Stokes flow on verification geometry (the LB twin matches "
                "the analytic profile to lb_err_pct). NOT the flow in your puck.",
        outputs=["thumb.png", "hi-res stills", "video (gitignored)"],
        used_in="PV-09 flow lens; Paper B visual companion / GFM candidate"),
    VizSpec(
        id="grain_pack_3d", title="Synthetic sphere pack coloured by local porosity",
        class_=2,
        producer=Producer(module=_P, function="pack_porosity_slice",
                          result_map={"phi": "phi", "phis": "phis"}),
        badge="EXPLORATORY_SIMULATION", evidence_strength="qualitative",
        fidelity_ceiling=(
            "Boolean (overlapping) spheres — an idealization, not imaged coffee. "
            "FINES ARE NOT RESOLVED: render the columnar-heterogeneity FIELD and "
            "label it as a field, never as particles. Grain radius ≥10 voxels; σ "
            "closure calibrated on 3 points. Tamped regime = extrapolation for any "
            "permeability colouring."),
        render_fn=f"{_C2}:draw_grain_pack_3d",
        components=["brewer2026.pack_generator", "wadsworth2026.permeability"],
        caption="Synthetic Boolean-sphere packing; grains drawn honestly, fines are a "
                "HETEROGENEITY FIELD (not resolved particles). 3D behind [viz3d].",
        outputs=["thumb.png", "3D stills", "turntable video (gitignored)"],
        used_in="PV-09 grind/pack lens; PV-11; public explainers"),
    VizSpec(
        id="wetting_front_sweep", title="Infiltration wetting front s(t)", class_=2,
        producer=Producer(module=_P, function="wetting_front",
                          result_map={"L_mm": "L_mm", "t_sat": "t_saturate_s"}),
        badge="RECONSTRUCTED", evidence_strength="independent",
        evidence_scope="parameter-free gate",
        fidelity_ceiling=(
            "Sharp BINARY front — the model says nothing about partial saturation "
            "behind the front (that is open gap G1; do not shade a saturation "
            "gradient). "
            "Fine grind (<300 µm) only; source declines the coarse case. Machine-mode "
            "reported times include fitted t_shift (post-fit) — label if shown."),
        render_fn=f"{_C2}:draw_wetting_front_sweep",
        components=["foster2025.infiltration", "foster2025.machine_mode"],
        caption="Wetting front from the recorded pressure — a reconstruction of the "
                "CT-validated Foster front model (nominal params, labelled).",
        outputs=["thumb.png", "frames", "video (gitignored)"],
        used_in="PV-01, PV-18 companion; PV-09 infiltration lens; Paper B §2 context"),
    VizSpec(
        id="channeling_concentration",
        title="Dynamic channel concentration (one configuration)", class_=2,
        producer=Producer(module=_P, function="channeling_concentration",
                          result_map={"n_eff_over_N": "n_eff_over_N",
                                      "collapse_time_s": "collapse_time_s"}),
        badge="EXPLORATORY_SIMULATION", evidence_strength="qualitative",
        fidelity_ceiling=(
            "Static σ(φ₁) is an EMPIRICAL closure (dial 1.1-1.5, LOO-interpolated, "
            "not externally validated). Dynamic N-tube collapse is ONE CONFIGURATION "
            "(gs 1.1, 9 bar, N=200) — 'strong concentration in the tested config', "
            "NOT a proven instability (G-lat); the lateral term is a HOMOGENIZING "
            "PROXY, not physical coupling (card-blocked; PV-14 constraint). "
            "Flow-control-specific — no latch under pressure control; render both if "
            "both are shown."),
        render_fn=f"{_C2}:draw_channeling_concentration",
        components=["brewer2026.streamtube", "ntube_union"],
        caption="N-tube flow concentrates to N_eff→1 in ONE configuration "
                "(gs 1.1, 9 bar, N=200) — one configuration, not a general result.",
        outputs=["thumb.png", "animation (gitignored)"],
        used_in="PV-14; Paper B §5 / Fig 5 companion; PV-09 bed-dynamics lens"),
    VizSpec(
        id="fines_migration_mechanism",
        title="Fines migration mechanism (fasano-structured)", class_=2,
        producer=Producer(module=_P, function="fines_migration",
                          result_map={"mass_balance": "mass_balance"}),
        badge="EXPLORATORY_SIMULATION", evidence_strength="qualitative",
        fidelity_ceiling=(
            "MECHANISM ILLUSTRATION ONLY: fasano-STRUCTURED — closures are OURS "
            "(paper's K(b,m), M, γ unpublished), zero identified parameters, NO "
            "coffee fit. May show release→advection→compact-layer growth and the "
            "nonmonotone q∞(p₀) SHAPE; must NOT be rendered as measured fines "
            "transport or given real-espresso parameter labels."),
        render_fn=f"{_C2}:draw_fines_migration",
        components=["fasano2000_partI.fines_migration"],
        caption="Release→advection→compact-layer growth + the q∞(p₀) shape. Closures "
                "are ours, not the paper's; not a coffee fit.",
        outputs=["thumb.png", "animation (gitignored)"],
        used_in="PV-09 fines lens (labelled); κ(t)-discrimination protocol explainer; "
                "Paper B mechanism figure"),

    # ===== Whole process — PV-09 multi-lens montage =======================
    VizSpec(
        id="hidden_puck_movie",
        title="The hidden puck — multi-lens montage (PV-09)", class_=2,
        class_label="1+2", composite=True, slow=True,
        producer=Producer(module=_P, function="process_stages",
                          result_map={"stages": "stages"}),
        badge="EXPLORATORY_SIMULATION",   # composite: STRICTEST lens badge (Note 1)
        evidence_strength="qualitative",
        fidelity_ceiling=(
            "PV-09 contract verbatim: PARALLEL LABELLED LENSES, NOT a mega-model. The "
            "shared shot clock synchronizes DISPLAY only — no cross-lens physical "
            "coupling is implied or computed. Every lens keeps its own badge + "
            "evidence label on screen for its full duration."),
        render_fn="puckworks.viz.process_movie:draw_hidden_puck_movie",
        components=["registry", "brewer2026.pack_generator", "foster2025.infiltration",
                    "brewer2026.lb_reference", "ntube_union", "waszkiewicz2025"],
        caption="PV-09: parallel labelled lenses on one shot clock — each lens its own "
                "component + badge. NOT one seamless mega-simulation.",
        outputs=["thumb.png", "montage video (gitignored)"],
        used_in="PV-09; SDCC / GFM / World of Coffee public venues; project trailer"),
]


def viz_by_id(vid) -> VizSpec:
    for v in VIZZES:
        if v.id == vid:
            return v
    raise KeyError(f"no VizSpec '{vid}' (have: {[v.id for v in VIZZES]})")


def source_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "UNKNOWN"


# --- the badge / provenance stamp (drawn INTO every output) ---------------
def stamp_fig(fig, spec: VizSpec, commit=None):
    """Draw the badge + evidence-strength + source commit onto the figure itself
    (PUBLIC_VALUE §3.1: put the badge in the graphic, not the caption). Returns the
    badge string drawn, so a test can assert it is present."""
    commit = commit if commit is not None else (spec.source_commit or source_commit())
    color = BADGE_COLORS.get(spec.badge, INK)
    label = f" {spec.badge} · {spec.evidence_display()} "
    fig.text(0.008, 0.978, label, ha="left", va="top", fontsize=8,
             fontweight="bold", color=BADGE_TEXT_COLOR,
             bbox=dict(boxstyle="round,pad=0.35", facecolor=color, edgecolor="none"))
    foot = f"{spec.id} · commit {str(commit)[:10]} · ceiling: {spec.fidelity_ceiling}"
    fig.text(0.008, 0.006, foot, ha="left", va="bottom", fontsize=5.2,
             color=INK, wrap=True)
    return spec.badge


def _resolve(render_fn):
    mod, fn = render_fn.split(":")
    return getattr(importlib.import_module(mod), fn)


def producer_data(spec: VizSpec) -> dict:
    """Call the spec's bound producer FUNCTION and return its full output dict (arrays
    included). `producer.compute()` returns only the mapped provenance scalars; a
    render needs the whole series — but from the SAME named function (still honest)."""
    p = spec.producer
    return getattr(importlib.import_module(p.module), p.function)(**p.kwargs)


def render_spec(spec: VizSpec, outdir=None, with_3d=False, video=False):
    """Resolve the spec's render_fn and draw it (badge-stamped). The render_fn owns
    compute+draw+stamp+save and returns a dict with at least {'thumb': path}."""
    import os
    spec.source_commit = source_commit()
    outdir = outdir or os.path.join("docs/figures/viz", spec.id)
    os.makedirs(outdir, exist_ok=True)
    return _resolve(spec.render_fn)(spec, outdir, with_3d=with_3d, video=video)


def render_all(select=None, out="docs/figures/viz", cls=None, with_3d=False,
               video=False, run_slow=False):
    """Render selected specs. Skips slow specs unless run_slow (LB/3D/video are not
    CI work). `select` = list of ids; `cls` = 1 or 2 to filter by class."""
    import os
    results = []
    for spec in VIZZES:
        if select and spec.id not in select:
            continue
        if cls and spec.class_ != cls:
            continue
        if spec.slow and not run_slow:
            results.append({"id": spec.id, "skipped": "slow (needs --slow/--video/--with-3d)"})
            continue
        results.append(render_spec(spec, outdir=os.path.join(out, spec.id),
                                   with_3d=with_3d, video=video))
    return results


def compute_spec(spec: VizSpec, out="docs/figures/viz"):
    """Two-step pipeline (like figures_paper_a): run the spec's Producer ONCE and
    cache to docs/figures/viz/<id>/data.json, provenance-stamped with source_commit."""
    import json
    import os
    data = spec.producer.compute()
    payload = {"id": spec.id, "producer": spec.producer.ref(),
               "source_commit": source_commit(), "badge": spec.badge,
               "evidence_strength": spec.evidence_strength, "data": data}
    outdir = os.path.join(out, spec.id)
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "data.json")
    with open(path, "w") as f:
        json.dump(payload, f, default=str)
    return path


def compute_all(select=None, out="docs/figures/viz", run_slow=False):
    """Run (cached) producers for the selected specs; skip slow ones unless run_slow."""
    done = []
    for spec in VIZZES:
        if select and spec.id not in select:
            continue
        if spec.producer.slow and not run_slow:
            done.append({"id": spec.id, "skipped": "slow producer"})
            continue
        done.append({"id": spec.id, "cached": compute_spec(spec, out=out)})
    return done


def validate_all() -> list:
    """Every VizSpec must pass its honesty contract (empty == clean)."""
    errs = []
    for v in VIZZES:
        errs.extend(v.validate())
    return errs


def write_gallery(path="docs/figures/viz/GALLERY.md"):
    """Regenerate the honesty index from the specs, in the SEED's column layout so
    it can be diffed against the hand-authored acceptance table. Composites (Note 1)
    render the STRICTEST lens badge with a '(composite)' marker; evidence scope
    qualifiers ride in parentheses (closed vocab word unchanged)."""
    import os
    commit = source_commit()
    lines = [
        "# Visual gallery — every visual and its honesty label (generated)",
        "",
        "*Generated by `python -m puckworks.viz gallery` from "
        "`puckworks/viz/registry.py`. Do not hand-edit — regenerate. Every visual "
        "binds to a producer and carries a public badge + evidence-strength + a "
        "fidelity ceiling it may not exceed (ROADMAP §8). Composites carry the "
        "STRICTEST lens badge (Note 1); per-lens badges are drawn inline.*",
        "",
        f"Source commit `{commit[:10]}`.",
        "",
        "| id | class | badge | evidence strength | producer / source component(s) | "
        "fidelity ceiling (binding caption content) | outputs | used in |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for v in VIZZES:
        src = f"`{v.producer.ref()}` — " + "; ".join(v.components)
        lines.append("| {id} | {cls} | {badge} | {ev} | {src} | {ceil} | {out} | {use} |".format(
            id=v.id, cls=v.class_display(), badge=v.badge_display(),
            ev=v.evidence_display(), src=src,
            ceil=v.fidelity_ceiling.replace("|", "/"),
            out=" + ".join(v.outputs), use=v.used_in))
    lines += ["", "## Captions", ""]
    for v in VIZZES:
        lines.append(f"- **{v.id}** — {v.caption}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path
