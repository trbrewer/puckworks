# SCI-MD-MASS-DELIVERY-003 result

**SINGLE_ANCHOR_MASS_DELIVERY_INADEQUATE.** The primary candidate remains ANCHORED_MASS.
This is the result of one independently audited scoring pass with zero new
curve fits, optimizer calls or native EWP runs. No post-score retuning occurred.

ANCHORED_MASS fails absolute adequacy because C01 mean absolute shot bias is
0.529251 pp, exceeding 0.50 pp, although all four mean shot RMSEs are below
1.00 pp. Against unanchored MASS, RMSE improves in every condition and by
0.141427 pp overall, but the 15.509% improvement misses 20% and mean absolute
bias deteriorates by 0.304947 pp. The shape earns value over persistence (94.465%
RMSE reduction). Competitiveness fails candidate adequacy and the bias margin
against anchored setting empirical. Neither empirical-superiority test passes.
**ANCHORED_EMPIRICAL is adequate in all four conditions**, with balanced
R=0.776937 pp and mean abs B=0.381108 pp; it is reported without automatic adoption.
All decision thresholds are numerically resolved.

G1 / NO_GOVERNING_PHYSICS_CHANGE. [Puckworks #282](https://github.com/trbrewer/puckworks/pull/282)
(closes issue #281) and [EWP #188](https://github.com/trbrewer/espresso-whole-pull/pull/188)
(closes issue #187) remain OPEN/UNMERGED for owner disposition.

## Complete suffix comparison

Cells are mean shot R / mean absolute shot B / signed mean shot B, in TDS
percentage points. Mass weights are within physical shots; shots are equally
weighted within conditions and the four conditions equally weighted overall.
Fraction 1 is excluded from every score. Unanchored scores are recomputed on
exactly the same five later fractions. Budgets are adopted working research
budgets, not measurement uncertainties or universal standards.

| Arm | C01 | C02 | C05 | C06 | Balanced |
|---|---|---|---|---|---|
| UNANCHORED_MASS | 1.121141 / 0.313129 / 0.233388 | 0.807782 / 0.064294 / -0.032365 | 0.658370 / 0.137990 / -0.049052 | 1.060237 / 0.032294 / -0.032294 | 0.911883 / 0.136927 / 0.029919 |
| ANCHORED_MASS | 0.804527 / 0.529251 / -0.529251 | 0.748500 / 0.416091 / -0.416091 | 0.610374 / 0.435755 / -0.435755 | 0.918424 / 0.386398 / -0.386398 | 0.770456 / 0.441874 / -0.441874 |
| UNANCHORED_EMPIRICAL | 1.187251 / 0.369434 / 0.280075 | 0.825033 / 0.051893 / -0.043206 | 0.688058 / 0.176084 / -0.006452 | 1.113879 / 0.035182 / -0.018307 | 0.953555 / 0.158148 / 0.053028 |
| ANCHORED_EMPIRICAL | 0.792811 / 0.420768 / -0.420768 | 0.744410 / 0.400039 / -0.400039 | 0.601506 / 0.344028 / -0.344028 | 0.969020 / 0.359597 / -0.359597 | 0.776937 / 0.381108 / -0.381108 |
| UNANCHORED_SETTING_EMPIRICAL | 1.210155 / 0.365061 / 0.328026 | 0.935938 / 0.086611 / 0.084655 | 1.029023 / 0.189717 / 0.037983 | 1.079414 / 0.029767 / 0.010219 | 1.063633 / 0.167789 / 0.115221 |
| ANCHORED_SETTING_EMPIRICAL | 0.865285 / 0.129407 / -0.113906 | 0.828586 / 0.180359 / -0.110723 | 0.901979 / 0.303361 / -0.300465 | 1.015457 / 0.149238 / -0.139296 | 0.902827 / 0.190591 / -0.166098 |
| ANCHOR_PERSISTENCE | 13.578814 / 12.957895 / 12.957895 | 14.060469 / 13.457562 / 13.457562 | 14.042581 / 13.402038 / 13.402038 | 13.996528 / 13.523658 / 13.523658 | 13.919598 / 13.335288 / 13.335288 |

## Decision axes

| Axis | Decision |
|---|---|
| A: Absolute all-condition suffix adequacy | FAIL |
| B: Material gain over unanchored MASS | FAIL |
| C: Material gain over anchor persistence | PASS |
| D: Adequacy plus competitiveness against both anchored empirical arms | FAIL |
| E: material superiority over ANCHORED_EMPIRICAL | FAIL |
| E: material superiority over ANCHORED_SETTING_EMPIRICAL | FAIL |

| Comparator | Balanced R reduction (pp) | Relative reduction | Definite condition wins | absB deterioration (pp) |
|---|---:|---:|---:|---:|
| ANCHORED_EMPIRICAL | 0.006481 | 0.834% | 1/4 | 0.060766 |
| ANCHORED_SETTING_EMPIRICAL | 0.132371 | 14.662% | 4/4 | 0.251283 |
| ANCHOR_PERSISTENCE | 13.149142 | 94.465% | 4/4 | -12.893415 |
| UNANCHORED_MASS | 0.141427 | 15.509% | 4/4 | 0.304947 |

All comparisons require 20% and 0.10 pp R improvement, lower R in at least three conditions, and at most 0.10 pp bias deterioration for material gain. Competitiveness uses the separate 0.10 pp R/bias margins and requires candidate adequacy. Superiority does not follow from competitiveness.

Adequate conditions by arm: UNANCHORED_MASS: PRED-C02, PRED-C05; ANCHORED_MASS: PRED-C02, PRED-C05, PRED-C06; UNANCHORED_EMPIRICAL: PRED-C02, PRED-C05; ANCHORED_EMPIRICAL: PRED-C01, PRED-C02, PRED-C05, PRED-C06; UNANCHORED_SETTING_EMPIRICAL: PRED-C02; ANCHORED_SETTING_EMPIRICAL: PRED-C01, PRED-C02, PRED-C05; ANCHOR_PERSISTENCE: none. No empirical arm is automatically adopted or relabelled as the primary candidate.

## Source identity and support

Original six source files and nine qualified registers match predecessor hashes.
Primary campaign PREDICTION_2022_03, PRED-C01/C02/C05/C06, source physical shots
PRED-E01/E02/E05/E06 with R1/R2/R3: 12 exact fraction-1 anchors. Collection order
and origin are established by the source cumulative-mass construction, its leading
zero, per-shot mE/mE_cum equality and original workbook net masses. Every one of
11 collected vials advances mass, including unassayed gaps; future vial 11 is
not an assay. Exact outcome IDs are fractions 2,3,5,7,10 for each shot: 60 assays.
All seven arms retain the same intended denominator; source origin/windows and
identity-set hashes are recorded in SOURCE.json, private coordinates and freeze.

All seven arms support 12/12 shots and 60/60 eligible assays: 0.343898600 kg
supported out of 0.343898600 kg intended assayed suffix mass. No unsupported
observations or missing anchors occurred. Per-condition denominators are in RESULTS.json.

Missing chemistry stays missing; HPLC-specific spill exclusions do not remove TDS.
No ramps, other grinds or experiment 46 were newly scored. Pannusch/Schmieder
share lineage and are not independent cohorts. Coffee lot remains UNKNOWN;
March roast batch is UNRESOLVED_POTENTIALLY_DIFFERENT. Source labels are
SOURCE_INTERNAL, TARGET_EXPOSED, RETROSPECTIVE_EARLY_ASSAY_CONDITIONED_COMPARISON.
Measured future mass windows are supplied evaluation queries, not forecasts.

## Numerical qualification and sensitivity

Maximum final solute numerical allowance: 5.01555e-15 kg (budget 1e-9). Maximum anchor denominator relative allowance: 7.46304e-12 (budget 1e-6). Ratio/product allowances propagate into R, B and every threshold comparison. Base empirical integration is exact and independently checked; compact integration retains refined and independent checks. Concentration bounds use analytical monotonicity or endpoints/knots, not a sampling grid.

| Anchored arm | Fraction 2 amplification | Fraction 3 | Fraction 5 | Fraction 7 | Fraction 10 |
|---|---|---|---|---|---|
| ANCHORED_EMPIRICAL | 0.6078–0.7221 | 0.4103–0.4841 | 0.2386–0.2518 | 0.1348–0.1647 | 0.0577–0.0890 |
| ANCHORED_MASS | 0.6049–0.6933 | 0.4328–0.4802 | 0.2325–0.2616 | 0.1303–0.1530 | 0.0582–0.0726 |
| ANCHORED_SETTING_EMPIRICAL | 0.6141–0.7609 | 0.4006–0.4927 | 0.2147–0.2805 | 0.1321–0.1715 | 0.0608–0.0766 |
| ANCHOR_PERSISTENCE | 1.0000–1.0000 | 1.0000–1.0000 | 1.0000–1.0000 | 1.0000–1.0000 | 1.0000–1.0000 |

Ranges are across the twelve shot-specific query windows. These are analytical
anchor-error amplification factors, not confidence intervals or sensor requirements.
Numerical allowance, displayed-source rounding, measurement uncertainty and
between-shot variation remain separate. No assay SD was inferred from replicates.
RESULTS.json includes numerical metric allowances, signed bias, all condition
coverage, error by fraction/horizon, maximum shot RMSE, predicted/observed solute
on assayed suffix support and unsupported reasons. Complete shot reports are private.
Assayed suffix sums are not measured whole-cup totals. Primary maximum shot RMSE
is 1.062791 pp. Across all sixty assayed suffix intervals, primary predicted solute
is 0.0229304182583 kg versus observed 0.0244479595345 kg. Numerical sum allowance
is 8.05e-14 kg; displayed-source rounding allowance is separately 3.82e-11 kg.
Primary balanced mean absolute errors at fractions 2/3/5/7/10 are
0.467411/0.190656/0.583729/1.303221/0.782223 pp; these horizon diagnostics preserve
condition balance and do not pool fractions as independent observations.

## Software, review and interpretation

Puckworks provides immutable anchor states, typed minimal inputs and coordinate-only
queries, strict serialization, conditional remaining-solute queries and synthetic
CLI examples. EWP binds the exact producer plus all three first-party runtime
modules and frozen model artifacts through isolated loading; no installed fallback
or duplicated numerical model. See README.md for runnable commands. Real anchors,
state files, prediction rows and logs stay private. A fitted curve plus a synthetic
anchor is labelled SYNTHETIC_ANCHOR_INPUT, never a reproduced physical shot.

PRE_SCORE_REVIEW.json is independent exact-freeze approval, not author approval.
FREEZE.json binds the evaluated producer identity; later documentation/result
commits do not redefine it. SCORE_RECEIPT.json and SCORE_COMPLETION.json document
one pass. SOFTWARE_QA.json separates ordinary local QA, hosted CI and review.
An initial local import-path failure and an EWP launcher-mode packaging defect
were corrected before scoring; original logs are retained. No scientific retuning.

This is not recipe-only prediction. Alpha is not identified soluble inventory.
Success does not identify causes of earlier campaign errors; failure does not
reject all amplitude or assimilation strategies. No time, pressure, flow,
mass-attainment, real-time assay, controller, universal-coefficient, causal or
physical-validation claim. Source-derived artifacts retain Pannusch/Schmieder
attribution and CC-BY-NC-3.0, DOI 10.17632/y2tz67f6ry.1, separate from first-party
software licensing. No laboratory operation or automatic successor.

PHYSICAL_VALIDATION = NOT_ESTABLISHED
PRODUCTION_DEFAULTS_CHANGED = false
PRODUCTION_DEPENDENCY_LOCK_CHANGED = false
NATIVE_EWP_RUNS = 0
NO_SUCCESSOR_AUTHORIZED
