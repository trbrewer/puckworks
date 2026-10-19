"""Bounded research comparison of the source law with its analytical limit.

Source equations/parameters: Pannusch et al., DOI 10.1016/j.jfoodeng.2023.111887.
Source-derived evidence: Mendeley 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0.
No production registration, default change, fitting or physical validation.
"""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from scipy.sparse import diags
from scipy.sparse.linalg import expm_multiply

from puckworks.models.pannusch2024 import solver as ps
from puckworks.models.pannusch2024 import temperature_history_fv as fv

CONDITIONS = ("PRED-C01", "PRED-C02", "PRED-C05", "PRED-C06")
SPECIES = ("caffeine", "trigonelline")
FRACTIONS = (1, 2, 3, 5, 7, 10)
RHO_COMMON = 980.0


@dataclass(frozen=True)
class Scenario:
    species: str
    temperature_C: float
    flow_label: float
    start_s: float = 0.0
    grind: float = 1.7

    def __post_init__(self):
        if self.species not in SPECIES or self.grind not in ps.GRINDS:
            raise ValueError("unsupported species/grind")
        if not np.isfinite([self.temperature_C, self.flow_label, self.start_s]).all():
            raise ValueError("nonfinite scenario")
        if not 80 <= self.temperature_C <= 98 or not 1e-6 <= self.Q <= 3e-6:
            raise ValueError("scenario outside source FV domain")

    @property
    def Q(self):
        return self.flow_label / 1000.0 / ps.RHO

    @property
    def T(self):
        return self.temperature_C + 273.15

    def system(self, cells):
        if not isinstance(cells, int) or cells < 1:
            raise ValueError("positive integer cell count required")
        return fv._System(self.species, self.grind, self.Q, cells)

    def constants(self):
        s = self.system(1)
        K, k1, k2 = s.coefficients(self.T)
        S = s.as1 + ps.PHI_V2*s.as2
        H = ps.ALPHA_L + S/K
        return dict(K=K, S=S, H=H, c_s0=s.Cstar, k1=k1, k2=k2,
                    alpha_s1=s.as1, alpha_s2=s.as2, Q_m3_s=self.Q,
                    initial_liquid_kg=ps.ACS*ps.L*ps.ALPHA_L*K*s.Cstar,
                    initial_fine_kg=ps.ACS*ps.L*s.as1*s.Cstar,
                    initial_coarse_kg=ps.ACS*ps.L*ps.PHI_V2*s.as2*s.Cstar,
                    initial_total_kg=s.M0(self.T),
                    front_s=self.start_s+ps.ACS*ps.L*H/self.Q)


def windows_array(windows, start):
    w = np.asarray(windows, float)
    if w.ndim != 2 or w.shape[1] != 2 or not len(w) or not np.isfinite(w).all():
        raise ValueError("finite interval pairs required")
    if np.any(w[:, 1] <= w[:, 0]) or np.any(w[:, 0] < start):
        raise ValueError("nonpositive or unsupported intervals")
    if np.any(w[1:, 0] < w[:-1, 1]):
        raise ValueError("ordered nonoverlapping intervals required")
    return w


def equilibrium_averages(scenario, windows, scale=1.0):
    w = windows_array(windows, scenario.start_s)
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError("positive finite inventory scale required")
    p = scenario.constants()
    overlap = np.maximum(0., np.minimum(w[:, 1], p['front_s'])-w[:, 0])
    return scale*p['K']*p['c_s0']*overlap/(w[:, 1]-w[:, 0])


def normalize(concentration, liquid_mass_kg, *, errors=None, inventory_kg=None):
    """Conditional vial solute kg and six shares; conservative ratio allowance.

    Errors are absolute concentration allowances, not experimental uncertainties.
    No clipping or pseudocounts. Exact-zero individual fractions remain valid.
    """
    c, m = np.asarray(concentration, float), np.asarray(liquid_mass_kg, float)
    if c.shape != (6,) or m.shape != (6,):
        raise ValueError("exactly six fractions required")
    if not np.isfinite(c).all() or not np.isfinite(m).all() or np.any(c < 0) or np.any(m <= 0):
        raise ValueError("nonfinite/negative concentration or nonpositive vial mass")
    q = m/RHO_COMMON*c
    total = float(q.sum())
    floor = 64*np.finfo(float).eps*(inventory_kg if inventory_kg is not None else float(np.max(q)))
    if not np.isfinite(total) or total <= max(0., floor):
        raise ValueError("normalization denominator unresolved")
    share = q/total
    e = np.zeros(6) if errors is None else np.asarray(errors, float)
    if e.shape != (6,) or not np.isfinite(e).all() or np.any(e < 0):
        raise ValueError("invalid concentration allowance")
    eq = m/RHO_COMMON*e
    E = float(eq.sum())
    if total <= E:
        raise ValueError("normalization denominator unresolved within allowance")
    d = (eq+share*E)/(total-E)
    return share, d, q


def finite_averages(scenario, windows, *, cells=1600, halves=False, rate_scale=1., scale=1.):
    """Existing 002 constant generator; exact exponential per segment.

    rate_scale is verification-only. Every gap is propagated. A local outlet
    reward avoids subtracting cumulative large totals for late fractions.
    """
    w = windows_array(windows, scenario.start_s)
    if not np.isfinite([rate_scale, scale]).all() or min(rate_scale, scale) <= 0:
        raise ValueError("positive finite scales required")
    s = scenario.system(cells)
    K, k1, k2 = s.coefficients(scenario.T)
    if rate_scale == 1:
        B = s.generator(scenario.T)
    else:
        B = fv._mass_generator(cells, s.Q/(s.W*ps.ALPHA_L),
                              s.as1*k1/ps.ALPHA_L*rate_scale,
                              ps.PHI_V2*s.as2*k2/ps.ALPHA_L*rate_scale,
                              K*k1*rate_scale, K*k2*rate_scale)
    y = s.initial(scenario.T)*scale
    M0 = s.M0(scenario.T)*scale
    boundaries = np.unique(np.r_[scenario.start_s, w.ravel()])
    delivery, cumulative, ledger, minimum = {}, 0., 0., float(np.min(y[:-1]/s.capacities))
    trace = float(B.diagonal().sum())
    for a, b in zip(boundaries[:-1], boundaries[1:]):
        y[-1] = 0.
        for _ in range(2 if halves else 1):
            dt = (b-a)/(2 if halves else 1)
            y = expm_multiply(B*dt, y, traceA=trace*dt)
            if not np.isfinite(y).all():
                raise ValueError("nonfinite exponential state")
            minimum = min(minimum, float(np.min(y[:-1]/s.capacities)))
        delivery[(a, b)] = float(y[-1])
        cumulative += float(y[-1])
        # Reconstruct physical phase fields independently of the accumulated reward.
        physical = y[:-1]/s.capacities
        remaining = s.W*(ps.ALPHA_L*physical[:cells].sum()
                         + s.as1*physical[cells:2*cells].sum()
                         + ps.PHI_V2*s.as2*physical[2*cells:].sum())
        ledger = max(ledger, abs(remaining+cumulative-M0)/M0)
    concentrations = np.array([sum(v for (a, b), v in delivery.items() if lo <= a and b <= hi)
                               /(s.Q*(hi-lo)) for lo, hi in w])
    if minimum < 0 or np.any(concentrations < 0) or ledger > 1e-9:
        raise ValueError("FV positivity/inventory qualification failed")
    return concentrations, dict(mass_balance_relative=ledger, minimum_phase_kg_m3=minimum,
                                total_outlet_kg=cumulative, remaining_kg=float(remaining),
                                initial_inventory_kg=M0, cells=cells,
                                intervals=len(boundaries)-1, halves=halves)


def independent_radau(scenario, windows, cells=40):
    """Verification in physical concentration coordinates, independently assembled."""
    w = windows_array(windows, scenario.start_s)
    s = scenario.system(cells)
    K, k1, k2 = s.coefficients(scenario.T)
    v = s.Q/(ps.ACS*ps.ALPHA_L)
    dz = ps.L/cells
    def rhs(t, y):
        l, f, c = y[:cells], y[cells:2*cells], y[2*cells:3*cells]
        r1, r2 = k1*(K*f-l), k2*(K*c-l)
        dl = -v/dz*(l-np.r_[0., l[:-1]]) + s.as1/ps.ALPHA_L*r1 + ps.PHI_V2*s.as2/ps.ALPHA_L*r2
        return np.r_[dl, -r1, -r2, s.Q*l[-1]]
    # Jacobian from this independent physical-coordinate RHS, without FV mass helper.
    J = np.column_stack([rhs(0., x) for x in np.eye(3*cells+1)])
    from scipy.sparse import csc_matrix
    y = np.r_[np.repeat([K*s.Cstar, s.Cstar, s.Cstar], cells), 0.]
    sol = solve_ivp(rhs, (scenario.start_s, w[-1, 1]), y, method='Radau',
                    jac=csc_matrix(J), rtol=2e-11, atol=1e-13, dense_output=True)
    if not sol.success:
        raise ValueError(sol.message)
    cbar = (sol.sol(w[:, 1])[-1]-sol.sol(w[:, 0])[-1])/(s.Q*(w[:, 1]-w[:, 0]))
    return cbar, sol


def grid_equilibrium_averages(scenario, windows, cells):
    """Finite-grid equilibrium verification reference, NOT scientific predictor.

    Conservative one-phase upwind chain, matrix exponential. Its outlet step
    response equals gammaincc(N, Q*(t-t0)/(W*H)), not the continuum front.
    """
    w = windows_array(windows, scenario.start_s)
    p = scenario.constants()
    rate = cells/(p['front_s']-scenario.start_s)
    from scipy.sparse import lil_matrix
    B = lil_matrix((cells+1, cells+1))
    B[:cells, :cells] = diags([-rate*np.ones(cells), rate*np.ones(cells-1)], [0, -1])
    B[cells, cells-1] = rate
    B = B.tocsc()
    y = np.r_[np.full(cells, p['initial_total_kg']/cells), 0.]
    values = {}
    for a, b in zip(np.unique(np.r_[scenario.start_s, w.ravel()])[:-1],
                    np.unique(np.r_[scenario.start_s, w.ravel()])[1:]):
        y[-1] = 0.
        y = expm_multiply(B*(b-a), y, traceA=-cells*rate*(b-a))
        values[(a, b)] = y[-1]
    return np.array([sum(v for (a, b), v in values.items() if lo <= a and b <= hi)
                     /(scenario.Q*(hi-lo)) for lo, hi in w])


def balanced(rows, key, analyte=None):
    """Equal analytes, shots, conditions after each deletion."""
    selected = [r for r in rows if analyte is None or r['analyte'] == analyte]
    if not selected:
        raise ValueError("empty reduction")
    means = []
    for condition in sorted({r['condition'] for r in selected}):
        shots = []
        for shot in sorted({r['shot'] for r in selected if r['condition'] == condition}):
            q = [r[key] for r in selected if r['condition'] == condition and r['shot'] == shot]
            shots.append(float(np.mean(q, axis=0)))
        means.append(float(np.mean(shots)))
    return float(np.mean(means))


def rmse(x):
    return float(np.sqrt(np.mean(np.asarray(x)**2)))
