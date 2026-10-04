"""Research cell-average FV backend: independent prescribed uniform T(t) and positive SI Q(t).

G2 / NUMERICAL_METHOD_CHANGE. Pannusch et al., DOI 10.1016/j.jfoodeng.2023.111887;
source-derived outputs: 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0, separately from
first-party software licensing. No change to the nodal backend or its evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy.sparse.linalg import expm_multiply

from . import closures as pc, solver as ps, temperature_history as th
from . import temperature_history_fv as fixed
from .flow_history import FlowHistory

FVSettings = fixed.FVSettings
_mass_generator = fixed._mass_generator
_freeze_arrays = fixed._freeze_arrays

TemperatureHistory = th.TemperatureHistory
InvalidTemperatureHistoryInput = th.InvalidTemperatureHistoryInput
BACKEND = "pannusch2024.flow_temperature.cell_average_upwind_fv.exponential_midpoint.v1"
BASES = (("phase_fields", "CELL_AVERAGE; kg/m^3 on source liquid/fine/coarse bases"),
         ("liquid_capacity", "A*dz*alpha_l; m^3"),
         ("fine_capacity", "A*dz*alpha_s1; m^3"),
         ("coarse_capacity", "A*dz*phi_v2*alpha_s2; m^3"),
         ("outlet_face", "kg/m^3; positive-Q upwind trace equals last liquid cell average"),
         ("outlet_solute", "kg"), ("hydraulic_volume", "m^3"),
         ("fraction_concentration", "kg/m^3 of collected liquid; numerical value only"))
LIMITATIONS = (
    "PHYSICAL_VALIDATION=NOT_ESTABLISHED",
    "Prescribed uniform temperature, not a solved or measured thermal field.",
    "Prescribed SI flow does not resolve the source experimental flow convention.",
    "First-order upwind diffusion is numerical error, not physical dispersion.",
    "Exact-arithmetic positivity/conservation are not floating-point certificates or accuracy.",
    "Per-call temporal/spatial accuracy NOT_ASSESSED; campaign scope is separately reported.",
    "Fitted c_s0 is not independently measured recoverable inventory.",
    "No physical yield, taste, source-MATLAB equivalence or empirical validation claim.",
)



@dataclass(frozen=True, eq=False)
class FVTrajectory:
    times_s: np.ndarray
    temperature_K: np.ndarray
    prescribed_flow_m3_s: np.ndarray
    liquid_cell_average_kg_m3: np.ndarray
    fine_cell_average_kg_m3: np.ndarray
    coarse_cell_average_kg_m3: np.ndarray
    outlet_face_kg_m3: np.ndarray
    outlet_solute_kg: np.ndarray
    hydraulic_volume_m3: np.ndarray

    def __post_init__(self):
        _freeze_arrays(self)


@dataclass(frozen=True, eq=False)
class FVTrace:
    """Primary partitions are independent of observers; states are phase masses."""
    times_s: np.ndarray
    masses_kg: np.ndarray
    frozen_temperature_K: np.ndarray
    frozen_flow_m3_s: np.ndarray

    def __post_init__(self):
        _freeze_arrays(self)


@dataclass(frozen=True, eq=False)
class FVQuadrature:
    """GL4 and GL8 on every numerical interval, evaluated from that step's start."""
    times_s: np.ndarray
    weights_s: np.ndarray
    order: np.ndarray
    primary_step_index: np.ndarray
    panel_end_s: np.ndarray
    full_interval: np.ndarray
    numerical_frozen_step_flux_kg_s: np.ndarray
    prescribed_flow_diagnostic_flux_kg_s: np.ndarray
    outlet_solute_kg: np.ndarray
    total_from_physical_fields_kg: np.ndarray
    phase_minima_kg_m3: np.ndarray

    def __post_init__(self):
        _freeze_arrays(self)


@dataclass(frozen=True)
class FVFraction:
    start_s: float
    end_s: float
    solute_kg: float | None
    volume_m3: float | None
    concentration_kg_m3: float | None
    raw_diagnostic_concentration_kg_m3: float | None
    status: str
    reason: str | None
    accuracy_status: str = "NOT_ASSESSED"
    physical_prediction_status: str = "NOT_VALIDATED"


@dataclass(frozen=True, eq=False)
class FVResult:
    solute: str
    grind: float
    flow_history: FlowHistory
    temperature_history: TemperatureHistory
    settings: FVSettings
    requested_span_s: tuple[float, float]
    actual_span_s: tuple[float, float]
    requested_observation_times_s: tuple[float, ...]
    observation_status: tuple[str, ...]
    edges_m: np.ndarray
    centers_m: np.ndarray
    phase_capacities_m3: np.ndarray
    observations: FVTrajectory
    checked_trajectory: FVTrajectory
    trace: FVTrace
    quadrature: FVQuadrature
    fractions: tuple[FVFraction, ...]
    segments: tuple
    status: str
    reason: str | None
    integration_complete: bool
    numerical_admissibility: str
    admissibility_diagnostics: tuple[tuple[str, float], ...]
    M0_cont_kg: float
    M0_fv_kg: float
    parameters: tuple[tuple[str, float | str], ...]
    geometry: tuple[tuple[str, float], ...]
    source_identities: tuple[tuple[str, str], ...]
    configuration_sha256: str
    exponential_applications: int
    propagations: int
    diagnostic_evaluations: int
    elapsed_wall_s: float
    backend: str = BACKEND
    method: str = "constant exponential / nonautonomous exponential midpoint; frozen-step partial exponential extension"
    units_and_bases: tuple = BASES
    limitations: tuple = LIMITATIONS
    accuracy_status: str = "NOT_ASSESSED"
    campaign_qualification: str = "NOT_ASSESSED_FOR_THIS_CALL"
    PHYSICAL_VALIDATION: str = "NOT_ESTABLISHED"

    def __post_init__(self):
        _freeze_arrays(self)
        # Segment records use immutable key/value tuples, despite accepting dicts internally.
        object.__setattr__(self, "segments", tuple(tuple(sorted(s.items())) for s in self.segments))

    def to_json(self, *, include_trajectories=True):
        def convert(value):
            if not include_trajectories and isinstance(value, (FVTrajectory, FVTrace, FVQuadrature)):
                return {"sample_count": len(value.times_s), "arrays": "OMITTED_BY_REQUEST"}
            if is_dataclass(value):
                return {f.name: convert(getattr(value, f.name)) for f in fields(value)}
            if isinstance(value, np.ndarray):
                return value.tolist()
            if isinstance(value, (tuple, list)):
                return [convert(x) for x in value]
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            return value
        record = convert(self)
        record["unsupported_observations"] = [
            {"time_s": t, "values": None, "reason": status}
            for t, status in zip(self.requested_observation_times_s, self.observation_status)
            if status != "SUPPORTED"]
        return json.dumps(record, sort_keys=True, allow_nan=False)


class _System:
    def __init__(self, solute, grind, n):
        self.n = n
        self.sp = dict(ps._solute_params()[solute])
        self.psi, self.d2 = ps.GRINDS[grind]["psi"], ps.GRINDS[grind]["d_s2"]
        self.as1 = self.psi*(1-ps.ALPHA_L)
        self.as2 = (1-self.psi)*(1-ps.ALPHA_L)
        self.d32 = 6/(self.psi*6/ps.D1_FINE+(1-self.psi)*6/self.d2)
        self.edges = np.linspace(0, ps.L, n+1)
        self.centers = (self.edges[:-1]+self.edges[1:])/2
        self.W = ps.ACS*ps.L/n
        self.capacities = np.repeat(self.W*np.array([ps.ALPHA_L, self.as1, ps.PHI_V2*self.as2]), n)
        self.Cstar = self.sp["c_s0"]

    def coefficients(self, T, Q):
        p = self.sp
        K = float(pc.vant_hoff_K(T, p["K_ref"], p["gamma"]))
        h1 = float(pc.sherwood_h(T, Q/ps.ACS, p["A1"], p["B1"], p["solute"], self.d32))
        h2 = float(pc.sherwood_h(T, Q/ps.ACS, p["A2"], p["B2"], p["solute"], self.d32))
        return K, 6*h1/ps.D1_FINE, 6*h2/(ps.PHI_V2*self.d2)

    def generator(self, T, Q):
        K, k1, k2 = self.coefficients(T, Q)
        return _mass_generator(self.n, Q/(self.W*ps.ALPHA_L), self.as1*k1/ps.ALPHA_L,
                               ps.PHI_V2*self.as2*k2/ps.ALPHA_L, K*k1, K*k2)

    def initial(self, T):
        K = float(pc.vant_hoff_K(T, self.sp["K_ref"], self.sp["gamma"]))
        return np.r_[self.capacities*np.repeat([K*self.Cstar, self.Cstar, self.Cstar], self.n), 0.]

    def M0(self, T):
        return ps.ACS*ps.L*self.Cstar*(ps.ALPHA_L*float(pc.vant_hoff_K(T, self.sp["K_ref"], self.sp["gamma"]))+self.as1+ps.PHI_V2*self.as2)


def _physical(times, masses, system, history, flow, t0):
    t = np.asarray(times)
    x = np.asarray(masses).reshape(len(t), 3*system.n+1)
    c = (x[:, :-1]/system.capacities).reshape(len(t), 3, system.n)
    return FVTrajectory(t, np.array([history.value_K(at) for at in t]),
                        np.array([flow.value_m3_s(at) for at in t]), c[:, 0], c[:, 1], c[:, 2],
                        c[:, 0, -1], x[:, -1], np.array([flow.integral(t0, at) for at in t]))


def _identities():
    from puckworks.data import DATA_DIR
    paths = {"flow_temperature_history_fv.py": Path(__file__),
             "flow_history.py": Path(__file__).with_name("flow_history.py"),
             "temperature_history_fv.py": Path(fixed.__file__), "temperature_history.py": Path(th.__file__),
             "solver.py": Path(ps.__file__), "closures.py": Path(pc.__file__)}
    for name in ("table2_fitted_params.csv", "table2_grind_psi_ds2.csv"):
        paths["pannusch2024/"+name] = DATA_DIR/"pannusch2024"/name
    return tuple((k, hashlib.sha256(v.read_bytes()).hexdigest()) for k, v in sorted(paths.items()))


@dataclass(frozen=True)
class _JointSegment:
    start_s: float
    end_s: float
    temperature: th._TemperatureSegment
    flow: object

    def forcing(self, t):
        return self.temperature.value_K(t), self.flow.value_m3_s(t)


def _segments(history, flow, t0, tf):
    ts = history.integration_segments(t0, tf)
    qs = flow.integration_segments(t0, tf)
    knots = sorted({t0, tf, *(s.end_s for s in ts), *(s.end_s for s in qs)})
    i = j = 0
    out = []
    for a, b in zip(knots, knots[1:]):
        while ts[i].end_s <= a:
            i += 1
        while qs[j].end_s <= a:
            j += 1
        out.append(_JointSegment(a, b, ts[i], qs[j]))
    return tuple(out)


def _inventory(c, mout, system):
    """Reconstruct capacities from geometry, independently of mass conversion."""
    weights = ps.ACS*(ps.L/system.n)*np.array([
        ps.ALPHA_L, system.psi*(1-ps.ALPHA_L),
        ps.PHI_V2*(1-system.psi)*(1-ps.ALPHA_L)])
    return np.sum(c*weights[:, None], axis=(-2, -1))+mout


def _exception_reason(exc, prefix):
    known = ("STEP_LIMIT", "WALL_TIME_LIMIT", "EXPONENTIAL_APPLICATION_LIMIT",
             "NONFINITE_EXPONENTIAL", "DIAGNOSTIC_SAMPLE_LIMIT")
    return str(exc) if isinstance(exc, RuntimeError) and str(exc) in known else prefix+type(exc).__name__


def _evolve(system, history, flow, span, obs, bounds, settings):
    """Private mass engine; passive initial/exchange seam is used only by tests."""
    t0, tf = span
    segments = _segments(history, flow, t0, tf)
    M0, y = system.M0(history.value_K(t0)), system.initial(history.value_K(t0))
    start = time.monotonic()
    calls = diagnostic_calls = 0

    def action(B, state, dt):
        nonlocal calls
        if time.monotonic()-start >= settings.wall_time_limit_s:
            raise RuntimeError("WALL_TIME_LIMIT")
        if calls >= settings.max_exponential_applications:
            raise RuntimeError("EXPONENTIAL_APPLICATION_LIMIT")
        calls += 1
        z = np.asarray(expm_multiply(B*dt, state, traceA=float(B.diagonal().sum())*dt))
        if z.shape != state.shape or not np.isfinite(z).all():
            raise RuntimeError("NONFINITE_EXPONENTIAL")
        return z

    times, states, frozen_T, frozen_Q = [t0], [y.copy()], [], []
    reason = None
    try:
        last_key, B = None, None
        for segment in segments:
            count = int(math.ceil((segment.end_s-segment.start_s)/settings.h_max_s))
            partition = np.linspace(segment.start_s, segment.end_s, count+1)
            for a, b in zip(partition[:-1], partition[1:]):
                if len(frozen_T) >= settings.max_steps:
                    raise RuntimeError("STEP_LIMIT")
                T, Q = segment.forcing(float(a+(b-a)/2))
                key = (T, Q)
                if key != last_key:
                    B, last_key = system.generator(T, Q), key
                y = action(B, y, float(b-a))
                times.append(float(b)); states.append(y.copy())
                frozen_T.append(T); frozen_Q.append(Q)
    except Exception as exc:
        reason = _exception_reason(exc, "EXPONENTIAL_EXCEPTION:")
    # Primary propagation is finished, regardless of success, before any observer.
    propagated = len(frozen_T)
    primary_times, primary_states = np.array(times), np.array(states)
    samples, quadrature = {t0: states[0]}, []
    rules = {order: np.polynomial.legendre.leggauss(order) for order in (4, 8)}
    actual = t0
    queries = np.unique(np.r_[obs, bounds])
    grids = np.linspace(t0, tf, int(math.ceil((tf-t0)/settings.diagnostic_step_s))+1)
    requested = np.unique(np.r_[queries, grids])
    try:
        last_key, B = None, None
        for i, (T, Q) in enumerate(zip(frozen_T, frozen_Q)):
            a, b = times[i:i+2]
            key = (T, Q)
            if key != last_key:
                B, last_key = system.generator(T, Q), key
            points = np.unique(np.r_[requested[(requested > a) & (requested < b)], a+(b-a)/2])
            partial_ends = queries[(queries > a) & (queries < b)]
            if diagnostic_calls+len(points)+12*(1+len(partial_ends)) > settings.max_diagnostic_samples:
                raise RuntimeError("DIAGNOSTIC_SAMPLE_LIMIT")
            pending = {float(t): action(B, states[i], float(t-a)) for t in points}
            diagnostic_calls += len(points)
            pending[b] = states[i+1]
            qpending = []
            for end in np.r_[b, partial_ends]:
                for order in (4, 8):
                    nodes, weights = rules[order]
                    for node, weight in zip(nodes, weights):
                        dt = (end-a)*(float(node)+1)/2
                        value = action(B, states[i], dt)
                        diagnostic_calls += 1
                        c = (value[:-1]/system.capacities).reshape(3, system.n)
                        total = float(_inventory(c, value[-1], system))
                        qpending.append((a+dt, (end-a)*float(weight)/2, order, i, end, end == b,
                            Q*c[0, -1], flow.value_m3_s(a+dt)*c[0, -1], value[-1], total, *np.min(c, axis=1)))
            # Publish only a wholly checked interval; never fill a failed query.
            samples.update(pending); quadrature.extend(qpending); actual = b
    except Exception as exc:
        observer_reason = _exception_reason(exc, "OBSERVER_EXCEPTION:")
        reason = observer_reason if reason is None else reason+";"+observer_reason

    checked_times = np.array(sorted(samples))
    checked_states = np.array([samples[t] for t in checked_times])
    q = np.asarray(quadrature).reshape(-1, 13)
    c = (checked_states[:, :-1]/system.capacities).reshape(-1, 3, system.n)
    minima = np.min(c, axis=(0, 2))/system.Cstar
    totals = _inventory(c, checked_states[:, -1], system)
    residual = (totals-M0)/M0
    mout_t = np.r_[checked_times, q[:, 0]]
    mout = np.r_[checked_states[:, -1], q[:, 8]]
    if len(q):
        minima = np.minimum(minima, np.min(q[:, 10:13], axis=0)/system.Cstar)
        residual = np.r_[residual, (q[:, 9]-M0)/M0]
    chronological = mout[np.argsort(mout_t, kind="stable")]
    dm_min = float(np.min(np.diff(chronological), initial=0.)/M0)
    admissible = bool(np.min(minima) >= -1e-10 and np.max(np.abs(residual)) <= 1e-8
                      and np.min(mout)/M0 >= -1e-10 and dm_min >= -1e-10)
    diagnostics = (("minimum_liquid_over_Cstar", float(minima[0])), ("minimum_fine_over_Cstar", float(minima[1])),
                   ("minimum_coarse_over_Cstar", float(minima[2])), ("maximum_inventory_residual_over_Mstar", float(np.max(np.abs(residual)))),
                   ("signed_min_inventory_residual_over_Mstar", float(np.min(residual))),
                   ("signed_max_inventory_residual_over_Mstar", float(np.max(residual))),
                   ("minimum_Mout_increment_over_Mstar", dm_min))
    complete = reason is None and actual == tf
    fractions = []
    for a, b in zip(bounds, bounds[1:]):
        if a not in samples or b not in samples:
            fractions.append(FVFraction(a, b, None, None, None, None, "UNSUPPORTED", "NOT_EVALUATED_IN_SUPPORTED_PREFIX"))
            continue
        dm, dv = float(samples[b][-1]-samples[a][-1]), flow.integral(a, b)
        raw = dm/dv
        resolved = dm > 64*np.finfo(float).eps*M0 and math.isfinite(raw)
        valid = admissible and resolved
        fractions.append(FVFraction(a, b, dm, dv, raw if valid else None, raw if math.isfinite(raw) else None,
            ("NUMERICAL_ONLY_ACCURACY_NOT_ASSESSED" if complete else "PREFIX_NUMERICAL_ONLY") if valid else "UNQUALIFIED",
            (None if complete else "INTEGRATION_INCOMPLETE") if valid else "ADMISSIBILITY_FAILED_OR_MASS_DIFFERENCE_UNRESOLVED"))
    records = []
    for segment in segments:
        if segment.start_s > actual:
            break
        end = min(segment.end_s, actual)
        ia, ib = int(np.searchsorted(primary_times, segment.start_s)), int(np.searchsorted(primary_times, end))
        records.append(dict(requested_span_s=(segment.start_s, segment.end_s), actual_span_s=(segment.start_s, end),
            endpoint_temperature_K=(segment.forcing(segment.start_s)[0], segment.forcing(segment.end_s)[0]),
            endpoint_flow_m3_s=(segment.forcing(segment.start_s)[1], segment.forcing(segment.end_s)[1]),
            start_state_sha256=th._digest(primary_states[ia].tobytes()), end_state_sha256=th._digest(primary_states[ib].tobytes()),
            propagations=ib-ia, status="COMPLETE" if end == segment.end_s else "PARTIAL"))
        if end == actual:
            break
    supported = [t for t in obs if t in samples]
    trace_keep = primary_times <= actual
    return dict(actual_span_s=(t0, actual), observation_status=tuple("SUPPORTED" if t in samples else "NOT_EVALUATED_IN_SUPPORTED_PREFIX" for t in obs),
        observations=_physical(supported, [samples[t] for t in supported], system, history, flow, t0),
        checked_trajectory=_physical(checked_times, checked_states, system, history, flow, t0),
        trace=FVTrace(primary_times[trace_keep], primary_states[trace_keep], np.array(frozen_T)[:np.sum(trace_keep)-1], np.array(frozen_Q)[:np.sum(trace_keep)-1]),
        quadrature=FVQuadrature(q[:, 0], q[:, 1], q[:, 2], q[:, 3], q[:, 4], q[:, 5], q[:, 6], q[:, 7], q[:, 8], q[:, 9], q[:, 10:13]),
        fractions=tuple(fractions), segments=tuple(records), status="COMPLETE" if complete else "INTEGRATION_FAILED", reason=reason,
        integration_complete=complete, numerical_admissibility="PASSED_SAMPLED_CHECKS" if admissible and complete else "PASSED_ON_FINITE_PREFIX" if admissible else "FAILED",
        admissibility_diagnostics=diagnostics, M0_cont_kg=M0, M0_fv_kg=float(np.sum(states[0])),
        exponential_applications=calls, propagations=propagated, diagnostic_evaluations=diagnostic_calls, elapsed_wall_s=time.monotonic()-start)


def simulate_flow_temperature_history_fv(temperature_history, *, flow_history, t_span_s,
        solute, grind=1.7, observation_times_s, fraction_bounds_s=(), settings=FVSettings()):
    """Joint prescribed positive Q/T research FV API; per-call accuracy NOT_ASSESSED.

    Primary steps are independent of observations. Interior physical states use
    the owning step's frozen generator; collected volume uses analytic Q(t).
    COMPLETE describes integration/support, never numerical or physical accuracy.
    """
    history, flow = temperature_history, flow_history
    if not isinstance(history, TemperatureHistory) or not isinstance(flow, FlowHistory) or not isinstance(settings, FVSettings):
        th._reject("histories/settings require immutable model-local contracts")
    span = th._clock(t_span_s, "t_span_s")
    if len(span) != 2:
        th._reject("t_span_s must contain exactly two model endpoints")
    t0, tf = span
    if not isinstance(solute, str) or solute not in th.SPECIES:
        th._reject("unknown source species")
    g = th._positive(grind, "grind")
    if g not in ps.GRINDS:
        th._reject("unknown source grind")
    obs, bounds = th._clock(observation_times_s, "observation_times_s", 1), th._clock(fraction_bounds_s, "fraction_bounds_s", 0)
    if len(bounds) == 1 or any(t < t0 or t > tf for t in (*obs, *bounds)):
        th._reject("malformed or unsupported observers")
    if any(b-a <= 1024*np.finfo(float).eps*(tf-t0) for a, b in zip(bounds, bounds[1:])):
        th._reject("unresolvable fraction volume interval")
    segments = _segments(history, flow, t0, tf)
    if min(settings.h_max_s, settings.diagnostic_step_s) <= 10*max(abs(np.spacing(t0)), abs(np.spacing(tf))):
        th._reject("clock cannot resolve requested numerical steps")
    steps = sum(math.ceil((s.end_s-s.start_s)/settings.h_max_s) for s in segments)
    grid_count = math.ceil((tf-t0)/settings.diagnostic_step_s)
    if steps > 200000 or grid_count > settings.max_diagnostic_samples:
        th._reject("requested partition or diagnostic grid exceeds allocation bound")
    count = 3*min(steps, settings.max_steps)+len(obs)+len(bounds)+grid_count+2
    if count*(3*settings.cells+1) > settings.max_state_values:
        th._reject("requested field allocation exceeds max_state_values")
    system = _System(solute, g, settings.cells)
    identities = _identities()
    geometry = (("A_m2", ps.ACS), ("L_m", ps.L), ("alpha_l", ps.ALPHA_L), ("phi_v2", ps.PHI_V2),
                ("alpha_s1", system.as1), ("alpha_s2", system.as2), ("d1_m", ps.D1_FINE),
                ("d2_m", system.d2), ("psi", system.psi), ("d32_m", system.d32))
    config = dict(backend=BACKEND, temperature_history=th._json_value(history), flow_history=th._json_value(flow), settings=th._json_value(settings),
                  span=span, solute=solute, grind=g, observations=obs, fractions=bounds,
                  parameters=system.sp, geometry=geometry, identities=identities)
    return FVResult(solute=solute, grind=g, flow_history=flow, temperature_history=history, settings=settings,
        requested_span_s=span, requested_observation_times_s=obs, edges_m=system.edges,
        centers_m=system.centers, phase_capacities_m3=system.capacities.reshape(3, settings.cells)[:, 0],
        parameters=tuple(sorted(system.sp.items())), geometry=geometry, source_identities=identities,
        configuration_sha256=th._digest(json.dumps(config, sort_keys=True, allow_nan=False).encode()),
        **_evolve(system, history, flow, span, obs, bounds, settings))
