"""swelling.py — Mo et al. 2023 (J. Food Eng.) swelling-throttled flow.

Card: docs/cards/mo2023_2.md (ROADMAP item 3.1). The paper's distinctive claim
(its extraction core "duplicates Cameron at lower fidelity", card verdict): grains
imbibe "additional water" by nonlinear diffusion and expand isotropically, which
shrinks the fixed-height bed's porosity ε_b(t), which throttles the Carman-Kozeny
flow at fixed Δp. Because the swelling timescale is τ ~ ℛ²/D^w, the small fines
fully swell within a shot while the large boulders only partially do -- so a
powder with coarser boulders (larger ℛ_c) swells less and its flow decays less.

This module implements the SWELLING mechanism and the fixed-Δp flow decay (the
headline, Fig 3(a)); the swelling-coupled solute EXTRACTION (Eqs 9-17 + bed) is a
further layer (its yield/strength is the Cameron-duplicating half) not built here.

Governing (their Eqs. 3, 8, 21, 25-28, 40-45):
  swelling         ∂c^w/∂t = D^w (1-c^w)(∂²c^w/∂r² + (2/r)∂c^w/∂r)
  BCs              c^w(ℛ)=C_M, ∂c^w/∂r(0)=0, c^w(r,0)=0
  swollen volume   (r/ℛ)³ = (3/ℛ³) ∫₀^ℛ ξ² (1-c^w)^(-1) dξ      (Eq 42)
  max swelling     s_m = [(1-C_M)^(-1/d_n) - 1] × 100%           (Eq 8)
  bed porosity     ε_b = 1 - (1-ε_b⁰)( (r_f/ℛ_f)³ ϑ_f + (r_c/ℛ_c)³ ϑ_c )  (Eq 21)
  Carman-Kozeny D  ∝ ε_b^(3+2n) d_[3,2]² / (1-ε_b)²,  d_[3,2]=2/(ϑ_c/r_c+ϑ_f/r_f)

Fixed Δp/μ/L cancel in the flow RATIO q(t)/q(0); we report the ratio (the
Δp-independent, faithfully-checkable Fig 3(a) target), not absolute velocity.
"""
import numpy as np
from scipy.integrate import solve_ivp

from puckworks import data as _d

# --- fixed constants (docs/cards/mo2023_2.md Parameters) ---------------------
EPS_B0 = 0.17          # initial bed porosity (Cameron 2020)
N_TORT = 0.5           # Carman-Kozeny tortuosity index tau=(1/eps)^n
C_M = 0.1              # surface additional-water fraction (-> s_m=3.57%)
D_W = 1.25e-10         # in-grain swelling diffusivity [m^2/s] (fit to ~30 s)


def s_max(c_m=C_M, d_n=3):
    """Maximum swelling degree [%] (Eq. 8): isotropic expansion at full uptake."""
    return ((1.0 - c_m) ** (-1.0 / d_n) - 1.0) * 100.0


def _granulometry():
    return {r["powder"]: r for r in _d.mo2_granulometry()}


def swelling_volume_ratio(R, t_eval, D_w=D_W, c_m=C_M, N=60):
    """Solve the nonlinear swelling PDE in a sphere of initial radius R and
    return (r/ℛ)³(t) -- the volumetric expansion factor (Eq 42) at each t_eval.
    (r/ℛ)³ runs from 1 (dry) to 1/(1-C_M) (fully swollen)."""
    r = np.linspace(0.0, R, N + 1)
    dr = R / N

    def rhs(t, c):
        full = np.empty(N + 1)
        full[:N] = c
        full[N] = c_m                                   # surface Dirichlet
        lap = np.empty(N)
        lap[1:] = ((full[2:] - 2.0 * full[1:N] + full[:N - 1]) / dr ** 2
                   + (2.0 / r[1:N]) * (full[2:] - full[:N - 1]) / (2.0 * dr))
        lap[0] = 6.0 * (full[1] - full[0]) / dr ** 2    # spherical centre limit
        return D_w * (1.0 - full[:N]) * lap
    sol = solve_ivp(rhs, [0.0, t_eval[-1]], np.zeros(N), method="BDF",
                    t_eval=t_eval, rtol=1e-7, atol=1e-9)
    out = []
    for k in range(sol.y.shape[1]):
        cw = np.append(sol.y[:, k], c_m)
        out.append(3.0 / R ** 3 * np.trapezoid(r ** 2 / (1.0 - cw), r))
    return np.array(out)


def _ck_conductivity(eps_b, d32, n=N_TORT):
    """Carman-Kozeny conductivity group (Δp,μ,L-independent): ε³ d² / (72 τ²
    (1-ε)²) with τ=(1/ε)^n -> ε^(3+2n) d² / (1-ε)² up to the constant 1/72."""
    return eps_b ** (3.0 + 2.0 * n) * d32 ** 2 / (1.0 - eps_b) ** 2


def flow_decay(powder, t_eval, eps_b0=EPS_B0, n=N_TORT, D_w=D_W, c_m=C_M, N=60):
    """Fixed-Δp flow throttling by swelling for a powder (E/H/M/F). Returns dict:
    t, eps_b(t), d32(t) [m], q_rel(t) = q(t)/q(0) (relative superficial velocity;
    Δp/μ/L cancel). Fine + coarse representative particles swell independently
    (Eq 21); the coarse particle only partially swells within the shot."""
    row = _granulometry()[powder]
    tf, tc = row["theta_f"], row["theta_c"]
    Rf, Rc = row["2R_f_um"] / 2.0 * 1e-6, row["2R_c_um"] / 2.0 * 1e-6
    vf = swelling_volume_ratio(Rf, t_eval, D_w, c_m, N)     # (r_f/ℛ_f)³(t)
    vc = swelling_volume_ratio(Rc, t_eval, D_w, c_m, N)     # (r_c/ℛ_c)³(t)
    eps_b = 1.0 - (1.0 - eps_b0) * (vf * tf + vc * tc)      # Eq 21
    rf, rc = Rf * vf ** (1.0 / 3.0), Rc * vc ** (1.0 / 3.0)
    d32 = 2.0 / (tc / rc + tf / rf)                         # Eq 26
    cond = _ck_conductivity(eps_b, d32, n)
    return dict(t=np.asarray(t_eval, float), eps_b=eps_b, d32=d32,
                q_rel=cond / cond[0])


def flow_decay_ratio(powder, t_end=60.0, **kw):
    """The Fig 3(a) headline: q(t_end)/q(0) at full-shot swelling. Small for finer
    powders (fines + smaller boulders swell more) -> stronger throttling."""
    fd = flow_decay(powder, np.array([1e-4, t_end]), **kw)
    return float(fd["q_rel"][-1])
