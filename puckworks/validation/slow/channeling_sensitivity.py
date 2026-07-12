"""channeling_sensitivity.py — closure-sensitivity of the P3 Result-1 interior
grind maximum (SLOW ~90 s; NOT CI, per CLAUDE.md rule 3).

Companion to `docs/ANALYSIS_P2.md` §2.3 and the PAPER_OUTLINE Result-1 reanalysis.
The P3 verdict is model-CAPACITY (the empirically-calibrated static-heterogeneity
closure is the only implemented generator that makes an interior grind maximum
without a doctored constant) — NOT identification. This module quantifies HOW
robust that interior-max is to the empirical sigma(phi1) closure, which the review
asked for: does peak formation depend on s_ref, exponent m, grid resolution, and
pressure?

Method (`harness.channeling_interior_max_sensitivity`): the streamtube EYResponse
spline depends only on (gs, p_bar, n_grid), not on the closure (s_ref, m), so the
s_ref x m grid reuses one build. Three probes — (1) s_ref x m grid at the
calibrated pressure/resolution: fraction of closure combos that yield an interior
max, with peak-location and prominence (ensemble EY at the peak minus the higher
endpoint, in EY-points); (2) pressure sweep at the calibrated closure; (3) n_grid
convergence at the calibrated closure.

Result: the interior-max is REAL and n_grid-CONVERGED at the calibrated closure
(so not a resolution artifact) but FRAGILE (present in only ~40 % of the s_ref x m
grid; it vanishes for weak channeling / low s_ref) and WEAK (median prominence
< ~0.2 EY-point; near-flat ~0.03 EY-point at the espresso-relevant 9 bar, where
the peak also drifts to a different grind). This fragility+weakness on the MODEL
side mirrors the weak-RSM / monotone-raw-cell picture on the schmieder TARGET side
— together they support "model capacity, not identification", and they say the
title/abstract must NOT rest on a robust channeling peak.

Run:  python -m puckworks.validation.slow.channeling_sensitivity
"""
from puckworks import harness as h


def report():
    r = h.channeling_interior_max_sensitivity()
    c = r["calibrated"]
    print("== P3 Result-1 closure-sensitivity ==")
    print("gs grid:", [round(x, 2) for x in r["gs_grid"]])
    print("calibrated (s_ref=%.2f m=%.2f p=%.0f n=%d): interior=%s peak_gs=%.2f "
          "prominence=%.3f EY-pt"
          % (c["s_ref"], c["m"], c["p_bar"], c["n_grid"], c["interior"],
             c["peak_gs"], c["prominence"]))
    print()
    print("(1) s_ref x m grid: interior-max in %d/%d (%.0f%%); peak_gs %s"
          % (r["grid_interior_n"], r["grid_n"], 100 * r["grid_interior_fraction"],
             r["peak_gs_range"]))
    print("    prominence: interior-only median %.3f max %.3f | FULL-GRID median %.3f "
          "IQR %s EY-pt (full-grid median is the honest central tendency)"
          % (r["prominence_median"], r["prominence_max"],
             r["prominence_median_fullgrid"], r["prominence_iqr_fullgrid"]))
    print("    non-interior (s_ref,m):", r["grid_noninterior"])
    print("(2) pressure sweep:", [(x["p_bar"], x["interior"], round(x["peak_gs"], 2),
                                   round(x["prominence"], 3)) for x in r["pressure_sweep"]])
    print("(3) n_grid convergence (converged=%s):" % r["n_grid_converged"],
          [(x["n_grid"], round(x["peak_gs"], 2), round(x["prominence"], 3))
           for x in r["n_grid_convergence"]])
    print()
    print("VERDICT:", r["verdict"])

    # concavity audit (Jensen premise; review Priority 3.1)
    ca = h.channeling_concavity_audit()
    print()
    print("== EY(k) concavity audit (Jensen premise) ==")
    print("min concave fraction %.3f; max clip mass %.4f; worst direct Jensen gap "
          "%.3f EY-pt (all <=0: %s) -> %s" % (
        ca["min_concave_fraction"], ca["max_clip_mass"], ca["max_jensen_gap_EYpt"],
        ca["all_jensen_gaps_negative"], ca["verdict"]))

    # magnitude comparison: model bump vs raw schmieder bump (both EY-pts)
    m = h.result1_magnitude_comparison()
    print()
    print("== Result-1 MAGNITUDE comparison (model bump vs schmieder response) ==")
    print("raw TDS-EY %s -> mid-vs-2.0 contrast %.3f EY-pt, Welch 95%% CI %s "
          "(excludes 0 -> monotone); within-cell std %.3f (descriptive)"
          % (m["raw_tds_ey"], m["raw_mid_vs_endpoint_contrast_EYpt"],
             m["raw_contrast_welch_ci95"], m["raw_within_cell_std_EYpt"]))
    print("model channeling bump: %.3f (5 bar) / %.3f (9 bar) EY-pt; < within-cell "
          "var=%s (no formal MDE)"
          % (m["model_prominence_5bar_EYpt"], m["model_prominence_9bar_EYpt"],
             m["model_bump_lt_within_cell_var"]))
    print("RSM: refit %.2f g vs printed %.2f g vs data %.2f g -> shape tool by "
          "PRINTED-COEFF ROUNDING, not a 1.7x overprediction"
          % (m["rsm_refit_central_g"], m["rsm_printed_central_g"], m["rsm_raw_central_g"]))
    print("VERDICT:", m["verdict"])
    return dict(sensitivity=r, magnitude=m)


if __name__ == "__main__":
    report()
