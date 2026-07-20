"""Notebook-formatting helpers for the Full Laboratory Tour deep dive (#43, ROADMAP §8).

Pure string builders (no IPython, no matplotlib) so the notebook JSON stays small and the formatting is
unit-tested here instead of embedded fragile in a cell. The notebook calls these and wraps each returned
string in ``IPython.display.Markdown``; because each block is displayed separately, paragraphs are
naturally blank-line separated (never "space + \\n").

Contract enforced by tests:
  * the dominant per-model heading is a PUBLIC name, never the raw dotted component id;
  * the novice explanation is split into labelled sections (What changes / What the model shows / Why this
    happens / Scope) — no italic wall of text, no ``*Figure — ...*`` line;
  * fixed inputs are humanized (``Dose: 20 g``, not ``dose_g=20.0``);
  * all technical evidence (component id, reference, role, physics, badge, evidence strength, varied +
    fixed inputs, fidelity ceiling, VizSpec id, producer, execution status) lives in a collapsed
    ``<details>`` block so a novice is not forced through it.
"""
from __future__ import annotations

import re

# ── value + label humanization ────────────────────────────────────────────────────────────
_FIXED_LABELS = {
    "dose_g": ("Dose", "g"),
    "target_beverage_g": ("Target beverage mass", "g"),
    "beverage_g": ("Beverage mass", "g"),
    "pressure_bar": ("Pressure", "bar"),
    "grind_setting": ("Grind setting", ""),
    "brew_temperature_c": ("Brew temperature", "°C"),
    "brew_temp_c": ("Brew temperature", "°C"),
}

_REASON_TEXT = {
    "NO_DEFENSIBLE_PUBLIC_RELATIONSHIP_YET":
        "No public figure yet — this component contributes a scientific self-check rather than a novel "
        "public relationship. Its check status lives in the technical details below.",
    "RIGHTS_BLOCKED":
        "No figure — this component is rights-blocked and is shown but never run here.",
    "OPTIONAL_DEPENDENCY_UNAVAILABLE":
        "No figure — an optional dependency is unavailable in this runtime, so the component did not run.",
    "REFERENCE_ONLY":
        "No figure — this component runs its own native reference case only.",
    "TOO_EXPENSIVE_FOR_DEFAULT_TOUR":
        "No figure — this relationship is too expensive to compute in the default tour.",
}

SEPARATOR = "\n\n---\n\n"


def format_number(v) -> str:
    """Compact number: drop a trailing ``.0`` (20.0 → '20'), keep real decimals (1.7 → '1.7')."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if f == int(f):
        return str(int(f))
    return f"{f:g}"


def humanize_label(key: str) -> tuple[str, str]:
    if key in _FIXED_LABELS:
        return _FIXED_LABELS[key]
    # generic fallback: strip a trailing unit token and title-case
    for suffix, unit in (("_g", "g"), ("_bar", "bar"), ("_c", "°C"), ("_s", "s"), ("_pct", "%")):
        if key.endswith(suffix):
            return key[: -len(suffix)].replace("_", " ").capitalize(), unit
    return key.replace("_", " ").capitalize(), ""


def humanize_fixed(fixed: dict) -> list[str]:
    """``{'dose_g':20.0,'pressure_bar':9.0}`` → ``['Dose: 20 g', 'Pressure: 9 bar']``."""
    out = []
    for k, v in (fixed or {}).items():
        name, unit = humanize_label(k)
        out.append(f"{name}: {format_number(v)}{(' ' + unit) if unit else ''}")
    return out


def public_model_name(cid: str) -> str:
    """A public author–year name from a component id — NEVER the raw dotted identifier as a heading.
    ``cameron2020.extraction_bdf`` → 'Cameron (2020)'; ``fasano2000_partI.fines_migration`` →
    'Fasano (2000, part I)'; ``brewer2026.lb_reference`` → 'Brewer (2026)'."""
    head = cid.split(".", 1)[0]
    m = re.match(r"([a-zA-Z]+)(\d{4})(?:_(.+))?$", head)
    if not m:
        return head.replace("_", " ").title()
    author, year, extra = m.group(1).title(), m.group(2), m.group(3)
    if extra:
        extra = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", extra).replace("_", " ")   # partI -> part I
    tail = f", {extra}" if extra else ""
    return f"{author} ({year}{tail})"


# ── per-model blocks ───────────────────────────────────────────────────────────────────────
def model_heading(story, cid: str) -> str:
    """Dominant H2: process stage + public model name. The raw id is NOT here (it is in details)."""
    return f"## {story.process_stage} — {public_model_name(cid)}"


def model_intro_blocks(story, cid: str) -> list[str]:
    return [model_heading(story, cid),
            f"**What it computes.** {story.what_it_computes}"]


def figure_headline_block(headline: str, question: str) -> str:
    """The figure's public heading + question (the figure itself no longer repeats these)."""
    return f"### {headline}\n\n**Question.** {question}"


def narrative_blocks(narrative) -> list[str]:
    """Structured novice explanation as separate blocks (short normal paragraphs; Scope as a blockquote)."""
    blocks = [f"**What changes.** {narrative.setup}",
              f"**What the model shows.** {narrative.finding}",
              f"**Why this happens.** {narrative.mechanism}"]
    if narrative.takeaway:
        blocks.append(f"**What is interesting.** {narrative.takeaway}")
    blocks.append(f"> **Scope.** {narrative.scope}")
    return blocks


def cup_block(story) -> str:
    """The single 'for your cup' note per model (not part of any figure's technical metadata)."""
    return f"**What this might mean for your cup.** {story.espresso_implications}"


def no_figure_block(reason: str, message: str = "") -> str:
    text = _REASON_TEXT.get(reason, f"No figure ({reason}).")
    note = f" _{message}_" if message else ""
    return f"_{text}_{note}"


def _figure_evidence_lines(figs: list) -> list[str]:
    lines = []
    for f in figs:
        fixed = "; ".join(humanize_fixed(f.fixed_inputs)) or "—"
        varied, _ = humanize_label(f.varied_input) if f.varied_input else ("reference case", "")
        lines += [
            f"- **{f.headline}** (`{f.viz_spec_id}`)",
            f"  - Evidence: {f.evidence_badge.replace('_', ' ')} · {f.evidence_strength}",
            f"  - Varied input: {varied}",
            f"  - Held fixed: {fixed}",
            f"  - Fidelity ceiling: {f.fidelity_ceiling}",
            f"  - Producer: `{f.producer_ref}`",
        ]
    return lines


def evidence_details_block(cid: str, story, result: dict, reference: str, figs: list) -> str:
    """The collapsed <details> block carrying every technical/evidence field for this model."""
    status = (result or {}).get("execution_status", "—")
    lines = ["<details>", "<summary><strong>Evidence and technical details</strong></summary>", "",
             f"- Component id: `{cid}`",
             f"- Execution status: {status}"]
    if reference:
        lines.append(f"- Full reference: {reference}")
    lines += [f"- Role: {story.role}",
              f"- What physics it represents: {story.physics}"]
    if figs:
        lines += ["", "**Figures**", *_figure_evidence_lines(figs)]
    lines += ["", "</details>"]
    return "\n".join(lines)


def model_separator() -> str:
    return SEPARATOR
