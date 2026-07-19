"""Explicit Guided Pull Laboratory component catalog (PV-19B Phase 3, #70).

One authoritative capability record per registered component. The common-scenario **disposition** and
**adapter capability** are stated EXPLICITLY here — never inferred from a broad `stage`/`kind`/`role`
substring heuristic. Registry-derived fields (module, stage, role, evidence, provenance, gate ids,
validity range) are declared and validated against `puckworks.components()`; runner/adapter capability,
rights, and quantity basis are consumed from their authoritative sources (`lab_runners`, `lab.ADAPTERS`,
`puckworks.rights`, `reference_basis`). CI requires the committed catalog to cover every registered
component; a missing entry, an unknown gate id, an unresolved runner/adapter id, or a rights mismatch
fails validation.
"""
from __future__ import annotations

import dataclasses

# explicit common-scenario disposition + adapter capability per component (the anti-heuristic core).
# disposition ∈ lab.DISPOSITIONS; adapter capability ∈ lab.ADAPTER_CAPABILITIES.
_CAPABILITY: dict[str, dict] = {
    # the one executable common-scenario lens
    "cameron2020.extraction_bdf": {"disposition": "COMMON_SCENARIO_READY",
                                   "adapter_capability": "COMMON_SCENARIO_READY"},
    # extraction runtime models that need a tested inventory/basis adapter before any overlay
    "mo2023_2.coupled_bed": {"disposition": "ADAPTER_REQUIRED", "adapter_capability": "ADAPTER_REQUIRED"},
    "pannusch2024.solver": {"disposition": "ADAPTER_REQUIRED", "adapter_capability": "ADAPTER_REQUIRED"},
    "romancorrochano2017.extraction": {"disposition": "ADAPTER_REQUIRED",
                                       "adapter_capability": "ADAPTER_REQUIRED"},
    # rights-blocked extraction model (#73)
    "grudeva2025.reduced": {"disposition": "RIGHTS_BLOCKED", "adapter_capability": "RIGHTS_BLOCKED"},
    # executable components with a native reference runner (not a common-scenario adapter)
    "foster2025.infiltration": {"disposition": "NATIVE_REFERENCE_ONLY",
                                "adapter_capability": "NOT_APPLICABLE"},
    "wadsworth2026.permeability": {"disposition": "NATIVE_REFERENCE_ONLY",
                                   "adapter_capability": "NOT_APPLICABLE"},
    "waszkiewicz2025.poroelastic": {"disposition": "NATIVE_REFERENCE_ONLY",
                                    "adapter_capability": "NOT_APPLICABLE"},
    "brewer2026.coupled_kappa_t": {"disposition": "NATIVE_REFERENCE_ONLY",
                                   "adapter_capability": "NOT_APPLICABLE"},
    # runtime supporting-stage lenses (non-extraction physics; an adapter would be required to overlay)
    "brewer2026.streamtube": {"disposition": "SUPPORTING_STAGE_LENS",
                              "adapter_capability": "ADAPTER_REQUIRED"},
    "foster2025.machine_mode": {"disposition": "SUPPORTING_STAGE_LENS",
                                "adapter_capability": "ADAPTER_REQUIRED"},
    "mo2023_2.swelling": {"disposition": "SUPPORTING_STAGE_LENS",
                          "adapter_capability": "ADAPTER_REQUIRED"},
    "wadsworth2026.inertial": {"disposition": "SUPPORTING_STAGE_LENS",
                               "adapter_capability": "ADAPTER_REQUIRED"},
    # calibration/closure components (not independent shot models)
    "brewer2026.lb_reference": {"disposition": "CALIBRATION_OR_CLOSURE",
                                "adapter_capability": "NOT_APPLICABLE"},
    "brewer2026.lb_taichi": {"disposition": "CALIBRATION_OR_CLOSURE",
                             "adapter_capability": "NOT_APPLICABLE"},
    "brewer2026.pack_generator": {"disposition": "CALIBRATION_OR_CLOSURE",
                                  "adapter_capability": "NOT_APPLICABLE"},
    "fasano2000_partI.fines_migration": {"disposition": "CALIBRATION_OR_CLOSURE",
                                         "adapter_capability": "NOT_APPLICABLE"},
    "lee2023.feedback": {"disposition": "CALIBRATION_OR_CLOSURE", "adapter_capability": "NOT_APPLICABLE"},
    "liang2021.desorption": {"disposition": "CALIBRATION_OR_CLOSURE",
                             "adapter_capability": "NOT_APPLICABLE"},
    "moroney2016.surrogate": {"disposition": "CALIBRATION_OR_CLOSURE",
                              "adapter_capability": "NOT_APPLICABLE"},
    "pannusch2024.closures": {"disposition": "CALIBRATION_OR_CLOSURE",
                              "adapter_capability": "NOT_APPLICABLE"},
    "sourcing2026.g10_liquor_rheology": {"disposition": "CALIBRATION_OR_CLOSURE",
                                         "adapter_capability": "NOT_APPLICABLE"},
    "sourcing2026.g1_glassbead_analog": {"disposition": "CALIBRATION_OR_CLOSURE",
                                         "adapter_capability": "NOT_APPLICABLE"},
    "sourcing2026.g3_pump_characteristic": {"disposition": "CALIBRATION_OR_CLOSURE",
                                            "adapter_capability": "NOT_APPLICABLE"},
    "wadsworth2026.grindmap": {"disposition": "CALIBRATION_OR_CLOSURE",
                               "adapter_capability": "NOT_APPLICABLE"},
}

# an optional-dependency-gated component: its runner capability degrades in an env missing the dependency.
_OPTIONAL_DEPENDENCY = {"brewer2026.lb_taichi": "taichi"}


@dataclasses.dataclass(frozen=True)
class CatalogEntry:
    component_id: str
    module: str
    card_path: str
    doi: str
    stage: str
    execution_role: str
    kind: str
    is_runtime_stage: bool
    is_calibration_or_closure: bool
    has_callable_code: bool
    native_runner_id: str | None
    common_scenario_adapter_id: str | None
    gate_ids: tuple
    evidence_strength: str
    provenance_class: str
    validity_range: object
    optional_dependency: str | None
    quantity_basis: str
    code_rights_state: str
    data_rights_state: str
    output_redistribution_state: str
    public_execution_eligible: bool
    output_publication_eligible: bool
    disposition: str
    adapter_capability: str
    metadata_review_date: str

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["gate_ids"] = list(self.gate_ids)
        return d


def _gate_ids(component) -> tuple:
    return tuple(getattr(g, "__name__", str(g)) for g in getattr(component, "gates", ()))


def catalog_entry(component) -> CatalogEntry:
    """Build one authoritative catalog entry from the registry + authoritative capability sources +
    the explicit disposition/adapter decision. Raises if the component has no explicit capability entry
    (no silent heuristic fallback)."""
    from puckworks import rights
    from puckworks.product import lab, lab_runners
    from puckworks.product import reference_basis as rb
    name = component.name
    if name not in _CAPABILITY:
        raise KeyError(f"no explicit catalog capability for {name!r} (add it — never infer from stage/kind)")
    cap = _CAPABILITY[name]
    role = getattr(component, "execution_role", "")
    rec = rights.rights_record(name)
    return CatalogEntry(
        component_id=name, module=getattr(component, "module", ""),
        card_path=f"docs/cards/{name.split('.')[0]}.md", doi=getattr(component, "doi", "") or "",
        stage=getattr(component, "stage", ""), execution_role=role, kind=getattr(component, "kind", ""),
        is_runtime_stage=(role == "runtime"), is_calibration_or_closure=(role == "calibration"),
        has_callable_code=(role in ("runtime", "calibration")),
        native_runner_id=(lab_runners.RUNNERS[name][0].runner_id if lab_runners.has_runner(name) else None),
        common_scenario_adapter_id=(lab.ADAPTERS[name].adapter_id if name in lab.ADAPTERS else None),
        gate_ids=_gate_ids(component), evidence_strength=getattr(component, "evidence_strength", ""),
        provenance_class=getattr(component, "provenance_class", ""),
        validity_range=getattr(component, "valid_range", None),
        optional_dependency=_OPTIONAL_DEPENDENCY.get(name),
        quantity_basis=rb.basis_of(name).quantity_basis,
        code_rights_state=rec.code_rights_state, data_rights_state=rec.data_rights_state,
        output_redistribution_state=rec.output_redistribution_state,
        public_execution_eligible=rights.may_execute_in_public_batch(name).allowed,
        output_publication_eligible=rights.may_publish_outputs(name).allowed,
        disposition=cap["disposition"], adapter_capability=cap["adapter_capability"],
        metadata_review_date="2026-07-19")


def build_catalog() -> list:
    """One entry per registered component, deterministic order."""
    import puckworks
    return [catalog_entry(c) for c in sorted(puckworks.components(), key=lambda c: c.name)]


def catalog_by_id() -> dict:
    return {e.component_id: e for e in build_catalog()}


def validate_catalog() -> list:
    """CI guard: every registered component has an explicit entry; the entry's disposition/adapter
    capability are in the finite vocabularies; gate ids resolve to real gate functions; a declared
    runner/adapter id resolves; rights states match the centralized registry. Returns problems."""
    import puckworks
    from puckworks import rights
    from puckworks.product import lab, lab_runners
    problems: list[str] = []
    registered = {c.name: c for c in puckworks.components()}
    # coverage: every registered component appears; no stale/extra catalog id
    for name in registered:
        if name not in _CAPABILITY:
            problems.append(f"registered component {name!r} has no explicit catalog capability")
    for name in _CAPABILITY:
        if name not in registered:
            problems.append(f"catalog capability for {name!r} names no registered component")
    for name, comp in registered.items():
        if name not in _CAPABILITY:
            continue
        e = catalog_entry(comp)
        if e.disposition not in lab.DISPOSITIONS:
            problems.append(f"{name}: disposition {e.disposition!r} not in DISPOSITIONS")
        if e.adapter_capability not in lab.ADAPTER_CAPABILITIES:
            problems.append(f"{name}: adapter_capability {e.adapter_capability!r} invalid")
        # gate ids resolve to real gate functions on the validation module
        from puckworks.validation import gates as G
        for gid in e.gate_ids:
            if not hasattr(G, gid):
                problems.append(f"{name}: gate id {gid!r} does not resolve in puckworks.validation.gates")
        if e.native_runner_id and not lab_runners.has_runner(name):
            problems.append(f"{name}: declares a runner id but no runner is registered")
        if e.common_scenario_adapter_id and name not in lab.ADAPTERS:
            problems.append(f"{name}: declares an adapter id but no adapter is registered")
        # rights must match the centralized registry
        rec = rights.rights_record(name)
        if (e.code_rights_state, e.data_rights_state, e.output_redistribution_state) != (
                rec.code_rights_state, rec.data_rights_state, rec.output_redistribution_state):
            problems.append(f"{name}: catalog rights disagree with puckworks.rights")
        # a rights-blocked component must be dispositioned RIGHTS_BLOCKED (never a lens/adapter)
        if rec.is_code_blocked and e.disposition != "RIGHTS_BLOCKED":
            problems.append(f"{name}: rights-blocked but disposition {e.disposition!r} != RIGHTS_BLOCKED")
    return problems


def canonical_json(entries: list) -> str:
    import json
    return json.dumps([e.to_dict() for e in entries], indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv=None) -> int:
    import argparse
    import sys
    ap = argparse.ArgumentParser(prog="puckworks.product.lab_catalog", description=__doc__)
    ap.add_argument("cmd", choices=["show", "verify"], nargs="?", default="show")
    a = ap.parse_args(argv)
    if a.cmd == "verify":
        problems = validate_catalog()
        if problems:
            print("CATALOG INVALID:")
            for p in problems:
                print("  -", p)
            return 1
        print(f"catalog OK: {len(build_catalog())} components covered")
        return 0
    sys.stdout.write(canonical_json(build_catalog()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
