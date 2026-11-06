# Results: post-hoc reset-flag exclusion

The sole scientific correction excludes 455 stored `reset_like=True` shots,
identified after #421's results. It is post hoc. The flag means an adjacent native
reported-weight drop >5 g anywhere in the original history; it does not identify
its cause. #421 remains the original result. The retained set is **unflagged shots**.

## 1. Observation and fold continuity

The funnel is 23,169 canonical shots / 555 users → 14,471 common pressure/weight
histories / 344 users → 10,686 structurally usable 001 shots / 318 users →
**10,231 unflagged shots / 315 users**, containing **159,466 windows**.
The stored survivor objects, observations, window roles and fold IDs are unchanged.
No fold generator was called. The same equal-user rule is recomputed over survivors.


| Original fold | Surviving shots | Surviving users |
| --- | --- | --- |
| 0 | 1810 | 64 |
| 1 | 1521 | 64 |
| 2 | 2068 | 63 |
| 3 | 2846 | 62 |
| 4 | 1986 | 62 |

The mandatory C0 check passed before any nonlinear fit: RMSE
**1.2084042519074556 g/s**, NRMSE **1.6547408859936399**, within the frozen 1e-9
tolerance of the supplied ten-decimal references. The maximum per-window difference
from the matched 001 cached C0 predictions is **0**. Final benchmark C0 reproduces
the same values. [CONTINUITY.json](CONTINUITY.json),
[C0 reproduction](C0_REPRODUCTION.json) and the frozen manifests bind these checks.

The target remains **reported weight-derived flow** over complete 2-s windows.
Amplitude uses only the first three windows from delivery onset; the next 2 s is
a guard. It is frozen for later windows. The later recorded pressure history and
current observed start mass are conditional inputs, not autonomous forecasts of
unknown future covariates. All other signal flags remain diagnostics.

## 2. Held-out prediction

Scores are equal-user means of per-shot RMSE. NRMSE uses the common calibration-only
RMS flow scale, floored at 0.1 g/s. Fold ranges are descriptive variation across the
five preserved folds, not confidence intervals. The pressure-varying subset uses
the unchanged scored-window mean-pressure span >2 bar and contains **2,783 shots /
221 users**. M0 and A are the declared no-recovery sensitivities.

### Overall

| Model | RMSE (g/s) | Fold RMSE range | NRMSE | Fold NRMSE range |
| --- | --- | --- | --- | --- |
| C0 | 1.208404 | 1.140714–1.309703 | 1.654741 | 1.551353–1.711638 |
| T0 | 1.117731 | 1.073631–1.203202 | 1.483938 | 1.394256–1.536047 |
| R0 | 0.989432 | 0.958688–1.075963 | 1.324572 | 1.258745–1.373487 |
| L0R | 0.960932 | 0.853060–1.242465 | 1.305962 | 1.049360–1.697804 |
| M0R | 0.828045 | 0.768982–0.983329 | 1.172328 | 1.032845–1.365334 |
| AR | 0.828771 | 0.768982–0.985362 | 1.176126 | 1.032845–1.377234 |
| M0 | 1.051583 | 1.007299–1.162867 | 1.470003 | 1.369494–1.601135 |
| A | 1.051436 | 1.007389–1.162484 | 1.470642 | 1.369106–1.601808 |


### Pressure Varying

| Model | RMSE (g/s) | Fold RMSE range | NRMSE | Fold NRMSE range |
| --- | --- | --- | --- | --- |
| C0 | 1.343786 | 1.163056–1.428558 | 2.526208 | 2.405813–2.757133 |
| T0 | 1.256210 | 1.125743–1.309977 | 2.358171 | 2.206302–2.621009 |
| R0 | 1.142112 | 1.016155–1.194911 | 2.172770 | 2.014078–2.424001 |
| L0R | 1.241771 | 0.911101–1.858594 | 2.281079 | 1.520261–3.213998 |
| M0R | 0.975451 | 0.844306–1.234142 | 1.954443 | 1.532240–2.406458 |
| AR | 0.977668 | 0.844306–1.236313 | 1.962971 | 1.532240–2.423294 |
| M0 | 1.132138 | 0.989927–1.346940 | 2.223268 | 1.882727–2.615917 |
| A | 1.131821 | 0.989497–1.345326 | 2.224270 | 1.881886–2.618966 |

**M0R is the recommended reference predictor**, selected by the lowest primary
held-out RMSE among all eight declared models. It also has the lowest overall
NRMSE and both metrics on the pressure-varying subset. This recommendation comes
from cross-validation; all-user deployment refits contribute no scores or contrasts.
No production default is changed.

### Paired differences and fold variation

Negative differences favor the first model. Intervals are the declared 1,000
complete-user bootstrap percentile intervals (seed 20261105), from cached predictions,
with no refits. They do not account for choosing this correction after seeing 001.
[FOLD_CONTRASTS.csv](FOLD_CONTRASTS.csv) contains all five fold differences for
both metrics; [CONTRASTS.csv](CONTRASTS.csv) also supplies NRMSE differences/intervals.

#### Overall

| Contrast | RMSE difference [95% interval], g/s | Fold difference range, g/s | NRMSE difference [95% interval] |
| --- | --- | --- | --- |
| AR-M0R | 0.000726 [-0.001819, 0.004133] | -0.000014–0.002033 | 0.003798 [-0.001175, 0.010982] |
| AR-T0 | -0.288960 [-0.367843, -0.195670] | -0.351622–-0.217840 | -0.307811 [-0.418377, -0.154783] |
| AR-R0 | -0.160661 [-0.230403, -0.075486] | -0.206125–-0.090601 | -0.148446 [-0.250238, 0.004698] |
| M0R-R0 | -0.161387 [-0.229560, -0.078129] | -0.206125–-0.092634 | -0.152244 [-0.249337, -0.005158] |
| L0R-T0 | -0.156799 [-0.266804, -0.013338] | -0.267544–0.039264 | -0.177976 [-0.368880, 0.081683] |
| L0R-R0 | -0.028500 [-0.134301, 0.110353] | -0.122047–0.166502 | -0.018610 [-0.201272, 0.237421] |
| R0-C0 | -0.218972 [-0.256431, -0.180094] | -0.257224–-0.173982 | -0.330169 [-0.364261, -0.297583] |
| T0-C0 | -0.090673 [-0.128493, -0.052482] | -0.127418–-0.035910 | -0.170803 [-0.190568, -0.150841] |


#### Pressure Varying

| Contrast | RMSE difference [95% interval], g/s | Fold difference range, g/s | NRMSE difference [95% interval] |
| --- | --- | --- | --- |
| AR-M0R | 0.002217 [-0.003126, 0.009655] | -0.000393–0.009456 | 0.008528 [-0.002934, 0.024377] |
| AR-T0 | -0.278542 [-0.388805, -0.127060] | -0.463598–-0.067930 | -0.395200 [-0.625191, -0.074916] |
| AR-R0 | -0.164444 [-0.269389, -0.020168] | -0.339526–0.046674 | -0.209799 [-0.427200, 0.095884] |
| M0R-R0 | -0.166661 [-0.268559, -0.029166] | -0.339526–0.044503 | -0.218327 [-0.425821, 0.072534] |
| L0R-T0 | -0.014438 [-0.212070, 0.239429] | -0.396802–0.554351 | -0.077092 [-0.502527, 0.515515] |
| L0R-R0 | 0.099660 [-0.099538, 0.351668] | -0.272731–0.668955 | 0.108309 [-0.311543, 0.682394] |
| R0-C0 | -0.201674 [-0.238090, -0.166487] | -0.244727–-0.146901 | -0.353438 [-0.395304, -0.311669] |
| T0-C0 | -0.087576 [-0.117996, -0.055829] | -0.120655–-0.037313 | -0.168037 [-0.189650, -0.148884] |

M0R improves on R0 overall by 0.161387 g/s and in every overall fold; the
pressure-varying aggregate improvement is 0.166661 g/s, with one fold reversing
sign (fold 3: +0.044503 g/s). AR does not improve on M0R in aggregate: +0.000726
g/s overall and +0.002217 g/s in the pressure-varying subset, with intervals spanning
zero. Its extra downturn flexibility is not the most useful selected shape here.
Both shared shapes outperform T0 and R0 in the aggregate.

L0R improves on T0 overall, but its difference from R0 is small and uncertain;
in the pressure-varying subset its point estimate is worse than R0, with an interval
spanning zero. Its overall fold RMSE spans 0.853–1.242 g/s, and its pressure-varying
fold RMSE spans 0.911–1.859 g/s. Linear pressure response is less consistent across
these folds than the selected saturating shape.

### Same surviving shots: original full-cohort fits versus filtered fits

Both columns score exactly the same surviving observations and original held-out
fold IDs. The 001 column comes only from its authenticated cached predictions;
none of its models is refitted. These are matched-survivor comparisons, not a
comparison with 001's full-cohort headline. Complete fold/NRMSE comparisons are in
[MATCHED_COMPARISON.csv](MATCHED_COMPARISON.csv).

| Model | Overall 001 fit | Overall 002 fit | Varying 001 fit | Varying 002 fit |
| --- | --- | --- | --- | --- |
| C0 | 1.208404 | 1.208404 | 1.343786 | 1.343786 |
| T0 | 1.144011 | 1.117731 | 1.302823 | 1.256210 |
| R0 | 1.155146 | 0.989432 | 1.304144 | 1.142112 |
| L0R | 1.063129 | 0.960932 | 1.167399 | 1.241771 |
| M0R | 1.174363 | 0.828045 | 1.340177 | 0.975451 |
| AR | 3.086366 | 0.828771 | 9.060740 | 0.977668 |
| M0 | 1.175170 | 1.051583 | 1.340585 | 1.132138 |
| A | 3.332255 | 1.051436 | 10.345467 | 1.131821 |

Refitting after the exclusion substantially changes the shared pressure fits:
M0R moves from 1.174363 to 0.828045 g/s and AR from 3.086366 to 0.828771 g/s on
identical survivors. This establishes sensitivity of the fitted predictor to the
flagged training records under this declared correction; it does not establish
the cause of their discontinuities. Improvement is not uniform across families:
L0R's pressure-varying score worsens from 1.167399 to 1.241771 g/s.

### Secondary whole-shot amplitude-adjusted reconstruction

The shared parameters remain those trained in the corresponding outer fold, but
amplitude is fitted on and scored against all complete windows, including the
guard. This easier same-shot task is secondary and does not select the default.

| Model | Reconstruction RMSE (g/s) | Reconstruction NRMSE |
| --- | --- | --- |
| C0 | 0.677123 | 0.896914 |
| T0 | 0.638971 | 0.788315 |
| R0 | 0.532011 | 0.610754 |
| L0R | 0.469796 | 0.480448 |
| M0R | 0.438334 | 0.450402 |
| AR | 0.437659 | 0.449739 |
| M0 | 0.537972 | 0.640223 |
| A | 0.537712 | 0.640212 |

AR is narrowly best for reconstruction (0.437659 g/s versus M0R 0.438334),
without being best for early-calibrated later prediction. The gap to primary
errors cautions against assuming a fixed early-calibrated amplitude describes
each whole shot adequately. Subset and fold reconstruction scores are in SCORES.csv.

## 3. Parameters explain the selected curves

The physical-coordinate parameters below are shared training estimates, never
held-out amplitude estimates. All selected starts report optimizer success.
Bounds are diagnostics, not criteria for whether a result counts. All pressure
families contact n=1; AR fold 2 contacts kappa=0, AR fold 3 contacts Pd=100 bar,
and every A fit contacts Pd=100 bar. No Mc or Tc bound is contacted. Exact contacts
and transformed bounds (tolerance 1e-7) are in [PARAMETER_BOUNDS.csv](PARAMETER_BOUNDS.csv).

| Fold | Model | n | Pd (bar) | kappa (/bar) | Mc (g) | Tc (s) |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | T0 | — | — | — | — | 1.501094 |
| 0 | R0 | — | — | — | 4.731135 | — |
| 0 | L0R | — | — | — | 3.240832 | — |
| 0 | M0R | 1.000000 | 3.730319 | — | 4.660207 | — |
| 0 | AR | 1.000000 | 4.761612 | 0.017313 | 4.648501 | — |
| 0 | M0 | 1.000000 | 10.129496 | — | — | — |
| 0 | A | 1.000000 | 100.000000 | 0.040964 | — | — |
| 1 | T0 | — | — | — | — | 1.435621 |
| 1 | R0 | — | — | — | 4.528483 | — |
| 1 | L0R | — | — | — | 3.206509 | — |
| 1 | M0R | 1.000000 | 3.638093 | — | 4.616947 | — |
| 1 | AR | 1.000000 | 8.793475 | 0.054137 | 4.589199 | — |
| 1 | M0 | 1.000000 | 9.477819 | — | — | — |
| 1 | A | 1.000000 | 100.000000 | 0.044237 | — | — |
| 2 | T0 | — | — | — | — | 1.630686 |
| 2 | R0 | — | — | — | 4.778988 | — |
| 2 | L0R | — | — | — | 3.181883 | — |
| 2 | M0R | 1.000000 | 3.461950 | — | 4.676884 | — |
| 2 | AR | 1.000000 | 3.461951 | 0.000000 | 4.676883 | — |
| 2 | M0 | 1.000000 | 10.360824 | — | — | — |
| 2 | A | 1.000000 | 100.000000 | 0.039272 | — | — |
| 3 | T0 | — | — | — | — | 1.485707 |
| 3 | R0 | — | — | — | 4.547073 | — |
| 3 | L0R | — | — | — | 3.399004 | — |
| 3 | M0R | 1.000000 | 4.290262 | — | 4.567275 | — |
| 3 | AR | 1.000000 | 100.000000 | 0.088348 | 4.536890 | — |
| 3 | M0 | 1.000000 | 13.479899 | — | — | — |
| 3 | A | 1.000000 | 100.000000 | 0.030369 | — | — |
| 4 | T0 | — | — | — | — | 1.720937 |
| 4 | R0 | — | — | — | 4.795254 | — |
| 4 | L0R | — | — | — | 3.106171 | — |
| 4 | M0R | 1.000000 | 3.673176 | — | 4.770638 | — |
| 4 | AR | 1.000000 | 3.764795 | 0.001839 | 4.768795 | — |
| 4 | M0 | 1.000000 | 10.991543 | — | — | — |
| 4 | A | 1.000000 | 100.000000 | 0.037958 | — | — |

M0R selects n=1, Pd=3.462–4.290 bar and Mc=4.567–4.771 g: a saturating
pressure response with appreciable early mass progression, not the large-Pd
near-linear limit or a very large Mc approximation to constant recovery. M0
without recovery has Pd=9.478–13.480 bar and higher primary error. T0 selects
Tc=1.436–1.721 s; R0 selects Mc=4.528–4.795 g; L0R selects Mc=3.106–3.399 g.
AR fold 3's n=1/Pd=100 gives an approximately linear saturation factor over the
observed range, multiplied by its exponential downturn. These descriptions do
not assign a physical mechanism.

### AR global capacity maximum

The pinned stationary-point check finds the unique global maximum for kappa>0;
with kappa=0 there is no finite maximum, only a supremum at infinity. Native training
pressures span 0–15 bar in every fold (15 plus roundoff in folds 0–3).

| Fold | kappa (/bar) | Global peak (bar) | Stationary points | Inside training pressure range |
| --- | --- | --- | --- | --- |
| 0 | 0.017313 | 12.260887 | 1 | True |
| 1 | 0.054137 | 9.950674 | 1 | True |
| 2 | 0.000000 | no finite peak | 0 | False |
| 3 | 0.088348 | 10.722880 | 1 | True |
| 4 | 0.001839 | 18.748269 | 1 | False |

Thus three AR folds have a finite in-range maximum, one finite maximum is
outside the range, and one fold is exactly monotone. Their near-tied prediction
scores do not establish a universal peak. All A peaks (20.380–28.464 bar) lie
outside the 0–15 bar training range. The four capacity families are plotted at
common normalization in CAPACITY_CURVES.svg; recovery and shot amplitude are omitted.

## 4. Diagnostic breakdowns and limitations

All values below come from the same frozen predictions, with no subgroup fits.
M0R RMSE is 1.084 g/s on rising-pressure windows, 0.841 on falling windows and
0.823 on level windows. This is direction dependence, not proof of a time artefact;
window groups overlap in shots and have different support. M0R errors by pressure
band 0–3 / 3–6 / 6–9 / >=9 bar are 0.764 / 0.793 / 0.784 / 0.654 g/s.

The negative-increment flag remains on **6,158 shots** (60.2% of survivors), with
M0R RMSE 0.870 g/s versus 0.679 on the 4,073 other unflagged shots. Clipping-like
shots remain eligible (129 shots / 48 users; M0R 1.081 g/s). Supplied-flow agreement
groups have M0R 0.705 g/s (agree), 1.408 (disagree), and 1.041 (missing). Flow-stable
versus other shots have 0.366 versus 0.853 g/s. These diagnostics are descriptive,
not admission rules or further corrections. Other model/flag results are in
[BREAKDOWNS.csv](BREAKDOWNS.csv); the gap partition is suppressed by the unchanged
release rules. Separate equal-user subgroup means need not average to the total.

Reported-weight authority is unknown throughout; no documented known-estimated
weight subgroup can be isolated. The supplied generic flow channel is labeled
`present_estimated_or_unknown_quantity` throughout and is diagnostic only; it is
not the observation target. This absence of authority metadata is a limitation,
not a claim of physical sensor measurement or an admission failure.

The aggregate example is a released equal-user mean over changing supported
cohorts, not an individual shot. Gaps are suppressed bins, and averaging can hide
large individual errors. The amplitude approximation remains a hypothesis under
test. Unknown machine/sensor provenance, residual noise and negative increments,
lag, hidden shot state, shutdown/post-drip behavior and self-selection limit transfer.
The post-hoc correction is not independent confirmation. These are predictive
usefulness results on reported signals, not mechanism, puck-pressure, causal-law,
universal-peak or physical-validation claims.

## Artifacts, numerical checks and cost

All 35 CV shared fits and seven deployment refits are saved with hashes, plus
six analytical C0 artifacts. MODEL_INDEX.csv identifies their roles. Deployment
models are excluded from scores and every contrast. All 24 pressure-model audits
passed the unchanged 1e-5 tolerance; maximum observed relative discrepancy was
3.552714e-15. NUMERICAL_AUDITS.csv includes all 48 models and their hashes.

Recorded CPU is **35.499337 core-hours**: **28.712818 CV optimization**, **5.892610
deployment optimization**, and **0.893909 other recorded CPU**. The six concurrent
fit jobs took **0.957508 wall-hours**. Driver/design overhead, repeated hashes,
reporting/bootstrap/comparison, figures, tests, review and hosted CI are unmetered;
this is not a complete host-level total. See ACCOUNTING.json and REPRODUCE.md.

Data source: Visualizer; thanks to the contributing users who made their shots
public. Research-use permission does not grant raw redistribution or endorsement.
