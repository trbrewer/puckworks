"""Independent FV concentration balances and test-only continuum benchmark.

Shares only unchanged source parameters/closures/geometry with the candidate.
No candidate generator/RHS calls or basis-vector construction of that generator.
Source-derived results: Pannusch et al., DOI 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import expm_multiply
import math
from puckworks.models.pannusch2024 import solver as ps, closures as pc


def operator_factory(solute, grind, n):
    sp = dict(ps._solute_params()[solute])
    psi, d2 = ps.GRINDS[grind]["psi"], ps.GRINDS[grind]["d_s2"]
    as1, as2 = psi*(1-ps.ALPHA_L), (1-psi)*(1-ps.ALPHA_L)
    d32 = 6/(psi*6/ps.D1_FINE+(1-psi)*6/d2)
    adv = 1./(ps.ACS*ps.ALPHA_L*(ps.L/n))
    transport = lil_matrix((3*n+1, 3*n+1))
    liquid_fine, fine_liquid, liquid_coarse, coarse_liquid = [lil_matrix(transport.shape) for _ in range(4)]
    for j in range(n):
        transport[j, j] = -adv
        if j:
            transport[j, j-1] = adv
        # Direct concentration balances: capacities cancel differently in each phase.
        liquid_fine[j, j] = -as1/ps.ALPHA_L
        liquid_fine[n+j, j] = 1
        fine_liquid[j, n+j] = as1/ps.ALPHA_L
        fine_liquid[n+j, n+j] = -1
        liquid_coarse[j, j] = -ps.PHI_V2*as2/ps.ALPHA_L
        liquid_coarse[2*n+j, j] = 1
        coarse_liquid[j, 2*n+j] = ps.PHI_V2*as2/ps.ALPHA_L
        coarse_liquid[2*n+j, 2*n+j] = -1
    transport[-1, n-1] = 1.
    base, lf, fl, lc, cl = [a.tocsc() for a in (transport, liquid_fine, fine_liquid, liquid_coarse, coarse_liquid)]
    def operator(T, Q):
        K = float(pc.vant_hoff_K(T, sp["K_ref"], sp["gamma"]))
        k1 = 6*float(pc.sherwood_h(T, Q/ps.ACS, sp["A1"], sp["B1"], solute, d32))/ps.D1_FINE
        k2 = 6*float(pc.sherwood_h(T, Q/ps.ACS, sp["A2"], sp["B2"], solute, d32))/(ps.PHI_V2*d2)
        return Q*base+k1*lf+(K*k1)*fl+k2*lc+(K*k2)*cl
    return operator


def initial_and_inventory(T, solute, grind, n):
    p = ps._solute_params()[solute]
    K = float(pc.vant_hoff_K(T, p["K_ref"], p["gamma"]))
    psi = ps.GRINDS[grind]["psi"]
    initial = np.r_[np.full(n, K*p["c_s0"]), np.full(2*n, p["c_s0"]), 0.]
    M0 = ps.ACS*ps.L*p["c_s0"]*(ps.ALPHA_L*K+psi*(1-ps.ALPHA_L)+ps.PHI_V2*(1-psi)*(1-ps.ALPHA_L))
    return initial, M0


def raw_history(history):
    if isinstance(history, dict):
        return history
    return dict(times_s=history.times_s, kind=history.kind,
                values=history.temperatures_K if hasattr(history, 'temperatures_K') else history.flows_m3_s)


def value(history, t, *, interval=None):
    """Independent clock lookup; never calls candidate history methods."""
    h = raw_history(history)
    knots, vals = h['times_s'], h['values']
    if not knots[0] <= t <= knots[-1]:
        raise ValueError('REFERENCE_HISTORY_SUPPORT')
    i = interval
    if i is None:
        i = next((j for j in range(len(knots)-1) if t < knots[j+1]), len(knots)-2)
    if h['kind'] == 'constant':
        return vals[i]
    u = (t-knots[i])/(knots[i+1]-knots[i])
    return (1-u)*vals[i]+u*vals[i+1]


def segments(temperature, flow, span):
    """Independent set union and interval ownership; no candidate segmentation."""
    th, qh = raw_history(temperature), raw_history(flow)
    a, b = span
    if any(h['times_s'][0] > a or h['times_s'][-1] < b for h in (th, qh)):
        raise ValueError('REFERENCE_HISTORY_SUPPORT')
    edges = sorted({a, b, *(t for h in (th, qh) for t in h['times_s'] if a < t < b)})
    out = []
    for left, right in zip(edges, edges[1:]):
        mid = (left+right)/2
        ti, qi = [next(i for i in range(len(h['times_s'])-1)
                      if h['times_s'][i] <= mid < h['times_s'][i+1]) for h in (th, qh)]
        out.append((left, right, ti, qi))
    return out


def volume(flow, a, b):
    """Independent direct polynomial integration on locally clipped intervals."""
    h = raw_history(flow)
    if not h['times_s'][0] <= a <= b <= h['times_s'][-1]:
        raise ValueError('REFERENCE_VOLUME_SUPPORT')
    terms = []
    for i, (l, r) in enumerate(zip(h['times_s'], h['times_s'][1:])):
        lo, hi = max(a, l), min(b, r)
        if hi <= lo:
            continue
        slope = 0 if h['kind'] == 'constant' else (h['values'][i+1]-h['values'][i])/(r-l)
        # Use q(lo)*dt + slope*dt²/2, not the candidate trapezoid formula.
        dt = hi-lo
        terms.append((h['values'][i]+slope*(lo-l))*dt+slope*dt*dt/2)
    return math.fsum(terms)


def time_for_volume(flow, target):
    """Stable analytic quadratic inverse, no simulated outlet or clock inference."""
    h = raw_history(flow)
    remaining = target
    for i, (a, b) in enumerate(zip(h['times_s'], h['times_s'][1:])):
        whole = volume(h, a, b)
        if remaining <= whole:
            q0 = h['values'][i]
            slope = 0. if h['kind'] == 'constant' else (h['values'][i+1]-q0)/(b-a)
            dt = remaining/q0 if slope == 0 else 2*remaining/(q0+math.sqrt(q0*q0+2*slope*remaining))
            return a+dt
        remaining -= whole
    raise ValueError('REFERENCE_TARGET_VOLUME_OUTSIDE_SUPPORT')


def reference(temperature, flow, solute, grind, n, observations, *, t_span_s,
              method='Radau', rtol=2e-12, scaled_atol=2e-14, max_step_s=.02,
              initial_fields=None):
    times = np.asarray(observations)
    t0, tf = t_span_s
    y, M0 = initial_and_inventory(value(temperature, t0), solute, grind, n)
    Cstar = ps._solute_params()[solute]['c_s0']
    if initial_fields is not None:
        # 004 additive input only. The historical 003 default path is unchanged.
        c = np.asarray(initial_fields)
        if c.shape != (3, n) or not np.isrealobj(c) or not np.isfinite(c).all() or np.any(c < 0):
            raise ValueError('INVALID_REFERENCE_INITIAL_FIELDS')
        psi = ps.GRINDS[grind]['psi']
        capacities = ps.ACS*(ps.L/n)*np.array([
            ps.ALPHA_L, psi*(1-ps.ALPHA_L), ps.PHI_V2*(1-psi)*(1-ps.ALPHA_L)])
        M0 = math.fsum((c*capacities[:, None]).ravel())
        Cstar = float(np.max(c))
        if M0 <= 0 or Cstar <= 0:
            raise ValueError('REFERENCE_REQUIRES_POSITIVE_INITIAL_INVENTORY')
        y = np.r_[c.ravel(), 0.]
    atol = np.r_[np.full(3*n, scaled_atol*Cstar), scaled_atol*M0]
    values = np.empty((len(times), len(y)))
    values[times == t0] = y
    checked_t, checked_y, records = [float(t0)], [y.copy()], []
    assemble = operator_factory(solute, grind, n)
    for a, b, ti, qi in segments(temperature, flow, t_span_s):
        def operator(t):
            return assemble(value(temperature, t, interval=ti), value(flow, t, interval=qi))
        indices = np.flatnonzero((times > a) & (times <= b))
        if method == 'ORDERED':
            if any(raw_history(h)['kind'] != 'constant' for h in (temperature, flow)):
                raise ValueError('ORDERED_REQUIRES_STEP_HISTORIES')
            A = operator((a+b)/2)
            previous = a
            for t in np.unique(np.r_[times[indices], b]):
                y = expm_multiply(A*(t-previous), y, traceA=float(A.diagonal().sum())*(t-previous))
                if t in times:
                    values[np.flatnonzero(times == t)[0]] = y
                checked_t.append(float(t)); checked_y.append(y.copy()); previous = t
            records.append(dict(span_s=[a, b], method='independent ordered concentration exponentials'))
        elif method == 'Radau':
            result = solve_ivp(lambda t, x: operator(t)@x, (a, b), y, method='Radau',
                jac=lambda t, x: operator(t), atol=atol, rtol=rtol, max_step=max_step_s, dense_output=True)
            if not result.success or result.t[-1] != b or not np.isfinite(result.y).all():
                raise RuntimeError('INDEPENDENT_RADAU_INCOMPLETE')
            if len(indices):
                values[indices] = result.sol(times[indices]).T
            diagnostic = np.unique(np.r_[result.t[1:], times[indices]])
            checked_t.extend(diagnostic); checked_y.extend(result.sol(diagnostic).T)
            y = result.y[:, -1].copy()
            records.append(dict(span_s=[a, b], accepted_steps=len(result.t)-1,
                                nfev=result.nfev, njev=result.njev, nlu=result.nlu))
        else:
            raise ValueError('UNKNOWN_REFERENCE_METHOD')
    if not np.isfinite(values).all():
        raise RuntimeError('NONFINITE_REFERENCE_OBSERVATIONS')
    return values, np.asarray(checked_t), np.asarray(checked_y), records


def stateful_u_fields(solute, n):
    """004 U family: independently integrated polynomial cell averages."""
    edges = np.arange(n+1, dtype=float)/n
    left, right = edges[:-1], edges[1:]
    avg_x = (right+left)/2
    avg_x2 = (right*right+right*left+left*left)/3
    return ps._solute_params()[solute]['c_s0']*np.array([
        .15+.25*avg_x, .85-.55*avg_x, .10+.45*avg_x2])


def primary_times(temperature, flow, span, h):
    return np.unique(np.concatenate([np.linspace(a,b,int(np.ceil((b-a)/h))+1)
                                    for a,b,_,_ in segments(temperature,flow,span)]))


def passive_exact(n, times, flow, C0=1.):
    edges = np.linspace(0, ps.L, n+1)
    def primitive(u):
        z = np.minimum(np.maximum(u, 0.), ps.L)
        return z/2-ps.L*np.sin(2*np.pi*z/ps.L)/(4*np.pi)
    shifts = [volume(flow, 0, t)/(ps.ACS*ps.ALPHA_L) for t in times]
    avg = np.array([C0*np.diff(primitive(edges-s))/(ps.L/n) for s in shifts])
    M0 = ps.ACS*ps.ALPHA_L*C0*ps.L/2
    outlet = np.array([ps.ACS*ps.ALPHA_L*C0*(ps.L/2-primitive(ps.L-s)) for s in shifts])
    return avg, outlet, M0
