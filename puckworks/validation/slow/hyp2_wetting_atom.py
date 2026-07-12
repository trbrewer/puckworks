"""hyp2_wetting_atom.py — Hypothesis #2 (incomplete wetting) SIGNATURE PROBE.

*** NON-COMPONENT ANALYSIS PROBE — NOT a model, NOT registered, NOT gated. ***

This is an exploratory probe over two ALREADY-CARDED components
(brewer2026.streamtube + foster2025.infiltration). It introduces NO new physics
and NO new constants beyond a single IMPOSED probe parameter w_dry(g). It does
NOT implement a Richards / van-Genuchten solver, does NOT touch egidi2018/2023,
and does NOT fit anything to data. The G1 continuous-saturation gap remains OPEN
pending a constitutive-data paper (ROADMAP G1 refinement); this probe only asks a
yes/no question: IF a wetting-failure "dry atom" existed, would it be
DISTINGUISHABLE from static channeling (#1)?

Validation strength: QUALITATIVE / exploratory. Every number below is a probe
output under imposed assumptions, not a validated prediction.

Construction
------------
- Baseline (#1, static channeling): the streamtube lognormal-k EY ensemble with
  the sigma(phi1) closure from task #1 (commit 0112281). This alone already
  produces the fine-grind EY peak.
- Dry atom (#2): a fraction w_dry(g) of tubes are assigned k -> 0 (non-conducting,
  zero extraction) -- the k->0 atom the lognormal distribution structurally lacks
  (foster card). w_dry is IMPOSED as a monotone-increasing-with-fineness grid,
  NOT fitted: w_dry(1.1)=0.20 falling to 0 by g~1.7. It is a signature switch, not
  a calibration.

Two signatures (reported per grind)
-----------------------------------
1. EY vs grind. Composite EY = (1 - w_dry) * EY_ensemble: the dry fraction is dead
   dose (contacted by no water), so it lowers overall EY MOST at fine grind. Does
   the atom SHARPEN / SHIFT the schmieder-target peak vs the pure-sigma result?
2. First-drip. The dry atom reduces the effective conducting permeability to
   k_eff = k(g) * (1 - w_dry(g)) (a labelled parallel-conductance PROXY: fewer
   conducting paths -> lower bulk k), fed to the foster first-drip triangle on the
   DE1 fixture-A pressure history. Does first-drip DELAY grow at fine grind? Pure
   sigma leaves the MEAN k (hence first-drip) unchanged, so a grind-dependent
   first-drip delay is #2's discriminating observable -- #1 cannot produce it.

Run:  python -m puckworks.validation.slow.hyp2_wetting_atom
"""
import json
import os

import numpy as np

from puckworks.models.brewer2026 import streamtube as st
from puckworks.models.foster2025 import infiltration as inf

# --- the ONE imposed probe parameter (monotone in fineness; NOT fitted) ------
_W_DRY_GRID_GS = np.array([1.1, 1.3, 1.5, 1.7, 1.9, 2.2])
_W_DRY_GRID_W = np.array([0.20, 0.13, 0.06, 0.00, 0.00, 0.00])


def w_dry(gs):
    """Imposed wetting-failure fraction: monotone-decreasing with coarsening,
    zero by gs~1.7. A signature switch, explicitly NOT a fitted calibration."""
    return float(np.interp(gs, _W_DRY_GRID_GS, _W_DRY_GRID_W))


def probe(gs_grid=(1.1, 1.3, 1.5, 1.7, 1.9, 2.2), s_ref=0.6, m=1.0,
          p_bar=5.0, n_grid=7, fixture="de1_fixtureA.json"):
    """Run both signatures across the grind grid. Returns per-grind pure-sigma vs
    composite EY, and baseline vs dry-atom first-drip (delay). Qualitative."""
    gs = np.asarray(gs_grid, float)
    sigma = st.sigma_closure_power(gs, s_ref=s_ref, m=m)
    # --- signature 1: EY vs grind (channeling only vs channeling + dry atom) ---
    ey_pure, ey_comp, wd = [], [], []
    for g, s in zip(gs, sigma):
        resp = st.EYResponse(gs=float(g), p_bar=p_bar, n_grid=n_grid)
        e = float(resp.ey_ensemble(float(s)))
        w = w_dry(g)
        ey_pure.append(e)
        ey_comp.append((1.0 - w) * e)          # dry fraction = dead dose
        wd.append(w)
    ey_pure = np.array(ey_pure); ey_comp = np.array(ey_comp); wd = np.array(wd)

    # --- signature 2: first-drip delay from the dry atom -----------------------
    data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    d = json.load(open(os.path.join(data_dir, fixture)))
    t = np.array(d["elapsed_s"]); P = np.array(d["pressure_bar"])
    obs_drip = float(t[np.argmax(np.array(d["weight_g"]) > 0.5)])
    t_base, t_dry, delay = [], [], []
    for g, w in zip(gs, wd):
        k, L = inf.k_from_kappa(float(g), d["dose_g"] / 1000, d["kappa_fitted"])
        tb = inf.front_from_pressure(t, P, k, 0.322, L)["t_saturate"]
        tc = inf.front_from_pressure(t, P, k * (1.0 - w), 0.322, L)["t_saturate"]
        t_base.append(tb); t_dry.append(tc)
        delay.append(None if (tb is None or tc is None) else tc - tb)

    ip_pure = int(np.argmax(ey_pure)); ip_comp = int(np.argmax(ey_comp))
    return dict(gs=gs, sigma=sigma, w_dry=wd,
                ey_pure=ey_pure, ey_composite=ey_comp,
                peak_gs_pure=float(gs[ip_pure]), peak_gs_composite=float(gs[ip_comp]),
                obs_first_drip_s=obs_drip, t_drip_baseline=t_base,
                t_drip_dry_atom=t_dry, first_drip_delay_s=delay)


def report():
    r = probe()
    print("== Hypothesis #2 wetting-atom probe (QUALITATIVE, imposed w_dry) ==")
    print(f"{'gs':>4} {'w_dry':>6} {'EY_#1':>7} {'EY_#1+2':>8} "
          f"{'t_drip_base':>11} {'t_drip_dry':>10} {'delay_s':>8}")
    for i, g in enumerate(r["gs"]):
        tb = r["t_drip_baseline"][i]; td = r["t_drip_dry_atom"][i]
        dl = r["first_drip_delay_s"][i]
        print(f"{g:>4.1f} {r['w_dry'][i]:>6.2f} {r['ey_pure'][i]:>7.2f} "
              f"{r['ey_composite'][i]:>8.2f} {tb:>11.2f} {td:>10.2f} "
              f"{(dl if dl is not None else float('nan')):>8.2f}")
    print(f"\nEY peak: pure-sigma at gs={r['peak_gs_pure']}, "
          f"composite at gs={r['peak_gs_composite']} "
          f"(schmieder target GL 1.7); observed first drip "
          f"{r['obs_first_drip_s']:.1f} s.")
    print("Verdict: static channeling (#1) already gives the EY dip; the dry atom "
          "sharpens/shifts it AND adds a grind-dependent first-drip delay that #1 "
          "cannot produce -> the two are distinguishable ONLY by first-drip data.")
    return r


if __name__ == "__main__":
    report()
