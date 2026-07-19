"""infiltration.py — Stage-0 dry-bed infiltration (Foster et al., Phys. Fluids 2025).

Models the wetting stage our extraction solver assumes away: a sharp front s(t)
penetrating an initially dry bed. For a *recorded* pressure trace (the DE1 case)
the front equation phi_T * s * ds/dt = (k/mu) * P(t) integrates in closed form,

    s(t) = sqrt( 2 k \\int_0^t P dt' / (mu * phi_T) ),

so ponding-machinery is unnecessary; their full pump/headspace model (their
Eqs. 2-7) matters only when pressure is not measured, and is left as the PUCK
LAB "machine mode" backlog item.

Validated against DE1 fixture 20210921T085910: predicted bed saturation
6.4-7.8 s across the porosity bracket (intergrain 0.173 ... water-accessible
0.322), observed first beverage on scale at 7.0 s; predicted bed uptake
7.5-14.0 g brackets the independently fitted measurement-layer W_dead = 8.8 g.

Capillary suction (their nominal p_c = 0.1 bar) is 2% of a flat 5-bar shot,
7% of a 1.5-bar preinfusion, 50% of a 0.2-bar blooming pause: include it for
low-pressure stages via the p_c argument.
"""
import numpy as np

MU_90C = 0.315e-3      # Pa s
RHO_90C = 965.0        # kg m^-3
# First-drip weight threshold (g): the scale reading above which the first beverage is "on scale". This is
# the SINGLE authoritative constant — the validation gate and the Lab native runner both consume it, so
# the threshold can never drift between them.
FIRST_DRIP_THRESHOLD_G = 0.5


def observed_first_drip_s(t, weight_g, threshold_g=FIRST_DRIP_THRESHOLD_G):
    """First time the recorded weight strictly crosses `threshold_g`, or None if it never does (no first
    drip — never a spurious argmax-of-all-False at t[0])."""
    t = np.asarray(t); w = np.asarray(weight_g)
    above = np.flatnonzero(w > threshold_g)
    return float(t[above[0]]) if above.size else None


def front_from_pressure(t, P_bar, k_SI, phi_T, L, p_c_bar=0.0,
                        mu=MU_90C, rho=RHO_90C, A=None):
    """Wetting-front position under a recorded/prescribed pressure history.

    t [s], P_bar [bar] arrays; k_SI [m2] bed permeability; phi_T water-accessible
    porosity; L [m] bed depth. Returns dict with s(t) [m] (capped at L),
    t_saturate [s or None], and uptake_g(t) if the bed area A [m2] is given.
    """
    t = np.asarray(t, float)
    P = (np.asarray(P_bar, float) + p_c_bar) * 1e5
    Pint = np.concatenate([[0.0], np.cumsum(0.5*(P[1:]+P[:-1])*np.diff(t))])
    s = np.sqrt(np.maximum(2.0*k_SI*Pint/(mu*phi_T), 0.0))
    t_sat = float(np.interp(L, s, t)) if s[-1] >= L else None
    out = dict(s=np.minimum(s, L), t_saturate=t_sat)
    if A is not None:
        out["uptake_g"] = phi_T * A * np.minimum(s, L) * rho * 1e3
        out["capacity_g"] = float(phi_T * A * L * rho * 1e3)
    return out


def k_from_kappa(gs, dose_kg, kappa, mu=MU_90C):
    """Convert the shot-fitted kappa multiplier to an SI permeability via the
    Cameron flux table (q = qbar(G,L) * kappa * P/P_ref)."""
    from puckworks.models.cameron2020 import extraction_bdf as em
    L = em.bed_depth(dose_kg)
    q_per_bar = em.darcy_flux(gs, 5.0, L=L, L_ref=em.bed_depth(0.020)) / 5.0 * kappa
    return q_per_bar * mu * L / 1e5, L


def scale_model(t, W_bev_g, uptake_g):
    """Mechanistic replacement for the [W - W_dead]_+ measurement layer:
    the scale sees beverage minus water still being invested in the bed,
    with the dead volume now time-resolved instead of a fitted constant."""
    return np.maximum(0.0, np.asarray(W_bev_g) - np.asarray(uptake_g))


if __name__ == "__main__":
    import json
    from puckworks.models.cameron2020 import extraction_bdf as em
    em.C_S0 = 118.0/em.PHI_S
    KV = json.load(open("/tmp/review_kval.json"))
    t = np.array(KV["recA"]["elapsed"]); P = np.array(KV["recA"]["pressure"])
    k, L = k_from_kappa(1.9, 0.018, KV["kappaA"])
    A = np.pi*em.R0**2
    for name, phiT in [("intergrain 0.173", 0.173), ("water-accessible 0.322", 0.322)]:
        r = front_from_pressure(t, P, k, phiT, L, A=A)
        print(f"[{name}] t_sat = {r['t_saturate']:.1f} s, capacity {r['capacity_g']:.1f} g "
              f"(observed first drip 7.0 s; fitted W_dead 8.8 g)")
