"""moroney2019 1-D two-grain linear-driving-force (LDF) extraction solver — VERIFICATION only.

Solves moroney2019's 1-D cylindrical reduction (their Eqs. 17-27, `docs/cards/moroney2019.md`)
by method of lines: upwind advection of the intergranular-liquid concentration c_l(z,t) at the
Darcy velocity v = Q/(alpha_l A), with two grain populations (small/large) each acting as a
linear-driving-force sink

    d c_l/dt + v d c_l/dz = sum_i 6 h_sl,i alpha_s,i / (alpha_l d_s,i) (c_s,i - c_l)
    d c_s,i/dt           = -6 h_sl,i / (phi_v d_s,i) (c_s,i - c_l)

with c_l(0,t)=0 and fully-wetted ICs c_l(z,0)=0, c_s,i(z,0)=c_s0 (Eqs. 26-27). Axial diffusion is
neglected (advection-dominated, per the card). Parameters come from the intaken moroney2019
Table 2 with the AUTHOR-CONFIRMED cooper2021 h_sl erratum applied (h_sl = reported/965.3), and the
bed height L from the moroney2015 primary dataset (the same Philips chamber).

This is a model-vs-itself VERIFICATION of the transcribed equations and the cooper2021 correction
(mass conservation, physical bounds, the two-timescale small/large structure). It is NOT a
registered runtime component and NOT a fit to data: reproducing moroney2019's reported
c_exit RMSE (5.81/6.23 kg m^-3) needs their own Fig-6 exit-concentration digitization, which is
not in the registry.
"""
import numpy as np
from scipy.integrate import solve_ivp

from puckworks import data as _data

PHI_V = 0.56                               # intragranular porosity (moroney2019 card)
_CHAMBER_ID_M = 0.059                       # Philips brew-chamber inner diameter
_Q_M3_S = 250e-6 / 60.0                     # 250 mL/min set point
# bed height per grind, from the moroney2015 primary dataset (same chamber)
_L_BY_GRIND = {"fine": "JK_drip_filter", "coarse": "Cimbali_20"}

_trapz = getattr(np, "trapezoid", None) or getattr(np, "trapz")


def _bed_height(grind):
    t2 = {r["parameter"]: r for r in _data.moroney2015_data()["table2_cylindrical_params"]}
    return float(t2["L"][_L_BY_GRIND[grind]])


def solve(grind, n_cells=120, t_end_s=250.0, n_out=51):
    """Solve the 1-D two-grain LDF model for `grind` in {'fine','coarse'} using the CORRECTED
    (cooper2021) h_sl. Returns a dict with the exit-concentration trace and the solute mass
    budget (removed from grains vs carried out of the bed)."""
    if grind not in _L_BY_GRIND:
        raise ValueError(f"grind must be 'fine' or 'coarse', got {grind!r}")
    t2 = {r["config"]: r for r in _data.moroney2019_table2()}
    small, large = t2[f"{grind}_2g_small"], t2[f"{grind}_2g_large"]
    d1, d2 = small["d_s_m"], large["d_s_m"]
    as1, as2 = small["alpha_s"], large["alpha_s"]
    h1, h2 = small["h_sl_corrected_ms"], large["h_sl_corrected_ms"]
    cs0 = small["c_s0_kgm3"]
    alpha_l = 1.0 - as1 - as2                                  # liquid volume fraction
    area = np.pi * (_CHAMBER_ID_M / 2.0) ** 2
    v = _Q_M3_S / (alpha_l * area)                             # Darcy velocity (Eq. 19 form)
    L = _bed_height(grind)
    N = int(n_cells)
    dz = L / N
    k1 = 6.0 * h1 * as1 / (alpha_l * d1)                       # LDF gain into liquid
    k2 = 6.0 * h2 * as2 / (alpha_l * d2)
    m1 = 6.0 * h1 / (PHI_V * d1)                               # grain depletion rate
    m2 = 6.0 * h2 / (PHI_V * d2)

    def rhs(_t, y):
        cl = y[0:N]
        cs1 = y[N:2 * N]
        cs2 = y[2 * N:3 * N]
        up = np.empty(N)
        up[0] = 0.0                                            # inlet c_l(0,t)=0
        up[1:] = cl[:-1]
        dcl = -v * (cl - up) / dz + k1 * (cs1 - cl) + k2 * (cs2 - cl)
        return np.concatenate([dcl, -m1 * (cs1 - cl), -m2 * (cs2 - cl)])

    y0 = np.concatenate([np.zeros(N), np.full(N, cs0), np.full(N, cs0)])
    t_eval = np.linspace(0.0, t_end_s, n_out)
    sol = solve_ivp(rhs, [0.0, t_end_s], y0, t_eval=t_eval, method="BDF", rtol=1e-6, atol=1e-6)
    cexit = sol.y[N - 1]                                       # outlet-cell liquid concentration
    cs1_final = sol.y[N:2 * N, -1]
    cs2_final = sol.y[2 * N:3 * N, -1]
    removed = (PHI_V * as1 * float((cs0 - cs1_final).mean())
               + PHI_V * as2 * float((cs0 - cs2_final).mean())) * area * L
    carried = v * alpha_l * area * float(_trapz(cexit, sol.t))
    return dict(
        grind=grind, t_s=sol.t, cexit_kgm3=cexit,
        v_mm_s=v * 1000.0, cs0_kgm3=cs0,
        cexit_peak=float(cexit.max()), t_peak_s=float(sol.t[int(cexit.argmax())]),
        cexit_end=float(cexit[-1]),
        tau_small_s=1.0 / m1, tau_large_s=1.0 / m2,
        mass_removed_g=removed * 1e3, mass_carried_g=carried * 1e3,
        budget_closure=(carried / removed) if removed else float("nan"),
        D_v_corrected={"small": h1 * d1, "large": h2 * d2},
        D_v_reported={"small": small["h_sl_reported_ms"] * d1,
                      "large": large["h_sl_reported_ms"] * d2},
    )
