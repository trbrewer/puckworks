# Joint-clock result detail

Final held-out capability scores use 0.005 s with the fitted parameters frozen. Each arm has all 56 brews available; no brew is dropped and no unavailable prediction is converted to censoring. The retained screen references are re-scored without new fits. This record expands the one-page SUMMARY; it creates no additional grading criterion.

## All four predeclared weights

Each cell is **onset RMSE or bound (s) / primary-trace flow RMSE (g/s) / 1-bar detections**. λ=1 remains primary.

| λ | J0 | J1 | J2 |
|---|---|---|---|
| 0.05 | ≥18.180 / 0.2725 / 1/5 | ≥8.697 / 0.2789 / 1/5 | ≥8.968 / 0.2684 / 1/5 |
| 0.5 | ≥18.870 / 0.2921 / 0/5 | ≥8.587 / 0.2781 / 1/5 | ≥8.219 / 0.2715 / 1/5 |
| 1 | ≥18.785 / 0.3263 / 0/5 | ≥8.598 / 0.2783 / 1/5 | ≥8.336 / 0.2744 / 1/5 |
| 2 | 10.786 / 1.1769 / 5/5 | 3.717 / 0.2915 / 5/5 | ≥8.557 / 0.2794 / 1/5 |

All arms detect all four 2-bar brews. At 1 bar, primary J0 detects zero of five; J1/J2 detect one of five. At λ=2, J0 and J1 detect five of five, but J0 sacrifices flow accuracy. J1 λ=2 has a 1-bar detector median of 35.178 s versus observed 25.058 s: detection is repaired, the signed error remains +10.120 s. Its full-cohort onset score is 3.717 [2.402, 5.580] s (NEAR); its inherited high-pressure slope grade is MISSES. All other joint onset grades are MISSES. The grade uses the point score/bound and the inherited bands, not a newly imposed interval gate.

[COMPARISON_TABLE.csv](COMPARISON_TABLE.csv) contains endpoint, primary and companion scores for every arm, B1 and D0. [NUMERICAL_SCORES.csv](NUMERICAL_SCORES.csv) places every 0.005-s score beside its 0.02-s sensitivity. [LOSS_BY_PRESSURE.csv](LOSS_BY_PRESSURE.csv) separates held-out F, O and λO for all eleven pressures, all weights and both steps; [TRAINING_LOSS_COMPONENTS.csv](TRAINING_LOSS_COMPONENTS.csv) retains the training diagnostics separately. F uses the fixed D0 fitting support, which differs from FORM_A reporting masks.

## Matched paired comparisons

Each pair uses the same 1,000 condition-then-whole-brew draws (seed 20261103), retaining both scores and their paired difference. These intervals are conditional on fitted parameters and fixed training-derived Mc, with no refit bootstrap. Intervals for censored scores describe computed lower bounds; differences between such bounds are not bounds on unknown true-RMSE differences.

| Primary pair | Endpoint difference [95%], g/s | Primary trace difference [95%], g/s | Difference of computed onset bounds [95%], s |
|---|---|---|---|
| J1−J0 | -0.0134 [-0.1137, +0.0868] | -0.0480 [-0.1256, +0.0186] | -10.19 [-12.22, -8.28] |
| J2−J0 | -0.0074 [-0.1072, +0.0908] | -0.0519 [-0.1269, +0.0139] | -10.45 [-12.57, -8.42] |
| J2−J1 | +0.0060 [-0.0093, +0.0193] | -0.0039 [-0.0121, +0.0043] | -0.26 [-0.84, +0.40] |
| J0−D0 | +0.0624 [-0.0315, +0.1661] | +0.0587 [-0.0003, +0.1238] | +0.81 [-0.10, +3.38] |
| J1−D0 | +0.0490 [+0.0092, +0.0813] | +0.0106 [-0.0237, +0.0465] | -9.38 [-11.42, -6.95] |
| J2−D0 | +0.0550 [+0.0198, +0.0884] | +0.0068 [-0.0219, +0.0343] | -9.64 [-11.81, -6.95] |

The added D0 beverage observer is a diagnostic, not a historical onset result. [PAIRED_COMPARISONS.csv](PAIRED_COMPARISONS.csv) includes both scores, companion traces, every weight and all three joint contrasts plus the separate D0 contrasts. At λ=2, J1−J0 onset RMSE is −7.068 [−9.030, −5.102] s with no censoring. J1−D0 endpoint RMSE rises +0.0749 [+0.0123, +0.1323] g/s. J2 provides no resolved incremental onset gain at the primary weight, and its front/lag decomposition is weakly identified. Some sensitivity comparisons improve flow (λ=0.05 J2−J1 primary trace −0.01045 [−0.01889, −0.00208] g/s), without resolving the full-cohort problem.

## Pressure response and clocks

| Primary arm | Endpoint residual at 1 / 2 / 3.5 bar, g/s | ≥9-bar slope, g/s/bar | Nominal peak grade |
|---|---|---|---|
| J0 | -0.0800 / +0.0245 / +0.3944 | -0.17324 (NEAR) | MEETS |
| J1 | -0.0160 / +0.1224 / +0.5173 | -0.07465 (MEETS) | MEETS |
| J2 | -0.0326 / +0.1648 / +0.4573 | -0.07823 (MEETS) | MEETS |

The slope is the inherited regression on the 9/11/13-bar condition means. Pooled held-out columns combine three different fold fits, not one constitutive curve.

**In-sample counterexample:** the descriptive J1 λ=1 curve detects 1-bar onset at **18.6 s** (observed **25.06**), with endpoint flow **0.112 g/s** and 9–13-bar slope **−0.0808 g/s/bar**. Pooled held-out slope columns combine three different fold fits; they are not one constitutive curve. [Retained sweep](DESCRIPTIVE_SWEEP.csv).

 Individual hydraulic residuals remain in GRADES.csv and FLOW_BY_BREW.csv; detector-median errors are different quantities and remain in ONSET_BY_PRESSURE.csv. The supplementary 3.5–13-bar condition-median RMS suppresses within-condition variation and never replaces the 56-brew score or per-brew rows.

Primary J2 unshifted bed / shifted scale RMSE is endpoint 0.2210 / 0.2080, primary trace 0.2638 / 0.2744, companion trace 0.3241 / 0.2755 g/s. The lag shifts scored liquid flow and beverage mass; pressure, wetting, chemistry and recovery keep their bed clocks. [Every weight/step decomposition](J2_BED_SCALE.csv). The fitted scale lag has an unidentified physical mechanism; it may compensate for recovery, observer, initial-state or clock assumptions.

D0’s capacity peak 6.00 [5.77, 6.27] bar has its historical parameter-refit interval. The joint models’ descriptive finite-time flow peaks are numerical sweep interpolations with no statistical interval. They are distinct from held-out nominal peak grades and fixed-parameter resampling intervals. Each descriptive sweep uses one common tuple, constant forcing, 100-s horizon and the same 23 pressures; no extra sweep was run. [EXTREMA.csv](EXTREMA.csv) records front, detector and flow extrema for every model/weight, ties, boundary minima and censor-obscured minima. Pw is J2’s analytic constant-pressure front minimum, not a detector minimum. J0/J1 fronts are pressure-flat, so they have no unique pressure optimum.

## Identification and search limitations

All 2,592 scheduled starts terminated; the selected fit is the lowest finite evaluated training objective, including intermediate trials and starts, not necessarily the terminal Powell vector. Every selected trial has a distinct exact objective among recorded trials. That bookkeeping does not establish identification or a global optimum: the objective is sampled and partly flat, and the finite multistart search is not exhaustive. FITS.csv lists every selected vector, Mc, boundary distance, exact-tie ranges and detection counts. OPTIMIZER_STARTS.csv retains competing terminal solutions.

**τ0 point estimates:** DESCRIPTIVE_ALL across weights **11.60–13.58 s**; ordinary folds at λ=1 **13.14–13.96 s**. These come from overlapping training sets, are not uncertainty intervals, and are not a measured wetting duration. [Fits](FITS.csv). J2 k_w0 spans 3.4942×10⁻¹⁵–3.2106×10⁻¹⁴ m², Pw 3.276–5.158 bar and t_s 3.972–11.002 s. Training sets overlap heavily, so fold stability does not identify a mechanism. J2’s descriptive selected objective is 0.705153 at Pw=3.5969 bar and t_s=10.3459 s. Two retained terminal solutions have objectives 0.707818 and 0.717208, with (k_w0, Pw, t_s)=(1.9626×10⁻¹⁴, 3.5968, 10.4055) and (4.4903×10⁻¹⁵, 4.9264, 5.6707). These similar criteria with different front/lag and flow parameters show weak identification; no equivalence threshold is imposed.

J0 λ=2 is especially unstable: in the 1-bar-held-out fold Pstar reaches its declared 100-bar upper bound (100.00000000000004 numerically), n grows to 1,116,894.54 and Pd=0.53991 bar. n had no declared upper fitting bound; no bound was added after seeing this result. The 8-bar-held-out Pstar is also near its upper bound. These estimates and J0’s poor flow response are retained, not clipped or replaced.

## Numerical verification and provenance

The largest 0.005-minus-0.02-s detector change is 0.100 s on a descriptive constant case and 0.094 s on a held-out brew (J0 λ=2, brew 6-2). No detection/non-detection outcome changes. The largest flow-RMSE change is +0.0000402648 g/s (J2 λ=.05 companion trace); the largest onset-score change is −0.008169 s (J0 λ=2). [Per-case numerical evidence](NUMERICAL_CHECKS.csv). No timestep threshold or new gate was introduced.

Saved D0 replay returns endpoint 0.1530012356 and own-support trace 0.2541847394 g/s. The common-mask D0 benchmark gives 0.1530014554/0.2676297208/0.3448577769 g/s endpoint/primary/companion. The first check reproduces historical conventions; the latter compares FORM_A masks and retained forcing. They are not interchangeable.

All 144 unique fit problems and 948 complete .005/.02-s case pairs are reconciled by frozen hashes. Six original attempts failed when Powell extrapolated a delay microscopically below its declared zero bound; their original failed records and 8.52394 core-hours remain. Continuations enforce the same declared domain and complete the remaining original starts. The original driver’s failure exit remains disclosed. The evaluator’s metadata boolean cast changes no numerics; earlier valid outputs and interrupted arrays remain intact. One failed diagnostic replay and an interrupted serialization case have unmeasured CPU overhead, explicitly disclosed rather than invented. Development/test/render overhead is outside the scientific execution total. See RUN_MANIFEST.json and METHODS.md.

The source files were inspected and authenticated: waszkiewicz2025/traces_per_brew, Zenodo 18046315, CC-BY-4.0; 56 distinct brews after the inherited alias rule. R0 chemistry retains engineering assumptions; matching native traces verifies the implementation, not physical chemistry. The inherited 102-case native verification and its coverage/qualification limits are linked by hash in VERIFICATION.json. Native traces, trial histories, failed records and prediction arrays remain outside Git. No EWP results were changed.

J1 is the parsimonious timing reference among the tested coupled models. At primary λ=1 it substantially reduces the computed onset-error bound, but four 1-bar brews remain undetected and endpoint error is higher than D0. J2 has no resolved incremental onset gain at the primary weight, and its front/lag decomposition is weakly identified. The λ=2 J1 sensitivity detects all 56 brews and reaches onset NEAR, while its 1-bar median remains 10.12 s late and the pooled held-out high-pressure slope becomes too flat. No evaluated held-out calibration repairs all the timing and flow features. These results identify a remaining low-pressure prediction problem under the fixed recovery and observation assumptions; they do not establish that Form A is incapable of combining low-pressure detection with a high-pressure downturn.
