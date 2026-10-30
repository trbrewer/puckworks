# PRESSURE-PEAK graded scorecard

Retrospective re-score of saved fits. Raw pressure primary; basket pressure reported separately as sensitivity. No refitting.

Grades measure capability on retrospective data, not validation. Bands were set by the owner before results were produced.

Grades: MEETS / NEAR / MISSES per criterion — accuracy vs that stage's B1 (TIE or BETTER; NEAR = UNRESOLVED with lower RMSE), peak location (5–7 bar; NEAR = one grid step beyond), slope ≥9 bar vs observed interval, resolved late-trend signs (≥4/5, 3/5). No overall PASS; ranking is advisory.

<details>
<summary>Owner-set criteria and grading bands (verbatim; read before results)</summary>

Grades are MEETS, NEAR or MISSES. There is no overall PASS.

1. Criterion 1, accuracy versus that stage's B1. Use the stage's existing paired comparison and ±0.25 g/s tie band:
   MEETS  = TIE or BETTER.
   NEAR   = UNRESOLVED, and the candidate's point endpoint RMSE is lower than B1's.
   MISSES = WORSE, or UNRESOLVED with a higher point RMSE.
   Still report % change versus B1 and trace RMSE.
2. Peak location. Observed: 6 [5, 6] bar on the nominal grid 1, 2, 3.5, 4, 5, 6, 7, 8, 9, 11, 13.
   MEETS  = the candidate's saved peak interval overlaps 5–7 bar.
   NEAR   = it overlaps 4 or 8 bar (one grid step beyond 5–7) but not 5–7.
   MISSES = otherwise.
   ALSO report a continuous model peak: evaluate the saved fold parameters on a 0.05-bar grid from 1 to 13 bar, holding every other input at that stage's convention. Report the median across folds and the fold range.
   For the data, report a continuous observed-peak estimate: fit a quadratic to the condition means at 4, 5, 6, 7 and 8 bar, with a whole-brew bootstrap (1,000 resamples, seed 20261102).
   The continuous values are descriptive only; the grade uses the saved interval.
3. High-pressure slope at or above 9 bar. Observed: −0.0655 [−0.0880, −0.0403] g/s/bar.
   MEETS  = the candidate's saved slope interval overlaps the observed interval.
   NEAR   = the interval lies entirely within [−0.176, −0.020] but does not overlap the observed interval.
   MISSES = otherwise (any non-negative or zero-crossing slope is a MISS).
4. Criterion 4, late trends. Score only the conditions where the observed late trend is resolved: 2, 3.5, 4, 5 and 6 bar, all rising (B0b LATE_TRENDS.csv).
   MEETS  = ≥4/5 matching signs.
   NEAR   = 3/5.
   MISSES = ≤2/5.
   Also report the original x/11 count in a separate, ungraded column.
   Confirm the resolved set from LATE_TRENDS.csv. If it differs from the five listed, use the file and report the difference.
5. Wetting-timing consistency: B0d rows only. Report whether the air-inclusive conductance-peak interval overlaps the matching timing interval, as YES or NO. Write NOT_SCORED for other stages.
6. Complexity: the number of fitted parameters, plus an EXPLORATORY or INELIGIBLE flag. This is reported, not graded.
7. Restart direction: copy each stage's restart statement. This is reported, not graded.

</details>

<!-- scorecard-results -->

| Candidate | Stage | Accuracy | Peak | Slope | Trend | Timing | Complexity | Restart |
|---|---|---|---|---|---|---|---|---|
| C1-exp | A | MEETS | MISSES | MISSES | NOT_SCORED | NOT_SCORED | 2 | cannot say |
| C3 | A | MEETS | MISSES | MISSES | NOT_SCORED | NOT_SCORED | 3 | cannot say |
| C4 | A | MEETS | NEAR | NEAR | NOT_SCORED | NOT_SCORED | 3 | higher* |
| B1 | A | MEETS | NEAR | MISSES | NOT_SCORED | NOT_SCORED | 3 REFERENCE | cannot say |
| D1 | B0 | MEETS | MEETS | MISSES | NOT_SCORED | NOT_SCORED | 3 | unused |
| D2 | B0 | MEETS | MISSES | MISSES | NOT_SCORED | NOT_SCORED | 3 | unused |
| C4 | B0 | MEETS | NEAR | MEETS | NOT_SCORED | NOT_SCORED | 3 | unused |
| B1 | B0 | MEETS | NEAR | MISSES | NOT_SCORED | NOT_SCORED | 3 REFERENCE | unused |
| C4 | B0b | NEAR | NEAR | MEETS | MEETS | NOT_SCORED | 3 | NOT_AVAILABLE |
| D1 | B0b | NEAR | MEETS | NEAR | MEETS | NOT_SCORED | 3 | NOT_AVAILABLE |
| D2 | B0b | NEAR | MISSES | MISSES | NEAR | NOT_SCORED | 3 | NOT_AVAILABLE |
| D3 | B0b | NEAR | NEAR | NEAR | MEETS | NOT_SCORED | 5 EXPLORATORY | NOT_AVAILABLE |
| B1 | B0b | MEETS | NEAR | MISSES | NEAR | NOT_SCORED | 3 REFERENCE | NOT_AVAILABLE |
| E1 | B0c | MEETS | NEAR | MEETS | MEETS | NOT_SCORED | 3 + 3n | unused |
| E3 | B0c | MEETS | MEETS | MISSES | MEETS | NOT_SCORED | 3 + 3n | unused |
| E2 | B0c | MEETS | MEETS | MEETS | MEETS | NOT_SCORED | 3 + 1n INELIGIBLE | unused |
| B1 | B0c | MEETS | NEAR | MISSES | NEAR | NOT_SCORED | 3 REFERENCE | unused |
| F1 | B0d | MEETS | MEETS | MISSES | MEETS | NO | 3 + 1n | NOT_AVAILABLE |
| F2 | B0d | MEETS | MEETS | MISSES | MEETS | NO | 3 + 1n | NOT_AVAILABLE |
| B1 | B0d | MEETS | NEAR | MISSES | NEAR | NOT_AVAILABLE | 3 REFERENCE | NOT_AVAILABLE |

B0c/E1, B0d/F1 lead: E1 matches the endpoint capability, high-pressure slope and resolved late-trend bands, while F1 matches endpoint capability, the saved peak interval and resolved trends. E1's saved peak interval remains one grid step high; F1 declines too steeply and its air-inclusive conductance peak disagrees with wetting timing. E1 therefore looks like a peak-location near miss on these criteria, whereas F1 retains a mechanism-consistency shortfall; neither interpretation establishes physical validation.

**Advisory leaders:** 1. B0c/E1; 2. B0d/F1. Full ranking and diagnostics below.

**Main limits:** E1 — peak location (NEAR); F1 — high-pressure slope (MISSES).

**Owner choice:** select E1 for a bounded EWP reproduction exercise; it leads the capability ranking without a missed graded criterion, while its peak-location and weaker aggregate-check limitations must remain explicit. No implementation is started.

**Second recommended action:** Test whether modelling the measured start-up pressure ramp (rather than constant pressure) moves the predicted flow peak toward 6 bar, using saved fits only.

Trigger uses the largest absolute effect (0.196 g/s), which exceeds half the typical eligible-candidate endpoint RMSE (0.242/2 = 0.121 g/s); the typical absolute effect (0.022 g/s) is below that threshold.

<details><summary>Full advisory ranking, replay checks, ramp effects, methods and sources</summary>

**Advisory ranking:** 1. B0c/E1 (3 MEETS, 0 MISSES, RMSE/B1 0.845); 2. B0d/F1 (3 MEETS, 1 MISSES, RMSE/B1 0.720); 3. B0d/F2 (3 MEETS, 1 MISSES, RMSE/B1 0.854); 4. B0c/E3 (3 MEETS, 1 MISSES, RMSE/B1 0.869); 5. B0b/D1 (2 MEETS, 0 MISSES, RMSE/B1 0.666); 6. B0b/C4 (2 MEETS, 0 MISSES, RMSE/B1 0.695); 7. B0/C4 (2 MEETS, 0 MISSES, RMSE/B1 0.734); 8. B0/D1 (2 MEETS, 1 MISSES, RMSE/B1 0.799); 9. A/C4 (1 MEETS, 0 MISSES, RMSE/B1 0.734); 10. B0/D2 (1 MEETS, 2 MISSES, RMSE/B1 0.751); 11. A/C1-exp (1 MEETS, 2 MISSES, RMSE/B1 0.982); 12. A/C3 (1 MEETS, 2 MISSES, RMSE/B1 0.983); 13. B0b/D2 (0 MEETS, 2 MISSES, RMSE/B1 0.896).

The initial all-curve consistency failure was due to start-up pressure history, not curve code: all checkable replays reproduced saved results (8 rows at prediction level, 11 at aggregate level). The signed ramp-effect median is -0.009 g/s, with range [-0.196, +0.112] g/s; the largest magnitudes occur at 13 and 2 bar. Here 'start-up pressure history' includes the nominal-versus-recorded pressure contrast, which is nonzero even for memoryless B1; the check does not isolate a causal start-up contribution.

The typical absolute ramp effect is 0.022 g/s (pooled median), below endpoint RMSEs of 0.211–0.349 g/s, but its largest value, 0.196 g/s, is comparable: start-up pressure history is a first-order factor for flow at 100 s in those largest-effect conditions, under this combined history-and-pressure-coordinate contrast.

Observed descriptive quadratic peak: **6.125 [5.907, 6.327] bar** (95% whole-brew bootstrap, 1000 resamples, seed 20261102; fit restricted to 4–8 bar).
Every curve below and in FIGURE.png is labelled **descriptive evaluation of saved fits — not a prediction**. Continuous model peaks and fold ranges are in SCORECARD.csv; FIGURE.png plots the requested unique curves (F1 is also a ranked leader). Constant line pressure from stable-clock zero to 100 s is a descriptive forcing convention, not a reconstruction of variable measured histories. No new mechanism fit, resampling of model parameters, or modification of earlier outputs occurred.
Ranking counts only the four graded criteria; NOT_SCORED contributes neither MEETS nor MISSES. Timing, complexity and restart are not ranking grades. B1 has its saved TIE capability label and is excluded from ranking; D3 is EXPLORATORY and E2 is INELIGIBLE. B0's raw sensitivity is promoted to this scorecard's primary; basket results occupy separate, ungraded CSV columns. Each stage uses its own B1 and saved interval method, so the cross-stage ranking is advisory, not a new matched statistical comparison.
Complexity lists free fitted parameters + n fixed training-estimated nuisance inputs; no coefficients were refitted here. Restart higher* copies Stage A: 'higher (consistent direction; continued delivery, no pause benefit)'; full source statements are in the CSV. Whole-brew resampling samples each existing brew as a unit within its pressure condition, preserving the cohort and its duplicate exclusion.
Resolved observed late trends confirmed from LATE_TRENDS.csv: 2, 3.5, 4, 5, 6 bar, all rising; no difference from the owner's set. Original x/11 counts remain ungraded in the CSV.
Replay and ramp effects are separate. PREDICTION checks compare replayed versus saved held-out condition-mean endpoints, tolerance 0.015 g/s. B0 references are reconstructed from saved condition residuals plus observed means; A/B1 shares exactly the same fold coefficients and observer. B0d references are condition aggregates extracted from the original saved endpoint cache, with coefficients checked against RESULT_TABLE.csv; individual brews are not exported. No per-fold scores were saved for the remaining A/B0b/B0c rows: their strongest check is AGGREGATE, one score comparison at max(0.005 g/s, 1% of saved RMSE). Their per-prediction checks remain NOT_AVAILABLE, not 11 independent successes. There is no 121-check matrix. E1/E3 retain fold-fixed onset coefficients and Mc; their onset pressure input interpolates saved early-pressure means from training conditions only (nearest endpoint beyond that fold's training range). Stable-pressure zero, original initial states and B0d air terms are preserved. Solid lines are constant-pressure idealisations; aggregate-only lines are lighter and labelled weaker check (aggregate only). INCONSISTENT curves would be dashed and excluded from peak interpretation. Grades always use saved intervals.

| Curve (all: descriptive evaluation of saved fits — not a prediction) | Status | Check tier | Prediction checks | Score checks | Largest check deviation, g/s | Constant-pressure idealisation peak median [fold range], bar |
|---|---|---|---|---|---|---|
| A/C1-exp | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 8.90 [8.20, 9.55]; weaker check (aggregate only) |
| A/C3 | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 8.90 [8.15, 9.60]; weaker check (aggregate only) |
| A/C4 | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 7.95 [7.60, 8.25]; weaker check (aggregate only) |
| A/B1 | CONSISTENT_IDEALISATION | PREDICTION | 11/11 | NOT_AVAILABLE | 2.22e-16 at 4 bar | 8.40 [7.65, 8.60] |
| B0/D1 | CONSISTENT_IDEALISATION | PREDICTION | 11/11 | NOT_AVAILABLE | 2.22e-16 at 4 bar | 7.75 [7.40, 8.05] |
| B0/D2 | CONSISTENT_IDEALISATION | PREDICTION | 11/11 | NOT_AVAILABLE | 4.44e-16 at 5 bar | 13.00 [13.00, 13.00] |
| B0/C4 | CONSISTENT_IDEALISATION | PREDICTION | 11/11 | NOT_AVAILABLE | 4.44e-16 at 5 bar | 7.95 [7.60, 8.25] |
| B0/B1 | CONSISTENT_IDEALISATION | PREDICTION | 11/11 | NOT_AVAILABLE | 2.22e-16 at 4 bar | 8.40 [7.65, 8.60] |
| B0b/C4 | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 7.80 [7.30, 8.05]; weaker check (aggregate only) |
| B0b/D1 | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 7.45 [7.25, 7.70]; weaker check (aggregate only) |
| B0b/D2 | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 10.20 [7.55, 10.40]; weaker check (aggregate only) |
| B0b/D3 | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 7.50 [7.25, 7.70]; weaker check (aggregate only) |
| B0b/B1 | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 8.10 [7.35, 8.20]; weaker check (aggregate only) |
| B0c/E1 (INTERPOLATED_INPUTS) | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 7.70 [7.15, 7.90]; weaker check (aggregate only) |
| B0c/E3 (INTERPOLATED_INPUTS) | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 7.45 [7.05, 7.65]; weaker check (aggregate only) |
| B0c/E2 | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |
| B0c/B1 | CONSISTENT_IDEALISATION_AGGREGATE | AGGREGATE | NOT_AVAILABLE | 1/1 | 0 (score) | 8.25 [7.50, 8.40]; weaker check (aggregate only) |
| B0d/F1 | CONSISTENT_IDEALISATION | PREDICTION | 11/11 | NOT_AVAILABLE | 0 at 1 bar | 7.40 [6.95, 7.65] |
| B0d/F2 | CONSISTENT_IDEALISATION | PREDICTION | 11/11 | NOT_AVAILABLE | 0 at 1 bar | 7.60 [7.00, 7.85] |
| B0d/B1 | CONSISTENT_IDEALISATION | PREDICTION | 11/11 | NOT_AVAILABLE | 0 at 1 bar | 8.40 [7.65, 8.60] |

Ramp effect = constant nominal-pressure endpoint minus measured-history replay at each fold's held-out condition. It includes nominal-versus-recorded pressure differences, evidenced by B1's nonzero contrast despite having no memory; it does not isolate a causal start-up contribution. The table gives the signed median and range across the original held-out conditions; every pressure's signed value is in SCORECARD.csv. The check tier shown for each result is the replay evidence supporting that ramp contrast.

| Candidate | Stage | Check tier | Median effect, g/s | Range, g/s | Largest absolute effect, g/s | Pressure, bar |
|---|---|---|---|---|---|---|
| C1-exp | A | AGGREGATE | -0.0004 | [-0.0194, +0.0827] | 0.0827 | 2 |
| C3 | A | AGGREGATE | +0.0014 | [-0.0176, +0.0846] | 0.0846 | 2 |
| C4 | A | AGGREGATE | -0.0017 | [-0.0226, +0.0929] | 0.0929 | 2 |
| B1 | A | PREDICTION | -0.0007 | [-0.1068, +0.0925] | 0.1068 | 13 |
| D1 | B0 | PREDICTION | -0.0890 | [-0.1652, +0.0854] | 0.1652 | 13 |
| D2 | B0 | PREDICTION | +0.0065 | [-0.0274, +0.0774] | 0.0774 | 2 |
| C4 | B0 | PREDICTION | -0.0017 | [-0.0226, +0.0929] | 0.0929 | 2 |
| B1 | B0 | PREDICTION | -0.0007 | [-0.1068, +0.0925] | 0.1068 | 13 |
| C4 | B0b | AGGREGATE | -0.0004 | [-0.0267, +0.1057] | 0.1057 | 2 |
| D1 | B0b | AGGREGATE | -0.0753 | [-0.1369, +0.0967] | 0.1369 | 13 |
| D2 | B0b | AGGREGATE | +0.0308 | [-0.0232, +0.0674] | 0.0674 | 2 |
| D3 | B0b | AGGREGATE | -0.0487 | [-0.1378, +0.0976] | 0.1378 | 13 |
| B1 | B0b | AGGREGATE | -0.0005 | [-0.1033, +0.0782] | 0.1033 | 13 |
| E1 | B0c | AGGREGATE | +0.0009 | [-0.0626, +0.1118] | 0.1118 | 2 |
| E3 | B0c | AGGREGATE | -0.0758 | [-0.1964, +0.0995] | 0.1964 | 13 |
| E2 | B0c | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE | NOT_AVAILABLE |
| B1 | B0c | AGGREGATE | -0.0006 | [-0.1059, +0.0857] | 0.1059 | 13 |
| F1 | B0d | PREDICTION | -0.0018 | [-0.0358, +0.0941] | 0.0941 | 2 |
| F2 | B0d | PREDICTION | -0.1020 | [-0.1873, +0.0859] | 0.1873 | 13 |
| B1 | B0d | PREDICTION | -0.0007 | [-0.1068, +0.0925] | 0.1068 | 13 |

NOT_AVAILABLE: B0c/E2: E2 requires observed onset at new pressures; no predictive onset may be substituted. B0d/B1: timing pair NOT_AVAILABLE (no air-inclusive reference law). B0b and B0d restart statements NOT_AVAILABLE; no stage-specific direction was saved.
Omitted requested rows: none; E2 is included and flagged as requested.
Generation compute: 10.74 s wall / 10.73 s process CPU; model refits: 0. QA time is reported separately in the PR.
Sources: [Stage A](../PRESSURE_PEAK_STAGE_A/RESULT_TABLE.csv), [B0](../PRESSURE_PEAK_STAGE_B0/RESULT_TABLE.csv), [B0b](../PRESSURE_PEAK_STAGE_B0B/RESULT_TABLE.csv), [B0c](../PRESSURE_PEAK_STAGE_B0C/RESULT_TABLE.csv), [B0d](../PRESSURE_PEAK_STAGE_B0D/RESULT_TABLE.csv), and their named companion CSVs; [100-s brew endpoints](../../../puckworks/data/waszkiewicz2025/equilibrium_windows.csv). Waszkiewicz et al. (2025), [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315), CC-BY-4.0. Only attributed aggregates are added. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

</details>
