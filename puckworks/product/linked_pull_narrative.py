"""Structured novice narrative for each relay station — built FROM computed stage results, never
hand-written numbers. Mirrors the Full Laboratory Tour's calm, labelled-section teaching style, but adds
the relay-specific "what enters / what is handed forward / what we assumed" so every hand-off is legible.

No taste translation: cup implications stay physical and conditional (more/less concentrated, more/less
soluble recovered, shorter/longer contact time, different release timing, stronger hydraulic resistance).
"""
from __future__ import annotations

import dataclasses

from . import linked_pull_adapters as AD
from . import linked_pull_manifest as MAN


def format_value(v) -> str:
    """Compact display of a linked value (number, bool, string, or short list)."""
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        if v == 0:
            return "0"
        av = abs(v)
        if av < 1e-3 or av >= 1e5:
            return f"{v:.2e}"
        return f"{v:g}"
    if isinstance(v, (list, tuple)):
        return f"[{len(v)} values]"
    return str(v)


@dataclasses.dataclass(frozen=True)
class LinkedStageNarrative:
    public_heading: str
    question: str
    what_enters: tuple            # tuple[str, ...]
    what_it_calculates: str
    what_the_model_shows: str
    what_is_handed_forward: str
    assumptions: tuple            # tuple[str, ...]
    why_it_happens: str
    why_it_is_interesting: str
    possible_cup_implication: str
    scope: str


# per-component physical explanations (mechanism + cup implication), kept physical and conditional
_PHYSICS = {
    "wadsworth2026.grindmap": (
        "Smaller particle scales pack more tightly and add surface area at the same time.",
        "Finer grinds can raise both extraction and resistance, so 'finer' is not automatically stronger."),
    "wadsworth2026.permeability": (
        "Permeability falls as grains get smaller and packing tightens.",
        "Lower permeability means more hydraulic resistance for the machine to overcome."),
    "brewer2026.pack_generator": (
        "A looser region offers an easier path than a tight one.",
        "Structural unevenness gives some paths a chance to carry much more water than others."),
    "foster2025.machine_mode": (
        "The pump, pipe, and trapped air shape pressure and flow before the coffee sees them.",
        "A dip or ramp in flow can come from the machine itself, not the puck."),
    "foster2025.infiltration": (
        "Early flow rushes into dry, empty pore space, sweeping a front down the bed.",
        "Less fully-wetted time can raise the risk that regions contribute unequally."),
    "wadsworth2026.inertial": (
        "At high flow, inertia adds resistance beyond linear Darcy drag.",
        "More pressure need not give proportionally more flow; contact time may not shorten as expected."),
    "sourcing2026.g10_liquor_rheology": (
        "Dilute coffee liquor is only slightly more viscous than water.",
        "Bulk viscosity barely changes flow resistance for a normal shot."),
    "cameron2020.extraction_bdf": (
        "Reaching the target cup mass fixes how long the bed extracts.",
        "TDS is concentration and EY is recovered soluble mass — neither is flavour."),
    "waszkiewicz2025.poroelastic": (
        "As solids dissolve, the model lets the bed's porosity and permeability respond.",
        "Changing flow can follow extraction, but this branch is a new, unvalidated coupling."),
    "brewer2026.coupled_kappa_t": (
        "Swelling, compaction, and extraction each change pore space; combined they can over-close it.",
        "A single flow curve does not uniquely identify which mechanism caused it."),
    "mo2023_2.swelling": (
        "Water entering particles swells them and shrinks the pore space.",
        "Swelling alone can lower flow over the shot."),
    "fasano2000_partI.fines_migration": (
        "Mobile fines can pack into a tighter, more resistant layer.",
        "Falling flow has several possible causes; one trace does not prove which."),
    "brewer2026.streamtube": (
        "Fast paths exhaust nearby solubles while slow paths contribute little.",
        "Uneven flow can lower the puck-wide extraction recovered in the cup."),
    "pannusch2024.closures": (
        "Bigger molecules diffuse out of grains more slowly than small ones.",
        "Compounds released on different clocks can give similar total strength with different make-up."),
    "pannusch2024.solver": (
        "Release timing depends on diffusion and flow, not just total amount.",
        "Equal TDS need not mean identical composition."),
    "romancorrochano2017.extraction": (
        "Diffusion out of spherical grains is faster for smaller molecules.",
        "The mix in the cup shifts over the shot even at fixed strength."),
    "moroney2016.surrogate": (
        "Extraction shows an early release, a plateau, then wash-through.",
        "The clock of release matters as much as the endpoint."),
    "mo2023_2.coupled_bed": (
        "Extraction resolved by bed depth shows the front filling and eluting.",
        "Depth structure can leave parts of the bed under-extracted."),
    "liang2021.desorption": (
        "At equilibrium the bed and liquid share solubles at a fixed ratio.",
        "The equilibrium ceiling is different bookkeeping from a flowing-shot yield."),
    "lee2023.feedback": (
        "Extraction changing porosity can redistribute water between paths.",
        "This particular decline needs an unphysical density, so it is a guarded hypothesis."),
    "grudeva2025.reduced": (
        "A reduced whole-shot extraction model with a moving front.",
        "Rights-blocked here, so it contributes nothing to this pull."),
}


def _station(station_id):
    return next(s for s in MAN.STATIONS if s[0] == station_id)


def _humanize_value(v) -> str:
    unit = f" {v.unit}" if v.unit else ""
    return f"{v.name.replace('_', ' ')} = {format_value(v.value)}{unit} [{v.origin.value.lower()}]"


def stage_narrative(stage) -> LinkedStageNarrative:
    st = _station(stage.station_id)
    mech, cup = _PHYSICS.get(stage.component_id, ("", ""))
    enters = tuple(_humanize_value(v) for v in stage.inputs) or ("the shared recipe scenario",)
    handed = ", ".join(v.name.replace("_", " ") for v in stage.outputs) or "a diagnostic read-out"
    shows = " ".join(stage.domain_findings) or (stage.message or "See the technical details.")
    assumptions = tuple(
        f"{aid}: {AD.ASSUMPTIONS[aid].statement}" for aid in stage.assumption_ids if aid in AD.ASSUMPTIONS)
    interesting = _interesting(stage)
    scope = _scope(stage)
    return LinkedStageNarrative(
        public_heading=st[1], question=st[2], what_enters=enters,
        what_it_calculates=mech or "This station reports a model output for the shared pull.",
        what_the_model_shows=shows, what_is_handed_forward=f"This station hands forward: {handed}.",
        assumptions=assumptions, why_it_happens=mech,
        why_it_is_interesting=interesting, possible_cup_implication=cup, scope=scope)


def _interesting(stage) -> str:
    st = stage.status.value
    if st == "RIGHTS_BLOCKED":
        return "It is shown in the chain map but never run — a rights boundary, not a scientific gap."
    if st == "DOMAIN_REJECTED":
        return "The entered scenario fell outside this model's card domain, so the relay declined it."
    if stage.assumption_ids:
        return ("This reading rests on an explicit assumed hand-off — the kind of bridge the relay exists "
                "to make visible.")
    return "It offers an independent reading of the same pull, not a vote to be averaged."


def _scope(stage) -> str:
    base = {
        "RIGHTS_BLOCKED": "Rights-blocked: zero execution; contributes no numbers to this pull.",
        "REFERENCE_ONLY": "A reference/native case only — not adapted to your entered scenario.",
        "OPTIONAL_DEPENDENCY_UNAVAILABLE": "An optional path skipped in this mode.",
        "DOMAIN_REJECTED": "Outside the model's carded domain for this scenario.",
        "EXECUTION_ERROR": "This station errored; it is reported as an error, never as a result.",
        "NOT_SELECTED": "Not selected for this pull.",
        "NOT_EXECUTED": "Not executed.",
    }.get(stage.status.value)
    if base:
        return base
    tail = " It rests on named assumptions." if stage.assumption_ids else ""
    return ("An illustrative model reading of the shared pull — not a validated coupled result and not a "
            "flavour prediction." + tail)
