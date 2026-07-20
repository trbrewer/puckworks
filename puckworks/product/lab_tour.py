"""Full Laboratory Tour — a broad, honest, per-component walk of the whole registry (#43 / #70).

The Tour resolves EVERY registered component to exactly ONE primary route and runs the ones that are
scientifically and legally available, WITHOUT pretending their outputs are directly comparable. It never
averages, ranks, normalizes, or overlays incompatible component outputs.

Six finite routes (richest available wins, but a rights block overrides everything):

  COMMON_SCENARIO      the component receives the entered recipe through a documented adapter
  NATIVE_REFERENCE     the component runs its own provenance-bound reference case
  SCIENTIFIC_CHECK     the component's registered gate(s) run (NOT a full model simulation)
  OPTIONAL_DEPENDENCY  the component needs an optional dependency/environment that is absent
  RIGHTS_BLOCKED       the component is shown but receives ZERO execution calls
  NO_EXECUTION_PATH    the component is catalogued but has no defensible runner/check today

"Ran successfully" and "directly comparable" are separate facts. A gate pass is not experimental
validation; a native reference is not a prediction of the user's shot; a calibration/closure gate is not
an extraction model; a catalog listing is not an execution.

The manifest is versioned and FROZEN (``FULL_LABORATORY_TOUR_V1``): a newly registered component, a rights
change, or a new runner that contradicts the frozen decision fails ``verify_tour_manifest`` until the
manifest is updated as a reviewable change — it never silently expands.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from enum import Enum

FULL_LABORATORY_TOUR_V1 = "full_laboratory_tour_v1"
TOUR_MANIFESTS = (FULL_LABORATORY_TOUR_V1,)


class TourExecutionKind(str, Enum):
    COMMON_SCENARIO = "COMMON_SCENARIO"
    NATIVE_REFERENCE = "NATIVE_REFERENCE"
    SCIENTIFIC_CHECK = "SCIENTIFIC_CHECK"
    OPTIONAL_DEPENDENCY = "OPTIONAL_DEPENDENCY"
    RIGHTS_BLOCKED = "RIGHTS_BLOCKED"
    NO_EXECUTION_PATH = "NO_EXECUTION_PATH"


class InputOrigin(str, Enum):
    ENTERED_RECIPE = "ENTERED_RECIPE"                # common scenario: the user's recipe via an adapter
    COMPONENT_NATIVE_CASE = "COMPONENT_NATIVE_CASE"  # native reference: the component's own bound case
    REGISTERED_FIXTURE = "REGISTERED_FIXTURE"        # scientific check: the gate's own data/fixture
    NONE = "NONE"                                    # blocked / optional-unavailable / no-path


class TourExecutionStatus(str, Enum):
    EXECUTED = "EXECUTED"                    # a producer/check ran and completed
    CHECK_FAILED = "CHECK_FAILED"            # a registered gate returned FAIL (a scientific negative)
    EXECUTION_ERROR = "EXECUTION_ERROR"      # a producer/gate raised (never a scientific zero)
    RIGHTS_BLOCKED = "RIGHTS_BLOCKED"        # rights-blocked; zero execution calls
    RIGHTS_NOT_CLEARED = "RIGHTS_NOT_CLEARED"  # not affirmatively cleared for this (public) context
    OPTIONAL_UNAVAILABLE = "OPTIONAL_UNAVAILABLE"  # optional dependency/environment absent
    NO_GATE_ACKNOWLEDGED = "NO_GATE_ACKNOWLEDGED"  # zero-gate component (acknowledged, never a pass)
    NO_EXECUTION_PATH = "NO_EXECUTION_PATH"  # catalogued, no defensible runner/check
    DOMAIN_DECLINED = "DOMAIN_DECLINED"      # the lens declined (recipe outside the evidence range)


# ── the FROZEN route decision for tour v1 (a reviewable change; verified against the live registry) ──
_K = TourExecutionKind
_TOUR_V1_ROUTES: dict[str, TourExecutionKind] = {
    # common-scenario lens (the entered recipe via an adapter)
    "cameron2020.extraction_bdf": _K.COMMON_SCENARIO,
    # native reference runners (the component's own provenance-bound case)
    "brewer2026.lb_reference": _K.NATIVE_REFERENCE,
    "foster2025.infiltration": _K.NATIVE_REFERENCE,
    "wadsworth2026.permeability": _K.NATIVE_REFERENCE,
    "waszkiewicz2025.poroelastic": _K.NATIVE_REFERENCE,
    # rights-blocked (shown, never executed) — #73
    "grudeva2025.reduced": _K.RIGHTS_BLOCKED,
    # optional dependency (taichi), no enabled quick demonstration yet
    "brewer2026.lb_taichi": _K.OPTIONAL_DEPENDENCY,
    # registered scientific checks (the component's own gate(s); not a full simulation)
    "brewer2026.coupled_kappa_t": _K.SCIENTIFIC_CHECK,
    "brewer2026.pack_generator": _K.SCIENTIFIC_CHECK,
    "brewer2026.streamtube": _K.SCIENTIFIC_CHECK,
    "fasano2000_partI.fines_migration": _K.SCIENTIFIC_CHECK,
    "foster2025.machine_mode": _K.SCIENTIFIC_CHECK,
    "lee2023.feedback": _K.SCIENTIFIC_CHECK,
    "liang2021.desorption": _K.SCIENTIFIC_CHECK,
    "mo2023_2.coupled_bed": _K.SCIENTIFIC_CHECK,
    "mo2023_2.swelling": _K.SCIENTIFIC_CHECK,
    "moroney2016.surrogate": _K.SCIENTIFIC_CHECK,
    "pannusch2024.closures": _K.SCIENTIFIC_CHECK,
    "pannusch2024.solver": _K.SCIENTIFIC_CHECK,
    "romancorrochano2017.extraction": _K.SCIENTIFIC_CHECK,
    "sourcing2026.g10_liquor_rheology": _K.SCIENTIFIC_CHECK,
    "sourcing2026.g1_glassbead_analog": _K.SCIENTIFIC_CHECK,
    "sourcing2026.g3_pump_characteristic": _K.SCIENTIFIC_CHECK,
    "wadsworth2026.grindmap": _K.SCIENTIFIC_CHECK,
    "wadsworth2026.inertial": _K.SCIENTIFIC_CHECK,
}
_TOUR_ROUTES = {FULL_LABORATORY_TOUR_V1: _TOUR_V1_ROUTES}

_INPUT_ORIGIN = {
    _K.COMMON_SCENARIO: InputOrigin.ENTERED_RECIPE,
    _K.NATIVE_REFERENCE: InputOrigin.COMPONENT_NATIVE_CASE,
    _K.SCIENTIFIC_CHECK: InputOrigin.REGISTERED_FIXTURE,
    _K.OPTIONAL_DEPENDENCY: InputOrigin.NONE,
    _K.RIGHTS_BLOCKED: InputOrigin.NONE,
    _K.NO_EXECUTION_PATH: InputOrigin.NONE,
}


def _optional_dependencies() -> dict:
    from puckworks.product import lab_catalog
    return dict(getattr(lab_catalog, "_OPTIONAL_DEPENDENCY", {"brewer2026.lb_taichi": "taichi"}))


def _dependency_available(dep: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(dep) is not None


def _derive_route(component) -> TourExecutionKind:
    """The route a component WOULD get from the authoritative sources (rights → adapter → runner →
    optional-no-gate → gate → none). The frozen manifest must equal this for every registered component;
    any drift is a reviewable manifest update (never a silent expansion)."""
    from puckworks import rights
    from puckworks.product import lab, lab_runners
    cid = component.name
    if rights.is_code_rights_blocked(cid):
        return _K.RIGHTS_BLOCKED
    if cid in getattr(lab, "ADAPTERS", {}):
        return _K.COMMON_SCENARIO
    if lab_runners.has_runner(cid):
        return _K.NATIVE_REFERENCE
    opt = _optional_dependencies()
    if cid in opt and not getattr(component, "gates", ()):
        return _K.OPTIONAL_DEPENDENCY
    if getattr(component, "gates", ()):
        return _K.SCIENTIFIC_CHECK
    if cid in opt:
        return _K.OPTIONAL_DEPENDENCY
    return _K.NO_EXECUTION_PATH


# ── the typed plan (one primary route per component) ─────────────────────────────────
@dataclasses.dataclass(frozen=True)
class TourComponentPlan:
    component_id: str
    stage: str
    execution_kind: TourExecutionKind
    producer_id: str | None
    comparability_group: str | None
    input_origin: InputOrigin
    expected_output_roles: tuple
    reason: str

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["execution_kind"] = self.execution_kind.value
        d["input_origin"] = self.input_origin.value
        d["expected_output_roles"] = list(self.expected_output_roles)
        return d


def _producer_id(component, kind: TourExecutionKind):
    from puckworks.product import lab, lab_runners
    cid = component.name
    if kind == _K.COMMON_SCENARIO:
        return lab.ADAPTERS[cid].adapter_id
    if kind == _K.NATIVE_REFERENCE:
        return lab_runners.RUNNERS[cid][0].runner_id
    if kind == _K.SCIENTIFIC_CHECK:
        return "gates:" + ",".join(sorted(getattr(g, "__name__", "") for g in component.gates))
    return None


def _comparability_group(component, kind: TourExecutionKind):
    # ONLY common-scenario extraction lenses that share a quantity basis may ever share an axis. Today
    # Cameron is the sole common lens, so its group is a singleton and nothing is ever overlaid. Every
    # other route is non-comparable by construction (group None).
    if kind == _K.COMMON_SCENARIO:
        return "extraction_ey_tds_bed_volume"
    return None


def _plan_reason(component, kind: TourExecutionKind) -> str:
    return {
        _K.COMMON_SCENARIO: "receives the entered recipe through a documented adapter",
        _K.NATIVE_REFERENCE: "runs its own provenance-bound native reference case (not a prediction of "
                             "the entered shot)",
        _K.SCIENTIFIC_CHECK: "runs its registered scientific gate(s) on their own fixture — a check, not "
                             "a full model simulation and not experimental validation",
        _K.OPTIONAL_DEPENDENCY: "needs an optional dependency/environment that is absent; no enabled quick "
                                "demonstration yet",
        _K.RIGHTS_BLOCKED: "rights-blocked; shown but never executed (see the component's rights record)",
        _K.NO_EXECUTION_PATH: "catalogued, but no defensible runner or check currently exists",
    }[kind]


def _expected_roles(kind: TourExecutionKind) -> tuple:
    return {
        _K.COMMON_SCENARIO: ("simulated", "derived", "prescribed"),
        _K.NATIVE_REFERENCE: ("simulated", "analytic_reference", "fitted", "reference", "derived"),
        _K.SCIENTIFIC_CHECK: ("gate_metric",),
    }.get(kind, ())


def _component_plan(component, kind: TourExecutionKind) -> TourComponentPlan:
    return TourComponentPlan(
        component_id=component.name, stage=getattr(component, "stage", ""), execution_kind=kind,
        producer_id=_producer_id(component, kind), comparability_group=_comparability_group(component, kind),
        input_origin=_INPUT_ORIGIN[kind], expected_output_roles=_expected_roles(kind),
        reason=_plan_reason(component, kind))


def tour_manifest(manifest_id: str = FULL_LABORATORY_TOUR_V1) -> dict:
    """The frozen tour plan: one TourComponentPlan per registered component, deterministic order."""
    if manifest_id not in _TOUR_ROUTES:
        raise ValueError(f"unknown tour manifest {manifest_id!r}; known: {TOUR_MANIFESTS}")
    import puckworks
    routes = _TOUR_ROUTES[manifest_id]
    plans = {}
    for c in sorted(puckworks.components(), key=lambda c: c.name):
        if c.name in routes:                              # unclassified components are caught by the verifier
            plans[c.name] = _component_plan(c, routes[c.name])
    return plans


def native_reference_ids(manifest_id: str = FULL_LABORATORY_TOUR_V1) -> tuple:
    """The FROZEN native-reference component ids in this tour (includes batch-only runners like the LB
    reference — deliberately NOT the interactive_fast policy, which omits it)."""
    routes = _TOUR_ROUTES[manifest_id]
    return tuple(sorted(cid for cid, k in routes.items() if k == _K.NATIVE_REFERENCE))


def verify_tour_manifest(manifest_id: str = FULL_LABORATORY_TOUR_V1) -> list:
    """Coverage verifier. Returns problems (empty == clean). Fails when a registered component has no tour
    resolution, an unknown id is listed, a rights-blocked component is assigned an executable route, the
    frozen route disagrees with the live registry (a new runner/adapter/rights change), or a native
    runner / common-scenario adapter is orphaned from the manifest."""
    import puckworks
    from puckworks.product import lab, lab_runners
    if manifest_id not in _TOUR_ROUTES:
        return [f"unknown tour manifest {manifest_id!r}"]
    routes = _TOUR_ROUTES[manifest_id]
    registered = {c.name: c for c in puckworks.components()}
    problems = []
    # coverage: every registered component classified exactly once
    for cid in registered:
        if cid not in routes:
            problems.append(f"{cid}: registered component has no tour resolution (classify it in the "
                            f"frozen manifest)")
    for cid in routes:
        if cid not in registered:
            problems.append(f"{cid}: manifest references an unknown (unregistered) component")
    # per-component consistency with the live authoritative sources
    for cid, comp in registered.items():
        if cid not in routes:
            continue
        frozen = routes[cid]
        derived = _derive_route(comp)
        if frozen != derived:
            problems.append(f"{cid}: frozen route {frozen.value} != derived {derived.value} "
                            f"(a reviewable manifest update is required)")
        if frozen == _K.RIGHTS_BLOCKED:
            from puckworks import rights
            if not rights.is_code_rights_blocked(cid):
                problems.append(f"{cid}: routed RIGHTS_BLOCKED but is not code-rights-blocked")
    # no orphaned native runner / common-scenario adapter
    for cid in lab_runners.RUNNERS:
        if routes.get(cid) != _K.NATIVE_REFERENCE:
            problems.append(f"{cid}: has a native runner but is not routed NATIVE_REFERENCE")
    for cid in getattr(lab, "ADAPTERS", {}):
        if routes.get(cid) != _K.COMMON_SCENARIO:
            problems.append(f"{cid}: has a common-scenario adapter but is not routed COMMON_SCENARIO")
    return problems


# ── per-component result + tour result ───────────────────────────────────────────────
@dataclasses.dataclass(frozen=True)
class TourComponentResult:
    component_id: str
    stage: str
    execution_kind: str
    execution_status: str
    input_origin: str
    inputs_used: list
    outputs: list
    output_roles: list
    evidence: dict
    fidelity_ceiling: str
    rights_decision: dict
    comparability_group: str | None
    comparable_component_ids: list
    duration_seconds: float | None
    scientific_hash: str | None
    message: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _sci_hash(payload) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
                                     default=str).encode("utf-8")).hexdigest()


def _rights_decision(cid: str) -> dict:
    from puckworks import rights
    r = rights.rights_record(cid)
    return {"code_rights_state": r.code_rights_state, "data_rights_state": r.data_rights_state,
            "output_redistribution_state": r.output_redistribution_state,
            "decision_issue": r.decision_issue}


# ── per-route execution (every executing route goes through lab_service: preflight before producer) ──
def _scenario_kwargs(scenario_request) -> dict:
    return {"preset_id": scenario_request.preset_id, "overrides": dict(scenario_request.overrides),
            "domain_policy": scenario_request.domain_policy}


def _blocked_card(plan, status: str, message: str, duration=None) -> TourComponentResult:
    """A non-scientific resolution card: empty outputs, NO scientific hash, no fabricated metric."""
    return TourComponentResult(
        component_id=plan.component_id, stage=plan.stage, execution_kind=plan.execution_kind.value,
        execution_status=status, input_origin=InputOrigin.NONE.value, inputs_used=[], outputs=[],
        output_roles=[], evidence={}, fidelity_ceiling="", rights_decision=_rights_decision(plan.component_id),
        comparability_group=None, comparable_component_ids=[], duration_seconds=duration,
        scientific_hash=None, message=message)


def _run_common_scenario(plan, scenario_request, execution_context) -> TourComponentResult:
    from puckworks.product import lab, lab_service
    t0 = time.perf_counter()
    req = lab.ScenarioRequest(lens_selection_policy="selected", requested_lens_ids=(plan.component_id,),
                              reference_selection_policy="none", **_scenario_kwargs(scenario_request))
    result = lab_service.execute_lab_request(req, execution_context=execution_context)
    dur = time.perf_counter() - t0
    if result.blocked:
        return _blocked_card(plan, TourExecutionStatus.RIGHTS_NOT_CLEARED.value,
                             "; ".join(result.blockers) or "not cleared for this context", dur)
    rep = result.report
    lenses = [x for x in rep.get("executed_lenses", []) if x["component_id"] == plan.component_id]
    if not lenses:
        # the lens did not execute (e.g. domain-declined); surface it distinctly, no fabricated output
        dom = rep.get("domain", {})
        return _blocked_card(plan, TourExecutionStatus.DOMAIN_DECLINED.value,
                             dom.get("block_reason") or "lens did not execute (outside evidence range)", dur)
    lens = lenses[0]
    outputs = [{"name": o["name"], "value": o["value"], "unit": o["unit"], "role": o["role"]}
               for o in lens["observables"]]
    payload = {"component_id": plan.component_id, "kind": plan.execution_kind.value, "outputs": outputs}
    return TourComponentResult(
        component_id=plan.component_id, stage=plan.stage, execution_kind=plan.execution_kind.value,
        execution_status=TourExecutionStatus.EXECUTED.value, input_origin=plan.input_origin.value,
        inputs_used=[{"name": k, **v} for k, v in (rep.get("scenario", {}).get("effective_recipe") or {}).items()
                     if isinstance(v, dict)] or [{"source": "entered recipe"}],
        outputs=outputs, output_roles=sorted({o["role"] for o in outputs}),
        evidence={"evidence_strength": _evidence_strength(plan.component_id)},
        fidelity_ceiling="one bounded scenario, one machine/coffee; chemical composition, not taste; not a "
                         "digital twin",
        rights_decision=_rights_decision(plan.component_id), comparability_group=plan.comparability_group,
        comparable_component_ids=[plan.component_id], duration_seconds=dur, scientific_hash=_sci_hash(payload),
        message="ran the entered recipe through the Cameron extraction adapter")


def _run_native_reference(plan, scenario_request, execution_context) -> TourComponentResult:
    from puckworks.product import lab, lab_service
    t0 = time.perf_counter()
    req = lab.ScenarioRequest(lens_selection_policy="none", reference_selection_policy="selected",
                              requested_reference_runner_ids=(plan.component_id,),
                              **_scenario_kwargs(scenario_request))
    result = lab_service.execute_lab_request(req, execution_context=execution_context)
    dur = time.perf_counter() - t0
    if result.blocked:
        return _blocked_card(plan, TourExecutionStatus.RIGHTS_NOT_CLEARED.value,
                             "; ".join(result.blockers) or "not cleared for this context", dur)
    refs = [x for x in result.report.get("executed_reference_results", [])
            if x["component_id"] == plan.component_id]
    if not refs:
        return _blocked_card(plan, TourExecutionStatus.EXECUTION_ERROR.value,
                             "native reference did not produce a result", dur)
    r = refs[0]
    if r.get("status") != "executed":
        return _blocked_card(plan, TourExecutionStatus.EXECUTION_ERROR.value,
                             r.get("error") or "native reference failed", dur)
    outputs = [{"name": o["name"], "value": o["value"], "unit": o["unit"], "role": o["role"]}
               for o in r.get("outputs", [])]
    return TourComponentResult(
        component_id=plan.component_id, stage=plan.stage, execution_kind=plan.execution_kind.value,
        execution_status=TourExecutionStatus.EXECUTED.value, input_origin=plan.input_origin.value,
        inputs_used=r.get("native_inputs", []), outputs=outputs,
        output_roles=sorted({o["role"] for o in outputs}),
        evidence=r.get("evidence", {}), fidelity_ceiling=r.get("fidelity_ceiling", ""),
        rights_decision=_rights_decision(plan.component_id), comparability_group=None,
        comparable_component_ids=[plan.component_id],   # a native case is comparable to nothing else
        duration_seconds=dur, scientific_hash=r.get("scientific_payload_hash"),
        message="ran the component's own native reference case (not a prediction of the entered shot)")


def _run_scientific_check(plan, execution_context) -> TourComponentResult:
    """Delegate to the single rights-aware component-check runner (the tour's ONE source of gate
    execution). A rights-blocked component is refused there before any gate call (defence in depth: it is
    also never routed here)."""
    from puckworks.product import lab_component_checks as CC
    cr = CC.run_component_checks([plan.component_id], execution_context=execution_context)[0]
    if cr.execution_status in (CC.ComponentCheckStatus.RIGHTS_BLOCKED.value,
                               CC.ComponentCheckStatus.RIGHTS_NOT_CLEARED.value):
        status = (TourExecutionStatus.RIGHTS_BLOCKED.value
                  if cr.execution_status == CC.ComponentCheckStatus.RIGHTS_BLOCKED.value
                  else TourExecutionStatus.RIGHTS_NOT_CLEARED.value)
        return _blocked_card(plan, status, cr.blocker)
    outputs = [{"gate_id": g["gate_id"], "status": g["status"], "metrics": g["metrics"],
                "summary": g["summary"]} for g in cr.gates]
    return TourComponentResult(
        component_id=plan.component_id, stage=plan.stage, execution_kind=plan.execution_kind.value,
        execution_status=cr.execution_status, input_origin=plan.input_origin.value,
        inputs_used=[{"source": "the gate's own registered fixture/data"}], outputs=outputs,
        output_roles=["gate_metric"], evidence=cr.evidence, fidelity_ceiling=cr.fidelity_ceiling,
        rights_decision=cr.rights_decision, comparability_group=None,
        comparable_component_ids=[plan.component_id], duration_seconds=cr.duration_seconds,
        scientific_hash=cr.scientific_hash,
        message="ran the component's registered scientific gate(s)")


def _run_optional(plan) -> TourComponentResult:
    dep = _optional_dependencies().get(plan.component_id, "")
    avail = _dependency_available(dep) if dep else False
    msg = (f"optional dependency '{dep}' is installed but no enabled quick demonstration exists yet"
           if avail else f"optional dependency '{dep}' is not available in this environment")
    return _blocked_card(plan, TourExecutionStatus.OPTIONAL_UNAVAILABLE.value, msg)


def _evidence_strength(cid: str) -> str:
    import puckworks
    for c in puckworks.components():
        if c.name == cid:
            return getattr(c, "evidence_strength", "")
    return ""


def _resolve_component(plan, scenario_request, execution_context) -> TourComponentResult:
    k = plan.execution_kind
    if k == _K.RIGHTS_BLOCKED:
        r = _rights_decision(plan.component_id)
        from puckworks import rights
        return _blocked_card(plan, TourExecutionStatus.RIGHTS_BLOCKED.value,
                             rights.rights_record(plan.component_id).rights_note
                             or "rights-blocked; not executed")
    if k == _K.COMMON_SCENARIO:
        return _run_common_scenario(plan, scenario_request, execution_context)
    if k == _K.NATIVE_REFERENCE:
        return _run_native_reference(plan, scenario_request, execution_context)
    if k == _K.SCIENTIFIC_CHECK:
        return _run_scientific_check(plan, execution_context)
    if k == _K.OPTIONAL_DEPENDENCY:
        return _run_optional(plan)
    return _blocked_card(plan, TourExecutionStatus.NO_EXECUTION_PATH.value,
                         "catalogued; no defensible runner or check currently exists")


@dataclasses.dataclass(frozen=True)
class LaboratoryTourResult:
    manifest_id: str
    execution_context: str
    scenario: dict
    components: list          # list[TourComponentResult]
    summary: dict
    stages: dict
    tour_scientific_hash: str

    def to_dict(self) -> dict:
        return {"report": "puckworks-full-laboratory-tour", "manifest_id": self.manifest_id,
                "execution_context": self.execution_context, "scenario": self.scenario,
                "summary": self.summary, "stages": self.stages,
                "components": [c.to_dict() for c in self.components],
                "tour_scientific_hash": self.tour_scientific_hash}


def _summary(results) -> dict:
    """Counts DERIVED from results (never hard-coded). Counts execution statuses only — never aggregates
    scientific values across components."""
    S = TourExecutionStatus
    def n(*st):
        return sum(1 for r in results if r.execution_status in [s.value for s in st])
    completed = n(S.EXECUTED)
    attempted = sum(1 for r in results if r.execution_status in
                    [S.EXECUTED.value, S.CHECK_FAILED.value, S.EXECUTION_ERROR.value])
    return {
        "registered": len(results),
        "attempted": attempted,
        "completed": completed,
        "check_failed": n(S.CHECK_FAILED),
        "execution_error": n(S.EXECUTION_ERROR),
        "rights_blocked": n(S.RIGHTS_BLOCKED),
        "rights_not_cleared": n(S.RIGHTS_NOT_CLEARED),
        "optional_unavailable": n(S.OPTIONAL_UNAVAILABLE),
        "no_execution_path": n(S.NO_EXECUTION_PATH),
        "domain_declined": n(S.DOMAIN_DECLINED),
        "no_gate_acknowledged": n(S.NO_GATE_ACKNOWLEDGED),
        "by_kind": {k.value: sum(1 for r in results if r.execution_kind == k.value)
                    for k in TourExecutionKind},
    }


def execute_laboratory_tour(scenario_request, *, manifest_id: str = FULL_LABORATORY_TOUR_V1,
                            execution_context: str = "LOCAL_PRIVATE") -> LaboratoryTourResult:
    """Resolve EVERY registered component to exactly one primary route and run the available ones, honestly
    and per-component. Order: validate scenario → validate manifest → resolve each component (rights before
    any producer) → assemble stage-grouped result → deterministic hashes over canonical scientific content.
    Every route already runs through lab_service (preflight before producer); rights-blocked components
    receive zero execution calls."""
    from puckworks.product import lab_rights_gate as gate
    if execution_context not in gate.EXECUTION_CONTEXTS:
        raise ValueError(f"execution_context must be one of {gate.EXECUTION_CONTEXTS}, "
                         f"got {execution_context!r}")
    problems = verify_tour_manifest(manifest_id)
    if problems:
        raise ValueError("tour manifest invalid: " + "; ".join(problems))
    plans = tour_manifest(manifest_id)
    results = [_resolve_component(plans[cid], scenario_request, execution_context)
               for cid in sorted(plans)]
    # stage grouping (deterministic)
    stages: dict = {}
    for r in results:
        stages.setdefault(r.stage, []).append(r.component_id)
    stages = {k: sorted(v) for k, v in sorted(stages.items())}
    summary = _summary(results)
    # tour-level hash over canonical per-component scientific content only (order-stable, no runtime)
    tour_payload = sorted(((r.component_id, r.execution_kind, r.execution_status, r.scientific_hash)
                           for r in results))
    return LaboratoryTourResult(
        manifest_id=manifest_id, execution_context=execution_context,
        scenario={"preset_id": scenario_request.preset_id, "overrides": dict(scenario_request.overrides),
                  "domain_policy": scenario_request.domain_policy},
        components=results, summary=summary, stages=stages, tour_scientific_hash=_sci_hash(tour_payload))
