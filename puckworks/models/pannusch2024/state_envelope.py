"""Conditional delivery envelopes of the unchanged discrete Pannusch FV model.

G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Engineering enclosures, not rigorous
interval arithmetic, statistical intervals, or continuum accuracy certificates.
Pannusch et al., DOI 10.1016/j.jfoodeng.2023.111887; source-derived output:
Mendeley 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0, separate from first-party code.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass, replace
from fractions import Fraction
import hashlib
import json
import math
import numbers
from pathlib import Path
import time
import warnings

import numpy as np
from scipy.optimize import linprog, OptimizeWarning
from scipy.sparse.linalg import expm_multiply

from . import stateful_fv as sf

ALGORITHM = 'pannusch2024.state_envelope.transpose_local_reward.highs.v1'
EPS = np.finfo(float).eps
PHASES = ('liquid', 'fine', 'coarse')


def _real(value, name, *, nonnegative=False):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, numbers.Real):
        raise ValueError(name+': FINITE_REAL_REQUIRED')
    try:
        x = float(value)
    except (ValueError, OverflowError) as exc:
        raise ValueError(name+': UNREPRESENTABLE_REAL') from exc
    if not math.isfinite(x) or (value != 0 and x == 0):
        raise ValueError(name+': UNREPRESENTABLE_REAL')
    if nonnegative and value < 0:
        raise ValueError(name+': NONNEGATIVE_REQUIRED')
    return x


def _interval(value, name, *, nonnegative=True):
    a = np.asarray(value, dtype=object)
    if a.shape != (2,):
        raise ValueError(name+': INTERVAL_SHAPE')
    lo, hi = (_real(v, name, nonnegative=nonnegative) for v in a)
    if lo > hi:
        raise ValueError(name+': REVERSED_INTERVAL')
    return lo, hi


def _integer(value, name, upper):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(name+': INTEGER_REQUIRED')
    if not 1 <= value <= upper:
        raise ValueError(name+': RESOURCE_DOMAIN')
    return int(value)


def _readonly(a):
    a = np.asarray(a, dtype=float)
    return np.frombuffer(a.tobytes(), dtype=float).reshape(a.shape)


def _concentrations(state):
    return np.concatenate([getattr(state, p+'_cell_average_kg_m3') for p in PHASES])


def _seal(obj):
    for f in fields(obj):
        a = getattr(obj, f.name, None)
        if isinstance(a, np.ndarray):
            object.__setattr__(obj, f.name, _readonly(a))


def _source_code():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


@dataclass(frozen=True, eq=False)
class FVChemicalStateSet:
    """Explicit concentration box intersected with kg inventory intervals.

    ``lower`` and ``upper`` are existing immutable FVChemicalState objects,
    interpreted as bounds, not as a default initial state. All their model,
    phase-basis, mesh, source and absolute-clock identities must agree.
    Optional phase intervals are in liquid/fine/coarse order. No distribution
    or measured-state interpretation is supplied. Empty sets remain objects
    with an explicit feasibility disposition, never nominal replacements.
    """
    lower: sf.FVChemicalState
    upper: sf.FVChemicalState
    total_inventory_kg: tuple[float, float]
    assumption_label: str
    phase_inventory_kg: tuple | None = None
    inventory_units: str = 'kg'
    capacities_m3: np.ndarray = field(init=False)
    lower_masses_kg: np.ndarray = field(init=False)
    upper_masses_kg: np.ndarray = field(init=False)
    feasibility: str = field(init=False)
    inventory_scale_kg: float = field(init=False)
    identity_sha256: str = field(init=False)

    def __post_init__(self):
        if not isinstance(self.lower, sf.FVChemicalState) or not isinstance(self.upper, sf.FVChemicalState):
            raise ValueError('EXPLICIT_CHEMICAL_STATE_BOUNDS_REQUIRED')
        self.lower.validate(); self.upper.validate()
        if (self.lower.model_identity != self.upper.model_identity
                or self.lower.time_s != self.upper.time_s):
            raise ValueError('BOUND_MODEL_OR_CLOCK_MISMATCH')
        if not isinstance(self.assumption_label, str) or not self.assumption_label.strip() or len(self.assumption_label) > 512:
            raise ValueError('INPUT_ASSUMPTION_LABEL_REQUIRED')
        if self.inventory_units != 'kg':
            raise ValueError('INVENTORY_REQUIRES_KG')
        total = _interval(self.total_inventory_kg, 'total inventory kg')
        phases = self.phase_inventory_kg
        if phases is not None:
            if np.asarray(phases, dtype=object).shape != (3, 2):
                raise ValueError('PHASE_INTERVAL_SHAPE')
            phases = tuple(_interval(v, 'phase inventory kg') for v in phases)
        n = len(self.lower.edges_m)-1
        cap = sf.fv._System(self.lower.solute, self.lower.grind, n).capacities
        lo, hi = (_concentrations(s)*cap for s in (self.lower, self.upper))
        if np.any(_concentrations(self.lower) > _concentrations(self.upper)):
            raise ValueError('REVERSED_CELL_BOUNDS')
        # Constructors already reject overflow/underflow; check again at this boundary.
        if not np.isfinite(np.r_[cap, lo, hi]).all() or np.any(cap <= 0):
            raise ValueError('UNREPRESENTABLE_MASS_BOUNDS')
        if np.any((_concentrations(self.upper) > 0) & (hi == 0)):
            raise ValueError('UNREPRESENTABLE_POSITIVE_MASS')
        F = Fraction.from_float
        low, high = [], []
        for j in range(3):
            l = sum(map(F, map(float, lo[j*n:(j+1)*n])), Fraction())
            u = sum(map(F, map(float, hi[j*n:(j+1)*n])), Fraction())
            if phases is not None:
                l, u = max(l, F(phases[j][0])), min(u, F(phases[j][1]))
            low.append(l); high.append(u)
        empty = any(l > u for l, u in zip(low, high))
        lower_total, upper_total = max(sum(low), F(total[0])), min(sum(high), F(total[1]))
        empty |= lower_total > upper_total
        # These laminar constraints have an exact interval feasibility criterion.
        object.__setattr__(self, 'feasibility', 'EMPTY_FEASIBLE_SET' if empty else 'ESTABLISHED_NONEMPTY')
        scale = max(0., float(upper_total))
        if F(scale) < upper_total:
            scale = float(np.nextafter(scale, np.inf))
        object.__setattr__(self, 'inventory_scale_kg', scale)
        object.__setattr__(self, 'total_inventory_kg', total)
        object.__setattr__(self, 'phase_inventory_kg', phases)
        object.__setattr__(self, 'capacities_m3', cap)
        object.__setattr__(self, 'lower_masses_kg', lo)
        object.__setattr__(self, 'upper_masses_kg', hi)
        _seal(self)
        object.__setattr__(self, 'identity_sha256', sf._hash(self))

    def validate(self):
        self.lower.validate(); self.upper.validate()
        if self.identity_sha256 != sf._hash(self):
            raise ValueError('STATE_SET_IDENTITY_MISMATCH')


@dataclass(frozen=True)
class FVEnvelopeSettings:
    """Finite per-query work limits; no tolerance is inferred from measurement."""
    max_exponential_actions: int = 100000
    max_steps: int = 10000
    response_wall_s: float = 120.
    max_lp_iterations: int = 10000
    lp_wall_s: float = 30.
    primal_tolerance: float = 1e-9
    dual_tolerance: float = 1e-9

    def __post_init__(self):
        for k, top in (('max_exponential_actions', 200000), ('max_steps', 20000),
                       ('max_lp_iterations', 100000)):
            object.__setattr__(self, k, _integer(getattr(self, k), k, top))
        for k, lo, hi in (('response_wall_s', 0., 120.), ('lp_wall_s', 0., 120.),
                         ('primal_tolerance', 1e-10, 1e-7), ('dual_tolerance', 1e-10, 1e-7)):
            v = _real(getattr(self, k), k, nonnegative=True)
            if v <= 0 or v < lo or v > hi:
                raise ValueError(k+': NUMERICAL_SETTINGS_DOMAIN')
            object.__setattr__(self, k, v)


@dataclass(frozen=True, eq=False)
class FVDeliveryResponse:
    plan: sf.FVPlan
    model: sf.FVChemicalState
    window_s: tuple[float, float]
    settings: FVEnvelopeSettings
    weights: np.ndarray | None
    coefficient_allowances: np.ndarray | None
    split_discrepancy: float | None
    arithmetic_floor: float | None
    volume_m3: float
    status: str
    termination: str
    exponential_applications: int
    response_passes: int
    conditioning_sum: float
    elapsed_wall_s: float
    algorithm: str = ALGORITHM
    algorithm_source_sha256: str = field(default_factory=_source_code)
    identity_sha256: str = field(init=False)

    def __post_init__(self):
        if not isinstance(self.plan, sf.FVPlan) or not isinstance(self.model, sf.FVChemicalState):
            raise ValueError('RESPONSE_MODEL_AND_PLAN_REQUIRED')
        if not isinstance(self.settings, FVEnvelopeSettings):
            raise ValueError('RESPONSE_NUMERICAL_SETTINGS_REQUIRED')
        window = _interval(self.window_s, 'response window', nonnegative=False)
        if not self.plan.t_span_s[0] <= window[0] <= window[1] <= self.plan.t_span_s[1]:
            raise ValueError('RESPONSE_WINDOW_OUTSIDE_PLAN')
        if self.volume_m3 != self.plan.flow_history.integral(*window):
            raise ValueError('RESPONSE_VOLUME_IDENTITY_MISMATCH')
        if self.status not in ('RESPONSE_QUALIFIED', 'NUMERICALLY_UNRESOLVED'):
            raise ValueError('RESPONSE_STATUS_REQUIRED')
        if self.status == 'RESPONSE_QUALIFIED' and (self.weights is None or self.coefficient_allowances is None):
            raise ValueError('QUALIFIED_RESPONSE_ARRAYS_REQUIRED')
        if (self.model.time_s != self.plan.t_span_s[0]
                or len(self.model.edges_m)-1 != self.plan.settings.cells):
            raise ValueError('RESPONSE_MODEL_CLOCK_OR_MESH_MISMATCH')
        for a in (self.weights, self.coefficient_allowances):
            if a is not None and (np.shape(a) != (3*self.plan.settings.cells,)
                                  or not np.isfinite(a).all()):
                raise ValueError('INVALID_RESPONSE_ARRAY')
            if a is not None and any(isinstance(v, (bool, np.bool_)) for v in np.asarray(a, dtype=object)):
                raise ValueError('BOOLEAN_RESPONSE_VALUE')
        if self.coefficient_allowances is not None and np.any(self.coefficient_allowances < 0):
            raise ValueError('NEGATIVE_RESPONSE_ALLOWANCE')
        object.__setattr__(self, 'window_s', window)
        _seal(self)
        object.__setattr__(self, 'identity_sha256', self._identity())

    def _identity(self):
        return sf._hash(tuple((f.name, getattr(self, f.name)) for f in fields(self)
                             if f.name not in ('elapsed_wall_s', 'identity_sha256')))

    def validate(self, state_set=None):
        self.plan.validate(); self.model.validate()
        if (self.identity_sha256 != self._identity() or self.algorithm != ALGORITHM
                or self.algorithm_source_sha256 != _source_code()):
            raise ValueError('RESPONSE_IDENTITY_OR_ALGORITHM_MISMATCH')
        if state_set is not None:
            state_set.validate()
            if (state_set.lower.model_identity != self.model.model_identity
                    or state_set.lower.time_s != self.plan.t_span_s[0]):
                raise ValueError('INCOMPATIBLE_RESPONSE_REUSE')


def build_delivery_response(plan, *, solute, window_s, grind=1.7,
                            settings=FVEnvelopeSettings()):
    """Two sparse backward passes (whole/split actions) on one ORIGINAL plan.

    Split actions are an arithmetic check with unchanged frozen forcing, not
    a finer time discretization. Every attempted exponential is counted.
    No state-set-dependent propagation or forward-coordinate sweep occurs.
    """
    if not isinstance(plan, sf.FVPlan) or not isinstance(settings, FVEnvelopeSettings):
        raise ValueError('IMMUTABLE_PLAN_AND_ENVELOPE_SETTINGS_REQUIRED')
    plan.validate()
    a, b = _interval(window_s, 'window seconds', nonnegative=False)
    if not plan.t_span_s[0] <= a <= b <= plan.t_span_s[1]:
        raise ValueError('WINDOW_OUTSIDE_PLAN')
    n = plan.settings.cells
    model = sf.FVChemicalState.from_cell_averages(solute=solute, grind=grind,
        time_s=plan.t_span_s[0], edges_m=np.linspace(0., sf.fv.ps.L, n+1),
        liquid_kg_m3=np.zeros(n), fine_kg_m3=np.zeros(n), coarse_kg_m3=np.zeros(n))
    system = sf.fv._System(solute, model.grind, n)
    start = time.monotonic()
    calls = passes = 0
    conditioning = 0.
    volume = plan.flow_history.integral(a, b)
    weights = errors = None
    discrepancy = floor = None
    status, reason = 'RESPONSE_QUALIFIED', 'COMPLETE'

    def action(B, vector, dt, splits):
        nonlocal calls, conditioning
        if dt == 0:
            return vector
        if dt/splits == 0:
            raise RuntimeError('UNREPRESENTABLE_ACTION_DURATION')
        for _ in range(splits):
            if calls >= settings.max_exponential_actions:
                raise RuntimeError('EXPONENTIAL_ACTION_LIMIT')
            if time.monotonic()-start >= settings.response_wall_s:
                raise RuntimeError('RESPONSE_WALL_LIMIT')
            calls += 1
            step = dt/splits
            conditioning += float(abs(B).sum(axis=0).max())*step
            vector = np.asarray(expm_multiply(B.T*step, vector,
                traceA=float(B.diagonal().sum())*step))
            if not np.isfinite(vector).all():
                raise RuntimeError('NONFINITE_TRANSPOSE_ACTION')
        return vector

    def backward(splits):
        nonlocal passes
        passes += 1
        lam = np.zeros(3*n+1)
        steps = plan.primary_steps[plan.primary_steps[:, 0] < b]
        if len(steps) > settings.max_steps:
            raise RuntimeError('RESPONSE_STEP_LIMIT')
        previous, B = None, None
        for left, right, T, Q in steps[::-1]:
            if (T, Q) != previous:
                B, previous = system.generator(T, Q), (T, Q)
            lo, hi = max(left, a), min(right, b)
            lam[-1] = 0.  # No old cumulative outlet offset is an uncertain state.
            if hi > lo:
                lam = action(B, lam, float(right-hi), splits)
                lam[-1] = 1.  # Direct interval reward; never cumulative subtraction.
                lam = action(B, lam, float(hi-lo), splits)
                lam[-1] = 0.
                lam = action(B, lam, float(lo-left), splits)
            else:
                lam = action(B, lam, float(right-left), splits)
        return lam[:-1]

    try:
        if b > a and (volume <= 0 or not math.isfinite(volume)):
            raise RuntimeError('UNREPRESENTABLE_POSITIVE_VOLUME')
        if a == b:
            weights, errors = np.zeros(3*n), np.zeros(3*n)
            discrepancy = floor = 0.
        else:
            weights, split = backward(1), backward(2)
            delta = np.abs(weights-split)
            discrepancy = float(np.max(delta))
            # Dimensionless scale 1 is the EXACT inventory/positivity response
            # bound, not an arbitrary kg floor. This is an engineering allowance.
            floor = 128*EPS*(1+calls+conditioning)
            errors = np.nextafter(delta+floor, np.inf)
            if np.any(weights < -errors) or np.any(weights > 1+errors):
                raise RuntimeError('RESPONSE_POSITIVITY_OR_INVENTORY_CHECK_FAILED')
            if not np.any(weights > 0):
                raise RuntimeError('UNRESOLVED_POSITIVE_WINDOW_RESPONSE')
        if time.monotonic()-start > settings.response_wall_s:
            raise RuntimeError('RESPONSE_WALL_LIMIT')
    except Exception as exc:
        status = 'NUMERICALLY_UNRESOLVED'
        reason = str(exc) if isinstance(exc, RuntimeError) else 'RESPONSE_EXCEPTION:'+type(exc).__name__
    return FVDeliveryResponse(plan, model, (a, b), settings, weights, errors, discrepancy,
        floor, volume, status, reason, calls, passes, conditioning, time.monotonic()-start)


@dataclass(frozen=True)
class FVConstraintResiduals:
    """Signed violations in original coordinates; positive means outside U."""
    cell_lower_kg: float
    cell_upper_kg: float
    phase_lower_kg: tuple
    phase_upper_kg: tuple
    total_lower_kg: float
    total_upper_kg: float
    phase_totals_kg: tuple
    total_kg: float
    feasible: bool

    @property
    def maximum_violation_kg(self):
        return max(0., self.cell_lower_kg, self.cell_upper_kg, self.total_lower_kg,
                   self.total_upper_kg, *self.phase_lower_kg, *self.phase_upper_kg)


def _residuals(u, m):
    n = len(m)//3
    totals = tuple(math.fsum(map(float, m[j*n:(j+1)*n])) for j in range(3))
    total = math.fsum(map(float, m))
    plo = tuple(lo-v for (lo, hi), v in zip(u.phase_inventory_kg or (), totals))
    phi = tuple(v-hi for (lo, hi), v in zip(u.phase_inventory_kg or (), totals))
    tl, th = u.total_inventory_kg
    feasible = (np.all(m >= u.lower_masses_kg) and np.all(m <= u.upper_masses_kg)
                and tl <= total <= th and all(x <= 0 for x in (*plo, *phi)))
    return FVConstraintResiduals(float(np.max(u.lower_masses_kg-m)),
        float(np.max(m-u.upper_masses_kg)), plo, phi, tl-total, total-th,
        totals, total, bool(feasible))


@dataclass(frozen=True, eq=False)
class FVWitness:
    state: sf.FVChemicalState | None
    optimizer_masses_kg: np.ndarray
    masses_kg: np.ndarray | None
    original_residuals: FVConstraintResiduals
    residuals: FVConstraintResiduals | None
    prediction_kg: float | None
    conversion_mass_change_kg: float | None
    repair: str
    repair_updates: int
    status: str
    termination: str
    replays: tuple = ()
    replay_interval_kg: tuple | None = None

    def __post_init__(self):
        _seal(self)


def _witness(u, m, g, settings):
    """Explicit bounded roundoff repair; original vector/residuals are retained.

    Clamp concentrations to the ORIGINAL box, then redistribute only enough
    mass to satisfy violated phase/total bounds. No constraint changes. Every
    reconstructed witness must pass strict original-coordinate comparisons.
    An unrepresentable intersection remains unresolved, never discarded.
    """
    raw = _residuals(u, m)
    c = m/u.capacities_m3
    updates = 0
    repair = 'NONE'
    state = mass = residual = prediction = change = None
    reason = 'COMPLETE'
    try:
        if (not np.isfinite(c).all() or np.any((m > 0) & (c == 0))
                or raw.maximum_violation_kg > 8*settings.primal_tolerance*u.inventory_scale_kg):
            raise RuntimeError('PRIMAL_OR_RECONSTRUCTION_UNRESOLVED')
        clo, chi = _concentrations(u.lower), _concentrations(u.upper)
        # Exact bound coordinates reconstruct their supplied concentration,
        # avoiding a gratuitous mass/division/product round trip at endpoints.
        c = np.where(m == u.lower_masses_kg, clo, np.where(m == u.upper_masses_kg, chi, c))
        clipped = np.minimum(np.maximum(c, clo), chi)
        updates += int(np.count_nonzero(c != clipped))
        c = clipped
        n = len(c)//3

        def move(indices, amount, direction):
            nonlocal updates
            masses = c*u.capacities_m3
            rooms = ((u.upper_masses_kg-masses) if direction > 0 else
                     (masses-u.lower_masses_kg))[indices]
            j = int(indices[int(np.argmax(rooms))])
            room = float(np.max(rooms))
            if room <= 0 or amount <= 0:
                raise RuntimeError('NO_REPRESENTABLE_FEASIBLE_REPAIR')
            value = (masses[j]+direction*min(room, amount))/u.capacities_m3[j]
            value = min(chi[j], max(clo[j], value))
            if value == c[j]:
                value = float(np.nextafter(c[j], chi[j] if direction > 0 else clo[j]))
            if value == c[j] or not clo[j] <= value <= chi[j]:
                raise RuntimeError('NO_REPRESENTABLE_FEASIBLE_REPAIR')
            c[j] = value
            updates += 1

        for _ in range(2*len(c)+32):
            mass = c*u.capacities_m3
            residual = _residuals(u, mass)
            if residual.feasible:
                break
            fixed_phase = False
            if u.phase_inventory_kg is not None:
                for j, ((lo, hi), value) in enumerate(zip(u.phase_inventory_kg, residual.phase_totals_kg)):
                    if value < lo or value > hi:
                        move(np.arange(j*n, (j+1)*n), lo-value if value < lo else value-hi,
                             1 if value < lo else -1)
                        fixed_phase = True
                        break
            if fixed_phase:
                continue
            lo, hi = u.total_inventory_kg
            direction = 1 if residual.total_kg < lo else -1
            amount = lo-residual.total_kg if direction > 0 else residual.total_kg-hi
            rooms = []
            for j in range(3):
                p = residual.phase_totals_kg[j]
                bound = u.phase_inventory_kg[j] if u.phase_inventory_kg is not None else (0., u.inventory_scale_kg)
                room = bound[1]-p if direction > 0 else p-bound[0]
                cell_room = math.fsum((u.upper_masses_kg-mass if direction > 0 else
                                      mass-u.lower_masses_kg)[j*n:(j+1)*n])
                rooms.append(min(room, cell_room))
            j = int(np.argmax(rooms))
            move(np.arange(j*n, (j+1)*n), min(amount, rooms[j]), direction)
        else:
            raise RuntimeError('FEASIBLE_REPAIR_ITERATION_LIMIT')
        state = sf.FVChemicalState.from_cell_averages(solute=u.lower.solute, grind=u.lower.grind,
            time_s=u.lower.time_s, edges_m=u.lower.edges_m,
            liquid_kg_m3=c[:n], fine_kg_m3=c[n:2*n], coarse_kg_m3=c[2*n:])
        mass = _concentrations(state)*u.capacities_m3
        residual = _residuals(u, mass)
        if not residual.feasible or np.any(_concentrations(state) < clo) or np.any(_concentrations(state) > chi):
            raise RuntimeError('RECONSTRUCTED_WITNESS_OUTSIDE_ORIGINAL_SET')
        prediction = _dot(g, mass)
        change = math.fsum(map(float, np.abs(mass-m)))
    except (ValueError, RuntimeError, OverflowError, FloatingPointError) as exc:
        reason = str(exc) if isinstance(exc, RuntimeError) else 'WITNESS_RECONSTRUCTION:'+type(exc).__name__
        state = None
    if updates:
        repair = 'EXPLICIT_ORIGINAL_BOX_CLAMP_AND_LAMINAR_INVENTORY_REBALANCE'
    return FVWitness(state, m, mass, raw, residual, prediction, change, repair, updates,
        'FEASIBLE' if state is not None else 'NUMERICALLY_UNRESOLVED', reason)


def _dot(g, m):
    with np.errstate(over='ignore', under='ignore', invalid='ignore'):
        products = g*m
    if not np.isfinite(products).all() or np.any((g != 0) & (m != 0) & (products == 0)):
        raise RuntimeError('UNREPRESENTABLE_DOT_PRODUCT')
    return math.fsum(map(float, products))


@dataclass(frozen=True, eq=False)
class FVOptimizationEvidence:
    solver_status: int
    termination: str
    iterations: int
    calls: int
    scale_kg: float
    objective_scale: float
    raw_objective_kg: float | None
    checked_dual_lower_kg: float | None
    dual_roundoff_allowance_kg: float | None
    stationarity_residual_inf: float | None
    inequality_duals: np.ndarray
    elapsed_wall_s: float
    settings: FVEnvelopeSettings

    def __post_init__(self):
        _seal(self)


@dataclass(frozen=True)
class FVExtremum:
    sense: str
    interval_kg: tuple[float, float]
    gap_kg: float
    optimizer_gap_kg: float | None
    response_allowance_kg: float
    summation_conversion_allowance_kg: float
    optimization: FVOptimizationEvidence
    witness: FVWitness | None
    status: str
    termination: str


def _constraints(u):
    n = len(u.lower_masses_kg)
    rows, rhs = [np.ones(n), -np.ones(n)], [u.total_inventory_kg[1], -u.total_inventory_kg[0]]
    for j, (lo, hi) in enumerate(u.phase_inventory_kg or ()):
        row = np.zeros(n); row[j*n//3:(j+1)*n//3] = 1.
        rows.extend((row, -row)); rhs.extend((hi, -lo))
    return np.array(rows), np.array(rhs)


def _optimize(u, g, coefficient_allowances, sense, settings):
    """HiGHS plus independently checked weak-duality evidence in a finite box."""
    start = time.monotonic()
    sign = 1 if sense == 'minimum' else -1
    scale = u.inventory_scale_kg
    response_error = float(np.max(coefficient_allowances))*scale
    unrepresentable_error = response_error == 0 and scale > 0 and np.any(coefficient_allowances > 0)
    radius = float(np.max(np.abs(g)))*scale
    fallback = (-radius-response_error, radius+response_error)
    witness = None
    solver_status, iterations, calls = -1, 0, 0
    dual = np.array([])
    raw_obj = dual_lower = dual_allowance = stationarity = opt_gap = None
    sum_error = 0.
    objective_scale = float(np.max(np.abs(g))) or 1.  # dimensionless, never a mass floor
    reason, status = 'COMPLETE', 'OPTIMIZATION_QUALIFIED'
    interval = fallback
    try:
        if unrepresentable_error:
            raise RuntimeError('UNREPRESENTABLE_RESPONSE_ALLOWANCE')
        if scale == 0:
            witness = _witness(u, np.zeros(len(g)), g, settings)
            interval, raw_obj, dual_lower, dual_allowance, stationarity, opt_gap = (0., 0.), 0., 0., 0., 0., 0.
            solver_status, reason = 0, 'ANALYTIC_ZERO_SET'
        else:
            A, rhs = _constraints(u)
            lo = u.lower_masses_kg/scale
            # Redundant per-cell m_i <= total feasible inventory keeps scaling
            # finite. Original cell, phase and total constraints remain checked.
            hi = np.minimum(u.upper_masses_kg, scale)/scale
            b = rhs/scale
            c = sign*g/objective_scale
            if (not np.isfinite(np.r_[lo, hi, b, c]).all()
                    or np.any((u.lower_masses_kg > 0) & (lo == 0))
                    or np.any((u.upper_masses_kg > 0) & (hi == 0))
                    or np.any((rhs != 0) & (b == 0))):
                raise RuntimeError('UNREPRESENTABLE_LP_SCALING')
            calls = 1
            with warnings.catch_warnings():
                # SciPy forwards this native HiGHS option at the dependency floor.
                warnings.filterwarnings('ignore', message='Unrecognized options detected.*', category=OptimizeWarning)
                result = linprog(c, A_ub=A, b_ub=b, bounds=np.column_stack((lo, hi)),
                    method='highs-ds', options=dict(maxiter=settings.max_lp_iterations,
                    time_limit=settings.lp_wall_s, primal_feasibility_tolerance=settings.primal_tolerance,
                    dual_feasibility_tolerance=settings.dual_tolerance, threads=1))
            solver_status, iterations = int(result.status), int(result.nit or 0)
            if not result.success or solver_status != 0:
                raise RuntimeError('OPTIMIZER_TERMINATED:'+str(solver_status))
            x = np.asarray(result.x)
            if x.shape != g.shape or not np.isfinite(x).all():
                raise RuntimeError('INVALID_OPTIMIZER_VECTOR')
            mass = x*scale
            if np.any((x != 0) & (mass == 0)) or not np.isfinite(mass).all():
                raise RuntimeError('UNREPRESENTABLE_OPTIMIZER_MASS')
            raw_obj = _dot(sign*g, mass)
            independent_fun = _dot(c, x)
            if abs(independent_fun-float(result.fun)) > 128*EPS*max(1., abs(independent_fun)):
                raise RuntimeError('OPTIMIZER_OBJECTIVE_RECOMPUTATION_FAILED')
            original_dual = np.asarray(result.ineqlin.marginals)
            if original_dual.shape != b.shape or not np.isfinite(original_dual).all():
                raise RuntimeError('INVALID_DUAL_VECTOR')
            if np.any(original_dual > settings.dual_tolerance):
                raise RuntimeError('DUAL_SIGN_CHECK_FAILED')
            # Explicit projection of DUAL multipliers onto y<=0. This changes
            # neither the primal constraints nor the supplied state set.
            dual = np.minimum(original_dual, 0.)
            aty = np.array([math.fsum(float(A[j, i]*dual[j]) for j in range(len(b)))
                            for i in range(len(c))])
            residual = c-aty
            stationarity = float(np.max(np.abs(residual)))
            support = np.minimum(residual*lo, residual*hi)
            value = math.fsum((*map(float, dual*b), *map(float, support)))
            # For ANY y<=0, y.b + min_box (c-A^T y).x is a global lower
            # bound. A stationarity error therefore cannot be hidden by success.
            magnitude = math.fsum(map(float, np.abs(dual*b))) + math.fsum(
                float((abs(c[i])+math.fsum(abs(float(A[j, i]*dual[j])) for j in range(len(b))))*hi[i])
                for i in range(len(c)))
            allowance = 128*EPS*(len(b)+2)*magnitude
            dual_lower = float(np.nextafter((value-allowance)*objective_scale*scale, -np.inf))
            dual_allowance = allowance*objective_scale*scale
            if not math.isfinite(dual_lower) or (allowance > 0 and dual_allowance == 0):
                raise RuntimeError('UNREPRESENTABLE_DUAL_EVIDENCE')
            witness = _witness(u, mass, g, settings)
            if witness.status != 'FEASIBLE':
                raise RuntimeError(witness.termination)
            pred = witness.prediction_kg
            sum_error = 64*EPS*math.fsum(map(float, np.abs(g*witness.masses_kg)))
            if sum_error == 0 and pred != 0:
                raise RuntimeError('UNREPRESENTABLE_SUMMATION_ALLOWANCE')
            signed_upper = sign*pred+sum_error
            if signed_upper < dual_lower:
                raise RuntimeError('PRIMAL_DUAL_ORDER_CHECK_FAILED')
            opt_gap = signed_upper-dual_lower
            lower, upper = dual_lower-response_error, signed_upper+response_error
            interval = ((float(np.nextafter(lower, -np.inf)), float(np.nextafter(upper, np.inf)))
                        if sign == 1 else
                        (float(np.nextafter(-upper, -np.inf)), float(np.nextafter(-lower, np.inf))))
            if not np.any(g) and not np.any(coefficient_allowances):
                interval, opt_gap, dual_lower = (0., 0.), 0., 0.
    except Exception as exc:
        status = 'NUMERICALLY_UNRESOLVED'
        reason = str(exc) if isinstance(exc, RuntimeError) else 'OPTIMIZATION_EXCEPTION:'+type(exc).__name__
    evidence = FVOptimizationEvidence(solver_status, reason, iterations, calls, scale, objective_scale,
        raw_obj, dual_lower, dual_allowance, stationarity, dual, time.monotonic()-start, settings)
    return FVExtremum(sense, interval, interval[1]-interval[0], opt_gap, response_error,
        sum_error, evidence, witness, status, reason)


@dataclass(frozen=True)
class FVReplay:
    state_identity: str
    response_identity: str
    forward_status: str
    forward_reason: str | None
    forward_window_status: str
    forward_actual_end_s: float
    prediction_kg: float
    forward_delivery_kg: float | None
    discrepancy_kg: float | None
    response_allowance_kg: float
    forward_arithmetic_allowance_kg: float
    summation_conversion_allowance_kg: float
    status: str
    termination: str
    exponential_applications: int
    elapsed_wall_s: float
    parent_accuracy: str = 'NOT_ASSESSED'


@dataclass(frozen=True)
class FVEnvelopeResult:
    kind: str
    state_set: FVChemicalStateSet
    responses: tuple
    epsilon_kg: float
    delta_kg: float | None
    comparison_basis: str | None
    volume_difference_m3: float | None
    volume_match_allowance_m3: float | None
    minimum: FVExtremum | None
    maximum: FVExtremum | None
    outer_delivery_interval_kg: tuple | None
    concentration_interval_kg_m3: tuple | None
    numerical_status: str
    decision_status: str
    termination: str
    opposite_sign_reversal_supported: bool = False
    material_reversal_supported: bool = False
    discretization_status: str = 'NOT_INCLUDED_IN_FIXED_OPERATOR_ENCLOSURE'
    PHYSICAL_VALIDATION: str = 'NOT_ESTABLISHED'
    scope: str = 'RESEARCH_ONLY'
    certificate_kind: str = 'ENGINEERING_ENCLOSURE_NOT_RIGOROUS_INTERVAL_ARITHMETIC'

    @property
    def optimization_calls(self):
        return sum(e.optimization.calls for e in (self.minimum, self.maximum) if e is not None)

    @property
    def forward_calls(self):
        return sum(len(e.witness.replays) for e in (self.minimum, self.maximum)
                   if e is not None and e.witness is not None)

    def to_json(self, *, include_arrays=False, include_timing=False):
        """Canonical strict JSON; bulky fields and nondeterministic timing opt in."""
        def convert(v):
            if isinstance(v, sf.FVChemicalState) and not include_arrays:
                return dict(state_identity=v.identity_sha256, model_identity=v.model_identity,
                    solute=v.solute, grind=v.grind, time_s=v.time_s, cells=len(v.edges_m)-1,
                    inventory_kg=v.inventory_kg)
            if isinstance(v, sf.FVPlan) and not include_arrays:
                return dict(plan_identity=v.identity_sha256, span_s=v.t_span_s,
                    settings=sf._json(v.settings), primary_steps=len(v.primary_steps),
                    temperature_history=sf._json(v.temperature_history), flow_history=sf._json(v.flow_history))
            if isinstance(v, np.ndarray):
                return (v.tolist() if include_arrays else
                        dict(shape=list(v.shape), sha256=hashlib.sha256(v.tobytes()).hexdigest()))
            if is_dataclass(v):
                return {f.name: convert(getattr(v, f.name)) for f in fields(v)
                        if include_timing or f.name != 'elapsed_wall_s'}
            if isinstance(v, (list, tuple)):
                return [convert(x) for x in v]
            if isinstance(v, np.generic):
                return v.item()
            return v
        value = convert(self)
        value.update(optimization_calls=self.optimization_calls, forward_calls=self.forward_calls)
        return json.dumps(value, sort_keys=True, indent=2, allow_nan=False)


def _bound(u, responses, epsilon_kg, delta_kg=None, basis=None, volume_difference=None, volume_allowance=None):
    if not isinstance(u, FVChemicalStateSet):
        raise ValueError('CHEMICAL_STATE_SET_REQUIRED')
    epsilon = _real(epsilon_kg, 'epsilon kg', nonnegative=True)
    if epsilon <= 0:
        raise ValueError('POSITIVE_EXTREMUM_GAP_RESOLUTION_REQUIRED')
    for response in responses:
        if not isinstance(response, FVDeliveryResponse):
            raise ValueError('DELIVERY_RESPONSE_REQUIRED')
        response.validate(u)
    contrast = len(responses) == 2
    kind = 'DIRECT_SHARED_STATE_CONTRAST' if contrast else 'DELIVERY_ENVELOPE'
    base = FVEnvelopeResult(kind, u, responses, epsilon, delta_kg, basis, volume_difference,
        volume_allowance, None, None, None, None, 'NUMERICALLY_UNRESOLVED',
        'NUMERICALLY_UNRESOLVED' if contrast else 'NOT_A_DECISION_QUERY', 'NOT_EVALUATED')
    if u.feasibility != 'ESTABLISHED_NONEMPTY':
        return replace(base, numerical_status='EMPTY_FEASIBLE_SET', termination=u.feasibility)
    fallback = (-u.inventory_scale_kg if contrast else 0., u.inventory_scale_kg)
    if any(r.status != 'RESPONSE_QUALIFIED' for r in responses):
        return replace(base, outer_delivery_interval_kg=fallback,
            termination='INVENTORY_FALLBACK_ONLY;'+ ';'.join(r.termination for r in responses))
    g = responses[0].weights.copy()
    error = responses[0].coefficient_allowances.copy()
    if contrast:
        g -= responses[1].weights
        error += responses[1].coefficient_allowances + 2*EPS*(
            np.abs(responses[0].weights)+np.abs(responses[1].weights))
    extrema = tuple(_optimize(u, g, error, sense, responses[0].settings)
                    for sense in ('minimum', 'maximum'))
    checked = []
    for e in extrema:
        lo, hi = e.interval_kg if e.status == 'OPTIMIZATION_QUALIFIED' else fallback
        lo, hi = max(fallback[0], lo), min(fallback[1], hi)
        if lo > hi:
            e = replace(e, status='NUMERICALLY_UNRESOLVED', termination='EMPTY_NUMERICAL_ENCLOSURE')
            lo, hi = fallback
        checked.append(replace(e, interval_kg=(lo, hi), gap_kg=hi-lo))
    minimum, maximum = checked
    outer = (minimum.interval_kg[0], maximum.interval_kg[1])
    ready = all(e.status == 'OPTIMIZATION_QUALIFIED' and e.gap_kg <= epsilon
                and e.witness is not None and e.witness.status == 'FEASIBLE' for e in checked)
    concentration = None
    reason = 'FRESH_PRIMARY_WITNESS_REPLAYS_REQUIRED' if ready else 'EXTREMUM_EVIDENCE_OR_RESOLUTION_FAILED'
    if not contrast and responses[0].volume_m3 > 0:
        concentration = tuple(v/responses[0].volume_m3 for v in outer)
        if not all(math.isfinite(v) for v in concentration) or any(
                m > 0 and c == 0 for m, c in zip(outer, concentration)):
            concentration, ready, reason = None, False, 'UNREPRESENTABLE_CONCENTRATION'
    return replace(base, minimum=minimum, maximum=maximum, outer_delivery_interval_kg=outer,
        concentration_interval_kg_m3=concentration,
        numerical_status='WITNESS_REPLAY_REQUIRED' if ready else 'NUMERICALLY_UNRESOLVED', termination=reason)


def bound_delivery(state_set, response, *, epsilon_kg):
    """Optimize both delivery extrema; fresh witness replay is a separate operation."""
    return _bound(state_set, (response,), epsilon_kg)


def contrast_deliveries(state_set, response_a, response_b, *, epsilon_kg, delta_kg, comparison_basis):
    """Optimize (g_A-g_B).m over the SAME U, never subtract separate envelopes."""
    margin = _real(delta_kg, 'delta kg', nonnegative=True)
    if comparison_basis not in ('MATCHED_COLLECTED_VOLUME', 'EXPLICIT_UNEQUAL_VOLUME'):
        raise ValueError('EXPLICIT_COMPARISON_BASIS_REQUIRED')
    if not isinstance(response_a, FVDeliveryResponse) or not isinstance(response_b, FVDeliveryResponse):
        raise ValueError('DELIVERY_RESPONSES_REQUIRED')
    difference = response_a.volume_m3-response_b.volume_m3
    allowance = 64*EPS*max(response_a.volume_m3, response_b.volume_m3)
    if comparison_basis == 'MATCHED_COLLECTED_VOLUME' and abs(difference) > allowance:
        raise ValueError('PRESCRIBED_COLLECTION_VOLUMES_DO_NOT_MATCH')
    return _bound(state_set, (response_a, response_b), epsilon_kg, margin,
                  comparison_basis, difference, allowance)


def replay_witness(state_set, response, witness):
    """ONE fresh unchanged forward trajectory. Explicitly invoked, never in an LP."""
    response.validate(state_set)
    if not isinstance(witness, FVWitness) or witness.state is None:
        raise ValueError('RECONSTRUCTED_FEASIBLE_WITNESS_REQUIRED')
    witness.state.validate()
    m = _concentrations(witness.state)*state_set.capacities_m3
    if not _residuals(state_set, m).feasible or not np.array_equal(m, witness.masses_kg):
        raise ValueError('WITNESS_OUTSIDE_OR_CHANGED_FROM_ORIGINAL_SET')
    prediction = _dot(response.weights, m)
    response_allowance = _dot(response.coefficient_allowances, m)
    sum_allowance = 64*EPS*math.fsum(map(float, np.abs(response.weights*m)))
    start = time.monotonic()
    try:
        forward = sf.simulate_stateful_fv(plan=response.plan, initial_state=witness.state,
            observation_times_s=tuple(sorted(set(response.window_s))), fraction_windows_s=(response.window_s,))
    except Exception as exc:
        return FVReplay(witness.state.identity_sha256, response.identity_sha256, 'FORWARD_REJECTED',
            type(exc).__name__, 'UNSUPPORTED', response.plan.t_span_s[0], prediction, None, None,
            response_allowance, 0., sum_allowance, 'NUMERICALLY_UNRESOLVED', 'FORWARD_REJECTION',
            0, time.monotonic()-start)
    fraction = forward.fractions[0]
    allowance = 256*EPS*(1+forward.exponential_applications+response.conditioning_sum)*math.fsum(m)
    discrepancy = None if fraction.solute_kg is None else fraction.solute_kg-prediction
    supported = (forward.status == 'COMPLETE' and forward.integration_complete
                 and all(s == 'SUPPORTED' for s in forward.observation_status)
                 and fraction.solute_kg is not None
                 and (fraction.status in ('VALID_NUMERICAL_ZERO', 'NUMERICAL_ONLY_ACCURACY_NOT_ASSESSED')
                      or response.window_s[0] == response.window_s[1]))
    good = supported and abs(discrepancy) <= response_allowance+allowance+sum_allowance
    if (math.fsum(m) > 0 and response.window_s[1] > response.window_s[0]
            and (prediction <= 0 or fraction.solute_kg is None or fraction.solute_kg <= 0)):
        good = False
    return FVReplay(witness.state.identity_sha256, response.identity_sha256, forward.status,
        forward.reason, fraction.status, forward.actual_end_s, prediction, fraction.solute_kg,
        discrepancy, response_allowance, allowance, sum_allowance,
        'REPLAY_QUALIFIED' if good else 'NUMERICALLY_UNRESOLVED',
        'COMPLETE' if good else 'FORWARD_SUPPORT_OR_REPLAY_DISCREPANCY_FAILED',
        forward.exponential_applications, time.monotonic()-start)


def qualify_envelope(result, *, minimum_replays, maximum_replays):
    """Attach fresh receipts, preserving all failures and underlying witness facts."""
    if result.minimum is None or result.maximum is None:
        return result
    extrema = []
    all_replays = tuple(minimum_replays)+tuple(maximum_replays)
    if len({id(r) for r in all_replays}) != len(all_replays):
        raise ValueError('FRESH_REPLAYS_REQUIRED_FOR_EACH_PRIMARY_WITNESS')
    for extremum, receipts in zip((result.minimum, result.maximum), (minimum_replays, maximum_replays)):
        witness = extremum.witness
        if witness is None or witness.state is None or len(receipts) != len(result.responses):
            raise ValueError('ALL_PRIMARY_WITNESS_PLAN_REPLAYS_REQUIRED')
        for response, receipt in zip(result.responses, receipts):
            if (not isinstance(receipt, FVReplay) or receipt.state_identity != witness.state.identity_sha256
                    or receipt.response_identity != response.identity_sha256):
                raise ValueError('REPLAY_WITNESS_OR_RESPONSE_MISMATCH')
        interval = None
        if all(r.status == 'REPLAY_QUALIFIED' for r in receipts):
            signs = (1.,) if len(receipts) == 1 else (1., -1.)
            pred = math.fsum(s*r.prediction_kg for s, r in zip(signs, receipts))
            value = math.fsum(s*r.forward_delivery_kg for s, r in zip(signs, receipts))
            pe = math.fsum(r.response_allowance_kg+r.summation_conversion_allowance_kg for r in receipts)
            fe = math.fsum(r.forward_arithmetic_allowance_kg+r.summation_conversion_allowance_kg for r in receipts)
            cancellation = 4*EPS*math.fsum(abs(r.prediction_kg)+abs(r.forward_delivery_kg) for r in receipts)
            interval = (min(pred-pe, value-fe)-cancellation, max(pred+pe, value+fe)+cancellation)
        extrema.append(replace(extremum, witness=replace(witness, replays=tuple(receipts), replay_interval_kg=interval)))
    minimum, maximum = extrema
    good = (result.numerical_status in ('WITNESS_REPLAY_REQUIRED', 'NUMERICALLY_QUALIFIED')
            and all(e.witness.replay_interval_kg is not None for e in extrema))
    intervals = [e.witness.replay_interval_kg for e in extrema if e.witness.replay_interval_kg is not None]
    margin = result.delta_kg
    decision, opposite, reversal = _decision(result.outer_delivery_interval_kg, margin, intervals, good)
    return replace(result, minimum=minimum, maximum=maximum,
        numerical_status='NUMERICALLY_QUALIFIED' if good else 'NUMERICALLY_UNRESOLVED',
        decision_status=decision, termination='COMPLETE' if good else 'PRIMARY_NUMERICAL_QUALIFICATION_FAILED',
        opposite_sign_reversal_supported=bool(opposite), material_reversal_supported=bool(reversal))


def _decision(outer, margin, intervals, qualified):
    opposite = any(i[0] > 0 for i in intervals) and any(i[1] < 0 for i in intervals)
    reversal = (margin is not None and any(i[0] > margin for i in intervals)
                and any(i[1] < -margin for i in intervals))
    decision = 'NOT_A_DECISION_QUERY'
    if margin is not None:
        decision = 'NUMERICALLY_UNRESOLVED'
        if qualified:
            lower, upper = outer
            if lower > margin:
                decision = 'A_UNIFORMLY_EXCEEDS_B_BY_MARGIN'
            elif upper < -margin:
                decision = 'B_UNIFORMLY_EXCEEDS_A_BY_MARGIN'
            elif lower >= -margin and upper <= margin:
                decision = 'NO_MATERIAL_DIFFERENCE_THROUGHOUT_SET'
            elif reversal:
                decision = 'DEMONSTRATED_MATERIAL_REVERSAL'
            else:
                decision = 'NO_UNIFORM_MATERIAL_CONCLUSION'
    return decision, opposite, bool(reversal)


def replay_extrema(result):
    """Explicit convenience operation: two forwards for an envelope, four for a contrast."""
    if result.minimum is None or result.maximum is None or any(
            e.witness is None or e.witness.state is None for e in (result.minimum, result.maximum)):
        return result
    receipts = [tuple(replay_witness(result.state_set, r, e.witness) for r in result.responses)
                for e in (result.minimum, result.maximum)]
    return qualify_envelope(result, minimum_replays=receipts[0], maximum_replays=receipts[1])
