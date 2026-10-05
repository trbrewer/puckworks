"""Joint early-fraction conditioning of an unchanged Pannusch FV state set.

G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Inherited response errors are engineering
estimates, not rigorous interval arithmetic, confidence intervals or continuum
certificates. Pannusch et al., DOI 10.1016/j.jfoodeng.2023.111887; source-derived
output CC-BY-NC-3.0 (10.17632/y2tz67f6ry.1), separate from first-party code.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass, replace
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import time
import warnings

import numpy as np
from scipy.optimize import linprog, OptimizeWarning

from . import state_envelope as se, stateful_fv as sf

MAX_OBSERVATIONS = 32
CONTRACT = 'ENGINEERING_ALLOWANCE_CONDITIONAL_NOT_RIGOROUS_OR_STATISTICAL'
F = Fraction.from_float


def _q(x):
    return F(float(x))


def _rounded(q, direction=0):
    """Directed conversion of an exact binary-rational calculation, no silent underflow."""
    try:
        x = float(q)
    except OverflowError as exc:
        raise RuntimeError('UNREPRESENTABLE_ARITHMETIC') from exc
    if not math.isfinite(x) or (q and x == 0):
        raise RuntimeError('UNREPRESENTABLE_ARITHMETIC')
    if direction < 0 and _q(x) > q:
        x = float(np.nextafter(x, -np.inf))
    if direction > 0 and _q(x) < q:
        x = float(np.nextafter(x, np.inf))
    if not math.isfinite(x) or (q and x == 0):
        raise RuntimeError('UNREPRESENTABLE_DIRECTED_CONVERSION')
    return x


def _product(a, b):
    q = _q(a)*_q(b)
    _rounded(q)  # Detect even intermediate product underflow/overflow explicitly.
    return q


def _dotq(a, b):
    return sum((_product(x, y) for x, y in zip(a, b)), Fraction())


def _array(value, shape, name):
    obj = np.asarray(value, dtype=object)
    if obj.shape != shape:
        raise ValueError(name+': SHAPE')
    out = np.array([se._real(v, name) for v in obj.flat]).reshape(shape)
    return se._readonly(out)


def _label(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 512:
        raise ValueError('NONEMPTY_BOUNDED_LABEL_REQUIRED')
    return value


def _source():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


@dataclass(frozen=True, eq=False)
class _Polytope:
    """Numerical core, deliberately independent of production response identities."""
    lower: np.ndarray
    upper: np.ndarray
    A: np.ndarray
    b: np.ndarray
    scale_kg: float
    row_labels: tuple

    def __post_init__(self):
        n = len(self.lower)
        if not 1 <= n <= 6001 or not 0 <= len(self.b) <= 128:
            raise ValueError('CORE_ALLOCATION_LIMIT')
        for name, shape in [('lower', (n,)), ('upper', (n,)),
                            ('A', (len(self.b), n)), ('b', (len(self.b),))]:
            object.__setattr__(self, name, _array(getattr(self, name), shape, name))
        if np.any(self.lower < 0) or np.any(self.upper < self.lower):
            raise ValueError('INVALID_FINITE_BOX')
        object.__setattr__(self, 'scale_kg', se._real(self.scale_kg, 'scale', nonnegative=True))
        labels = tuple(_label(s) for s in self.row_labels)
        if len(labels) != len(self.b):
            raise ValueError('ROW_LABELS_REQUIRED')
        object.__setattr__(self, 'row_labels', labels)


@dataclass(frozen=True, eq=False)
class _Residuals:
    row_violations_kg: np.ndarray
    box_lower_violations_kg: np.ndarray
    box_upper_violations_kg: np.ndarray
    feasible: bool

    def __post_init__(self):
        se._seal(self)


def _residuals(poly, mass):
    if np.shape(mass) != poly.lower.shape or not np.isfinite(mass).all():
        raise RuntimeError('INVALID_PRIMAL_MASSES')
    rows = [_dotq(a, mass)-_q(b) for a, b in zip(poly.A, poly.b)]
    lower = [_q(a)-_q(m) for a, m in zip(poly.lower, mass)]
    upper = [_q(m)-_q(b) for b, m in zip(poly.upper, mass)]
    good = all(v <= 0 for v in (*rows, *lower, *upper))
    return _Residuals(np.array([_rounded(v, 1) for v in rows]),
        np.array([_rounded(v, 1) for v in lower]),
        np.array([_rounded(v, 1) for v in upper]), good)


@dataclass(frozen=True, eq=False)
class _LPEvidence:
    problem: _Polytope
    objective: np.ndarray
    solver_status: int = -1
    termination: str = 'NOT_CALLED'
    iterations: int = 0
    calls: int = 0
    objective_scale: float = 1.
    raw_masses_kg: np.ndarray | None = None
    raw_residuals: _Residuals | None = None
    raw_objective_kg: float | None = None
    checked_dual_lower_kg: float | None = None
    dual_conversion_allowance_kg: float | None = None
    inequality_duals: np.ndarray | None = None
    projected_duals: np.ndarray | None = None
    stationarity_residual: np.ndarray | None = None
    scaling_roundoff_kg: float | None = None
    elapsed_wall_s: float = 0.
    status: str = 'UNRESOLVED'

    def __post_init__(self):
        se._seal(self)


def _weak_dual(poly, c, y):
    """Original-kg finite-box weak duality; exact sums of binary64 inputs.

    ANY y<=0 works. A poor dual produces a loose bound, never a fake small gap.
    No solver residual tolerance participates in this certificate.
    """
    if np.shape(y) != poly.b.shape or not np.isfinite(y).all() or np.any(y > 0):
        raise RuntimeError('DUAL_SIGN_OR_SHAPE')
    residual = [_q(c[i])-_dotq(poly.A[:, i], y) for i in range(len(c))]
    support = [min(r*_q(lo), r*_q(hi)) for r, lo, hi in zip(residual, poly.lower, poly.upper)]
    for v in support:
        _rounded(v)
    exact = _dotq(y, poly.b)+sum(support, Fraction())
    lower = _rounded(exact, -1)
    allowance = _rounded(exact-_q(lower), 1)
    return lower, allowance, np.array([_rounded(v) for v in residual])


def _solve(poly, objective, settings):
    """One bounded HiGHS call plus independent original-coordinate checks."""
    c = _array(objective, poly.lower.shape, 'objective')
    start = time.monotonic()
    e = _LPEvidence(poly, c)
    try:
        if np.array_equal(poly.lower, poly.upper):
            m = poly.lower
            res = _residuals(poly, m)
            obj = _rounded(_dotq(c, m))
            return replace(e, solver_status=0, termination='ANALYTICAL_SINGLETON',
                raw_masses_kg=m, raw_residuals=res, raw_objective_kg=obj,
                checked_dual_lower_kg=_rounded(_dotq(c, m), -1),
                dual_conversion_allowance_kg=0., status='CHECKED' if res.feasible else 'UNRESOLVED')
        scale = poly.scale_kg
        if scale <= 0:
            raise RuntimeError('NONZERO_BOX_WITH_ZERO_SCALE')
        cs = float(np.max(np.abs(c))) or 1.  # dimensionless, never an inventory floor
        with np.errstate(all='ignore'):
            lo, hi, b, cn = poly.lower/scale, poly.upper/scale, poly.b/scale, c/cs
        for original, normalized in ((poly.lower, lo), (poly.upper, hi), (poly.b, b), (c, cn)):
            if not np.isfinite(normalized).all() or np.any((original != 0) & (normalized == 0)):
                raise RuntimeError('UNREPRESENTABLE_LP_SCALING')
        scaling = max((_q(abs(_rounded(_q(v)*_q(scale)-_q(o))))
                       for orig, norm in ((poly.lower, lo), (poly.upper, hi), (poly.b, b))
                       for o, v in zip(orig, norm)), default=Fraction())
        e = replace(e, calls=1, objective_scale=cs, scaling_roundoff_kg=_rounded(scaling, 1))
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='Unrecognized options detected.*', category=OptimizeWarning)
            result = linprog(cn, A_ub=poly.A, b_ub=b, bounds=np.column_stack((lo, hi)),
                method='highs-ds', options=dict(maxiter=settings.max_lp_iterations,
                time_limit=min(30., settings.lp_wall_s), threads=1,
                primal_feasibility_tolerance=settings.primal_tolerance,
                dual_feasibility_tolerance=settings.dual_tolerance))
        e = replace(e, solver_status=int(result.status), iterations=int(result.nit or 0))
        if time.monotonic()-start > min(30., settings.lp_wall_s):
            raise RuntimeError('LP_WALL_LIMIT')
        if not result.success or result.status != 0:
            raise RuntimeError('OPTIMIZER_TERMINATED:'+str(result.status))
        x = np.asarray(result.x)
        if x.shape != c.shape or not np.isfinite(x).all():
            raise RuntimeError('INVALID_OPTIMIZER_VECTOR')
        m = np.array([_rounded(_product(v, scale)) for v in x])
        res = _residuals(poly, m)
        obj = _rounded(_dotq(c, m))
        e = replace(e, raw_masses_kg=m, raw_residuals=res, raw_objective_kg=obj)
        fun = _dotq(cn, x)
        allowance = _q(128*se.EPS)*sum((abs(_product(a, b)) for a, b in zip(cn, x)), Fraction())
        if abs(fun-_q(result.fun)) > allowance:
            raise RuntimeError('OBJECTIVE_RECONSTRUCTION_FAILED')
        yd = np.asarray(result.ineqlin.marginals)
        if yd.shape != poly.b.shape or not np.isfinite(yd).all():
            raise RuntimeError('INVALID_DUAL_VECTOR')
        e = replace(e, inequality_duals=yd)
        if np.any(yd > settings.dual_tolerance):
            raise RuntimeError('DUAL_SIGN_CHECK_FAILED')
        # Project only duals, never observations or primal states. Rescale to kg
        # objective coordinates, then certify against ORIGINAL rows and bounds.
        y = np.array([_rounded(_product(min(v, 0.), cs)) for v in yd])
        lower, rounding, residual = _weak_dual(poly, c, y)
        if res.feasible and _q(lower) > _dotq(c, m):
            raise RuntimeError('PRIMAL_DUAL_ORDER_FAILED')
        e = replace(e, projected_duals=y, stationarity_residual=residual,
            checked_dual_lower_kg=lower, dual_conversion_allowance_kg=rounding,
            termination='COMPLETE', status='CHECKED')
    except Exception as exc:
        e = replace(e, status='UNRESOLVED', termination=str(exc) if isinstance(exc, RuntimeError)
                    else 'LP_EXCEPTION:'+type(exc).__name__)
    return replace(e, elapsed_wall_s=time.monotonic()-start)


def _phase_one(poly, settings):
    """A strictly positive CHECKED lower bound proves outer contradiction."""
    if np.array_equal(poly.lower, poly.upper):
        return _solve(poly, np.zeros(len(poly.lower)), settings)
    violations = [_dotq(a, poly.lower)-_q(b) for a, b in zip(poly.A, poly.b)]
    high = _rounded(max([Fraction(), *violations]), 1)
    phase = _Polytope(np.r_[poly.lower, 0.], np.r_[poly.upper, high],
        np.column_stack((poly.A, -np.ones(len(poly.b)))), poly.b, poly.scale_kg,
        poly.row_labels)
    return _solve(phase, np.r_[np.zeros(len(poly.lower)), 1.], settings)


def _coefficient_bounds(g, a):
    if np.shape(g) != np.shape(a) or np.any(np.asarray(a) < 0):
        raise ValueError('INVALID_RESPONSE_ALLOWANCE')
    return (np.array([_rounded(_q(x)-_q(y), -1) for x, y in zip(g, a)]),
            np.array([_rounded(_q(x)+_q(y), 1) for x, y in zip(g, a)]))


def _intersect(base, bands, *, inner):
    """bands are (label,g,a,l,u). Manufactured tests use this core directly."""
    rows, rhs, labels = list(base.A), list(base.b), list(base.row_labels)
    if len(bands) > MAX_OBSERVATIONS:
        raise ValueError('OBSERVATION_COUNT_LIMIT')
    for label, g, a, lo, hi in bands:
        low, high = _coefficient_bounds(g, a)
        rows.extend((high if inner else low, -low if inner else -high))
        rhs.extend((hi, -lo))
        labels.extend((label+':upper', label+':lower'))
    return _Polytope(base.lower, base.upper, np.array(rows), np.array(rhs),
                     base.scale_kg, tuple(labels))


def _base_polytope(u):
    A, b = se._constraints(u)
    labels = ['total:upper', 'total:lower']
    for name in se.PHASES if u.phase_inventory_kg is not None else ():
        labels.extend((name+':upper', name+':lower'))
    return _Polytope(u.lower_masses_kg, np.minimum(u.upper_masses_kg, u.inventory_scale_kg),
                     A, b, u.inventory_scale_kg, tuple(labels))


def _inward_repair_problem(poly, raw, settings):
    """A bounded ALL-row repair search, never laminar inventory rebalancing."""
    margin = _product(1024*se.EPS, poly.scale_kg)
    cap = _product(64*settings.primal_tolerance, poly.scale_kg)
    lo, hi = [], []
    for l, h, r in zip(poly.lower, poly.upper, raw):
        delta = min(margin/len(raw), (_q(h)-_q(l))/4)
        lo.append(_rounded(max(_q(l)+delta, _q(r)-cap/(2*len(raw))), 1))
        hi.append(_rounded(min(_q(h)-delta, _q(r)+cap/(2*len(raw))), -1))
    b = []
    for i, (row, value) in enumerate(zip(poly.A, poly.b)):
        equality = any(np.array_equal(row, -other) and value == -poly.b[j]
                       for j, other in enumerate(poly.A) if j != i)
        b.append(value if equality else _rounded(_q(value)-margin, -1))
    return _Polytope(np.array(lo), np.array(hi), poly.A, np.array(b), poly.scale_kg, poly.row_labels)


@dataclass(frozen=True, eq=False)
class FVEqualChildPullback:
    """Explicit P^T response on coarse masses; never a native coarse response.

    P splits each phase mass equally between two children. No new fine-cell
    freedom. The native response and its fine plan/source identity are retained.
    """
    native: se.FVDeliveryResponse
    coarse_model: sf.FVChemicalState
    weights: np.ndarray | None = field(init=False)
    coefficient_allowances: np.ndarray | None = field(init=False)
    mapping_roundoff_allowances: np.ndarray | None = field(init=False)
    identity_sha256: str = field(init=False)
    mapping: str = 'EQUAL_TWO_CHILD_PHASE_MASS_LIFT'

    def __post_init__(self):
        if not isinstance(self.native, se.FVDeliveryResponse) or not isinstance(self.coarse_model, sf.FVChemicalState):
            raise ValueError('NATIVE_RESPONSE_AND_COARSE_MODEL_REQUIRED')
        self.native.validate(); self.coarse_model.validate()
        if self.mapping != 'EQUAL_TWO_CHILD_PHASE_MASS_LIFT':
            raise ValueError('UNSUPPORTED_PULLBACK_MAPPING')
        lifted = _lift_state(self.coarse_model)
        if lifted.model_identity != self.native.model.model_identity or lifted.time_s != self.native.model.time_s:
            raise ValueError('PULLBACK_MODEL_MISMATCH')
        g = a = roundoff = None
        if self.native.weights is not None and self.native.coefficient_allowances is not None:
            g, a, roundoff = [], [], []
            for pair, error in zip(self.native.weights.reshape(-1, 2),
                                   self.native.coefficient_allowances.reshape(-1, 2)):
                exact = (_q(pair[0])+_q(pair[1]))/2
                value = _rounded(exact)
                conversion = abs(exact-_q(value))
                g.append(value)
                a.append(_rounded((_q(error[0])+_q(error[1]))/2+conversion, 1))
                roundoff.append(_rounded(conversion, 1))
            g, a, roundoff = np.array(g), np.array(a), np.array(roundoff)
        for name, value in [('weights', g), ('coefficient_allowances', a), ('mapping_roundoff_allowances', roundoff)]:
            object.__setattr__(self, name, value)
        se._seal(self)
        object.__setattr__(self, 'identity_sha256', self._identity())

    def _identity(self):
        return sf._hash((self.native.identity_sha256, self.coarse_model.model_identity,
                         self.coarse_model.time_s, self.mapping, self.weights, self.coefficient_allowances))

    @property
    def model(self):
        return self.coarse_model

    @property
    def plan(self):
        return self.native.plan

    @property
    def window_s(self):
        return self.native.window_s

    @property
    def status(self):
        return self.native.status

    @property
    def settings(self):
        return self.native.settings

    def validate(self, state_set=None):
        self.native.validate(); self.coarse_model.validate()
        if self._identity() != self.identity_sha256:
            raise ValueError('PULLBACK_IDENTITY_MISMATCH')
        if state_set is not None:
            state_set.validate()
            if (state_set.lower.model_identity != self.coarse_model.model_identity
                    or state_set.lower.time_s != self.coarse_model.time_s):
                raise ValueError('PULLBACK_STATE_SET_MISMATCH')


def _lift_state(state):
    n = len(state.edges_m)-1
    if 2*n > 2000:
        raise ValueError('FINE_MESH_RESOURCE_LIMIT')
    c = [np.repeat(getattr(state, p+'_cell_average_kg_m3'), 2) for p in se.PHASES]
    fine = sf.FVChemicalState.from_cell_averages(solute=state.solute, grind=state.grind,
        time_s=state.time_s, edges_m=np.linspace(0., sf.fv.ps.L, 2*n+1),
        liquid_kg_m3=c[0], fine_kg_m3=c[1], coarse_kg_m3=c[2])
    coarse_m = se._concentrations(state)*sf.fv._System(state.solute, state.grind, n).capacities
    fine_m = se._concentrations(fine)*sf.fv._System(state.solute, state.grind, 2*n).capacities
    expected = np.repeat(coarse_m/2, 2)
    if np.any((np.repeat(coarse_m, 2) > 0) & (expected == 0)) or not np.array_equal(fine_m, expected):
        raise ValueError('UNREPRESENTABLE_EXACT_EQUAL_CHILD_LIFT')
    return fine


def pull_back_equal_children(response, state_set):
    """Bind an explicit fine response to the original coarse coordinate space."""
    if not isinstance(state_set, se.FVChemicalStateSet):
        raise ValueError('ORIGINAL_STATE_SET_REQUIRED')
    state_set.validate()
    return FVEqualChildPullback(response, state_set.lower)


def _response(value, u=None):
    if not isinstance(value, (se.FVDeliveryResponse, FVEqualChildPullback)):
        raise ValueError('DELIVERY_RESPONSE_REQUIRED')
    value.validate(u)
    if value.window_s[1] <= value.window_s[0]:
        raise ValueError('POSITIVE_DURATION_FRACTION_REQUIRED')
    return value


@dataclass(frozen=True, eq=False)
class FVFractionObservation:
    """An already specified delivered-solute kg band on [start,end).

    The bound response supplies species/model, source/configuration, phase bases,
    mesh, absolute clock, plan and window identities. No assay conversion occurs.
    Duplicate bands/windows need distinct labels; labels themselves are unique.
    """
    label: str
    response: se.FVDeliveryResponse | FVEqualChildPullback
    mass_interval_kg: tuple[float, float]
    provenance: str
    identity_sha256: str = field(init=False)

    def __post_init__(self):
        _label(self.label); _label(self.provenance); _response(self.response)
        band = se._interval(self.mass_interval_kg, 'observation kg')
        object.__setattr__(self, 'mass_interval_kg', band)
        object.__setattr__(self, 'identity_sha256', self._identity())

    def _identity(self):
        return sf._hash((self.label, self.response.identity_sha256, self.mass_interval_kg, self.provenance))

    def validate(self, u, plan):
        self.response.validate(u)
        if self.response.plan.identity_sha256 != plan.identity_sha256:
            raise ValueError('OBSERVATION_PLAN_MISMATCH')
        if self.identity_sha256 != self._identity():
            raise ValueError('OBSERVATION_IDENTITY_MISMATCH')


@dataclass(frozen=True, eq=False)
class FVPrefixConditionedSet:
    """The original U AND every joint observation constraint, never tightened boxes."""
    original: se.FVChemicalStateSet
    plan: sf.FVPlan
    observations: tuple[FVFractionObservation, ...]
    algorithm_source_sha256: str = field(default_factory=_source)
    identity_sha256: str = field(init=False)
    allowance_contract: str = CONTRACT

    def __post_init__(self):
        if not isinstance(self.original, se.FVChemicalStateSet) or not isinstance(self.plan, sf.FVPlan):
            raise ValueError('ORIGINAL_SET_AND_IMMUTABLE_PLAN_REQUIRED')
        self.original.validate(); self.plan.validate()
        if not isinstance(self.observations, (list, tuple)) or len(self.observations) > MAX_OBSERVATIONS:
            raise ValueError('BOUNDED_OBSERVATION_LIST_REQUIRED')
        if not self.observations and len(self.original.lower.edges_m)-1 != self.plan.settings.cells:
            raise ValueError('MESH_MISMATCH_REQUIRES_EXPLICIT_PULLBACK_OBSERVATIONS')
        if self.original.lower.time_s != self.plan.t_span_s[0]:
            raise ValueError('INITIAL_CLOCK_MISMATCH')
        for obs in self.observations:
            if not isinstance(obs, FVFractionObservation):
                raise ValueError('FRACTION_OBSERVATION_REQUIRED')
            obs.validate(self.original, self.plan)
        if len({o.label for o in self.observations}) != len(self.observations):
            raise ValueError('UNIQUE_OBSERVATION_LABELS_REQUIRED')
        observations = tuple(sorted(self.observations, key=lambda o: (o.label, o.identity_sha256)))
        object.__setattr__(self, 'observations', observations)
        object.__setattr__(self, 'identity_sha256', self._identity())

    def _identity(self):
        return sf._hash((self.original.identity_sha256, self.plan.identity_sha256,
            tuple(o.identity_sha256 for o in self.observations), self.algorithm_source_sha256))

    def validate(self):
        self.original.validate(); self.plan.validate()
        for obs in self.observations:
            obs.validate(self.original, self.plan)
        if self.identity_sha256 != self._identity() or self.algorithm_source_sha256 != _source():
            raise ValueError('CONDITIONED_SET_IDENTITY_OR_SOURCE_MISMATCH')


def condition_on_fractions(state_set, plan, observations):
    """Retain joint constraints. No propagation, fit, LP, equilibrium or prior."""
    return FVPrefixConditionedSet(state_set, plan, observations)


@dataclass(frozen=True)
class FVConservationBound:
    interval_kg: tuple | None
    selected_labels: tuple
    summed_lower_mass_kg: float | None
    status: str
    explanation: str = 'CONSERVATIVE_DISJOINT_SUBSET; NOT_TIGHTEST_UNION_BOUND; NO_KINETIC_RESPONSE'


def conservation_bound(inventory_upper_kg, windows_and_bands):
    """Independent weighted interval scheduling; no FV response coefficients."""
    M = se._real(inventory_upper_kg, 'inventory upper kg', nonnegative=True)
    if not isinstance(windows_and_bands, (list, tuple)) or len(windows_and_bands) > MAX_OBSERVATIONS:
        raise ValueError('BOUNDED_CONSERVATION_INPUT_REQUIRED')
    items = []
    for label, window, band in windows_and_bands:
        _label(label)
        a, b = se._interval(window, 'conservation window', nonnegative=False)
        l, u = se._interval(band, 'conservation mass kg')
        if b <= a:
            raise ValueError('POSITIVE_DURATION_FRACTION_REQUIRED')
        items.append((b, a, label, l))
    items.sort()
    values, labels = [Fraction()], [()]
    for i, (end, start, label, lo) in enumerate(items):
        previous = max([0, *[j+1 for j in range(i) if items[j][0] <= start]])
        take = values[previous]+_q(lo)
        if take > values[-1]:
            values.append(take); labels.append((*labels[previous], label))
        else:
            values.append(values[-1]); labels.append(labels[-1])
    remainder = _q(M)-values[-1]
    try:
        upper, lower_sum = _rounded(remainder, 1), _rounded(values[-1], -1)
    except RuntimeError:
        upper = lower_sum = None
    contradiction = remainder < 0
    return FVConservationBound(None if upper is None else (0., upper), labels[-1], lower_sum,
        'CONSERVATION_CONTRADICTION' if contradiction else
        ('CONSERVATION_BOUND' if upper is not None else 'NUMERICALLY_UNRESOLVED'))


@dataclass(frozen=True, eq=False)
class FVConditionedWitness:
    raw_optimizer_masses_kg: np.ndarray
    raw_residuals: _Residuals | None
    state: sf.FVChemicalState | None = None
    masses_kg: np.ndarray | None = None
    final_residuals: _Residuals | None = None
    original_set_residuals: se.FVConstraintResiduals | None = None
    repair_method: str = 'NONE'
    repair_work: int = 0
    repair_optimization: _LPEvidence | None = None
    mass_change_kg: float | None = None
    prediction_interval_kg: tuple | None = None
    replay: object | None = None
    status: str = 'UNRESOLVED'
    termination: str = 'NOT_RECONSTRUCTED'

    def __post_init__(self):
        se._seal(self)


def _prediction(response, mass):
    nominal = _dotq(response.weights, mass)
    error = _dotq(response.coefficient_allowances, mass)
    return (_rounded(nominal-error, -1), _rounded(nominal+error, 1))


def _reconstruct(u, inner, mass, target):
    raw_res = _residuals(inner, mass)
    w = FVConditionedWitness(mass, raw_res)
    try:
        with np.errstate(all='ignore'):
            c = mass/u.capacities_m3
        if not np.isfinite(c).all() or np.any((mass != 0) & (c == 0)):
            raise RuntimeError('UNREPRESENTABLE_CONCENTRATION')
        # Exact endpoints reuse caller-supplied representable concentrations;
        # this is not a clamp or inventory repair. Every row is rechecked below.
        clo, chi = se._concentrations(u.lower), se._concentrations(u.upper)
        c = np.where(mass == u.lower_masses_kg, clo,
                     np.where(mass == u.upper_masses_kg, chi, c))
        n = len(c)//3
        state = sf.FVChemicalState.from_cell_averages(solute=u.lower.solute, grind=u.lower.grind,
            time_s=u.lower.time_s, edges_m=u.lower.edges_m, liquid_kg_m3=c[:n],
            fine_kg_m3=c[n:2*n], coarse_kg_m3=c[2*n:])
        m = se._concentrations(state)*u.capacities_m3
        final = _residuals(inner, m)
        original = se._residuals(u, m)
        change = _rounded(sum((abs(_q(x)-_q(y)) for x, y in zip(m, mass)), Fraction()), 1)
        w = replace(w, state=state, masses_kg=m, final_residuals=final,
                    original_set_residuals=original, mass_change_kg=change)
        if not final.feasible or not original.feasible or np.any(c < clo) or np.any(c > chi):
            raise RuntimeError('RECONSTRUCTED_STATE_VIOLATES_JOINT_CONSTRAINTS')
        return replace(w, prediction_interval_kg=_prediction(target, m),
                       status='CHECKED_REPLAY_REQUIRED', termination='COMPLETE')
    except Exception as exc:
        return replace(w, termination=str(exc) if isinstance(exc, RuntimeError)
                       else 'RECONSTRUCTION_EXCEPTION:'+type(exc).__name__)


def _candidate(u, inner, evidence, target, *, search=None):
    if evidence.raw_masses_kg is None:
        return None
    raw = evidence.raw_masses_kg
    w = _reconstruct(u, inner, raw, target)
    if w.status == 'CHECKED_REPLAY_REQUIRED':
        return w
    try:
        # A bounded concentration-box projection is only a candidate. Unlike
        # 005's laminar repair it performs NO phase/total rebalancing and must
        # pass every original U and actual inner observation row afterwards.
        # The more restrictive replay-reserve search rows are not feasibility
        # requirements: a tiny violation of a search margin is not a band violation.
        c = raw/u.capacities_m3
        projected = np.minimum(np.maximum(c, se._concentrations(u.lower)), se._concentrations(u.upper))
        projected_mass = projected*u.capacities_m3
        fixed = _reconstruct(u, inner, projected_mass, target)
        if fixed.masses_kg is not None:
            change = _rounded(sum((abs(_q(x)-_q(y)) for x, y in zip(fixed.masses_kg, raw)), Fraction()), 1)
            if (fixed.status == 'CHECKED_REPLAY_REQUIRED'
                    and _q(change) <= _product(64*target.settings.primal_tolerance, u.inventory_scale_kg)):
                return replace(fixed, raw_optimizer_masses_kg=raw, raw_residuals=w.raw_residuals,
                    repair_method='BOUNDED_BOX_PROJECTION_ALL_JOINT_ROWS_RECHECKED',
                    repair_work=int(np.count_nonzero(projected != c)), mass_change_kg=change)
        problem = _inward_repair_problem(inner if search is None else search, raw, target.settings)
        repair = _solve(problem, evidence.objective, target.settings)
        w = replace(w, repair_method='BOUNDED_ALL_ROW_INWARD_LP', repair_work=repair.calls,
                    repair_optimization=repair)
        if repair.status != 'CHECKED' or repair.raw_masses_kg is None:
            return replace(w, termination='ALL_ROW_REPAIR_UNRESOLVED')
        fixed = _reconstruct(u, inner, repair.raw_masses_kg, target)
        change = _rounded(sum((abs(_q(x)-_q(y)) for x, y in zip(
            fixed.masses_kg if fixed.masses_kg is not None else repair.raw_masses_kg, raw)), Fraction()), 1)
        fixed = replace(fixed, raw_optimizer_masses_kg=raw, raw_residuals=w.raw_residuals,
                        repair_method=w.repair_method, repair_work=repair.calls,
                        repair_optimization=repair, mass_change_kg=change)
        if _q(change) > _product(64*target.settings.primal_tolerance, u.inventory_scale_kg):
            return replace(fixed, status='UNRESOLVED', termination='REPAIR_MASS_CHANGE_LIMIT')
        return fixed
    except Exception as exc:
        return replace(w, termination='ALL_ROW_REPAIR:'+type(exc).__name__)


@dataclass(frozen=True)
class _CoreResult:
    outer: _Polytope
    inner: _Polytope
    search: _Polytope
    feasibility: _LPEvidence
    outer_optimizations: tuple
    inner_optimizations: tuple
    outer_interval_kg: tuple | None
    minimum_bracket_kg: tuple | None
    maximum_bracket_kg: tuple | None
    compatibility: str
    bounds: str
    termination: str


def _query_core(base, bands, g, a, epsilon_kg, settings=se.FVEnvelopeSettings(), *, search_bands=None):
    """Model-free numerical core: no response identity can be manufactured here."""
    outer = _intersect(base, bands, inner=False)
    inner = _intersect(base, bands, inner=True)
    search = inner if search_bands is None else _intersect(base, search_bands, inner=True)
    feasibility = _phase_one(outer, settings)
    fixed = np.array_equal(outer.lower, outer.upper)
    contradiction = ((fixed and feasibility.raw_residuals is not None and not feasibility.raw_residuals.feasible)
        or (not fixed and feasibility.status == 'CHECKED'
            and feasibility.checked_dual_lower_kg is not None and feasibility.checked_dual_lower_kg > 0))
    if contradiction:
        return _CoreResult(outer, inner, search, feasibility, (), (), None, None, None,
            'INCOMPATIBLE_UNDER_DECLARED_CONTRACT', 'NOT_APPLICABLE', 'CHECKED_OUTER_CONTRADICTION')
    low, high = _coefficient_bounds(g, a)
    out = tuple(_solve(outer, c, settings) for c in (low, -high))
    ins = tuple(_solve(search, c, settings) for c in (high, -low))
    fallback_low = sum((min(_product(c, l), _product(c, h)) for c, l, h in zip(low, base.lower, base.upper)), Fraction())
    fallback_high = sum((max(_product(c, l), _product(c, h)) for c, l, h in zip(high, base.lower, base.upper)), Fraction())
    lower = max(_rounded(fallback_low, -1), out[0].checked_dual_lower_kg) if out[0].status == 'CHECKED' else _rounded(fallback_low, -1)
    upper = min(_rounded(fallback_high, 1), -out[1].checked_dual_lower_kg) if out[1].status == 'CHECKED' else _rounded(fallback_high, 1)
    brackets = []
    for i, e in enumerate(ins):
        if e.raw_residuals is not None and e.raw_residuals.feasible:
            q = _dotq(high if i == 0 else low, e.raw_masses_kg)
            brackets.append((lower, _rounded(q, 1)) if i == 0 else (_rounded(q, -1), upper))
        else:
            brackets.append(None)
    compatible = any(v is not None for v in brackets)
    good = all(e.status == 'CHECKED' for e in out) and all(
        v is not None and 0 <= _q(v[1])-_q(v[0]) <= _q(epsilon_kg) for v in brackets)
    return _CoreResult(outer, inner, search, feasibility, out, ins, (lower, upper), *brackets,
        'ESTABLISHED' if compatible else 'UNRESOLVED', 'QUALIFIED' if good else 'NUMERICALLY_UNRESOLVED',
        'COMPLETE' if good else 'COMPATIBLE_EXTREMA_OR_RESOLUTION_UNRESOLVED')


@dataclass(frozen=True)
class FVConditionalExtremum:
    sense: str
    interval_kg: tuple | None
    gap_kg: float | None
    outer_optimization: _LPEvidence
    inner_optimization: _LPEvidence
    witness: FVConditionedWitness | None
    status: str = 'NUMERICALLY_UNRESOLVED'


@dataclass(frozen=True)
class _MappedBaseline:
    outer_delivery_interval_kg: tuple
    minimum: se.FVExtremum | None
    maximum: se.FVExtremum | None
    numerical_status: str = 'PULLED_BACK_ARITHMETIC_ONLY_NOT_REPLAYED'


def _baseline(u, response, epsilon):
    if isinstance(response, se.FVDeliveryResponse):
        return se.bound_delivery(u, response, epsilon_kg=epsilon)
    if response.status != 'RESPONSE_QUALIFIED' or u.feasibility != 'ESTABLISHED_NONEMPTY':
        return _MappedBaseline((0., u.inventory_scale_kg), None, None, 'NUMERICALLY_UNRESOLVED')
    ext = tuple(se._optimize(u, response.weights, response.coefficient_allowances, s, response.settings)
                for s in ('minimum', 'maximum'))
    low = ext[0].interval_kg[0] if ext[0].status == 'OPTIMIZATION_QUALIFIED' else 0.
    high = ext[1].interval_kg[1] if ext[1].status == 'OPTIMIZATION_QUALIFIED' else u.inventory_scale_kg
    return _MappedBaseline((max(0., low), min(u.inventory_scale_kg, high)), *ext)


def _json_value(v, arrays, timing):
    if isinstance(v, np.ndarray):
        return v.tolist() if arrays else dict(shape=list(v.shape), sha256=hashlib.sha256(v.tobytes()).hexdigest())
    if isinstance(v, sf.FVChemicalState) and not arrays:
        return dict(state_identity=v.identity_sha256, model_identity=v.model_identity,
                    solute=v.solute, grind=v.grind, cells=len(v.edges_m)-1,
                    time_s=v.time_s, inventory_kg=v.inventory_kg)
    if isinstance(v, sf.FVPlan) and not arrays:
        return dict(plan_identity=v.identity_sha256, span_s=v.t_span_s,
                    primary_steps=len(v.primary_steps), settings=sf._json(v.settings),
                    flow_history=sf._json(v.flow_history), temperature_history=sf._json(v.temperature_history))
    if is_dataclass(v):
        return {f.name: _json_value(getattr(v, f.name), arrays, timing) for f in fields(v)
                if timing or f.name != 'elapsed_wall_s'}
    if isinstance(v, (list, tuple)):
        return [_json_value(x, arrays, timing) for x in v]
    if isinstance(v, dict):
        return {k: _json_value(x, arrays, timing) for k, x in v.items()}
    if isinstance(v, np.generic):
        return v.item()
    return v


@dataclass(frozen=True)
class FVPrefixBounds:
    conditioned_set: FVPrefixConditionedSet
    target: se.FVDeliveryResponse | FVEqualChildPullback
    epsilon_kg: float
    unconditioned: object
    conservation: FVConservationBound
    core: _CoreResult | None = None
    witness_search_allowances: tuple = ()
    conditioned_outer_interval_kg: tuple | None = None
    minimum: FVConditionalExtremum | None = None
    maximum: FVConditionalExtremum | None = None
    compatibility: str = 'UNRESOLVED'
    bounds: str = 'NUMERICALLY_UNRESOLVED'
    termination: str = 'NOT_EVALUATED'
    baseline_width_kg: float | None = None
    conditioned_width_kg: float | None = None
    absolute_width_reduction_kg: float | None = None
    relative_width_reduction: float | None = None
    combined_endpoint_uncertainty_kg: float | None = None
    reduction_resolved: bool = False
    discretization: str = 'NOT_INCLUDED_IN_FIXED_OPERATOR_BOUNDS'
    allowance_contract: str = CONTRACT
    PHYSICAL_VALIDATION: str = 'NOT_ESTABLISHED'
    scope: str = 'RESEARCH_ONLY'

    @property
    def optimization_calls(self):
        base = (self.unconditioned.optimization_calls if isinstance(self.unconditioned, se.FVEnvelopeResult)
                else sum(e.optimization.calls for e in (self.unconditioned.minimum, self.unconditioned.maximum) if e is not None))
        if self.core is None:
            return base
        return base + sum(e.calls for e in (self.core.feasibility, *self.core.outer_optimizations,
            *self.core.inner_optimizations)) + sum(e.witness.repair_optimization.calls for e in (self.minimum, self.maximum)
                if e is not None and e.witness is not None and e.witness.repair_optimization is not None)

    @property
    def forward_calls(self):
        return sum(e is not None and e.witness is not None and e.witness.replay is not None
                   for e in (self.minimum, self.maximum))

    def to_json(self, *, include_arrays=False, include_timing=False):
        value = _json_value(self, include_arrays, include_timing)
        value.update(optimization_calls=self.optimization_calls, forward_calls=self.forward_calls)
        return json.dumps(value, indent=2, sort_keys=True, allow_nan=False)


def _widths(result):
    base = result.unconditioned.outer_delivery_interval_kg
    outer = result.conditioned_outer_interval_kg
    if base is None or outer is None:
        return result
    try:
        bw, cw = _q(base[1])-_q(base[0]), _q(outer[1])-_q(outer[0])
        delta = _rounded(bw-cw)
        ratio = None if bw == 0 else _rounded((bw-cw)/bw)
        gaps = [e.gap_kg for e in (result.minimum, result.maximum) if e is not None]
        bgaps = [e.gap_kg for e in (result.unconditioned.minimum, result.unconditioned.maximum) if e is not None]
        uncertainty = (_rounded(sum(map(_q, gaps+bgaps)), 1)
                       if len(gaps+bgaps) == 4 and all(g is not None for g in gaps+bgaps) else None)
        return replace(result, baseline_width_kg=_rounded(bw, 1), conditioned_width_kg=_rounded(cw, 1),
            absolute_width_reduction_kg=delta, relative_width_reduction=ratio,
            combined_endpoint_uncertainty_kg=uncertainty,
            reduction_resolved=result.bounds == 'QUALIFIED' and uncertainty is not None and delta > uncertainty)
    except RuntimeError:
        return replace(result, termination=result.termination+';WIDTH_ARITHMETIC_UNRESOLVED')


def bound_future_delivery(conditioned_set, target_response, *, epsilon_kg):
    """Bound one finite later fraction; no target observation/value is accepted.

    Empty native observations return the EXACT existing 005 result and require
    the existing replay path, with no duplicate propagation or wrapper optimizer.
    Nonempty queries require replay_conditioned_extrema before QUALIFIED.
    """
    if not isinstance(conditioned_set, FVPrefixConditionedSet):
        raise ValueError('PREFIX_CONDITIONED_SET_REQUIRED')
    conditioned_set.validate()
    u = conditioned_set.original
    target = _response(target_response, u)
    epsilon = se._real(epsilon_kg, 'epsilon kg', nonnegative=True)
    if epsilon <= 0:
        raise ValueError('POSITIVE_EPSILON_REQUIRED')
    if target.plan.identity_sha256 != conditioned_set.plan.identity_sha256:
        raise ValueError('TARGET_PLAN_MISMATCH')
    for obs in conditioned_set.observations:
        if obs.response.window_s[1] > target.window_s[0]:
            raise ValueError('CONDITIONING_MUST_END_BEFORE_TARGET')
        if type(obs.response) is not type(target):
            raise ValueError('MIXED_NATIVE_AND_PULLBACK_COORDINATES')
    if not conditioned_set.observations:
        if not isinstance(target, se.FVDeliveryResponse):
            raise ValueError('EMPTY_QUERY_REQUIRES_NATIVE_005_COORDINATES')
        return se.bound_delivery(u, target, epsilon_kg=epsilon)
    conservation = conservation_bound(u.inventory_scale_kg, tuple(
        (o.label, o.response.window_s, o.mass_interval_kg) for o in conditioned_set.observations))
    # Failed responses retain a labelled conservation/unconditioned fallback.
    baseline = _baseline(u, target, epsilon)
    result = FVPrefixBounds(conditioned_set, target, epsilon, baseline, conservation)
    if u.feasibility == 'EMPTY_FEASIBLE_SET':
        return replace(result, compatibility='INCOMPATIBLE_UNDER_DECLARED_CONTRACT', bounds='NOT_APPLICABLE',
                       termination='EXACT_ORIGINAL_LAMINAR_SET_CONTRADICTION')
    if any(r.status != 'RESPONSE_QUALIFIED' for r in (target, *(o.response for o in conditioned_set.observations))):
        return replace(result, conditioned_outer_interval_kg=(0., u.inventory_scale_kg),
                       termination='RESPONSE_FAILED;FALLBACK_DOES_NOT_CERTIFY_CONDITIONING')
    try:
        bands = tuple((o.label, o.response.weights, o.response.coefficient_allowances,
                       *o.mass_interval_kg) for o in conditioned_set.observations)
        search_bands = []
        search_allowances = []
        for obs, band in zip(conditioned_set.observations, bands):
            native = obs.response.native if isinstance(obs.response, FVEqualChildPullback) else obs.response
            # Reserve enough for both the response-to-forward discrepancy and
            # the entire forward interval, using the declared maximum action
            # count. This is a sufficient SEARCH restriction only, not outer U.
            reserve = 512*se.EPS*(1+native.plan.settings.max_exponential_applications+native.conditioning_sum)
            allowances = se._readonly([_rounded(_q(a)+_q(reserve), 1) for a in band[2]])
            search_allowances.append(allowances)
            search_bands.append((band[0], band[1], allowances, band[3], band[4]))
        result = replace(result, witness_search_allowances=tuple(search_allowances))
        core = _query_core(_base_polytope(u), bands, target.weights, target.coefficient_allowances,
                           epsilon, target.settings, search_bands=search_bands)
        result = replace(result, core=core, compatibility=core.compatibility if core.bounds == 'NOT_APPLICABLE'
                         else 'UNRESOLVED', bounds='NOT_APPLICABLE' if core.bounds == 'NOT_APPLICABLE'
                         else 'NUMERICALLY_UNRESOLVED', termination=core.termination)
        if core.outer_interval_kg is None:
            return result
        original = baseline.outer_delivery_interval_kg or (0., u.inventory_scale_kg)
        outer = (max(0., original[0], core.outer_interval_kg[0]),
                 min(u.inventory_scale_kg, original[1], core.outer_interval_kg[1]))
        if outer[0] > outer[1]:
            return replace(result, termination='NUMERICAL_OUTER_ORDER_UNRESOLVED')
        extrema = []
        for i, sense in enumerate(('minimum', 'maximum')):
            witness = _candidate(u, core.inner, core.inner_optimizations[i], target, search=core.search)
            bracket = None
            if witness is not None and witness.status == 'CHECKED_REPLAY_REQUIRED':
                bracket = ((outer[0], witness.prediction_interval_kg[1]) if i == 0 else
                           (witness.prediction_interval_kg[0], outer[1]))
            extrema.append(FVConditionalExtremum(sense, bracket,
                None if bracket is None else _rounded(_q(bracket[1])-_q(bracket[0]), 1),
                core.outer_optimizations[i], core.inner_optimizations[i], witness))
        return _widths(replace(result, conditioned_outer_interval_kg=outer,
            minimum=extrema[0], maximum=extrema[1], termination='CONDITIONED_WITNESS_REPLAYS_REQUIRED'))
    except Exception as exc:
        return replace(result, conditioned_outer_interval_kg=(0., u.inventory_scale_kg),
                       termination=str(exc) if isinstance(exc, RuntimeError) else 'CONDITIONING_EXCEPTION:'+type(exc).__name__)


@dataclass(frozen=True)
class FVWindowReplay:
    response_identity: str
    window_s: tuple
    observation_label: str | None
    band_kg: tuple | None
    prediction_kg: float
    response_allowance_kg: float
    forward_delivery_kg: float | None
    forward_allowance_kg: float
    discrepancy_kg: float | None
    replay_interval_kg: tuple | None
    combined_interval_kg: tuple | None
    contained: bool
    status: str


@dataclass(frozen=True)
class FVConditionedReplay:
    state_identity: str
    replay_state_identity: str | None
    plan_identity: str
    windows: tuple
    status: str
    termination: str
    exponential_applications: int | None
    forward_status: str
    elapsed_wall_s: float
    parent_accuracy: str = 'NOT_ASSESSED'


def _replay(result, witness):
    start = time.monotonic()
    u, target, conditioned = result.conditioned_set.original, result.target, result.conditioned_set
    receipt = FVConditionedReplay(witness.state.identity_sha256, None, target.plan.identity_sha256,
        (), 'UNRESOLVED', 'NOT_REPLAYED', None, 'NOT_CALLED', 0.)
    try:
        witness.state.validate()
        m = se._concentrations(witness.state)*u.capacities_m3
        if (witness.state.model_identity != u.lower.model_identity or witness.state.time_s != u.lower.time_s
                or not np.array_equal(m, witness.masses_kg)
                or not _residuals(_base_polytope(u), m).feasible
                or not se._residuals(u, m).feasible
                or not _residuals(result.core.inner, m).feasible):
            raise RuntimeError('WITNESS_CHANGED_OR_OUTSIDE_JOINT_SET')
        state = _lift_state(witness.state) if isinstance(target, FVEqualChildPullback) else witness.state
        responses = tuple(o.response for o in conditioned.observations)+(target,)
        windows = tuple(r.window_s for r in responses)
        receipt = replace(receipt, replay_state_identity=state.identity_sha256, forward_status='ATTEMPTED')
        forward = sf.simulate_stateful_fv(plan=target.plan, initial_state=state,
            observation_times_s=tuple(sorted({v for w in windows for v in w})), fraction_windows_s=windows)
        receipt = replace(receipt, exponential_applications=forward.exponential_applications,
                          forward_status=forward.status, parent_accuracy=forward.accuracy_status)
        rows = []
        for i, (response, fraction) in enumerate(zip(responses, forward.fractions)):
            native = response.native if isinstance(response, FVEqualChildPullback) else response
            nominal, err = _dotq(response.weights, m), _dotq(response.coefficient_allowances, m)
            # Exact binary-rational accumulation has zero summation rounding;
            # directed interval conversion and representable state rechecks are explicit.
            allowance = _product(256*se.EPS*(1+forward.exponential_applications+native.conditioning_sum),
                                 _rounded(sum(map(_q, m)), 1))
            value = fraction.solute_kg
            replay_interval = combined = None
            discrepancy = None
            good = (forward.status == 'COMPLETE' and forward.integration_complete
                    and all(s == 'SUPPORTED' for s in forward.observation_status)
                    and value is not None and fraction.status in
                    ('VALID_NUMERICAL_ZERO', 'NUMERICAL_ONLY_ACCURACY_NOT_ASSESSED'))
            if value is not None:
                discrepancy = _rounded(_q(value)-nominal)
                good = good and abs(_q(value)-nominal) <= err+allowance
                replay_interval = (_rounded(_q(value)-allowance, -1), _rounded(_q(value)+allowance, 1))
                combined = (_rounded(min(nominal-err, _q(value)-allowance), -1),
                            _rounded(max(nominal+err, _q(value)+allowance), 1))
            obs = conditioned.observations[i] if i < len(conditioned.observations) else None
            contained = (combined is not None and (obs is None or
                (obs.mass_interval_kg[0] <= combined[0] and combined[1] <= obs.mass_interval_kg[1])))
            rows.append(FVWindowReplay(response.identity_sha256, response.window_s,
                None if obs is None else obs.label, None if obs is None else obs.mass_interval_kg,
                _rounded(nominal), _rounded(err, 1), value, _rounded(allowance, 1), discrepancy,
                replay_interval, combined, contained, 'CHECKED' if good and contained else 'UNRESOLVED'))
        good = len(rows) == len(responses) and all(r.status == 'CHECKED' for r in rows)
        receipt = replace(receipt, windows=tuple(rows), status='CHECKED' if good else 'UNRESOLVED',
                          termination='COMPLETE' if good else 'REPLAY_SUPPORT_DISCREPANCY_OR_CONTAINMENT_FAILED')
    except Exception as exc:
        receipt = replace(receipt, termination=str(exc) if isinstance(exc, RuntimeError)
                          else 'REPLAY_EXCEPTION:'+type(exc).__name__)
    return replace(receipt, elapsed_wall_s=time.monotonic()-start)


def replay_conditioned_extrema(result):
    """Two fresh batched unchanged forward trajectories; empty queries use 005."""
    if isinstance(result, se.FVEnvelopeResult):
        return se.replay_extrema(result)
    if not isinstance(result, FVPrefixBounds):
        raise ValueError('PREFIX_BOUNDS_REQUIRED')
    result.conditioned_set.validate(); result.target.validate(result.conditioned_set.original)
    if result.bounds == 'NOT_APPLICABLE' or result.minimum is None or result.maximum is None:
        return result
    extrema = []
    for e in (result.minimum, result.maximum):
        witness = e.witness
        if witness is None or witness.status != 'CHECKED_REPLAY_REQUIRED':
            extrema.append(e); continue
        if witness.replay is not None:
            raise ValueError('WITNESS_ALREADY_REPLAYED')
        replay = _replay(result, witness)
        witness = replace(witness, replay=replay, status='COMPATIBLE' if replay.status == 'CHECKED' else 'UNRESOLVED')
        bracket = None
        if replay.status == 'CHECKED':
            lo, hi = replay.windows[-1].combined_interval_kg
            outer = result.conditioned_outer_interval_kg
            bracket = (outer[0], hi) if e.sense == 'minimum' else (lo, outer[1])
        gap = None if bracket is None else _rounded(_q(bracket[1])-_q(bracket[0]), 1)
        good = (gap is not None and 0 <= gap <= result.epsilon_kg and e.outer_optimization.status == 'CHECKED')
        extrema.append(replace(e, witness=witness, interval_kg=bracket, gap_kg=gap,
                               status='QUALIFIED' if good else 'NUMERICALLY_UNRESOLVED'))
    compatible = any(e.witness is not None and e.witness.status == 'COMPATIBLE' for e in extrema)
    good = all(e.status == 'QUALIFIED' for e in extrema)
    return _widths(replace(result, minimum=extrema[0], maximum=extrema[1],
        compatibility='ESTABLISHED' if compatible else 'UNRESOLVED',
        bounds='QUALIFIED' if good else 'NUMERICALLY_UNRESOLVED',
        termination='COMPLETE' if good else 'CONDITIONED_EXTREMA_OR_REPLAY_UNRESOLVED'))
