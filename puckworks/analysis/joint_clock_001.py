"""Approved joint-clock research predictor; fixed R0 chemistry, no runtime model.

The screen's conservative column is reused byte-for-byte. During fitting only,
chemistry may stop after the first onset's entire observer support is known.
Hydraulics always spans the fixed flow support; non-detections use the original
full observation contract. This is exact prefix evaluation, not a TDS surrogate.
"""
import math

import numpy as np
from scipy.signal import savgol_filter

from . import wetting_screen_001 as W

MODELS = ("J0", "J1", "J2")
WEIGHTS = (.05, .5, 1., 2.)
FLOW_SCALE = .437
ONSET_SCALE = 4.534


def decode(parameters, model, mc):
    parameters = np.asarray(parameters, dtype=float)
    if len(parameters) != {"J0": 4, "J1": 5, "J2": 7}[model]:
        raise ValueError("Wrong joint parameter count")
    theta = np.r_[parameters[:4], mc]
    arm = {"J0": "Z", "J1": "W1", "J2": "W2T"}[model]
    wet = parameters[4:6] if model == "J2" else parameters[4:]
    return theta, arm, wet, float(parameters[6]) if model == "J2" else 0.


def coordinates(parameters, model):
    z = np.asarray(parameters, dtype=float).copy()
    log_indices = [0, 1, 3]+([4, 5] if model == "J2" else [])
    z[log_indices] = np.log(z[log_indices])
    if model != "J0":
        z[-1] /= 100.
    return z


def physical(z, model):
    p = np.asarray(z, dtype=float).copy()
    log_indices = [0, 1, 3]+([4, 5] if model == "J2" else [])
    p[log_indices] = np.exp(p[log_indices])
    if model != "J0":
        p[-1] *= 100.
    return p


def bounds(model):
    lo, hi = [.001, .5, 1., .1], [20., 100., np.inf, 100.]
    if model == "J1":
        lo += [0.]
        hi += [100.]
    elif model == "J2":
        lo += [1e-16, .5, 0.]
        hi += [1e-12, 30., 100.]
    return coordinates(lo, model), coordinates(hi, model)


@W.njit(cache=True)
def liquid_only(time, cap, front, mc, gamma=0., gamma_p=0., pressure=None, exposure=None):
    """Exactly the nonnative hydraulic update in W._column; chemistry is passive."""
    if gamma_p != 0. and pressure is None:
        raise ValueError("Pressure fade requires pressure forcing")
    mass = np.zeros(len(time))
    flow = np.zeros(len(time))
    pressure_time = 0.
    if front[0] == 1.:
        flow[0] = cap[0]/math.e
    for j in range(1, len(time)):
        mass[j] = mass[j-1]
        if front[j-1] >= 1.:
            dt = time[j]-time[j-1]
            r = math.exp(-math.exp(-mass[j-1]/mc))
            if gamma != 0.:
                r *= math.exp(-gamma*mass[j-1])
            delta_phi = 0.
            if pressure is not None:
                delta_phi = .5*dt*(pressure[j-1]+pressure[j])
            if gamma_p != 0.:
                r *= math.exp(-gamma_p*pressure_time)
            mid = mass[j-1]+.25*dt*(cap[j-1]+cap[j])*r
            add = .5*dt*(cap[j-1]+cap[j])*math.exp(-math.exp(-mid/mc))
            if gamma != 0.:
                add *= math.exp(-gamma*mid)
            if gamma_p != 0.:
                add *= math.exp(-gamma_p*(pressure_time+.5*delta_phi))
            pressure_time += delta_phi
            mass[j] += add
            flow[j] = cap[j]*math.exp(-math.exp(-mass[j]/mc))
            if gamma != 0.:
                flow[j] *= math.exp(-gamma*mass[j])
            if gamma_p != 0.:
                flow[j] *= math.exp(-gamma_p*pressure_time)
        if exposure is not None:
            exposure[j] = pressure_time
    return mass, flow


class Prepared:
    """Pressure-only predictor with reusable chemistry prefixes for scale-lag search."""
    def __init__(self, source_t, source_p, theta, arm, wet, dt=.02, cells=256,
                 horizon=100., r0=W.R0(), *, gamma=0., gamma_p=0.):
        if not math.isfinite(gamma) or gamma < 0.:
            raise ValueError("Fade gamma must be finite and nonnegative")
        if not math.isfinite(gamma_p) or gamma_p < 0. or (gamma != 0. and gamma_p != 0.):
            raise ValueError("Pressure fade must be nonnegative and separate from mass fade")
        if source_t[0] > 0. or source_t[-1] < horizon or horizon < 100.:
            raise ValueError("Predictor missing fixed pressure support")
        time = np.r_[np.arange(0., horizon, dt), horizon]
        front, tb = W.wetting_grid(time, source_t, source_p, theta, arm, wet, r0)
        if 0. < tb < horizon and tb not in time:
            old_time = time
            time = np.sort(np.r_[time, tb])
            front = np.sqrt(np.interp(time, old_time, front**2))
            front[time >= tb] = 1.
        pressure = np.maximum(np.interp(time, source_t, source_p), 0.)
        with np.errstate(over="ignore"):
            cap = W.capacity(theta, pressure)
        if not np.isfinite(cap).all():
            raise ValueError("Nonfinite capacity: unavailable prediction")
        exposure = np.zeros(len(time))
        mass, flow = liquid_only(time, cap, front, theta[4], gamma, gamma_p, pressure, exposure)
        self.time, self.front, self.tb = time, front, tb
        self.cap, self.mc, self.mass, self.flow = cap, theta[4], mass, flow
        self.dt, self.cells, self.r0 = dt, cells, r0
        self.gamma = gamma
        self.gamma_p, self.pressure, self.exposure = gamma_p, pressure, exposure
        self.prefix, self.prefix_n = None, 0
        self.column_calls = 0

    def chemistry(self, end):
        n = min(len(self.time), np.searchsorted(self.time, end, side="left")+1)
        if n <= self.prefix_n:
            return self.prefix
        r = self.r0
        exposure = np.zeros(n)
        values = W._column(self.time[:n], self.cap[:n], self.front[:n], self.mc,
            self.cells, r.phi, r.rho, r.length, r.area, r.inventory_kg, r.rate,
            r.capacity, r.diffusivity, r.length/r.native_cells, False, self.gamma,
            self.gamma_p, self.pressure[:n], exposure)
        mass, solute, flow, stored, remaining, inlet_loss, c, solid, max_c, min_c = values
        if not all(np.isfinite(x).all() for x in (mass, solute, flow, stored, remaining)):
            raise ValueError("Nonfinite R0 column: unavailable prediction")
        residual = r.inventory_kg*1000-remaining-stored-solute-inlet_loss
        self.prefix = dict(time=self.time[:n], front_fraction=self.front[:n],
            front_s=self.tb, liquid_g=mass, solute_g=solute, beverage_g=mass+solute,
            bed_flow_g_s=flow, stored_solute_g=stored, remaining_g=remaining,
            inlet_loss_g=inlet_loss, concentration=c, solid=solid,
            max_concentration=max_c, min_concentration=min_c,
            max_balance_error_g=float(np.max(np.abs(residual))), dt=self.dt, cells=self.cells)
        if self.gamma_p != 0.:
            self.prefix['pressure_exposure_bar_s'] = exposure
        self.prefix_n = n
        self.column_calls += 1
        return self.prefix

    def scored_flow(self, times, lag=0.):
        times = np.asarray(times)
        if times.min() < 0. or (times-lag).max() > self.time[-1]:
            raise ValueError("Missing flow support")
        return np.interp(times-lag, self.time, self.flow, left=0.)

    def observer(self, observation_times, lag=0., accelerate=True):
        times = np.asarray(observation_times)
        if len(times) < 31 or times[0] < 0 or times[-1] > 100. or (np.diff(times) <= 0).any():
            raise ValueError("Invalid fixed observation support")
        starts = times[times[-1]-times >= 2.]
        if not len(starts):
            raise ValueError("No confirmation support")
        last_required = max(0., times[-1]-lag)
        for end in ((20., 50., 100.) if accelerate else (100.,)):
            prediction = self.chemistry(min(end, last_required))
            use = times[times-lag <= prediction["time"][-1]]
            if len(use) < 31:
                continue
            mass, _ = W.scale_prediction(prediction, use, lag)
            flow = savgol_filter(np.gradient(mass, use), 31, 1)
            complete = len(use) == len(times)
            # A gradient needs one future sample, then the centered filter 15.
            # Trim all 16 affected samples before applying sustained_onset.
            safe = len(use) if complete else len(use)-16
            value = float(W.sustained_onset(use[:safe], mass[:safe], flow[:safe]))
            if math.isfinite(value) or complete:
                return dict(onset_s=value if math.isfinite(value) else None,
                    detected=math.isfinite(value), censor_bound_s=float(starts[-1]),
                    last_timestamp_s=float(times[-1]), samples=len(times),
                    chemistry_until_s=float(prediction["time"][-1]),
                    exact_prefix=not complete)
        raise ValueError("Prediction failed to cover fixed observer; unavailable")


def prepare(source, parameters, model, mc, dt=.02, cells=256):
    theta, arm, wet, lag = decode(parameters, model, mc)
    return Prepared(source["predict_times_s"], source["predict_pressure_bar"],
                    theta, arm, wet, dt, cells, source["predict_horizon_s"]), lag


def loss_components(flow, target, observer, observed_onset):
    return (float(np.mean((flow-target)**2))/FLOW_SCALE**2,
            W.squared_onset(observer, observed_onset)/ONSET_SCALE**2)
