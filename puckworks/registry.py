"""puckworks.registry — component metadata, lookup, and gate execution.

A component is a stage implementation with provenance and validation gates.
The 'mega-model' is a configuration: one registered component per stage (or an
offline calibration chain feeding parameters into runtime components).

Schema v2 (2026-07-15) splits the overloaded ``kind`` string into three typed axes so a
generator can render Paper 3 from live metadata (WP2.1):

    execution_role   : what the component DOES at run time
    provenance_class : WHERE it came from (published port vs project work)
    evidence_strength: HOW WELL it is validated (never auto-assigned)

``kind`` is retained as a DEPRECATED compatibility field; ``register`` back-fills
``execution_role`` and ``provenance_class`` from ``kind``/``name`` when not given, so existing
registrations migrate without changing behaviour.
"""
from dataclasses import dataclass, field
from typing import Callable, Optional

STAGES = ["grind", "packing", "machine", "infiltration", "flow",
          "extraction", "bed_dynamics", "observables"]

EXECUTION_ROLES = ("runtime", "calibration", "observational_adapter", "diagnostic")
PROVENANCE_CLASSES = ("published_port", "project_model", "project_synthesis", "reference_only")
EVIDENCE_STRENGTHS = (
    "controlled_independent", "within_campaign_held_out", "post_fit_reconstruction",
    "source_curve_reproduction", "code_verification", "sign_or_compatibility",
    "qualitative_capacity", "exploratory_synthesis", "proposed_experiment",
)


@dataclass
class Component:
    name: str
    stage: str
    kind: str                       # DEPRECATED: use execution_role. Kept for back-compat.
    paper: str
    doi: str = ""
    module: str = ""
    assumptions: str = ""
    valid_range: str = ""
    gates: list = field(default_factory=list)   # callables -> dict(passed=bool, ...)
    notes: str = ""
    # --- schema v2 typed axes (execution_role/provenance_class back-filled in register) ---
    execution_role: Optional[str] = None
    provenance_class: Optional[str] = None
    evidence_strength: Optional[str] = None     # never auto-assigned (no upgrading of claims)


_REGISTRY: dict[str, Component] = {}


def _derive_execution_role(kind: str) -> str:
    # synthesis is a provenance concept, not an execution role; a synthesis component still
    # advances state at run time, so it maps to 'runtime'.
    return {"runtime": "runtime", "calibration": "calibration",
            "synthesis": "runtime"}.get(kind, kind)


def _derive_provenance_class(name: str, kind: str) -> str:
    if kind == "synthesis":
        return "project_synthesis"
    if name.startswith("brewer2026"):
        return "project_model"
    if name.startswith("sourcing2026"):
        return "reference_only"
    return "published_port"


def register(c: Component):
    assert c.stage in STAGES, c.stage
    if c.name in _REGISTRY:
        raise ValueError("duplicate component id %r" % c.name)
    # migrate: back-fill the typed axes from the legacy kind/name when not explicitly set.
    if c.execution_role is None:
        c.execution_role = _derive_execution_role(c.kind)
    if c.provenance_class is None:
        c.provenance_class = _derive_provenance_class(c.name, c.kind)
    # validate every SET enum value (evidence_strength may legitimately be None = unclassified).
    assert c.execution_role in EXECUTION_ROLES, c.execution_role
    assert c.provenance_class in PROVENANCE_CLASSES, c.provenance_class
    assert c.evidence_strength is None or c.evidence_strength in EVIDENCE_STRENGTHS, \
        c.evidence_strength
    _REGISTRY[c.name] = c
    return c


def components(stage: str | None = None):
    return [c for c in _REGISTRY.values() if stage is None or c.stage == stage]


def get(name: str) -> Component:
    return _REGISTRY[name]


def validate_registry():
    """Return a list of schema problems (empty = clean): unknown enum values, or a component
    with no evidence classification. Cross-references to cards/manifest/gates are checked by
    the Paper-3 reconciliation (PR4), which has those inputs."""
    problems = []
    for c in _REGISTRY.values():
        if c.execution_role not in EXECUTION_ROLES:
            problems.append("%s: bad execution_role %r" % (c.name, c.execution_role))
        if c.provenance_class not in PROVENANCE_CLASSES:
            problems.append("%s: bad provenance_class %r" % (c.name, c.provenance_class))
        if c.evidence_strength is not None and c.evidence_strength not in EVIDENCE_STRENGTHS:
            problems.append("%s: bad evidence_strength %r" % (c.name, c.evidence_strength))
        if c.evidence_strength is None:
            problems.append("%s: unclassified evidence_strength" % c.name)
    return problems


def run_gates(name: str, verbose=True) -> bool:
    c = _REGISTRY[name]
    ok = True
    for g in c.gates:
        r = g()
        ok &= bool(r.get("passed"))
        if verbose:
            print(f"[{name}] {g.__name__}: {'PASS' if r.get('passed') else 'FAIL'}  "
                  f"{ {k: v for k, v in r.items() if k != 'passed'} }")
    return ok


def run_all_gates(verbose=True) -> bool:
    return all(run_gates(n, verbose) for n in sorted(_REGISTRY))
