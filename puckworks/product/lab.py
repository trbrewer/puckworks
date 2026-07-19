"""Guided Pull Laboratory (PV-19B): expose the full component registry, run the compatible subset as
independent model lenses — with exact scenario identity, correct observable roles, an explicit
component capability/rights matrix, honest request semantics, and layered cryptographic integrity.

Two modes, kept scrupulously distinct:

* **Common-scenario model lenses** — one bounded espresso scenario is mapped into the *compatible*
  models; each runs independently through its existing authoritative producer. Only
  ``cameron2020.extraction_bdf`` is executable as the common-scenario lens today (via
  ``puckworks.product.simulate_pull``). Every other component gets an honest disposition; a lens that
  is *requested* but has no adapter is ``REQUESTED_BUT_NOT_EXECUTABLE`` — never silently dropped.
* **Component reference suite** — executable components' native reference cases (registry visibility),
  never presented as predictions of the common shot. Only actually-executed references appear in
  ``executed_reference_results``; the rest are honest coverage placeholders.

Schema v4 (distinct from ``PullRun`` v1). Request semantics are explicit and validated:

* ``domain_policy`` (``warn`` | ``strict``) is *operational*: the effective config carries the request's
  policy and the domain is evaluated once through the authoritative product domain BEFORE the producer
  runs. A ``REJECTED`` input blocks under any policy; an evidence-range ``WARNING`` blocks under
  ``strict``. When blocked, the scientific producer is **not** called.
* ``requested_lens_ids`` actually selects which common-scenario lenses execute (default: every
  executable common lens). An unknown id raises; a known-but-not-executable id is surfaced, not dropped.
* ``reference_selection_policy`` (``none`` | ``interactive_fast`` | ``selected``) is unambiguous. Under
  ``selected`` the ``requested_reference_runner_ids`` are validated; an unknown id raises.

Three integrity layers, each recomputed on demand (never trusted from the embedded field):

* **scientific payload** (``scientific_payload_sha256``) — the science, free of build provenance AND of
  the environment-dependent capability snapshot, so it is stable across build identity, Python version,
  and optional-dependency installation (installing Taichi does not change it for a Cameron-only request).
* **capability snapshot** (``capability_snapshot_sha256``) — the environment-dependent capability/rights
  matrix, optional-dependency availability, and interpreter fingerprint.
* **full artifact** (``artifact_sha256``) — the complete downloadable JSON including build provenance and
  the other two hashes (excluding only its own field).

Canonical JSON is finite: ``NaN``/``Infinity`` are rejected, never serialized.

This module **duplicates no model equation** (it calls ``simulate_pull`` and the registry), never sums
or averages competing mechanisms, never maps a grinder dial to a universal particle size, never overlays
incompatible concentration reference volumes, and never upgrades an evidence label. It does **not** run
git subprocesses — build provenance is supplied explicitly by the caller.

CLI::

    python -m puckworks.product.lab matrix   --format md|json
    python -m puckworks.product.lab compare  --preset pv19_named --format md|json
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import platform
import sys

SCHEMA_VERSION = 5
ARTIFACT_SCHEMA_VERSION = 1
_DEFAULT_PRESET = "pv19_named"
PRIMARY_LENS_ID = "cameron2020.extraction_bdf"        # the single declared primary common-scenario lens

# ── finite vocabularies ────────────────────────────────────────────────────────────
DOMAIN_POLICIES = ("warn", "strict")
REFERENCE_SELECTION_POLICIES = ("none", "interactive_fast", "selected")
# how the common-scenario lenses are chosen (never a future-expanding empty-tuple default)
LENS_SELECTION_POLICIES = ("primary", "all_ready", "selected", "none")
# per-request state of a lens; component-level reference resolution states
LENS_EXECUTION_STATES = ("NOT_REQUESTED", "EXECUTED", "REQUESTED_BUT_NOT_EXECUTABLE", "FAILED")
LENS_READINESS_STATES = ("READY", "NO_ADAPTER", "RIGHTS_BLOCKED", "OUTSIDE_DOMAIN", "NOT_APPLICABLE")
REFERENCE_RESOLUTION_STATES = (
    "EXECUTED", "FAILED", "RUNNER_NOT_IMPLEMENTED", "RIGHTS_BLOCKED",
    "OPTIONAL_DEPENDENCY_UNAVAILABLE", "RUNTIME_BUDGET_EXCEEDED", "NOT_APPLICABLE",
)

DISPOSITIONS = (
    "COMMON_SCENARIO_READY", "COMMON_SCENARIO_WITH_VERIFIED_ADAPTER", "NATIVE_REFERENCE_ONLY",
    "SUPPORTING_STAGE_LENS", "CALIBRATION_OR_CLOSURE", "ADAPTER_REQUIRED", "OUTSIDE_SCENARIO_DOMAIN",
    "RIGHTS_BLOCKED", "NOT_EXECUTABLE", "SKIPPED_OPTIONAL_DEPENDENCY", "FAILED", "METADATA_INCOMPLETE",
)
# STATIC capability of a component's native reference runner (does it exist / can it run in this env) —
# distinct from whether it was requested or executed for a given request.
NATIVE_RUNNER_CAPABILITIES = (
    "AVAILABLE", "NOT_IMPLEMENTED", "OPTIONAL_DEPENDENCY_UNAVAILABLE", "RIGHTS_BLOCKED", "NOT_APPLICABLE",
)
# STATIC capability of the common-scenario adapter for a component.
ADAPTER_CAPABILITIES = ("COMMON_SCENARIO_READY", "ADAPTER_REQUIRED", "RIGHTS_BLOCKED", "NOT_APPLICABLE")
# back-compat alias: older callers/tests validate a matrix row's native_runner_state against this name.
RUNNER_STATES = NATIVE_RUNNER_CAPABILITIES

# PER-REQUEST execution outcome of a native reference runner (what actually happened this run).
REQUEST_EXECUTION_STATES = (
    "NOT_REQUESTED", "EXECUTED", "FAILED", "SKIPPED_OPTIONAL_DEPENDENCY", "SKIPPED_RUNTIME_BUDGET",
    "RIGHTS_BLOCKED", "NOT_APPLICABLE",
)
# PER-REQUEST state of a common-scenario lens.
LENS_REQUEST_STATES = ("NOT_REQUESTED", "EXECUTED", "REQUESTED_BUT_NOT_EXECUTABLE")

WHAT_THIS_DOES_NOT_PROVE = [
    "Model agreement is not validation; these are independent lenses, not a validated digital twin.",
    "Competing mechanisms are never summed or averaged; overlaying two models is not an ensemble.",
    "A grinder dial is not a universal particle size; no dial->size conversion is applied.",
    "Concentrations on different reference volumes (bed-volume vs grain-volume) are not overlaid; such "
    "lenses are marked ADAPTER_REQUIRED until an inventory-conserving conversion is tested.",
    "The common scenario is not a best recipe and predicts no flavor or sensory quality.",
    "Native reference-suite results are each a component's OWN reference case, not a prediction of the "
    "common shot.",
]

# ── explicit component capability metadata (facts the registry does not encode) ──
# Rights truth is NOT kept here: it lives in the centralized puckworks.rights registry (issue #73), so
# the Lab consumes one authoritative record per component instead of a product-local dictionary.
_OPTIONAL_DEPENDENCY = {"brewer2026.lb_taichi": "taichi"}
# NOTE: which components have a common-scenario adapter is NOT a separate dict — it is the ADAPTERS
# registry (defined below). Disposition/adapter capability come from the explicit lab_catalog.
# concentration reference basis where known (honest; 'unspecified' otherwise)
_REFERENCE_BASIS = {
    "cameron2020.extraction_bdf": "bed-volume (Cameron c_s0 = 118 / phi_s)",
    "grudeva2025.reduced": "grain-volume incl. internal pores (Grudeva) — not comparable to bed-volume",
    "mo2023_2.coupled_bed": "per bed-depth cell (Mo) — reference basis differs from Cameron",
}

# observable name -> (semantic role, short note). Roles trace the PullRun producer semantics.
_OBSERVABLE_ROLES = {
    "pressure_bar": ("prescribed", "constant input, not predicted"),
    "beverage_mass_g": ("prescribed", "target beverage mass, not a model prediction"),
    "mean_flow_g_s": ("derived", "derived from the prescribed beverage target and modeled shot duration"),
    "shot_duration_s": ("simulated", "modeled shot duration"),
    "extracted_mass_g": ("simulated", ""),
    "extraction_yield_pct": ("simulated", ""),
    "tds_pct": ("simulated", ""),
    "first_drip_s": ("unsupported", "saturated-bed configuration does not model wetting/first drip"),
    "first_modeled_solute_arrival_s":
        ("derived", "numerical diagnostic (first modeled cup solute > 0); NOT physical first drip"),
    "composition": ("reference", "single soluble pool; no per-species composition in this model"),
}
_VALID_ROLES = ("prescribed", "derived", "predicted", "simulated", "fitted", "measured", "unsupported",
                "reference")


class IntegrityError(Exception):
    """Raised when a report's embedded integrity hashes do not match a fresh recomputation."""


# ── typed records (frozen; construction-time validation) ────────────────────────────
@dataclasses.dataclass(frozen=True)
class ScenarioRequest:
    preset_id: str
    overrides: dict = dataclasses.field(default_factory=dict)
    domain_policy: str = "warn"
    lens_selection_policy: str = "primary"
    requested_lens_ids: tuple = ()
    reference_selection_policy: str = "interactive_fast"
    requested_reference_runner_ids: tuple = ()

    def __post_init__(self):
        import puckworks.product as prod
        if self.preset_id not in prod.available_pull_presets():
            raise ValueError(f"unknown preset_id {self.preset_id!r}")
        allowed = {f.name for f in dataclasses.fields(prod.PullRecipe)}
        bad = set(self.overrides) - allowed
        if bad:
            raise ValueError(f"unknown recipe override field(s): {sorted(bad)}")
        if self.domain_policy not in DOMAIN_POLICIES:
            raise ValueError(f"domain_policy must be one of {DOMAIN_POLICIES}, got {self.domain_policy!r}")
        if self.lens_selection_policy not in LENS_SELECTION_POLICIES:
            raise ValueError(f"lens_selection_policy must be one of {LENS_SELECTION_POLICIES}, "
                             f"got {self.lens_selection_policy!r}")
        if self.reference_selection_policy not in REFERENCE_SELECTION_POLICIES:
            raise ValueError(f"reference_selection_policy must be one of {REFERENCE_SELECTION_POLICIES}, "
                             f"got {self.reference_selection_policy!r}")
        # canonicalize the lens ids (dedupe preserving first-seen order — a documented rule, so
        # 'Cameron twice' becomes one Cameron and executes once)
        object.__setattr__(self, "requested_lens_ids", _dedupe(self.requested_lens_ids))
        object.__setattr__(self, "requested_reference_runner_ids",
                           tuple(self.requested_reference_runner_ids))
        # unambiguous lens selection: requested ids are meaningful ONLY under the 'selected' policy
        if self.requested_lens_ids and self.lens_selection_policy != "selected":
            raise ValueError("requested_lens_ids requires lens_selection_policy='selected' "
                             "(a non-'selected' policy would silently ignore them)")
        if self.lens_selection_policy == "selected" and not self.requested_lens_ids:
            raise ValueError("lens_selection_policy='selected' requires requested_lens_ids")
        # unambiguous reference selection: requested ids are meaningful ONLY under the 'selected' policy,
        # and 'selected' requires at least one id — never silently ignore either side.
        if self.requested_reference_runner_ids and self.reference_selection_policy != "selected":
            raise ValueError("requested_reference_runner_ids requires reference_selection_policy='selected'"
                             " (a non-'selected' policy would silently ignore them)")
        if self.reference_selection_policy == "selected" and not self.requested_reference_runner_ids:
            raise ValueError("reference_selection_policy='selected' requires requested_reference_runner_ids")


@dataclasses.dataclass(frozen=True)
class ScenarioExecution:
    request: ScenarioRequest
    base_recipe: dict
    effective_recipe: dict
    effective_config: dict
    applied_overrides: dict
    pull_run: dict | None            # back-compat: the PRIMARY (Cameron) lens's raw run, or None
    domain_findings: tuple           # back-compat: the primary lens's domain findings
    run_id: str | None
    effective_domain_policy: str = "warn"
    domain_blocked: bool = False
    domain_block_reason: str = ""
    prepared: object = None          # PreparedScenario (model-independent)
    lens_results: tuple = ()         # per-lens results (adapter-driven execution)


@dataclasses.dataclass(frozen=True)
class BuildProvenance:
    """Build/artifact identity supplied EXPLICITLY by the caller (never derived via git here)."""
    package_version: str | None = None
    source_commit: str | None = None
    workflow_run_id: str | None = None
    wheel_sha256: str | None = None

    def to_dict(self) -> dict:
        return {"package_version": self.package_version, "source_commit": self.source_commit,
                "workflow_run_id": self.workflow_run_id, "wheel_sha256": self.wheel_sha256,
                "artifact_schema_version": ARTIFACT_SCHEMA_VERSION}


@dataclasses.dataclass(frozen=True)
class ComponentLabSpec:
    """One validated capability record per registered component. STATIC (per-request execution state is
    computed separately in build_comparison), so capability is never conflated with what actually ran."""
    component_id: str
    stage: str
    kind: str
    execution_role: str
    module: str
    provenance_class: str
    evidence_strength: str
    n_gates: int
    has_callable_code: bool
    is_runtime_stage: bool
    is_calibration_or_closure: bool
    available_in_env: bool
    optional_dependency: str | None
    code_rights_state: str
    data_rights_state: str
    output_redistribution_state: str
    rights_note: str
    rights_decision_issue: str
    native_runner_capability: str
    common_scenario_adapter_capability: str
    concentration_reference_basis: str
    validity_range: object
    disposition: str
    metadata_complete: bool = True

    def __post_init__(self):
        if self.native_runner_capability not in NATIVE_RUNNER_CAPABILITIES:
            raise ValueError(f"{self.component_id}: native_runner_capability "
                             f"{self.native_runner_capability!r} invalid")
        if self.common_scenario_adapter_capability not in ADAPTER_CAPABILITIES:
            raise ValueError(f"{self.component_id}: common_scenario_adapter_capability "
                             f"{self.common_scenario_adapter_capability!r} invalid")
        if self.disposition not in DISPOSITIONS:
            raise ValueError(f"{self.component_id}: disposition {self.disposition!r} invalid")

    def to_row(self) -> dict:
        """Matrix row dict; keeps back-compat field aliases consumed by governance/tests."""
        d = dataclasses.asdict(self)
        d["rights_state"] = self.code_rights_state
        d["native_runner_state"] = self.native_runner_capability
        d["common_scenario_adapter_state"] = self.common_scenario_adapter_capability
        return d


def _default_provenance() -> BuildProvenance:
    import puckworks
    return BuildProvenance(package_version=puckworks.__version__)   # version string, not a git call


# ── components ──────────────────────────────────────────────────────────────────────
def _components():
    import puckworks
    return list(puckworks.components())


def _optional_dep_available(dep: str) -> bool:
    import importlib.util
    return importlib.util.find_spec(dep) is not None


# ── model-independent scenario preparation (NO producer call) ───────────────────────
def _dedupe(seq) -> tuple:
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return tuple(out)


@dataclasses.dataclass(frozen=True)
class PreparedScenario:
    """A bounded scenario mapped to a base recipe/config with NO model output. It carries no producer
    result, no PullRun, and no lens-specific domain conclusion — those belong to each lens adapter."""
    request: ScenarioRequest
    base_preset: str
    base_recipe: dict
    effective_recipe: dict
    applied_overrides: dict
    effective_config: dict
    shared_quantities: dict          # scenario inputs with units (model-independent)
    scenario_findings: tuple         # scenario-level validation (not a lens's evidence domain)
    source: str
    recipe_obj: object = None        # non-serialized handles for adapters
    config_obj: object = None


def prepare_scenario(request: ScenarioRequest) -> PreparedScenario:
    """Prepare the bounded scenario with EXACT preset identity + override provenance. Calls NO model
    producer and reaches NO Cameron-specific domain conclusion."""
    import puckworks.product as prod
    base_recipe, config = prod.load_pull_preset(request.preset_id)
    base_dict = dataclasses.asdict(base_recipe)
    over = {k: float(v) if isinstance(v, (int, float)) else v for k, v in request.overrides.items()}
    eff_recipe = dataclasses.replace(base_recipe, **over) if over else base_recipe
    applied = {k: {"base": base_dict.get(k), "effective": getattr(eff_recipe, k)} for k in over}
    effective_config = dataclasses.replace(config, domain_policy=request.domain_policy)
    eff_dict = dataclasses.asdict(eff_recipe)
    shared = {
        "dose_g": {"value": eff_dict.get("dose_g"), "unit": "g"},
        "target_beverage_g": {"value": eff_dict.get("target_beverage_g"), "unit": "g"},
        "pressure_bar": {"value": eff_dict.get("pressure_bar"), "unit": "bar"},
        "brew_temperature_c": {"value": eff_dict.get("brew_temperature_c"), "unit": "degC"},
    }
    return PreparedScenario(
        request=request, base_preset=request.preset_id, base_recipe=base_dict, effective_recipe=eff_dict,
        applied_overrides=applied, effective_config=_config_summary(effective_config),
        shared_quantities=shared, scenario_findings=(),
        source=f"puckworks.product.load_pull_preset('{request.preset_id}')"
               + (" with explicit overrides" if applied else " (unmodified)"),
        recipe_obj=eff_recipe, config_obj=effective_config)


# ── lens adapter protocol + registry (the ONLY place a common-scenario producer is called) ──
@dataclasses.dataclass(frozen=True)
class LensAdapterSpec:
    adapter_id: str
    adapter_version: str
    component_id: str
    runtime_class: str
    is_primary: bool
    accepted_scenario_quantities: tuple
    required_fixed_inputs: tuple
    evidence: dict
    evaluate_domain: object          # (prepared) -> tuple[finding dict]
    prepare_inputs: object           # (prepared) -> (recipe_obj, config_obj, mapping dict)
    producer: object                 # (recipe_obj, config_obj) -> raw PullRun dict
    translate_outputs: object        # (raw run) -> {"observables":..., "traces":...}


def _cameron_evaluate_domain(prepared: PreparedScenario) -> tuple:
    import puckworks.product as prod
    return tuple(_finding_to_dict(f) for f in prod.evaluate_domain(prepared.recipe_obj))


def _cameron_prepare_inputs(prepared: PreparedScenario) -> tuple:
    mapping = {"dose_g": "recipe.dose_g", "target_beverage_g": "recipe.target_beverage_g",
               "pressure_bar": "recipe.pressure_bar", "brew_temperature_c": "recipe.brew_temperature_c",
               "note": "the shared scenario recipe IS Cameron's native input (no re-mapping)"}
    return prepared.recipe_obj, prepared.config_obj, mapping


def _cameron_producer(recipe_obj, config_obj) -> dict:
    import puckworks.product as prod
    return prod.pull_run_to_dict(prod.simulate_pull(recipe_obj, config_obj))


def _cameron_translate_outputs(run: dict) -> dict:
    return {"observables": _observable_records(run), "traces": _trace_records(run)}


_CAMERON_ADAPTER = LensAdapterSpec(
    adapter_id="cameron2020_bdf_common_scenario", adapter_version="1", component_id=PRIMARY_LENS_ID,
    runtime_class="interactive-fast", is_primary=True,
    accepted_scenario_quantities=("dose_g", "target_beverage_g", "pressure_bar", "brew_temperature_c"),
    required_fixed_inputs=("coffee_profile", "pressure_profile"),
    evidence={"note": "executed via the existing authoritative producer; no equation is re-implemented"},
    evaluate_domain=_cameron_evaluate_domain, prepare_inputs=_cameron_prepare_inputs,
    producer=_cameron_producer, translate_outputs=_cameron_translate_outputs)

# component_id -> adapter. The registry is explicit; adding an adapter never changes `primary` behavior.
ADAPTERS: dict = {PRIMARY_LENS_ID: _CAMERON_ADAPTER}


def _adapter_for(component_id: str) -> LensAdapterSpec | None:
    return ADAPTERS.get(component_id)


def lens_readiness(component_id: str) -> tuple:
    """(readiness_state, ready_bool, reason). READY only when an adapter exists AND the component's code
    is not rights-blocked for local execution."""
    from puckworks import rights
    if not any(c.name == component_id for c in _components()):
        return "NOT_APPLICABLE", False, "not a registered component"
    if rights.is_code_rights_blocked(component_id):
        return "RIGHTS_BLOCKED", False, "code rights blocked (see rights registry / #73)"
    if _adapter_for(component_id) is None:
        return "NO_ADAPTER", False, "no common-scenario adapter for this component"
    return "READY", True, ""


def resolve_lens_selection(request: ScenarioRequest) -> list:
    """The component ids to CONSIDER as common-scenario lenses, per the finite selection policy. An
    unknown id (not a registered component) raises; a registered-but-not-ready id is still considered so
    it can be surfaced as declined. Adding a future adapter never changes `primary`."""
    policy = request.lens_selection_policy
    registered = {c.name for c in _components()}
    if policy == "none":
        return []
    if policy == "primary":
        return [PRIMARY_LENS_ID]
    if policy == "all_ready":
        return sorted(cid for cid in ADAPTERS if lens_readiness(cid)[1])
    # 'selected'
    unknown = [i for i in request.requested_lens_ids if i not in registered]
    if unknown:
        raise ValueError(f"unknown requested lens id(s): {sorted(unknown)} (not registered components)")
    return list(request.requested_lens_ids)


def _decide_domain_block(findings: tuple, domain_policy: str) -> tuple:
    """Mirror the producer's own gate: REJECTED always blocks; WARNING blocks only under strict."""
    rejected = [f for f in findings if f["status"] == "rejected"]
    warned = [f for f in findings if f["status"] == "warning"]
    if rejected:
        return True, "rejected input: " + ", ".join(f["field"] for f in rejected)
    if warned and domain_policy == "strict":
        return True, "strict domain policy: out-of-range " + ", ".join(f["field"] for f in warned)
    return False, ""


def execute_lenses(prepared: PreparedScenario) -> list:
    """Execute ONLY the selected, ready, in-domain common-scenario lenses. The producer of each adapter is
    the sole place a common-scenario model runs; it is never called for a declined lens. One lens failing
    never erases another's result."""
    from puckworks import rights
    request = prepared.request
    considered = resolve_lens_selection(request)
    results = []
    for cid in considered:
        readiness_state, ready, reason = lens_readiness(cid)
        rights_decision = rights.may_execute_locally(cid).to_dict()
        base = {"component_id": cid, "adapter_id": None, "requested_state": "REQUESTED_BUT_NOT_EXECUTABLE",
                "adapter_readiness": readiness_state, "rights_use_decision": rights_decision,
                "domain_findings": [], "producer_invoked": False, "status": "declined",
                "input_mapping": {}, "observables": [], "traces": [], "decline_reason": reason}
        if not ready:
            results.append(base)
            continue
        adapter = _adapter_for(cid)
        base["adapter_id"] = adapter.adapter_id
        findings = adapter.evaluate_domain(prepared)
        base["domain_findings"] = list(findings)
        blocked, block_reason = _decide_domain_block(findings, request.domain_policy)
        if blocked:
            base["adapter_readiness"] = "OUTSIDE_DOMAIN"
            base["decline_reason"] = block_reason
            results.append(base)
            continue
        try:
            recipe_obj, config_obj, mapping = adapter.prepare_inputs(prepared)
            raw = adapter.producer(recipe_obj, config_obj)          # the ONLY common-scenario producer call
            outputs = adapter.translate_outputs(raw)
            results.append({**base, "requested_state": "EXECUTED", "producer_invoked": True,
                            "status": "executed", "input_mapping": mapping,
                            "observables": outputs["observables"], "traces": outputs["traces"],
                            "adapter": f"{adapter.adapter_id}({request.preset_id})",
                            "evidence_note": adapter.evidence.get("note", ""),
                            "warnings": raw.get("warnings", []), "raw_run": raw,
                            "disposition": "COMMON_SCENARIO_READY"})
        except Exception as exc:                                    # isolate failure
            results.append({**base, "requested_state": "FAILED", "producer_invoked": True,
                            "status": "FAILED", "decline_reason": f"{type(exc).__name__}: {exc}"})
    return results


# ── scenario execution (compat entry point: prepare + execute selected lenses) ──────
def execute_scenario(request: ScenarioRequest) -> ScenarioExecution:
    """Prepare the bounded scenario and execute ONLY the selected common-scenario lenses (default policy
    `primary` = Cameron). The producer is NOT called for a lens that is not selected, not ready, or
    domain-blocked. Returns a ScenarioExecution carrying the prepared scenario and the per-lens results;
    `pull_run` is the primary lens's raw run for back-compat (None if the primary did not execute)."""
    prepared = prepare_scenario(request)
    lens_results = execute_lenses(prepared)
    primary = next((r for r in lens_results if r["component_id"] == PRIMARY_LENS_ID), None)
    primary_executed = bool(primary and primary["status"] == "executed")
    run = primary["raw_run"] if primary_executed else None
    # back-compat domain fields reflect the PRIMARY lens (Cameron) when it was considered
    dom_findings = tuple(primary["domain_findings"]) if primary else ()
    blocked = bool(primary and primary["adapter_readiness"] == "OUTSIDE_DOMAIN")
    block_reason = primary["decline_reason"] if blocked else ""
    return ScenarioExecution(
        request=request, base_recipe=prepared.base_recipe, effective_recipe=prepared.effective_recipe,
        effective_config=prepared.effective_config, applied_overrides=prepared.applied_overrides,
        pull_run=run, domain_findings=dom_findings, run_id=(run or {}).get("run_id"),
        effective_domain_policy=request.domain_policy, domain_blocked=blocked,
        domain_block_reason=block_reason, prepared=prepared, lens_results=tuple(lens_results))


def _config_summary(config) -> dict:
    return {"config_id": getattr(config, "config_id", None),
            "config_version": getattr(config, "config_version", None),
            "domain_policy": getattr(config, "domain_policy", None)}


def _finding_to_dict(f) -> dict:
    if isinstance(f, dict):
        return f
    status = getattr(f, "status", "")
    status = getattr(status, "value", status)
    return {"status": str(status), "field": getattr(f, "field", ""),
            "plain_explanation": getattr(f, "plain_explanation", ""),
            "technical_reason": getattr(f, "technical_reason", ""),
            "supported_range": getattr(f, "supported_range", ""),
            "supplied_value": getattr(f, "supplied_value", None)}


def run_scenario(preset_id: str = _DEFAULT_PRESET, *, dose_g=None, target_beverage_g=None,
                 pressure_bar=None, brew_temperature_c=None) -> dict | None:
    """DEPRECATED compatibility wrapper. Returns the bare PullRun dict for a bounded scenario (or None if
    the request is domain-blocked and the producer did not run).

    A bare PullRun dict cannot carry preset identity, so DO NOT feed it back to build_comparison for a
    non-default preset — use execute_scenario()/build_comparison(execution) instead."""
    over = {k: float(v) for k, v in dict(
        dose_g=dose_g, target_beverage_g=target_beverage_g, pressure_bar=pressure_bar,
        brew_temperature_c=brew_temperature_c).items() if v is not None}
    return execute_scenario(ScenarioRequest(preset_id=preset_id, overrides=over)).pull_run


# ── capability / rights matrix (STATIC) ─────────────────────────────────────────────
def _lab_spec(comp) -> ComponentLabSpec:
    name = getattr(comp, "name", None)
    role = getattr(comp, "execution_role", "") or ""
    stage = getattr(comp, "stage", "") or ""
    kind = getattr(comp, "kind", "") or ""
    # honest METADATA_INCOMPLETE fallback rather than an invented capability
    metadata_complete = bool(name) and bool(role) and bool(getattr(comp, "module", ""))
    from puckworks import rights
    rights_rec = rights.rights_record(name or "")
    rights_blocked = rights_rec.is_code_blocked

    has_callable = role in ("runtime", "calibration")
    is_runtime_stage = role == "runtime"
    is_calibration = role == "calibration"
    opt_dep = _OPTIONAL_DEPENDENCY.get(name)
    available_in_env = (opt_dep is None) or _optional_dep_available(opt_dep)

    from puckworks.product import lab_catalog, lab_runners
    has_native_runner = lab_runners.has_runner(name)

    # DISPOSITION + adapter capability come from the EXPLICIT committed catalog — never a stage/kind/role
    # substring heuristic. A component absent from the catalog (or lacking registry metadata) is an
    # honest METADATA_INCOMPLETE, never an invented capability.
    if not metadata_complete or name not in lab_catalog._CAPABILITY:
        runner_cap, adapter_cap, disposition = "NOT_APPLICABLE", "NOT_APPLICABLE", "METADATA_INCOMPLETE"
        metadata_complete = False
    else:
        entry = lab_catalog.catalog_entry(comp)
        disposition = entry.disposition
        adapter_cap = entry.adapter_capability
        # runner capability is an AUTHORITATIVE fact (registration + rights + optional dependency), not a
        # heuristic: the runner either exists, is rights-blocked, needs a missing dependency, or is absent.
        if rights_blocked:
            runner_cap = "RIGHTS_BLOCKED"
        elif name in ADAPTERS:                          # the common-scenario lens has no separate runner
            runner_cap = "NOT_APPLICABLE"
        elif has_native_runner:
            runner_cap = "AVAILABLE"
        elif opt_dep and not available_in_env:
            runner_cap = "OPTIONAL_DEPENDENCY_UNAVAILABLE"
            disposition = "SKIPPED_OPTIONAL_DEPENDENCY"  # env overlay of the committed catalog base
        else:
            runner_cap = "NOT_IMPLEMENTED"

    return ComponentLabSpec(
        component_id=name or "<unknown>", stage=stage, kind=kind, execution_role=role,
        module=getattr(comp, "module", ""), provenance_class=getattr(comp, "provenance_class", ""),
        evidence_strength=getattr(comp, "evidence_strength", ""), n_gates=len(getattr(comp, "gates", [])),
        has_callable_code=has_callable, is_runtime_stage=is_runtime_stage,
        is_calibration_or_closure=is_calibration, available_in_env=available_in_env,
        optional_dependency=opt_dep, code_rights_state=rights_rec.code_rights_state,
        data_rights_state=rights_rec.data_rights_state,
        output_redistribution_state=rights_rec.output_redistribution_state,
        rights_note=rights_rec.rights_note, rights_decision_issue=rights_rec.decision_issue,
        native_runner_capability=runner_cap, common_scenario_adapter_capability=adapter_cap,
        concentration_reference_basis=_REFERENCE_BASIS.get(name, "unspecified"),
        validity_range=getattr(comp, "valid_range", None), disposition=disposition,
        metadata_complete=metadata_complete)


def build_matrix(execution: ScenarioExecution) -> list:
    """Every registered component -> exactly one validated Lab capability record (never a substring
    heuristic on the run). We read the run's executed coverage only to sanity-check identity, never to
    classify. Deterministic ordering."""
    run = execution.pull_run or {}
    _ = {c["component_id"] for c in run.get("coverage", []) if c.get("executed")}  # identity only
    rows = [_lab_spec(c).to_row() for c in _components()]
    seen = {r["component_id"] for r in rows}
    assert len(seen) == len(rows), "duplicate Lab capability record"
    for r in rows:
        assert r["disposition"] in DISPOSITIONS and r["native_runner_state"] in NATIVE_RUNNER_CAPABILITIES
    rows.sort(key=lambda r: r["component_id"])
    return rows


# ── common-scenario lens selection (requested_lens_ids actually controls execution) ──
def _lens_selection(execution: ScenarioExecution) -> tuple[list, list]:
    """(selection_records, executed_lens_ids) derived from the adapter-driven lens_results. Executed,
    declined, and failed lenses are all surfaced honestly; nothing is silently discarded."""
    records, executed = [], []
    for r in execution.lens_results:
        state = "EXECUTED" if r["status"] == "executed" else (
            "FAILED" if r["status"] == "FAILED" else "REQUESTED_BUT_NOT_EXECUTABLE")
        records.append({"component_id": r["component_id"], "lens_request_state": state,
                        "adapter_readiness": r["adapter_readiness"], "reason": r.get("decline_reason", "")})
        if state == "EXECUTED":
            executed.append(r["component_id"])
    return records, executed


# ── executed lens (correct observable roles) ────────────────────────────────────────
def _observable_records(run: dict) -> list:
    out = []
    for key, o in sorted(run.get("final_observables", {}).items()):
        if not isinstance(o, dict):
            continue
        role, default_note = _OBSERVABLE_ROLES.get(key, ("derived", ""))
        if o.get("status") == "unavailable":
            role = "unsupported"
        note = o.get("note") or o.get("reason") or default_note
        rec = {"name": key, "value": o.get("value"), "unit": o.get("unit"), "role": role,
               "status": o.get("status", "available"), "note": note}
        if key == "first_modeled_solute_arrival_s":
            rec["is_physical_first_drip"] = False
            rec["semantic_class"] = "diagnostic"
        out.append(rec)
    return out


def _trace_records(run: dict) -> list:
    out = []
    for t in run.get("traces", []):
        series = [{"series_id": s.get("series_id"), "label": s.get("label"), "unit": s.get("unit"),
                   "role": s.get("role"), "values": s.get("values", []), "caveat": s.get("caveat", "")}
                  for s in t.get("series", [])]
        out.append({"trace_id": t.get("trace_id"), "component_id": t.get("component_id"),
                    "observable": t.get("axis_label"), "axis_label": t.get("axis_label"),
                    "axis_unit": t.get("axis_unit"), "axis_values": t.get("axis_values", []),
                    "series": series, "evidence_badge": t.get("evidence_badge"),
                    "evidence_strength": t.get("evidence_strength"),
                    "fidelity_ceiling": t.get("fidelity_ceiling"), "caveat": t.get("caveat", "")})
    return out


def _executed_lens_view(r: dict) -> dict:
    """The report view of an executed lens result (the private raw_run is dropped from the artifact)."""
    return {
        "component_id": r["component_id"], "adapter": r.get("adapter"),
        "status": "executed", "disposition": "COMMON_SCENARIO_READY",
        "observables": r["observables"], "traces": r["traces"],
        "domain_findings": list(r["domain_findings"]), "warnings": r.get("warnings", []),
        "input_mapping": r.get("input_mapping", {}),
        "evidence_note": r.get("evidence_note", ""),
    }


def _executed_lenses(execution: ScenarioExecution, executed_ids: list) -> list:
    """The report view of every lens that actually executed (deterministic order)."""
    return [_executed_lens_view(r) for r in execution.lens_results if r["status"] == "executed"]


# ── native reference selection (resolves COMPONENTS, not just runner registrations) ──
def _resolve_reference_component_ids(request: ScenarioRequest) -> list:
    """Component ids to resolve as native references. Under 'selected' an id that is a registered
    component but has no runner is RESOLVED (to RUNNER_NOT_IMPLEMENTED), not rejected; only an id absent
    from the registry is 'unknown' and raises."""
    from puckworks.product import lab_runners
    policy = request.reference_selection_policy
    if policy == "none":
        return []
    if policy == "interactive_fast":
        return list(lab_runners.INTERACTIVE_FAST)
    registered = {c.name for c in _components()}
    unknown = [i for i in request.requested_reference_runner_ids if i not in registered]
    if unknown:
        raise ValueError(f"unknown reference id(s): {sorted(unknown)} (not registered components)")
    return list(request.requested_reference_runner_ids)


def _reference_resolution_state(cid: str, ran: dict | None) -> str:
    """Resolve a requested reference COMPONENT to a finite state (never a silent drop)."""
    from puckworks import rights
    from puckworks.product import lab_runners
    if ran is not None:
        return "EXECUTED" if ran.get("status") == "executed" else "FAILED"
    if rights.is_code_rights_blocked(cid):
        return "RIGHTS_BLOCKED"
    if not lab_runners.has_runner(cid):
        dep = _OPTIONAL_DEPENDENCY.get(cid)
        if dep and not _optional_dep_available(dep):
            return "OPTIONAL_DEPENDENCY_UNAVAILABLE"
        return "RUNNER_NOT_IMPLEMENTED"
    return "NOT_APPLICABLE"


def _reference_selection(execution: ScenarioExecution) -> tuple[list, list]:
    """(selection_records, executed_results). Every resolved COMPONENT gets a finite resolution state;
    executed_results are the actually-run native reference cases. A rights-blocked component is never
    executed; a registered component with no runner is RUNNER_NOT_IMPLEMENTED, not 'unknown'."""
    from puckworks import rights
    from puckworks.product import lab_runners
    resolved = _resolve_reference_component_ids(execution.request)
    # only components that HAVE a runner and are not rights-blocked are actually executed
    to_run = [c for c in resolved if lab_runners.has_runner(c) and not rights.is_code_rights_blocked(c)]
    executed = lab_runners.run_selected(to_run) if to_run else []
    by_id = {r["component_id"]: r for r in executed}
    records = []
    for cid in sorted(set(resolved)):
        state = _reference_resolution_state(cid, by_id.get(cid))
        records.append({"component_id": cid, "native_runner_execution_state": state,
                        "reference_selection_policy": execution.request.reference_selection_policy})
    return records, executed


# ── reference-suite capability coverage (STATIC; env-dependent -> capability snapshot) ──
def _reference_suite_coverage(matrix: list) -> list:
    out = []
    for row in matrix:
        cap = row["native_runner_capability"]
        if cap == "AVAILABLE":
            note = "native reference runner available; execution is per-request (see reference_selection)"
        elif cap == "RIGHTS_BLOCKED":
            note = row["rights_note"] or "rights-blocked; not executed"
        elif cap == "OPTIONAL_DEPENDENCY_UNAVAILABLE":
            note = f"optional dependency '{row['optional_dependency']}' unavailable; a skip is not a pass"
        elif cap == "NOT_APPLICABLE":
            note = "common-scenario lens (not a separate native reference runner)" \
                if row["component_id"] in ADAPTERS else "no native reference runner applies"
        else:
            note = "Native reference runner not yet implemented; no result was generated."
        out.append({"component_id": row["component_id"], "runner_state": cap,
                    "native_runner_capability": cap, "note": note})
    return out


# ── comparison assembly + integrity ─────────────────────────────────────────────────
def build_comparison(execution: ScenarioExecution, *, provenance: BuildProvenance | None = None) -> dict:
    if isinstance(execution, dict):                       # guard the old identity-losing call shape
        raise TypeError("build_comparison now requires a ScenarioExecution (use execute_scenario); a "
                        "bare PullRun dict cannot carry preset identity")
    prov = provenance or _default_provenance()
    matrix = build_matrix(execution)
    by_disp: dict[str, int] = {}
    for r in matrix:
        by_disp[r["disposition"]] = by_disp.get(r["disposition"], 0) + 1

    lens_records, executed_lens_ids = _lens_selection(execution)
    executed_lenses = _executed_lenses(execution, executed_lens_ids)
    ref_records, executed_refs = _reference_selection(execution)
    req = execution.request

    scenario = {
        "scenario_id": req.preset_id, "preset_id": req.preset_id,
        "title": f"Guided Pull Laboratory common scenario ({req.preset_id}); one machine/coffee",
        "base_recipe": execution.base_recipe, "effective_recipe": execution.effective_recipe,
        "applied_overrides": execution.applied_overrides,
        "config": execution.effective_config, "domain_policy": execution.effective_domain_policy,
        "source": f"puckworks.product.load_pull_preset('{req.preset_id}')"
                  + (" with explicit overrides" if execution.applied_overrides else " (unmodified)"),
        "fixed_assumptions": ["single soluble pool", "saturated bed (no wetting/first drip)",
                              "prescribed constant pressure"],
        "scope": "one bounded scenario, one machine/coffee; grinder dial is non-portable",
        "nonportable_grinder_warning": "a grinder dial is not a universal particle size",
    }
    request_echo = {
        "preset_id": req.preset_id, "domain_policy": req.domain_policy,
        "effective_domain_policy": execution.effective_domain_policy,
        "lens_selection_policy": req.lens_selection_policy,
        "requested_lens_ids": list(req.requested_lens_ids),
        "reference_selection_policy": req.reference_selection_policy,
        "requested_reference_runner_ids": list(req.requested_reference_runner_ids),
    }
    # per-lens execution record (capability vs what actually ran, with each lens's OWN domain)
    lens_execution = [{
        "component_id": r["component_id"], "adapter_id": r["adapter_id"],
        "requested_state": r["requested_state"], "adapter_readiness": r["adapter_readiness"],
        "producer_invoked": r["producer_invoked"], "status": r["status"],
        "rights_use_decision": r["rights_use_decision"],
        "domain_finding_count": len(r["domain_findings"]),
        "decline_reason": r.get("decline_reason", ""), "input_mapping": r.get("input_mapping", {}),
    } for r in execution.lens_results]
    producer_invocations = sum(1 for r in execution.lens_results if r["producer_invoked"])
    # domain block reflects the PRIMARY lens (Cameron) when it was considered; per-lens domain lives above
    domain = {
        "policy": req.domain_policy, "effective_policy": execution.effective_domain_policy,
        "primary_lens": PRIMARY_LENS_ID,
        "blocked": execution.domain_blocked, "block_reason": execution.domain_block_reason,
        "producer_executed": execution.pull_run is not None,
        "rejected_count": sum(1 for f in execution.domain_findings if f["status"] == "rejected"),
        "warning_count": sum(1 for f in execution.domain_findings if f["status"] == "warning"),
        "findings": list(execution.domain_findings),
    }
    # ── env-dependent capability snapshot (excluded from the scientific hash) ──
    capability_snapshot = {
        "component_matrix": matrix,
        "reference_suite_coverage": _reference_suite_coverage(matrix),
        "excluded_or_dispositioned": [
            {"component_id": r["component_id"], "disposition": r["disposition"],
             "rights_state": r["rights_state"],
             "reason": r["rights_note"] or r["native_runner_capability"]}
            for r in matrix if r["disposition"] != "COMMON_SCENARIO_READY"],
        "dispositions": dict(sorted(by_disp.items())),
        "optional_dependency_availability": {
            cid: _optional_dep_available(dep) for cid, dep in sorted(_OPTIONAL_DEPENDENCY.items())},
        "environment_fingerprint": {
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform()},
    }
    report = {
        "schema_version": SCHEMA_VERSION,
        "report": "puckworks-guided-pull-laboratory",
        "scenario": scenario,
        "request": request_echo,
        "domain": domain,
        "counts": {"components": len(matrix),
                   "executed_common_scenario_lenses": len(executed_lenses),
                   "common_scenario_producer_invocations": producer_invocations,
                   "executed_native_references": sum(1 for r in executed_refs
                                                      if r.get("status") == "executed"),
                   "failed_native_references": sum(1 for r in executed_refs
                                                   if r.get("status") == "FAILED")},
        "lens_selection": lens_records,
        "lens_execution": lens_execution,
        "executed_lenses": executed_lenses,
        "reference_selection": ref_records,
        "executed_reference_results": executed_refs,
        "what_this_does_not_prove": WHAT_THIS_DOES_NOT_PROVE,
        "fidelity_ceiling": "One bounded scenario on one machine/coffee; one executed extraction lens; "
                            "the rest are independent lenses / native references. Not a validated "
                            "multi-model simulation, not a digital twin, not a best recipe.",
        "capability_snapshot": capability_snapshot,
        "provenance": prov.to_dict(),
    }
    return attach_integrity(report)


# ── layered integrity (each hash recomputed on demand; NaN/Inf rejected) ─────────────
def _reject_nonfinite(obj, path="$") -> None:
    if isinstance(obj, float):
        if obj != obj or obj in (float("inf"), float("-inf")):
            raise ValueError(f"non-finite float at {path}: {obj!r} (NaN/Infinity is never serialized)")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _reject_nonfinite(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _reject_nonfinite(v, f"{path}[{i}]")


def _canonical(obj: dict) -> str:
    _reject_nonfinite(obj)
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def _sha256_canonical(obj: dict) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


def _scientific_payload(report: dict) -> dict:
    """The science: free of build provenance, integrity fields, AND the env-dependent capability
    snapshot — so the hash is stable across build identity, Python version, and optional-dependency
    installation (installing Taichi does not change it for a Cameron-only request)."""
    r = json.loads(json.dumps(report))
    for k in ("provenance", "integrity", "capability_snapshot"):
        r.pop(k, None)
    return r


def _capability_payload(report: dict) -> dict:
    return json.loads(json.dumps(report.get("capability_snapshot", {})))


def _artifact_payload(report: dict) -> dict:
    """The full artifact (incl. provenance + the other two hashes) minus its own artifact hash."""
    r = json.loads(json.dumps(report))
    r.get("integrity", {}).pop("artifact_sha256", None)
    return r


def compute_scientific_result_sha256(report: dict) -> str:
    return _sha256_canonical(_scientific_payload(report))


def compute_capability_snapshot_sha256(report: dict) -> str:
    return _sha256_canonical(_capability_payload(report))


def compute_artifact_sha256(report: dict) -> str:
    return _sha256_canonical(_artifact_payload(report))


def attach_integrity(report: dict) -> dict:
    """Compute and embed all three integrity layers in dependency order (scientific + capability first,
    then the artifact hash which covers them). Returns the same report."""
    integ = report.setdefault("integrity", {})
    integ.pop("artifact_sha256", None)
    integ["scientific_payload_sha256"] = compute_scientific_result_sha256(report)
    integ["capability_snapshot_sha256"] = compute_capability_snapshot_sha256(report)
    integ["artifact_sha256"] = compute_artifact_sha256(report)
    return report


def verify_integrity(report: dict, *, strict: bool = False) -> dict:
    """Recompute every layer from the report's own content and compare to the embedded hashes. Returns
    a structured result; with strict=True, raises IntegrityError on any mismatch. Never trusts the
    embedded value — it is always recomputed."""
    embedded = report.get("integrity", {})
    checks = {
        "scientific_payload_sha256": (embedded.get("scientific_payload_sha256"),
                                      compute_scientific_result_sha256(report)),
        "capability_snapshot_sha256": (embedded.get("capability_snapshot_sha256"),
                                       compute_capability_snapshot_sha256(report)),
        "artifact_sha256": (embedded.get("artifact_sha256"), compute_artifact_sha256(report)),
    }
    mismatches = [{"layer": k, "embedded": got, "recomputed": exp}
                  for k, (got, exp) in checks.items() if got != exp]
    result = {"ok": not mismatches, "mismatches": mismatches,
              "checked": {k: {"embedded": got, "recomputed": exp} for k, (got, exp) in checks.items()}}
    if strict and mismatches:
        raise IntegrityError("integrity mismatch: " + ", ".join(m["layer"] for m in mismatches))
    return result


# public integrity API (back-compat names kept)
def scientific_payload(report: dict) -> dict:
    return _scientific_payload(report)


def scientific_json(report: dict) -> str:
    return _canonical(_scientific_payload(report))


def scientific_sha256(report: dict) -> str:
    return report.get("integrity", {}).get("scientific_payload_sha256") \
        or compute_scientific_result_sha256(report)


def capability_snapshot_sha256(report: dict) -> str:
    return report.get("integrity", {}).get("capability_snapshot_sha256") \
        or compute_capability_snapshot_sha256(report)


def artifact_json(report: dict) -> str:
    """The FULL downloadable artifact JSON (carries build provenance + all integrity hashes)."""
    return _canonical(report)


def artifact_sha256(report: dict) -> str:
    return report.get("integrity", {}).get("artifact_sha256") or compute_artifact_sha256(report)


# back-compat: the batch/UI download the FULL artifact (not a provenance-stripped payload)
def canonical_json(report: dict) -> str:
    return artifact_json(report)


# ── shared plotting-data layer (used by Streamlit + batch; no science recalculated here) ──
def _unit_slug(unit) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "_", str(unit or "none").lower()).strip("_") or "none"


def assert_unit_safe(panel: dict) -> dict:
    """A single ordinary y-axis carries exactly one unit. Overlaying incompatible units (bar/g/s/g/%/
    kg/m^3) on one axis is physically meaningless — reject it rather than draw it."""
    units = {s["unit"] for s in panel.get("series", [])}
    if len(units) > 1:
        raise ValueError(f"panel {panel.get('panel_id')!r} mixes units {sorted(map(str, units))} on one "
                         f"axis; split by unit before plotting")
    return panel


def render_data(report: dict) -> list:
    """Return **unit-safe** plot-ready panels straight from the artifact's trace data. Each source trace
    is split into one panel PER UNIT, so a single y-axis never mixes incompatible units; same-unit series
    legitimately share an axis. Units + roles are preserved (no science recalculated here). Panels are
    emitted in a deterministic (trace, unit) order."""
    panels = []
    for lens in report["executed_lenses"]:
        for t in lens["traces"]:
            by_unit: dict = {}
            order: list = []
            for s in t["series"]:
                if not s.get("values"):
                    continue
                u = s.get("unit")
                if u not in by_unit:
                    by_unit[u] = []
                    order.append(u)
                by_unit[u].append(s)
            for u in order:
                series = by_unit[u]
                panel = {
                    "panel_id": f"{t['trace_id']}::{_unit_slug(u)}", "trace_id": t["trace_id"],
                    "component_id": t["component_id"], "unit": u,
                    "title": f"{t['component_id']}: {t['observable']} [{u}]",
                    "x_label": f"{t['axis_label']} ({t['axis_unit']})",
                    "y_label": f"{t['observable']} ({u})", "x": t["axis_values"],
                    "series": [{"label": s["label"] or s["series_id"], "unit": s["unit"],
                                "role": s["role"], "y": s["values"]} for s in series],
                    "evidence_badge": t["evidence_badge"], "fidelity_ceiling": t["fidelity_ceiling"],
                }
                panels.append(assert_unit_safe(panel))
    return panels


def panel_inventory(report: dict) -> list:
    """A compact (panel_id, unit, series count) inventory of the unit-safe panels — for coverage
    reporting (e.g. the before/after figure inventory)."""
    return [{"panel_id": p["panel_id"], "component_id": p["component_id"], "unit": p["unit"],
             "n_series": len(p["series"]), "roles": sorted({s["role"] for s in p["series"]})}
            for p in render_data(report)]


def render_markdown(report: dict) -> str:
    c = report["counts"]; sc = report["scenario"]; cap = report["capability_snapshot"]
    dom = report["domain"]
    lines = [
        "# Guided Pull Laboratory — model-lens comparison", "",
        "_Independent model lenses over one bounded scenario, plus a component reference suite. "
        "**Not** a validated digital twin; competing mechanisms are never summed or averaged._", "",
        f"- scenario: **{sc['scenario_id']}** (preset `{sc['preset_id']}`, "
        f"{'overridden' if sc['applied_overrides'] else 'unmodified'})",
        f"- domain policy: **{dom['effective_policy']}** · producer executed: "
        f"**{dom['producer_executed']}**"
        + (f" · BLOCKED: {dom['block_reason']}" if dom["blocked"] else ""),
        f"- registered components: **{c['components']}** · executed common-scenario lenses: "
        f"**{c['executed_common_scenario_lenses']}** · executed native references: "
        f"**{c['executed_native_references']}**", "",
        "## Coverage by disposition", "",
    ]
    for k, v in cap["dispositions"].items():
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Executed common-scenario lens", ""]
    if report["executed_lenses"]:
        for lens in report["executed_lenses"]:
            lines.append(f"### `{lens['component_id']}` — {lens['status']} ({lens['adapter']})")
            lines.append("")
            lines.append("| observable | value | unit | role | note |")
            lines.append("|---|---|---|---|---|")
            for o in lens["observables"]:
                lines.append(f"| {o['name']} | {o['value']} | {o['unit'] or ''} | {o['role']} | "
                             f"{(o['note'] or '')[:60]} |")
            lines.append("")
    else:
        lines += ["_No common-scenario lens executed for this request._", ""]
    lines += ["## Lens selection (requested vs executable)", ""]
    for ls in report["lens_selection"]:
        lines.append(f"- `{ls['component_id']}` — **{ls['lens_request_state']}**"
                     + (f": {ls['reason']}" if ls["reason"] else ""))
    lines += ["", "## Excluded / dispositioned components (honest, not hidden)", ""]
    for e in cap["excluded_or_dispositioned"]:
        lines.append(f"- `{e['component_id']}` — **{e['disposition']}** "
                     f"({e['rights_state']}): {e['reason']}")
    lines += ["", "## Executed native reference results", ""]
    if report["executed_reference_results"]:
        for r in report["executed_reference_results"]:
            lines.append(f"- `{r['component_id']}` — {r['status']} ({r['label']})")
    else:
        lines.append("_None executed._")
    lines += ["", "## Reference-runner coverage", ""]
    for r in cap["reference_suite_coverage"]:
        lines.append(f"- `{r['component_id']}` — {r['runner_state']}: {r['note']}")
    lines += ["", "## What this does not prove", ""]
    lines += [f"- {s}" for s in report["what_this_does_not_prove"]]
    lines += ["", f"**Fidelity ceiling.** {report['fidelity_ceiling']}",
              "", "## Provenance / integrity", "",
              f"- package_version: `{report['provenance'].get('package_version')}`",
              f"- source_commit: `{report['provenance'].get('source_commit')}`",
              f"- workflow_run_id: `{report['provenance'].get('workflow_run_id')}`",
              f"- wheel_sha256: `{report['provenance'].get('wheel_sha256')}`",
              f"- scientific_payload_sha256: `{report['integrity']['scientific_payload_sha256']}`",
              f"- capability_snapshot_sha256: `{report['integrity']['capability_snapshot_sha256']}`",
              f"- artifact_sha256: `{report['integrity']['artifact_sha256']}`", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="puckworks.product.lab", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("matrix", "compare"):
        s = sub.add_parser(name)
        s.add_argument("--preset", default=_DEFAULT_PRESET)
        s.add_argument("--domain-policy", choices=list(DOMAIN_POLICIES), default="warn")
        s.add_argument("--references", choices=list(REFERENCE_SELECTION_POLICIES),
                       default="interactive_fast")
        s.add_argument("--format", choices=["md", "json"], default="md")
        s.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    execution = execute_scenario(ScenarioRequest(
        preset_id=args.preset, domain_policy=args.domain_policy,
        reference_selection_policy=args.references))
    if args.cmd == "matrix":
        matrix = build_matrix(execution)
        text = (json.dumps(matrix, indent=2, sort_keys=True) + "\n" if args.format == "json"
                else "\n".join(f"{r['component_id']:34} {r['disposition']:28} "
                               f"{r['native_runner_state']:26} {r['rights_state']}"
                               for r in matrix) + "\n")
    else:
        report = build_comparison(execution)
        text = artifact_json(report) if args.format == "json" else render_markdown(report)
    if args.out:
        from pathlib import Path
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
