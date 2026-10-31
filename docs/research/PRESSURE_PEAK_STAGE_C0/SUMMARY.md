# PRESSURE-PEAK Stage C0

**Retrospective capability, not validation; TARGET_EXPOSED. PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

<details><summary>Owner-set grading bands (verbatim; set before results)</summary>

Flow criteria: identical to the scorecard (accuracy vs this stage's B1; peak 5–7 bar MEETS / 4 or 8 bar NEAR; slope MEETS if it overlaps [−0.0880, −0.0403], NEAR if within [−0.176, −0.020]; trends on resolved conditions 2/3.5/4/5/6 bar, MEETS ≥4/5, NEAR 3/5).
Onset accuracy (held-out onset RMSE): MEETS ≤ 3.51 s (W1 level); NEAR ≤ 4.53 s (W0 level); otherwise MISSES.
Low-pressure bias (mean flow residual at 1–3.5 bar): MEETS if |bias| ≤ 0.10 g/s; NEAR if ≤ 0.20 g/s; otherwise MISSES. Report E1's and F1's values as comparators.
Consistency (the key test), comparing the 95% intervals for P* from fits (i) and (ii):
  MEETS if they overlap; NEAR if the gap ≤ 1 bar; otherwise MISSES. Same rule for P0.
Grades measure capability on retrospective data, not validation. Do not use PASS.

</details>

| Fit | Accuracy | Peak | Slope | Trends | Onset | Low-pressure bias |
|---|---|---|---|---|---|---|
| T1 flow-only | NEAR | MEETS | NEAR | MEETS | NOT_SCORED | NEAR |
| T1-W onset-only | NOT_SCORED | NOT_SCORED | NOT_SCORED | NOT_SCORED | NEAR | NOT_SCORED |
| T1/T1-W joint | NEAR | MEETS | NEAR | NEAR | NEAR | NEAR |

Independent-fit interval consistency: P* **NEAR**; P0 **NEAR** (gaps in CSV).

![Flow and onset versus pressure](FIGURE.png)

The threshold reduces but does not remove low-pressure bias: +0.184 g/s (flow-only) and +0.117 g/s (joint), versus saved E1 +0.446 and F1 +0.149 g/s. Separate P* and P0 intervals remain disjoint (NEAR and NEAR), so a common pressure scale is not established. The joint constant-pressure flow peak lands at 7.00 bar and its onset minimum at 7.00 bar, versus observed flow 6.1 [5.9, 6.3] bar and onset minimum at the 3.5-bar nominal condition.

Held-out endpoint RMSE: T1 0.193, joint 0.193, B1 0.286 g/s. Onset RMSE: T1-W 3.522, joint 3.672, W0 4.534, W1 3.512 s.

The joint onset curve is nearly flat. The held-out 1-bar fits touch the predeclared bounds: P0=−5 bar (onset-only), b=0.0001 s·bar (joint); no bounds were changed.

Ungraded held-out trace RMSE (same B0c mask/support): T1 flow-only 0.280, T1/T1-W joint 0.278, B1 0.437, E1 0.329, F1 0.366 g/s; timing-only rows have no flow prediction.

Joint residual scales: **0.437 g/s**, [B0c SUMMARY.md:38](../PRESSURE_PEAK_STAGE_B0C/SUMMARY.md#L38); **4.534 s**, [B0d SUMMARY.md:11](../PRESSURE_PEAK_STAGE_B0D/SUMMARY.md#L11). B0c mask/support/weighting, stable clock and 100-s endpoint retained; 56 brews, 11 held-out-condition folds, raw line pressure. Observed onset is a target/mask only; M starts at zero at stable pressure. Training-fold Mc fixed; references unchanged.

Uncertainty: 200/200 whole-brew refits per fit type, repeating all folds and training Mc; seed 20261104. Accuracy uses B0c's 1,000 paired condition-then-brew resamples and ±0.25 g/s band. Parameters describe full-cohort fits; grades use held-out predictions. Joint 0.05-bar-grid extrema coincide by construction (P*+P0). Compute 4.02 min. [Parameters, 95% intervals, bounds and full scores](RESULT_TABLE.csv).

**Recommended next step:** Owner: keep C0 in Python and review the wetting mismatch and bound-limited low-pressure fits before considering solver transfer.

Sources inspected: Waszkiewicz traces_per_brew, equilibrium_windows and original timing/pressure records; B0c/B0d saved fits. Waszkiewicz et al. (2025), [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315), CC-BY-4.0. No solver, historical result or source-data changes.
