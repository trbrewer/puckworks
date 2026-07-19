"""Orthogonal quantity semantics + separated readiness axes (PV-19B Phase 5, #70).

The old `reference_basis.QUANTITY_BASES` conflated several independent concepts (a true reference
denominator, spatial discretization, species cardinality, phase, and a relative-trend output class). This
module makes each axis independent via `QuantityDefinition`, and separates the two decisions that were
previously entangled:

1. **Shared-scenario execution readiness** — can the ONE bounded scenario honestly supply every input a
   model needs? (A model can be a common-scenario lens showing its native outputs in a separate panel
   without ever converting to Cameron's EY/TDS.)
2. **Output comparability** — for a pair of outputs, may they be directly overlaid, compared only after a
   validated conversion, faceted separately, shown reference-only, or never compared?

A plot **compatibility signature** decides when two series may share an ordinary axis or have a
difference/ratio computed. Nothing here executes a model or invents a conversion.
"""
from __future__ import annotations

import dataclasses

# ── independent axes (each finite; NONE is a denominator except `reference_basis`) ──
# true reference denominators only — per-species / flow-trend / profile are NOT denominators
REFERENCE_BASES = (
    "packed_bed_volume", "pore_liquid_volume", "mobile_liquid_volume", "grain_external_volume",
    "grain_total_volume", "dry_coffee_mass", "beverage_mass", "beverage_volume", "local_cell_volume",
    "dimensionless", "not_applicable",
)
PHASES = ("solid", "pore_liquid", "mobile_liquid", "cup_outlet", "whole_bed", "not_applicable")
SPECIES_SCOPES = ("single_soluble_pool", "named_species", "species_vector", "total_solute",
                  "not_applicable")
SPATIAL_SUPPORTS = ("global", "bed_cell", "depth_profile", "outlet", "cup")
TEMPORAL_SUPPORTS = ("instantaneous", "cumulative", "final", "steady_state")
AGGREGATIONS = ("absolute", "mean", "sum", "relative_trend", "normalized_ratio")

EXECUTION_READINESS_STATES = (
    "READY_FOR_SHARED_SCENARIO", "INPUT_ADAPTER_REQUIRED", "OUTSIDE_SHARED_DOMAIN",
    "RIGHTS_BLOCKED", "RIGHTS_REVIEW_REQUIRED", "RUNTIME_BLOCKED", "INSUFFICIENT_PROVENANCE",
)
COMPARABILITY_STATES = (
    "DIRECTLY_OVERLAID", "COMPARED_AFTER_VALIDATED_CONVERSION", "FACETED_SEPARATELY",
    "REFERENCE_ONLY", "NOT_COMPARABLE", "UNSUPPORTED",
)


@dataclasses.dataclass(frozen=True)
class QuantityDefinition:
    quantity_id: str
    numerator: str                   # the physical quantity in the numerator
    reference_basis: str             # the denominator / reference volume|mass (REFERENCE_BASES)
    phase: str
    species_scope: str
    spatial_support: str
    temporal_support: str
    aggregation: str
    unit: str
    semantic_role: str
    observable_definition: str
    evidence_note: str = ""

    def __post_init__(self):
        for field, vocab in (("reference_basis", REFERENCE_BASES), ("phase", PHASES),
                             ("species_scope", SPECIES_SCOPES), ("spatial_support", SPATIAL_SUPPORTS),
                             ("temporal_support", TEMPORAL_SUPPORTS), ("aggregation", AGGREGATIONS)):
            v = getattr(self, field)
            if v not in vocab:
                raise ValueError(f"{self.quantity_id}: {field}={v!r} not in the finite vocabulary")

    def signature(self) -> tuple:
        """The plot-compatibility signature: two series may share an ordinary axis (or have a
        difference/ratio computed) ONLY when their signatures match."""
        return (self.reference_basis, self.unit, self.phase, self.species_scope,
                self.spatial_support, self.temporal_support, self.aggregation)


def may_share_axis(a: QuantityDefinition, b: QuantityDefinition) -> bool:
    """Two quantities may share one ordinary axis only when their full semantic signatures match — same
    unit is necessary but NOT sufficient (a different reference basis, phase, or species scope forbids it).
    A relative trend is never overlaid with an absolute quantity."""
    if "relative_trend" in (a.aggregation, b.aggregation) and a.aggregation != b.aggregation:
        return False
    return a.signature() == b.signature()


def output_comparability(a: QuantityDefinition, b: QuantityDefinition,
                         *, validated_conversion_registered: bool = False) -> str:
    """The comparability verdict for a pair of outputs. Fail-closed: without a validated conversion,
    incompatible signatures are FACETED_SEPARATELY (or NOT_COMPARABLE for a relative trend vs absolute),
    never silently overlaid."""
    if a.aggregation == "relative_trend" or b.aggregation == "relative_trend":
        return "REFERENCE_ONLY" if a.aggregation == b.aggregation else "NOT_COMPARABLE"
    if may_share_axis(a, b):
        return "DIRECTLY_OVERLAID"
    if validated_conversion_registered:
        return "COMPARED_AFTER_VALIDATED_CONVERSION"
    return "FACETED_SEPARATELY"


# ── the Cameron common-scenario output + the candidates' native outputs (typed) ────
CAMERON_EY = QuantityDefinition(
    quantity_id="cameron.extraction_yield", numerator="dissolved_solute_mass",
    reference_basis="dry_coffee_mass", phase="cup_outlet", species_scope="single_soluble_pool",
    spatial_support="cup", temporal_support="cumulative", aggregation="absolute", unit="%",
    semantic_role="simulated", observable_definition="cumulative extraction yield (single pool)")

# native output definitions per second-lens candidate (typed; used for the comparability re-audit)
_CANDIDATE_OUTPUT: dict[str, QuantityDefinition] = {
    "mo2023_2.coupled_bed": QuantityDefinition(
        quantity_id="mo.cell_concentration", numerator="solute_concentration",
        reference_basis="local_cell_volume", phase="pore_liquid", species_scope="total_solute",
        spatial_support="bed_cell", temporal_support="instantaneous", aggregation="absolute",
        unit="kg/m^3", semantic_role="simulated",
        observable_definition="bed-depth-resolved pore-liquid concentration"),
    "pannusch2024.solver": QuantityDefinition(
        quantity_id="pannusch.species_concentration", numerator="species_concentration",
        reference_basis="mobile_liquid_volume", phase="mobile_liquid", species_scope="named_species",
        spatial_support="outlet", temporal_support="cumulative", aggregation="absolute",
        unit="kg/m^3", semantic_role="simulated",
        observable_definition="per-species outlet concentrations (caffeine/trigonelline/CGA)"),
    "romancorrochano2017.extraction": QuantityDefinition(
        quantity_id="romancorrochano.extraction_trend", numerator="relative_extraction",
        reference_basis="dimensionless", phase="cup_outlet", species_scope="total_solute",
        spatial_support="cup", temporal_support="cumulative", aggregation="relative_trend",
        unit="-", semantic_role="derived",
        observable_definition="relative extraction TREND (not an absolute EY/TDS)"),
}


def candidate_output(component_id: str) -> QuantityDefinition | None:
    return _CANDIDATE_OUTPUT.get(component_id)


# ── shared-scenario execution readiness (distinct from comparability) ──────────────
# per-candidate execution assessment against the ONE bounded scenario (facts from cards/registry)
_EXECUTION: dict[str, dict] = {
    "mo2023_2.coupled_bed": {
        "state": "INPUT_ADAPTER_REQUIRED",
        "missing_inputs": ["cell measures + cup/outlet boundary must be defined before integrating "
                           "inventory"],
        "grinder": "fine/coarse families; NO dial->size mapping invented",
        "reason": "shared inputs can map, but a bed-cell -> cup boundary is required before execution"},
    "pannusch2024.solver": {
        "state": "INPUT_ADAPTER_REQUIRED",
        "missing_inputs": ["a named source for every per-species initial concentration",
                           "an EK43-dial -> particle mapping is NOT available (do not invent one)"],
        "grinder": "center-grind (EK43 1.7) assumption; NO portable dial->size mapping",
        "reason": "per-species inputs need named sources before the shared scenario can drive it"},
    "romancorrochano2017.extraction": {
        "state": "READY_FOR_SHARED_SCENARIO",
        "missing_inputs": [],
        "grinder": "grain-scale microstructural diffusion; NO dial mapping",
        "reason": "can run on the shared scenario as a supporting TREND lens in a separate panel"},
    "grudeva2025.reduced": {
        "state": "RIGHTS_BLOCKED",
        "missing_inputs": [],
        "grinder": "n/a",
        "reason": "code rights blocked (#73); excluded from lens consideration entirely"},
}


def shared_scenario_execution_readiness(component_id: str) -> dict:
    """Can the ONE bounded scenario honestly supply this model's inputs? Rights-blocked short-circuits;
    otherwise the recorded assessment governs. This is independent of output comparability."""
    from puckworks import rights
    if rights.is_code_rights_blocked(component_id):
        return {"component_id": component_id, "execution_readiness": "RIGHTS_BLOCKED",
                "missing_inputs": [], "grinder": "n/a", "reason": "code rights blocked (#73)"}
    a = _EXECUTION.get(component_id)
    if a is None:
        return {"component_id": component_id, "execution_readiness": "INSUFFICIENT_PROVENANCE",
                "missing_inputs": ["no execution assessment on record"], "grinder": "unknown",
                "reason": "treat conservatively"}
    return {"component_id": component_id, "execution_readiness": a["state"],
            "missing_inputs": a["missing_inputs"], "grinder": a["grinder"], "reason": a["reason"]}


def candidate_comparability(component_id: str) -> str:
    """Comparability of a candidate's native output against Cameron's EY (fail-closed; no validated
    cross-quantity conversion is registered)."""
    q = candidate_output(component_id)
    if q is None:
        return "UNSUPPORTED"
    return output_comparability(CAMERON_EY, q, validated_conversion_registered=False)


# ── measurement / evidence agenda (turns a blocker into a concrete acquisition plan) ──
def measurement_agenda() -> list:
    """One structured action record per execution blocker: what to acquire, the acceptance calculation,
    and the test it would enable. Nothing here authorizes execution."""
    agenda = []
    for cid, a in sorted(_EXECUTION.items()):
        if a["state"] in ("READY_FOR_SHARED_SCENARIO", "RIGHTS_BLOCKED"):
            continue
        for i, miss in enumerate(a["missing_inputs"]):
            agenda.append({
                "blocker_id": f"{cid}#{i}", "component": cid, "missing_quantity": miss,
                "required_source": "a named published source or a measured dataset for this input",
                "acceptance": "the input maps to a shared-scenario quantity with matching units + a "
                              "documented provenance; no invented grinder/inventory mapping",
                "enables_test": f"a shared-scenario execution readiness test for {cid}",
                "issue": "#70", "status": "OPEN", "evidence_ceiling": "input-mapping only until acquired"})
    return agenda


def roman_corrochano_lens_readiness() -> dict:
    """Deterministic readiness record for adding romancorrochano2017.extraction as a SECOND common-scenario
    lens (a separate-panel relative-trend lens — never converted to Cameron EY/TDS). The adapter is
    DEFERRED because the affirmative rights review its public use requires was not completed: its code and
    output rights remain NOT_REVIEWED (see docs/rights_review_notes.md). No adapter is implemented; no
    cross-model arithmetic exists. This record links the blocker to the campaign that would validate it."""
    from puckworks import rights
    cid = "romancorrochano2017.extraction"
    exe = shared_scenario_execution_readiness(cid)
    rec = rights.rights_record(cid)
    public_exec = rights.may_execute_in_public_batch(cid)
    publish = rights.may_publish_outputs(cid)
    return {
        "component_id": cid,
        "execution_readiness": exe["execution_readiness"],       # READY_FOR_SHARED_SCENARIO
        "missing_inputs": exe["missing_inputs"],                 # none; no grinder-dial mapping needed
        "output_comparability_vs_cameron_ey": candidate_comparability(cid),   # NOT_COMPARABLE (trend)
        "presentation": "separate panel; relative trend only; no difference/ratio/ranking vs Cameron",
        "code_rights_state": rec.code_rights_state,
        "output_redistribution_state": rec.output_redistribution_state,
        "public_execution_cleared": public_exec.allowed,         # False (NOT_REVIEWED)
        "output_publication_cleared": publish.allowed,           # False (NOT_REVIEWED)
        "adapter_status": "DEFERRED_PENDING_RIGHTS_REVIEW",
        "blocker": "affirmative rights review (code execution + output redistribution) not completed; "
                   "public use is blocked by the rights preflight",
        "validation_campaign": "EXP-006",
        "no_adapter_implemented": True,
    }


def build_report() -> dict:
    """The re-audit: for every candidate, the TWO independent decisions + the measurement agenda."""
    import puckworks
    candidates = sorted(c.name for c in puckworks.components()
                        if c.stage == "extraction" and c.execution_role == "runtime"
                        and c.name != "cameron2020.extraction_bdf")
    rows = []
    for cid in candidates:
        exe = shared_scenario_execution_readiness(cid)
        q = candidate_output(cid)
        rows.append({
            "component_id": cid,
            "execution_readiness": exe["execution_readiness"],
            "missing_inputs": exe["missing_inputs"], "grinder": exe["grinder"],
            "native_output": None if q is None else q.observable_definition,
            "native_output_signature": None if q is None else list(q.signature()),
            "comparability_vs_cameron_ey": candidate_comparability(cid),
            "reason": exe["reason"]})
    executed_as_lens = [r["component_id"] for r in rows
                        if r["execution_readiness"] == "READY_FOR_SHARED_SCENARIO"]
    directly_comparable = [r["component_id"] for r in rows
                           if r["comparability_vs_cameron_ey"] == "DIRECTLY_OVERLAID"]
    return {
        "report": "puckworks-lab-quantity-semantics-readiness",
        "common_scenario_lens": "cameron2020.extraction_bdf",
        "cameron_ey_signature": list(CAMERON_EY.signature()),
        "reference_bases": list(REFERENCE_BASES),
        "candidates": rows,
        "shared_scenario_executable_as_separate_panel_lens": executed_as_lens,
        "directly_comparable_to_cameron_ey": directly_comparable,
        "measurement_agenda": measurement_agenda(),
        "conclusion": ("Shared-scenario EXECUTION and output COMPARABILITY are separate: a candidate can "
                       "run on the shared scenario and show its native outputs in a SEPARATE panel "
                       "without converting to Cameron EY/TDS. No candidate's native output is directly "
                       "comparable to Cameron EY (different reference basis / species scope / a relative "
                       "trend), and no validated cross-quantity conversion is registered — so no direct "
                       "overlay is offered. A model does NOT need an EY/TDS conversion merely to execute."),
        "boundaries": ["shared-scenario execution does not imply output comparability",
                       "same unit is necessary but not sufficient to share an axis",
                       "a relative trend is never overlaid with an absolute EY/TDS",
                       "no invented grinder-dial or inventory conversion", "model agreement is not validation"],
    }


def canonical_json(report: dict) -> str:
    import json
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv=None) -> int:
    import argparse
    import sys
    ap = argparse.ArgumentParser(prog="puckworks.product.quantity_semantics", description=__doc__)
    ap.add_argument("--format", choices=["json"], default="json")
    ap.parse_args(argv)
    sys.stdout.write(canonical_json(build_report()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
