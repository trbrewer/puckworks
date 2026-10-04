"""Independent FV concentration balances and test-only continuum benchmark.

Shares only unchanged source parameters/closures/geometry with the candidate.
No candidate generator/RHS calls or basis-vector construction of that generator.
Source-derived results: Pannusch et al., DOI 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import lil_matrix
from puckworks.models.pannusch2024 import solver as ps, closures as pc


def operator_factory(Q, solute, grind, n):
    sp = dict(ps._solute_params()[solute])
    psi, d2 = ps.GRINDS[grind]["psi"], ps.GRINDS[grind]["d_s2"]
    as1, as2 = psi*(1-ps.ALPHA_L), (1-psi)*(1-ps.ALPHA_L)
    d32 = 6/(psi*6/ps.D1_FINE+(1-psi)*6/d2)
    adv = Q/(ps.ACS*ps.ALPHA_L*(ps.L/n))
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
    transport[-1, n-1] = Q
    base, lf, fl, lc, cl = [a.tocsc() for a in (transport, liquid_fine, fine_liquid, liquid_coarse, coarse_liquid)]
    def operator(T):
        K = float(pc.vant_hoff_K(T, sp["K_ref"], sp["gamma"]))
        k1 = 6*float(pc.sherwood_h(T, Q/ps.ACS, sp["A1"], sp["B1"], solute, d32))/ps.D1_FINE
        k2 = 6*float(pc.sherwood_h(T, Q/ps.ACS, sp["A2"], sp["B2"], solute, d32))/(ps.PHI_V2*d2)
        return base+k1*lf+(K*k1)*fl+k2*lc+(K*k2)*cl
    return operator


def initial_and_inventory(T, solute, grind, n):
    p = ps._solute_params()[solute]
    K = float(pc.vant_hoff_K(T, p["K_ref"], p["gamma"]))
    psi = ps.GRINDS[grind]["psi"]
    initial = np.r_[np.full(n, K*p["c_s0"]), np.full(2*n, p["c_s0"]), 0.]
    M0 = ps.ACS*ps.L*p["c_s0"]*(ps.ALPHA_L*K+psi*(1-ps.ALPHA_L)+ps.PHI_V2*(1-psi)*(1-ps.ALPHA_L))
    return initial, M0


def radau(history, Q, solute, grind, n, observations, *, t_span_s, rtol=2e-12, scaled_atol=2e-14, max_step_s=.02):
    """Actual T(t), independent segment-local assembly, no candidate freezing."""
    times = np.asarray(observations)
    t0, tf = t_span_s
    y, M0 = initial_and_inventory(history.value_K(t0), solute, grind, n)
    Cstar = ps._solute_params()[solute]["c_s0"]
    atol = np.r_[np.full(3*n, scaled_atol*Cstar), scaled_atol*M0]
    values = np.empty((len(times), len(y)))
    values[times == t0] = y
    checked_t, checked_y, records = [float(t0)], [y.copy()], []
    assemble = operator_factory(Q, solute, grind, n)
    for segment in history.integration_segments(float(t0), float(tf)):
        a, b = segment.start_s, segment.end_s
        def operator(t):
            return assemble(segment.value_K(float(t)))
        result = solve_ivp(lambda t, x: operator(t)@x, (a, b), y, method="Radau",
                           jac=lambda t, x: operator(t), atol=atol, rtol=rtol,
                           max_step=max_step_s, dense_output=True)
        if not result.success or result.t[-1] != b or not np.isfinite(result.y).all():
            raise RuntimeError("INDEPENDENT_RADAU_INCOMPLETE")
        indices = np.flatnonzero((times > a) & (times <= b))
        values[indices] = result.sol(times[indices]).T
        diagnostic = np.unique(np.r_[result.t[1:], times[indices]])
        checked_t.extend(diagnostic); checked_y.extend(result.sol(diagnostic).T)
        y = result.y[:, -1].copy()
        records.append(dict(span_s=[a, b], accepted_steps=len(result.t)-1,
                            nfev=result.nfev, njev=result.njev, nlu=result.nlu))
    if not np.isfinite(values).all():
        raise RuntimeError("NONFINITE_REFERENCE_OBSERVATIONS")
    return values, np.asarray(checked_t), np.asarray(checked_y), records


def passive_exact(n, times, Q, C0=1.):
    """Analytic integrals of the clean-inlet translated sin² profile; no solver call."""
    edges = np.linspace(0, ps.L, n+1)
    velocity = Q/(ps.ACS*ps.ALPHA_L)
    def primitive(u):
        # Bounds encode the compact support of the analytical initial condition.
        z = np.minimum(np.maximum(u, 0.), ps.L)
        return z/2-ps.L*np.sin(2*np.pi*z/ps.L)/(4*np.pi)
    avg = np.array([C0*np.diff(primitive(edges-velocity*t))/(ps.L/n) for t in times])
    M0 = ps.ACS*ps.ALPHA_L*C0*ps.L/2
    outlet = np.array([ps.ACS*ps.ALPHA_L*C0*(ps.L/2-primitive(ps.L-velocity*t)) for t in times])
    return avg, outlet, M0
