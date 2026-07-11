"""extraction.py — Mo et al. 2023 swelling-coupled solute extraction (fixed-q).

Card: docs/cards/mo2023_2.md (ROADMAP item 3.1). The extraction half of the
swelling model (Eqs 9-17 + bed 19-24). The card verdict is explicit that this
core "duplicates Cameron at lower fidelity", so we build only what makes the
paper's DISTINCTIVE point: at a FIXED flow rate, swelling is nearly invisible in
the yield (their Fig 2), in stark contrast to the ~10x flow throttling swelling
causes at fixed dP (their Fig 3a, module swelling.flow_decay).

Two representative grains (fine + coarse) extract by hindered Fickian diffusion
(D_p = eps_p D_b/(beta H_c)) into a lumped bed swept by the imposed flow q. The
swelling coupling enters ONLY through eps_p and the grain radius: full swelling
raises eps_p by ~15% (faster diffusion) but grows R by 3.6% (R^2 up ~7%, slower),
so the grain diffusion timescale R^2/D_p changes by only ~-7% -> the yield barely
moves. The bed solve reuses romancorrochano2017.extraction.bed_lumped per
population (they share the flow but are run independently here -- adequate for the
swelling ON-vs-OFF comparison, which is the point).

Fixed constants (card): eps_p0=0.4, beta=3.2, H_c=2, D_b=2e-9, C_M=0.1, K=0.9.
"""
import numpy as np

from puckworks import data as _d
from puckworks.models.romancorrochano2017 import extraction as _rx
from puckworks.models.mo2023_2 import swelling as _sw

EPS_P0 = 0.4           # initial grain (intraparticle) porosity
BETA = 3.2            # tortuosity-like hindrance
H_C = 2.0            # partition/hindrance factor
D_B = 2.0e-9          # bulk solute diffusivity [m^2/s]
K_PART = 0.9           # partition coefficient (tuned, card gate 3)
EPS_B = 0.17           # bed porosity (dry)
# rig geometry (2-shot, card): bed radius 29 mm, height 13.5 mm
BED_RADIUS_M = 0.029
BED_HEIGHT_M = 0.0135


def deff_grain(swelling=False):
    """Hindered intraparticle diffusivity D_p = eps_p D_b/(beta H_c). Full
    swelling raises eps_p = 1-(1-eps_p0)(1-C_M) (card Eq 11)."""
    eps_p = 1.0 - (1.0 - EPS_P0) * (1.0 - _sw.C_M) if swelling else EPS_P0
    return eps_p * D_B / (BETA * H_C)


def extract_fixed_flow(powder, q_mL_s, swelling=False, t_end=25.0, n=150,
                       K=K_PART, eps_b=EPS_B):
    """Fixed-flow-rate 2-population extraction. Returns (t, yield_frac(t)) with the
    fine/coarse grains swelling-modified (Deff, R) when swelling=True. yield_frac
    is the fraction of extractable inventory (x y0 for absolute EY)."""
    row = {r["powder"]: r for r in _d.mo2_granulometry()}[powder]
    tf, tc = row["theta_f"], row["theta_c"]
    Rf, Rc = row["2R_f_um"] / 2e6, row["2R_c_um"] / 2e6
    Deff = deff_grain(swelling)
    if swelling:
        rr = (1.0 - _sw.C_M) ** (-1.0 / 3.0)              # isotropic radius growth
        Rf, Rc = Rf * rr, Rc * rr
    V_bed = np.pi * BED_RADIUS_M ** 2 * BED_HEIGHT_M
    Q = q_mL_s * 1e-6
    t = np.linspace(0.0, t_end, n)
    yf = _rx.bed_lumped(Deff=Deff, R=Rf, K=K, Q=Q, eps_bed=eps_b,
                        V_bed=V_bed * tf, t_eval=t)["yield_frac"]
    yc = _rx.bed_lumped(Deff=Deff, R=Rc, K=K, Q=Q, eps_bed=eps_b,
                        V_bed=V_bed * tc, t_eval=t)["yield_frac"]
    return t, tf * yf + tc * yc


def swelling_insensitivity(powder="M", q_list=(2, 3, 4)):
    """The card's gate-4 result: at fixed flow, swelling barely changes the yield.
    Returns per-flow the swell/no-swell end yields and their relative difference,
    plus the contrast with the fixed-dP flow decay (swelling.flow_decay)."""
    rows = {}
    for q in q_list:
        _, y0 = extract_fixed_flow(powder, q, swelling=False)
        _, ys = extract_fixed_flow(powder, q, swelling=True)
        rows[q] = dict(yield_no_swell=float(y0[-1]), yield_swell=float(ys[-1]),
                       rel_diff=float(abs(ys[-1] - y0[-1]) / y0[-1]),
                       rises_with_Mc=bool(y0[-1] > y0[len(y0) // 10]))
    kappa_ratio = _sw.flow_decay_ratio(powder)             # fixed-dP throttle
    return dict(per_flow=rows, fixedq_max_rel_diff=max(r["rel_diff"] for r in rows.values()),
                fixeddp_flow_ratio=kappa_ratio,
                contrast=f"fixed-dP ~{1/kappa_ratio:.0f}x vs fixed-q "
                         f"<{100*max(r['rel_diff'] for r in rows.values()):.0f}%")
