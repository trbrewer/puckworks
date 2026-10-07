"""007: joint common-past B_MINUS_A queries over unchanged FV operators.

G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Engineering allowances, not statistical,
continuum or physical certificates. Pannusch DOI 10.1016/j.jfoodeng.2023.111887;
source-derived output CC-BY-NC-3.0 (10.17632/y2tz67f6ry.1), separately from code.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np

from . import prefix_conditioned as pc, state_envelope as se, stateful_fv as sf

ORIENTATION = 'B_MINUS_A'


def _source():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _native(response):
    return response.native if isinstance(response, pc.FVEqualChildPullback) else response


def _history_prefix(history, initial, branch):
    """Original panel representation, including affine defining endpoints.

    Never sample/recompile a shortened plan. Panels starting AT branch are
    excluded; the left limiting value belongs to the preceding panel. Keeping
    original affine endpoints also detects interpolation leakage from the future.
    """
    values = history.flows_m3_s if isinstance(history, sf.FlowHistory) else history.temperatures_K
    panels = tuple((a, b, values[i], values[i+1] if history.kind == 'linear' else values[i])
                   for i, (a, b) in enumerate(zip(history.times_s, history.times_s[1:]))
                   if a < branch and b > initial)
    return (history.kind, getattr(history, 'units', 'K'), 'LEFT_CLOSED_RIGHT_OPEN', panels)


@dataclass(frozen=True)
class FVCommonPastReceipt:
    plan_a_identity: str
    plan_b_identity: str
    response_a_identity: str
    response_b_identity: str
    original_set_identity: str
    observation_identities: tuple
    model_identity: str
    native_model_identity: str
    source_identities: tuple
    initial_time_s: float
    branch_time_s: float
    target_window_s: tuple
    prefix_steps: int
    prescribed_prefix_identity: str
    compiled_prefix_identity: str
    fv_settings: sf.FVSettings
    numerical_settings: se.FVEnvelopeSettings
    mapping: str
    comparison_basis: str
    epsilon_kg: float
    delta_kg: float
    target_volumes_m3: tuple
    post_branch_volumes_m3: tuple
    target_volume_difference_m3: float
    volume_rounding_allowance_m3: float
    original_assumption: str
    exact_zero: bool
    orientation: str = ORIENTATION
    algorithm_source_sha256: str = field(default_factory=_source)
    identity_sha256: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'identity_sha256', sf._hash(self))


@dataclass(frozen=True)
class _MappedEmptySet:
    """Explicit 007-only empty fine-to-coarse query; never a fake 006 set."""
    original: se.FVChemicalStateSet
    plan: sf.FVPlan
    observations: tuple = ()

    def validate(self):
        self.original.validate(); self.plan.validate()
        if self.observations:
            raise ValueError('MAPPED_EMPTY_PATH_ONLY')


def _validate(conditioned, a, b, branch_time_s, epsilon_kg, delta_kg, comparison_basis):
    # Scalar/type checks precede validation/hash traversal and numerical allocation.
    branch = se._real(branch_time_s, 'branch seconds')
    epsilon = se._real(epsilon_kg, 'epsilon kg', nonnegative=True)
    margin = se._real(delta_kg, 'delta kg', nonnegative=True)
    if epsilon <= 0:
        raise ValueError('POSITIVE_EPSILON_REQUIRED')
    if comparison_basis not in ('MATCHED_COLLECTED_VOLUME', 'EXPLICIT_UNEQUAL_VOLUME'):
        raise ValueError('EXPLICIT_COMPARISON_BASIS_REQUIRED')
    if not isinstance(conditioned, (pc.FVPrefixConditionedSet, _MappedEmptySet)):
        raise ValueError('PREFIX_CONDITIONED_SET_REQUIRED')
    if not isinstance(conditioned.observations, tuple) or len(conditioned.observations) > pc.MAX_OBSERVATIONS:
        raise ValueError('BOUNDED_OBSERVATION_TUPLE_REQUIRED')
    conditioned.validate()
    u = conditioned.original
    a, b = pc._response(a, u), pc._response(b, u)
    if type(a) is not type(b):
        raise ValueError('MIXED_NATIVE_AND_PULLBACK_COORDINATES')
    if isinstance(conditioned, _MappedEmptySet) and not isinstance(a, pc.FVEqualChildPullback):
        raise ValueError('EXPLICIT_PULLBACK_RESPONSES_REQUIRED')
    pa, pb = a.plan, b.plan
    if pa.identity_sha256 != conditioned.plan.identity_sha256:
        raise ValueError('CONDITIONING_PLAN_A_MISMATCH')
    if (a.model.model_identity != b.model.model_identity
            or _native(a).model.model_identity != _native(b).model.model_identity):
        raise ValueError('INCOMPATIBLE_MODEL_OR_MAPPING')
    if pa.settings != pb.settings or a.settings != b.settings:
        raise ValueError('INCOMPATIBLE_NUMERICAL_SETTINGS')
    if pa.t_span_s != pb.t_span_s or u.lower.time_s != pa.t_span_s[0]:
        raise ValueError('INCOMPATIBLE_COMPLETE_SPAN_OR_INITIAL_CLOCK')
    initial, end = pa.t_span_s
    if not initial < branch < end:
        raise ValueError('BRANCH_STRICTLY_INSIDE_COMPLETE_SPAN_REQUIRED')
    if not all(np.any(p.primary_times_s == branch) for p in (pa, pb)):
        raise ValueError('OFF_GRID_BRANCH_NOT_AN_ORIGINAL_PRIMARY_BOUNDARY')
    if a.window_s != b.window_s:
        raise ValueError('TARGET_WINDOW_MISMATCH')
    if not branch <= a.window_s[0] < a.window_s[1] <= end:
        raise ValueError('INVALID_TARGET_WINDOW_SUPPORT')
    for obs in conditioned.observations:
        obs.validate(u, pa)
        if type(obs.response) is not type(a):
            raise ValueError('MIXED_NATIVE_AND_PULLBACK_COORDINATES')
        if obs.response.settings != a.settings:
            raise ValueError('INCOMPATIBLE_OBSERVATION_NUMERICAL_SETTINGS')
        if obs.response.window_s[1] > branch:
            raise ValueError('OBSERVATION_EXTENDS_BEYOND_BRANCH')
    signatures = []
    for name in ('flow_history', 'temperature_history'):
        x, y = (_history_prefix(getattr(p, name), initial, branch) for p in (pa, pb))
        if x != y:
            if x[:3] != y[:3] or tuple(v[:2] for v in x[3]) != tuple(v[:2] for v in y[3]):
                reason = 'DIFFERENT_HISTORY_REPRESENTATION_OR_PARTITION'
            elif x[0] == 'linear' and any(v[1] > branch for v in x[3]):
                reason = 'FUTURE_KNOT_INTERPOLATION_LEAKAGE'
            else:
                reason = 'CHANGED_PRESCRIBED_PAST'
            raise ValueError(reason+':'+name)
        signatures.append(x)
    xa = pa.primary_steps[pa.primary_steps[:, 1] <= branch]
    xb = pb.primary_steps[pb.primary_steps[:, 1] <= branch]
    if not np.array_equal(xa[:, :2], xb[:, :2]):
        raise ValueError('DIFFERENT_ORIGINAL_PRIMARY_PARTITION')
    if not np.array_equal(xa, xb):
        raise ValueError('DIFFERENT_ORIGINAL_COMPILED_PAST')
    # Model identity binds phase bases, mesh, geometry, source/configuration and
    # generator algorithm. Settings and actual frozen T/Q bind each operator.
    volumes = tuple(p.flow_history.integral(*a.window_s) for p in (pa, pb))
    post = tuple(p.flow_history.integral(branch, end) for p in (pa, pb))
    allowance = pc._rounded(pc._q(64*se.EPS)*pc._q(max(volumes)), 1)
    diff = pc._q(volumes[1])-pc._q(volumes[0])
    if comparison_basis == 'MATCHED_COLLECTED_VOLUME' and abs(diff) > pc._q(allowance):
        raise ValueError('PRESCRIBED_TARGET_COLLECTION_VOLUMES_DO_NOT_MATCH')
    mapping = a.mapping if isinstance(a, pc.FVEqualChildPullback) else 'NATIVE_ORIGINAL_MASS_COORDINATES'
    receipt = FVCommonPastReceipt(pa.identity_sha256, pb.identity_sha256,
        a.identity_sha256, b.identity_sha256, u.identity_sha256,
        tuple(o.identity_sha256 for o in conditioned.observations), a.model.model_identity,
        _native(a).model.model_identity, a.model.source_identities, initial, branch, a.window_s,
        len(xa), sf._hash(signatures), sf._hash((xa, a.model.model_identity, pa.settings)),
        pa.settings, a.settings, mapping, comparison_basis, epsilon, margin, volumes, post,
        pc._rounded(diff), allowance, u.assumption_label,
        pa.identity_sha256 == pb.identity_sha256)
    return receipt, epsilon, margin


def _signed_coefficients(ga, aa, gb, ab):
    """Model-free seam: signed difference plus BOTH errors and exact conversion."""
    if np.ndim(ga) != 1 or not 1 <= len(ga) <= 6000:
        raise ValueError('SIGNED_COEFFICIENT_ALLOCATION_LIMIT')
    ga, aa, gb, ab = (pc._array(x, np.shape(ga), 'signed coefficient') for x in (ga, aa, gb, ab))
    if np.any(aa < 0) or np.any(ab < 0):
        raise ValueError('NEGATIVE_RESPONSE_ALLOWANCE')
    d, allowances, conversion = [], [], []
    for x, ax, y, ay in zip(ga, aa, gb, ab):
        exact = pc._q(y)-pc._q(x)
        value = pc._rounded(exact)
        rounding = abs(pc._q(value)-exact)
        d.append(value); conversion.append(pc._rounded(rounding, 1))
        allowances.append(pc._rounded(pc._q(ax)+pc._q(ay)+rounding, 1))
    return tuple(se._readonly(x) for x in (d, allowances, conversion))


@dataclass(frozen=True, eq=False)
class FVSignedContrast:
    """A signed objective, deliberately NOT an FVDeliveryResponse."""
    response_a: object
    response_b: object
    receipt: FVCommonPastReceipt
    weights: np.ndarray | None = field(init=False)
    coefficient_allowances: np.ndarray | None = field(init=False)
    subtraction_allowances: np.ndarray | None = field(init=False)
    identity_sha256: str = field(init=False)

    def __post_init__(self):
        a, b = self.response_a, self.response_b
        values = (None, None, None)
        if all(r.weights is not None and r.coefficient_allowances is not None for r in (a, b)):
            values = _signed_coefficients(a.weights, a.coefficient_allowances, b.weights, b.coefficient_allowances)
            if self.receipt.exact_zero:
                values = tuple(np.zeros_like(a.weights) for _ in range(3))
        for k, v in zip(('weights', 'coefficient_allowances', 'subtraction_allowances'), values):
            object.__setattr__(self, k, v)
        se._seal(self)
        object.__setattr__(self, 'identity_sha256', sf._hash((self.receipt.identity_sha256, *values)))

    @property
    def settings(self):
        return self.response_a.settings


@dataclass(frozen=True)
class FVPairedReplay:
    state_identity: str
    replay_state_identity: str | None
    receipt_identity: str
    branch_a: object | None = None
    branch_b: object | None = None
    legacy_receipts_b_a: tuple = ()
    prefix_trace_identities: tuple = ()
    branch_state_identities: tuple = ()
    prefix_deliveries_kg: tuple = ()
    prefix_volumes_m3: tuple = ()
    maximum_prefix_mass_discrepancy_kg: float | None = None
    prefix_bitwise_equal: bool = False
    signed_prediction_interval_kg: tuple | None = None
    signed_forward_interval_kg: tuple | None = None
    combined_interval_kg: tuple | None = None
    forward_difference_kg: float | None = None
    subtraction_rounding_kg: float | None = None
    forward_calls: int = 0
    status: str = 'UNRESOLVED'
    termination: str = 'NOT_REPLAYED'


def _repair_calls(witness):
    if witness is None:
        return 0
    own = 0 if witness.repair_optimization is None else witness.repair_optimization.calls
    return own+_repair_calls(getattr(witness, 'previous_attempt', None))


@dataclass(frozen=True)
class FVCommonPastBounds:
    conditioned_set: object
    objective: FVSignedContrast
    epsilon_kg: float
    delta_kg: float
    core: object | None = None
    legacy_b_a: object | None = None
    outer_interval_kg: tuple | None = None
    minimum: pc.FVConditionalExtremum | None = None
    maximum: pc.FVConditionalExtremum | None = None
    compatibility: str = 'UNRESOLVED'
    bounds: str = 'NUMERICALLY_UNRESOLVED'
    decision: str = 'NUMERICALLY_UNRESOLVED'
    termination: str = 'NOT_EVALUATED'
    fallback: str | None = None
    opposite_sign_witnesses: bool = False
    material_reversal_witnesses: bool = False
    orientation: str = ORIENTATION
    legacy_label_mapping: tuple = (('legacy_A', 'public_B'), ('legacy_B', 'public_A'))
    allowance_contract: str = pc.CONTRACT
    PHYSICAL_VALIDATION: str = 'NOT_ESTABLISHED'
    scope: str = 'RESEARCH_ONLY'

    @property
    def receipt(self):
        return self.objective.receipt

    @property
    def optimization_calls(self):
        if self.legacy_b_a is not None:
            return self.legacy_b_a.optimization_calls + sum(_repair_calls(e.witness)
                for e in (self.minimum, self.maximum) if e is not None)
        if self.core is None:
            return 0
        return sum(e.calls for e in (self.core.feasibility, *self.core.outer_optimizations,
            *self.core.inner_optimizations)) + sum(_repair_calls(e.witness)
            for e in (self.minimum, self.maximum) if e is not None)

    @property
    def forward_calls(self):
        return sum(e.witness.replay.forward_calls for e in (self.minimum, self.maximum)
                   if e is not None and e.witness is not None and e.witness.replay is not None)

    def to_json(self, *, include_arrays=False, include_timing=False):
        value = pc._json_value(self, include_arrays, include_timing)
        value.update(optimization_calls=self.optimization_calls, forward_calls=self.forward_calls)
        return json.dumps(value, sort_keys=True, indent=2, allow_nan=False)


def _bands(conditioned):
    bands, search = [], []
    for obs in conditioned.observations:
        r, native = obs.response, _native(obs.response)
        row = (obs.label, r.weights, r.coefficient_allowances, *obs.mass_interval_kg)
        bands.append(row)
        reserve = 512*se.EPS*(1+native.plan.settings.max_exponential_applications+native.conditioning_sum)
        allowance = se._readonly([pc._rounded(pc._q(x)+pc._q(reserve), 1) for x in r.coefficient_allowances])
        search.append((obs.label, r.weights, allowance, *obs.mass_interval_kg))
    return tuple(bands), tuple(search)


def bound_common_past_contrast(conditioned_set, response_a, response_b, *, branch_time_s,
                               epsilon_kg, delta_kg, comparison_basis):
    """Bound B-A on one original U intersected with every supplied early band.

    This operation performs structural common-past validation itself. Call
    replay_common_past_extrema for compatible witness and complete-gap evidence.
    Empty native queries retain reversed 005 optimization and qualification.
    """
    if not isinstance(conditioned_set, pc.FVPrefixConditionedSet):
        raise ValueError('PREFIX_CONDITIONED_SET_REQUIRED')
    return _bound(conditioned_set, response_a, response_b, branch_time_s=branch_time_s,
                  epsilon_kg=epsilon_kg, delta_kg=delta_kg, comparison_basis=comparison_basis)


def bound_mapped_common_past_contrast(state_set, response_a, response_b, *, observations=(),
                                      branch_time_s, epsilon_kg, delta_kg, comparison_basis):
    """Explicit equal-child numerical-core path, including empty mapped queries.

    Does not relax 006's empty-pullback guard or manufacture native responses.
    """
    if not all(isinstance(r, pc.FVEqualChildPullback) for r in (response_a, response_b)):
        raise ValueError('EXPLICIT_PULLBACK_RESPONSES_REQUIRED')
    if not isinstance(observations, (tuple, list)) or len(observations) > pc.MAX_OBSERVATIONS:
        raise ValueError('BOUNDED_OBSERVATION_LIST_REQUIRED')
    if not isinstance(state_set, se.FVChemicalStateSet):
        raise ValueError('ORIGINAL_STATE_SET_REQUIRED')
    conditioned = (pc.condition_on_fractions(state_set, response_a.plan, observations)
                   if observations else _MappedEmptySet(state_set, response_a.plan))
    return _bound(conditioned, response_a, response_b, branch_time_s=branch_time_s,
                  epsilon_kg=epsilon_kg, delta_kg=delta_kg, comparison_basis=comparison_basis)


@dataclass(frozen=True, eq=False)
class FVContrastWitness(pc.FVConditionedWitness):
    """007 adapter provenance; raw evidence always remains the optimizer vector."""
    legacy_witness: object | None = None
    previous_attempt: object | None = None
    proposal_coordinates: str | None = None


def _existing_state(u, inner, state, raw, target, *, legacy=None):
    """Check actual stored concentrations without a mass/concentration round trip."""
    w = FVContrastWitness(raw, pc._residuals(inner, raw), state=state, legacy_witness=legacy)
    try:
        state.validate()
        c = se._concentrations(state)
        m = c*u.capacities_m3
        final, original = pc._residuals(inner, m), se._residuals(u, m)
        change = pc._rounded(sum(abs(pc._q(x)-pc._q(y)) for x, y in zip(m, raw)), 1)
        w = replace(w, masses_kg=m, final_residuals=final, original_set_residuals=original,
                    mass_change_kg=change, repair_method='EXISTING_REPRESENTABLE_STATE_RECHECKED')
        if (state.model_identity != u.lower.model_identity or state.time_s != u.lower.time_s
                or not final.feasible or not original.feasible
                or np.any(c < se._concentrations(u.lower)) or np.any(c > se._concentrations(u.upper))):
            raise RuntimeError('EXISTING_STATE_FAILS_007_JOINT_CHECK')
        if pc._q(change) > pc._product(64*target.settings.primal_tolerance, u.inventory_scale_kg):
            raise RuntimeError('REPAIR_MASS_CHANGE_LIMIT')
        return replace(w, prediction_interval_kg=pc._prediction(target, m),
                       status='CHECKED_REPLAY_REQUIRED', termination='COMPLETE')
    except Exception as exc:
        return replace(w, termination=str(exc) if isinstance(exc, RuntimeError)
                       else 'EXISTING_STATE_EXCEPTION:'+type(exc).__name__)


def _local_proposal_problem(u, poly, raw, settings):
    """Translated, scaled ALL-row search in a bounded concentration box.

    The auxiliary slack is maximized, never imposed as a feasibility condition.
    Exact opposite equalities get zero slack; dependent rows can force slack to
    zero. This is a proposal only. Acceptance uses unchanged original kg rows.
    """
    n = len(raw)
    radius = pc._product(64*settings.primal_tolerance, u.inventory_scale_kg)/(2*n)
    clo, chi = se._concentrations(u.lower), se._concentrations(u.upper)
    lower, upper = [], []
    for r, cap, l, h, ml, mh in zip(raw, u.capacities_m3, clo, chi, poly.lower, poly.upper):
        lower.append(max(l, pc._rounded(max(pc._q(ml), pc._q(r)-radius)/pc._q(cap), 1)))
        upper.append(min(h, pc._rounded(min(pc._q(mh), pc._q(r)+radius)/pc._q(cap), -1)))
    lower, upper = np.array(lower), np.array(upper)
    if np.any(lower > upper):
        raise RuntimeError('REPAIR_MASS_CHANGE_LIMIT')
    ml, mh = lower*u.capacities_m3, upper*u.capacities_m3
    rows, rhs = [], []
    margin = pc._product(1024*se.EPS, u.inventory_scale_kg)
    for i, (a, b) in enumerate(zip(poly.A, poly.b)):
        variation = [pc._q(x)*(pc._q(h)-pc._q(l)) for x, l, h in zip(a, ml, mh)]
        scale = sum(abs(x) for x in variation)
        remaining = pc._q(b)-pc._dotq(a, ml)
        if scale == 0:
            if remaining < 0:
                raise RuntimeError('LOCAL_FIXED_ROW_INFEASIBLE')
            rows.append([0.]*(n+1)); rhs.append(0.)
            continue
        equality = any(np.array_equal(a, -other) and b == -poly.b[j]
                       for j, other in enumerate(poly.A) if j != i)
        slack = 0. if equality else pc._rounded(min(margin, scale)/scale)
        rows.append([*(pc._rounded(x/scale) for x in variation), slack])
        rhs.append(pc._rounded(remaining/scale))
    problem = pc._Polytope(np.zeros(n+1), np.ones(n+1), np.array(rows).reshape(-1, n+1),
                          np.array(rhs), 1., poly.row_labels)
    return problem, lower, upper


def _joint_proposal(u, inner, evidence, target, *, previous, search=None):
    """One bounded LP proposal; no repeated tightening or acceptance tolerance."""
    raw = evidence.raw_masses_kg
    if raw is None:
        return previous
    try:
        problem, lo, hi = _local_proposal_problem(u, inner if search is None else search, raw, target.settings)
        objective = np.zeros(len(raw)+1); objective[-1] = -1.
        repair = pc._solve(problem, objective, target.settings)
        w = FVContrastWitness(raw, pc._residuals(inner, raw), previous_attempt=previous,
            repair_method='BOUNDED_LOCAL_ALL_ROW_CONCENTRATION_PROPOSAL', repair_work=repair.calls,
            repair_optimization=repair, proposal_coordinates='DIMENSIONLESS_LOCAL_CONCENTRATIONS_AND_OPTIONAL_SLACK')
        if repair.status != 'CHECKED' or repair.raw_masses_kg is None:
            return replace(w, termination='LOCAL_ALL_ROW_PROPOSAL_UNRESOLVED')
        z = repair.raw_masses_kg[:-1]
        c = lo+(hi-lo)*z
        n = len(c)//3
        state = sf.FVChemicalState.from_cell_averages(solute=u.lower.solute, grind=u.lower.grind,
            time_s=u.lower.time_s, edges_m=u.lower.edges_m,
            liquid_kg_m3=c[:n], fine_kg_m3=c[n:2*n], coarse_kg_m3=c[2*n:])
        checked = _existing_state(u, inner, state, raw, target)
        return replace(checked, previous_attempt=previous, repair_method=w.repair_method,
            repair_work=repair.calls, repair_optimization=repair, proposal_coordinates=w.proposal_coordinates)
    except Exception as exc:
        return FVContrastWitness(raw, pc._residuals(inner, raw), previous_attempt=previous,
            repair_method='BOUNDED_LOCAL_ALL_ROW_CONCENTRATION_PROPOSAL',
            termination=str(exc) if isinstance(exc, RuntimeError) else 'LOCAL_PROPOSAL_EXCEPTION:'+type(exc).__name__)


def _candidate(u, inner, evidence, target, *, search=None, legacy=None):
    if legacy is not None:
        first = _existing_state(u, inner, legacy.state, legacy.optimizer_masses_kg, target, legacy=legacy)
        if first.status == 'CHECKED_REPLAY_REQUIRED':
            return first
    else:
        first = pc._candidate(u, inner, evidence, target, search=search)
        if first is None or first.status == 'CHECKED_REPLAY_REQUIRED':
            return first
    return _joint_proposal(u, inner, evidence, target, previous=first, search=search)


def _bound(conditioned, a, b, **kwargs):
    receipt, epsilon, margin = _validate(conditioned, a, b, **kwargs)
    objective = FVSignedContrast(a, b, receipt)
    result = FVCommonPastBounds(conditioned, objective, epsilon, margin)
    u = conditioned.original
    legacy = None
    if not conditioned.observations and isinstance(a, se.FVDeliveryResponse):
        legacy = se.contrast_deliveries(u, b, a, epsilon_kg=epsilon, delta_kg=margin,
                                       comparison_basis=receipt.comparison_basis)
        result = replace(result, legacy_b_a=legacy)
    if u.feasibility == 'EMPTY_FEASIBLE_SET':
        return replace(result, compatibility='INCOMPATIBLE_UNDER_DECLARED_CONTRACT', bounds='NOT_APPLICABLE',
                       decision='INCOMPATIBLE', termination='EXACT_ORIGINAL_SET_CONTRADICTION')
    if any(r.status != 'RESPONSE_QUALIFIED' for r in (a, b, *(o.response for o in conditioned.observations))):
        return replace(result, outer_interval_kg=(-u.inventory_scale_kg, u.inventory_scale_kg),
            fallback='SIGNED_INVENTORY_ONLY', termination='RESPONSE_FAILED;CONDITIONING_NOT_CERTIFIED')
    try:
        if not conditioned.observations and isinstance(a, se.FVDeliveryResponse):
            # 005 A-B with positional labels (B,A) is exactly public B_MINUS_A.
            inventory_fallback = any(e is None or e.status != 'OPTIMIZATION_QUALIFIED'
                                     for e in (legacy.minimum, legacy.maximum))
            result = replace(result, legacy_b_a=legacy, outer_interval_kg=legacy.outer_delivery_interval_kg,
                             fallback='LEGACY_SIGNED_INVENTORY_ENDPOINT_FALLBACK'
                             if inventory_fallback and not receipt.exact_zero else None,
                             termination='LEGACY_B_A:'+legacy.termination)
            if legacy.minimum is None or legacy.maximum is None:
                return result
            outer = (0., 0.) if receipt.exact_zero else legacy.outer_delivery_interval_kg
            extrema = []
            for e in (legacy.minimum, legacy.maximum):
                w = None
                if e.witness is not None and e.witness.state is not None and e.witness.status == 'FEASIBLE':
                    # Preserve the entire legacy optimizer/repair receipt independently.
                    base = pc._base_polytope(u)
                    proposal = pc._LPEvidence(base, objective.weights if e.sense == 'minimum' else -objective.weights,
                        raw_masses_kg=e.witness.optimizer_masses_kg)
                    w = _candidate(u, base, proposal, objective, legacy=e.witness)
                extrema.append(pc.FVConditionalExtremum(e.sense, None, None, e.optimization, e.optimization, w))
            return replace(result, outer_interval_kg=outer, minimum=extrema[0], maximum=extrema[1])
        bands, search = _bands(conditioned)
        core = pc._query_core(pc._base_polytope(u), bands, objective.weights,
                             objective.coefficient_allowances, epsilon, a.settings, search_bands=search)
        result = replace(result, core=core, outer_interval_kg=core.outer_interval_kg, termination=core.termination,
            fallback='FINITE_BOX_OBJECTIVE_OUTER_ONLY' if any(e.status != 'CHECKED' for e in core.outer_optimizations) else None)
        if core.compatibility == 'INCOMPATIBLE_UNDER_DECLARED_CONTRACT':
            return replace(result, compatibility=core.compatibility, bounds='NOT_APPLICABLE', decision='INCOMPATIBLE')
        if core.outer_interval_kg is None or core.outer_interval_kg[0] > core.outer_interval_kg[1]:
            return replace(result, termination='NUMERICAL_OUTER_ORDER_UNRESOLVED')
        extrema = []
        for i, sense in enumerate(('minimum', 'maximum')):
            witness = _candidate(u, core.inner, core.inner_optimizations[i], objective, search=core.search)
            extrema.append(pc.FVConditionalExtremum(sense, None, None, core.outer_optimizations[i],
                                                    core.inner_optimizations[i], witness))
        return replace(result, minimum=extrema[0], maximum=extrema[1], termination='PAIRED_WITNESS_REPLAYS_REQUIRED')
    except RuntimeError as exc:
        return replace(result, termination=str(exc))


def _window_replay(response, fraction, forward, mass, obs=None):
    nominal = pc._dotq(response.weights, mass)
    error = pc._dotq(response.coefficient_allowances, mass)
    allowance = pc._product(256*se.EPS*(1+forward.exponential_applications+_native(response).conditioning_sum),
                            pc._rounded(sum(map(pc._q, mass)), 1))
    value = fraction.solute_kg
    ri = hull = discrepancy = None
    good = (forward.status == 'COMPLETE' and forward.integration_complete and forward.planned_horizon_complete
            and all(s == 'SUPPORTED' for s in forward.observation_status)
            and dict(forward.diagnostics).get('sampled_admissibility') == 'PASS'
            and fraction.status in ('VALID_NUMERICAL_ZERO', 'NUMERICAL_ONLY_ACCURACY_NOT_ASSESSED')
            and (fraction.start_s, fraction.end_s) == response.window_s)
    if value is not None:
        discrepancy = pc._rounded(pc._q(value)-nominal)
        good = good and abs(pc._q(value)-nominal) <= error+allowance
        ri = (pc._rounded(pc._q(value)-allowance, -1), pc._rounded(pc._q(value)+allowance, 1))
        hull = (pc._rounded(min(nominal-error, pc._q(value)-allowance), -1),
                pc._rounded(max(nominal+error, pc._q(value)+allowance), 1))
    contained = hull is not None and (obs is None or obs.mass_interval_kg[0] <= hull[0] <= hull[1] <= obs.mass_interval_kg[1])
    return pc.FVWindowReplay(response.identity_sha256, response.window_s, None if obs is None else obs.label,
        None if obs is None else obs.mass_interval_kg, pc._rounded(nominal), pc._rounded(error, 1), value,
        pc._rounded(allowance, 1), discrepancy, ri, hull, contained,
        'CHECKED' if good and contained else 'UNRESOLVED')


def _legacy_receipt(u, response, witness, forward, row):
    """005 replay evidence from the SAME actual batched forward, no propagation.

    The formulas/fields are the native replay_witness contract; the 005 qualifier
    consumes these in B,A order. 007 also retains stricter exact interval hulls.
    """
    m = witness.masses_kg
    prediction = se._dot(response.weights, m)
    error = se._dot(response.coefficient_allowances, m)
    summation = 64*se.EPS*math.fsum(map(float, np.abs(response.weights*m)))
    allowance = 256*se.EPS*(1+forward.exponential_applications+response.conditioning_sum)*math.fsum(m)
    value = row.forward_delivery_kg
    discrepancy = None if value is None else value-prediction
    good = row.status == 'CHECKED' and abs(discrepancy) <= error+allowance+summation
    return se.FVReplay(witness.state.identity_sha256, response.identity_sha256, forward.status, forward.reason,
        forward.fractions[0].status, forward.actual_end_s, prediction, value, discrepancy, error, allowance,
        summation, 'REPLAY_QUALIFIED' if good else 'NUMERICALLY_UNRESOLVED',
        'COMPLETE' if good else 'FORWARD_SUPPORT_OR_REPLAY_DISCREPANCY_FAILED', forward.exponential_applications,
        forward.elapsed_wall_s)


def _paired_replay(result, witness):
    obj, u = result.objective, result.conditioned_set.original
    receipt = FVPairedReplay(witness.state.identity_sha256, None, result.receipt.identity_sha256)
    try:
        witness.state.validate()
        m = se._concentrations(witness.state)*u.capacities_m3
        inner = result.core.inner if result.core is not None else pc._base_polytope(u)
        if (witness.state.model_identity != u.lower.model_identity or witness.state.time_s != u.lower.time_s
                or not np.array_equal(m, witness.masses_kg) or not pc._residuals(inner, m).feasible
                or not se._residuals(u, m).feasible):
            raise RuntimeError('WITNESS_CHANGED_OR_OUTSIDE_JOINT_SET')
        state = pc._lift_state(witness.state) if isinstance(obj.response_a, pc.FVEqualChildPullback) else witness.state
        receipt = replace(receipt, replay_state_identity=state.identity_sha256)
        obs = result.conditioned_set.observations
        forwards, branches, legacy = [], [], []
        for label, target in (('a', obj.response_a), ('b', obj.response_b)):
            # Observations on A are applicable to B ONLY via the validated receipt.
            # No fabricated B early response or mutation of the observations.
            responses = (target, *(o.response for o in obs))
            windows = tuple(r.window_s for r in responses)
            times = tuple(sorted({result.receipt.branch_time_s, *(v for w in windows for v in w)}))
            start = time.monotonic()
            receipt = replace(receipt, forward_calls=receipt.forward_calls+1)
            forward = sf.simulate_stateful_fv(plan=target.plan, initial_state=state,
                observation_times_s=times, fraction_windows_s=windows)
            if (forward.root_state.identity_sha256 != state.identity_sha256
                    or forward.plan.identity_sha256 != target.plan.identity_sha256
                    or len(forward.fractions) != len(responses)):
                raise RuntimeError('REPLAY_STATE_PLAN_OR_WINDOW_MISMATCH')
            rows = tuple(_window_replay(r, f, forward, m, None if i == 0 else obs[i-1])
                         for i, (r, f) in enumerate(zip(responses, forward.fractions)))
            good = all(r.status == 'CHECKED' for r in rows)
            branch = pc.FVConditionedReplay(witness.state.identity_sha256, state.identity_sha256,
                target.plan.identity_sha256, rows, 'CHECKED' if good else 'UNRESOLVED',
                'COMPLETE' if good else 'REPLAY_SUPPORT_DISCREPANCY_OR_CONTAINMENT_FAILED',
                forward.exponential_applications, forward.status, time.monotonic()-start)
            receipt = replace(receipt, **{'branch_'+label: branch})
            branches.append(branch); forwards.append(forward)
            if result.legacy_b_a is not None:
                legacy.append(_legacy_receipt(u, target, witness, forward, rows[0]))
        a, b = forwards
        k = result.receipt.prefix_steps
        if any(len(f.primary.times_s) <= k or f.primary.times_s[k] != result.receipt.branch_time_s for f in forwards):
            raise RuntimeError('BRANCH_CHEMICAL_STATE_UNSUPPORTED')
        traces = tuple(f.raw_primary_masses_kg[:k+1, :-1] for f in forwards)
        phase_views = tuple(tuple(getattr(f.primary, p+'_cell_average_kg_m3')[:k+1] for p in se.PHASES) for f in forwards)
        equal = (np.array_equal(traces[0], traces[1]) and
            all(np.array_equal(x, y) for x, y in zip(phase_views[0], phase_views[1])) and
            np.array_equal(a.primary.times_s[:k+1], b.primary.times_s[:k+1]) and
            np.array_equal(a.step_outlet_solute_kg[:k], b.step_outlet_solute_kg[:k]) and
            np.array_equal(a.step_volume_m3[:k], b.step_volume_m3[:k]))
        receipt = replace(receipt, legacy_receipts_b_a=tuple(reversed(legacy)),
            prefix_trace_identities=tuple(sf._hash(t) for t in traces),
            branch_state_identities=tuple(sf._hash((f.primary.times_s[k], f.raw_primary_masses_kg[k, :-1],
                                                   state.model_identity)) for f in forwards),
            prefix_deliveries_kg=tuple(float(f.primary.segment_outlet_solute_kg[k]) for f in forwards),
            prefix_volumes_m3=tuple(float(f.primary.segment_volume_m3[k]) for f in forwards),
            maximum_prefix_mass_discrepancy_kg=float(np.max(np.abs(traces[0]-traces[1]))),
            prefix_bitwise_equal=bool(equal))
        if not equal:
            raise RuntimeError('COMMON_PREFIX_BITWISE_REPLAY_MISMATCH')
        if not all(r.status == 'CHECKED' for r in branches):
            raise RuntimeError('PAIRED_REPLAY_FAILED')
        ra, rb = (r.windows[0] for r in branches)
        exact = pc._q(rb.forward_delivery_kg)-pc._q(ra.forward_delivery_kg)
        value = pc._rounded(exact)
        conversion = abs(pc._q(value)-exact)
        prediction = pc._prediction(obj, m)
        fi = (pc._rounded(pc._q(rb.replay_interval_kg[0])-pc._q(ra.replay_interval_kg[1]), -1),
              pc._rounded(pc._q(rb.replay_interval_kg[1])-pc._q(ra.replay_interval_kg[0]), 1))
        # Hull includes each branch's response/forward uncertainty separately;
        # tiny signed contrast NEVER normalizes or cancels those uncertainties.
        hull = (min(prediction[0], pc._rounded(pc._q(rb.combined_interval_kg[0])-pc._q(ra.combined_interval_kg[1]), -1)),
                max(prediction[1], pc._rounded(pc._q(rb.combined_interval_kg[1])-pc._q(ra.combined_interval_kg[0]), 1)))
        nominal = pc._dotq(obj.weights, m)
        error = pc._dotq(obj.coefficient_allowances, m)
        forward_error = pc._q(ra.forward_allowance_kg)+pc._q(rb.forward_allowance_kg)
        if abs(exact-nominal) > error+forward_error:
            raise RuntimeError('SIGNED_RESPONSE_REPLAY_DISCREPANCY')
        if result.receipt.exact_zero:
            if a.plan.identity_sha256 != b.plan.identity_sha256 or ra.forward_delivery_kg != rb.forward_delivery_kg:
                raise RuntimeError('IDENTICAL_OPERATOR_REPLAY_DISAGREEMENT')
            hull = (0., 0.)  # Algebraic identity; compatibility checked above.
        return replace(receipt, signed_prediction_interval_kg=prediction, signed_forward_interval_kg=fi,
            combined_interval_kg=hull, forward_difference_kg=value,
            subtraction_rounding_kg=pc._rounded(conversion, 1), status='CHECKED', termination='COMPLETE')
    except Exception as exc:
        return replace(receipt, termination=str(exc) if isinstance(exc, RuntimeError)
                       else 'PAIRED_REPLAY_EXCEPTION:'+type(exc).__name__)


def _decision(outer, margin, intervals, qualified):
    opposite = any(i[0] > 0 for i in intervals) and any(i[1] < 0 for i in intervals)
    reversal = any(i[0] > margin for i in intervals) and any(i[1] < -margin for i in intervals)
    decision = 'NUMERICALLY_UNRESOLVED'
    if qualified:
        lo, hi = outer
        if lo > margin:
            decision = 'B_UNIFORMLY_EXCEEDS_A_BY_MARGIN'
        elif hi < -margin:
            decision = 'A_UNIFORMLY_EXCEEDS_B_BY_MARGIN'
        elif -margin <= lo <= hi <= margin:
            decision = 'NO_MATERIAL_DIFFERENCE'
        elif reversal:
            decision = 'DEMONSTRATED_MATERIAL_REVERSAL'
        else:
            decision = 'NO_UNIFORM_MATERIAL_CONCLUSION'
    return decision, bool(opposite), bool(reversal)


def replay_common_past_extrema(result):
    """Both complete plans from each SAME reconstructed state; no branch reset."""
    if not isinstance(result, FVCommonPastBounds):
        raise ValueError('COMMON_PAST_BOUNDS_REQUIRED')
    obj, r = result.objective, result.receipt
    checked, _, _ = _validate(result.conditioned_set, obj.response_a, obj.response_b,
        r.branch_time_s, result.epsilon_kg, result.delta_kg, r.comparison_basis)
    if (checked != r or obj.identity_sha256 != sf._hash((r.identity_sha256, obj.weights,
            obj.coefficient_allowances, obj.subtraction_allowances))
            or obj.identity_sha256 != FVSignedContrast(obj.response_a, obj.response_b, checked).identity_sha256):
        raise ValueError('COMMON_PAST_RECEIPT_OR_OBJECTIVE_CHANGED')
    if result.minimum is None or result.maximum is None or result.bounds == 'NOT_APPLICABLE':
        return result
    extrema = []
    for e in (result.minimum, result.maximum):
        w = e.witness
        if w is None or w.status != 'CHECKED_REPLAY_REQUIRED':
            extrema.append(e); continue
        if w.replay is not None:
            raise ValueError('WITNESS_ALREADY_REPLAYED')
        replay = _paired_replay(result, w)
        extrema.append(_qualify_extremum(result, e, replay))
    return _finish_replays(result, extrema)


def _qualify_extremum(result, e, replay):
    w = replace(e.witness, replay=replay, status='COMPATIBLE' if replay.status == 'CHECKED' else 'UNRESOLVED')
    bracket = gap = None
    if replay.status == 'CHECKED':
        lo, hi = replay.combined_interval_kg
        outer = result.outer_interval_kg
        bracket = (outer[0], hi) if e.sense == 'minimum' else (lo, outer[1])
        gap = pc._rounded(pc._q(bracket[1])-pc._q(bracket[0]), 1)
    outer_good = result.legacy_b_a is None and e.outer_optimization.status == 'CHECKED'
    if result.legacy_b_a is not None:
        original = getattr(result.legacy_b_a, e.sense)
        outer_good = original.status == 'OPTIMIZATION_QUALIFIED'
    good = gap is not None and 0 <= gap <= result.epsilon_kg and outer_good
    return replace(e, witness=w, interval_kg=bracket, gap_kg=gap,
                           status='QUALIFIED' if good else 'NUMERICALLY_UNRESOLVED')


def _finish_replays(result, extrema):
    legacy = result.legacy_b_a
    if legacy is not None and all(e.witness is not None and e.witness.replay is not None
                                 and len(e.witness.replay.legacy_receipts_b_a) == 2
                                 and e.witness.state.identity_sha256 == getattr(legacy, e.sense).witness.state.identity_sha256
                                 for e in extrema):
        legacy = se.qualify_envelope(legacy, minimum_replays=extrema[0].witness.replay.legacy_receipts_b_a,
                                     maximum_replays=extrema[1].witness.replay.legacy_receipts_b_a)
    intervals = [e.witness.replay.combined_interval_kg for e in extrema
                 if e.witness is not None and e.witness.status == 'COMPATIBLE']
    good = all(e.status == 'QUALIFIED' for e in extrema)
    decision, opposite, reversal = _decision(result.outer_interval_kg, result.delta_kg, intervals, good)
    return replace(result, minimum=extrema[0], maximum=extrema[1], legacy_b_a=legacy,
        compatibility='ESTABLISHED' if intervals else 'UNRESOLVED',
        bounds='QUALIFIED' if good else 'NUMERICALLY_UNRESOLVED', decision=decision,
        opposite_sign_witnesses=opposite, material_reversal_witnesses=reversal,
        termination='COMPLETE' if good else 'PAIRED_WITNESSES_OR_COMPLETE_GAPS_UNRESOLVED')
