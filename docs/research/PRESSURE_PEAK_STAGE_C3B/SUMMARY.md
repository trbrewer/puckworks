# PRESSURE-PEAK C3b: T3-O onset observer

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** EXPLORATORY; ungraded.

The screen fits seven parameters to 56 brews: DESCRIPTIVE_ALL plus 11 LOCO folds. All 48 starts ran. In-sample fits can mislead and point LOCO does not replace paired refits.

C2 objective replays precede comparison: T2-F saved 0.0719361259858887, recomputed 0.0719361259858887; T2 joint (capped) saved 0.7389509324955357, recomputed 0.7389509324955357. Both agree at rtol=1e-12. T2-F's replay is unscaled flow loss; on the common 0.437 g/s and 4.534 s joint scales its objective is 0.669226.

The full-cohort joint objective is 0.755662. Selected parameters (a, Pstar, P0f, Pd, P0o, b, t0) are 1.102, 12.63, 0.7368, 4.039, 0.4524, 4.37, 9.043. Units are g/s/bar for a, bar for pressures, s·bar for b and s for t0.

| Held-out metric | T3-O | C2 T2-F | C2 T2 joint (capped) |
|---|---:|---:|---:|
| Endpoint RMSE, g/s | 0.2089 | 0.1798 | 0.2099 |
| Trace RMSE, g/s | 0.2979 | 0.2743 | 0.3013 |
| Onset RMSE, s | 10.3354 | 3.5224 | 6.3771 |
| Low-pressure bias, g/s | 0.3075 | 0.0804 | 0.3004 |
| Low-pressure MAE, g/s | 0.3606 | 0.2515 | 0.3616 |
| >=9-bar slope, g/s/bar | -0.1171 | -0.1193 | -0.0551 |

The LOCO median 100-s flow peak is 6.45 bar versus C2 T2-F's 6.90 bar; the observer-onset minimum is 4.75 bar. Held-out 1-bar censoring is 4/5. Its predicted onsets / recorded ends (s), in brew order, are 1-1: 120.97/120.97; 1-2: 16.08/142.79; 1-3: 122.20/122.20; 1-4: 121.26/121.26; 1-5b: 142.87/142.87.

No selected fit censors a training brew; none receives the possible plateau artefact label.
Start objectives disagree in 11/12 fits. The 1-bar holdout pins P0o at -5 bar; no other selected bound/proximity flag occurs. Training and held-out onset-floor uses are zero. Four full-cohort 1-bar predictions have flow below 0.1 g/s at onset or within the following 2 s; held-out drop-back flags are zero. In the other eleven fits, halving the finite-difference step changes the Jacobian by 0.9995 to 0.9998 in relative norm near crossing switches. Optimizer convergence does not establish a smooth optimum. The CSV retains all starts, initial/final censor counts, diagnostics, condition residuals and fold extrema.

Pre-declared reading: **kink flow law cannot support T3-O**. This is a capability screen, not a physical conclusion. C3 is not authorized; return to owner.

Cumulative wall time through output: 2110.70 s; serial, one BLAS thread, two-hour cap. [Full results and CI fixtures](RESULT_TABLE.csv). Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0. Earlier stages and source data are unchanged.
