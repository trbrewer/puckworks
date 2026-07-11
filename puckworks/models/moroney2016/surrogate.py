"""surrogate.py — Moroney et al. 2016 asymptotic extraction surrogate.

Card: docs/cards/moroney2016.md (ROADMAP item 1.4). CALIBRATION provider: a
matched-asymptotic, constant-dP reduction of the Moroney 2015 two-population
extraction model. The small parameter eps = t_a/t_d separates an inner
(advection, surface dissolution) layer from an outer (bulk kernel diffusion)
region; closed-form composite solutions relate exit concentration to process
parameters with no PDE solve.

Leading-order composite exit concentration (their Eq. 3.45, z=0 outlet):
    c_h0(0, t) = 1                                            for t < 1
               = (e^a2 - 1) / (e^a2 - 1 + e^{a2 a3 (t-1)})    for t > 1
with a2 = t_a/t_s, a3 = pore capacity / initial surface coffee (Table 1). This
captures the saturated plateau (t<1) and the first-wash-through timing, but is
too steep in the long-time TAIL: the outer bulk-diffusion solution (their
Eqs. 3.61-3.62) and the O(eps) inner correction (3.56) — referenced but not
transcribed on the card — govern the tail and are NOT reproduced here. So Fig 6
reproduction is QUALITATIVE (as the source itself states: graphical, no error
metrics; eps=0.127 => ~13% first-order truncation).

Scope (card): saturated bed only (needs infiltration to supply psi_s0/eta/IC);
constant dP with linear pressure profile; isothermal single lumped solute;
1D homogeneous. Not a runtime stage while cameron2020 holds that slot.
"""
import numpy as np

# Dimensionless groups from Table 1 (fine grind), card Eqs. 2.25-2.26.
A2 = 5.139               # t_a / t_s
A3 = 0.473               # pore mass capacity / initial surface coffee
ETA = 0.5                # initial intragranular concentration level
EPS = 0.127              # t_a / t_d (first-order truncation ~ eps)


def composite_exit(t, a2=A2, a3=A3):
    """Leading-order composite exit concentration c_h0(0, t) (Eq. 3.45).
    Nondimensional time t (t=1 is the first wash-through)."""
    t = np.asarray(t, float)
    out = np.ones_like(t)
    m = t > 1.0
    e2 = np.exp(a2)
    out[m] = (e2 - 1.0) / (e2 - 1.0 + np.exp(a2 * a3 * (t[m] - 1.0)))
    return out


def washthrough_halfmax_time(a2=A2, a3=A3):
    """Nondimensional t at which the leading-order exit reaches c=1/2 (the
    wash-through midpoint). Analytic: 1 + ln(e^a2 - 1)/(a2 a3)."""
    return 1.0 + np.log(np.exp(a2) - 1.0) / (a2 * a3)
