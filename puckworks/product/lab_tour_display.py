"""Novice-facing display organization for a Full Laboratory Tour result (Phase 5, #43).

Turns a `LaboratoryTourResult` (or its dict) into ordered, plain-language sections + per-component cards.
It NEVER leads with the internal component id (the id lives in the card's technical detail), never
overlays incompatible results, and states per card what ran, where the inputs came from, whether the
result is comparable to another, and what it does NOT establish. Pure — no notebook/Streamlit dependency.

Each registered component appears in EXACTLY ONE section (a component is never double-counted):
  1. common-scenario (the entered recipe) -> "Your reference shot"
  2. not executed (blocked / optional / not-cleared / no-path) -> "Components not run"
  3. registered scientific check -> "Calibration and evidence checks"
  4. everything else that executed (native references) -> its espresso-stage section
"""
from __future__ import annotations

# ordered stage sections for EXECUTED native-reference results (empty sections are omitted at render time)
_STAGE_SECTIONS = [
    ("Grind and particle representation", "grind"),
    ("Packing and permeability", "packing"),
    ("Machine and boundary conditions", "machine"),
    ("Wetting and infiltration", "infiltration"),
    ("Flow and pressure response", "flow"),
    ("Bed dynamics and migration", "bed_dynamics"),
    ("Extraction and transport", "extraction"),
]

_BADGE = {
    "COMMON_SCENARIO": "USES YOUR SHOT",
    "NATIVE_REFERENCE": "NATIVE REFERENCE CASE",
    "SCIENTIFIC_CHECK": "SCIENTIFIC CHECK",
    "OPTIONAL_DEPENDENCY": "OPTIONAL DEPENDENCY UNAVAILABLE",
    "RIGHTS_BLOCKED": "RIGHTS BLOCKED",
    "NO_EXECUTION_PATH": "NO EXECUTION PATH",
}
_NOT_RUN_STATUSES = {"RIGHTS_BLOCKED", "RIGHTS_NOT_CLEARED", "OPTIONAL_UNAVAILABLE", "NO_EXECUTION_PATH",
                     "DOMAIN_DECLINED"}

_HEADLINE = {
    "COMMON_SCENARIO": "A model that used your recipe",
    "NATIVE_REFERENCE": "A model's own reference case",
    "SCIENTIFIC_CHECK": "A registered scientific check",
    "OPTIONAL_DEPENDENCY": "Needs an optional add-on",
    "RIGHTS_BLOCKED": "Shown, but not run (rights)",
    "NO_EXECUTION_PATH": "Catalogued (no runnable demo yet)",
}
_INPUTS_PLAIN = {
    "ENTERED_RECIPE": "your entered recipe (dose, beverage mass, pressure)",
    "COMPONENT_NATIVE_CASE": "the model's own provenance-bound reference case",
    "REGISTERED_FIXTURE": "the check's own registered data/fixture",
    "NONE": "nothing (this component was not run)",
}
_COMPARABLE = ("compared only to itself — Puckworks never overlays, averages, or ranks different models' "
               "outputs")


def _badge(comp: dict) -> str:
    if comp["execution_status"] == "EXECUTION_ERROR":
        return "EXECUTION ERROR"
    if comp["execution_status"] == "RIGHTS_NOT_CLEARED":
        return "NOT CLEARED HERE"
    if comp["execution_status"] == "DOMAIN_DECLINED":
        return "OUTSIDE EVIDENCE RANGE"
    if comp["execution_status"] == "CHECK_FAILED":
        return "SCIENTIFIC CHECK — FAILED"
    return _BADGE.get(comp["execution_kind"], comp["execution_kind"])


def _does_not_establish(comp: dict) -> str:
    if comp.get("fidelity_ceiling"):
        return comp["fidelity_ceiling"]
    return ("this component was not run here, so it establishes nothing about your shot"
            if comp["execution_status"] in _NOT_RUN_STATUSES else
            "this does not establish a beverage/taste outcome and is not directly comparable to other models")


def component_card(comp: dict, reference: str = "") -> dict:
    """One novice card. Leads with a plain headline + badge; the component id sits in `technical`."""
    return {
        "badge": _badge(comp),
        "headline": _HEADLINE.get(comp["execution_kind"], comp["execution_kind"]),
        "what_ran": comp.get("message", ""),
        "inputs": _INPUTS_PLAIN.get(comp.get("input_origin", "NONE"), comp.get("input_origin", "")),
        "outputs": comp.get("outputs", [])[:4],
        "comparable": _COMPARABLE,
        "does_not_establish": _does_not_establish(comp),
        "technical": {"component_id": comp["component_id"], "stage": comp.get("stage", ""),
                      "execution_kind": comp["execution_kind"], "execution_status": comp["execution_status"],
                      "reference": reference, "rights_decision": comp.get("rights_decision", {}),
                      "scientific_hash": comp.get("scientific_hash")},
    }


def _references() -> dict:
    import puckworks
    out = {}
    for c in puckworks.components():
        out[c.name] = getattr(c, "doi", "") or getattr(c, "paper", "") or ""
    return out


def tour_display_sections(tour) -> list:
    """Ordered [(section_title, [cards])] for a tour result (dict or LaboratoryTourResult). Each component
    appears once; empty stage sections are omitted; 'Overview', 'Components not run', and 'Technical
    provenance' always appear."""
    t = tour if isinstance(tour, dict) else tour.to_dict()
    refs = _references()
    comps = {c["component_id"]: c for c in t["components"]}
    assigned = set()
    sections: list = []

    # 1. Overview (counts only; never aggregates scientific values across components)
    s = t["summary"]
    sections.append(("Overview", [{
        "badge": "OVERVIEW", "headline": "What this tour did",
        "what_ran": (f"Resolved all {s['registered']} registered components; {s['completed']} executed "
                     f"({s['by_kind']['COMMON_SCENARIO']} used your recipe, "
                     f"{s['by_kind']['NATIVE_REFERENCE']} ran a native reference case, "
                     f"{s['by_kind']['SCIENTIFIC_CHECK']} ran a scientific check); "
                     f"{s['rights_blocked']} rights-blocked, {s['optional_unavailable']} optional."),
        "does_not_establish": ("results across models are NOT directly comparable and are never averaged, "
                               "ranked, or overlaid; a check pass is not experimental validation"),
    }]))

    # 2. Your reference shot (the common-scenario result)
    common = [c for c in t["components"] if c["execution_kind"] == "COMMON_SCENARIO"]
    if common:
        sections.append(("Your reference shot", [component_card(c, refs.get(c["component_id"], ""))
                                                 for c in common]))
        assigned.update(c["component_id"] for c in common)

    # 3. Stage sections for EXECUTED native references (empty sections omitted)
    for title, stage in _STAGE_SECTIONS:
        cards = [component_card(c, refs.get(c["component_id"], "")) for c in t["components"]
                 if c["component_id"] not in assigned and c["execution_kind"] == "NATIVE_REFERENCE"
                 and c["stage"] == stage and c["execution_status"] == "EXECUTED"]
        if cards:
            sections.append((title, cards))
            assigned.update(card["technical"]["component_id"] for card in cards)

    # 4. Calibration and evidence checks (all scientific-check results, grouped)
    checks = [c for c in t["components"] if c["component_id"] not in assigned
              and c["execution_kind"] == "SCIENTIFIC_CHECK"]
    if checks:
        sections.append(("Calibration and evidence checks",
                         [component_card(c, refs.get(c["component_id"], "")) for c in checks]))
        assigned.update(c["component_id"] for c in checks)

    # 5. Components not run (blocked / optional / not-cleared / no-path / any remaining)
    not_run = [c for c in t["components"] if c["component_id"] not in assigned]
    sections.append(("Components not run",
                     [component_card(c, refs.get(c["component_id"], "")) for c in not_run]))
    assigned.update(c["component_id"] for c in not_run)

    # 6. Technical provenance (never a scientific claim)
    sections.append(("Technical provenance", [{
        "badge": "PROVENANCE", "headline": "How to reproduce and verify",
        "manifest_id": t["manifest_id"], "execution_context": t["execution_context"],
        "tour_scientific_hash": t["tour_scientific_hash"], "scenario": t["scenario"],
    }]))
    return sections


def assert_every_component_shown_once(tour) -> None:
    """Guard: every registered component appears in exactly one section card (never dropped, never twice)."""
    t = tour if isinstance(tour, dict) else tour.to_dict()
    shown = []
    for _, cards in tour_display_sections(t):
        for card in cards:
            cid = card.get("technical", {}).get("component_id")
            if cid:
                shown.append(cid)
    expected = {c["component_id"] for c in t["components"]}
    if sorted(shown) != sorted(expected) or len(shown) != len(set(shown)):
        raise AssertionError(f"display coverage mismatch: shown={sorted(shown)} expected={sorted(expected)}")
