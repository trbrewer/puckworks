"""Independent physical equation assembly for temperature-history verification.

Shares unchanged source closures, fitted parameter table, geometry and separately
verified nodal stencil. Does not import the new production module or call its
RHS/operator builder. No assay, mass-clock, rate or slow-population wrappers.
Source-derived reports: Pannusch et al., DOI 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import csc_matrix, lil_matrix
from scipy.sparse.linalg import expm_multiply

from puckworks.models.pannusch2024 import closures as pc
from puckworks.models.pannusch2024 import solver as ps


def operator_factory(Q, solute, grind, nz):
    """Independent coefficient-separated row assembly, reused only within one solve."""
    sp = ps._solute_params()[solute]
    psi, d2 = ps.GRINDS[grind]["psi"], ps.GRINDS[grind]["d_s2"]
    a1, a2 = psi*(1-ps.ALPHA_L), (1-psi)*(1-ps.ALPHA_L)
    d32 = 6/(psi*6/ps.D1_FINE+(1-psi)*6/d2)
    q = Q/ps.ACS
    d = ps.five_point_biased_upwind(nz, ps.L/(nz-1), q)
    transport = lil_matrix((3*nz, 3*nz))
    for i in range(1, nz):
        for j in np.flatnonzero(d[i, 1:])+1:
            transport[i-1, j-1] = -q/ps.ALPHA_L*d[i, j]
    transport[-1, nz-2] = Q
    bases = []
    for offset, rate, liquid in ((nz-1, 6/ps.D1_FINE, 6*a1/(ps.ALPHA_L*ps.D1_FINE)),
                                 (2*nz-1, 6/(ps.PHI_V2*d2), 6*a2/(ps.ALPHA_L*d2))):
        from_liquid = lil_matrix((3*nz, 3*nz))
        from_grain = lil_matrix((3*nz, 3*nz))
        for i in range(nz):
            from_grain[offset+i, offset+i] = -rate
            if i:
                from_liquid[i-1, i-1] = -liquid
                from_liquid[offset+i, i-1] = rate
                from_grain[i-1, offset+i] = liquid
        bases.extend((csc_matrix(from_liquid), csc_matrix(from_grain)))
    transport = csc_matrix(transport)

    def operator(T_K):
        K = float(pc.vant_hoff_K(T_K, sp["K_ref"], sp["gamma"]))
        h1 = float(pc.sherwood_h(T_K, q, sp["A1"], sp["B1"], solute, d32))
        h2 = float(pc.sherwood_h(T_K, q, sp["A2"], sp["B2"], solute, d32))
        return transport+h1*bases[0]+h1*K*bases[1]+h2*bases[2]+h2*K*bases[3]
    return operator


def physical_operator(T_K, Q, solute, grind, nz):
    """Explicit row assembly of [cl[1:], cs1, cs2, Mout], in SI seconds."""
    return operator_factory(Q, solute, grind, nz)(T_K)


def reference_initial(T_K, solute, nz):
    sp = ps._solute_params()[solute]
    K = float(pc.vant_hoff_K(T_K, sp["K_ref"], sp["gamma"]))
    return np.r_[np.full(nz-1, K*sp["c_s0"]), np.full(2*nz, sp["c_s0"]), 0.]


def continuum_M0(T_K, solute, grind):
    sp = ps._solute_params()[solute]
    K = float(pc.vant_hoff_K(T_K, sp["K_ref"], sp["gamma"]))
    psi = ps.GRINDS[grind]["psi"]
    return ps.ACS*ps.L*sp["c_s0"]*(ps.ALPHA_L*K+psi*(1-ps.ALPHA_L)
                                      +ps.PHI_V2*(1-psi)*(1-ps.ALPHA_L))


def ordered_exponential(edges, temperatures_K, Q, solute, grind, nz, observations):
    """Exact-time semidiscrete propagation; no temporal interpolation of queries."""
    times = np.asarray(observations)
    y = reference_initial(temperatures_K[0], solute, nz)
    values = np.empty((len(times), len(y)))
    values[0] = y
    diagnostics = []
    for a, b, T in zip(edges[:-1], edges[1:], temperatures_K):
        op = physical_operator(T, Q, solute, grind, nz)
        # The declared regular diagnostic grid is computed together efficiently.
        dt = 0.0125
        n = int(round((b-a)/dt))
        grid = np.linspace(a, b, n+1)
        regular = expm_multiply(op, y, start=0., stop=b-a, num=n+1, endpoint=True)
        indices = np.flatnonzero((times >= a) & (times <= b))
        for j in indices:
            t = times[j]
            k = int(round((t-a)/dt))
            if 0 <= k <= n and abs(grid[k]-t) <= 2e-13:
                values[j] = regular[k]
            else:
                values[j] = expm_multiply(op*(t-a), y)
        next_y = regular[-1].copy()
        diagnostics.append({"span_s": [a, b], "matrix_shape": list(op.shape),
                            "matrix_nnz": op.nnz, "queries": len(indices),
                            "carried_state_equal": bool(np.array_equal(regular[0], y))})
        y = next_y
    return values, diagnostics


def independent_radau(knots, temperatures_K, Q, solute, grind, nz, observations,
                      rtol=2e-12, normalized_atol=2e-14, max_step_s=.05):
    """Independently assembled nonautonomous A(T(t)) with Radau integration."""
    y = reference_initial(temperatures_K[0], solute, nz)
    cs0 = ps._solute_params()[solute]["c_s0"]
    M0 = continuum_M0(temperatures_K[0], solute, grind)
    atol = np.r_[np.full(3*nz-1, cs0*normalized_atol), M0*normalized_atol]
    times = np.asarray(observations)
    values = np.empty((len(times), len(y)))
    diagnostics = []
    checked_times, checked_states = [], []
    assembled = operator_factory(Q, solute, grind, nz)
    for i, (a, b) in enumerate(zip(knots[:-1], knots[1:])):
        def operator(t):
            T = temperatures_K[i]+(temperatures_K[i+1]-temperatures_K[i])*(t-a)/(b-a)
            return assembled(T)
        sol = solve_ivp(lambda t, u: operator(t)@u, (a, b), y,
                        method="Radau", jac=lambda t, u: operator(t), rtol=rtol,
                        atol=atol, max_step=max_step_s, dense_output=True)
        if not sol.success or sol.t[-1] != b or not np.isfinite(sol.y).all():
            raise RuntimeError("independent Radau incomplete; no successful reference")
        indices = np.flatnonzero((times >= a) & (times <= b))
        values[indices] = sol.sol(times[indices]).T
        checked = np.unique(np.r_[sol.t, times[indices]])
        checked_times.extend(checked)
        checked_states.extend(sol.sol(checked).T)
        y = sol.y[:, -1].copy()
        diagnostics.append({"span_s": [a, b], "accepted_steps": len(sol.t)-1,
                            "nfev": sol.nfev, "njev": sol.njev, "nlu": sol.nlu})
    if not np.isfinite(values).all():
        raise RuntimeError("nonfinite independent reference")
    return values, diagnostics, np.asarray(checked_times), np.asarray(checked_states)
