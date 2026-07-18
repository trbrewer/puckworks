"""Guided Espresso Pull — a rights-independent, runnable guided mechanism explorer (issue #48).

A user enters a bounded recipe and runs an end-to-end model *configuration* on CPU. The primary
chain is anchored on the coherent, self-contained ``cameron2020.extraction_bdf`` shot model (which
internally spans grind -> flow -> extraction -> cup); every other registered component receives an
explicit **coverage disposition** rather than being silently forced into one calculation. This is a
guided *mechanism explorer*, not an optimizer, a flavor predictor, or a digital twin.

Everything here is rights-independent: it computes from model code + caller inputs and ships/loads no
upstream fixture data. Chemical **composition** is reported where supported — never sensory flavor.
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import dataclass
from enum import Enum
from typing import Callable

import puckworks

PULL_RUN_SCHEMA_VERSION = 1

# EK43 dial range the primary model is documented for (evidence/calibration bounds), plus the wider
# solver-safe hard bounds. Sources: cameron2020.extraction_bdf card (valid_range) + solver limits.
_GS_EVIDENCE = (1.1, 2.3)
_GS_HARD = (1.0, 2.5)
_DOSE_EVIDENCE_G = (15.0, 25.0)
_BEV_EVIDENCE_G = (25.0, 60.0)
_TEMP_EVIDENCE_C = (85.0, 96.0)
_PRESSURE_EVIDENCE_BAR = (6.0, 9.0)


# ─────────────────────────────── enums ───────────────────────────────────────────
class DomainStatus(str, Enum):
    IN_DOMAIN = "in_domain"
    WARNING = "warning"
    REJECTED = "rejected"
    NOT_APPLICABLE = "not_applicable"


class ComponentDisposition(str, Enum):
    USED_PRIMARY = "used_primary"
    USED_ADAPTER = "used_adapter"
    COMPARED_AS_LENS = "compared_as_lens"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    CALIBRATION_ONLY = "calibration_only"
    NOT_APPLICABLE = "not_applicable"
    EXCLUDED_INCOMPATIBLE = "excluded_incompatible"
    EXCLUDED_OUT_OF_DOMAIN = "excluded_out_of_domain"
    EXCLUDED_OPTIONAL_DEPENDENCY = "excluded_optional_dependency"
    EXCLUDED_RUNTIME_BUDGET = "excluded_runtime_budget"


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
    component_version: str
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


@dataclass(frozen=True)
class PullConfig:
    config_id: str
    config_version: int
    stage_components: dict     # stage -> component_id (primary chain)
    domain_policy: str = "warn"   # "warn" | "strict"
    lenses: tuple[str, ...] = ()
    grid_N: int = 40
    grid_M: int = 24
    seed: int = 0
    editable_fields: tuple[str, ...] = ()   # which recipe fields guided mode may change

    def __post_init__(self):
        if self.domain_policy not in ("warn", "strict"):
            raise PullDomainError("domain_policy must be 'warn' or 'strict'")


@dataclass(frozen=True)
class ComponentCoverage:
    component_id: str
    stage: str
    disposition: ComponentDisposition
    reason: str


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
    final_observables: dict
    domain_findings: tuple[DomainFinding, ...]
    assumptions_summary: tuple[str, ...]
    coverage: tuple[ComponentCoverage, ...]
    warnings: tuple[str, ...]
    completion_state: str      # "completed" | "completed_with_warnings" | "failed"
    started_at: float = 0.0    # wall-clock (NOT part of the deterministic payload)
    ended_at: float = 0.0
    runtime_s: float = 0.0


# ─────────────────────────────── coffee profiles ─────────────────────────────────
# The reference profile is model-backed by cameron2020's built-in microstructure/inventory; it does
# not invent parameters and is not selected by a bean name.
_PROFILES: dict[str, CoffeeProfile] = {
    "reference": CoffeeProfile(
        profile_id="reference",
        source="cameron2020.extraction_bdf built-in microstructure + single soluble pool",
        supported_components=("cameron2020.extraction_bdf",),
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
                         "cameron2020.extraction_bdf", reason, plain, action, "solver/physical limits")


def _evidence(field, value, lo, hi, units, plain):
    if lo <= value <= hi:
        return DomainFinding(DomainStatus.IN_DOMAIN, field, value, f"{lo}-{hi}", units,
                             "cameron2020.extraction_bdf", "within documented evidence range",
                             plain, "", "cameron2020.extraction_bdf card")
    return DomainFinding(DomainStatus.WARNING, field, value, f"{lo}-{hi}", units,
                         "cameron2020.extraction_bdf",
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
    WARNING. Never clamps."""
    gs = recipe.grind_setting
    findings: list[DomainFinding | None] = [
        _hard("dose_g", recipe.dose_g, recipe.dose_g > 0, ">0", "g",
              "dose must be positive", "You must use some coffee.", "set a positive dose"),
        _hard("target_beverage_g", recipe.target_beverage_g, recipe.target_beverage_g > 0, ">0", "g",
              "beverage mass must be positive", "The cup must hold some liquid.", "set a positive target"),
        _hard("brew_temperature_c", recipe.brew_temperature_c, 0 < recipe.brew_temperature_c < 100,
              "0-100 (exclusive)", "degC", "temperature must be a liquid-water brew temperature",
              "Brew temperature must be between 0 and 100 C.", "use ~85-96 C"),
        _hard("pressure_bar", recipe.pressure_bar, recipe.pressure_bar > 0, ">0", "bar",
              "pump overpressure must be positive", "The pump must push.", "use ~6-9 bar"),
    ]
    if gs is not None:
        findings.append(_hard("grind_setting", gs, _GS_HARD[0] <= gs <= _GS_HARD[1],
                              f"{_GS_HARD[0]}-{_GS_HARD[1]}", "EK43 dial",
                              "grind setting outside the solver-safe range",
                              "This grind is too far outside the model's stable range to compute.",
                              f"use an EK43 dial in {_GS_EVIDENCE[0]}-{_GS_EVIDENCE[1]}"))
    hard = [f for f in findings if f is not None]
    if any(f.status is DomainStatus.REJECTED for f in hard):
        return tuple(hard)

    ev = [
        _evidence("grind_setting", gs, *_GS_EVIDENCE, "EK43 dial", "How fine the coffee is ground.") if gs is not None else None,
        _evidence("dose_g", recipe.dose_g, *_DOSE_EVIDENCE_G, "g", "How much dry coffee."),
        _evidence("target_beverage_g", recipe.target_beverage_g, *_BEV_EVIDENCE_G, "g", "How much espresso in the cup."),
        _evidence("brew_temperature_c", recipe.brew_temperature_c, *_TEMP_EVIDENCE_C, "degC", "Water temperature."),
        _evidence("pressure_bar", recipe.pressure_bar, *_PRESSURE_EVIDENCE_BAR, "bar", "Pump pressure."),
    ]
    return tuple(f for f in ev if f is not None)


# ─────────────────────────────── coverage ledger ─────────────────────────────────
# Honest disposition of every registered component relative to the guided-pull primary chain. The
# primary model internally spans grind/flow/extraction/cup; the rest are calibration, parallel
# lenses, or not compatible with the primary contract without a verified adapter.
_COVERAGE_RULES: dict[str, tuple[ComponentDisposition, str]] = {
    "cameron2020.extraction_bdf": (ComponentDisposition.USED_PRIMARY,
        "coherent self-contained shot model spanning grind->flow->extraction->cup"),
}
_STAGE_DEFAULT: dict[str, tuple[ComponentDisposition, str]] = {
    "extraction": (ComponentDisposition.COMPARED_AS_LENS,
        "alternative extraction lineage; not coupled into the primary chain (conventions/inventory differ) — runs only as a separate lens"),
    "flow": (ComponentDisposition.CALIBRATION_ONLY, "calibration/flow-closure input, not a runtime primary stage"),
    "grind": (ComponentDisposition.CALIBRATION_ONLY, "grind calibration map, not runtime physics"),
    "packing": (ComponentDisposition.CALIBRATION_ONLY, "bed/permeability calibration input"),
    "bed_dynamics": (ComponentDisposition.COMPARED_AS_LENS,
        "bed-dynamics model on a different reference frame; not coupled to the primary chain without a verified adapter"),
    "machine": (ComponentDisposition.COMPARED_AS_LENS,
        "machine/pump model with its own dimensionless frame; parallel lens only"),
    "infiltration": (ComponentDisposition.COMPARED_AS_LENS,
        "unsaturated-flow/wetting model; the primary model assumes a saturated bed from t=0 (parallel lens only)"),
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
                (ComponentDisposition.NOT_APPLICABLE, "no defined role in the guided-pull chain"))
        out.append(ComponentCoverage(c.name, c.stage, disp, reason))
    return tuple(out)


# ─────────────────────────────── orchestration ───────────────────────────────────
def _component_meta(component_id: str):
    puckworks.load_builtin_components()
    return puckworks.get(component_id)


def _emit(progress, event, payload):
    if progress is not None:
        progress(event, payload)


def _stage(stage_id, seq, cam, method_plain, method_technical, inputs, outputs, findings, runtime_s, caveat):
    return StageResult(
        stage_id=stage_id, sequence=seq, component_id="cameron2020.extraction_bdf",
        component_version=cam.paper, execution_role=cam.execution_role,
        method_name="cameron2020 BDF single-solute bed model",
        method_plain=method_plain, method_technical=method_technical,
        inputs=inputs, outputs=outputs, evidence_badge="simulated",
        evidence_strength=cam.evidence_strength, provenance_class=cam.provenance_class,
        assumptions=cam.assumptions, valid_range=cam.valid_range,
        domain_findings=tuple(findings), fitted_parameters={}, runtime_s=runtime_s,
        success=True, caveat=caveat, references=f"{cam.paper}; doi:{cam.doi}")


def simulate_pull(recipe: PullRecipe, config: PullConfig, *,
                  progress: ProgressCallback | None = None) -> PullRun:
    """Run the guided espresso pull. Raises :class:`PullDomainError` on hard-invalid input, or on an
    evidence-range departure under ``domain_policy='strict'``. The result serializes deterministically.
    """
    from puckworks.models.cameron2020 import extraction_bdf as cam_model

    _profile(recipe.coffee_profile)                     # validate profile (never bean-derived)
    started = time.monotonic()
    _emit(progress, PullEvent.RUN_STARTED, {"config": config.config_id})

    findings = evaluate_domain(recipe)
    if any(f.status is DomainStatus.REJECTED for f in findings):
        _emit(progress, PullEvent.RUN_FAILED, {"reason": "rejected input"})
        raise PullDomainError("recipe rejected: " + "; ".join(
            f"{f.field}={f.supplied_value} ({f.technical_reason})"
            for f in findings if f.status is DomainStatus.REJECTED))
    warns = [f for f in findings if f.status is DomainStatus.WARNING]
    if warns and config.domain_policy == "strict":
        _emit(progress, PullEvent.RUN_FAILED, {"reason": "strict domain"})
        raise PullDomainError("strict domain policy: out-of-range " + ", ".join(f.field for f in warns))

    gs = _grind_setting(recipe)
    cam = _component_meta("cameron2020.extraction_bdf")
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
                {"fines_fraction": {"value": round(float(phi1), 4), "unit": "-"},
                 "boulder_fraction": {"value": round(float(phi2), 4), "unit": "-"},
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
    L = cam_model.bed_depth(m_in)
    q = cam_model.darcy_flux(gs, recipe.pressure_bar, L=L, L_ref=cam_model.bed_depth(0.020))
    t_shot = m_out / (math.pi * cam_model.R0 ** 2 * cam_model.RHO_OUT * q)
    mf = _stage("machine_flow", seq, cam,
                "Pump pressure drives flow through the bed (Darcy), setting the shot time.",
                "darcy_flux(gs, p_bar); t_shot = m_out / (pi R0^2 rho_out q)",
                {"pressure": {"value": recipe.pressure_bar, "unit": "bar"},
                 "bed_depth": {"value": round(L, 5), "unit": "m"}},
                {"darcy_flux": {"value": float(q), "unit": "m/s"},
                 "shot_duration": {"value": round(t_shot, 2), "unit": "s"}},
                find("pressure_bar"), time.monotonic() - t0,
                "constant-pressure Darcy flow; no dynamic channeling or preinfusion transient")
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
    # first drip: first time cumulative dissolved mass becomes positive
    first_drip = next((float(shot.t[i]) for i in range(len(shot.t)) if shot.m_cup[i] > 0), 0.0)
    ex = _stage("extraction", seq, cam,
                "Solute dissolves from the grounds into the flowing water and reaches the cup.",
                "BDF integration of the single-solute two-family bed model (Cameron Eqs.)",
                {"dose": {"value": recipe.dose_g, "unit": "g"},
                 "target_beverage": {"value": recipe.target_beverage_g, "unit": "g"},
                 "temperature": {"value": recipe.brew_temperature_c, "unit": "degC"}},
                {"extraction_yield": {"value": round(float(shot.EY), 2), "unit": "%"},
                 "tds": {"value": round(float(shot.tds), 2), "unit": "%"},
                 "dissolved_mass": {"value": round(float(shot.m_cup[-1]) * 1000, 3), "unit": "g"},
                 "first_drip": {"value": round(first_drip, 2), "unit": "s"}},
                find("brew_temperature_c") + find("dose_g") + find("target_beverage_g"),
                solve_s, "EY ceiling ~29.6% (per-bed-volume inventory); temperature enters only "
                         "through the recorded recipe, not a resolved thermal transient")
    stages.append(ex)
    _emit(progress, PullEvent.STAGE_COMPLETED, {"stage": "extraction"})

    extracted_g = float(shot.EY) / 100.0 * recipe.dose_g
    final_obs = {
        "pressure_bar": {"value": recipe.pressure_bar, "unit": "bar", "note": "constant profile (v1)"},
        "mean_flow_g_s": {"value": round(recipe.target_beverage_g / t_shot, 3), "unit": "g/s"},
        "first_drip_s": {"value": round(first_drip, 2), "unit": "s"},
        "shot_duration_s": {"value": round(float(shot.t_shot), 2), "unit": "s"},
        "beverage_mass_g": {"value": recipe.target_beverage_g, "unit": "g"},
        "extracted_mass_g": {"value": round(extracted_g, 3), "unit": "g"},
        "extraction_yield_pct": {"value": round(float(shot.EY), 2), "unit": "%"},
        "tds_pct": {"value": round(float(shot.tds), 2), "unit": "%"},
        "composition": {"value": "single soluble pool (no per-species composition in this model)",
                        "unit": "-"},
    }

    coverage = _coverage()
    warn_msgs = tuple(f"{f.field}: {f.plain_explanation}" for f in warns)
    completion = "completed_with_warnings" if warns else "completed"
    run_id = _run_id(recipe, config)
    _emit(progress, PullEvent.RUN_COMPLETED, {"run_id": run_id, "state": completion})
    ended = time.monotonic()

    return PullRun(
        schema_version=PULL_RUN_SCHEMA_VERSION, package_version=puckworks.__version__,
        source_commit=None, run_id=run_id, recipe=recipe, config=config,
        stages=tuple(stages), lenses=(), final_observables=final_obs, domain_findings=findings,
        assumptions_summary=(cam.assumptions,), coverage=coverage, warnings=warn_msgs,
        completion_state=completion, started_at=0.0, ended_at=0.0, runtime_s=round(ended - started, 3))


def _run_id(recipe: PullRecipe, config: PullConfig) -> str:
    """Deterministic run id from configuration + inputs (no wall clock)."""
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
                            stage_components={"grind": "cameron2020.extraction_bdf",
                                              "machine_flow": "cameron2020.extraction_bdf",
                                              "extraction": "cameron2020.extraction_bdf"},
                            domain_policy="warn", editable_fields=())
        return recipe, config
    if preset_id == "guided_v1":
        recipe = PullRecipe(dose_g=20.0, target_beverage_g=40.0, brew_temperature_c=93.0,
                            pressure_bar=9.0, grinder_model="EK43", coffee_profile="reference",
                            grind_setting=1.7)
        config = PullConfig(config_id="guided_v1", config_version=1,
                            stage_components={"grind": "cameron2020.extraction_bdf",
                                              "machine_flow": "cameron2020.extraction_bdf",
                                              "extraction": "cameron2020.extraction_bdf"},
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
            "stage_components": c.stage_components, "domain_policy": c.domain_policy,
            "lenses": list(c.lenses), "grid_N": c.grid_N, "grid_M": c.grid_M, "seed": c.seed,
            "editable_fields": list(c.editable_fields)}


def _finding_dict(f: DomainFinding) -> dict:
    return {"status": f.status.value, "field": f.field, "supplied_value": f.supplied_value,
            "supported_range": f.supported_range, "units": f.units, "component": f.component,
            "technical_reason": f.technical_reason, "plain_explanation": f.plain_explanation,
            "suggested_action": f.suggested_action, "source": f.source}


def _stage_dict(s: StageResult) -> dict:
    return {"stage_id": s.stage_id, "sequence": s.sequence, "component_id": s.component_id,
            "component_version": s.component_version, "execution_role": s.execution_role,
            "method_name": s.method_name, "method_plain": s.method_plain,
            "method_technical": s.method_technical, "inputs": s.inputs, "outputs": s.outputs,
            "evidence_badge": s.evidence_badge, "evidence_strength": s.evidence_strength,
            "provenance_class": s.provenance_class, "assumptions": s.assumptions,
            "valid_range": s.valid_range,
            "domain_findings": [_finding_dict(f) for f in s.domain_findings],
            "fitted_parameters": s.fitted_parameters, "success": s.success, "caveat": s.caveat,
            "references": s.references}    # runtime_s intentionally excluded (nondeterministic)


def pull_run_to_dict(run: PullRun) -> dict:
    """Deterministic scientific payload (NO wall-clock time / runtime — run_id derives from inputs)."""
    return {
        "schema_version": run.schema_version, "package_version": run.package_version,
        "source_commit": run.source_commit, "run_id": run.run_id,
        "recipe": _recipe_dict(run.recipe), "config": _config_dict(run.config),
        "stages": [_stage_dict(s) for s in run.stages],
        "lenses": [_stage_dict(s) for s in run.lenses],
        "final_observables": run.final_observables,
        "domain_findings": [_finding_dict(f) for f in run.domain_findings],
        "assumptions_summary": list(run.assumptions_summary),
        "coverage": [{"component_id": c.component_id, "stage": c.stage,
                      "disposition": c.disposition.value, "reason": c.reason} for c in run.coverage],
        "warnings": list(run.warnings), "completion_state": run.completion_state,
    }


def pull_run_to_json(run: PullRun) -> str:
    return json.dumps(pull_run_to_dict(run), indent=2, sort_keys=True, ensure_ascii=False,
                      allow_nan=False) + "\n"


def pull_run_to_markdown(run: PullRun) -> str:
    r, obs = run.recipe, run.final_observables
    lines = [
        f"# Guided Espresso Pull — {run.config.config_id}",
        "",
        f"*Exploratory simulation (a model-backed coffee profile, not a taste prediction or digital "
        f"twin). Run id `{run.run_id}` · state: **{run.completion_state}**.*",
        "",
        "## Recipe",
        f"- {r.dose_g} g in → {r.target_beverage_g} g out · {r.brew_temperature_c} °C · "
        f"{r.pressure_bar} bar · {r.grinder_model} dial {r.grind_setting} · profile "
        f"`{r.coffee_profile}`" + (f" · bean *{r.bean_label}* (label only)" if r.bean_label else ""),
        "",
        "## Final observables",
    ]
    for k, v in obs.items():
        lines.append(f"- **{k}**: {v['value']} {v['unit']}".rstrip())
    lines += ["", "## Stages (Recipe → Grind → Machine/Flow → Extraction → Cup)"]
    for s in run.stages:
        badge = s.evidence_badge
        lines.append(f"### {s.sequence}. {s.stage_id} — {s.method_name} [{badge}]")
        lines.append(f"{s.method_plain}")
        lines.append("- inputs: " + ", ".join(f"{k}={x['value']} {x['unit']}".rstrip()
                                                for k, x in s.inputs.items()))
        lines.append("- outputs: " + ", ".join(f"{k}={x['value']} {x['unit']}".rstrip()
                                                 for k, x in s.outputs.items()))
        lines.append(f"- evidence: {s.evidence_strength} · valid range: {s.valid_range}")
        lines.append(f"- caveat: {s.caveat}")
    if run.warnings:
        lines += ["", "## ⚠ Domain warnings"] + [f"- {w}" for w in run.warnings]
    lines += ["", "## Component coverage"]
    for c in run.coverage:
        lines.append(f"- `{c.component_id}` ({c.stage}): **{c.disposition.value}** — {c.reason}")
    lines += ["", "## What this does not prove",
              "- Not your actual puck, not a flavor/taste prediction, not the 'best' recipe.",
              "- Parallel lenses (if any) are separate scientific views, never averaged into a consensus.",
              f"- Assumptions: {'; '.join(run.assumptions_summary)}"]
    return "\n".join(lines) + "\n"


def pull_run_summary(run: PullRun) -> str:
    obs = run.final_observables
    return (f"[{run.completion_state}] {run.config.config_id} {run.run_id}: "
            f"EY {obs['extraction_yield_pct']['value']}% · TDS {obs['tds_pct']['value']}% · "
            f"{obs['shot_duration_s']['value']}s · {obs['beverage_mass_g']['value']}g"
            + (f" · {len(run.warnings)} warning(s)" if run.warnings else ""))
