"""puckworks.registry — component metadata, lookup, and gate execution.

A component is a stage implementation with provenance and validation gates.
The 'mega-model' is a configuration: one registered component per stage (or an
offline calibration chain feeding parameters into runtime components).

Schema v2 (2026-07-15) splits the overloaded ``kind`` string into three typed axes so a
generator can render Paper 3 from live metadata (WP2.1):

    execution_role   : what the component DOES at run time
    provenance_class : WHERE it came from (published port vs project work)
    evidence_strength: HOW WELL it is validated (never auto-assigned)

``kind`` is retained as a DEPRECATED compatibility field; ``register`` back-fills only
``execution_role`` from ``kind`` (a documented 1:1 map). ``provenance_class`` and
``evidence_strength`` are NO LONGER inferred from the component name — they are assigned from the
authoritative tables in ``puckworks.models`` and enforced by ``finalize_registry``. Public
accessors (``get``/``components``) return read-only snapshots; ``_mutable`` is the internal
handle used to apply the authoritative metadata. ``load_builtin_components`` names the
registration explicitly instead of relying on an import side effect.
"""
import copy
from dataclasses import dataclass, field
from typing import Callable, Optional

SCHEMA_VERSION = 2   # 2: typed axes (execution_role/provenance_class/evidence_strength) authoritative

STAGES = ["grind", "packing", "machine", "infiltration", "flow",
          "extraction", "bed_dynamics", "observables"]

# a gate is a zero-arg callable returning a mapping with a "passed" key
Gate = Callable[[], dict]

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
    gates: list[Gate] = field(default_factory=list)   # zero-arg callables -> dict(passed=bool, ...)
    notes: str = ""
    # --- schema v2 typed axes (execution_role/provenance_class back-filled in register) ---
    execution_role: Optional[str] = None
    provenance_class: Optional[str] = None
    evidence_strength: Optional[str] = None     # never auto-assigned (no upgrading of claims)


_REGISTRY: dict[str, Component] = {}


def _derive_execution_role(kind: str) -> str:
    # execution_role from the legacy `kind` (a documented 1:1 map, NOT name-prefix inference):
    # a synthesis component still advances state at run time, so it maps to 'runtime'.
    return {"runtime": "runtime", "calibration": "calibration",
            "synthesis": "runtime"}.get(kind, kind)


def register(c: Component):
    # WP4.4: metadata validation raises EXPLICIT exceptions (not `assert`) so enum/stage checks
    # cannot vanish under `python -O`.
    if c.stage not in STAGES:
        raise ValueError("component %r: bad stage %r (not in %r)" % (c.name, c.stage, STAGES))
    if c.name in _REGISTRY:
        raise ValueError("duplicate component id %r" % c.name)
    # execution_role is back-filled from `kind` (deprecated) when not given. provenance_class and
    # evidence_strength are NOT inferred from the name — they are assigned explicitly by the
    # authoritative tables in puckworks.models and enforced by finalize_registry().
    if c.execution_role is None:
        c.execution_role = _derive_execution_role(c.kind)
    if c.execution_role not in EXECUTION_ROLES:
        raise ValueError("component %r: bad execution_role %r" % (c.name, c.execution_role))
    if c.provenance_class is not None and c.provenance_class not in PROVENANCE_CLASSES:
        raise ValueError("component %r: bad provenance_class %r" % (c.name, c.provenance_class))
    if c.evidence_strength is not None and c.evidence_strength not in EVIDENCE_STRENGTHS:
        raise ValueError("component %r: bad evidence_strength %r" % (c.name, c.evidence_strength))
    _REGISTRY[c.name] = c
    return c


def finalize_registry():
    """After the authoritative metadata tables are applied, every component must carry a valid
    provenance_class (no name-prefix inference) — raise if any is unset/invalid."""
    for c in _REGISTRY.values():
        if c.provenance_class not in PROVENANCE_CLASSES:
            raise ValueError("component %r: provenance_class %r not assigned/valid — set it in "
                             "the authoritative table" % (c.name, c.provenance_class))
    return True


def load_builtin_components():
    """Ensure the built-in components are registered (idempotent). Importing puckworks.models has
    the same effect; this names the operation explicitly rather than relying on an import side
    effect at the call site."""
    import puckworks.models  # noqa: F401  (registration runs on first import; cached thereafter)
    return len(_REGISTRY)


def reset_registry():
    """Clear the registry (test helper for isolated/alternate component sets)."""
    _REGISTRY.clear()


def _snapshot(c: Component) -> Component:
    s = copy.copy(c)
    s.gates = tuple(c.gates)          # read-only gate collection
    return s


def components(stage: str | None = None):
    """Read-only snapshots of the registered components (mutating a snapshot does not affect the
    registry)."""
    return [_snapshot(c) for c in _REGISTRY.values() if stage is None or c.stage == stage]


def get(name: str) -> Component:
    """A read-only snapshot of one component."""
    return _snapshot(_REGISTRY[name])


def _mutable(name: str) -> Component:
    """Internal: the live registry object (for the authoritative-metadata assignment)."""
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
    """Boolean COMPAT wrapper. Prefer `gate_runner.evaluate_component_gates` for a typed report.
    Evaluates every gate of the component (no short-circuit) and returns True iff none FAIL/ERROR.
    A zero-gate component is NOT a vacuous pass — SKIP/ACKNOWLEDGED_EXCEPTION are non-failing but
    explicit in the typed result."""
    from puckworks.gate_runner import evaluate_component_gates, GateStatus
    results = evaluate_component_gates(name)
    if verbose:
        for r in results:
            print("[%s] %s: %s  %s" % (name, r.gate_id, r.status.value,
                                       r.exception_message or r.metrics))
    return not any(r.status in (GateStatus.FAIL, GateStatus.ERROR) for r in results)


def run_all_gates(verbose=True) -> bool:
    """Boolean COMPAT wrapper over `gate_runner.evaluate_all_gates` — runs EVERY gate (no
    short-circuit) and returns the suite's pass state. Prefer the typed suite for reporting."""
    from puckworks.gate_runner import evaluate_all_gates
    suite = evaluate_all_gates()
    if verbose:
        print(suite.summary_text())
    return suite.passed
