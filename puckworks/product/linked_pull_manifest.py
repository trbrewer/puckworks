"""Frozen link graph for the Espresso Model Relay (illustrative_linked_pull_v1).

This manifest is the versioned, verifiable design of the relay: it classifies EVERY registered component
exactly once into a public station with an intended disposition, and declares the frozen directed link
graph (the hand-offs) the engine fills in with typed `LinkRecord`s at run time. A newly registered
component makes `verify_linked_pull_manifest()` fail until it is deliberately classified — the relay may
never silently ignore a model.

The complete relay is a PRODUCT-level orchestration artifact, NOT a new scientific component. It is never
registered in `puckworks.registry`, and its manifest id is not a tour manifest.
"""
from __future__ import annotations

import dataclasses

from .linked_pull_records import LinkKind, ScenarioRelationship, StageStatus

MANIFEST_ID = "illustrative_linked_pull_v1"

# ── stations (the public, ordered relay) ──────────────────────────────────────────────────
STATIONS = (
    ("recipe", "The recipe card", "What are we asking this collection of models to examine?"),
    ("grind", "From grinder dial to particle sizes",
     "How big are the coffee particles this pull is built from?"),
    ("packing", "Building an illustrative puck",
     "What kind of porous object will water be pushed through?"),
    ("machine", "What the machine delivers",
     "Before water reaches the coffee, what do the pump, pipe, and trapped air do?"),
    ("wetting", "Wetting the dry bed",
     "How long does it take to make the whole bed available to flowing water?"),
    ("flow", "The hydraulic flow bench",
     "Does more pressure translate directly into proportionally more flow?"),
    ("pore_scale", "Optional pore-scale relay",
     "What does uneven flow look like at the pore scale?"),
    ("extraction", "The baseline whole-shot extraction",
     "What does the baseline saturated extraction model predict for this recipe?"),
    ("puck_change", "Letting the puck change",
     "Once water and extraction begin, how might the puck's resistance change?"),
    ("heterogeneous", "Heterogeneous extraction branch",
     "What happens when the same average flow is divided unevenly between paths?"),
    ("multisolute", "Multi-solute extraction",
     "Can two shots with similar strength contain material released on different clocks?"),
    ("other_lenses", "Other extraction lenses",
     "What do the other extraction models see that the baseline does not?"),
    ("dashboard", "One pull, several readings",
     "What does this illustrative relay suggest about the final cup?"),
)
STATION_IDS = tuple(s[0] for s in STATIONS)


@dataclasses.dataclass(frozen=True)
class ComponentDisposition:
    component_id: str
    station_id: str
    role_kind: LinkKind           # how this component participates in the relay
    intended_status: StageStatus  # the disposition the engine aims for (may downgrade at run time)
    scenario_relationship: ScenarioRelationship
    role: str                     # one-line human description of its relay role


def _d(cid, station, kind, status, rel, role):
    return ComponentDisposition(cid, station, kind, status, rel, role)


_X = StageStatus
_K = LinkKind
_R = ScenarioRelationship

# EVERY registered component, classified exactly once (verified against the live registry).
COMPONENT_DISPOSITIONS: dict = {d.component_id: d for d in (
    # grind
    _d("wadsworth2026.grindmap", "grind", _K.ILLUSTRATIVE_ASSUMPTION, _X.EXECUTED_WITH_ASSUMPTIONS,
       _R.ADAPTED_SCENARIO, "Assumption-labelled physical-size bridge from Cameron's boulder radius."),
    # packing
    _d("wadsworth2026.permeability", "packing", _K.DOCUMENTED_ADAPTER, _X.EXECUTED_WITH_ASSUMPTIONS,
       _R.ADAPTED_SCENARIO, "Primary permeability prior from the matched physical radius."),
    _d("brewer2026.pack_generator", "packing", _K.DIRECT_MODEL_OUTPUT, _X.EXECUTED,
       _R.ADAPTED_SCENARIO, "Primary synthetic-geometry lens (deterministic Boolean-sphere pack)."),
    # machine
    _d("foster2025.machine_mode", "machine", _K.DIRECT_MODEL_OUTPUT, _X.EXECUTED_WITH_ASSUMPTIONS,
       _R.ADAPTED_SCENARIO, "Primary machine-delivery station (pressure nodes + flow)."),
    _d("sourcing2026.g3_pump_characteristic", "machine", _K.REFERENCE_CONSTRAINT, _X.REFERENCE_ONLY,
       _R.NATIVE_REFERENCE, "Pump-envelope reference constraint (not a runtime edge)."),
    # wetting
    _d("foster2025.infiltration", "wetting", _K.DOCUMENTED_ADAPTER, _X.EXECUTED_WITH_ASSUMPTIONS,
       _R.ADAPTED_SCENARIO, "Primary wetting hand-off (permeability + geometry + machine pressure)."),
    _d("sourcing2026.g1_glassbead_analog", "wetting", _K.REFERENCE_CONSTRAINT, _X.REFERENCE_ONLY,
       _R.NATIVE_REFERENCE, "Wetting-shape reference constraint (glass-bead analogy, not coffee)."),
    # flow
    _d("wadsworth2026.inertial", "flow", _K.DIAGNOSTIC_ONLY, _X.EXECUTED_WITH_ASSUMPTIONS,
       _R.ADAPTED_SCENARIO, "Primary flow-regime diagnostic (Darcy vs Forchheimer, Fo_F)."),
    _d("sourcing2026.g10_liquor_rheology", "flow", _K.REFERENCE_CONSTRAINT, _X.EXECUTED,
       _R.NATIVE_REFERENCE, "Liquid-property closure (viscosity/density) for the flow bench."),
    # optional pore-scale
    _d("brewer2026.lb_reference", "pore_scale", _K.OPTIONAL_SLOW_PATH, _X.OPTIONAL_DEPENDENCY_UNAVAILABLE,
       _R.ADAPTED_SCENARIO, "Optional slow pore-flow link (extended mode)."),
    _d("brewer2026.lb_taichi", "pore_scale", _K.OPTIONAL_SLOW_PATH, _X.OPTIONAL_DEPENDENCY_UNAVAILABLE,
       _R.NOT_EXECUTED, "Optional accelerator/capability path (Taichi; not required)."),
    # extraction baseline
    _d("cameron2020.extraction_bdf", "extraction", _K.DIRECT_MODEL_OUTPUT, _X.EXECUTED_WITH_ASSUMPTIONS,
       _R.ADAPTED_SCENARIO, "Baseline whole-shot saturated extraction station."),
    # puck change
    _d("waszkiewicz2025.poroelastic", "puck_change", _K.ILLUSTRATIVE_ASSUMPTION,
       _X.EXECUTED_WITH_ASSUMPTIONS, _R.ADAPTED_SCENARIO,
       "One-way linked bed-response branch (Cameron dissolved mass -> porosity/permeability)."),
    _d("brewer2026.coupled_kappa_t", "puck_change", _K.ALTERNATIVE_BRANCH, _X.EXECUTED_WITH_ASSUMPTIONS,
       _R.ADAPTED_SCENARIO, "Explicit stress-test composition branch (may show over-closure)."),
    _d("mo2023_2.swelling", "puck_change", _K.ALTERNATIVE_BRANCH, _X.EXECUTED_WITH_ASSUMPTIONS,
       _R.ADAPTED_SCENARIO, "Alternative swelling mechanism."),
    _d("fasano2000_partI.fines_migration", "puck_change", _K.ALTERNATIVE_BRANCH, _X.EXECUTED,
       _R.NATIVE_REFERENCE, "Alternative resistance mechanism (fines migration)."),
    _d("lee2023.feedback", "puck_change", _K.ALTERNATIVE_BRANCH, _X.REFERENCE_ONLY,
       _R.NATIVE_REFERENCE, "Guarded alternative feedback hypothesis (needs an unphysical region)."),
    # heterogeneous extraction
    _d("brewer2026.streamtube", "heterogeneous", _K.DIRECT_MODEL_OUTPUT, _X.EXECUTED,
       _R.SAME_SCENARIO, "Linked heterogeneous-extraction branch on the Cameron response."),
    # multi-solute
    _d("pannusch2024.solver", "multisolute", _K.DOCUMENTED_ADAPTER, _X.EXECUTED_WITH_ASSUMPTIONS,
       _R.ADAPTED_SCENARIO, "Secondary linked multi-solute extraction branch."),
    _d("pannusch2024.closures", "multisolute", _K.REFERENCE_CONSTRAINT, _X.EXECUTED,
       _R.NATIVE_REFERENCE, "Property and transport closures for the multi-solute branch."),
    # other lenses
    _d("romancorrochano2017.extraction", "other_lenses", _K.ALTERNATIVE_BRANCH, _X.EXECUTED,
       _R.ADAPTED_SCENARIO, "Molecular-size diffusion-clock lens (normalized release)."),
    _d("moroney2016.surrogate", "other_lenses", _K.ALTERNATIVE_BRANCH, _X.EXECUTED,
       _R.ADAPTED_SCENARIO, "Alternative reduced extraction-clock lens."),
    _d("mo2023_2.coupled_bed", "other_lenses", _K.ALTERNATIVE_BRANCH, _X.EXECUTED,
       _R.ADAPTED_SCENARIO, "Depth-resolved extraction lens."),
    _d("liang2021.desorption", "other_lenses", _K.DIAGNOSTIC_ONLY, _X.EXECUTED,
       _R.NATIVE_REFERENCE, "Equilibrium ceiling / retained-liquid observable context."),
    _d("grudeva2025.reduced", "other_lenses", _K.RIGHTS_BLOCKED, _X.RIGHTS_BLOCKED,
       _R.NOT_EXECUTED, "Rights-blocked (#73): shown in the map, ZERO execution and adapter calls."),
)}


@dataclasses.dataclass(frozen=True)
class EdgeSpec:
    edge_id: str
    source_component_id: str | None    # None => the recipe card
    source_field: str
    target_component_id: str
    target_field: str
    kind: LinkKind
    adapter_id: str | None
    assumption_ids: tuple[str, ...]
    optional: bool = False             # extended-mode-only


def _e(eid, src, sf, tgt, tf, kind, adapter=None, assumptions=(), optional=False):
    return EdgeSpec(eid, src, sf, tgt, tf, kind, adapter, assumptions, optional)


# The frozen directed link graph — the hand-offs the chain map draws and the engine fills with typed
# LinkRecords. Edges never touch grudeva2025.reduced. This is the intended topology; a component executed
# without an incoming edge is a shared-recipe lens, not a linked hand-off.
LINK_EDGES: tuple = (
    _e("recipe_to_cameron", None, "grind_setting", "cameron2020.extraction_bdf", "grind_setting",
       _K.SHARED_INPUT_ONLY),
    _e("cameron_radius_to_grindmap", "cameron2020.extraction_bdf", "boulder_radius_m",
       "wadsworth2026.grindmap", "physical_radius_m", _K.ILLUSTRATIVE_ASSUMPTION,
       adapter="radius_match", assumptions=("A01",)),
    _e("grindmap_to_permeability", "wadsworth2026.grindmap", "physical_radius_m",
       "wadsworth2026.permeability", "radius_m", _K.DOCUMENTED_ADAPTER, adapter="radius_to_permeability"),
    _e("grindmap_to_pack", "wadsworth2026.grindmap", "physical_radius_m",
       "brewer2026.pack_generator", "radius_m", _K.DOCUMENTED_ADAPTER, adapter="radius_to_pack",
       assumptions=("A03",)),
    _e("permeability_to_infiltration", "wadsworth2026.permeability", "k_m2",
       "foster2025.infiltration", "k_m2", _K.DOCUMENTED_ADAPTER, adapter="si_permeability_guard",
       assumptions=("A02", "A05")),
    _e("permeability_to_inertial", "wadsworth2026.permeability", "k_m2",
       "wadsworth2026.inertial", "k_m2", _K.DIRECT_MODEL_OUTPUT),
    _e("machine_to_infiltration", "foster2025.machine_mode", "p_h",
       "foster2025.infiltration", "p_top_of_bed", _K.DOCUMENTED_ADAPTER, adapter="pressure_node_top",
       assumptions=("A04",)),
    _e("machine_to_inertial", "foster2025.machine_mode", "dP_bed",
       "wadsworth2026.inertial", "dP_bed", _K.DOCUMENTED_ADAPTER, adapter="pressure_node_drop"),
    _e("rheology_to_inertial", "sourcing2026.g10_liquor_rheology", "viscosity_pa_s",
       "wadsworth2026.inertial", "viscosity_pa_s", _K.REFERENCE_CONSTRAINT, assumptions=("A07",)),
    _e("recipe_to_extraction", None, "dose_g", "cameron2020.extraction_bdf", "dose_g",
       _K.SHARED_INPUT_ONLY),
    _e("machine_to_extraction", "foster2025.machine_mode", "P_of_t",
       "cameron2020.extraction_bdf", "pressure_bar", _K.DOCUMENTED_ADAPTER,
       adapter="representative_pressure", assumptions=("A06",)),
    _e("cameron_to_waszkiewicz", "cameron2020.extraction_bdf", "dissolved_mass_g",
       "waszkiewicz2025.poroelastic", "dissolution_fraction", _K.ILLUSTRATIVE_ASSUMPTION,
       adapter="dissolution_fraction", assumptions=("A09",)),
    _e("cameron_to_streamtube", "cameron2020.extraction_bdf", "response",
       "brewer2026.streamtube", "response", _K.DIRECT_MODEL_OUTPUT),
    _e("machine_to_pannusch", "foster2025.machine_mode", "Q_of_t",
       "pannusch2024.solver", "flow_trace", _K.DOCUMENTED_ADAPTER, adapter="representative_flow",
       assumptions=("A11", "A12")),
    # extended-mode-only pore-scale relay
    _e("pack_to_lb", "brewer2026.pack_generator", "solid_mask", "brewer2026.lb_reference", "solid_mask",
       _K.OPTIONAL_SLOW_PATH, adapter="lb_solid_mask", assumptions=("A03",), optional=True),
    _e("lb_to_streamtube", "brewer2026.lb_reference", "sigma_micro", "brewer2026.streamtube", "sigma",
       _K.OPTIONAL_SLOW_PATH, adapter="lb_sigma", assumptions=("A10",), optional=True),
)


def verify_linked_pull_manifest() -> list:
    """Empty list == a clean manifest. Fails when a registered component is unclassified, an unknown
    component is classified, an edge references an unknown component, the graph has a cycle, or any edge
    touches the rights-blocked component."""
    from puckworks import registry
    errs = []
    live = {c.name for c in registry.components()}
    classified = set(COMPONENT_DISPOSITIONS)
    for cid in sorted(live - classified):
        errs.append(f"unclassified component (relay manifest must cover it): {cid}")
    for cid in sorted(classified - live):
        errs.append(f"manifest classifies an unknown component: {cid}")
    for d in COMPONENT_DISPOSITIONS.values():
        if d.station_id not in STATION_IDS:
            errs.append(f"{d.component_id}: unknown station {d.station_id}")
    # edges reference known components (source None == recipe) and never touch grudeva
    blocked = {cid for cid, d in COMPONENT_DISPOSITIONS.items() if d.role_kind == LinkKind.RIGHTS_BLOCKED}
    for e in LINK_EDGES:
        for who in (e.source_component_id, e.target_component_id):
            if who is not None and who not in classified:
                errs.append(f"edge {e.edge_id}: unknown component {who}")
        if e.source_component_id in blocked or e.target_component_id in blocked:
            errs.append(f"edge {e.edge_id}: touches rights-blocked component (must have zero edges)")
    errs.extend(_acyclicity_errors())
    return errs


def _acyclicity_errors() -> list:
    """Kahn's algorithm over component->component edges (recipe source is a root)."""
    nodes = set(COMPONENT_DISPOSITIONS)
    adj = {n: [] for n in nodes}
    indeg = {n: 0 for n in nodes}
    for e in LINK_EDGES:
        if e.source_component_id is None:
            continue
        adj[e.source_component_id].append(e.target_component_id)
        indeg[e.target_component_id] += 1
    queue = [n for n in nodes if indeg[n] == 0]
    seen = 0
    while queue:
        n = queue.pop()
        seen += 1
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)
    return [] if seen == len(nodes) else ["link graph is not acyclic (a cycle exists)"]


def edges_for_mode(mode: str) -> tuple:
    """Edges active in a given mode ('fast' omits OPTIONAL_SLOW_PATH edges)."""
    if mode == "extended":
        return LINK_EDGES
    return tuple(e for e in LINK_EDGES if not e.optional)


def dispositions_by_station() -> dict:
    out = {sid: [] for sid in STATION_IDS}
    for d in COMPONENT_DISPOSITIONS.values():
        out[d.station_id].append(d)
    return out
