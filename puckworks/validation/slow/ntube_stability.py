"""ntube_stability.py — Result-3 deepening: linear-stability + phase diagram of
the N-tube channeling-κ(t) concentration (SLOW ~60 s; NOT CI, per CLAUDE.md rule 3).

Companion to `docs/ANALYSIS_P2.md` §2.4 and the PAPER_OUTLINE Result-3 work list.
The N-tube union (§2.4) found that, in the tested near-choke config, an uncoupled
streamtube ensemble concentrates flow into a single channel. The review asked to
turn that numerical observation into (a) a stability analysis, (b) a flow- vs
pressure-control distinction, and (c) a phase diagram — which this module does.

(1) LINEAR STABILITY (analytical, `harness.ntube_stability_analysis`). Around the
    uniform state, a perturbation's linear amplification over the shot is the
    end-to-start conductance ratio A = (M(phi_max)/M(phi_0))^(1-lateral). Poroelastic
    M->0 at the near-choke shutoff => A diverges (UNSTABLE); Kozeny-Carman A~1.5
    (STABLE). This is the analytical origin of the numerical latch and its
    closure-dependence.

(2) CONTROL REGIME. The single-channel latch is specific to FLOW control (fixed
    total flow shared across tubes -> a fast tube STEALS -> latch). Under PRESSURE
    control (fixed dP, tubes independent -> no fixed pie) there is NO latch: the
    flow distribution stays broad. So the instability is a pump/flow-controlled
    (schmieder/DE1) phenomenon, not a pressure-controlled one.

(3) PHASE DIAGRAM. N_eff_final over heterogeneity (grind/sigma) x lateral coupling,
    for both control modes, poroelastic closure. Maps where the ensemble collapses
    (N_eff -> ~1) vs stays distributed.

All exploratory / qualitative (NOT a registered component; a *physical* lateral-
coupling model is card-blocked, CLAUDE.md rule 1 -- the lateral term here is a
homogenizing proxy). Run:  python -m puckworks.validation.slow.ntube_stability
"""
from puckworks import harness as h


def report():
    print("== (1) linear-stability analysis ==")
    st = h.ntube_stability_analysis()
    for name, d in st["closures"].items():
        print("  %-11s A=%.3g (log10 %.1f) unstable=%s | numeric N_eff_final=%.2f"
              % (name, d["amplification_A"], d["log10_A"], d["unstable"],
                 d["n_eff_final_numeric"]))
    print("  ", st["verdict"])

    print("\n== (2) control regime (poroelastic, gs 1.1) ==")
    for ctrl in ("flow", "pressure"):
        x = h.ntube_kappa_t_union(gs=1.1, N=150, closure="poroelastic",
                                  control=ctrl, compute_ey=False)
        print("  %-9s: N_eff_final=%.1f  max_single_tube=%.3f  concentrates=%s"
              % (ctrl, x["n_eff_channels_final"], x["max_single_tube_share_final"],
                 x["concentrates"]))
    print("  -> the single-channel latch is FLOW-control-specific; pressure control "
          "keeps the distribution broad.")

    print("\n== (3) phase diagram: N_eff_final over grind x lateral, both controls ==")
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
