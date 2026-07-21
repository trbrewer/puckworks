"""Rendering the Espresso Model Relay for humans — a standalone Markdown report and notebook Markdown
blocks. Pure string builders (no IPython): the notebook wraps each block in `IPython.display.Markdown`.

Everything here reads the SERIALIZED result dict, so what a reader sees can never drift from the recorded
provenance. The permanent illustrative warning is always emitted near the top and again at the end.
"""
from __future__ import annotations

from . import linked_pull_manifest as MAN
from .linked_pull_narrative import format_value

PERMANENT_WARNING = (
    "**Important — this is an illustrative model relay.**\n\n"
    "Puckworks' components come from different papers, machines, coffees, geometries, definitions, and "
    "evidence levels. This notebook deliberately passes selected outputs between them to demonstrate "
    "possible platform capabilities. Some handoffs are direct, some use documented adapters, and some "
    "require substantial assumptions. The complete relay has **not** been validated as one scientific "
    "model. Treat its outputs as educational model lenses, not as a prediction of your espresso or its "
    "flavour.")

_EDGE_STYLE = {
    "DIRECT_MODEL_OUTPUT": "solid line — direct model output",
    "DOCUMENTED_ADAPTER": "dashed line — documented adapter",
    "ILLUSTRATIVE_ASSUMPTION": "dotted line — illustrative assumption",
    "SHARED_INPUT_ONLY": "thin grey line — shared input only",
    "DIAGNOSTIC_ONLY": "thin grey line — diagnostic only",
    "OPTIONAL_SLOW_PATH": "dashed line — optional (extended mode)",
    "RIGHTS_BLOCKED": "blocked — no execution",
}


def legend_lines() -> list:
    return [f"- {v}" for v in _EDGE_STYLE.values()]


# ── counts banner ─────────────────────────────────────────────────────────────────────────
def counts_summary(result: dict) -> str:
    c = result["counts"]
    return ("**This relay at a glance** — "
            f"{c['components_executed']} components executed · {c['cross_component_handoffs']} "
            f"cross-component hand-offs "
            f"({c['direct_handoffs']} direct, {c['documented_adapters']} documented adapters, "
            f"{c['illustrative_assumptions']} illustrative assumptions) · "
            f"{c['assumptions_introduced']} named assumptions. No single confidence score — the value is "
            f"the visible trail, not one number.")


# ── chain map (generated from LinkRecords, never hand-drawn) ────────────────────────────────
def chain_map_text(result: dict) -> str:
    """A deterministic text chain map built from the serialized links + dispositions."""
    disp = {s["component_id"]: s for s in result["stages"]}
    lines = ["Recipe card", "  |"]
    by_station = MAN.dispositions_by_station()
    for sid in MAN.STATION_IDS:
        if sid in ("recipe", "dashboard"):
            continue
        st = next(s for s in MAN.STATIONS if s[0] == sid)
        lines.append(f"  v  [{st[1]}]")
        for d in by_station[sid]:
            row = disp.get(d.component_id, {})
            status = row.get("status", d.intended_status.value)
            mark = "  x " if status == "RIGHTS_BLOCKED" else "  - "
            lines.append(f"{mark}{d.component_id}  ({status})")
    lines.append("  v  [One pull, several readings]")
    edges = [f"    {e['source_component_id'] or 'recipe'} --{e['kind']}--> {e['target_component_id']}"
             for e in result["links"]]
    return "\n".join(lines) + "\n\n  hand-offs:\n" + "\n".join(edges)


# ── per-stage notebook blocks ───────────────────────────────────────────────────────────────
def station_blocks(stage: dict) -> list:
    """Markdown blocks for one station: public heading, question, what enters, figure slot handled by the
    notebook, then labelled sections + collapsed technical details."""
    from .lab_tour_notebook_display import public_model_name
    nar = stage.get("narrative") or {}
    cid = stage["component_id"]
    name = public_model_name(cid) if cid != "recipe" else "The recipe card"
    blocks = [f"## {stage['public_heading']} — {name}",
              f"**Question.** {nar.get('question', '')}"]
    if nar.get("what_enters"):
        blocks.append("**What enters.** " + "; ".join(nar["what_enters"]))
    if nar.get("what_it_calculates"):
        blocks.append("**What this model calculates.** " + nar["what_it_calculates"])
    if nar.get("what_the_model_shows"):
        blocks.append("**What the model shows.** " + nar["what_the_model_shows"])
    if nar.get("what_is_handed_forward"):
        blocks.append("**What we hand forward.** " + nar["what_is_handed_forward"])
    if nar.get("assumptions"):
        blocks.append("**What we had to assume.**\n" + "\n".join(f"- {a}" for a in nar["assumptions"]))
    if nar.get("why_it_is_interesting"):
        blocks.append("**Why this is interesting.** " + nar["why_it_is_interesting"])
    if nar.get("possible_cup_implication"):
        blocks.append("**What this might mean for the cup.** " + nar["possible_cup_implication"])
    if nar.get("scope"):
        blocks.append("> **Scope.** " + nar["scope"])
    blocks.append(_details_block(stage))
    return blocks


def _details_block(stage: dict) -> str:
    lines = ["<details>", "<summary><strong>Evidence and technical details</strong></summary>", "",
             f"- Component id: `{stage['component_id']}`",
             f"- Station: {stage['station_id']}",
             f"- Execution status: {stage['status']}",
             f"- Scenario relationship: {stage['scenario_relationship']}",
             f"- Rights decision: {stage['rights_decision']}"]
    if stage.get("outputs"):
        lines.append("- Outputs:")
        for o in stage["outputs"]:
            unit = f" {o['unit']}" if o["unit"] else ""
            aid = f" · assumes {', '.join(o['assumption_ids'])}" if o.get("assumption_ids") else ""
            lines.append(f"  - {o['name']}: {format_value(o['value'])}{unit} "
                         f"[{o['basis']}; {o['origin'].lower()}{aid}]")
    if stage.get("message"):
        lines.append(f"- Note: {stage['message']}")
    lines += ["", "</details>"]
    return "\n".join(lines)


# ── final dashboard (no averaging) ──────────────────────────────────────────────────────────
def _find(result, cid):
    return next((s for s in result["stages"] if s["component_id"] == cid), None)


def _out(stage, name):
    if not stage:
        return None
    return next((o for o in stage["outputs"] if o["name"] == name), None)


def cup_dashboard_blocks(result: dict) -> list:
    """Separate, clearly-labelled result families — never one merged authoritative prediction."""
    blocks = ["## One pull, several readings",
              "> **What this illustrative relay suggests about the final cup**"]
    cam = _find(result, "cameron2020.extraction_bdf")
    ey = _out(cam, "extraction_yield"); tds = _out(cam, "strength_tds")
    fam = []
    if ey and tds:
        fam.append(f"- **Baseline cup (Cameron).** EY {format_value(ey['value'])}%, "
                   f"TDS {format_value(tds['value'])}% — concentration and recovered soluble mass, not flavour.")
    wet = _out(_find(result, "foster2025.infiltration"), "fraction_of_shot_before_saturation")
    if wet:
        fam.append(f"- **Wetting context (Foster).** The sharp front uses ~{format_value(wet['value'])}% "
                   f"of the modeled shot time before the full bed is available.")
    fo = _out(_find(result, "wadsworth2026.inertial"), "forchheimer_number")
    ratio = _out(_find(result, "wadsworth2026.inertial"), "inertial_flow_ratio")
    if fo and ratio:
        fam.append(f"- **Hydraulic context (Wadsworth).** Fo_F {format_value(fo['value'])}; inertial flow "
                   f"is {format_value((1 - ratio['value']) * 100)}% below the naive Darcy value.")
    het = _find(result, "brewer2026.streamtube")
    deficit = _out(het, "ey_deficit_pct")
    if deficit:
        fam.append(f"- **Heterogeneity branch (streamtube).** Uneven paths give ~"
                   f"{format_value(deficit['value'])}% lower EY than the homogeneous Cameron branch.")
    fam.append("- **Puck-change branches.** Waszkiewicz, coupled-kappa, swelling, and fines each show a "
               "possible resistance change — reported separately, never averaged.")
    fam.append("- **Chemistry clocks (Pannusch et al.).** Compounds release on different clocks; equal TDS "
               "need not mean identical composition. Not converted into flavour scores.")
    blocks.append("\n".join(fam))
    blocks.append(counts_summary(result))
    blocks.append("> The value of this relay is not one final number. It is the visible trail from recipe, "
                  "through assumptions and model handoffs, to several scientifically distinct readings of "
                  "the same hypothetical pull.")
    return blocks


# ── the standalone Markdown report ──────────────────────────────────────────────────────────
def relay_markdown(result: dict) -> str:
    out = [f"# The Espresso Model Relay ({result['manifest_id']})",
           "*An illustrative, assumption-rich linked pull across separate models. "
           "This is not a validated coupled simulation.*", "", PERMANENT_WARNING, "",
           counts_summary(result), "", "## Chain map", "```", chain_map_text(result), "```", ""]
    for stage in result["stages"]:
        if stage["component_id"] == "recipe":
            continue
        out += station_blocks(stage) + [""]
    out += cup_dashboard_blocks(result) + ["", "## Assumption ledger", ""]
    for a in result["assumptions"]:
        out.append(f"- **{a['assumption_id']} ({a['category']}).** {a['statement']} "
                   f"_Validation needed:_ {a['validation_needed']}")
    out += ["", "---", "", PERMANENT_WARNING]
    return "\n".join(out)
