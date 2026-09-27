# SCI-MD-MASS-DELIVERY-008 result

**ADAPTATION_ADEQUATE_INCREMENT_NOT_ESTABLISHED.** Fixed primary A2. One fresh independent exact-freeze approval followed by one new-task scoring operation.

One separately assayed calibration shot makes A2 adequate under the declared retrospective budgets, but does not earn any of the three predeclared material increments. I_CAL and I_CHEM fail the required 9/11 target wins (8 and 7 respectively). I_LOCAL fails the absolute improvement threshold (0.099491553 pp versus 0.10 pp), target wins (8/11) and calibration-choice wins (7/11). These failures are definite after numerical allowances; no threshold is relaxed. A0 and M also fail overall adequacy because too few calibration choices qualify, even though their balanced error and bias meet the scalar budgets.

The practical consequence is a narrowly supported research use: a one-shot offset can meet this cohort's adequacy budgets, but this experiment does not establish a material reason to retain the pretrained conditional model over the matched source-only or mass-only controls. Two calibration choices still fail A2 adequacy, and no favourable choice may be selected retrospectively. No deployment, successor or additional fitting is selected.

G1 / NO_GOVERNING_PHYSICS_CHANGE. [Producer draft PR #294](https://github.com/trbrewer/puckworks/pull/294) / [consumer draft PR #200](https://github.com/trbrewer/espresso-whole-pull/pull/200), issues #293 / #199. Both remain draft/open/unmerged.

| Status axis | Result |
|---|---|
| Source / coverage | PASS / PASS |
| Calibration A2 / A0 / M | PASS / PASS / PASS |
| Numerical F2 / A2 / A0 / M | PASS / PASS / PASS / PASS |
| Adequacy F2 / A2 / A0 / M | FAIL / PASS / FAIL / FAIL |
| I_CAL / I_CHEM / I_LOCAL | FAIL / FAIL / FAIL |

| Arm | Balanced R (pp) | Mean absolute pair bias (pp) | Adequate calibration choices (need 9/11) | Adequacy |
|---|---:|---:|---:|---|
| F2 | 0.599148861 | 0.532634505 | 0/11 | FAIL |
| A2 | 0.483157724 | 0.346409646 | 9/11 | PASS |
| A0 | 0.600495775 | 0.499012855 | 3/11 | FAIL |
| M | 0.582649277 | 0.455719143 | 4/11 | FAIL |

| A2 increment | R gain (pp) | Relative gain | Target wins | Calibration-choice wins | Mean absolute-bias deterioration (pp) | Status |
|---|---:|---:|---:|---:|---:|---|
| I_CAL | 0.115991137 | 19.3593% | 8/11 | 9/11 | -0.18622486 | FAIL |
| I_CHEM | 0.117338052 | 19.5402% | 7/11 | 9/11 | -0.152603209 | FAIL |
| I_LOCAL | 0.0994915529 | 17.0757% | 8/11 | 7/11 | -0.109309497 | FAIL |

The full status vector and numerical bounds in [RESULTS.json](RESULTS.json) are authoritative. Pair R is the beverage-mass-weighted TDS RMSE, and bias is made absolute within each pair before averaging. No predictions are averaged across calibration choices. Rows, columns and overall summaries give each declared pair equal weight. Adequacy uses 1.00/0.50 pp budgets, 8/10 individually adequate targets per calibration choice and 9/11 adequate choices. Each increment needs 0.10 pp and 15% balanced-R reduction, 9/11 definite wins on both row and column means, and at most 0.10 pp absolute-bias deterioration. Threshold bounds are numerical allowances, not confidence intervals, statistical significance or assay uncertainty. A failed increment does not establish equivalence.

G0 metadata clarification: the saved arm summaries retain `required_adequate_pairs=83` from a generic summary routine. This unused field is not an overall adequacy gate. Overall adequacy uses the balanced error/bias budgets and 9/11 adequate calibration choices, each requiring 8/10 adequate targets. A2 has 81/110 individually adequate pairs and 9/11 adequate choices, so its PASS is consistent with the predeclared rules. The independent reviewer confirmed that the unused field enters no final decision. Saved JSON, scoring code and score bytes remain unchanged; this clarification involves no rescore.

| Sensitivity to calibration choice | Row-mean R min / median / max (pp) | Row-mean absolute bias min / median / max (pp) |
|---|---:|---:|
| F2 | 0.554430093 / 0.602711143 / 0.634328199 | 0.481705949 / 0.537161195 / 0.573421491 |
| A2 | 0.389836064 / 0.419375159 / 0.749479555 | 0.231138112 / 0.267526174 / 0.706838432 |
| A0 | 0.454106452 / 0.517704371 / 1.02761898 | 0.361268502 / 0.414424854 / 0.917841586 |
| M | 0.426371554 / 0.484622205 / 1.2620942 | 0.291101021 / 0.362328189 / 1.07556254 |

All calibration choices are retained, including adverse choices. A2 is definitely worse in calibration-row / target-column mean R in 2/11 / 3/11 versus F2, 2/11 / 4/11 versus A0, 4/11 / 3/11 versus M. Complete row/column scores remain private; public distributions and adverse counts are descriptive, not independent experiments. No favourable calibration shot was selected.

| Physical observations versus repeated slots | Count |
|---|---:|
| Original qualified physical shots / eligible physical shots | 13 / 11 |
| Original regular vial positions in the qualified 13-shot inventory | 208 |
| Original eligible prefix assays / pooled summaries | 98 / 22 |
| Unique observed eligible suffix intervals | 55 |
| Unique eligible positive prefix plus suffix assays | 153 |
| Possible calibration shots / ordered off-diagonal pairs | 11 / 110 |
| Prediction slots per arm / all four arms | 550 / 2,200 |

Only the 55 unique observed suffix intervals are reused across pair scores. Every eligible shot is calibration data in other folds, so no globally untouched holdout or 110 independent experiments exist. The 22 prefix summaries were constructed from 98 original assays; this is not a two-physical-assay demonstration. The source varies across repeated shots. Arbitrary source-block ordering establishes neither chronological deployment nor controlled fixed-recipe reproducibility.

The exact 007 parser, chemistry-blind pools, original recorded Weight mass origin, mass-weighted concentrations and limited binary shared-boundary reconciliation are preserved. The extra block and terminal intervals remain excluded inventory. The two early positive-mass unavailable-chemistry gaps remain unavailable; their masses still advance the coordinate. No imputation, dose/yield normalization, spout doubling or target rebinning occurred.

| Support / extrapolation | Qualified slots | Parent-feature flagged slots | Outside own calibration mass range |
|---|---:|---:|---:|
| F2 | 550/550 | 90 | 0 |
| A2 | 550/550 | 90 | 0 |
| A0 | 550/550 | 40 | 0 |
| M | 550/550 | 0 | 189 |

All arms use the unchanged 006 mass ceiling. For M this is a comparison envelope, not chemistry-derived target support. Feature extrapolation and M calibration-range flags are separate; no flagged window was removed. A2-versus-M tests practical utility at the same ONE-calibration-shot budget, not equal-input architecture. A0 is the separate early-chemistry control, not a second-assay ablation.

Exactly 22 scalar calibrations and 11 MASS fits / 88 starts completed, with 16204 actual residual calls including numerical Jacobians, maximum 535/2,000 per start, and 0 failed starts. No retries, extra starts, omitted folds, fallback predictions or historical scorer calls. Scientific execution wall time 3.3460277 s / 3,600 s; one worker and one BLAS thread. Peak scientific RSS 90712 KiB / 8 GiB. New private scientific bundle 4761112 bytes / 2 GiB. Complete start records, final/last parameters, termination reasons and boundary hits remain private. M time rate is exactly zero. Convergence is not identifiability or physical validation.

Maximum total interval solute numerical allowance 1.08380634e-13 kg, versus 1e-9 kg. Independent quadrature/refinement, root enclosure, SI conversion, conservation, additivity, zero-width, ordering and domain/anchor checks are distinct from physical validation. F2 reuses verified historical predictions; none were regenerated. All 2,200 producer/consumer slots match byte for byte.

| Exact scientific identity | Commit | Tree |
|---|---|---|
| Evaluated producer | 5ec47c07cd5da6845c40fc9ea4467fcdd44afbaf | 7e299f207783e6242390c7483bff1a106a111736 |
| Reviewed consumer | f794000f1b5c4a1575509af89861e89f37d7f9dc | aa6eeedba2a046961c37400f09675a3366276306 |
| Producer reviewed base | 173d4265e17b7e79f1d8792dc9a49b1c5ef90985 | 522da1fca29424215367542aac09c7f6c0b2855d |
| Consumer reviewed base | 3f5ad6121f37fbad33348e92c65263b13378ef30 | f37837c9e839d1eafa19d01cfe8fdc876ea5ac13 |

[Freeze binding](FREEZE_BINDING.json), [independent pre-score binding](PRE_SCORE_REVIEW_BINDING.json), [prediction manifest](PREDICTION_MANIFEST.json), [execution](EXECUTION.json) and [result binding](RESULT_BINDING.json) preserve identities. Detailed evidence is retained outside Git under the private label `mass-delivery-008-evidence/run-001`; private receipts and row artifacts are not published. Reports read saved completed results without originals, fitting or prediction. Final ordinary publication review and hosted required CI are separate live PR statuses; pending CI is not success.

007 remains **FROZEN_CONDITIONAL_TRANSFER_INADEQUATE_ON_DECLARED_COHORT**, C2 adequacy FAIL and I0/I1 PASS/PASS. 008 is a distinct adaptation experiment with new, explicitly declared fold-local information. It is not a repair, rerun or reversal of failed zero-shot transfer.

RESEARCH_ONLY; TARGET_EXPOSED; RETROSPECTIVE_ONE_CALIBRATION_SHOT_SOURCE_ADAPTATION; CONDITIONAL_ON_COLLECTED_BEVERAGE_MASS_AND_PERMITTED_EARLY_CHEMISTRY; PHYSICAL_VALIDATION=NOT_ESTABLISHED. No fresh blind/prospective validation, real-time sampling policy, universally portable coffee model, hydraulics, inventory closure, identified measurement bias or physical-mechanism claim. Unassayed intervals are not filled to create a measured whole-cup total.

Pannusch/Schmieder, Mendeley 10.17632/y2tz67f6ry.1: source-derived CC-BY-NC-3.0 treatment remains separate from first-party software. Grudeva permission remains PERMISSION_DOCUMENTED, with no new rights grant or raw redistribution. Originals, locators, individual offsets/models, predictions, observations and private receipts remain outside Git.

MERGE_AUTHORIZED=false; PRODUCTION_ADOPTION_AUTHORIZED=false; PRODUCTION_DEPENDENCY_LOCK_CHANGED=false; NATIVE_EWP_RUNS=0; NO_SUCCESSOR_AUTHORIZED.
