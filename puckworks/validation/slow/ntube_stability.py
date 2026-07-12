"""ntube_stability.py — Result-3: finite-time concentration + phase map of the
N-tube channeling-κ(t) model (SLOW ~60 s; NOT CI, per CLAUDE.md rule 3).

Companion to `docs/ANALYSIS_P2.md` §2.4. The N-tube union (§2.4) found that, in
the tested near-choke config, an uncoupled streamtube ensemble concentrates flow
into a single effective channel. **This is an EXPLORATORY finite-time result, NOT
a stability theorem** (downgraded 2026-07-12 after the PAPER_B review):

(1) FINITE-TIME GAIN (`harness.ntube_finite_time_gain`). A perturbation grows, to
    leading order under fixed-flow, by the conductance ratio G=(M_f/M_0)^(1-lat).
    But M_0->0 at the near-choke shutoff, so the poroelastic G is FLOOR-DEPENDENT
    (scales ~1/floor) -- it is NOT a floor-independent eigenvalue, and its
    magnitude is not meaningful. Kozeny-Carman G~1.5 is floor-independent. The
    ROBUST, measured result is the numerical concentration (N_eff), not G.

(2) CONTROL REGIME. The single-channel concentration is specific to FLOW control
    (fixed total flow shared -> a fast tube STEALS -> N_eff->1). Under PRESSURE
    control (independent tubes) there is NO such collapse (N_eff stays ~84). A
    pump/flow-controlled phenomenon.

(3) PHASE MAP. N_eff_final over grind x homogenization, both control modes,
    poroelastic closure. Maps where the ensemble concentrates vs stays distributed.

All exploratory / qualitative (NOT a registered component; a *physical* lateral-
coupling model is card-blocked, CLAUDE.md rule 1 -- the lateral term here is a
homogenizing proxy). A genuine stability result needs a physical lateral operator
+ a Jacobian / finite-time-Lyapunov analysis (open). Run:
`python -m puckworks.validation.slow.ntube_stability`
"""
from puckworks import harness as h


def report():
    print("== (1) finite-time gain (floor-dependent -> NOT a stability eigenvalue) ==")
    st = h.ntube_finite_time_gain()
    for name, d in st["closures"].items():
        print("  %-11s gain-by-floor %s  floor_sensitive=%s | numeric N_eff_final=%.2f"
              % (name, d["finite_time_gain_by_floor"], d["gain_is_floor_sensitive"],
                 d["n_eff_final_numeric"]))
    print("  ", st["verdict"])

    print("\n== (2) control regime (poroelastic, gs 1.1) ==")
    for ctrl in ("flow", "pressure"):
        x = h.ntube_kappa_t_union(gs=1.1, N=150, closure="poroelastic",
                                  control=ctrl, compute_ey=False)
        print("  %-9s: N_eff_final=%.1f  max_single_tube=%.3f  concentrates=%s"
              % (ctrl, x["n_eff_channels_final"], x["max_single_tube_share_final"],
                 x["concentrates"]))
    print("  -> the single-channel concentration is FLOW-control-specific; pressure "
          "control keeps the distribution broad.")

    print("\n== (3) phase map: N_eff_final over grind x homogenization, both controls ==")
    grinds = (1.1, 1.5, 2.0)
    laterals = (0.0, 0.3, 0.6, 0.9)
    for ctrl in ("flow", "pressure"):
        print("  control=%s   " % ctrl + "  ".join("lat=%.1f" % L for L in laterals))
        for gs in grinds:
            cells = []
            for L in laterals:
                x = h.ntube_kappa_t_union(gs=gs, N=150, closure="poroelastic",
                                          lateral=L, control=ctrl, compute_ey=False)
                cells.append("%6.1f" % x["n_eff_channels_final"])
            print("    gs=%.1f      " % gs + "  ".join(cells))
    print("  (N_eff_final of 150 tubes; ~1 = single-channel latch, ~150 = uniform)")
    return st


if __name__ == "__main__":
    report()
