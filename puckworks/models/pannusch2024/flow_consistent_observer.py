"""Opt-in prescribed-volume continuous extension of checked stateful FV output.

Numerical extension, not exact varying chemistry: the clock scales the entire
frozen generator. RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Pannusch et al., 10.1016/j.jfoodeng.2023.111887; source-derived output
10.17632/y2tz67f6ry.1, CC-BY-NC-3.0; first-party software licensing separate.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields
import hashlib
import json
import math
from pathlib import Path
import time
from typing import Sequence

import numpy as np

from . import stateful_fv as sf

METHOD = "pannusch2024.flow_consistent_observer.volume_clock.v1"
_EPS = np.finfo(float).eps
CLOCK_RTOL = 64 * _EPS
COMPOSITION_RTOL = 512 * _EPS
LOCAL_FLUX_CSCALE = 2e-11


def _require(ok, reason):
    if not ok:
        raise ValueError(reason)


def _finite_array(value, shape, name):
    _require(isinstance(value, np.ndarray) and value.shape == shape
             and np.isrealobj(value) and np.isfinite(value).all(), name)


def _checked_prefix(result):
    """Validate content and physical views; hashes are not execution authenticity.

    Histories are structurally reconstructed, but forcing is evaluated only on
    retained intervals, never on a future planned interval to supply a query.
    No primary evolution or legacy interior observation is used as a new check.
    """
    _require(type(result) is sf.StatefulFVResult, "CHECKED_STATEFUL_RESULT_REQUIRED")
    r = result
    _require(r.identity_sha256 == sf._hash(r), "RESULT_IDENTITY_MISMATCH")
    r.root_state.validate()
    r.plan.validate()
    root, p = r.root_state, r.plan
    # Re-run constructor guards as well as content hashes.
    args = {f.name: getattr(root, f.name) for f in fields(root) if f.init}
    rebuilt = sf.FVChemicalState(**args)
    _require(rebuilt.identity_sha256 == root.identity_sha256, "ROOT_STATE_MISMATCH")
    for history in (p.flow_history, p.temperature_history):
        _require(type(history)(**{f.name: getattr(history, f.name) for f in fields(history)}) == history,
                 "HISTORY_MISMATCH")
    sf.FVSettings(**{f.name: getattr(p.settings, f.name) for f in fields(p.settings)})
    n = p.settings.cells
    s = sf.fv._System(root.solute, root.grind, n)
    _require(len(root.edges_m) == n+1 and np.array_equal(root.edges_m, s.edges), "MESH_MISMATCH")
    _require(type(r.start_index) is int and 0 <= r.start_index < len(p.primary_times_s), "START_INDEX")
    ts = r.primary.times_s
    _require(isinstance(ts, np.ndarray) and ts.ndim == 1 and len(ts) > 0, "PRIMARY_TIMES")
    k = len(ts)
    _finite_array(p.primary_steps, (len(p.primary_times_s)-1, 4), "PLAN_DIMENSIONS")
    _require(np.array_equal(p.primary_times_s, np.r_[p.t_span_s[0], p.primary_steps[:, 1]])
             and np.array_equal(p.primary_steps[:, 0], p.primary_times_s[:-1])
             and np.all(np.diff(p.primary_times_s) > 0), "PLAN_TIMESTAMPS")
    _require(np.array_equal(ts, p.primary_times_s[r.start_index:r.start_index+k]), "PRIMARY_SCHEDULE")
    _require(r.actual_end_s == ts[-1] and ts[0] <= r.actual_end_s <= r.requested_stop_s
             <= p.t_span_s[1] and r.requested_stop_s in p.primary_times_s, "ACTUAL_SUPPORT")
    _finite_array(r.raw_primary_masses_kg, (k, 3*n+1), "RAW_PRIMARY_DIMENSIONS")
    _finite_array(r.step_outlet_solute_kg, (k-1,), "STEP_MASS_DIMENSIONS")
    _finite_array(r.step_volume_m3, (k-1,), "STEP_VOLUME_DIMENSIONS")
    _require(r.exportable_primary.shape == (k,) and np.isin(r.exportable_primary, (0., 1.)).all(),
             "EXPORTABLE_DIMENSIONS")
    good = r.exportable_primary.astype(bool)
    _require(not np.any(good[1:] & ~good[:-1]), "NONCONTIGUOUS_CHECKED_PREFIX")
    end = int(np.flatnonzero(~good)[0])-1 if not np.all(good) else k-1
    _require(np.array_equal(r.step_outlet_solute_kg, r.raw_primary_masses_kg[1:, -1]), "RAW_DELIVERY_MISMATCH")
    _require(len(r.prior_outlet_terms_kg) <= 200000 and len(r.prior_outlet_terms_kg) == len(r.prior_volume_terms_m3)
             and all(math.isfinite(x) for x in r.prior_outlet_terms_kg)
             and all(math.isfinite(x) and x > 0 for x in r.prior_volume_terms_m3), "PRIOR_ACCOUNTING")
    _require(r.mode in ("FRESH_STATE", "SAME_SCHEDULE_CONTINUATION", "BRANCH"), "RESULT_MODE")
    if r.mode == "FRESH_STATE":
        _require(r.start_index == 0 and not r.prior_outlet_terms_kg and r.parent_identity is None
                 and root.time_s == ts[0], "FRESH_LINEAGE")
        initial = np.r_[np.concatenate([root.liquid_cell_average_kg_m3,
            root.fine_cell_average_kg_m3, root.coarse_cell_average_kg_m3])*s.capacities, 0.]
        _require(np.array_equal(initial, r.raw_primary_masses_kg[0]), "ROOT_RAW_STATE")
    else:
        _require(isinstance(r.parent_identity, str) and len(r.parent_identity) == 64
                 and all(x in '0123456789abcdef' for x in r.parent_identity)
                 and len(r.prior_outlet_terms_kg) > 0 and root.time_s <= ts[0]
                 and r.raw_primary_masses_kg[0, -1] == r.prior_outlet_terms_kg[-1], "CONTINUATION_LINEAGE")
        if r.mode == "SAME_SCHEDULE_CONTINUATION":
            _require(r.start_index > 0 and len(r.prior_volume_terms_m3) >= r.start_index,
                     "CONTINUATION_INDEX")
        else:
            _require(r.start_index == 0, "BRANCH_INDEX")
    c = (r.raw_primary_masses_kg[:, :-1]/s.capacities).reshape(k, 3, n)
    for j, name in enumerate(('liquid_cell_average_kg_m3', 'fine_cell_average_kg_m3',
                              'coarse_cell_average_kg_m3')):
        _finite_array(getattr(r.primary, name), (k, n), "PHYSICAL_DIMENSIONS")
        _require(np.array_equal(c[:, j], getattr(r.primary, name)), "RAW_PHYSICAL_MISMATCH")
    inventory = np.array([sf._inventory(*row, root.grind) for row in c])
    masses = np.array([math.fsum(r.step_outlet_solute_kg[:i]) for i in range(k)])
    origins = np.array([math.fsum((*r.prior_outlet_terms_kg, *r.step_outlet_solute_kg[:i])) for i in range(k)])
    vols = np.array([p.flow_history.integral(ts[0], t) for t in ts])
    origin_vols = np.array([math.fsum((*r.prior_volume_terms_m3, v)) for v in vols])
    expected = dict(outlet_face_kg_m3=c[:, 0, -1], remaining_inventory_kg=inventory,
        segment_outlet_solute_kg=masses, origin_outlet_solute_kg=origins,
        segment_volume_m3=vols, origin_volume_m3=origin_vols)
    for name, value in expected.items():
        _finite_array(getattr(r.primary, name), (k,), "PRIMARY_VIEW_DIMENSIONS")
        _require(np.array_equal(value, getattr(r.primary, name)), "PRIMARY_ACCOUNTING_VIEW_MISMATCH")
    # Validate only stored forcing intervals. History knots may not be interior.
    knots = (*p.flow_history.times_s, *p.temperature_history.times_s)
    for i, (a, b) in enumerate(zip(ts, ts[1:])):
        step = p.primary_steps[r.start_index+i]
        mid = float(a+(b-a)/2)
        _require(not any(a < t < b for t in knots), "UNSPLIT_FORCING_KNOT")
        _require(abs(step[2]-p.temperature_history.value_K(mid)) <= CLOCK_RTOL*step[2]
                 and abs(step[3]-p.flow_history.value_m3_s(mid)) <= CLOCK_RTOL*step[3], "FROZEN_FORCING_MISMATCH")
        _require(r.step_volume_m3[i] == p.flow_history.integral(a, b), "STORED_VOLUME_MISMATCH")
    for i in range(end+1):
        _require(sf._within(min(0., float(np.min(c[i]))), root.concentration_scale_kg_m3, 1e-10)
            and sf._within(math.fsum((inventory[i], origins[i], -root.inventory_kg)), root.inventory_kg, 1e-8)
            and sf._within(math.fsum((inventory[i], masses[i], -inventory[0])), inventory[0], 1e-8),
            "CHECKED_PRIMARY_ADMISSIBILITY")
        if i:
            _require(sf._within(min(0., r.step_outlet_solute_kg[i-1]), inventory[0], 1e-10)
                and sf._within(math.fsum((inventory[i], r.step_outlet_solute_kg[i-1], -inventory[i-1])),
                               inventory[i-1], 1e-8), "CHECKED_INTERVAL_ADMISSIBILITY")
    # Old raw/physical views must agree, even though they do not qualify new interiors.
    dt, dy = r.raw_diagnostic_times_s, r.raw_diagnostic_masses_kg
    _require(dt.ndim == 1 and np.all(np.diff(dt) > 0) and np.all((dt >= ts[0]) & (dt <= ts[-1])),
             "DIAGNOSTIC_SUPPORT")
    _finite_array(dy, (len(dt), 3*n+1), "DIAGNOSTIC_DIMENSIONS")
    _require(len(dt) > 0 and all(t in dt for t in ts), "MISSING_PRIMARY_DIAGNOSTICS")
    for t,y in zip(ts, r.raw_primary_masses_kg):
        _require(np.array_equal(dy[np.searchsorted(dt,t)], y), "PRIMARY_DIAGNOSTIC_MISMATCH")
    _require(r.raw_quadrature.ndim == 2 and r.raw_quadrature.shape[1] == 13
             and np.isfinite(r.raw_quadrature).all(), "QUADRATURE_DIMENSIONS")
    q = r.raw_quadrature
    if len(q):
        _require(np.isin(q[:,2], (4.,8.)).all() and np.all(q[:,3] == np.floor(q[:,3]))
                 and np.all((q[:,3] >= 0) & (q[:,3] < k-1)), "QUADRATURE_OWNER")
        for i in range(k-1):
            rows = q[q[:,3] == i]
            _require(all(np.count_nonzero((rows[:,2] == order) & (rows[:,5] == 1)) == order
                         for order in (4,8)) and np.all((rows[:,0] >= ts[i]) & (rows[:,0] <= ts[i+1]))
                         and np.all((rows[:,4] > ts[i]) & (rows[:,4] <= ts[i+1])), "QUADRATURE_SUPPORT")
    else:
        _require(k == 1, "MISSING_CHECKED_QUADRATURE")
    ot = r.observations.times_s
    _require(len(r.observation_times_s) == len(r.observation_status)
             and np.array_equal(ot, [t for t, status in zip(r.observation_times_s, r.observation_status)
                                    if status == 'SUPPORTED']), "OBSERVATION_STATUS_MISMATCH")
    for i, t in enumerate(ot):
        hits = np.flatnonzero(dt == t)
        _require(len(hits) == 1 and t <= ts[max(end, 0)], "OLD_OBSERVATION_SUPPORT")
        y = dy[hits[0]]
        dc = (y[:-1]/s.capacities).reshape(3, n)
        j = int(np.searchsorted(ts, t))
        terms = r.step_outlet_solute_kg[:j] if ts[j] == t else (*r.step_outlet_solute_kg[:j-1], float(y[-1]))
        v = p.flow_history.integral(ts[0],t)
        views = dict(outlet_face_kg_m3=dc[0,-1], remaining_inventory_kg=sf._inventory(*dc,root.grind),
            segment_outlet_solute_kg=math.fsum(terms), origin_outlet_solute_kg=math.fsum((*r.prior_outlet_terms_kg,*terms)),
            segment_volume_m3=v, origin_volume_m3=math.fsum((*r.prior_volume_terms_m3,v)))
        for name,value in views.items():
            _require(getattr(r.observations,name).shape == (len(ot),) and getattr(r.observations,name)[i] == value,
                     "OLD_OBSERVATION_ACCOUNTING_MISMATCH")
        for j, name in enumerate(('liquid_cell_average_kg_m3', 'fine_cell_average_kg_m3', 'coarse_cell_average_kg_m3')):
            _require(np.array_equal(getattr(r.observations, name)[i], dc[j]), "OLD_RAW_PHYSICAL_MISMATCH")
    return s, end


@dataclass(frozen=True)
class FlowConsistentPanel:
    owner_index: int
    start_s: float
    end_s: float
    solute_kg: float
    volume_m3: float
    actual_Q_GL4_kg: float
    actual_Q_GL8_kg: float
    frozen_Q_GL8_kg: float
    inventory_residual_kg: float
    composition_residual_kg: float
    actual_flux_residual_kg: float
    actual_flux_residual_over_Cstar: float | None
    quadrature_control_kg: float


@dataclass(frozen=True, eq=False)
class FlowConsistentFVResult:
    upstream_result_sha256: str
    upstream_plan_sha256: str
    model_sha256: str
    source_dependencies: tuple
    observation_times_s: tuple[float, ...]
    fraction_windows_s: tuple[tuple[float, float], ...]
    observation_status: tuple[str, ...]
    observations: sf.StatefulTrajectory
    raw_observation_masses_kg: np.ndarray
    fractions: tuple[sf.fv.FVFraction, ...]
    panels: tuple[FlowConsistentPanel, ...]
    # Per sampled state: physical time, interval/local/root signed inventory
    # residuals, three phase minima, owning-interval delivered mass, owner index.
    checks: np.ndarray
    clock_residuals: np.ndarray
    quadrature: np.ndarray
    root_time_s: float
    continuation_start_s: float
    upstream_checked_end_s: float | None
    actual_checked_end_s: float | None
    request_support: str
    numerical_admissibility: str
    reason: str | None
    exponential_applications: int
    elapsed_wall_s: float
    method: str = METHOD
    accuracy_status: str = "NOT_ASSESSED"
    campaign_qualification: str = "NOT_ASSESSED_FOR_THIS_CALL"
    PHYSICAL_VALIDATION: str = "NOT_ESTABLISHED"
    scope: str = "RESEARCH_ONLY"
    identity_sha256: str = field(init=False)

    def __post_init__(self):
        sf._freeze(self)

    def to_json(self) -> str:
        record = sf._json(self)
        record['identity_sha256'] = self.identity_sha256
        record['unsupported_observations'] = [dict(time_s=t, values=None, reason=s)
            for t, s in zip(self.observation_times_s, self.observation_status) if s != 'SUPPORTED']
        return json.dumps(record, sort_keys=True, allow_nan=False)


class _Clock:
    """Local analytic volumes, never differences of large volume clocks."""
    def __init__(self, flow, a, b, Q):
        self.flow, self.a, self.b, self.h, self.Q = flow, a, b, b-a, Q
        self.V = flow.integral(a, b)
        _require(math.isfinite(self.V) and self.V > 0, "UNREPRESENTABLE_INTERVAL_VOLUME")
        self.residual = (self.h*Q-self.V)/self.V
        self.endpoint_residual = ((self.h/self.V)*self.V-self.h)/self.h
        _require(abs(self.residual) <= CLOCK_RTOL and abs(self.endpoint_residual) <= CLOCK_RTOL,
                 "CLOCK_ENDPOINT_IDENTITY_FAILED")
        i = flow._index(a)
        self.constant = flow.kind == 'constant' or flow.flows_m3_s[i] == flow.flows_m3_s[i+1]

    def delta(self, l, r):
        _require(self.a <= l <= r <= self.b, "CLOCK_SUPPORT")
        if l == r:
            return 0.
        if self.constant or (l == self.a and r == self.b):
            value = r-l
        else:
            volume = self.flow.integral(l, r)
            _require(volume > 0 and math.isfinite(volume), "UNREPRESENTABLE_LOCAL_VOLUME")
            value = (self.h/self.V)*volume
        _require(value > 0 and math.isfinite(value), "UNREPRESENTABLE_CLOCK_INCREMENT")
        return value

    def at(self, t):
        if t == self.a:
            return 0.
        if t == self.b:
            return self.h
        v = self.delta(self.a, t)
        _require(0 < v < self.h, "INTERIOR_CLOCK_UNRESOLVED")
        return v


class _Actions:
    def __init__(self, settings, started):
        self.settings, self.started, self.calls = settings, started, 0

    def check(self):
        if time.monotonic()-self.started >= self.settings.wall_time_limit_s:
            raise RuntimeError("WALL_TIME_LIMIT")
        if self.calls >= self.settings.max_exponential_applications:
            raise RuntimeError("EXPONENTIAL_APPLICATION_LIMIT")

    def evolve(self, A, y, duration):
        self.check()
        state = y.copy()
        state[-1] = 0.
        if duration == 0:
            return state
        self.calls += 1
        z = np.asarray(sf.fv.expm_multiply(A*duration, state,
                       traceA=float(A.diagonal().sum())*duration))
        _require(z.shape == state.shape and np.isfinite(z).all(), "NONFINITE_EXPONENTIAL")
        return z


def observe_flow_consistent_fv(
    result: sf.StatefulFVResult, *, observation_times_s: Sequence[float],
    fraction_windows_s: Sequence[Sequence[float]] = (),
    resource_settings: sf.FVSettings | None = None,
) -> FlowConsistentFVResult:
    """Observe the contiguous admissible retained prefix; never propagate it.

    Unsupported requests have absent values and explicit reasons. Intervals are
    published atomically after new phase, inventory and actual-Q flux checks.
    Fractions are never silently truncated. Request order/duplicates are retained.
    Endpoint states and whole-step masses remain upstream-authoritative.
    """
    started = time.monotonic()
    system, last = _checked_prefix(result)
    r, p, root = result, result.plan, result.root_state
    obs = sf._reals(observation_times_s, 'observations', 0)
    _require(all(x == 0 or y != 0 for x,y in zip(observation_times_s,obs)), "UNREPRESENTABLE_OBSERVATION_TIME")
    windows = tuple(sf._reals(w, 'fraction window', 2) for w in fraction_windows_s)
    _require(all(len(w) == 2 and w[0] <= w[1] for w in windows), "INVALID_FRACTION_WINDOW")
    for original, converted in zip(fraction_windows_s, windows):
        _require(all(x == 0 or y != 0 for x,y in zip(original,converted))
                 and (original[0] == original[1] or converted[0] != converted[1]), "UNREPRESENTABLE_FRACTION_CLOCK")
    settings = p.settings if resource_settings is None else resource_settings
    _require(isinstance(settings, sf.FVSettings) and all(getattr(settings, k) == getattr(p.settings, k)
        for k in ('cells', 'h_max_s', 'diagnostic_step_s')), "RESOURCE_SETTINGS_CANNOT_CHANGE_PLAN")
    _require((len(obs)+2*len(windows)+2)*(3*system.n+1) <= settings.max_state_values, "STATE_ALLOCATION_LIMIT")
    action = _Actions(settings, started)
    ts, raw = r.primary.times_s, r.raw_primary_masses_kg
    start = float(ts[0]); supported_end = float(ts[last]) if last >= 0 else None
    C, M = root.concentration_scale_kg_m3, root.inventory_kg
    def inv(y):
        return sf._inventory(*(y[:-1]/system.capacities).reshape(3, system.n), root.grind)
    local_M = inv(raw[0])
    local_C = float(np.max(np.abs(raw[0, :-1]/system.capacities)))
    samples = {start: raw[0]} if last >= 0 else {}
    panels, checks, clocks, pieces = [], [], [], [[] for _ in windows]
    quadrature = []
    checked_end, reason = (start if last >= 0 else None), None
    requests = sorted({*obs, *(t for w in windows for t in w)})
    target = max((t for t in requests if supported_end is not None and start <= t <= supported_end), default=start)
    rules = {order: np.polynomial.legendre.leggauss(order) for order in (4, 8)}
    previous_key, A = None, None
    try:
        for i in range(max(0, last)):
            a, b = map(float, ts[i:i+2])
            if a >= target:
                break
            action.check()
            T, Q = p.primary_steps[r.start_index+i, 2:]
            if (T, Q) != previous_key:
                A, previous_key = system.generator(T, Q), (T, Q)
            clock = _Clock(p.flow_history, a, b, Q)
            pending = {}
            pending_checks = []
            def check(t, y):
                c = (y[:-1]/system.capacities).reshape(3, system.n)
                bed = inv(y)
                dm = float(y[-1]) if t != a else 0.
                interval = math.fsum((bed, dm, -inv(raw[i])))
                local = math.fsum((bed, *r.step_outlet_solute_kg[:i], dm, -local_M))
                origin = math.fsum((bed, *r.prior_outlet_terms_kg, *r.step_outlet_solute_kg[:i], dm, -M))
                minima = tuple(map(float, np.min(c, axis=1)))
                pending_checks.append((t, interval, local, origin, *minima, dm, i))
                _require(t == a or M == 0 or dm > 0, "OUTLET_INCREMENT_UNRESOLVED")
                _require(all(sf._within(min(0., x), local_C, 1e-10) for x in minima)
                    and sf._within(min(0., dm), local_M, 1e-10)
                    and sf._within(interval, inv(raw[i]), 1e-8)
                    and sf._within(local, local_M, 1e-8) and sf._within(origin, M, 1e-8),
                    "NEW_INTERIOR_ADMISSIBILITY_FAILED")
            def at(t):
                if t in pending:
                    return pending[t]
                y = raw[i] if t == a else raw[i+1] if t == b else action.evolve(A, raw[i], clock.at(t))
                check(t, y)
                pending[t] = y
                return y
            at(a); at(b)
            at(a+(b-a)/2)
            for t in p.diagnostic_times_s[(p.diagnostic_times_s > a) & (p.diagnostic_times_s < b)]:
                at(float(t))
            for t in requests:
                if a < t < b:
                    at(t)
            intervals = {(a, b)}
            for l, h in windows:
                if l >= start and supported_end is not None and h <= supported_end and l < h:
                    lo, hi = max(a, l), min(b, h)
                    if lo < hi:
                        intervals.add((lo, hi))
            panel_map = {}
            pending_quadrature = []
            for l, h in sorted(intervals):
                left, right = at(l), at(h)
                evolved = right if l == a and h == b else action.evolve(A, left, clock.delta(l, h))
                dm = float(evolved[-1]); volume = p.flow_history.integral(l, h)
                _require(volume > 0 and math.isfinite(volume), "UNREPRESENTABLE_LOCAL_VOLUME")
                residual = math.fsum((inv(right), dm, -inv(left)))
                composition = math.fsum((0. if l == a else float(left[-1]), dm, -float(right[-1])))
                _require(sf._within(residual, inv(left), 1e-8)
                         and sf._within(composition, inv(raw[i]), COMPOSITION_RTOL), "LOCAL_COMPOSITION_FAILED")
                _require(np.isfinite(evolved).all() and sf._within(float(np.max(np.abs(evolved[:-1]-right[:-1]))),
                         inv(raw[i]), COMPOSITION_RTOL), "LOCAL_PHASE_COMPOSITION_FAILED")
                integrals = {}
                for order in (4, 8):
                    nodes, weights = rules[order]
                    actual, frozen = [], []
                    for node, weight in zip(nodes, weights):
                        t = l+(h-l)*(float(node)+1)/2
                        y = at(t)
                        c_last = float(y[system.n-1]/system.capacities[system.n-1])
                        w = (h-l)*float(weight)/2
                        _require(w > 0, "UNREPRESENTABLE_QUADRATURE_WEIGHT")
                        pending_quadrature.append((i, l, h, order, t, w, c_last, inv(y),
                            0. if t == a else float(y[-1]), *np.min((y[:-1]/system.capacities).reshape(3, system.n), axis=1)))
                        actual.append(w*(Q if clock.constant else p.flow_history.value_m3_s(t))*c_last)
                        frozen.append(w*Q*c_last)
                    integrals[order] = (math.fsum(actual), math.fsum(frozen))
                g4, g8, frozen = integrals[4][0], integrals[8][0], integrals[8][1]
                error, control = g8-dm, g8-g4
                allowance = max(LOCAL_FLUX_CSCALE*C*volume, COMPOSITION_RTOL*abs(dm))
                _require(math.isfinite(allowance) and abs(error) <= allowance
                         and abs(control) <= allowance, "ACTUAL_Q_LOCAL_FLUX_CLOSURE_FAILED")
                panel_map[l, h] = FlowConsistentPanel(i, l, h, dm, volume, g4, g8, frozen,
                    residual, composition, error, sf._scaled(error/volume, C), control)
            _require(len(checks)+len(pending_checks) <= settings.max_diagnostic_samples, "DIAGNOSTIC_SAMPLE_LIMIT")
            # Publish only after every requested piece and every sampled phase is checked.
            for t in requests:
                if a <= t <= b:
                    samples[t] = at(t)
            checks.extend(pending_checks)
            clocks.append((a, b, clock.residual, clock.endpoint_residual))
            panels.extend(panel_map.values())
            quadrature.extend(pending_quadrature)
            for j, (l, h) in enumerate(windows):
                key = (max(a, l), min(b, h))
                if key in panel_map and l >= start and supported_end is not None and h <= supported_end and l < h:
                    pieces[j].append(panel_map[key])
            checked_end = b
    except (ValueError, RuntimeError, FloatingPointError, OverflowError) as exc:
        reason = str(exc)
    def status(t):
        if t < start:
            return 'BEFORE_CONTINUATION_START'
        if supported_end is None or t > supported_end:
            return 'OUTSIDE_UPSTREAM_CHECKED_PREFIX'
        if t not in samples or checked_end is None or t > checked_end:
            return reason or 'NOT_CHECKED'
        return 'SUPPORTED'
    statuses = tuple(status(t) for t in obs)
    supported = [t for t, s in zip(obs, statuses) if s == 'SUPPORTED']
    states = np.asarray([samples[t] for t in supported]).reshape(len(supported), 3*system.n+1)
    c = (states[:, :-1]/system.capacities).reshape(-1, 3, system.n)
    local_mass, origin_mass, local_volume, origin_volume = [], [], [], []
    for t, y in zip(supported, states):
        j = int(np.searchsorted(ts, t))
        terms = r.step_outlet_solute_kg[:j] if ts[j] == t else (*r.step_outlet_solute_kg[:j-1], float(y[-1]))
        local_mass.append(math.fsum(terms)); origin_mass.append(math.fsum((*r.prior_outlet_terms_kg, *terms)))
        v = p.flow_history.integral(start, t)
        local_volume.append(v); origin_volume.append(math.fsum((*r.prior_volume_terms_m3, v)))
    trajectory = sf.StatefulTrajectory(np.asarray(supported), c[:, 0], c[:, 1], c[:, 2], c[:, 0, -1],
        np.asarray([inv(y) for y in states]), np.asarray(local_mass), np.asarray(origin_mass),
        np.asarray(local_volume), np.asarray(origin_volume))
    fractions = []
    for (l, h), parts in zip(windows, pieces):
        why = None
        if status(l) != 'SUPPORTED' or status(h) != 'SUPPORTED':
            why = status(l) if status(l) != 'SUPPORTED' else status(h)
        elif l == h:
            fractions.append(sf.fv.FVFraction(l, h, 0., 0., None, None, 'UNDEFINED', 'ZERO_DURATION'))
            continue
        elif not parts or parts[0].start_s != l or parts[-1].end_s != h or any(x.end_s != y.start_s for x, y in zip(parts, parts[1:])):
            why = 'INCOMPLETE_FRACTION'
        if why:
            fractions.append(sf.fv.FVFraction(l, h, None, None, None, None, 'UNSUPPORTED', why))
            continue
        dm, dv = math.fsum(x.solute_kg for x in parts), math.fsum(x.volume_m3 for x in parts)
        concentration = dm/dv
        resolved = math.isfinite(concentration) and (M == 0 or (dm > 0 and concentration > 0))
        fractions.append(sf.fv.FVFraction(l, h, dm, dv, concentration if resolved else None,
            concentration if math.isfinite(concentration) else None,
            ('VALID_NUMERICAL_ZERO' if M == 0 else 'NUMERICAL_ONLY_ACCURACY_NOT_ASSESSED') if resolved else 'UNQUALIFIED',
            None if resolved else 'OUTLET_INCREMENT_UNRESOLVED'))
    complete = all(s == 'SUPPORTED' for s in statuses) and all(f.status not in ('UNSUPPORTED', 'UNQUALIFIED') for f in fractions)
    dependencies = (*sf._sources(), ('flow_consistent_observer.py', hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    return FlowConsistentFVResult(r.identity_sha256, p.identity_sha256, root.model_identity, dependencies,
        obs, windows, statuses, trajectory, states, tuple(fractions), tuple(panels), np.asarray(checks).reshape(-1, 9),
        np.asarray(clocks).reshape(-1, 4), np.asarray(quadrature).reshape(-1, 12), root.time_s, start, supported_end, checked_end,
        'COMPLETE' if complete else 'INCOMPLETE', 'PASSED_ON_RETURNED_SUPPORT' if last >= 0 else 'NO_ADMISSIBLE_SUPPORT',
        reason, action.calls, time.monotonic()-started)
