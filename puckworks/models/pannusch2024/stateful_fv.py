"""Explicit chemical states and checked continuation of the prescribed-Q/T FV model.

RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED. Pannusch et al.,
10.1016/j.jfoodeng.2023.111887; source-derived output CC-BY-NC-3.0
(10.17632/y2tz67f6ry.1), separately from first-party code licensing.
"""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, field
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from . import flow_temperature_history_fv as fv
from .flow_history import _real, _reals

FVSettings = fv.FVSettings
FlowHistory = fv.FlowHistory
TemperatureHistory = fv.TemperatureHistory
SCHEMA_VERSION = 1
BASES = fv.th.BASES[:3]
ALGORITHM = "pannusch2024.stateful_fv.interval_local_accumulator.v1"


def _json(value):
    if is_dataclass(value):
        return {f.name: _json(getattr(value, f.name)) for f in fields(value)
                if f.name != "identity_sha256"}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (tuple, list)):
        return [_json(v) for v in value]
    if isinstance(value, dict):
        return {k: _json(v) for k, v in value.items()}
    if isinstance(value, np.generic):
        return value.item()
    return value


def _hash(value):
    def identity(v):
        if isinstance(v, np.ndarray):
            return dict(shape=list(v.shape), dtype=v.dtype.str,
                        data_sha256=hashlib.sha256(v.tobytes()).hexdigest())
        if is_dataclass(v):
            return {f.name: identity(getattr(v, f.name)) for f in fields(v)
                    if f.name != "identity_sha256"}
        if isinstance(v, (tuple, list)):
            return [identity(x) for x in v]
        if isinstance(v, dict):
            return {k: identity(x) for k, x in v.items()}
        return _json(v)
    return hashlib.sha256(json.dumps(identity(value), sort_keys=True, allow_nan=False,
                                    separators=(",", ":")).encode()).hexdigest()


def _sources():
    return (*fv._identities(), ("stateful_fv.py", hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))


def _geometry():
    return (("A_m2", fv.ps.ACS), ("L_m", fv.ps.L), ("alpha_l", fv.ps.ALPHA_L),
            ("phi_v2", fv.ps.PHI_V2), ("d1_m", fv.ps.D1_FINE))


def _configuration(solute, grind):
    return (tuple(sorted(fv.ps._solute_params()[solute].items())),
            tuple(sorted(fv.ps.GRINDS[grind].items())),
            tuple(sorted(fv.pc.SOLUTES[solute].items())))


def _inventory(liquid, fine, coarse, grind):
    """Independent physical-field inventory; fine has no phi_v2 factor."""
    psi = fv.ps.GRINDS[grind]["psi"]
    W = fv.ps.ACS*(fv.ps.L/len(liquid))
    return math.fsum([*(W*fv.ps.ALPHA_L*liquid),
                      *(W*psi*(1-fv.ps.ALPHA_L)*fine),
                      *(W*fv.ps.PHI_V2*(1-psi)*(1-fv.ps.ALPHA_L)*coarse)])


def _scaled(residual, scale):
    if scale == 0:
        return 0. if residual == 0 else None
    x = float(residual/scale)
    return x if math.isfinite(x) else None


def _within(residual, scale, tolerance):
    x = _scaled(residual, scale)
    return x is not None and abs(x) <= tolerance


def _freeze(obj):
    object.__setattr__(obj, "identity_sha256", "")
    fv._freeze_arrays(obj)
    object.__setattr__(obj, "identity_sha256", _hash(obj))


@dataclass(frozen=True, eq=False)
class FVChemicalState:
    """Three explicit cell averages on distinct source bases, never measured by implication."""
    solute: str
    grind: float
    time_s: float
    edges_m: np.ndarray
    liquid_cell_average_kg_m3: np.ndarray
    fine_cell_average_kg_m3: np.ndarray
    coarse_cell_average_kg_m3: np.ndarray
    initialization: str = "CALLER_SUPPLIED"
    equilibrium_temperature_K: float | None = None
    schema_version: int = SCHEMA_VERSION
    units_and_bases: tuple = BASES
    geometry: tuple = field(default_factory=_geometry)
    source_identities: tuple = field(default_factory=_sources)
    source_configuration: tuple = field(init=False)
    identity_sha256: str = field(init=False)

    def __post_init__(self):
        if not isinstance(self.solute, str) or self.solute not in fv.th.SPECIES:
            raise ValueError("UNKNOWN_SOURCE_SPECIES")
        g = _real(self.grind, "grind")
        if g not in fv.ps.GRINDS:
            raise ValueError("UNKNOWN_SOURCE_GRIND")
        t = _real(self.time_s, "model time")
        edges = np.asarray(_reals(self.edges_m, "cell edges", 2))
        n = len(edges)-1
        fv.fixed._integer(n, "cells", 1, 2000)
        if not np.array_equal(edges, np.linspace(0., fv.ps.L, n+1)):
            raise ValueError("INCOMPATIBLE_SOURCE_MESH_OR_GEOMETRY")
        if type(self.schema_version) is not int or self.schema_version != SCHEMA_VERSION:
            raise ValueError("INCOMPATIBLE_STATE_SCHEMA")
        if self.units_and_bases != BASES or self.geometry != _geometry():
            raise ValueError("INCOMPATIBLE_PHASE_BASES_OR_GEOMETRY")
        if self.source_identities != _sources():
            raise ValueError("INCOMPATIBLE_SOURCE_IDENTITY")
        arrays = []
        for name in ("liquid_cell_average_kg_m3", "fine_cell_average_kg_m3", "coarse_cell_average_kg_m3"):
            a = np.asarray(_reals(getattr(self, name), name, n))
            if a.shape != (n,) or np.any(a < 0):
                raise ValueError("INVALID_PHASE_SHAPE_OR_NEGATIVE_CONCENTRATION")
            arrays.append(a)
            object.__setattr__(self, name, a)
        system = fv._System(self.solute, g, n)
        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            m = np.concatenate(arrays)*system.capacities
        if not np.isfinite(m).all() or np.any((np.concatenate(arrays) > 0) & (m == 0)):
            raise ValueError("UNREPRESENTABLE_PHASE_MASS")
        try:
            inventory = _inventory(*arrays, g)
        except OverflowError as exc:
            raise ValueError("UNREPRESENTABLE_INVENTORY") from exc
        if not math.isfinite(inventory) or (any(np.any(a > 0) for a in arrays) and inventory <= 0):
            raise ValueError("UNREPRESENTABLE_INVENTORY")
        if self.initialization == "SOURCE_EQUILIBRIUM":
            T = _real(self.equilibrium_temperature_K, "equilibrium temperature K")
            if not 353.15 <= T <= 371.15:
                raise ValueError("EQUILIBRIUM_TEMPERATURE_DOMAIN")
            p = system.sp
            K = float(fv.pc.vant_hoff_K(T, p["K_ref"], p["gamma"]))
            if not np.array_equal(np.concatenate(arrays), np.repeat([K*p["c_s0"], p["c_s0"], p["c_s0"]], n)):
                raise ValueError("FALSE_SOURCE_EQUILIBRIUM_PROVENANCE")
        elif self.initialization != "CALLER_SUPPLIED" or self.equilibrium_temperature_K is not None:
            raise ValueError("INVALID_INITIALIZATION_PROVENANCE")
        object.__setattr__(self, "grind", g)
        object.__setattr__(self, "time_s", t)
        object.__setattr__(self, "edges_m", edges)
        object.__setattr__(self, "source_configuration", _configuration(self.solute, g))
        _freeze(self)

    @classmethod
    def from_cell_averages(cls, *, solute, time_s, liquid_kg_m3, fine_kg_m3,
                           coarse_kg_m3, edges_m, grind=1.7):
        return cls(solute, grind, time_s, edges_m, liquid_kg_m3, fine_kg_m3, coarse_kg_m3)

    @classmethod
    def source_equilibrium(cls, temperature_history, *, time_s, solute, cells=400, grind=1.7):
        if not isinstance(temperature_history, TemperatureHistory):
            raise ValueError("TEMPERATURE_HISTORY_REQUIRED")
        fv.fixed._integer(cells, "cells", 1, 2000)
        if solute not in fv.th.SPECIES:
            raise ValueError("UNKNOWN_SOURCE_SPECIES")
        T = temperature_history.value_K(_real(time_s, "model time"))
        p = fv.ps._solute_params()[solute]
        K = float(fv.pc.vant_hoff_K(T, p["K_ref"], p["gamma"]))
        return cls(solute, grind, time_s, np.linspace(0, fv.ps.L, cells+1),
                   np.full(cells, K*p["c_s0"]), np.full(cells, p["c_s0"]),
                   np.full(cells, p["c_s0"]), "SOURCE_EQUILIBRIUM", T)

    @property
    def inventory_kg(self):
        return _inventory(self.liquid_cell_average_kg_m3, self.fine_cell_average_kg_m3,
                          self.coarse_cell_average_kg_m3, self.grind)

    @property
    def concentration_scale_kg_m3(self):
        return float(max(np.max(self.liquid_cell_average_kg_m3), np.max(self.fine_cell_average_kg_m3),
                         np.max(self.coarse_cell_average_kg_m3)))

    @property
    def model_identity(self):
        return _hash((self.solute, self.grind, self.edges_m, self.geometry, self.units_and_bases,
                      self.schema_version, self.source_identities, self.source_configuration, ALGORITHM))

    def validate(self):
        if (self.identity_sha256 != _hash(self) or self.source_identities != _sources()
                or self.geometry != _geometry() or self.source_configuration != _configuration(self.solute, self.grind)):
            raise ValueError("STATE_IDENTITY_OR_SOURCE_MISMATCH")


@dataclass(frozen=True, eq=False)
class FVPlan:
    """Full planned horizon. Observation requests and a stop do not alter this plan."""
    temperature_history: TemperatureHistory
    flow_history: FlowHistory
    t_span_s: tuple[float, float]
    settings: FVSettings = FVSettings()
    schema_version: int = SCHEMA_VERSION
    primary_steps: np.ndarray = field(init=False)
    primary_times_s: np.ndarray = field(init=False)
    diagnostic_times_s: np.ndarray = field(init=False)
    identity_sha256: str = field(init=False)

    def __post_init__(self):
        if not isinstance(self.temperature_history, TemperatureHistory) or not isinstance(self.flow_history, FlowHistory) or not isinstance(self.settings, FVSettings):
            raise ValueError("IMMUTABLE_HISTORY_AND_SETTINGS_REQUIRED")
        if type(self.schema_version) is not int or self.schema_version != SCHEMA_VERSION:
            raise ValueError("INCOMPATIBLE_PLAN_SCHEMA")
        span = _reals(self.t_span_s, "planned span", 2)
        if len(span) != 2 or span[1] <= span[0] or not math.isfinite(span[1]-span[0]):
            raise ValueError("INVALID_PLANNED_SPAN")
        a, b = span
        if min(self.settings.h_max_s, self.settings.diagnostic_step_s) <= 10*max(abs(np.spacing(a)), abs(np.spacing(b))):
            raise ValueError("UNRESOLVABLE_PLAN_CLOCK")
        segments = fv._segments(self.temperature_history, self.flow_history, a, b)
        steps = sum(math.ceil((s.end_s-s.start_s)/self.settings.h_max_s) for s in segments)
        grid = math.ceil((b-a)/self.settings.diagnostic_step_s)
        if steps > 200000 or grid > self.settings.max_diagnostic_samples:
            raise ValueError("PLAN_ALLOCATION_LIMIT")
        schedule = np.asarray(tuple(fv._primary_steps(segments, self.settings.h_max_s)))
        if not np.isfinite(schedule).all() or np.any(schedule[:, 1] <= schedule[:, 0]):
            raise ValueError("NONFINITE_OR_UNRESOLVABLE_SCHEDULE")
        object.__setattr__(self, "t_span_s", span)
        object.__setattr__(self, "primary_steps", schedule)
        object.__setattr__(self, "primary_times_s", np.r_[a, schedule[:, 1]])
        object.__setattr__(self, "diagnostic_times_s", np.linspace(a, b, grid+1))
        _freeze(self)

    def validate(self):
        if self.identity_sha256 != _hash(self):
            raise ValueError("PLAN_IDENTITY_MISMATCH")


@dataclass(frozen=True, eq=False, init=False)
class FVCheckpoint:
    """Created only by a checked result. Raw masses and delivery terms are retained."""
    root_state: FVChemicalState
    plan: FVPlan
    primary_index: int
    time_s: float
    raw_masses_kg: np.ndarray
    liquid_cell_average_kg_m3: np.ndarray
    fine_cell_average_kg_m3: np.ndarray
    coarse_cell_average_kg_m3: np.ndarray
    outlet_terms_kg: tuple[float, ...]
    volume_terms_m3: tuple[float, ...]
    remaining_inventory_kg: float
    local_concentration_scale_kg_m3: float
    parent_identity: str | None
    schema_version: int
    identity_sha256: str

    def __init__(self):
        raise TypeError("Use StatefulFVResult.checkpoint or FVCheckpoint.from_json")

    @property
    def root_time_s(self):
        return self.root_state.time_s

    @property
    def origin_outlet_solute_kg(self):
        return math.fsum(self.outlet_terms_kg)

    @property
    def origin_volume_m3(self):
        return math.fsum(self.volume_terms_m3)

    def validate(self):
        self.root_state.validate()
        self.plan.validate()
        if type(self.schema_version) is not int or self.schema_version != SCHEMA_VERSION or self.identity_sha256 != _hash(self):
            raise ValueError("CHECKPOINT_IDENTITY_OR_SCHEMA_MISMATCH")
        if (type(self.primary_index) is not int or not 0 < self.primary_index < len(self.plan.primary_times_s)
                or not self.root_time_s <= self.plan.t_span_s[0] <= self.time_s):
            raise ValueError("CHECKPOINT_CLOCK_OR_INDEX_MISMATCH")
        if self.plan.primary_times_s[self.primary_index] != self.time_s:
            raise ValueError("CHECKPOINT_CLOCK_SCHEDULE_MISMATCH")
        if len(self.outlet_terms_kg) > 200000 or len(self.volume_terms_m3) != len(self.outlet_terms_kg):
            raise ValueError("CHECKPOINT_ACCOUNTING_LIMIT_OR_MISMATCH")
        if len(self.root_state.edges_m)-1 != self.plan.settings.cells:
            raise ValueError("CHECKPOINT_MESH_MISMATCH")
        s = fv._System(self.root_state.solute, self.root_state.grind, self.plan.settings.cells)
        if self.raw_masses_kg.shape != (3*s.n+1,) or not np.isfinite(self.raw_masses_kg).all():
            raise ValueError("CHECKPOINT_RAW_STATE_SHAPE_OR_NONFINITE")
        if (len(self.outlet_terms_kg) < self.primary_index
                or not all(math.isfinite(v) and v > 0 for v in self.volume_terms_m3)
                or not all(math.isfinite(v) and _within(min(0., v), self.root_state.inventory_kg, 1e-10) for v in self.outlet_terms_kg)
                or self.raw_masses_kg[-1] != self.outlet_terms_kg[-1]):
            raise ValueError("CHECKPOINT_ACCUMULATOR_MISMATCH")
        tail = self.volume_terms_m3[-self.primary_index:]
        expected = tuple(self.plan.flow_history.integral(a, b) for a, b in
                         zip(self.plan.primary_times_s[:self.primary_index], self.plan.primary_times_s[1:self.primary_index+1]))
        if tail != expected:
            raise ValueError("CHECKPOINT_VOLUME_SCHEDULE_MISMATCH")
        c = self.raw_masses_kg[:-1].reshape(3, s.n)/s.capacities.reshape(3, s.n)
        if not np.array_equal(c, np.array([self.liquid_cell_average_kg_m3,
                                          self.fine_cell_average_kg_m3, self.coarse_cell_average_kg_m3])):
            raise ValueError("CHECKPOINT_RAW_PHYSICAL_VIEW_MISMATCH")
        if (self.local_concentration_scale_kg_m3 != float(np.max(np.abs(c)))
                or not _within(min(0., float(np.min(c))), self.root_state.concentration_scale_kg_m3, 1e-10)):
            raise ValueError("CHECKPOINT_LOCAL_SCALE_OR_ADMISSIBILITY_MISMATCH")
        m = _inventory(*c, self.root_state.grind)
        if m != self.remaining_inventory_kg or not _within(math.fsum((m, *self.outlet_terms_kg, -self.root_state.inventory_kg)), self.root_state.inventory_kg, 1e-8):
            raise ValueError("CHECKPOINT_INVENTORY_MISMATCH")

    def to_json(self):
        """Bounded versioned data only. Hashes detect corruption, not authenticity."""
        return json.dumps(dict(format="pannusch2024.FVCheckpoint.v1", checkpoint=_json(self),
                               identity_sha256=self.identity_sha256), sort_keys=True, allow_nan=False)

    @classmethod
    def from_json(cls, payload):
        if not isinstance(payload, str) or len(payload) > 32000000:
            raise ValueError("CHECKPOINT_FORMAT_OR_SIZE_LIMIT")
        try:
            def invalid(value):
                raise ValueError("NONFINITE_JSON")
            def unique(pairs):
                out = {}
                for k, v in pairs:
                    if k in out:
                        raise ValueError("DUPLICATE_JSON_KEY")
                    out[k] = v
                return out
            doc = json.loads(payload, parse_constant=invalid, object_pairs_hook=unique)
            if set(doc) != {'format', 'checkpoint', 'identity_sha256'} or doc['format'] != 'pannusch2024.FVCheckpoint.v1':
                raise ValueError("CHECKPOINT_FORMAT")
            r = doc['checkpoint']
            if set(r) != {f.name for f in fields(cls) if f.name != 'identity_sha256'}:
                raise ValueError("CHECKPOINT_FIELDS")
            root_record = dict(r['root_state'])
            config = root_record.pop('source_configuration')
            for key in ('source_identities', 'geometry', 'units_and_bases'):
                root_record[key] = tuple(tuple(x) for x in root_record[key])
            root = FVChemicalState(**root_record)
            if _json(root.source_configuration) != config:
                raise ValueError("CHECKPOINT_SOURCE_CONFIGURATION")
            p = r['plan']
            expected_plan_keys = {f.name for f in fields(FVPlan) if f.name != 'identity_sha256'}
            if set(p) != expected_plan_keys:
                raise ValueError("CHECKPOINT_PLAN_FIELDS")
            plan = FVPlan(TemperatureHistory(**p['temperature_history']), FlowHistory(**p['flow_history']),
                          tuple(p['t_span_s']), FVSettings(**p['settings']), p['schema_version'])
            for key in ('primary_steps', 'primary_times_s', 'diagnostic_times_s'):
                if not np.array_equal(np.asarray(p[key]), getattr(plan, key)):
                    raise ValueError("CHECKPOINT_SCHEDULE_MISMATCH")
            cp = object.__new__(cls)
            for f in fields(cls):
                key = f.name
                if key == 'identity_sha256':
                    continue
                v = root if key == 'root_state' else plan if key == 'plan' else r[key]
                if key in ('raw_masses_kg', 'liquid_cell_average_kg_m3', 'fine_cell_average_kg_m3', 'coarse_cell_average_kg_m3'):
                    v = np.asarray(_reals(v, key, 1))
                elif key in ('outlet_terms_kg', 'volume_terms_m3'):
                    v = _reals(v, key, 1)
                object.__setattr__(cp, key, v)
            _freeze(cp)
            if cp.identity_sha256 != doc['identity_sha256']:
                raise ValueError("CHECKPOINT_HASH_MISMATCH")
            cp.validate()
            return cp
        except (KeyError, TypeError, IndexError, AttributeError, OverflowError) as exc:
            raise ValueError("MALFORMED_CHECKPOINT") from exc


@dataclass(frozen=True, eq=False)
class StatefulTrajectory:
    times_s: np.ndarray
    liquid_cell_average_kg_m3: np.ndarray
    fine_cell_average_kg_m3: np.ndarray
    coarse_cell_average_kg_m3: np.ndarray
    outlet_face_kg_m3: np.ndarray
    remaining_inventory_kg: np.ndarray
    segment_outlet_solute_kg: np.ndarray
    origin_outlet_solute_kg: np.ndarray
    segment_volume_m3: np.ndarray
    origin_volume_m3: np.ndarray

    def __post_init__(self):
        fv._freeze_arrays(self)


@dataclass(frozen=True, eq=False)
class StatefulFVResult:
    root_state: FVChemicalState
    plan: FVPlan
    mode: str
    parent_identity: str | None
    start_index: int
    requested_stop_s: float
    actual_end_s: float
    observation_times_s: tuple
    observation_status: tuple
    observations: StatefulTrajectory
    primary: StatefulTrajectory
    raw_primary_masses_kg: np.ndarray
    raw_quadrature: np.ndarray
    raw_diagnostic_times_s: np.ndarray
    raw_diagnostic_masses_kg: np.ndarray
    prior_outlet_terms_kg: tuple
    prior_volume_terms_m3: tuple
    step_outlet_solute_kg: np.ndarray
    step_volume_m3: np.ndarray
    exportable_primary: np.ndarray
    fractions: tuple
    diagnostics: tuple
    integration_complete: bool
    planned_horizon_complete: bool
    status: str
    reason: str | None
    propagations: int
    exponential_applications: int
    diagnostic_evaluations: int
    elapsed_wall_s: float
    identity_sha256: str = field(init=False)
    accuracy_status: str = "NOT_ASSESSED"
    PHYSICAL_VALIDATION: str = "NOT_ESTABLISHED"
    scope: str = "RESEARCH_ONLY"

    def __post_init__(self):
        _freeze(self)

    @property
    def root_time_s(self):
        return self.root_state.time_s

    @property
    def continuation_start_s(self):
        return float(self.plan.primary_times_s[self.start_index])

    def checkpoint(self, time_s):
        t = _real(time_s, "checkpoint time")
        hits = np.flatnonzero(self.primary.times_s == t)
        if not len(hits):
            if t in self.plan.primary_times_s:
                raise ValueError("CHECKPOINT_BEYOND_CHECKED_PREFIX")
            raise ValueError("CHECKPOINT_REQUIRES_PRIMARY_ENDPOINT")
        i = int(hits[0])
        if i == 0:
            raise ValueError("CHECKPOINT_REQUIRES_COMPLETED_PRIMARY_STEP")
        if not self.exportable_primary[i]:
            raise ValueError("CHECKPOINT_INADMISSIBLE_PREFIX")
        n = self.plan.settings.cells
        c = np.array([self.primary.liquid_cell_average_kg_m3[i], self.primary.fine_cell_average_kg_m3[i],
                      self.primary.coarse_cell_average_kg_m3[i]])
        cp = object.__new__(FVCheckpoint)
        values = dict(root_state=self.root_state, plan=self.plan, primary_index=self.start_index+i,
                      time_s=t, raw_masses_kg=self.raw_primary_masses_kg[i].copy(),
                      liquid_cell_average_kg_m3=c[0], fine_cell_average_kg_m3=c[1], coarse_cell_average_kg_m3=c[2],
                      outlet_terms_kg=(*self.prior_outlet_terms_kg, *map(float, self.step_outlet_solute_kg[:i])),
                      volume_terms_m3=(*self.prior_volume_terms_m3, *map(float, self.step_volume_m3[:i])),
                      remaining_inventory_kg=_inventory(*c, self.root_state.grind),
                      local_concentration_scale_kg_m3=float(np.max(np.abs(c))),
                      parent_identity=self.parent_identity, schema_version=SCHEMA_VERSION)
        for k, v in values.items():
            object.__setattr__(cp, k, v)
        _freeze(cp)
        cp.validate()
        return cp

    def to_json(self, *, include_trajectories=True):
        value = _json(self)
        if not include_trajectories:
            for k in ("observations", "primary", "raw_primary_masses_kg", "raw_quadrature",
                      "raw_diagnostic_times_s", "raw_diagnostic_masses_kg"):
                value[k] = {"arrays": "OMITTED_BY_REQUEST"}
        value["request_report_identity"] = self.identity_sha256
        return json.dumps(value, sort_keys=True, allow_nan=False)


def simulate_stateful_fv(*, plan=None, initial_state=None, checkpoint=None,
                         observation_times_s, fraction_windows_s=(), stop_time_s=None,
                         resource_settings=None, _branch=False):
    """Fresh supplied-state run or same-schedule resume; no arbitrary offsets.

    Use branch_stateful_fv for a changed future plan. Stops must be existing
    primary endpoints of the full plan. Fractions are explicit (start, end) pairs.
    """
    if (initial_state is None) == (checkpoint is None):
        raise ValueError("EXACTLY_ONE_INITIAL_STATE_OR_CHECKPOINT_REQUIRED")
    if checkpoint is not None:
        if not isinstance(checkpoint, FVCheckpoint):
            raise ValueError("CHECKED_CHECKPOINT_REQUIRED")
        checkpoint.validate()
        root = checkpoint.root_state
        plan = checkpoint.plan if plan is None else plan
        if not isinstance(plan, FVPlan):
            raise ValueError("FV_PLAN_REQUIRED")
        if not _branch and plan.identity_sha256 != checkpoint.plan.identity_sha256:
            raise ValueError("CHANGED_FORCING_OR_SCHEDULE_REQUIRES_EXPLICIT_BRANCH")
        if _branch and (plan.t_span_s[0] != checkpoint.time_s or plan.settings != checkpoint.plan.settings):
            raise ValueError("BRANCH_CLOCK_OR_NUMERICAL_SETTINGS_MISMATCH")
        index = 0 if _branch else checkpoint.primary_index
        raw = checkpoint.raw_masses_kg.copy()
        prior_m, prior_v = checkpoint.outlet_terms_kg, checkpoint.volume_terms_m3
        parent = checkpoint.identity_sha256
        mode = "BRANCH" if _branch else "SAME_SCHEDULE_CONTINUATION"
    else:
        if not isinstance(initial_state, FVChemicalState) or not isinstance(plan, FVPlan):
            raise ValueError("CHEMICAL_STATE_AND_PLAN_REQUIRED")
        initial_state.validate()
        root = initial_state
        if root.time_s != plan.t_span_s[0] or len(root.edges_m)-1 != plan.settings.cells:
            raise ValueError("INITIAL_STATE_CLOCK_OR_MESH_MISMATCH")
        index, prior_m, prior_v, parent, mode = 0, (), (), None, "FRESH_STATE"
        s = fv._System(root.solute, root.grind, plan.settings.cells)
        raw = np.r_[np.concatenate([root.liquid_cell_average_kg_m3, root.fine_cell_average_kg_m3,
                                    root.coarse_cell_average_kg_m3])*s.capacities, 0.]
    plan.validate()
    start = float(plan.primary_times_s[index])
    stop = plan.t_span_s[1] if stop_time_s is None else _real(stop_time_s, "stop time")
    hits = np.flatnonzero(plan.primary_times_s == stop)
    if not len(hits) or stop < start:
        raise ValueError("STOP_REQUIRES_EXISTING_FUTURE_PRIMARY_ENDPOINT")
    end_index = int(hits[0])
    obs = _reals(observation_times_s, "observations", 0)
    if any(b <= a for a, b in zip(obs, obs[1:])) or any(t < start or t > plan.t_span_s[1] for t in obs):
        raise ValueError("OBSERVATION_CLOCK_OR_CONTINUATION_SUPPORT")
    windows = tuple(_reals(w, "fraction window", 2) for w in fraction_windows_s)
    if any(len(w) != 2 or not start <= w[0] <= w[1] <= plan.t_span_s[1] for w in windows):
        raise ValueError("FRACTION_CLOCK_OR_CONTINUATION_SUPPORT")
    settings = plan.settings if resource_settings is None else resource_settings
    if not isinstance(settings, FVSettings) or any(getattr(settings, k) != getattr(plan.settings, k)
            for k in ("cells", "h_max_s", "diagnostic_step_s")):
        raise ValueError("RESOURCE_SETTINGS_CANNOT_CHANGE_NUMERICAL_PLAN")
    if (3*(end_index-index)+len(obs)+2*len(windows)+len(plan.diagnostic_times_s)+2)*(3*settings.cells+1) > settings.max_state_values:
        raise ValueError("STATE_ALLOCATION_LIMIT")
    system = fv._System(root.solute, root.grind, settings.cells)
    c = (raw[:-1]/system.capacities).reshape(3, settings.cells)
    local_inventory = _inventory(*c, root.grind)
    local_C = float(np.max(np.abs(c)))
    context = dict(inventory=local_inventory, state=raw,
                   steps=plan.primary_steps[index:end_index], diagnostic_times=plan.diagnostic_times_s,
                   windows=windows)
    bounds = tuple(sorted({t for w in windows for t in w}))
    if stop == start:
        data = dict(actual=start, samples={start: raw}, quadrature=np.empty((0, 13)), window_parts=[],
                    times=np.array([start]), states=raw[None, :], frozen_T=np.array([]), frozen_Q=np.array([]),
                    reason=None, propagations=0, exponential_applications=0, diagnostic_evaluations=0, elapsed_wall_s=0.)
    else:
        data = fv._evolve(system, plan.temperature_history, plan.flow_history, (start, stop),
                          obs, bounds, settings, _stateful=context)
    return _report(data, root, plan, index, stop, obs, windows, mode, parent,
                   prior_m, prior_v, local_inventory, local_C, system)


def branch_stateful_fv(checkpoint, *, plan, observation_times_s, fraction_windows_s=(),
                       stop_time_s=None, resource_settings=None):
    """Explicit new future forcing, preserving raw chemistry and root accounting."""
    return simulate_stateful_fv(plan=plan, checkpoint=checkpoint,
                               observation_times_s=observation_times_s, fraction_windows_s=fraction_windows_s,
                               stop_time_s=stop_time_s, resource_settings=resource_settings, _branch=True)


def _report(d, root, plan, index, stop, obs, windows, mode, parent, prior_m, prior_v, Mlocal, Clocal, system):
    times, masses = d['times'], d['states']
    start, actual = float(times[0]), float(d['actual'])
    increments = masses[1:, -1].copy()
    volumes = np.array([plan.flow_history.integral(a, b) for a, b in zip(times, times[1:])])
    Mroot, Croot = root.inventory_kg, root.concentration_scale_kg_m3
    exact_zero = Croot == 0.
    local_residuals, root_residuals, step_residuals = [], [], []
    good = np.ones(len(times), dtype=bool)
    minimum_phase = np.full(3, np.inf)
    minimum_increment = 0.

    def inventory(y):
        return _inventory(*(y[:-1]/system.capacities).reshape(3, system.n), root.grind)

    def totals(t, y):
        # A primary endpoint's raw accumulator is its preceding step's delivery.
        j = int(np.searchsorted(times, t, side='left'))
        if j < len(times) and times[j] == t:
            terms = increments[:j]
        else:
            terms = (*increments[:j-1], float(y[-1]))
        return math.fsum(terms), math.fsum((*prior_m, *terms))

    def check(t, cmin, bed, dm, owner, step_dm):
        nonlocal minimum_phase, minimum_increment
        local_res = math.fsum((bed, dm, -Mlocal))
        root_res = math.fsum((bed, *prior_m, dm, -Mroot))
        step_res = math.fsum((bed, step_dm, -inventory(masses[owner])))
        local_residuals.append(local_res); root_residuals.append(root_res); step_residuals.append(step_res)
        minimum_phase = np.minimum(minimum_phase, cmin)
        minimum_increment = min(minimum_increment, step_dm)
        valid = all(_within(min(0., x), Clocal, 1e-10) for x in cmin)
        valid &= _within(min(0., step_dm), Mlocal, 1e-10)
        valid &= _within(local_res, Mlocal, 1e-8) and _within(root_res, Mroot, 1e-8)
        valid &= _within(step_res, inventory(masses[owner]), 1e-8)
        if not valid:
            # Interior points and the right endpoint belong to the same interval.
            first = max(0, int(np.searchsorted(times, t, side='left')))
            good[first:] = False

    sample_times = np.array(sorted(d['samples']))
    sample_states = np.array([d['samples'][t] for t in sample_times])
    for t, y in zip(sample_times, sample_states):
        j = max(0, int(np.searchsorted(times, t, side='left'))-1)
        dm, _ = totals(t, y)
        c = (y[:-1]/system.capacities).reshape(3, system.n)
        step_dm = 0. if t == start else float(y[-1])
        check(t, np.min(c, axis=1), inventory(y), dm, j, step_dm)
    q = d['quadrature']
    for row in q:
        t, _, _, owner = row[:4]
        owner = int(owner)
        dm = math.fsum((*increments[:owner], float(row[8])))
        check(t, row[10:13], float(row[9]), dm, owner, float(row[8]))
    # All chronological sampled deliveries, including quadrature nodes, must be monotone.
    chronological = [(float(t), totals(t, y)[0]) for t, y in zip(sample_times, sample_states)]
    chronological += [(float(row[0]), math.fsum((*increments[:int(row[3])], float(row[8])))) for row in q]
    chronological.sort(key=lambda x: x[0])
    for (a, ma), (b, mb) in zip(chronological, chronological[1:]):
        if not _within(min(0., mb-ma), Mlocal, 1e-10):
            good[max(0, int(np.searchsorted(times, b, side='left'))):] = False
    admissible = bool(np.all(good))
    reason = d['reason']
    if not admissible:
        reason = 'SAMPLED_ADMISSIBILITY_FAILED' if reason is None else reason+';SAMPLED_ADMISSIBILITY_FAILED'

    def trajectory(tvalues, yvalues):
        t = np.asarray(tvalues)
        y = np.asarray(yvalues).reshape(len(t), 3*system.n+1)
        c = (y[:, :-1]/system.capacities).reshape(len(t), 3, system.n)
        local, origin = zip(*(totals(at, val) for at, val in zip(t, y))) if len(t) else ((), ())
        v = np.array([plan.flow_history.integral(start, at) for at in t])
        return StatefulTrajectory(t, c[:, 0], c[:, 1], c[:, 2], c[:, 0, -1],
            np.array([inventory(row) for row in y]), np.asarray(local), np.asarray(origin), v,
            np.array([math.fsum((*prior_v, float(value))) for value in v]))

    statuses = []
    supported = []
    for t in obs:
        if t not in d['samples']:
            status = 'PLANNED_STOP_NOT_EVALUATED' if stop < plan.t_span_s[1] and t > stop else 'NOT_EVALUATED_IN_CHECKED_PREFIX'
        elif not good[int(np.searchsorted(times, t, side='left'))]:
            status = 'SAMPLED_ADMISSIBILITY_FAILED'
        else:
            status = 'SUPPORTED'
            supported.append(t)
        statuses.append(status)
    fractions = []
    for wi, (a, b) in enumerate(windows):
        if a < start or b > actual or a not in d['samples'] or b not in d['samples']:
            fractions.append(fv.FVFraction(a, b, None, None, None, None, 'UNSUPPORTED', 'NOT_EVALUATED_IN_CHECKED_PREFIX'))
            continue
        dv = plan.flow_history.integral(a, b)
        if a == b or dv == 0:
            fractions.append(fv.FVFraction(a, b, 0., dv, None, None, 'UNDEFINED', 'ZERO_DURATION_OR_UNREPRESENTABLE_VOLUME'))
            continue
        parts = [p for p in d['window_parts'] if p[0] == wi]
        dm = math.fsum(p[4] for p in parts)
        raw_c = dm/dv
        finite = math.isfinite(raw_c)
        valid = bool(np.all(good[:int(np.searchsorted(times, b, side='left'))+1])) and finite
        # Never promote an underflowed delivery of a positive root state to exact zero.
        resolved = exact_zero or dm > 0.
        status = 'VALID_NUMERICAL_ZERO' if exact_zero else 'NUMERICAL_ONLY_ACCURACY_NOT_ASSESSED'
        why = None
        if not valid or not resolved:
            status = 'UNQUALIFIED'
            why = 'SAMPLED_ADMISSIBILITY_FAILED' if not valid else 'OUTLET_INCREMENT_UNRESOLVED'
        fractions.append(fv.FVFraction(a, b, dm, dv, raw_c if valid and resolved else None,
                         raw_c if finite else None, status, why))
    def residual_record(label, values, scale):
        worst = _scaled(max(map(abs, values)), scale)
        return (label, dict(initial_kg=float(values[0]), final_kg=float(values[len(sample_times)-1]),
                            signed_min_kg=float(min(values)), signed_max_kg=float(max(values)),
                            worst_absolute_kg=float(max(map(abs, values))),
                            worst_scaled=worst, scale_kg=scale,
                            normalization_reason=None if worst is not None else 'NONZERO_ERROR_WITH_ZERO_OR_UNREPRESENTABLE_SCALE'))
    diagnostics = (
        residual_record('local_inventory', local_residuals, Mlocal),
        residual_record('origin_inventory', root_residuals, Mroot),
        residual_record('interval_inventory', step_residuals, Mlocal),
        ('minimum_phase_kg_m3', tuple(map(float, minimum_phase))),
        ('minimum_interval_outlet_solute_kg', minimum_increment),
        ('root_concentration_scale_kg_m3', Croot), ('local_concentration_scale_kg_m3', Clocal),
        ('exact_zero_root', exact_zero), ('sampled_admissibility', 'PASS' if admissible else 'FAIL'))
    complete = d['reason'] is None and actual == stop
    status = ('PLANNED_STOP' if stop < plan.t_span_s[1] else 'COMPLETE') if complete else 'INTEGRATION_FAILED'
    if not admissible:
        status = 'SAMPLED_ADMISSIBILITY_FAILED'
    return StatefulFVResult(root, plan, mode, parent, index, stop, actual, obs, tuple(statuses),
        trajectory(supported, [d['samples'][t] for t in supported]), trajectory(times, masses),
        masses, q, sample_times, sample_states, prior_m, prior_v, increments, volumes, good,
        tuple(fractions), diagnostics, complete, complete and actual == plan.t_span_s[1], status, reason,
        d['propagations'], d['exponential_applications'], d['diagnostic_evaluations'], d['elapsed_wall_s'])
