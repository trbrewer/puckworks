"""PW-WETTING-SCREEN-001: fixed R0 column and frozen form A, research only.

R0 source: EWP 67bead2, espressoWholePullFoam.C (filling storage,
explicit capacity-limited release, implicit upwind transport and diffusion).
No runtime component, chemistry fit, observed-mass input, or CFD invocation.
"""
from dataclasses import dataclass
import math

import numpy as np
from scipy.signal import savgol_filter

try:
    from numba import njit
except ImportError:
    def njit(*args, **kwargs):
        return lambda function: function

from .pressure_peak_stage_b0 import sustained_onset

NOMINAL = np.array([1., 2., 3.5, 4., 5., 6., 7., 8., 9., 11., 13.])
DOMAINS = dict(k_w0=(1e-16, 1e-12), Pw=(.5, 30.), delay=(0., 100.))
ARMS = ("W0", "Z", "W1", "W2", "W2T")


@dataclass(frozen=True)
class R0:
    phi: float = .4
    mu: float = .000315
    rho: float = 965.
    length: float = .009011660896432553
    radius: float = .029
    inventory_kg: float = .02*.28
    rate: float = .15
    capacity: float = 180.
    diffusivity: float = 1e-9
    wetting_k: float = 1.77e-15
    native_cells: int = 256

    @property
    def area(self):
        return math.pi*self.radius**2

    @property
    def pore_g(self):
        return 1000*self.rho*self.area*self.length*self.phi


def capacity(theta, pressure):
    """theta=(a,Pstar,n,Pd,Mc), pressure in bar, result g/s."""
    a, pstar, n, pd, _ = theta
    pressure = np.maximum(pressure, 0.)
    return a*pd*(-np.expm1(-(pressure/pd)**n))*np.exp(-pressure/pstar)


def freeze_tuple(bank, held_condition):
    """One OUTER fold tuple, including Mc, for all its training/evaluation brews."""
    key = "DESCRIPTIVE_ALL" if held_condition is None else f"HYD-LOCO-{held_condition:.1f}"
    return np.asarray(bank[key], dtype=float).copy()


def wetting_grid(time, source_t, source_p, theta, arm, parameters, r0=R0()):
    """Three-point quadrature for the front, matching EWP's pressure convention."""
    time = np.asarray(time)
    if arm == "Z" or (arm == "W1" and parameters[0] == 0.):
        return np.ones_like(time), 0.
    if arm == "W1":
        tau = parameters[0]
        return np.sqrt(np.minimum(time/tau, 1.)), float(tau)
    dt = np.diff(time)
    middle = .5*(time[1:]+time[:-1])
    nodes = np.array([-math.sqrt(3/5), 0., math.sqrt(3/5)])
    tq = middle[:, None]+.5*dt[:, None]*nodes
    pq = np.maximum(np.interp(tq.ravel(), source_t, source_p).reshape(tq.shape), 0.)
    if arm == "W0":
        eq = capacity(theta, pq)/math.e
    elif arm in ("W2", "W2T"):
        k0, pw = parameters[:2]
        eq = 1000*r0.rho*r0.area*k0*np.exp(-pq/pw)*pq*1e5/(r0.mu*r0.length)
    elif arm == "A0":  # verification only, never a fitted screen family
        eq = 1000*r0.rho*r0.area*r0.wetting_k*pq*1e5/(r0.mu*r0.length)
    else:
        raise ValueError("Unknown wetting arm")
    exposure = np.r_[0., np.cumsum(.5*dt*(eq@np.array([5/9, 8/9, 5/9])))]
    target = r0.pore_g/2
    hits = np.flatnonzero(exposure >= target)
    tb = math.inf
    if len(hits):
        j = hits[0]
        lo, hi = time[j-1], time[j]
        # Resolve the crossing inside this interval without moving pressure time.
        initial = exposure[j-1]
        for _ in range(40):
            mid = .5*(lo+hi)
            tq0 = .5*(mid+time[j-1])+.5*(mid-time[j-1])*nodes
            pp = np.maximum(np.interp(tq0, source_t, source_p), 0.)
            if arm == "W0":
                qq = capacity(theta, pp)/math.e
            else:
                kk = r0.wetting_k if arm == "A0" else parameters[0]*np.exp(-pp/parameters[1])
                qq = 1000*r0.rho*r0.area*kk*pp*1e5/(r0.mu*r0.length)
            partial = .5*(mid-time[j-1])*np.dot(qq, [5/9, 8/9, 5/9])
            if initial+partial >= target:
                hi = mid
            else:
                lo = mid
        tb = .5*(lo+hi)
    return np.sqrt(np.minimum(exposure/target, 1.)), tb


@njit(cache=True)
def _column(time, cap, front, mc, cells, phi, rho, length, area, inventory,
            rate, cmax, diffusion, smoothing, native_time_scheme, gamma=0.):
    """Conservative R0 finite volumes; no transport during filling, as in EWP."""
    nt = len(time)
    c = np.zeros(cells)
    solid = np.full(cells, inventory/(area*length))
    old_s = np.zeros(cells)
    if front[0] == 1.:
        old_s[:] = 1.
    mass = np.zeros(nt)
    solute = np.zeros(nt)
    flow = np.zeros(nt)
    stored = np.zeros(nt)
    remaining = np.full(nt, inventory*1000.)
    loss = np.zeros(nt)
    max_c = 0.
    min_c = 0.
    dx = length/cells
    cell_volume = area*dx
    upper = np.empty(cells)
    diagonal = np.empty(cells)
    rhs = np.empty(cells)
    sr = np.empty(cells)
    slopes = np.empty(cells)
    if front[0] == 1.:
        flow[0] = cap[0]/math.e
    for j in range(1, nt):
        dt = time[j]-time[j-1]
        saturated = front[j-1] >= 1.
        water = mass[j-1]
        cup_s = solute[j-1]
        back = loss[j-1]
        if saturated:
            r = math.exp(-math.exp(-water/mc))
            if gamma != 0.:
                r *= math.exp(-gamma*water)
            if native_time_scheme:
                add = dt*cap[j]*r
                flow[j] = cap[j]*r
            else:
                mid = water+.25*dt*(cap[j-1]+cap[j])*r
                add = .5*dt*(cap[j-1]+cap[j])*math.exp(-math.exp(-mid/mc))
                if gamma != 0.:
                    add *= math.exp(-gamma*mid)
                flow[j] = cap[j]*math.exp(-math.exp(-(water+add)/mc))
                if gamma != 0.:
                    flow[j] *= math.exp(-gamma*(water+add))
            velocity = add/(dt*1000*rho*area)
            adv = velocity/dx
            diff = phi*diffusion/(dx*dx)
            for i in range(cells):
                sr[i] = min(max(rate*solid[i]*max(1.-c[i]/cmax, 0.), 0.), solid[i]/dt)
                rhs[i] = phi/dt*c[i]+sr[i]
                # Inlet fixed C=0 (half-cell diffusion), outlet zero gradient.
                diagonal[i] = phi/dt+adv+diff*(3. if i == 0 else 1. if i == cells-1 else 2.)
                upper[i] = -diff if i < cells-1 else 0.
                slopes[i] = -(adv+diff) if i > 0 else 0.
            for i in range(1, cells):
                factor = slopes[i]/diagonal[i-1]
                diagonal[i] -= factor*upper[i-1]
                rhs[i] -= factor*rhs[i-1]
            c[-1] = rhs[-1]/diagonal[-1]
            for i in range(cells-2, -1, -1):
                c[i] = (rhs[i]-upper[i]*c[i+1])/diagonal[i]
            for i in range(cells):
                solid[i] = max(solid[i]-dt*sr[i], 0.)
                old_s[i] = 1.
            water += add
            cup_s += add*c[-1]/rho
            back += dt*area*phi*diffusion*2*c[0]/dx*1000.
        else:
            for i in range(cells):
                sat = (1. if front[j] >= 1. else
                       .5*(1.+math.tanh((front[j]*length-(i+.5)*dx)/smoothing)))
                release = min(max(rate*solid[i]*sat*max(1.-c[i]/cmax, 0.), 0.), solid[i]/dt)
                dissolved = phi*old_s[i]*c[i]+dt*release
                c[i] = dissolved/(phi*sat) if sat > 1e-300 else 0.
                solid[i] = max(solid[i]-dt*release, 0.)
                old_s[i] = sat
        mass[j], solute[j], loss[j] = water, cup_s, back
        dissolved_sum = 0.
        solid_sum = 0.
        for i in range(cells):
            max_c = max(max_c, c[i])
            min_c = min(min_c, c[i])
            dissolved_sum += phi*old_s[i]*c[i]*cell_volume*1000.
            solid_sum += solid[i]*cell_volume*1000.
        stored[j], remaining[j] = dissolved_sum, solid_sum
    return mass, solute, flow, stored, remaining, loss, c, solid, max_c, min_c


def predict(source_t, source_p, theta, arm, parameters=(), *, dt=.02, cells=256,
            r0=R0(), native_time_scheme=False):
    """All inputs are pressure, frozen coefficients and fixed R0 constants."""
    if not (len(source_t) == len(source_p) >= 2 and source_t[0] <= 0 and source_t[-1] >= 100):
        raise ValueError("Predictor pressure coverage must span the fixed 0–100-s horizon")
    time = np.linspace(0., 100., round(100/dt)+1)
    front, tb = wetting_grid(time, source_t, source_p, theta, arm, parameters, r0)
    if not native_time_scheme and 0 < tb < 100. and tb not in time:
        old_time = time
        time = np.sort(np.r_[time, tb])
        front = np.sqrt(np.interp(time, old_time, front**2))
        front[time >= tb] = 1.
    pressure = np.maximum(np.interp(time, source_t, source_p), 0.)
    cap = capacity(theta, pressure)
    values = _column(time, cap, front, theta[4], cells, r0.phi, r0.rho,
                     r0.length, r0.area, r0.inventory_kg, r0.rate, r0.capacity,
                     r0.diffusivity, r0.length/r0.native_cells, native_time_scheme)
    mass, solute, flow, stored, remaining, inlet_loss, c, solid, max_c, min_c = values
    residual = r0.inventory_kg*1000-remaining-stored-solute-inlet_loss
    if not all(np.isfinite(x).all() for x in (mass, solute, flow, stored, remaining)):
        raise ValueError("Unavailable nonfinite column prediction")
    return dict(time=time, front_fraction=front, front_s=tb, liquid_g=mass,
                solute_g=solute, beverage_g=mass+solute, bed_flow_g_s=flow,
                stored_solute_g=stored, remaining_g=remaining, inlet_loss_g=inlet_loss,
                concentration=c, solid=solid, max_concentration=max_c, min_concentration=min_c,
                max_balance_error_g=float(np.max(np.abs(residual))),
                dt=dt, cells=cells)


def scale_prediction(prediction, times, lag=0.):
    """Lag BOTH beverage and scored liquid flow; never lag the bed pressure."""
    query = np.asarray(times)-lag
    if np.max(query) > prediction["time"][-1] or np.min(times) < 0.:
        raise ValueError("Missing predictor coverage; comparison unavailable, not shortened")
    beverage = np.interp(query, prediction["time"], prediction["beverage_g"], left=0.)
    liquid_flow = np.interp(query, prediction["time"], prediction["bed_flow_g_s"], left=0.)
    return beverage, liquid_flow


def observe(prediction, observation_times, lag=0.):
    """B0c on the fixed original usable timestamps; no coverage-driven censor."""
    t = np.asarray(observation_times)
    if len(t) < 31 or t[0] < 0 or t[-1] > 100 or (np.diff(t) <= 0).any():
        raise ValueError("Invalid observation-support contract")
    mass, _ = scale_prediction(prediction, t, lag)
    # The model's cup is empty throughout stable-pressure [-2, 0]. In
    # particular, Z may already have mass at the first *positive* sample;
    # subtracting that sample would silently change B0c's baseline.
    mass = mass-0.
    flow = savgol_filter(np.gradient(mass, t), 31, 1)
    value = float(sustained_onset(t, mass, flow))
    starts = t[t[-1]-t >= 2.]
    if not len(starts):
        raise ValueError("Unavailable confirmation support")
    return dict(onset_s=value if math.isfinite(value) else None,
                detected=math.isfinite(value), censor_bound_s=float(starts[-1]),
                last_timestamp_s=float(t[-1]), samples=len(t))


def squared_onset(observation, observed_onset):
    t = observation["onset_s"]
    return ((t-observed_onset)**2 if t is not None else
            max(0., observation["censor_bound_s"]-observed_onset)**2)


def median_with_censor(values, bounds):
    """A median is exact only when all possible censored ranks lie above it."""
    if any(v is None and b is None for v, b in zip(values, bounds)):
        return None, None
    lower = np.asarray([b if v is None else v for v, b in zip(values, bounds)])
    median = float(np.median(lower))
    censored = [b for v, b in zip(values, bounds) if v is None]
    known = not censored or min(censored) > np.sort(lower)[len(lower)//2]
    return median if known else None, median

