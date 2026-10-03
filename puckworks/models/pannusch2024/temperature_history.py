"""Prescribed uniform T(t), fixed SI Q, for the existing saturated Pannusch model.

Equations/parameters: Pannusch et al., J. Food Eng. 367 (2024), 111887;
Mendeley 10.17632/y2tz67f6ry.1. Source-derived outputs retain CC-BY-NC-3.0
attribution separately from first-party software licensing. No thermal field,
experimental ramp reconstruction, empirical validation, or legacy API change.
See docs/analysis/model_pannusch2024_temp_history_001/CONTRACT.md.
"""
from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
import hashlib
import json
import math
from pathlib import Path
import time

import numpy as np
from scipy.integrate import BDF
from scipy.sparse import bmat, csc_matrix, eye

from . import closures as pc
from . import solver as source

SPECIES = ("caffeine", "trigonelline", "5CQA", "tds")
LIMITATIONS = (
    "PHYSICAL_VALIDATION=NOT_ESTABLISHED",
    "Prescribed spatially uniform temperature; no solved thermal field or thermal lag.",
    "Caller-prescribed SI flow domain; experimental flow convention remains unresolved.",
    "Numerical qualification is limited to reported cases, not every allowed history.",
    "Fitted c_s0 is not independently measured recoverable inventory.",
    "Sampled positivity is not an all-time proof; the source nodal stencil is not conservative.",
    "No empirical scoring, native-MATLAB equivalence, coupling or production adoption.",
)
BASES = (
    ("liquid", "kg/m^3 of liquid"),
    ("fine", "kg/m^3 on source fine-grain basis; inventory capacity alpha_s1"),
    ("coarse", "kg/m^3 on source coarse-grain basis; inventory capacity phi_v2*alpha_s2"),
    ("outlet_solute", "kg"), ("hydraulic_volume", "m^3"),
    ("fraction_concentration", "kg/m^3 of collected liquid"),
)


class InvalidTemperatureHistoryInput(ValueError):
    """Rejected before integration; machine-readable status is INVALID_INPUT."""

    def to_json(self):
        return json.dumps({"status": "INVALID_INPUT", "reason": str(self)}, allow_nan=False)


def _reject(reason):
    raise InvalidTemperatureHistoryInput(reason)


def _reject_complex(value, name):
    """Reject complex values before NumPy can silently discard imaginary parts."""
    try:
        a = np.asarray(value)
    except (TypeError, ValueError, OverflowError):
        _reject(f"{name} must contain real numeric values")
    if np.iscomplexobj(a) or (a.dtype.kind == "O" and any(
            np.iscomplexobj(x) or isinstance(x, (np.ndarray, list, tuple)) for x in a.flat)):
        _reject(f"{name} must contain real numeric values, not complex values")


def _vector(value, name, minimum=1):
    _reject_complex(value, name)
    try:
        a = np.asarray(value, dtype=float)
    except (TypeError, ValueError, OverflowError):
        _reject(f"{name} must be a finite one-dimensional numeric sequence")
    if a.ndim != 1 or len(a) < minimum or not np.isfinite(a).all():
        _reject(f"{name} has invalid shape, length or nonfinite values")
    return tuple(float(x) for x in a)


def _clock(value, name, minimum=2):
    x = _vector(value, name, minimum)
    if any(b <= a or not math.isfinite(b-a) for a, b in zip(x, x[1:])):
        _reject(f"{name} must increase strictly with finite differences")
    return x


def _positive(value, name):
    _reject_complex(value, name)
    if isinstance(value, (bool, np.bool_, str)) or np.ndim(value) != 0:
        _reject(f"{name} must be finite and positive")
    try:
        v = float(value)
    except (TypeError, ValueError, OverflowError):
        _reject(f"{name} must be finite and positive")
    if not math.isfinite(v) or v <= 0:
        _reject(f"{name} must be finite and positive")
    return v


@dataclass(frozen=True)
class TemperatureHistory:
    """Kelvin forcing. Linear knots or constant interval edges, never extrapolated.

    Constant intervals are left-closed/right-open, with the final endpoint
    assigned to the final interval. Duplicate times never encode steps.
    """

    times_s: tuple[float, ...]
    temperatures_K: tuple[float, ...]
    kind: str

    def __post_init__(self):
        t = _clock(self.times_s, "history times")
        temperatures = _vector(self.temperatures_K, "temperatures_K")
        if not isinstance(self.kind, str) or self.kind not in ("linear", "constant"):
            _reject("history kind must be linear or constant")
        expected = len(t) if self.kind == "linear" else len(t)-1
        if len(temperatures) != expected or any(not 353.15 <= x <= 371.15 for x in temperatures):
            _reject("temperature count or 353.15..371.15 K domain violated")
        object.__setattr__(self, "times_s", t)
        object.__setattr__(self, "temperatures_K", temperatures)

    @classmethod
    def linear_celsius(cls, times_s, temperatures_C):
        """Explicit Celsius conversion; one value per strictly increasing knot."""
        return cls(times_s, tuple(x+273.15 for x in _vector(temperatures_C, "temperatures_C")),
                   "linear")

    @classmethod
    def constant_celsius(cls, edges_s, temperatures_C):
        """Explicit Celsius conversion; one value per interval, not per edge."""
        return cls(edges_s, tuple(x+273.15 for x in _vector(temperatures_C, "temperatures_C")),
                   "constant")

    def value_K(self, t_s):
        _reject_complex(t_s, "temperature query time")
        t = float(t_s)
        if not math.isfinite(t) or not self.times_s[0] <= t <= self.times_s[-1]:
            _reject("temperature query outside supplied history support")
        i = min(int(np.searchsorted(self.times_s, t, side="right"))-1, len(self.times_s)-2)
        if self.kind == "constant":
            return self.temperatures_K[i]
        a, b = self.times_s[i:i+2]
        return self.temperatures_K[i] + (t-a)/(b-a)*(
            self.temperatures_K[i+1]-self.temperatures_K[i])

    def integration_segments(self, start_s, end_s):
        """Each segment owns both endpoint coefficients, including its left limit."""
        _reject_complex(start_s, "segment start time")
        _reject_complex(end_s, "segment end time")
        if not self.times_s[0] <= start_s < end_s <= self.times_s[-1]:
            _reject("history must cover the complete model interval")
        out = []
        for i, (left, right) in enumerate(zip(self.times_s, self.times_s[1:])):
            a, b = max(left, start_s), min(right, end_s)
            if a >= b:
                continue
            if self.kind == "constant":
                ta = tb = self.temperatures_K[i]
            else:
                slope = (self.temperatures_K[i+1]-self.temperatures_K[i])/(right-left)
                ta = self.temperatures_K[i] + slope*(a-left)
                tb = self.temperatures_K[i] + slope*(b-left)
            out.append(_TemperatureSegment(a, b, ta, tb))
        return tuple(out)


@dataclass(frozen=True)
class _TemperatureSegment:
    start_s: float
    end_s: float
    start_K: float
    end_K: float

    def value_K(self, t_s):
        if not self.start_s <= t_s <= self.end_s:
            raise ValueError("segment temperature queried beyond its support")
        return self.start_K + (self.end_K-self.start_K)*(t_s-self.start_s)/(
            self.end_s-self.start_s)


@dataclass(frozen=True)
class TemperatureHistorySettings:
    """BDF tolerances scale concentrations by c_s0 and mass by continuum M0.

    The defaults are the frozen fine temporal level. diagnostic_step_s bounds
    sampling gaps; accepted steps and their quarter points are also checked.
    """

    nz: int = 200
    rtol: float = 1e-9
    normalized_atol: float = 1e-11
    max_step_s: float = 0.05
    diagnostic_step_s: float = 0.0125
    max_steps: int = 100000
    wall_time_limit_s: float = 60.0

    def __post_init__(self):
        for key, low, high in (("nz", 5, 2000), ("max_steps", 1, 1000000)):
            v = getattr(self, key)
            if isinstance(v, bool) or not isinstance(v, (int, np.integer)) or not low <= v <= high:
                _reject(f"{key} must be an integer in {low}..{high}")
            object.__setattr__(self, key, int(v))
        for key in ("rtol", "normalized_atol", "max_step_s", "diagnostic_step_s",
                    "wall_time_limit_s"):
            object.__setattr__(self, key, _positive(getattr(self, key), key))
        if not 100*np.finfo(float).eps <= self.rtol <= 0.1 or self.normalized_atol > 0.1:
            _reject("tolerances outside supported numerical settings")
        if self.max_step_s/self.diagnostic_step_s > 100000:
            _reject("diagnostic sampling exceeds 100000 subdivisions per maximum step")
        if self.wall_time_limit_s > 3600:
            _reject("wall_time_limit_s must be <=3600")


def _immutable_array(value):
    a = np.asarray(value, dtype=float)
    # Immutable bytes backing prevents even setflags(write=True) from mutating results.
    return np.frombuffer(a.tobytes(), dtype=float).reshape(a.shape)


@dataclass(frozen=True, eq=False)
class PhysicalTrajectory:
    times_s: np.ndarray
    temperature_K: np.ndarray
    liquid_kg_m3: np.ndarray
    fine_kg_m3: np.ndarray
    coarse_kg_m3: np.ndarray
    outlet_solute_kg: np.ndarray
    hydraulic_volume_m3: np.ndarray

    def __post_init__(self):
        for f in fields(self):
            object.__setattr__(self, f.name, _immutable_array(getattr(self, f.name)))


@dataclass(frozen=True)
class FractionConcentration:
    start_s: float
    end_s: float
    solute_kg: float | None
    volume_m3: float | None
    concentration_kg_m3: float | None
    status: str
    reason: str | None


@dataclass(frozen=True)
class SegmentDiagnostic:
    requested_span_s: tuple[float, float]
    actual_span_s: tuple[float, float]
    endpoint_temperature_K: tuple[float, float]
    start_state_sha256: str
    end_state_sha256: str
    accepted_steps: int
    nfev: int
    njev: int
    nlu: int
    status: str
    reason: str | None


@dataclass(frozen=True, eq=False)
class TemperatureHistoryResult:
    solute: str
    grind: float
    flow_m3_s: float
    history: TemperatureHistory
    settings: TemperatureHistorySettings
    requested_span_s: tuple[float, float]
    actual_span_s: tuple[float, float]
    requested_observation_times_s: tuple[float, ...]
    observation_status: tuple[str, ...]
    observations: PhysicalTrajectory
    checked_trajectory: PhysicalTrajectory
    fractions: tuple[FractionConcentration, ...]
    segments: tuple[SegmentDiagnostic, ...]
    status: str
    reason: str | None
    integration_complete: bool
    M0_cont_kg: float
    parameters: tuple[tuple[str, float | str], ...]
    geometry: tuple[tuple[str, float], ...]
    source_identities: tuple[tuple[str, str], ...]
    configuration_sha256: str
    units_and_bases: tuple[tuple[str, str], ...] = BASES
    limitations: tuple[str, ...] = LIMITATIONS
    qualification_status: str = "NOT_ASSESSED_FOR_THIS_CALL"

    def to_json(self, *, include_trajectories=True):
        """Strict JSON; unsupported quantities are null, never NaN or extrapolated."""
        return json.dumps(_json_value(self, include_trajectories), sort_keys=True, allow_nan=False)


def _json_value(value, include_trajectories=True):
    if isinstance(value, PhysicalTrajectory) and not include_trajectories:
        return {"sample_count": len(value.times_s),
                "support_s": [float(value.times_s[0]), float(value.times_s[-1])]
                if len(value.times_s) else None,
                "arrays": "OMITTED_BY_SERIALIZATION_REQUEST"}
    if is_dataclass(value):
        return {f.name: _json_value(getattr(value, f.name), include_trajectories) for f in fields(value)}
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (tuple, list)):
        return [_json_value(x, include_trajectories) for x in value]
    return value


def _digest(value):
    return hashlib.sha256(value).hexdigest()


def _source_identities():
    from puckworks.data import DATA_DIR
    base = Path(__file__).parent
    paths = {"temperature_history.py": Path(__file__), "solver.py": base/"solver.py",
             "closures.py": base/"closures.py"}
    for name in ("table2_fitted_params.csv", "table2_grind_psi_ds2.csv"):
        paths["pannusch2024/"+name] = DATA_DIR/"pannusch2024"/name
    return tuple((key, _digest(path.read_bytes())) for key, path in sorted(paths.items()))


class _PhysicalSystem:
    """One solve's fixed configuration. No source dictionaries/globals are mutated."""

    def __init__(self, solute, grind, Q, nz):
        self.nz, self.Q = nz, Q
        self.sp = dict(source._solute_params()[solute])
        g = source.GRINDS[grind]
        self.psi, self.d2 = float(g["psi"]), float(g["d_s2"])
        self.as1 = self.psi*(1-source.ALPHA_L)
        self.as2 = (1-self.psi)*(1-source.ALPHA_L)
        self.q = Q/source.ACS
        self.d32 = 6.0/(self.psi*6.0/source.D1_FINE+(1-self.psi)*6.0/self.d2)
        self.D = csc_matrix(source.five_point_biased_upwind(
            nz, source.L/(nz-1), self.q))
        self.select = eye(nz, format="csc")[1:, :]
        self.insert = self.select.T

    def coefficients(self, T):
        p = self.sp
        h1 = float(pc.sherwood_h(T, self.q, p["A1"], p["B1"], p["solute"], self.d32))
        h2 = float(pc.sherwood_h(T, self.q, p["A2"], p["B2"], p["solute"], self.d32))
        K = float(pc.vant_hoff_K(T, p["K_ref"], p["gamma"]))
        f1, f2 = 6*h1/source.D1_FINE, 6*h2/(source.PHI_V2*self.d2)
        return K, f1, f2, self.as1*f1/source.ALPHA_L, source.PHI_V2*self.as2*f2/source.ALPHA_L

    def initial_state(self, T):
        y = np.full(3*self.nz, self.sp["c_s0"], dtype=float)
        y[:self.nz-1] *= self.coefficients(T)[0]
        y[-1] = 0.
        return y

    def continuum_inventory(self, T):
        return source.ACS*source.L*self.sp["c_s0"]*(source.ALPHA_L*self.coefficients(T)[0]
                                                       +self.as1+source.PHI_V2*self.as2)

    def physical_rhs(self, T, y):
        n = self.nz
        cl = np.r_[0., y[:n-1]]
        s1, s2 = y[n-1:2*n-1], y[2*n-1:3*n-1]
        K, f1, f2, m1, m2 = self.coefficients(T)
        e1, e2 = K*s1-cl, K*s2-cl
        dc = -(self.q/source.ALPHA_L)*(self.D@cl)+m1*e1+m2*e2
        return np.r_[dc[1:], -f1*e1, -f2*e2, self.Q*cl[-1]]

    def physical_jacobian(self, T):
        n = self.nz
        K, f1, f2, m1, m2 = self.coefficients(T)
        liquid = -(self.q/source.ALPHA_L)*self.D[1:, 1:]-(m1+m2)*eye(n-1)
        outlet = csc_matrix(([self.Q], ([0], [n-2])), shape=(1, n-1))
        return bmat([[liquid, m1*K*self.select, m2*K*self.select, csc_matrix((n-1, 1))],
                     [f1*self.insert, -f1*K*eye(n), None, csc_matrix((n, 1))],
                     [f2*self.insert, None, -f2*K*eye(n), csc_matrix((n, 1))],
                     [outlet, csc_matrix((1, n)), csc_matrix((1, n)), csc_matrix((1, 1))]],
                    format="csc")


def _trajectory(times, states, system, history, t0):
    t = np.asarray(times, dtype=float)
    y = np.asarray(states, dtype=float).reshape(len(t), 3*system.nz)
    n = system.nz
    return PhysicalTrajectory(t, np.array([history.value_K(x) for x in t]),
                              np.column_stack((np.zeros(len(t)), y[:, :n-1])),
                              y[:, n-1:2*n-1], y[:, 2*n-1:3*n-1],
                              y[:, -1], system.Q*(t-t0))


def simulate_temperature_history(
    history, *, flow_m3_s, t_span_s, solute, grind=1.7,
    observation_times_s, fraction_bounds_s=(), settings=TemperatureHistorySettings(),
):
    """Integrate from model t0, including any unobserved prefix, with clean inlet.

    Invalid inputs raise InvalidTemperatureHistoryInput before any integration.
    Failed solves return their finite supported prefix and explicit null observers.
    Observation arrays contain only supported requests, in the requested order.
    checked_trajectory includes accepted steps, quarter-step samples and a refined
    diagnostic grid. There is no dense-output extrapolation or numerical cache.
    """
    if not isinstance(history, TemperatureHistory) or not isinstance(settings, TemperatureHistorySettings):
        _reject("history/settings require their immutable model-local contracts")
    span = _clock(t_span_s, "t_span_s")
    if len(span) != 2:
        _reject("t_span_s must contain exactly the model start and end")
    t0, tf = span
    Q = _positive(flow_m3_s, "flow_m3_s")
    if not 1e-6 <= Q <= 3e-6:
        _reject("flow_m3_s outside caller-prescribed 1e-6..3e-6 SI domain")
    if not isinstance(solute, str) or solute not in SPECIES:
        _reject("unknown solute identity")
    _reject_complex(grind, "grind")
    if isinstance(grind, (bool, np.bool_, str)) or np.ndim(grind) != 0:
        _reject("grind must be a declared source setting: 1.4, 1.7 or 2.0")
    try:
        grind = float(grind)
    except (TypeError, ValueError, OverflowError):
        _reject("invalid grind setting")
    if grind not in source.GRINDS:
        _reject("grind must be a declared source setting: 1.4, 1.7 or 2.0")
    obs = _clock(observation_times_s, "observation_times_s", minimum=1)
    bounds = _clock(fraction_bounds_s, "fraction_bounds_s", minimum=0)
    if len(bounds) == 1:
        _reject("fractions require zero or at least two boundaries")
    if any(t < t0 or t > tf for t in (*obs, *bounds)):
        _reject("observation/fraction outside explicit model support")
    if any(b-a <= 1024*np.finfo(float).eps*(tf-t0) for a, b in zip(bounds, bounds[1:])):
        _reject("fraction volume difference is numerically unresolvable")
    if min(settings.max_step_s, settings.diagnostic_step_s) <= 10*max(
            abs(np.spacing(t0)), abs(np.spacing(tf))):
        _reject("clock magnitude cannot resolve requested numerical steps")
    if (tf-t0)/settings.diagnostic_step_s > 1000000:
        _reject("diagnostic sampling exceeds one million uniform subdivisions")
    segments = history.integration_segments(t0, tf)
    system = _PhysicalSystem(solute, grind, Q, settings.nz)
    M0 = system.continuum_inventory(history.value_K(t0))
    cs0 = system.sp["c_s0"]
    atol = np.r_[np.full(3*settings.nz-1, cs0*settings.normalized_atol),
                 M0*settings.normalized_atol]
    y = system.initial_state(history.value_K(t0))
    # Inputs have already been checked. This internal union is not input repair.
    queries = sorted(set((*obs, *bounds)))
    samples = {t0: y.copy()}
    checked_t, checked_y = [t0], [y.copy()]
    records, steps, actual, reason = [], 0, t0, None
    started = time.monotonic()
    for segment in segments:
        first = y.copy()
        stepper = None
        count = 0
        try:
            def fun(t, state):
                return system.physical_rhs(segment.value_K(t), state)

            def jac(t, state):
                return system.physical_jacobian(segment.value_K(t))

            stepper = BDF(fun, segment.start_s, y.copy(), segment.end_s,
                          rtol=settings.rtol, atol=atol, max_step=settings.max_step_s, jac=jac)
            while stepper.status == "running":
                if steps >= settings.max_steps:
                    reason = "ACCEPTED_STEP_LIMIT"
                    break
                if time.monotonic()-started >= settings.wall_time_limit_s:
                    reason = "WALL_TIME_LIMIT"
                    break
                old_t = stepper.t
                message = stepper.step()
                if stepper.status == "failed":
                    reason = "INTEGRATION_FAILURE: "+str(message)
                    break
                if not np.isfinite(stepper.y).all() or not old_t < stepper.t <= segment.end_s:
                    reason = "NONFINITE_OR_INVALID_ACCEPTED_STEP"
                    break
                dense = stepper.dense_output()
                # Each dense call is confined to the accepted step's support.
                count_grid = max(4, int(math.ceil((stepper.t-old_t)/settings.diagnostic_step_s)))
                grid = np.unique(np.r_[np.linspace(old_t, stepper.t, count_grid+1)[1:],
                                       np.linspace(old_t, stepper.t, 5)[1:]])
                wanted = [t for t in queries if old_t < t <= stepper.t]
                grid = np.unique(np.r_[grid, wanted])
                values = dense(grid).T
                at_queries = dense(np.asarray(wanted)).T if wanted else np.empty((0, len(y)))
                if not np.isfinite(values).all() or not np.isfinite(at_queries).all():
                    reason = "NONFINITE_DENSE_OUTPUT"
                    break
                y = stepper.y.copy()
                actual = float(stepper.t)
                values[-1] = y  # accepted endpoint, a single consistent physical knot state
                checked_t.extend(float(t) for t in grid)
                checked_y.extend(values)
                for t, state in zip(wanted, at_queries):
                    samples[t] = y.copy() if t == actual else state.copy()
                count += 1
                steps += 1
            if reason is None and (stepper.status != "finished" or actual != segment.end_s):
                reason = "INCOMPLETE_SEGMENT"
        except Exception as exc:
            # Preserve only the last fully checked finite prefix; don't serialize local paths.
            reason = "INTEGRATOR_EXCEPTION:"+type(exc).__name__
        records.append(SegmentDiagnostic(
            (segment.start_s, segment.end_s), (segment.start_s, actual),
            (segment.start_K, segment.end_K), _digest(first.tobytes()), _digest(y.tobytes()),
            count, int(getattr(stepper, "nfev", 0)), int(getattr(stepper, "njev", 0)),
            int(getattr(stepper, "nlu", 0)), "COMPLETE" if reason is None else "FAILED", reason))
        if reason is not None:
            break
    complete = reason is None and actual == tf
    fractions = []
    for a, b in zip(bounds, bounds[1:]):
        if a not in samples or b not in samples:
            fractions.append(FractionConcentration(a, b, None, None, None,
                                                   "UNSUPPORTED", "OUTSIDE_ACTUAL_SUPPORT"))
            continue
        ma, mb = float(samples[a][-1]), float(samples[b][-1])
        dm, dv = mb-ma, Q*(b-a)
        subtraction_allowance = 2*(atol[-1]+settings.rtol*max(abs(ma), abs(mb)))
        subtraction_allowance += 64*np.finfo(float).eps*M0
        if abs(dm) <= subtraction_allowance or dm < 0 or not math.isfinite(dm/dv):
            fractions.append(FractionConcentration(a, b, dm, dv, None,
                                                   "NUMERICALLY_UNRESOLVED", "MASS_DIFFERENCE_UNRESOLVED"))
        else:
            fractions.append(FractionConcentration(a, b, dm, dv, dm/dv,
                                                   "COMPLETE" if complete else "PREFIX_SUPPORTED",
                                                   None if complete else "INTEGRATION_INCOMPLETE"))
    supported = [t for t in obs if t in samples]
    status = "COMPLETE" if complete else "INTEGRATION_FAILED"
    if complete and any(f.concentration_kg_m3 is None for f in fractions):
        status, reason = "OBSERVER_UNRESOLVED", "NUMERICALLY_UNRESOLVED_FRACTION"
    identities = _source_identities()
    config = {"history": _json_value(history), "settings": _json_value(settings), "Q": Q,
              "span": span, "solute": solute, "grind": grind, "observations": obs,
              "fraction_bounds": bounds, "parameters": system.sp, "sources": identities}
    geometry = (("A_m2", source.ACS), ("L_m", source.L), ("alpha_l", source.ALPHA_L),
                ("phi_v2", source.PHI_V2), ("d1_m", source.D1_FINE), ("d2_m", system.d2),
                ("psi", system.psi), ("d32_m", system.d32))
    config["geometry"] = geometry
    return TemperatureHistoryResult(
        solute, grind, Q, history, settings, span, (t0, actual), obs,
        tuple("SUPPORTED" if t in samples else "OUTSIDE_ACTUAL_SUPPORT" for t in obs),
        _trajectory(supported, [samples[t] for t in supported], system, history, t0),
        _trajectory(checked_t, checked_y, system, history, t0), tuple(fractions), tuple(records),
        status, reason, complete, M0, tuple(sorted(system.sp.items())), geometry, identities,
        _digest(json.dumps(config, sort_keys=True, allow_nan=False).encode()))
