"""Bounded LC capacity substitution into the frozen J1 research evaluator.

No runtime component. TARGET_EXPOSED; physical validation not established.
The inherited evaluator and all predecessor artifacts remain byte-identical.
"""
import numpy as np

from . import joint_clock_001 as J
from . import pressure_peak_stage_c3e as C

ORDER = ("a", "Pstar", "n", "Pd", "f", "tau0")


def coordinates(parameters):
    """Explicit six-coordinate extension: f is linear; final tau0 alone /100."""
    p = np.asarray(parameters, dtype=float)
    if p.shape != (6,):
        raise ValueError("LC-J1 requires (a, Pstar, n, Pd, f, tau0)")
    common = J.coordinates(p[[0, 1, 2, 3, 5]], "J1")
    return np.r_[common[:4], p[4], common[4]]


def physical(z):
    z = np.asarray(z, dtype=float)
    if z.shape != (6,):
        raise ValueError("LC-J1 requires six coordinates with tau0 last")
    common = J.physical(z[[0, 1, 2, 3, 5]], "J1")
    return np.r_[common[:4], z[4], common[4]]


def bounds():
    return (coordinates([.001, .5, 1., .1, 0., 0.]),
            coordinates([20., 100., np.inf, 100., 1., 100.]))


def capacity(parameters, pressure):
    """Existing C3E LC law, g/s at nonnegative bar; no changed definition."""
    p = np.asarray(parameters)[:5]
    pressure = np.maximum(pressure, 0.)
    # Evaluate exact nested boundaries through the original J1 expression.
    # C3E's general stable opening helper is algebraically identical but its
    # exp(n*log(P/Pd)) roundoff can change tiny mass-balance diagnostics.
    if p[4] == 0.:
        with np.errstate(over="ignore"):
            return J.W.capacity(np.r_[p[:4], 1.], pressure)
    if p[4] == 1. or p[2] == 1.:
        return J.W.capacity([p[0], p[1], 1., p[3], 1.], pressure)
    return C.capacity(p, pressure, "LC")[0]


class Prepared(J.Prepared):
    """Only capacity changes; inherited front/column/observer methods are reused."""
    def __init__(self, source, parameters, mc, dt=.02, cells=256):
        p = np.asarray(parameters)
        if p.shape != (6,):
            raise ValueError("Wrong LC-J1 parameter vector")
        super().__init__(source["predict_times_s"], source["predict_pressure_bar"],
                         np.r_[p[:4], mc], "W1", [p[5]], dt, cells,
                         source["predict_horizon_s"])
        # Parent construction initializes timing and empty chemistry cache. Its
        # provisional A hydraulics are replaced before any column/observer call.
        pressure = np.maximum(np.interp(self.time, source["predict_times_s"],
                                       source["predict_pressure_bar"]), 0.)
        self.cap = capacity(p, pressure)
        if not np.isfinite(self.cap).all():
            raise ValueError("Nonfinite LC capacity: unavailable")
        self.mass, self.flow = J.liquid_only(self.time, self.cap, self.front, mc)


def prepare(source, parameters, mc, dt=.02, cells=256):
    return Prepared(source, parameters, mc, dt, cells)


def objective(data, parameters, weight, held, dt=.02, accelerate=True):
    """Exact inherited equal-condition/equal-brew objective and fixed support."""
    from .joint_clock_001_run import label
    sources = [s for s in data["sources"] if held is None or s["nominal_pressure_bar"] != held]
    mc = data["bank"][label(held)][4]
    parts, detectors, calls = [], [], 0
    for s in sources:
        predictor = prepare(s, parameters, mc, dt)
        observer = predictor.observer(s["observer_times_s"], accelerate=accelerate)
        parts.append(J.loss_components(predictor.scored_flow(s["fit_times_s"]),
            s["fit_flow_g_s"], observer, s["observed_onset_for_scoring_only_s"]))
        detectors.append(observer["detected"])
        calls += predictor.column_calls
    conditions = sorted({s["nominal_pressure_bar"] for s in sources})
    groups = [np.array([i for i, s in enumerate(sources) if s["nominal_pressure_bar"] == p]) for p in conditions]
    means = np.array([np.asarray(parts)[g].mean(axis=0) for g in groups])
    flow, onset = means.mean(axis=0)
    value = float(flow+weight*onset)
    if not np.isfinite(value):
        raise ValueError("Nonfinite objective is unavailable, never censored")
    return dict(parameters=list(map(float, parameters)), objective=value,
        flow_component=float(flow), onset_component=float(onset),
        weighted_onset_component=float(weight*onset), detected=sum(detectors),
        intended=len(sources), available=len(sources), column_calls=calls,
        condition_components=[dict(pressure_bar=p, flow=float(v[0]), onset=float(v[1]),
            weighted_onset=float(weight*v[1]), detected=int(np.sum(np.asarray(detectors)[g])),
            brews=len(g)) for p, v, g in zip(conditions, means, groups)])
