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

SCHEMA_VERSION = 4
ARTIFACT_SCHEMA_VERSION = 1
_DEFAULT_PRESET = "pv19_named"

# ── finite vocabularies ────────────────────────────────────────────────────────────
DOMAIN_POLICIES = ("warn", "strict")
REFERENCE_SELECTION_POLICIES = ("none", "interactive_fast", "selected")

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
_COMMON_SCENARIO_LENSES = {"cameron2020.extraction_bdf": "puckworks.product.simulate_pull"}
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
        if self.reference_selection_policy not in REFERENCE_SELECTION_POLICIES:
            raise ValueError(f"reference_selection_policy must be one of {REFERENCE_SELECTION_POLICIES}, "
                             f"got {self.reference_selection_policy!r}")
        # normalize the request tuples (deterministic, hashable) without dropping anything silently
        object.__setattr__(self, "requested_lens_ids", tuple(self.requested_lens_ids))
        object.__setattr__(self, "requested_reference_runner_ids",
                           tuple(self.requested_reference_runner_ids))
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
    pull_run: dict | None
    domain_findings: tuple
    run_id: str | None
    effective_domain_policy: str = "warn"
    domain_blocked: bool = False
    domain_block_reason: str = ""


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


# ── scenario execution (exact identity + override provenance + operational domain policy) ──
def execute_scenario(request: ScenarioRequest) -> ScenarioExecution:
    """Run the authoritative producer for a bounded scenario, preserving the EXACT preset identity and
    the applied overrides. The effective config carries the REQUEST's domain policy; the domain is
    evaluated once, up front, and the producer is NOT called when the request is domain-blocked."""
    import puckworks.product as prod
    base_recipe, config = prod.load_pull_preset(request.preset_id)
    base_dict = dataclasses.asdict(base_recipe)
    over = {k: float(v) if isinstance(v, (int, float)) else v for k, v in request.overrides.items()}
    eff_recipe = dataclasses.replace(base_recipe, **over) if over else base_recipe
    applied = {k: {"base": base_dict.get(k), "effective": getattr(eff_recipe, k)} for k in over}

    # the effective config's domain policy IS the request's policy (operational, not cosmetic)
    effective_config = dataclasses.replace(config, domain_policy=request.domain_policy)
    findings = tuple(_finding_to_dict(f) for f in prod.evaluate_domain(eff_recipe))
    rejected = [f for f in findings if f["status"] == "rejected"]
    warned = [f for f in findings if f["status"] == "warning"]
    # mirror the producer's own gate: REJECTED always blocks; WARNING blocks only under strict.
    blocked, reason = False, ""
    if rejected:
        blocked = True
        reason = "rejected input: " + ", ".join(f["field"] for f in rejected)
    elif warned and request.domain_policy == "strict":
        blocked = True
        reason = "strict domain policy: out-of-range " + ", ".join(f["field"] for f in warned)

    run = None
    if not blocked:
        run = prod.pull_run_to_dict(prod.simulate_pull(eff_recipe, effective_config))
    return ScenarioExecution(
        request=request, base_recipe=base_dict, effective_recipe=dataclasses.asdict(eff_recipe),
        effective_config=_config_summary(effective_config), applied_overrides=applied, pull_run=run,
        domain_findings=findings, run_id=(run or {}).get("run_id"),
        effective_domain_policy=request.domain_policy, domain_blocked=blocked, domain_block_reason=reason)


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
    is_common_lens = name in _COMMON_SCENARIO_LENSES

    from puckworks.product import lab_runners
    has_native_runner = lab_runners.has_runner(name)

    if not metadata_complete:
        runner_cap, adapter_cap, disposition = "NOT_APPLICABLE", "NOT_APPLICABLE", "METADATA_INCOMPLETE"
    elif rights_blocked:
        runner_cap, adapter_cap, disposition = "RIGHTS_BLOCKED", "RIGHTS_BLOCKED", "RIGHTS_BLOCKED"
    elif is_common_lens:
        # Cameron is executed AS the common-scenario lens; it is not a *separate* native reference runner
        runner_cap, adapter_cap, disposition = "NOT_APPLICABLE", "COMMON_SCENARIO_READY", \
            "COMMON_SCENARIO_READY"
    elif has_native_runner:
        runner_cap = "AVAILABLE"
        adapter_cap = "ADAPTER_REQUIRED" if stage == "extraction" else "NOT_APPLICABLE"
        disposition = "NATIVE_REFERENCE_ONLY"
    elif opt_dep and not available_in_env:
        runner_cap, adapter_cap, disposition = "OPTIONAL_DEPENDENCY_UNAVAILABLE", "NOT_APPLICABLE", \
            "SKIPPED_OPTIONAL_DEPENDENCY"
    elif opt_dep:
        runner_cap, adapter_cap, disposition = "NOT_IMPLEMENTED", "NOT_APPLICABLE", "NATIVE_REFERENCE_ONLY"
    elif is_calibration:
        runner_cap, adapter_cap, disposition = "NOT_IMPLEMENTED", "NOT_APPLICABLE", "CALIBRATION_OR_CLOSURE"
    elif kind in ("reference", "synthesis"):
        runner_cap, adapter_cap, disposition = "NOT_IMPLEMENTED", "NOT_APPLICABLE", "NATIVE_REFERENCE_ONLY"
    elif stage == "extraction":
        runner_cap, adapter_cap, disposition = "NOT_IMPLEMENTED", "ADAPTER_REQUIRED", "ADAPTER_REQUIRED"
    elif stage in ("bed_dynamics", "flow", "infiltration", "machine"):
        runner_cap, adapter_cap, disposition = "NOT_IMPLEMENTED", "ADAPTER_REQUIRED", "SUPPORTING_STAGE_LENS"
    else:
        runner_cap, adapter_cap, disposition = "NOT_IMPLEMENTED", "NOT_APPLICABLE", "NATIVE_REFERENCE_ONLY"

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
    """Return (selection_records, executed_lens_ids). An unknown requested lens raises; a known but
    non-executable lens (no common adapter, rights-blocked, or domain-blocked) is surfaced as
    REQUESTED_BUT_NOT_EXECUTABLE — never silently discarded."""
    from puckworks import rights
    req = execution.request
    registered = {c.name for c in _components()}
    for lid in req.requested_lens_ids:
        if lid not in registered:
            raise ValueError(f"unknown requested lens id {lid!r} (not a registered component)")
    selected = list(req.requested_lens_ids) if req.requested_lens_ids else list(_COMMON_SCENARIO_LENSES)
    records, executed = [], []
    for lid in selected:
        if lid not in _COMMON_SCENARIO_LENSES:
            state, reason = "REQUESTED_BUT_NOT_EXECUTABLE", "no common-scenario adapter for this component"
        elif rights.is_code_rights_blocked(lid):
            state, reason = "REQUESTED_BUT_NOT_EXECUTABLE", "code rights blocked (see rights registry)"
        elif execution.domain_blocked:
            state, reason = "REQUESTED_BUT_NOT_EXECUTABLE", execution.domain_block_reason
        elif execution.pull_run is None:
            state, reason = "REQUESTED_BUT_NOT_EXECUTABLE", "producer did not run"
        else:
            state, reason = "EXECUTED", ""
            executed.append(lid)
        records.append({"component_id": lid, "lens_request_state": state, "reason": reason})
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


def _lens_result(execution: ScenarioExecution) -> dict:
    run = execution.pull_run or {}
    return {
        "component_id": "cameron2020.extraction_bdf",
        "adapter": f"puckworks.product.simulate_pull({execution.request.preset_id})",
        "status": "executed", "disposition": "COMMON_SCENARIO_READY",
        "observables": _observable_records(run),
        "traces": _trace_records(run),
        "domain_findings": list(execution.domain_findings),
        "warnings": run.get("warnings", []),
        "evidence_note": "executed via the existing authoritative producer; no equation is re-implemented",
    }


def _executed_lenses(execution: ScenarioExecution, executed_ids: list) -> list:
    """The lens result objects for the lenses that actually executed (today: cameron only)."""
    return [_lens_result(execution) for lid in executed_ids if lid == "cameron2020.extraction_bdf"]


# ── native reference selection (unambiguous policy; no silent discard) ───────────────
def _resolve_reference_runner_ids(request: ScenarioRequest) -> list:
    from puckworks.product import lab_runners
    policy = request.reference_selection_policy
    if policy == "none":
        return []
    if policy == "interactive_fast":
        return list(lab_runners.INTERACTIVE_FAST)
    # 'selected' — validate every requested id; an unknown id raises rather than being dropped
    ids = list(request.requested_reference_runner_ids)
    unknown = [i for i in ids if not lab_runners.has_runner(i)]
    if unknown:
        raise ValueError(f"unknown reference runner id(s): {sorted(unknown)}")
    return ids


def _reference_selection(execution: ScenarioExecution) -> tuple[list, list]:
    """Return (selection_records, executed_results). selection_records carry the per-request execution
    state for every resolved runner; executed_results are the actually-run native reference cases."""
    from puckworks.product import lab_runners
    resolved = _resolve_reference_runner_ids(execution.request)
    executed = lab_runners.run_selected(resolved) if resolved else []
    by_id = {r["component_id"]: r for r in executed}
    records = []
    for cid in sorted(set(resolved)):
        r = by_id.get(cid)
        if r is None:
            state = "NOT_APPLICABLE"
        elif r.get("status") == "executed":
            state = "EXECUTED"
        elif r.get("status") == "FAILED":
            state = "FAILED"
        else:
            state = "NOT_APPLICABLE"
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
                if row["component_id"] in _COMMON_SCENARIO_LENSES else "no native reference runner applies"
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
        "requested_lens_ids": list(req.requested_lens_ids),
        "reference_selection_policy": req.reference_selection_policy,
        "requested_reference_runner_ids": list(req.requested_reference_runner_ids),
    }
    domain = {
        "policy": req.domain_policy, "effective_policy": execution.effective_domain_policy,
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
                   "executed_native_references": sum(1 for r in executed_refs
                                                      if r.get("status") == "executed"),
                   "failed_native_references": sum(1 for r in executed_refs
                                                   if r.get("status") == "FAILED")},
        "lens_selection": lens_records,
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
