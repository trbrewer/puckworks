"""Standalone fixed-flow EJAM reduced equations; no upstream implementation imports.

Front-fitted conservative finite volumes; Eulerian grain memory is transported
on the moving coordinate mesh. Scientific and numerical limits are explicit.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.sparse import lil_matrix

from .kernel import modal_spectrum


@dataclass(frozen=True)
class Parameters:
    phi_f: float = .64
    phi_b: float = .16
    phi_l: float = .20
    varphi_lb: float = 0.
    c_f_init: float = 1.388
    c_b_init: float = 1.388
    d_sb: float = 1.
    source_id: str = "EJAM_2026_EQ76_77_TABLE2_DIMENSIONLESS"

    def __post_init__(self):
        values = (self.phi_f, self.phi_b, self.phi_l, self.varphi_lb,
                  self.c_f_init, self.c_b_init, self.d_sb)
        if not all(math.isfinite(v) for v in values):
            raise ValueError("parameters must be finite")
        if min(self.phi_f, self.phi_b, self.phi_l, self.d_sb) <= 0:
            raise ValueError("phase fractions and boulder diffusivity must be positive")
        if not math.isclose(self.phi_f + self.phi_b + self.phi_l, 1., abs_tol=1e-12):
            raise ValueError("external phase fractions must sum to one")
        if not 0 <= self.varphi_lb < 1 or min(self.c_f_init, self.c_b_init) < 0:
            raise ValueError("invalid internal pore fraction or initial concentration")
        if not self.source_id:
            raise ValueError("an explicit source/configuration identity is required")

    @property
    def phi_t(self):
        return self.phi_l + self.phi_b * self.varphi_lb

    @property
    def gamma(self):
        return self.phi_l / self.phi_t

    @property
    def beta(self):
        return self.phi_f / self.phi_t

    @property
    def delta(self):
        return self.phi_b / self.phi_t

    @property
    def q_f(self):
        return 1 / (3 * self.beta)

    @property
    def q_b(self):
        return 1 / (3 * self.delta)

    @property
    def boulder_initial_wet(self):
        return self.c_b_init + self.varphi_lb


@dataclass(frozen=True)
class Controls:
    cells: int = 128
    modes: int = 32
    front_mesh_power: float = 2.
    rtol: float = 2e-8
    atol: float = 2e-10
    max_step: float = .05

    def __post_init__(self):
        for key, lower in (("cells", 8), ("modes", 2)):
            value = getattr(self, key)
            if isinstance(value, bool) or not isinstance(value, int) or value < lower:
                raise ValueError(f"{key} must be an integer >= {lower}")
        for key in ("rtol", "atol", "max_step", "front_mesh_power"):
            value = getattr(self, key)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{key} must be finite and positive")


def front_speed(c_front: float, parameters: Parameters = Parameters()) -> float:
    """Eq.74 with the ratio multiplying only the fines-capacity term."""
    if not math.isfinite(c_front) or not 0 <= c_front <= 1:
        raise ValueError("front concentration must lie in [0,1]")
    if parameters.c_f_init <= 1:
        raise ValueError("degenerate/unsaturated fine capacity; saturated-layer law unsupported")
    numerator = 1 - c_front
    denominator = parameters.gamma * numerator + parameters.beta * (parameters.c_f_init - c_front)
    return numerator / denominator  # at C=1 denominator is positive; explicit speed zero


@dataclass(frozen=True)
class Result:
    status: str
    parameters: dict
    controls: dict
    time: list = field(default_factory=list)
    s_w: list = field(default_factory=list)
    s_d: list = field(default_factory=list)
    outlet_concentration: list = field(default_factory=list)
    cumulative_discharged_solute: list = field(default_factory=list)
    profile_z: list = field(default_factory=list)
    liquid_profiles: list = field(default_factory=list)
    fines_profiles: list = field(default_factory=list)
    boulder_mean_profiles: list = field(default_factory=list)
    events: dict = field(default_factory=dict)
    inventories: dict = field(default_factory=dict)
    diagnostics: dict = field(default_factory=dict)
    unavailable_reasons: dict = field(default_factory=dict)
    convergence_status: str = "NOT_ASSESSED_SINGLE_RUN"
    physical_validation: str = "NOT_ESTABLISHED"

    def to_dict(self) -> dict:
        result = asdict(self)
        json.dumps(result, allow_nan=False)
        return result

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False)


def _failure(status, p, controls, reason):
    return Result(status, asdict(p), asdict(controls), unavailable_reasons={"simulation": reason})


def simulate(parameters: Parameters = Parameters(), controls: Controls = Controls(), *,
             times=None, profile_z=None) -> Result:
    """Dimensionless solution. No network, fitting, dimensional defaults or global state.

    Samples are observations of dense BDF output; front arrival is root localized.
    Dry liquid profiles use zero as a no-liquid convention, not measured beverage.
    """
    p, ctrl = parameters, controls
    ts = np.asarray(np.linspace(0, 8, 161) if times is None else times, float)
    zs = np.asarray(np.linspace(0, 1, 101) if profile_z is None else profile_z, float)
    if ts.ndim != 1 or ts.size < 2 or not np.all(np.isfinite(ts)) or ts[0] < 0 or np.any(np.diff(ts) <= 0):
        raise ValueError("times must be finite, nonnegative and strictly increasing")
    if zs.ndim != 1 or not zs.size or not np.all(np.isfinite(zs)) or np.any(np.diff(zs) <= 0) or zs[0] < 0 or zs[-1] > 1:
        raise ValueError("profile_z must be a strictly increasing finite grid in [0,1]")
    if p.c_f_init <= 1 or p.boulder_initial_wet < 1:
        return _failure("UNSUPPORTED_REGIME", p, ctrl, "No supported saturated-layer initial state")
    if front_speed(0, p) > 1:
        return _failure("UNSUPPORTED_REGIME", p, ctrl, "Desaturation initially overtakes wetting")
    n = ctrl.cells
    w, rates = modal_spectrum(p.d_sb, ctrl.modes)
    k = len(w)
    a, cb0 = p.gamma + p.beta, p.boulder_initial_wet
    face = 1 - (1-np.linspace(0, 1, n+1))**ctrl.front_mesh_power
    widths = np.diff(face)
    if np.any(widths <= 0):
        raise ValueError("mesh power produces unresolved floating-point cell widths")
    xi = .5*(face[1:]+face[:-1])
    right_extrap = (face[2:]-xi[1:])/np.diff(xi)
    left_extrap = (xi[1:-1]-face[1:-2])/np.diff(xi)[1:]
    # s, liquid cell averages, modal cell averages, cumulative cup inventory.
    y0 = np.r_[0., np.zeros(n), np.full(k * n, cb0), 0.]
    size = len(y0)
    pattern = lil_matrix((size, size), dtype=int)
    pattern[:, 0] = 1
    pattern[:, n-1:n+1] = 1
    for j in range(n):
        pattern[1+j, 1+max(0, j-2):2+j] = 1
        for m in range(k):
            at = 1 + n + m*n + j
            pattern[1+j, at] = 1
            pattern[at, 1+j] = 1
            pattern[at, at:1+n+m*n+min(n, j+3)] = 1
    pattern = pattern.tocsr()

    def rhs(t, y, *, fixed, dripping):
        s, c, x = y[0], y[1:1+n], y[1+n:-1].reshape(k, n)
        cf = np.r_[0., 2*c[0], c[1:]+right_extrap*(c[1:]-c[:-1])]
        C = cf[-1]
        # Newton iterates are not accepted physical states; validate accepted output below.
        v = 0. if fixed else (1-C)/(p.gamma*(1-C)+p.beta*(p.c_f_init-C))
        G = p.delta * np.sum((w*rates)[:, None]*(x-c), axis=0)
        out = C if fixed else float(dripping)
        if s == 0:
            return np.r_[v, G[0]*v*xi, (-rates[:, None]*cb0*(1-xi)).ravel(), out]
        dc = (-np.diff((1-a*face*v)*cf)/widths+s*G-v*a*c)/(s*a)
        xf = np.c_[x[:, 0], x[:, 1:-1]+left_extrap*(x[:, 1:-1]-x[:, 2:]), 2*x[:, -1]-cb0, np.full(k, cb0)]
        dx = v/s*(np.diff(face*xf, axis=1)/widths-x)-rates[:, None]*(x-c)
        return np.r_[v, dc, dx.ravel(), out]

    def arrival(t, y):
        return y[0]-1

    arrival.terminal = True
    arrival.direction = 1

    def overtaking(t, y):
        return y[0]/t-1 if t > 0 else front_speed(0, p)-1

    overtaking.terminal = True
    overtaking.direction = 1
    segments = []
    state, start, fixed, event_time = y0, 0., False, None
    horizon = float(ts[-1])
    for end in sorted(set([min(1., horizon), horizon])):
        while start < end:
            r = solve_ivp(lambda t, y: rhs(t, y, fixed=fixed, dripping=start >= 1),
                          (start, end), state, method="BDF", rtol=ctrl.rtol, atol=ctrl.atol,
                          max_step=ctrl.max_step, jac_sparsity=pattern, dense_output=True,
                          events=None if fixed else (arrival, overtaking))
            if not r.success:
                return _failure("NUMERICAL_FAILURE", p, ctrl, r.message)
            segments.append((start, float(r.t[-1]), fixed, r))
            start, state = float(r.t[-1]), r.y[:, -1]
            if not fixed and len(r.t_events[0]):
                event_time = start
                fixed = True
                # The localized event already has s=1 to solver precision; no projection.
            elif not fixed and len(r.t_events[1]):
                return _failure("UNSUPPORTED_REGIME", p, ctrl, "Desaturation overtook wetting before outlet exit")

    def evaluate(t):
        for lo, hi, is_fixed, r in segments:
            if lo <= t <= hi:
                return r.sol(t), is_fixed
        raise RuntimeError("time outside integrated domain")

    def crossing(z):
        if z == 0:
            return 0.
        if z == 1 and event_time is not None:
            return event_time
        for lo, hi, is_fixed, r in segments:
            if not is_fixed and r.y[0, 0] <= z <= r.y[0, -1]:
                return float(brentq(lambda t: r.sol(t)[0]-z, lo, hi, xtol=1e-12))
        return None

    wet, desat, outlet, cup, cprof, fprof, bprof = [], [], [], [], [], [], []
    liquid_inv, fine_inv, boulder_inv, residual = [], [], [], []
    initial = p.beta*p.c_f_init + p.delta*p.c_b_init
    for t in ts:
        y, is_fixed = evaluate(float(t))
        s, c, x = float(y[0]), y[1:n+1], y[n+1:-1].reshape(k, n)
        B = w @ x
        sw, C = min(float(t), 1.), float(c[-1]+right_extrap[-1]*(c[-1]-c[-2]))
        ce = 0. if t < 1 else (C if event_time is not None and t >= event_time else 1.)
        cz = np.where(zs <= sw, 1., 0.)
        fz, bz = np.full(zs.size, p.c_f_init), np.where(zs <= sw, cb0, p.c_b_init)
        active = zs < s
        if s > 0:
            cz[active] = np.interp(zs[active], np.r_[0., s*xi, s], np.r_[0., c, C])
            fz[active] = cz[active]
            bz[active] = np.interp(zs[active], s*xi, B)
        cz[zs == 0] = 0.
        if event_time is not None and t >= event_time:
            cz[zs == 1] = C
            fz[zs == 1] = C
            bz[zs == 1] = B[-1]
        li = p.gamma*(s*float(widths @ c)+sw-s)
        fi = p.beta*(s*float(widths @ c)+(1-s)*p.c_f_init)
        bi = p.delta*(s*float(widths @ B)+(sw-s)*cb0+(1-sw)*p.c_b_init)
        wet.append(sw); desat.append(s); outlet.append(ce); cup.append(float(y[-1]))
        cprof.append(cz.tolist()); fprof.append(fz.tolist()); bprof.append(bz.tolist())
        liquid_inv.append(li); fine_inv.append(fi); boulder_inv.append(bi)
        residual.append((li+fi+bi+float(y[-1])-initial)/initial)
    aqueous_states = [np.vstack((r.y[1:n+1],
                       r.y[n]+right_extrap[-1]*(r.y[n]-r.y[n-1])))
                      for _, _, _, r in segments]
    min_c = min(float(c.min()) for c in aqueous_states)
    max_c = max(float(c.max()) for c in aqueous_states)
    min_B = min(float(np.min(np.einsum('k,knt->nt', w, r.y[n+1:-1].reshape(k, n, -1))))
                for _, _, _, r in segments)
    bound = min_c >= -1e-8 and max_c <= 1+1e-8 and min_B >= -1e-8
    mass_ok = max(abs(v) for v in residual) <= 1e-6
    unavailable = {}
    if event_time is None:
        unavailable["desaturation_exit"] = "Right-censored at run horizon; no localized arrival"
    if horizon < 1:
        unavailable["first_drip"] = "Run horizon precedes prescribed first drip"
    if not bound:
        unavailable["boundedness"] = "Numerical bound budget exceeded; no concentrations clipped"
    if not mass_ok:
        unavailable["conservation"] = "Normalized conservation budget exceeded; no mass correction"
    return Result(
        "COMPLETED" if bound and mass_ok else "NUMERICAL_VERIFICATION_FAILED", asdict(p), asdict(ctrl),
        ts.tolist(), wet, desat, outlet, cup, zs.tolist(), cprof, fprof, bprof,
        {"first_drip": 1. if horizon >= 1 else None, "prescribed_first_drip": 1.,
         "first_drip_role": "model-derived under prescribed fixed flow",
         "desaturation_exit": event_time, "saturation_plateau_end": event_time,
         "saturation_plateau_duration": max(event_time-1, 0.) if event_time is not None else None,
         "wetting_at_profile_z": [float(z) if z <= horizon else None for z in zs],
         "desaturation_at_profile_z": [crossing(float(z)) for z in zs]},
        {"normalization": "phi_T * bed_depth * bed_area * c_sat", "initial": initial,
         "external_liquid": liquid_inv, "fines": fine_inv, "boulders_including_pores": boulder_inv,
         "normalized_residual": residual},
        {"aqueous_min": min_c, "aqueous_max": max_c, "boulder_mean_min": min_B,
         "max_normalized_conservation_residual": max(abs(v) for v in residual),
         "q_f": p.q_f, "q_b": p.q_b, "phi_t": p.phi_t,
         "nfev": sum(r.nfev for _, _, _, r in segments),
         "method": "conservative front-fitted finite volumes, BDF, spherical relaxation modes",
         "dry_profile_convention": "zero denotes absent mobile liquid before wetting",
         "initial_flux": "integrable singularity regularized by explicit finite tail mode"},
        unavailable)
