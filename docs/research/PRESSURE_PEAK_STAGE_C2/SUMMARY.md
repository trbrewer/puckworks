# PRESSURE-PEAK Stage C2: constrained onset threshold

**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.**

56 brews; 11 held-out conditions; 200 paired draws, seed 20261105. Only change: onset P0 ≤ min(5, min(training Pe) − 0.01) bar. T2-F flow P0 remains uncapped. Peak grades use C1’s nominal-condition peak intervals.

| Fit | Accuracy | Peak | Slope | Trends | Onset | Low bias |
|---|---|---|---|---|---|---|
| T2-F | NEAR | MEETS | NEAR | NEAR | NEAR | MEETS |
| T2 joint (capped) | NEAR | MEETS | MEETS | MEETS | MISSES | MISSES |
| C0 joint (capped) | NEAR | MEETS | NEAR | MEETS | NEAR | MISSES |

| Fit | Pd [95%] | Pstar [95%] | P0 [95%] (bar) |
|---|---|---|---|
| T2-F | 3.984 [3.233, 4.756] | 12.213 [10.255, 14.814] | 1.279 [1.118, 1.442] |
| T2 joint (capped) | 3.655 [3.150, 4.132] | 18.191 [16.637, 20.411] | 0.662 [0.549, 0.756] |
| C0 joint (capped) | — | 6.422 [6.121, 6.661] | 0.729 [0.628, 0.819] |

Paired onset/flow consistency: Pd MEETS (gap 0.000 bar); P0 NEAR (gap 0.346). Pstar ungraded.

| Fit | Flow peak; analytic | Onset minimum; analytic | Endpoint / trace / onset RMSE | Slope [95%] | Low bias; residuals 1 / 2 / 3.5 bar; MAE |
|---|---|---|---|---|---|
| T2-F | 6.90 [6.70, 7.00]; 6.89 [6.72, 7.02] | 4.55 [2.35, 5.05]; 4.53 [2.37, 5.07] | 0.180 / 0.274 / 3.522 | -0.1193 [-0.1483, -0.0942] | +0.080; -0.093 / -0.164 / +0.498; 0.252 |
| T2 joint (capped) | 7.20 [6.70, 7.45]; 7.22 [6.71, 7.45] | 4.35 [3.75, 4.65]; 4.33 [3.76, 4.65] | 0.210 / 0.301 / 6.377 | -0.0551 [-0.0697, -0.0392] | +0.300; -0.092 / +0.442 / +0.551; 0.362 |
| C0 joint (capped) | 7.15 [6.95, 7.35]; 7.15 [6.93, 7.34] | 7.15 [6.95, 7.35]; 7.15 [6.93, 7.34] | 0.200 / 0.292 / 3.858 | -0.1143 [-0.1365, -0.0965] | +0.274; -0.089 / +0.402 / +0.509; 0.334 |

Extrema: fold median [range], 0.05-bar grid; observed flow/onset: 6.1/3.5 bar. Analytic extrema exclude mass memory. Units: flow g/s; onset s; slope g/s/bar.

| Onset fit | Cap: point folds / 11; full | Refit folds / 2200; full draws / 200 | Min training margin: point / refits (bar) | Held-out floor uses: point / refits |
|---|---|---|---|---|
| T2 onset-only (capped) | 0; 0 | 0; 0 | 0.334381 / 0.047420 | 0 / 0 |
| T2 joint (capped) | 0; 0 | 0; 0 | 0.206684 / 0.046031 | 4 / 847 |
| C0 T1-W onset-only (capped) | 0; 0 | 0; 0 | 0.334367 / 0.047407 | 0 / 0 |
| C0 joint (capped) | 0; 0 | 9; 1 | 0.148237 / 0.010000 | 4 / 815 |

All 9,648 training-margin checks succeed; no active training floor. CSV lists every ungraded held-out floor use and prediction. Held-out 1-bar onset predictions (1-1, 1-2, 1-3, 1-4, 1-5b; s): T2-F 12.74 / 12.67 / 12.77 / 12.77 / 12.77; T2 joint (capped) 78.67 / 23.01 / 76.07 / 76.41 / 76.46; C0 joint (capped) 14.32 / 14.31 / 14.32 / 14.32 / 14.32.

C1 T2-F endpoint/trace RMSE was 0.193/0.287 g/s. Its low/high Pd groups (158/42 draws) had analytic flow 6.460/6.812 and onset 3.216/4.249 bar. Full C1, C0 T1/joint, E1, F1 and B1 comparisons and onset-only estimates are in CSV.

Restart: Full relaxation of the whole-bed factor bounds the restart jump at exp(P_r/Pstar). With P_r = 8.389625 bar, matching the low end of the observed ratio (1.747450) requires Pstar <= 15.030932 bar, and matching the high end (2.349328) requires Pstar <= 9.822430 bar. If the T2-F Pstar interval lies wholly above the low-end limit, relaxation of the whole-bed term cannot account for the restart rise within T2; if it overlaps, it is not excluded. Ungraded; one qualitative record.

C2 T2-F hypothetical gain 1.988 [1.762, 2.266]×; not excluded by this upper-bound check. T2 has no relaxation state and predicts no pause benefit.

Flow identities: rtol=1e-12; C1 resampling matches exactly. Runtime 11.41 min cumulative wall / 7.46 refit CPU h; two-hour wall cap retained. [Full results and audits](RESULT_TABLE.csv) · [Figure](FIGURE.png). Waszkiewicz et al. (2025), Zenodo 18046315, CC-BY-4.0.
Runtime includes interrupted BLAS oversubscription: 3.67 min / 5.54 CPU h. Resumed with one BLAS thread per worker; all draws retained.

**Recommendation:** Review held-out onset extrapolation before selecting further work.
