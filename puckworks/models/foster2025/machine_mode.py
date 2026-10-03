"""Foster et al. (2025), dimensional Eqs. 23–29, finite machine trajectory.

Complements foster2025.infiltration (which consumes a measured P(t)). The
published fine-grind case is source-curve reproduction, not physical validation.
Reported time = model time + fitted t_shift. See docs/cards/foster2025_2.md and
MODEL-FOSTER2025-POSTSAT-001. Water flows/inventories carry no solute meaning.
"""
from dataclasses import dataclass, fields, replace

import numpy as np
from scipy.integrate import solve_ivp


@dataclass
class FosterParams:
    """Table I (fine-grind fit). SI units; R_f is Pa*s/m^3."""
    L: float = 9.975e-3
    H0: float = 7.8e-3
    A: float = 0.002734
    mu: float = 0.315e-3
    rho: float = 965.0
    p_a: float = 1.01325e5
    Q_m: float = 317e-6 / 60
    R_f: float = 3.83e6
    g: float = 9.81
    p_c: float = 0.1e5
    p_m: float = 15e5
    beta: float = 1.226
    k: float = 2.97e-15
    phi_T: float = 0.322
    t_shift: float = 0.796


class UnsupportedRegime(ValueError):
    """Parameters or an internal state leave the supported source branch."""


class UnavailableObservation(ValueError):
    """A requested observation is outside support, or the solve failed."""


_ROUNDOFF = 64 * np.finfo(float).eps
_GL_X, _GL_W = np.polynomial.legendre.leggauss(8)


def validate_parameters(p):
    """Support ordinary ponding then saturation, with the source pump branch."""
    if not all(np.isfinite(getattr(p, f.name)) for f in fields(p)):
        raise UnsupportedRegime("parameters must be finite")
    if any(getattr(p, k) <= 0 for k in
           ("L", "H0", "A", "mu", "rho", "p_a", "Q_m", "g", "k")):
        raise UnsupportedRegime("dimensions, viscosity, density and permeability must be positive")
    if not 0 < p.phi_T < 1:
        raise UnsupportedRegime("require 0 < phi_T < 1")
    if p.p_m <= p.p_a or p.R_f < 0 or p.beta < 1 or p.p_c < 0:
        raise UnsupportedRegime("require p_m>p_a, R_f>=0, beta>=1, p_c>=0")
    if p.beta * p.p_a >= p.p_m:
        raise UnsupportedRegime("no positive initial pump flow")


def p_h(H, p):
    """Absolute headspace pressure [Pa], source Eq. 5 (not gauge pressure)."""
    H = np.asarray(H)
    if (not np.all(np.isfinite(H)) or not np.isfinite(p.H0) or p.H0 <= 0
            or not np.isfinite(p.p_a * p.beta) or p.p_a * p.beta <= 0
            or np.any(H < -_ROUNDOFF * p.H0) or np.any(H >= p.H0)):
        raise UnsupportedRegime("invalid headspace height or gas parameters")
    return p.p_a * p.H0 * p.beta / (p.H0 - H)


def Q_pump(H, p):
    """Admissible source Eq. 7 positive root [m^3/s]; no state clipping."""
    if (not all(np.isfinite(x) for x in (p.p_m, p.p_a, p.Q_m, p.R_f))
            or p.p_m <= p.p_a or p.Q_m <= 0 or p.R_f < 0):
        raise UnsupportedRegime("invalid pump characteristic")
    pressure = p_h(H, p)
    H_stop = p.H0 * (1 - p.beta * p.p_a / p.p_m)
    if np.any(np.asarray(H) > H_stop) or np.any(pressure > p.p_m):
        raise UnsupportedRegime("headspace exceeds pump shutoff (H_stop)")
    a = (p.p_m - p.p_a) / p.Q_m ** 2
    disc = p.R_f ** 2 + 4 * a * (p.p_m - pressure)
    if not np.all(np.isfinite(disc)) or np.any(disc < 0):
        raise UnsupportedRegime("pump root is not finite and real")
    # Preserve the shipped algebra on the qualified earlier-stage trajectory.
    q = -p.Q_m ** 2 / (2 * (p.p_m - p.p_a)) * (p.R_f - np.sqrt(disc))
    if not np.all(np.isfinite(q)) or np.any(q < 0) or np.any(q > p.Q_m):
        raise UnsupportedRegime("pump flow outside source range [0,Q_m]")
    return q


def f_bed(H, s, p):
    """Superficial bed-inlet velocity [m/s], Eq. 16, including p_c at s=L."""
    if not np.all(np.isfinite(s)) or np.any(np.asarray(s) <= 0):
        raise UnsupportedRegime("Darcy front length must be positive and finite")
    return -(p.k / (p.mu * s)) * (p.p_a - p.p_c - p_h(H, p) - p.rho * p.g * (H + s))


def ponding(p=None):
    """(s_p [m], t_p_model [s], fixed Q_p [m^3/s]), source Eqs. 24–25."""
    p = p or FosterParams()
    validate_parameters(p)
    Q_p = float(Q_pump(0.0, p))
    denominator = p.k * p.A * p.rho * p.g - p.mu * Q_p
    if denominator >= 0 or Q_p <= 0:
        raise UnsupportedRegime("unsupported absent/degenerate ponding")
    s_p = p.k * p.A * (p.p_a * (1 - p.beta) - p.p_c) / denominator
    t_p = p.A * p.phi_T * s_p / Q_p
    if not (0 < s_p < p.L and np.isfinite(t_p) and t_p > 0):
        raise UnsupportedRegime("require nondegenerate ordering 0<s_p<L")
    return s_p, t_p, Q_p


def _bed_checked(H, s, p, Q_p):
    f = f_bed(H, s, p)
    if (not np.all(np.isfinite(f)) or np.any(f < 0)
            or np.any(p.A * f > Q_p * (1 + _ROUNDOFF))):
        raise UnsupportedRegime("source Eq. 18 cap and staged balance disagree")
    return f


def _flow_integral(segment, left, right, p, Q_p, saturated):
    """Gauss integration of each flow, never a storage complement."""
    mid = (np.asarray(left) + np.asarray(right)) / 2
    half = (np.asarray(right) - np.asarray(left)) / 2
    times = mid[..., None] + half[..., None] * _GL_X
    state = segment.sol(times.ravel())
    H = state[0] if saturated else state[1]
    qp = Q_pump(H, p).reshape(times.shape)
    qb = p.A * _bed_checked(H, p.L if saturated else state[0], p, Q_p)
    qo = qb.reshape(times.shape) if saturated else np.zeros_like(qp)
    return np.stack((half * (qp @ _GL_W), half * (qo @ _GL_W)), axis=-1)


def _volume_table(segment, p, Q_p, saturated):
    increments = _flow_integral(segment, segment.t[:-1], segment.t[1:], p, Q_p, saturated)
    return np.vstack((np.zeros(2), np.cumsum(increments, axis=0)))


def solve(p=None, *, horizon_s=30.0, rtol=1e-9, atol_scale=1e-11, max_step=0.005):
    """Integrate through a finite *model-time* horizon (default 30 s).

    ``sol`` retains the two-state (s,H) pre-saturation result; ``post_sol`` is
    the scalar H segment starting at the actual saturation event. Unreached
    t_s is None. Failed solves retain labeled diagnostics but observers reject
    them, even on partial support. Successful early horizons are observable.
    atol_scale multiplies L/H0 for component-scaled absolute tolerances.
    ``metadata`` and ``observe`` are finite JSON-compatible reporting surfaces.
    """
    p = replace(p or FosterParams())  # caller mutation must not change a solved trajectory
    s_p, t_p, Q_p = ponding(p)
    if not np.isfinite(horizon_s) or horizon_s < 0:
        raise ValueError("horizon_s must be finite and nonnegative")
    if any(not np.isfinite(v) or v <= 0 for v in (rtol, atol_scale, max_step)):
        raise ValueError("solver tolerances and max_step must be finite and positive")
    r = dict(sol=None, post_sol=None, s_p=s_p, t_p=t_p, t_s=None, Q_p=Q_p, p=p,
             requested_horizon_s=float(horizon_s), actual_support_s=[0.0, float(min(t_p, horizon_s))],
             success=True, status="SUCCESS", message="requested horizon completed",
             settings=dict(method="LSODA", rtol=rtol, atol_scale=atol_scale, max_step=max_step))
    if horizon_s <= t_p:
        return r

    def rhs(t, y):
        s, H = y
        f = _bed_checked(H, s, p, Q_p)
        return [f / p.phi_T, float(Q_pump(H, p)) / p.A - f]

    def hit_L(t, y):
        return y[0] - p.L
    hit_L.terminal = True
    hit_L.direction = 1
    try:
        sol = solve_ivp(rhs, [t_p, horizon_s], [s_p, 0.0], method="LSODA", events=hit_L,
                        rtol=rtol, atol=atol_scale * np.array([p.L, p.H0]),
                        max_step=max_step, dense_output=True)
        r["sol"] = sol
        r["actual_support_s"][1] = float(sol.t[-1])
        if not sol.success:
            r.update(success=False, status="NUMERICAL_FAILURE", message=str(sol.message))
            return r
        r["_pre_volumes"] = _volume_table(sol, p, Q_p, False)
        if len(sol.t_events[0]) == 0:
            return r
        r["t_s"] = ts = float(sol.t_events[0][0])
        if ts < horizon_s:
            Hs = float(sol.y_events[0][0][1])

            def post_rhs(t, y):
                H = y[0]
                return [float(Q_pump(H, p)) / p.A - _bed_checked(H, p.L, p, Q_p)]

            r["post_entry_derivative_m_s"] = float(post_rhs(ts, [Hs])[0])
            post = solve_ivp(post_rhs, [ts, horizon_s], [Hs], method="LSODA",
                             rtol=rtol, atol=atol_scale * p.H0,
                             max_step=max_step, dense_output=True)
            r["post_sol"] = post
            r["actual_support_s"][1] = float(post.t[-1])
            if not post.success:
                r.update(success=False, status="NUMERICAL_FAILURE", message=str(post.message))
                return r
            r["_post_volumes"] = _volume_table(post, p, Q_p, True)
    except UnsupportedRegime as exc:
        r.update(success=False, status="UNSUPPORTED_DOMAIN", message=str(exc))
    return r


def require_success(r):
    """Fail closed for every live consumer, regardless of retained finite samples."""
    if not r["success"]:
        raise UnavailableObservation(f"{r['status']}: {r['message']}")


def _check_time(t_model, r):
    require_success(r)
    if not np.isfinite(t_model) or not 0 <= t_model <= r["actual_support_s"][1]:
        raise UnavailableObservation("model time outside actual integrated support")


def _reported_to_model(t_reported, r):
    require_success(r)
    shift = r["p"].t_shift
    if (not np.isfinite(t_reported)
            or not shift <= t_reported <= r["actual_support_s"][1] + shift):
        raise UnavailableObservation("reported time outside actual integrated support")
    # Only remove floating-point cancellation at inclusive clock endpoints.
    if t_reported == shift:
        return 0.0
    if t_reported == r["actual_support_s"][1] + shift:
        return r["actual_support_s"][1]
    return t_reported - shift


def _sH(t_model, r):
    """(s,H) [m] on finite model-time support, with exact saturated s=L."""
    _check_time(t_model, r)
    p = r["p"]
    if t_model <= r["t_p"]:
        return r["Q_p"] * t_model / (p.A * p.phi_T), 0.0
    if r["t_s"] is not None and t_model >= r["t_s"]:
        H = (r["post_sol"].sol(t_model)[0] if r["post_sol"] is not None
             else r["sol"].y_events[0][0][1])
        return p.L, float(H)
    s, H = r["sol"].sol(t_model)
    return float(s), float(H)


def _segment_volumes(t, r, saturated):
    segment = r["post_sol"] if saturated else r["sol"]
    table = r["_post_volumes"] if saturated else r["_pre_volumes"]
    i = int(np.searchsorted(segment.t, t, side="right") - 1)
    return table[i] + _flow_integral(segment, segment.t[i], t, r["p"], r["Q_p"], saturated)


def metadata(r):
    """JSON-safe status/support, including unavailable events as null."""
    end = r["actual_support_s"][1]
    shift = r["p"].t_shift
    return dict(numerical_status=r["status"], success=r["success"], message=r["message"],
                requested_model_horizon_s=r["requested_horizon_s"],
                actual_model_support_s=list(r["actual_support_s"]),
                actual_reported_support_s=[shift, end + shift],
                ponding_model_s=r["t_p"] if end >= r["t_p"] else None,
                saturation_model_s=r["t_s"],
                event_status=dict(ponding="REACHED" if end >= r["t_p"] else "UNREACHED",
                                  saturation="REACHED" if r["t_s"] is not None else "UNREACHED"),
                post_saturation_status=("INTEGRATED" if r["success"] and r["post_sol"] is not None
                                        else "NOT_QUALIFIED"),
                validation_ceiling="source_curve_reproduction",
                PHYSICAL_VALIDATION="NOT_ESTABLISHED")


def observe(t_model, r=None):
    """SI-labelled hydraulic observations; no pre-start or terminal extension."""
    r = r or solve()
    s, H = _sH(t_model, r)
    p = r["p"]
    pump = float(Q_pump(H, p))
    bed = r["Q_p"] if t_model <= r["t_p"] else float(p.A * _bed_checked(H, s, p, r["Q_p"]))
    saturated = r["t_s"] is not None and t_model >= r["t_s"]
    volumes = np.array([r["Q_p"] * min(t_model, r["t_p"]), 0.0])
    if t_model > r["t_p"]:
        volumes += _segment_volumes(min(t_model, r["t_s"]) if saturated else t_model, r, False)
    if saturated and r["post_sol"] is not None:
        volumes += _segment_volumes(t_model, r, True)
    return dict(model_time_s=float(t_model), reported_time_s=float(t_model + p.t_shift),
                s_m=s, H_m=H, headspace_pressure_absolute_Pa=float(p_h(H, p)),
                Q_pump_m3_s=pump, Q_bed_in_m3_s=bed, Q_out_m3_s=bed if saturated else 0.0,
                V_pump_m3=float(volumes[0]), V_out_m3=float(volumes[1]),
                V_storage_m3=float(p.A * (H + p.phi_T * s)), **metadata(r))


def front_headspace_mm(t_exp, r=None):
    """(s,H) [mm] at reported time; t_exp=model+t_shift, applied once."""
    r = r or solve()
    s, H = _sH(_reported_to_model(t_exp, r), r)
    return s * 1e3, H * 1e3


def bed_flow_norm(t_exp, r=None):
    """Figure 15 bed INFLOW / Q_m, source Eq. 18 with FIXED Q_p cap."""
    r = r or solve()
    tm = _reported_to_model(t_exp, r)
    p = r["p"]
    s, H = _sH(tm, r)
    if tm <= r["t_p"]:
        return r["Q_p"] / p.Q_m
    return float(min(r["Q_p"], _bed_checked(H, s, p, r["Q_p"]) * p.A) / p.Q_m)


def flow_minimum(r=None):
    """(Q_min/Q_m, reported time), restricted to ponding THROUGH saturation."""
    r = r or solve()
    require_success(r)
    if r["t_s"] is None:
        raise UnavailableObservation("flow_minimum requires reached saturation")
    t = np.linspace(r["t_p"], r["t_s"], 400) + r["p"].t_shift
    q = np.array([bed_flow_norm(ti, r) for ti in t])
    i = int(np.argmin(q))
    return float(q[i]), float(t[i])


def reported_times(p=None, *, horizon_s=30.0):
    """Reached ponding/saturation in reported seconds; unreached event is None."""
    r = solve(p, horizon_s=horizon_s)
    require_success(r)
    m = metadata(r)
    return tuple(None if m[k] is None else m[k] + r["p"].t_shift
                 for k in ("ponding_model_s", "saturation_model_s"))
