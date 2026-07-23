"""moroney2015 well-mixed batch (French-press) two-population extraction solver.

Solves moroney2015's fitted batch reduction (their Eqs. 52-56, `docs/cards/moroney2015.md`): a
well-mixed suspension with an intergranular liquid concentration c_h, an intragranular pore
concentration c_v, an evolving intragranular porosity phi_v, and a surface-inventory fraction psi_s.

Two transcription corrections (both flagged on the card / mass-balance required, NOT invented):
  * Eq. (53) v->h transfer: the printed sign is the v-phase LOSING solute to h
    (card: "note sign convention as printed; this is the v-phase losing solute to h"), and the
    (1-phi_h) volume factor belongs to the h-phase balance (52), not the v-phase balance (53).
    Coded conservatively so total soluble mass is conserved.

The immersion-dilution volume bookkeeping is DERIVED (exact reconstruction), not assumed: from
60 g coffee at 4 % moisture, c_s = 1400 kg/m^3, and the dry-in-air intragranular porosity phi_v = 0.56
(Section 5.1, distinct from Table 1's post-kernel-dissolution phi_v0 = 0.6444 = 0.56 + phi_s,b0), the
suspension volume V_T = 541.1 cm^3 and bulk-liquid volume V_h = 447.6 cm^3 reconstruct Table 1's
phi_h = V_h/V_T = 0.8272 to four decimals, confirming the authors' construction. c_h and the Fig-2/6
brew concentration are direct liquid concentrations, so they compare with NO extra factor; the
volume factors only enter when converting between extracted-mass yield and concentration.

NOT a registered runtime component; a source-curve reproduction of the paper's own Fig-6 batch
plateau from Table 1 + the derived bookkeeping. No fit performed here; no invented values.
"""
import numpy as np
from scipy.integrate import solve_ivp

from puckworks import data as _data

_DOSE_G = 60.0
_MOISTURE = 0.04
_PHI_V_DRY = 0.56          # dry-in-air intragranular porosity (Section 5.1)
_C_S_SOLID = 1400.0        # coffee true density (kg/m^3)
_V_WATER_M3 = 500e-6       # batch water charge


def derived_volumes():
    """DERIVED (exact reconstruction) immersion volume bookkeeping. Returns V_s/V_l/V_T/V_h (m^3)
    and phi_h reconstructed from the volumes — which matches Table 1's 0.8272 to four decimals."""
    V_s = _DOSE_G * (1.0 - _MOISTURE) / _C_S_SOLID * 1e-3     # dry-solid volume (57.6 g / 1400)
    V_l = V_s / (1.0 - _PHI_V_DRY)                            # grain envelope volume
    V_T = _V_WATER_M3 + V_s                                   # suspension volume
    V_h = V_T - V_l                                           # bulk (intergranular) liquid volume
    return dict(V_s_m3=V_s, V_l_m3=V_l, V_T_m3=V_T, V_h_m3=V_h,
                phi_h_reconstructed=V_h / V_T,
                V_T_over_V_water=V_T / _V_WATER_M3,           # 1.0823 (bed-volume -> water-charge)
                V_h_over_V_water=V_h / _V_WATER_M3)           # 0.8953 (bulk-liquid fraction)


def _params(grind):
    t1 = {r["parameter"]: r for r in _data.moroney2015_data()["table1_batch_params"]}
    def P(name):
        return float(t1[name][grind])
    return dict(a=P("alpha_star"), b=P("beta_star"), phi_h=P("phi_h"), phi_v0=P("phi_v0"),
                Dv=P("D_h = D_v"), ksv1=P("k_sv1") * 1e-6, ksv2=P("k_sv2") * 1e-6,
                ll=P("l_l") * 1e-6, mm=P("m") * 1e-6, phi_c0=P("phi_c0"), c_sat=P("c_sat"),
                c_s=P("c_s"), r_s=P("r_s"), phi_ss0=P("phi_ss0"), phi_sb0=P("phi_sb0"),
                c_v0=P("c_v0"))


def solve(grind, t_end_s=600.0):
    """Solve the batch reduction for `grind` in {'JK_drip_filter','Cimbali_20'}. Returns the c_h
    trajectory, its equilibrium plateau, the c_v0 IC cross-check, and the soluble mass budget."""
    p = _params(grind)
    phi_h, r_s, c_sat, c_s = p["phi_h"], p["r_s"], p["c_sat"], p["c_s"]

    def rhs(_t, y):
        ch, cv, phi_v, psi = y
        Avv = p["a"] * phi_v ** (4.0 / 3.0) * p["Dv"] * (6.0 / (p["ksv2"] * p["ll"]))   # (53) coeff
        Bc = p["b"] * (12.0 * p["Dv"] * p["phi_c0"] / (p["ksv1"] * p["mm"]))            # surface (55)
        dpsi = -Bc * ((c_sat - ch) / c_s) * r_s * psi                                   # (55)
        dphi_v = -(1.0 / r_s) * dpsi                                                     # (54)
        # (52): h-phase gains from v->h (with 1-phi_h) and surface dissolution
        dch = ((1.0 - phi_h) * Avv * (cv - ch)
               + p["b"] * (1.0 - phi_h) * (12.0 * p["Dv"] * p["phi_c0"] / (p["ksv1"] * p["mm"]))
               * (c_sat - ch) * psi) / phi_h
        dcv = (-Avv * (cv - ch) - cv * dphi_v) / phi_v                                   # (53) v loses
        return [dch, dcv, dphi_v, dpsi]

    sol = solve_ivp(rhs, [0.0, t_end_s], [0.0, p["c_v0"], p["phi_v0"], 1.0],
                    t_eval=np.linspace(0.0, t_end_s, 61), method="BDF", rtol=1e-9, atol=1e-11)
    ch = sol.y[0]
    vols = derived_volumes()
    # total soluble mass available (surface + kernel), and the conservation equilibrium
    M_soluble_g = (p["phi_ss0"] + p["phi_sb0"]) * c_s * (1.0 - phi_h) * vols["V_T_m3"] * 1e3
    return dict(
        grind=grind, t_s=sol.t, ch_kgm3=ch,
        ch_equilibrium=float(ch[-1]),
        c_v0_table=p["c_v0"], c_v0_derived=p["phi_sb0"] * c_s / p["phi_v0"],   # IC cross-check
        M_soluble_g=M_soluble_g, extractable_pct_dose=M_soluble_g / _DOSE_G * 100.0,
        c_sat=c_sat,
    )
