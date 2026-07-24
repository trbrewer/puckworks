"""Guided Espresso Pull — a rights-independent, runnable guided mechanism explorer (issue #48).

A user enters a bounded recipe and runs an end-to-end model *configuration* on CPU. The primary
chain is anchored on the coherent, self-contained ``cameron2020.extraction_bdf`` shot model (which
internally spans grind -> flow -> extraction -> cup); every other registered component receives an
explicit **coverage disposition** rather than being silently forced into one calculation. This is a
guided *mechanism explorer*, not an optimizer, a flavor predictor, or a digital twin.

Everything here is rights-independent: it computes from model code + caller inputs and ships/loads no
upstream fixture data. Chemical **composition** is reported where supported — never sensory flavor.

The public ``PullRun`` (schema version 1, unreleased) also carries **authoritative traces** — typed,
serializable time/depth series copied straight from the solver result, each labelled by *value role*
(prescribed model input · simulated model output · derived quantity) so the visual report never
presents a prescribed pressure as if it were measured, or fabricates a wetting/first-drip curve.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Callable

import puckworks

PULL_RUN_SCHEMA_VERSION = 1

# EK43 dial range the primary model is documented for (evidence/calibration bounds), plus the wider
# solver-safe hard bounds. Sources: cameron2020.extraction_bdf card (valid_range) + solver limits.
_GS_EVIDENCE = (1.1, 2.3)
_GS_HARD = (1.0, 2.5)
_DOSE_EVIDENCE_G = (15.0, 25.0)
_BEV_EVIDENCE_G = (25.0, 60.0)
_PRESSURE_EVIDENCE_BAR = (6.0, 9.0)
# Recorded-context sanity bounds for a liquid-water brew temperature. Temperature is RECORDED-ONLY:
# the primary v0.3.0 model has no thermal transient, so temperature never enters the calculation and
# a departure is NOT model extrapolation (it is NOT_APPLICABLE, never a WARNING).
_TEMP_LIQUID_C = (0.0, 100.0)

# Hard COMPUTATIONAL-SAFETY ceilings (distinct from the evidence ranges above): generous
# "nothing is physically sane past here" bounds that keep an absurd input (e.g. dose_g=1e9) out of
# the solver, where it would blow up bed depth / flux and produce non-finite output. A value inside
# the ceiling but outside the evidence range is still only a WARNING; only past the ceiling is REJECT.
_DOSE_HARD_MAX = 100.0        # g  (espresso dose is ~7-25 g; 4x the evidence max)
_BEV_HARD_MAX = 500.0         # g
_PRESSURE_HARD_MAX = 20.0     # bar (Ulka deadhead ~15 bar)

_PRIMARY = "cameron2020.extraction_bdf"
_SUPPORTED_CONFIG_IDS = ("pv19_named", "guided_v1")
_SUPPORTED_CONFIG_VERSION = 1
_SUPPORTED_PRESSURE_PROFILE = "constant"
_EXPECTED_STAGE_COMPONENTS = {"grind": _PRIMARY, "machine_flow": _PRIMARY, "extraction": _PRIMARY}

# Value-role vocabulary for a trace series (issue #48, §1A). Distinguishes a *prescribed model input*
# (e.g. constant pump pressure), a *simulated model output* (e.g. modeled solute arrival), and a
# *derived quantity* (e.g. cumulative beverage mass integrated from the model's flow).
SERIES_ROLES = ("prescribed_input", "simulated", "derived")

# Figure-level evidence vocabulary (puckworks.public.schema): the guided pull is an exploratory
# simulation, code-verified against the source paper but NOT independently validated against a
# measured cup. "code_verification" (the registry's internal word) is not a public evidence rung;
# "verification" is the closest public rung and is honest under the EXPLORATORY_SIMULATION badge.
_TRACE_BADGE = "EXPLORATORY_SIMULATION"
_TRACE_EVIDENCE_STRENGTH = "verification"
_CAMERON_CEILING = (
    "single-solute, saturated-bed BDF extraction: extraction-yield / TDS / flow / outlet-concentration "
    "trends and chemical composition only — not puck wetting, physical first drip, a dynamic pressure "
    "profile, a thermal transient, channeling, or flavor")


# ─────────────────────────────── enums ───────────────────────────────────────────
class DomainStatus(str, Enum):
    IN_DOMAIN = "in_domain"
    WARNING = "warning"
    REJECTED = "rejected"
    NOT_APPLICABLE = "not_applicable"


class ComponentDisposition(str, Enum):
    EXECUTED_PRIMARY = "executed_primary"                 # executed as the primary chain in this run
    CALIBRATION_ONLY = "calibration_only"                 # feeds parameters, not a runtime stage
    AVAILABLE_AS_SEPARATE_LENS = "available_as_separate_lens"   # eligible, but NOT executed this run
    NOT_EXECUTED = "not_executed"                         # no defined role; not executed
    DIAGNOSTIC_ONLY = "diagnostic_only"
    NOT_APPLICABLE = "not_applicable"
    EXCLUDED_INCOMPATIBLE = "excluded_incompatible"
    EXCLUDED_OUT_OF_DOMAIN = "excluded_out_of_domain"
    EXCLUDED_OPTIONAL_DEPENDENCY = "excluded_optional_dependency"
    EXCLUDED_RUNTIME_BUDGET = "excluded_runtime_budget"


# Only the primary chain is actually executed. Everything else is eligible/calibration/excluded.
_EXECUTED_DISPOSITIONS = (ComponentDisposition.EXECUTED_PRIMARY,)


class PullEvent(str, Enum):
    RUN_STARTED = "run_started"
    STAGE_STARTED = "stage_started"
    STAGE_WARNING = "stage_warning"
    STAGE_COMPLETED = "stage_completed"
    LENS_STARTED = "lens_started"
    LENS_COMPLETED = "lens_completed"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"


class PullDomainError(ValueError):
    """Raised when a recipe/config is hard-invalid (REJECTED), or leaves evidence domain under
    ``domain_policy='strict'``."""


class PullExecutionError(RuntimeError):
    """Raised when the solver runs on an accepted recipe but produces a non-finite / non-physical
    value (e.g. a zero/negative Darcy flux, or a non-finite yield). A controlled failure — never a
    leaked ZeroDivision/SciPy/NumPy exception or a silent inf/nan in the result."""


def _freeze(obj):
    """Recursively convert dicts→read-only proxies (and lists→tuples) so a frozen PullRun record is
    deeply immutable (PW-PULL-006). Serializers call _thaw to recover plain JSON-safe containers."""
    if isinstance(obj, dict):
        return MappingProxyType({k: _freeze(v) for k, v in obj.items()})
    if isinstance(obj, (list, tuple)):
        return tuple(_freeze(v) for v in obj)
    return obj


def _thaw(obj):
    """Inverse of _freeze for serialization: proxies→plain dicts, tuples→lists. JSON-neutral."""
    if isinstance(obj, MappingProxyType):
        return {k: _thaw(v) for k, v in obj.items()}
    if isinstance(obj, tuple):
        return [_thaw(v) for v in obj]
    return obj


def _require_finite(name, value):
    v = float(value)
    if not math.isfinite(v):
        raise PullExecutionError("solver produced a non-finite %s: %r" % (name, value))
    return v


def _require_finite_positive(name, value):
    v = _require_finite(name, value)
    if v <= 0:
        raise PullExecutionError("solver produced a non-positive %s: %r" % (name, value))
    return v


ProgressCallback = Callable[[PullEvent, dict], None]


# ─────────────────────────────── records ─────────────────────────────────────────
@dataclass(frozen=True)
class CoffeeProfile:
    """A named, model-backed parameter set. It NEVER derives parameters from a free-text bean name."""

    profile_id: str
    source: str
    supported_components: tuple[str, ...]
    parameters: dict          # explicit values + units, model-backed
    context: str              # applicable coffee/roast/grind context
    evidence_strength: str
    caveat: str

    def __post_init__(self):
        object.__setattr__(self, "parameters", _freeze(dict(self.parameters)))


@dataclass(frozen=True)
class PullRecipe:
    dose_g: float
    target_beverage_g: float
    brew_temperature_c: float
    pressure_bar: float
    grinder_model: str
    coffee_profile: str
    grind_setting: float | None = None
    mean_particle_radius_m: float | None = None
    preinfusion_s: float | None = None
    preinfusion_pressure_bar: float | None = None
    basket_diameter_mm: float | None = None
    bean_label: str | None = None
    notes: str | None = None

    def __post_init__(self):
        for name in ("dose_g", "target_beverage_g", "brew_temperature_c", "pressure_bar"):
            v = getattr(self, name)
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(float(v)):
                raise PullDomainError(f"{name} must be a finite number")
        if not self.grinder_model or not isinstance(self.grinder_model, str):
            raise PullDomainError("grinder_model is required")
        if self.grind_setting is not None and self.mean_particle_radius_m is not None:
            raise PullDomainError(
                "supply grind_setting OR mean_particle_radius_m, not both (no verified adapter "
                "maps one grinder's dial to a physical radius)")
        if self.grind_setting is None and self.mean_particle_radius_m is None:
            raise PullDomainError("a grind_setting (dial) or mean_particle_radius_m is required")


@dataclass(frozen=True)
class PullSeries:
    """One authoritative model series (issue #48, §1A). Values are an immutable tuple of finite
    floats copied from the solver at full precision (rounding happens only at display time)."""

    series_id: str
    label: str
    values: tuple[float, ...]
    unit: str
    role: str                                   # one of SERIES_ROLES
    method: str                                 # concise derivation/method statement
    caveat: str
    domain_findings: tuple[DomainFinding, ...] = ()

    def __post_init__(self):
        if not self.series_id:
            raise PullDomainError("PullSeries.series_id must be non-empty")
        if not self.unit:
            raise PullDomainError(f"PullSeries {self.series_id!r} needs an explicit unit")
        if self.role not in SERIES_ROLES:
            raise PullDomainError(
                f"PullSeries {self.series_id!r} role {self.role!r} not in {SERIES_ROLES}")
        if not isinstance(self.values, tuple):
            raise PullDomainError(f"PullSeries {self.series_id!r} values must be an immutable tuple")
        if not self.values:
            raise PullDomainError(f"PullSeries {self.series_id!r} must have at least one value")
        for v in self.values:
            if not isinstance(v, float) or not math.isfinite(v):
                raise PullDomainError(f"PullSeries {self.series_id!r} has a non-finite value")


@dataclass(frozen=True)
class PullTrace:
    """A stage-anchored bundle of one independent axis and one or more :class:`PullSeries`."""

    trace_id: str
    stage_id: str
    component_id: str
    axis_label: str
    axis_unit: str
    axis_values: tuple[float, ...]
    series: tuple[PullSeries, ...]
    method: str
    evidence_badge: str                         # figure badge (public.schema.BADGES)
    evidence_strength: str
    fidelity_ceiling: str
    assumptions: str
    caveat: str

    def __post_init__(self):
        if not (self.trace_id and self.stage_id and self.component_id):
            raise PullDomainError("PullTrace ids (trace/stage/component) must be non-empty")
        if not self.axis_unit:
            raise PullDomainError(f"PullTrace {self.trace_id!r} needs an explicit axis unit")
        if not isinstance(self.axis_values, tuple):
            raise PullDomainError(f"PullTrace {self.trace_id!r} axis_values must be an immutable tuple")
        for v in self.axis_values:
            if not isinstance(v, float) or not math.isfinite(v):
                raise PullDomainError(f"PullTrace {self.trace_id!r} has a non-finite axis value")
        n = len(self.axis_values)
        if n < 1:
            raise PullDomainError(f"PullTrace {self.trace_id!r} axis must be non-empty")
        if any(b <= a for a, b in zip(self.axis_values, self.axis_values[1:])):
            raise PullDomainError(f"PullTrace {self.trace_id!r} axis must be strictly increasing")
        if not self.series:
            raise PullDomainError(f"PullTrace {self.trace_id!r} must have at least one series")
        ids = [s.series_id for s in self.series]
        if len(set(ids)) != len(ids):
            raise PullDomainError(f"PullTrace {self.trace_id!r} has duplicate series ids {ids}")
        for s in self.series:
            if len(s.values) != n:
                raise PullDomainError(
                    f"PullTrace {self.trace_id!r} series {s.series_id!r} length {len(s.values)} "
                    f"!= axis length {n}")


@dataclass(frozen=True)
class DomainFinding:
    status: DomainStatus
    field: str
    supplied_value: object
    supported_range: str
    units: str
    component: str
    technical_reason: str
    plain_explanation: str
    suggested_action: str
    source: str


@dataclass(frozen=True)
class StageResult:
    stage_id: str
    sequence: int
    component_id: str
    source_citation: str
    execution_role: str
    method_name: str
    method_plain: str
    method_technical: str
    inputs: dict              # name -> {"value":..., "unit":...}
    outputs: dict
    evidence_badge: str
    evidence_strength: str
    provenance_class: str
    assumptions: str
    valid_range: str
    domain_findings: tuple[DomainFinding, ...]
    fitted_parameters: dict
    runtime_s: float
    success: bool
    caveat: str
    references: str

    def __post_init__(self):
        for name in ("inputs", "outputs", "fitted_parameters"):
            object.__setattr__(self, name, _freeze(dict(getattr(self, name))))


@dataclass(frozen=True)
class PullConfig:
    config_id: str
    config_version: int
    stage_components: dict     # stage -> component_id (primary chain)
    domain_policy: str = "warn"   # "warn" | "strict"
    pressure_profile: str = "constant"   # only "constant" is executable in v0.3.0
    lenses: tuple[str, ...] = ()
    grid_N: int = 40
    grid_M: int = 24
    # which recipe/config fields guided mode may change:
    #   None       -> unrestricted (any field editable)
    #   ()         -> a FIXED preset: nothing is editable
    #   (a, b, ..) -> only those named fields are editable
    editable_fields: tuple[str, ...] | None = None

    def __post_init__(self):
        if self.editable_fields is not None and (
                not isinstance(self.editable_fields, tuple)
                or not all(isinstance(f, str) for f in self.editable_fields)):
            raise PullDomainError("editable_fields must be None or a tuple of field-name strings")
        if self.domain_policy not in ("warn", "strict"):
            raise PullDomainError("domain_policy must be 'warn' or 'strict'")
        if self.pressure_profile != _SUPPORTED_PRESSURE_PROFILE:
            raise PullDomainError(
                f"pressure_profile {self.pressure_profile!r} is not executable; the v0.3.0 primary "
                f"model uses a prescribed {_SUPPORTED_PRESSURE_PROFILE!r} pressure only")
        for name in ("grid_N", "grid_M"):
            v = getattr(self, name)
            if not isinstance(v, int) or isinstance(v, bool) or v <= 0:
                raise PullDomainError(f"{name} must be a positive integer")
        if not isinstance(self.lenses, tuple):
            raise PullDomainError("lenses must be a tuple")
        object.__setattr__(self, "stage_components", _freeze(dict(self.stage_components)))


@dataclass(frozen=True)
class ComponentCoverage:
    component_id: str
    stage: str
    disposition: ComponentDisposition
    executed: bool
    reason: str


@dataclass(frozen=True)
class PullReportArtifacts:
    """Descriptor of the files a rendered guided-pull report wrote (issue #48, §2A). Paths are
    strings under ``out_dir``; ``files`` is the full generated list in deterministic order."""

    out_dir: str
    results_json: str
    report_md: str
    summary_png: str
    pressure_flow_png: str
    cup_progress_png: str
    extraction_progress_png: str
    captions_txt: str
    files: tuple[str, ...]


@dataclass(frozen=True)
class PullRun:
    schema_version: int
    package_version: str
    source_commit: str | None
    run_id: str
    recipe: PullRecipe
    config: PullConfig
    stages: tuple[StageResult, ...]
    lenses: tuple[StageResult, ...]
    traces: tuple[PullTrace, ...]
    final_observables: dict
    domain_findings: tuple[DomainFinding, ...]
    assumptions_summary: tuple[str, ...]
    coverage: tuple[ComponentCoverage, ...]
    warnings: tuple[str, ...]
    completion_state: str      # "completed" | "completed_with_warnings"

    def __post_init__(self):
        object.__setattr__(self, "final_observables", _freeze(dict(self.final_observables)))


# ─────────────────────────────── coffee profiles ─────────────────────────────────
# The reference profile is model-backed by cameron2020's built-in microstructure/inventory; it does
# not invent parameters and is not selected by a bean name.
_PROFILES: dict[str, CoffeeProfile] = {
    "reference": CoffeeProfile(
        profile_id="reference",
        source="cameron2020.extraction_bdf built-in microstructure + single soluble pool",
        supported_components=(_PRIMARY,),
        parameters={"soluble_inventory": {"value": "per-bed-volume (EY ceiling ~29.6%)", "unit": "-"},
                    "solute_pool": {"value": "single", "unit": "-"}},
        context="medium roast, EK43-class grind, 20 g in / 40 g out espresso",
        evidence_strength="code_verification",
        caveat="model-backed reference parameters; not tuned to any specific bean or user shot"),
}


def _profile(profile_id: str) -> CoffeeProfile:
    if profile_id not in _PROFILES:
        raise PullDomainError(
            f"unknown coffee_profile {profile_id!r}; known: {sorted(_PROFILES)} "
            "(parameters are never generated from a bean name)")
    return _PROFILES[profile_id]


# ─────────────────────────────── domain engine ───────────────────────────────────
def _hard(field, value, ok, rng, units, reason, plain, action):
    if ok:
        return None
    return DomainFinding(DomainStatus.REJECTED, field, value, rng, units,
                         _PRIMARY, reason, plain, action, "solver/physical limits")


def _evidence(field, value, lo, hi, units, plain):
    if lo <= value <= hi:
        return DomainFinding(DomainStatus.IN_DOMAIN, field, value, f"{lo}-{hi}", units,
                             _PRIMARY, "within documented evidence range",
                             plain, "", "cameron2020.extraction_bdf card")
    return DomainFinding(DomainStatus.WARNING, field, value, f"{lo}-{hi}", units,
                         _PRIMARY,
                         f"{value} is outside the documented evidence range {lo}-{hi} {units}",
                         plain + " — this run extrapolates beyond the model's validated range",
                         f"move {field} into {lo}-{hi} {units} for a supported result",
                         "cameron2020.extraction_bdf card")


def _grind_setting(recipe: PullRecipe) -> float:
    # v1: the EK43 dial IS cameron's grind setting; a physical radius has no verified dial adapter.
    if recipe.grind_setting is not None:
        return float(recipe.grind_setting)
    raise PullDomainError(
        "mean_particle_radius_m is accepted by the recipe but has no verified dial adapter for "
        "the primary model yet; supply an EK43 grind_setting for guided_v1")


def evaluate_domain(recipe: PullRecipe) -> tuple[DomainFinding, ...]:
    """Return all domain findings. Hard-invalid inputs are REJECTED; evidence-range departures are
    WARNING; recorded-only / not-modeled inputs are NOT_APPLICABLE. Never clamps."""
    gs = recipe.grind_setting
    findings: list[DomainFinding | None] = [
        _hard("dose_g", recipe.dose_g, 0 < recipe.dose_g <= _DOSE_HARD_MAX, f"0-{_DOSE_HARD_MAX:g}", "g",
              "dose must be positive and within the solver-safe ceiling",
              "You must use some coffee, and not an absurd amount.", "set a dose in ~15-25 g"),
        _hard("target_beverage_g", recipe.target_beverage_g,
              0 < recipe.target_beverage_g <= _BEV_HARD_MAX, f"0-{_BEV_HARD_MAX:g}", "g",
              "beverage mass must be positive and within the solver-safe ceiling",
              "The cup must hold some liquid, and not an absurd amount.", "set a target in ~25-60 g"),
        _hard("brew_temperature_c", recipe.brew_temperature_c,
              _TEMP_LIQUID_C[0] < recipe.brew_temperature_c < _TEMP_LIQUID_C[1],
              "0-100 (exclusive)", "degC", "not a liquid-water brew temperature",
              "Recorded brew temperature must be between 0 and 100 C.", "record ~85-96 C"),
        _hard("pressure_bar", recipe.pressure_bar, 0 < recipe.pressure_bar <= _PRESSURE_HARD_MAX,
              f"0-{_PRESSURE_HARD_MAX:g}", "bar",
              "pump overpressure must be positive and within the solver-safe ceiling",
              "The pump must push, but not past a physically implausible pressure.", "use ~6-9 bar"),
    ]
    if gs is not None:
        findings.append(_hard("grind_setting", gs, _GS_HARD[0] <= gs <= _GS_HARD[1],
                              f"{_GS_HARD[0]}-{_GS_HARD[1]}", "EK43 dial",
                              "grind setting outside the solver-safe range",
                              "This grind is too far outside the model's stable range to compute.",
                              f"use an EK43 dial in {_GS_EVIDENCE[0]}-{_GS_EVIDENCE[1]}"))
    # Unsupported recipe fields: rejected (never silently accepted) until a capable component couples.
    if recipe.preinfusion_s is not None:
        findings.append(DomainFinding(
            DomainStatus.REJECTED, "preinfusion_s", recipe.preinfusion_s, "must be unset", "s",
            _PRIMARY, "no preinfusion-capable component is coupled to the primary chain",
            "The v0.3.0 primary model begins from a saturated bed; it cannot model a preinfusion phase.",
            "leave preinfusion unset for guided_v1", "guided-pull scope"))
    if recipe.preinfusion_pressure_bar is not None:
        findings.append(DomainFinding(
            DomainStatus.REJECTED, "preinfusion_pressure_bar", recipe.preinfusion_pressure_bar,
            "must be unset", "bar", _PRIMARY,
            "no preinfusion-capable component is coupled to the primary chain",
            "The v0.3.0 primary model has no preinfusion phase to pressurize.",
            "leave preinfusion pressure unset for guided_v1", "guided-pull scope"))
    if recipe.basket_diameter_mm is not None:
        findings.append(DomainFinding(
            DomainStatus.REJECTED, "basket_diameter_mm", recipe.basket_diameter_mm,
            "must be unset", "mm", _PRIMARY,
            "the primary solver uses a fixed basket radius and does not consume a diameter override",
            "The v0.3.0 primary model does not take a basket-geometry override.",
            "leave basket_diameter_mm unset for guided_v1", "guided-pull scope"))

    hard = [f for f in findings if f is not None]
    if any(f.status is DomainStatus.REJECTED for f in hard):
        return tuple(hard)

    ev: list[DomainFinding | None] = [
        _evidence("grind_setting", gs, *_GS_EVIDENCE, "EK43 dial", "How fine the coffee is ground.") if gs is not None else None,
        _evidence("dose_g", recipe.dose_g, *_DOSE_EVIDENCE_G, "g", "How much dry coffee."),
        _evidence("target_beverage_g", recipe.target_beverage_g, *_BEV_EVIDENCE_G, "g", "How much espresso in the cup."),
        _evidence("pressure_bar", recipe.pressure_bar, *_PRESSURE_EVIDENCE_BAR, "bar", "Pump pressure."),
        # Temperature is RECORDED-ONLY — the primary model has no thermal transient, so a departure is
        # NOT model extrapolation. It is reported as NOT_APPLICABLE, never a WARNING.
        DomainFinding(
            DomainStatus.NOT_APPLICABLE, "brew_temperature_c", recipe.brew_temperature_c,
            "recorded-only", "degC", _PRIMARY,
            "the v0.3.0 primary model contains no thermal transient; temperature is recorded context",
            "Temperature is recorded with the recipe but does not affect the current v0.3.0 primary model.",
            "", "guided-pull scope"),
    ]
    return tuple(f for f in ev if f is not None)


# ─────────────────────────────── coverage ledger ─────────────────────────────────
# Honest disposition of every registered component relative to the guided-pull primary chain. Only
# the primary model is EXECUTED; the rest are calibration inputs, eligible-but-not-executed separate
# lenses, or not compatible with the primary contract without a verified adapter. We never say
# "compared" — no parallel lens is executed in a guided-pull run.
_SEPARATE_LENS = ("intentionally kept separate: its state definitions or conventions are not verified "
                  "as a causal adapter to the primary chain, so it was NOT executed in this run")
_COVERAGE_RULES: dict[str, tuple[ComponentDisposition, str]] = {
    _PRIMARY: (ComponentDisposition.EXECUTED_PRIMARY,
        "coherent self-contained shot model spanning grind->flow->extraction->cup; executed as the primary chain"),
}
_STAGE_DEFAULT: dict[str, tuple[ComponentDisposition, str]] = {
    "extraction": (ComponentDisposition.AVAILABLE_AS_SEPARATE_LENS,
        "alternative extraction lineage (conventions/inventory differ); " + _SEPARATE_LENS),
    "flow": (ComponentDisposition.CALIBRATION_ONLY, "calibration/flow-closure input, not a runtime primary stage"),
    "grind": (ComponentDisposition.CALIBRATION_ONLY, "grind calibration map, not runtime physics"),
    "packing": (ComponentDisposition.CALIBRATION_ONLY, "bed/permeability calibration input"),
    "bed_dynamics": (ComponentDisposition.AVAILABLE_AS_SEPARATE_LENS,
        "bed-dynamics model on a different reference frame; " + _SEPARATE_LENS),
    "machine": (ComponentDisposition.AVAILABLE_AS_SEPARATE_LENS,
        "machine/pump model with its own dimensionless frame; " + _SEPARATE_LENS),
    "infiltration": (ComponentDisposition.AVAILABLE_AS_SEPARATE_LENS,
        "unsaturated-flow/wetting model; the primary model assumes a saturated bed from t=0; " + _SEPARATE_LENS),
}


def _coverage() -> tuple[ComponentCoverage, ...]:
    puckworks.load_builtin_components()
    out = []
    for c in sorted(puckworks.components(), key=lambda x: (x.stage, x.name)):
        if c.name in _COVERAGE_RULES:
            disp, reason = _COVERAGE_RULES[c.name]
        elif "lb_taichi" in c.name:
            disp, reason = ComponentDisposition.EXCLUDED_OPTIONAL_DEPENDENCY, "optional GPU/taichi component; excluded from the default CPU run"
        elif c.kind == "calibration" or c.execution_role == "calibration":
            disp, reason = ComponentDisposition.CALIBRATION_ONLY, "calibration component (feeds parameters, not a runtime stage)"
        else:
            disp, reason = _STAGE_DEFAULT.get(c.stage,
                (ComponentDisposition.NOT_EXECUTED, "no defined role in the guided-pull chain; not executed"))
        out.append(ComponentCoverage(c.name, c.stage, disp, disp in _EXECUTED_DISPOSITIONS, reason))
    return tuple(out)


# ─────────────────────────────── config enforcement ──────────────────────────────
def _validate_config(config: PullConfig) -> None:
    """Reject a configuration the engine cannot honestly execute (issue #48, §1E). Guards against
    accepting an arbitrary record and then running the Cameron chain regardless of its contents."""
    if config.config_id not in _SUPPORTED_CONFIG_IDS:
        raise PullDomainError(
            f"unknown config_id {config.config_id!r}; supported: {_SUPPORTED_CONFIG_IDS}")
    if config.config_version != _SUPPORTED_CONFIG_VERSION:
        raise PullDomainError(
            f"config_version {config.config_version} unsupported (only {_SUPPORTED_CONFIG_VERSION})")
    if dict(config.stage_components) != _EXPECTED_STAGE_COMPONENTS:
        raise PullDomainError(
            "unsupported stage_components override; the only executable primary mapping is "
            f"{_EXPECTED_STAGE_COMPONENTS}")
    if config.lenses:
        raise PullDomainError(
            f"requested lenses {tuple(config.lenses)} are unavailable: no parallel-lens executor is "
            "implemented in v0.3.0 (alternatives are reported as separate, non-executed dispositions)")


# ─────────────────────────────── orchestration ───────────────────────────────────
def _component_meta(component_id: str):
    puckworks.load_builtin_components()
    return puckworks.get(component_id)


def _emit(progress, event, payload):
    # PW-PULL-011: a user progress callback is UNTRUSTED — its exception must not abort the scientific
    # run. Isolate it, warn to stderr (never silently swallow), and continue producing the result.
    if progress is None:
        return
    try:
        progress(event, payload)
    except Exception as exc:   # noqa: BLE001 - callback isolation is the point
        import sys
        print("guided-pull progress callback raised %s (ignored, run continues): %s"
              % (type(exc).__name__, exc), file=sys.stderr)


def _md(text) -> str:
    """Escape a string for safe INLINE markdown (PW-PULL-012): neutralize table pipes, code backticks,
    and markdown emphasis, and collapse control characters/newlines to spaces so a user- or
    model-provided label cannot corrupt the rendered report structure."""
    s = "" if text is None else str(text)
    s = "".join(" " if (ord(c) < 32) else c for c in s)          # control chars / newlines -> space
    # escape the structurally-dangerous markdown characters. NOT underscore: GFM does not emphasize
    # intra-word underscores, and escaping them would corrupt identifiers like extraction_yield_pct.
    for ch in ("\\", "`", "|", "*", "#", "<", ">", "[", "]"):
        s = s.replace(ch, "\\" + ch)
    return s


def _stage(stage_id, seq, cam, method_plain, method_technical, inputs, outputs, findings, runtime_s, caveat):
    return StageResult(
        stage_id=stage_id, sequence=seq, component_id=_PRIMARY,
        source_citation=cam.paper, execution_role=cam.execution_role,
        method_name="cameron2020 BDF single-solute bed model",
        method_plain=method_plain, method_technical=method_technical,
        inputs=inputs, outputs=outputs, evidence_badge="simulated",
        evidence_strength=cam.evidence_strength, provenance_class=cam.provenance_class,
        assumptions=cam.assumptions, valid_range=cam.valid_range,
        domain_findings=tuple(findings), fitted_parameters={}, runtime_s=runtime_s,
        success=True, caveat=caveat, references=f"{cam.paper}; doi:{cam.doi}")


def _series(series_id, label, values, unit, role, method, caveat):
    return PullSeries(series_id=series_id, label=label, values=tuple(float(v) for v in values),
                      unit=unit, role=role, method=method, caveat=caveat)


def _build_traces(cam_model, cam, recipe, gs, q, shot) -> tuple[PullTrace, ...]:
    """Authoritative traces copied straight from the solver result (issue #48, §1B) — never rebuilt
    from the rounded final observables. Full solver precision is preserved; rounding is display-only.
    """
    import numpy as np

    m_in = recipe.dose_g / 1000.0
    area = math.pi * cam_model.R0 ** 2
    t = np.asarray(shot.t, dtype=float)
    # Constant model flow: the primary model uses a constant Darcy flux q, so mass flow is constant.
    massflow_g_s = area * q * cam_model.RHO_OUT * 1000.0
    flow_series = np.full_like(t, massflow_g_s)
    # Cumulative beverage mass = integral of the constant model flow over solver time (NOT a forced
    # line to the target). Endpoint equals target beverage mass by construction of t_shot.
    beverage_g = area * q * cam_model.RHO_OUT * t * 1000.0
    pressure_series = np.full_like(t, float(recipe.pressure_bar))
    extracted_g = np.asarray(shot.m_cup, dtype=float) * 1000.0      # simulated solute reaching the cup
    ey_pct = 100.0 * np.asarray(shot.m_cup, dtype=float) / m_in     # derived from simulated m_cup
    cl_out = np.asarray(shot.cl_out, dtype=float)                   # simulated outlet concentration

    def trace(trace_id, stage_id, axis_label, axis_unit, axis_values, series, method, caveat):
        return PullTrace(
            trace_id=trace_id, stage_id=stage_id, component_id=_PRIMARY,
            axis_label=axis_label, axis_unit=axis_unit,
            axis_values=tuple(float(v) for v in axis_values), series=tuple(series),
            method=method, evidence_badge=_TRACE_BADGE, evidence_strength=_TRACE_EVIDENCE_STRENGTH,
            fidelity_ceiling=_CAMERON_CEILING, assumptions=cam.assumptions, caveat=caveat)

    machine_flow = trace(
        "machine_flow_time", "machine_flow", "time", "s", t,
        [_series("prescribed_pressure_bar", "Prescribed pump pressure", pressure_series, "bar",
                 "prescribed_input",
                 "prescribed constant pump overpressure — a model input, not a measured or predicted "
                 "pressure trace",
                 "the model does not predict a dynamic pressure profile; this line is the input you set"),
         _series("flow_g_s", "Model flow", flow_series, "g/s", "simulated",
                 "constant Darcy mass flow area*q*rho_out, with q from darcy_flux(gs, p_bar)",
                 "constant flow; no channeling or preinfusion transient is modeled"),
         _series("cumulative_beverage_g", "Cumulative beverage mass", beverage_g, "g", "derived",
                 "integral of the constant model flow over solver time; endpoint equals the target "
                 "beverage mass by construction of the shot time t_shot",
                 "derived from the model's constant flow — beverage mass is not measured")],
        "prescribed constant pressure drives a constant Darcy flow; beverage mass accumulates linearly",
        "constant-pressure Darcy flow; no dynamic channeling, wetting front, or preinfusion transient")

    extraction = trace(
        "extraction_time", "extraction", "time", "s", t,
        [_series("cumulative_extracted_g", "Cumulative dissolved mass in cup", extracted_g, "g",
                 "simulated", "model cumulative dissolved solute reaching the cup (shot.m_cup), kg->g",
                 "single soluble pool; no per-species composition in this model"),
         _series("extraction_yield_pct", "Cumulative extraction yield", ey_pct, "%", "derived",
                 "100 * (cumulative dissolved mass) / dose, from the simulated solute arrival",
                 "derived from simulated dissolved mass; EY ceiling ~29.6% (per-bed-volume inventory)"),
         _series("outlet_concentration", "Outlet liquid concentration", cl_out, "kg/m^3", "simulated",
                 "modeled outlet liquid concentration shot.cl_out",
                 "concentration of the single soluble pool leaving the bed")],
        "solute dissolves from the grounds into the flowing water and accumulates in the cup",
        "temperature enters only as recorded recipe context, not a resolved thermal transient")

    bed_profile = trace(
        "bed_liquid_profile", "extraction", "bed depth", "m", np.asarray(shot.z, dtype=float),
        [_series("liquid_concentration_final", "Liquid concentration at shot end",
                 np.asarray(shot.cl_final, dtype=float), "kg/m^3", "simulated",
                 "modeled liquid-phase concentration along bed depth at t_shot (shot.cl_final)",
                 "a single end-of-shot snapshot along depth, not a measured profile")],
        "final liquid concentration along the bed depth at the end of the shot",
        "one end-of-shot snapshot; the guided run does not expose full internal state matrices")

    return (machine_flow, extraction, bed_profile)


def simulate_pull(recipe: PullRecipe, config: PullConfig, *,
                  progress: ProgressCallback | None = None) -> PullRun:
    """Run the guided espresso pull. Raises :class:`PullDomainError` on hard-invalid input / an
    unsupported configuration / a strict-mode evidence departure, or :class:`PullExecutionError` on a
    non-finite solver result. Every started run emits exactly ONE terminal event: RUN_COMPLETED on
    success, or RUN_FAILED (with a stable `category`) on ANY failure of the producer phase — model
    import, solve, trace construction, or serialization — never a RUN_STARTED left dangling.
    """
    emitted = {"started": False, "failed": False}
    try:
        return _simulate_pull_impl(recipe, config, progress, emitted)
    except PullExecutionError as e:
        _emit_run_failed(progress, emitted, str(e), "execution")
        raise
    except PullDomainError as e:
        _emit_run_failed(progress, emitted, str(e), "domain")
        raise
    except Exception as e:                               # noqa: BLE001 - one terminal event, then re-raise
        _emit_run_failed(progress, emitted, "%s: %s" % (type(e).__name__, e), "internal")
        raise


def _emit_run_failed(progress, emitted, reason, category):
    """Emit RUN_FAILED at most once per started run (the impl already emits it for domain rejection)."""
    if emitted["started"] and not emitted["failed"]:
        emitted["failed"] = True
        _emit(progress, PullEvent.RUN_FAILED, {"reason": reason, "category": category})


def _simulate_pull_impl(recipe: PullRecipe, config: PullConfig, progress, emitted) -> PullRun:
    from puckworks.models.cameron2020 import extraction_bdf as cam_model

    _profile(recipe.coffee_profile)                     # validate profile (never bean-derived)
    _validate_config(config)                            # reject an unexecutable configuration
    _emit(progress, PullEvent.RUN_STARTED, {"config": config.config_id})
    emitted["started"] = True

    findings = evaluate_domain(recipe)
    if any(f.status is DomainStatus.REJECTED for f in findings):
        _emit_run_failed(progress, emitted, "rejected input", "domain")
        raise PullDomainError("recipe rejected: " + "; ".join(
            f"{f.field}={f.supplied_value} ({f.technical_reason})"
            for f in findings if f.status is DomainStatus.REJECTED))
    warns = [f for f in findings if f.status is DomainStatus.WARNING]
    if warns and config.domain_policy == "strict":
        _emit_run_failed(progress, emitted, "strict domain", "domain")
        raise PullDomainError("strict domain policy: out-of-range " + ", ".join(f.field for f in warns))

    gs = _grind_setting(recipe)
    cam = _component_meta(_PRIMARY)
    m_in, m_out = recipe.dose_g / 1000.0, recipe.target_beverage_g / 1000.0

    def find(fld):
        return [f for f in findings if f.field == fld]

    stages: list[StageResult] = []
    seq = 0

    # Grind stage
    seq += 1
    _emit(progress, PullEvent.STAGE_STARTED, {"stage": "grind"})
    t0 = time.monotonic()
    phi1, phi2, a2, bet1, bet2 = cam_model.grind_microstructure(gs)
    gr = _stage("grind", seq, cam, "How fine the grind is, turned into the bed microstructure.",
                "grind_microstructure(gs): fines/boulder volume fractions and radii for the dial",
                {"grind_setting": {"value": gs, "unit": "EK43 dial"}},
                {"fines_fraction": {"value": float(phi1), "unit": "-"},
                 "boulder_fraction": {"value": float(phi2), "unit": "-"},
                 "boulder_radius": {"value": float(a2), "unit": "m"}},
                find("grind_setting"), time.monotonic() - t0,
                "grind is represented by the model's two-family microstructure, not a measured PSD")
    stages.append(gr)
    for f in gr.domain_findings:
        if f.status is DomainStatus.WARNING:
            _emit(progress, PullEvent.STAGE_WARNING, {"stage": "grind", "field": f.field})
    _emit(progress, PullEvent.STAGE_COMPLETED, {"stage": "grind"})

    # Machine (pressure) + Flow stage: Darcy flux and shot time
    seq += 1
    _emit(progress, PullEvent.STAGE_STARTED, {"stage": "machine_flow"})
    t0 = time.monotonic()
    L = _require_finite_positive("bed_depth", cam_model.bed_depth(m_in))
    q = _require_finite_positive("darcy_flux",
                                 cam_model.darcy_flux(gs, recipe.pressure_bar, L=L,
                                                      L_ref=cam_model.bed_depth(0.020)))
    t_shot = _require_finite_positive(
        "shot_duration", m_out / (math.pi * cam_model.R0 ** 2 * cam_model.RHO_OUT * q))
    mf = _stage("machine_flow", seq, cam,
                "Prescribed pump pressure drives a constant Darcy flow through the bed, setting the shot time.",
                "darcy_flux(gs, p_bar); t_shot = m_out / (pi R0^2 rho_out q)",
                {"pressure": {"value": recipe.pressure_bar, "unit": "bar",
                              "note": "prescribed constant input (not a predicted profile)"},
                 "bed_depth": {"value": float(L), "unit": "m"}},
                {"darcy_flux": {"value": float(q), "unit": "m/s"},
                 "mass_flow": {"value": float(math.pi * cam_model.R0 ** 2 * q * cam_model.RHO_OUT * 1000),
                               "unit": "g/s"},
                 "shot_duration": {"value": float(t_shot), "unit": "s"}},
                find("pressure_bar"), time.monotonic() - t0,
                "constant-pressure Darcy flow; no dynamic channeling, wetting front, or preinfusion transient")
    stages.append(mf)
    for f in mf.domain_findings:
        if f.status is DomainStatus.WARNING:
            _emit(progress, PullEvent.STAGE_WARNING, {"stage": "machine_flow", "field": f.field})
    _emit(progress, PullEvent.STAGE_COMPLETED, {"stage": "machine_flow"})

    # Extraction + Cup stage: the full BDF solve
    seq += 1
    _emit(progress, PullEvent.STAGE_STARTED, {"stage": "extraction"})
    t0 = time.monotonic()
    shot = cam_model.simulate_shot(gs=gs, p_bar=recipe.pressure_bar, m_in=m_in, m_out=m_out,
                                   N=config.grid_N, M=config.grid_M)
    solve_s = time.monotonic() - t0
    # Validate the solver outputs before they reach any report field — a non-finite yield / TDS /
    # duration / dissolved mass becomes a controlled PullExecutionError, never inf/nan in the JSON.
    _require_finite("extraction_yield", shot.EY)
    _require_finite("tds", shot.tds)
    _require_finite_positive("shot_duration", shot.t_shot)
    _require_finite("dissolved_mass", float(shot.m_cup[-1]))
    # DIAGNOSTIC, NOT physical first drip: the first time modeled cup solute becomes positive. The
    # primary model starts from a SATURATED bed and does not solve wetting/hydraulic breakthrough.
    first_arrival = next((float(shot.t[i]) for i in range(len(shot.t)) if shot.m_cup[i] > 0), 0.0)
    ex = _stage("extraction", seq, cam,
                "Solute dissolves from the grounds into the flowing water and reaches the cup.",
                "BDF integration of the single-solute two-family bed model (Cameron Eqs.)",
                {"dose": {"value": recipe.dose_g, "unit": "g"},
                 "target_beverage": {"value": recipe.target_beverage_g, "unit": "g"},
                 "temperature": {"value": recipe.brew_temperature_c, "unit": "degC",
                                 "note": "recorded-only; not a model input (no thermal transient)"}},
                {"extraction_yield": {"value": float(shot.EY), "unit": "%"},
                 "tds": {"value": float(shot.tds), "unit": "%"},
                 "dissolved_mass": {"value": float(shot.m_cup[-1]) * 1000, "unit": "g"},
                 "first_modeled_solute_arrival": {"value": float(first_arrival), "unit": "s",
                     "note": "numerical diagnostic, NOT physical first drip (saturated-bed model)"}},
                find("brew_temperature_c") + find("dose_g") + find("target_beverage_g"),
                solve_s, "EY ceiling ~29.6% (per-bed-volume inventory); temperature enters only "
                         "through the recorded recipe, not a resolved thermal transient")
    stages.append(ex)
    _emit(progress, PullEvent.STAGE_COMPLETED, {"stage": "extraction"})

    traces = _build_traces(cam_model, cam, recipe, gs, q, shot)

    extracted_g = float(shot.EY) / 100.0 * recipe.dose_g
    final_obs = {
        "pressure_bar": {"value": recipe.pressure_bar, "unit": "bar",
                         "note": "prescribed constant input (v1); not a predicted profile"},
        "mean_flow_g_s": {"value": float(recipe.target_beverage_g / t_shot), "unit": "g/s",
                          "note": "constant model flow"},
        "first_drip_s": {"value": None, "unit": "s", "status": "unavailable",
                         "reason": "the primary configuration begins from a saturated bed and does not "
                                   "model puck wetting or hydraulic breakthrough"},
        "first_modeled_solute_arrival_s": {"value": float(first_arrival), "unit": "s",
                         "status": "diagnostic",
                         "note": "numerical diagnostic: first time modeled cup solute > 0; NOT physical first drip"},
        "shot_duration_s": {"value": float(shot.t_shot), "unit": "s"},
        "beverage_mass_g": {"value": recipe.target_beverage_g, "unit": "g"},
        "extracted_mass_g": {"value": float(extracted_g), "unit": "g"},
        "extraction_yield_pct": {"value": float(shot.EY), "unit": "%"},
        "tds_pct": {"value": float(shot.tds), "unit": "%"},
        "composition": {"value": "single soluble pool (no per-species composition in this model)",
                        "unit": "-"},
    }

    coverage = _coverage()
    warn_msgs = tuple(f"{f.field}: {f.plain_explanation}" for f in warns)
    completion = "completed_with_warnings" if warns else "completed"
    run_id = _run_id(recipe, config)
    _emit(progress, PullEvent.RUN_COMPLETED, {"run_id": run_id, "state": completion})

    return PullRun(
        schema_version=PULL_RUN_SCHEMA_VERSION, package_version=puckworks.__version__,
        source_commit=None, run_id=run_id, recipe=recipe, config=config,
        stages=tuple(stages), lenses=(), traces=traces, final_observables=final_obs,
        domain_findings=findings, assumptions_summary=(cam.assumptions,), coverage=coverage,
        warnings=warn_msgs, completion_state=completion)


def _run_id(recipe: PullRecipe, config: PullConfig) -> str:
    """Deterministic run id from configuration + inputs (no wall clock, no rendered files)."""
    rd = _recipe_dict(recipe)
    rd.pop("bean_label", None); rd.pop("notes", None)   # metadata only — must not change the run id
    payload = json.dumps({"recipe": rd, "config": _config_dict(config)}, sort_keys=True)
    return "pull-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# ─────────────────────────────── presets ─────────────────────────────────────────
def available_pull_presets() -> tuple[str, ...]:
    return ("pv19_named", "guided_v1")


def load_pull_preset(preset_id: str) -> tuple[PullRecipe, PullConfig]:
    if preset_id == "pv19_named":
        recipe = PullRecipe(dose_g=20.0, target_beverage_g=40.0, brew_temperature_c=93.0,
                            pressure_bar=9.0, grinder_model="EK43", coffee_profile="reference",
                            grind_setting=1.7, bean_label="reference named shot")
        config = PullConfig(config_id="pv19_named", config_version=1,
                            stage_components=dict(_EXPECTED_STAGE_COMPONENTS),
                            domain_policy="warn", editable_fields=())
        return recipe, config
    if preset_id == "guided_v1":
        recipe = PullRecipe(dose_g=20.0, target_beverage_g=40.0, brew_temperature_c=93.0,
                            pressure_bar=9.0, grinder_model="EK43", coffee_profile="reference",
                            grind_setting=1.7)
        config = PullConfig(config_id="guided_v1", config_version=1,
                            stage_components=dict(_EXPECTED_STAGE_COMPONENTS),
                            domain_policy="warn",
                            editable_fields=("dose_g", "target_beverage_g", "brew_temperature_c",
                                             "pressure_bar", "grind_setting", "coffee_profile",
                                             "bean_label", "domain_policy"))
        return recipe, config
    raise PullDomainError(f"unknown preset {preset_id!r}; known: {available_pull_presets()}")


# ─────────────────────────────── serialization ───────────────────────────────────
def _recipe_dict(r: PullRecipe) -> dict:
    return {k: getattr(r, k) for k in (
        "dose_g", "target_beverage_g", "brew_temperature_c", "pressure_bar", "grinder_model",
        "coffee_profile", "grind_setting", "mean_particle_radius_m", "preinfusion_s",
        "preinfusion_pressure_bar", "basket_diameter_mm", "bean_label", "notes")}


def _config_dict(c: PullConfig) -> dict:
    return {"config_id": c.config_id, "config_version": c.config_version,
            "stage_components": _thaw(c.stage_components), "domain_policy": c.domain_policy,
            "pressure_profile": c.pressure_profile, "lenses": list(c.lenses),
            "grid_N": c.grid_N, "grid_M": c.grid_M,
            "editable_fields": None if c.editable_fields is None else list(c.editable_fields)}


def _finding_dict(f: DomainFinding) -> dict:
    return {"status": f.status.value, "field": f.field, "supplied_value": f.supplied_value,
            "supported_range": f.supported_range, "units": f.units, "component": f.component,
            "technical_reason": f.technical_reason, "plain_explanation": f.plain_explanation,
            "suggested_action": f.suggested_action, "source": f.source}


def _series_dict(s: PullSeries) -> dict:
    return {"series_id": s.series_id, "label": s.label, "values": list(s.values), "unit": s.unit,
            "role": s.role, "method": s.method, "caveat": s.caveat,
            "domain_findings": [_finding_dict(f) for f in s.domain_findings]}


def _trace_dict(t: PullTrace) -> dict:
    return {"trace_id": t.trace_id, "stage_id": t.stage_id, "component_id": t.component_id,
            "axis_label": t.axis_label, "axis_unit": t.axis_unit, "axis_values": list(t.axis_values),
            "series": [_series_dict(s) for s in t.series], "method": t.method,
            "evidence_badge": t.evidence_badge, "evidence_strength": t.evidence_strength,
            "fidelity_ceiling": t.fidelity_ceiling, "assumptions": t.assumptions, "caveat": t.caveat}


def _stage_dict(s: StageResult) -> dict:
    return {"stage_id": s.stage_id, "sequence": s.sequence, "component_id": s.component_id,
            "source_citation": s.source_citation, "execution_role": s.execution_role,
            "method_name": s.method_name, "method_plain": s.method_plain,
            "method_technical": s.method_technical, "inputs": _thaw(s.inputs), "outputs": _thaw(s.outputs),
            "evidence_badge": s.evidence_badge, "evidence_strength": s.evidence_strength,
            "provenance_class": s.provenance_class, "assumptions": s.assumptions,
            "valid_range": s.valid_range,
            "domain_findings": [_finding_dict(f) for f in s.domain_findings],
            "fitted_parameters": _thaw(s.fitted_parameters), "success": s.success, "caveat": s.caveat,
            "references": s.references}    # runtime_s intentionally excluded (nondeterministic)


def pull_run_to_dict(run: PullRun) -> dict:
    """Deterministic scientific payload (NO wall-clock time / runtime — run_id derives from inputs).
    Trace series carry full solver precision; only display renderers round."""
    return {
        "schema_version": run.schema_version, "package_version": run.package_version,
        "source_commit": run.source_commit, "run_id": run.run_id,
        "recipe": _recipe_dict(run.recipe), "config": _config_dict(run.config),
        "stages": [_stage_dict(s) for s in run.stages],
        "lenses": [_stage_dict(s) for s in run.lenses],
        "traces": [_trace_dict(t) for t in run.traces],
        "final_observables": _thaw(run.final_observables),
        "domain_findings": [_finding_dict(f) for f in run.domain_findings],
        "assumptions_summary": list(run.assumptions_summary),
        "coverage": [{"component_id": c.component_id, "stage": c.stage,
                      "disposition": c.disposition.value, "executed": c.executed,
                      "reason": c.reason} for c in run.coverage],
        "warnings": list(run.warnings), "completion_state": run.completion_state,
    }


def pull_run_to_json(run: PullRun) -> str:
    return json.dumps(pull_run_to_dict(run), indent=2, sort_keys=True, ensure_ascii=False,
                      allow_nan=False) + "\n"


def _disp(x):
    """Round a float to DISPLAY precision (4 decimals) for human-facing markdown/summary output.
    Non-floats pass through. The serialized JSON payload keeps FULL solver precision (PW-PULL-007);
    rounding lives only in the renderers."""
    return round(x, 4) if isinstance(x, float) else x


def _fmt_obs(k: str, v: dict) -> str:
    """One-line rendering of a final observable, honest about unavailable/diagnostic status."""
    status = v.get("status")
    if status == "unavailable":
        return f"- **{k}**: unavailable — {v.get('reason', 'not modeled')}"
    val = _disp(v.get("value"))
    unit = v.get("unit", "")
    line = f"- **{_md(k)}**: {val} {_md(unit)}".rstrip()
    if status == "diagnostic":
        line += f" _(diagnostic — {v.get('note', '')})_"
    return line


def pull_run_to_markdown(run: PullRun) -> str:
    r, obs = run.recipe, run.final_observables
    lines = [
        f"# Guided Espresso Pull — {run.config.config_id}",
        "",
        f"*Exploratory simulation (a model-backed coffee profile, not a taste prediction or digital "
        f"twin). Run id `{run.run_id}` · state: **{run.completion_state}**.*",
        "",
        "## Recipe",
        f"- {r.dose_g} g in → {r.target_beverage_g} g out · {r.pressure_bar} bar · {_md(r.grinder_model)} "
        f"dial {r.grind_setting} · profile `{_md(r.coffee_profile)}`"
        + (f" · bean *{_md(r.bean_label)}* (label only)" if r.bean_label else ""),
        f"- brew temperature {r.brew_temperature_c} °C — *recorded-only; not a model input in v0.3.0*",
        "",
        "## Final observables",
    ]
    lines += [_fmt_obs(k, v) for k, v in obs.items()]
    lines += ["", "## Stages (Recipe → Grind → Machine/Flow → Extraction → Cup)"]
    for s in run.stages:
        lines.append(f"### {s.sequence}. {s.stage_id} — {s.method_name} [{s.evidence_badge}]")
        lines.append(_md(s.method_plain))
        lines.append("- inputs: " + ", ".join(f"{_md(k)}={_disp(x['value'])} {_md(x['unit'])}".rstrip()
                                                for k, x in s.inputs.items()))
        lines.append("- outputs: " + ", ".join(f"{_md(k)}={_disp(x['value'])} {_md(x['unit'])}".rstrip()
                                                 for k, x in s.outputs.items()))
        lines.append(f"- evidence: {s.evidence_strength} · valid range: {s.valid_range}")
        lines.append(f"- caveat: {_md(s.caveat)}")
    lines += ["", "## Authoritative traces (static text equivalent of the figures)"]
    for t in run.traces:
        lines.append(f"### {t.trace_id} — vs {t.axis_label} ({t.axis_unit}) [{t.evidence_badge}]")
        lines.append(f"- fidelity ceiling: {t.fidelity_ceiling}")
        for ser in t.series:
            end = ser.values[-1] if ser.values else float("nan")
            lines.append(f"- **{_md(ser.label)}** ({ser.role}, {_md(ser.unit)}): endpoint {round(end, 4)} — {_md(ser.method)}")
    if run.warnings:
        lines += ["", "## ⚠ Domain warnings"] + [f"- {w}" for w in run.warnings]
    lines += ["", "## Component coverage"]
    for c in run.coverage:
        mark = "executed" if c.executed else "not executed"
        lines.append(f"- `{_md(c.component_id)}` ({c.stage}): **{c.disposition.value}** ({mark}) — {_md(c.reason)}")
    lines += ["", "## What this does not prove",
              "- Not your actual puck, not a flavor/taste prediction, not the 'best' recipe.",
              "- Physical first drip and puck wetting are NOT modeled (the primary model starts from a "
              "saturated bed).",
              "- Pressure is a prescribed constant input, not a predicted dynamic profile. Temperature "
              "is recorded-only.",
              "- Alternative components are separate scientific views; none were executed or averaged "
              "into a consensus in this run.",
              f"- Assumptions: {'; '.join(run.assumptions_summary)}"]
    return "\n".join(lines) + "\n"


def render_pull_report(run: PullRun, out_dir, *, overwrite: bool = False) -> PullReportArtifacts:
    """Render the guided-pull visual report (JSON + Markdown + figures) from an ALREADY-COMPLETED
    :class:`PullRun`. The renderer never calls :func:`simulate_pull`, never mutates the run, and
    never recomputes scientific values — it reads ``run.traces`` and ``run.final_observables``.

    Figures need the optional visualization dependencies (``puckworks[viz]``); JSON/Markdown/CLI
    summary paths do not. Importing this function does not import matplotlib — the viz backend is
    loaded lazily here so ``puckworks.product`` stays matplotlib-free.
    """
    from puckworks.viz.pull_report import render as _render      # lazy: no matplotlib at import
    return _render(run, out_dir, overwrite=overwrite)


def pull_run_summary(run: PullRun) -> str:
    obs = run.final_observables
    return (f"[{run.completion_state}] {run.config.config_id} {run.run_id}: "
            f"EY {_disp(obs['extraction_yield_pct']['value'])}% · TDS {_disp(obs['tds_pct']['value'])}% · "
            f"{_disp(obs['shot_duration_s']['value'])}s · {_disp(obs['beverage_mass_g']['value'])}g · "
            f"first drip unavailable (not modeled)"
            + (f" · {len(run.warnings)} warning(s)" if run.warnings else ""))
