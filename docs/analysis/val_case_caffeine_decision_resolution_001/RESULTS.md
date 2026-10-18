# Caffeine: persistent average gains, conditional comparative value

S2’s primary balanced RMSE improvement over S1, D0 and S0 remains strictly positive after **every one of the 12 declared physical-shot deletions**, including each scenario’s numerical allowance. That adds evidence of within-cohort influence stability to the historical result. It does not earn additional complexity: every primary deletion gain remains below the original 0.10 mg/g component, S2 is worse in some tested conditions, and its temperature comparison with D0 changes sign.

The original result is unchanged: **SIMPLER_CAFFEINE_PREDICTOR_ADEQUATE_NO_EARNED_COMPLEXITY**; all four primary adequacy decisions PASS; S2 A/B/C/D = PASS/FAIL/FAIL/FAIL. There is no independently justified intended-use criterion here that establishes practical incremental value. Neither equivalence nor absence of useful value is established.

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL. Evidence class: EXPLORATORY. Historical results were exposed before the specification freeze. [Protocol](PROTOCOL.md), [input identities](INPUT_MANIFEST.json), [full-precision public results](RESULTS.json), [handoff](HANDOFF.md).

## Evidence and reproduction

All five components completed: retained-shot to condition/panel reproduction and exact decisions; independent fraction-to-shot arithmetic; primary deletions; temperature deletions; source-observed variability. Both routes reproduce the historical numbers exactly in the execution environment: **zero nonzero arithmetic discrepancies and zero changed decisions**. Original and reproduced values, components and labels appear side by side in RESULTS.json. No original workbook cells were needed: the admitted, hash-bound retained observations include the required concentrations, masses, coordinates and source-field crosswalk.

The fixed population is 24 PRED physical shots, three per condition, with target fractions 3/5/7/10: 12 primary shots/48 windows, six temperature shots/24 windows, six flow shots/24 windows per arm. All **96 caffeine observations are source-valid**; prediction-domain support is **95/96**. `PRED-E07-R1`, C07, fraction 10 remains unsupported for `OUTSIDE_COMMON_TRAINING_MASS_DOMAIN`. The valid assay contributes to source-observed dispersion only. Early HPLC caffeine spills do not exclude these later targets. All 45 FIT shots in 15 designs remain training. Pannusch/Schmieder share lineage and are not independent replication.

D0 uses early measured masses without TDS or the C2 parent. S0 uses a constant share of frozen C2; S1 uses a mass-context share and already receives early TDS through C2. S2 adds early-TDS composition conditioning. Thus S2 versus S1 tests additional composition conditioning, not a TDS-versus-no-TDS experiment. D0 retains its no-TDS information advantage. S2 remains the historically designated candidate.

## All-arm and all-panel capability

R is a mass-weighted within-shot RMSE; B is signed shot bias; A=abs(B) is formed before averaging. Means first weight shots equally within condition, then conditions equally. Units below are mg/g. Full-flow metrics remain unavailable; shown flow values retain all six shots and both conditions, using each shot’s supported windows.

| Panel | Arm | R | Mean A | Mean B | Historical full adequacy | Support |
|---|---|---:|---:|---:|---|---|
| primary | D0 | 0.192258153 | 0.078832573 | -0.038568088 | PASS | 48/48 |
| primary | S0 | 0.215565189 | 0.140025144 | -0.140025144 | PASS | 48/48 |
| primary | S1 | 0.152188938 | 0.078570649 | -0.013100844 | PASS | 48/48 |
| primary | S2 | 0.125168095 | 0.088412899 | -0.056349458 | PASS | 48/48 |
| temperature_stress | D0 | 0.120398037 | 0.070562090 | -0.019367080 | PASS | 24/24 |
| temperature_stress | S0 | 0.166697704 | 0.118762948 | -0.118762948 | PASS | 24/24 |
| temperature_stress | S1 | 0.145712856 | 0.070482364 | 0.005294760 | PASS | 24/24 |
| temperature_stress | S2 | 0.125159081 | 0.081111489 | -0.030072536 | PASS | 24/24 |
| flow_stress | D0 | 0.200522376 | 0.082675508 | -0.052617831 | INCOMPLETE | 23/24 |
| flow_stress | S0 | 0.322506230 | 0.159145024 | -0.149639117 | INCOMPLETE | 23/24 |
| flow_stress | S1 | 0.317846180 | 0.125998742 | -0.045807519 | INCOMPLETE | 23/24 |
| flow_stress | S2 | 0.243466641 | 0.099668695 | -0.056193553 | INCOMPLETE | 23/24 |

All four primary arms satisfy every original condition’s R≤0.50 and mean A≤0.25 budgets. C07 remains incomplete for every arm under the original complete-shot lower-bound logic (denominator three). C08 retains all original m2 extrapolation flags: three shots per arm; neither stress panel was used to select a model. Actually-assayed-window mass-error summaries remain separate in RESULTS.json; they do not validate whole-cup caffeine.

## Historical contractual result

Every increment requires all four components: ≥0.10 mg/g balanced R gain, ≥15% relative gain, ≥3/4 definite condition wins, and ≤0.05 mg/g mean-A deterioration. Conservative numerical allowances apply; equality and denominator rules are unchanged. These are historical research budgets, not assay uncertainty or intended-use health/quality criteria.

| Axis / reference | R gain | Relative gain | Conservative lower relative gain | Definite / possible wins | A deterioration | Absolute / relative / wins / bias | Original = reproduced |
|---|---:|---:|---:|---:|---:|---|---|
| B / S1 | 0.0270208431 | 17.7548011% | 17.7548010% | 2 / 2 of 4 | 0.0098422506 | FAIL/PASS/FAIL/PASS | FAIL |
| C / D0 | 0.0670900581 | 34.8958196% | 34.8958195% | 3 / 3 of 4 | 0.0095803266 | FAIL/PASS/PASS/PASS | FAIL |
| D / S0 | 0.0903970941 | 41.9349222% | 41.9349221% | 4 / 4 of 4 | -0.0516122451 | FAIL/PASS/PASS/PASS | FAIL |

The absolute-gain component fails for every comparator; the S1 condition-win component also fails. The original relative and bias components pass. Primary mean-A deterioration versus S1 and D0 is small but adverse; S0’s mean A improves. Signed-bias differences and continuous component headroom are retained separately in RESULTS.json.

## Paired descriptive performance and condition dependence

Positive R gain means reference minus S2. These baseline condition summaries retain every tested condition. Flow rows are supported-subset diagnostics, including the incomplete C07 shot.

| Condition | Panel | S2 vs S1 R gain | S2 vs D0 R gain | S2 vs S0 R gain |
|---|---|---:|---:|---:|
| PRED-C01 | primary | 0.066170767 | 0.147530962 | 0.067056978 |
| PRED-C02 | primary | -0.001061564 | 0.079317893 | 0.166808018 |
| PRED-C05 | primary | -0.004258450 | -0.015562069 | 0.058306886 |
| PRED-C06 | primary | 0.047232620 | 0.057073446 | 0.069416494 |
| PRED-C03 | temperature_stress | 0.025808699 | -0.019880255 | 0.023543516 |
| PRED-C04 | temperature_stress | 0.015298852 | 0.010358167 | 0.059533731 |
| PRED-C07 | flow_stress | 0.065590312 | 0.032017393 | 0.036312546 |
| PRED-C08 | flow_stress | 0.083168765 | -0.117905924 | 0.121766632 |

**Adverse findings remain explicit:** S2 is worse than S1 in C02 and C05, and worse than D0 in C05. Temperature C03 favors D0 while C04 favors S2. D0’s temperature baseline gain is −0.004761044 mg/g and supported-flow baseline gain is −0.042944266 mg/g (both favor D0). S2 improves supported-flow R over S1 and S0, but that is not complete-flow adequacy. C08’s D0 advantage is 0.117905924 mg/g.

| Panel | Reference | Positive / zero / negative paired shot R gains |
|---|---|---:|
| primary | S1 | 7 / 0 / 5 |
| primary | D0 | 9 / 0 / 3 |
| primary | S0 | 11 / 0 / 1 |
| temperature_stress | S1 | 6 / 0 / 0 |
| temperature_stress | D0 | 2 / 0 / 4 |
| temperature_stress | S0 | 4 / 0 / 2 |
| flow_stress | S1 | 6 / 0 / 0 |
| flow_stress | D0 | 2 / 0 / 4 |
| flow_stress | S0 | 4 / 0 / 2 |

These are descriptive counts of the retained physical shots, not independent population trials. Complete paired shot values and condition contrasts are retained privately. Individual shot metrics and keyed deletion means are not published because together with public condition means they could reconstruct restricted values.

## Stability under the declared physical-shot deletions

Primary has baseline plus 12 deletions; temperature has baseline plus six. Each deletion removes the same whole physical trajectory from all four arms, retains every original condition, averages two remaining shots in the affected condition and three elsewhere, then weights conditions equally. Fits, conditioning and predictions stay frozen. There are **no flow deletions** and no replacement A/B/C/D verdicts.

The point ranges below use deletions only. The allowance-expanded envelopes use baseline plus all declared deletions, each with its own propagated allowance: min(g−u), max(g+u). Display rounding does not change comparisons; exact values are in RESULTS.json. These finite sensitivity envelopes are neither certified bounds nor confidence intervals.

| Panel | Reference | Baseline R gain | Deletion-only point range | Baseline + deletion numerical envelope | Deletion + / 0 / − | All points >0? | All lower endpoints >0? |
|---|---|---:|---|---|---:|---|---|
| primary | S1 | 0.0270208431 | [0.0165798078, 0.0363634281] | [0.016579807770, 0.036363428156] | 12 / 0 / 0 | yes | yes |
| primary | D0 | 0.0670900581 | [0.0495198276, 0.0816980216] | [0.049519827525, 0.081698021624] | 12 / 0 / 0 | yes | yes |
| primary | S0 | 0.0903970941 | [0.0803152846, 0.0981317799] | [0.080315284527, 0.098131780003] | 12 / 0 / 0 | yes | yes |
| temperature_stress | S1 | 0.0205537752 | [0.0137509161, 0.0246922200] | [0.013750916050, 0.024692220085] | 6 / 0 / 0 | yes | yes |
| temperature_stress | D0 | -0.0047610439 | [-0.0244662711, 0.0098097475] | [-0.024466271171, 0.009809747515] | 3 / 0 / 3 | no | no |
| temperature_stress | S0 | 0.0415386233 | [0.0186096484, 0.0635809618] | [0.018609648349, 0.063580961883] | 6 / 0 / 0 | yes | yes |

The primary gains persist against all comparators under every declared deletion. Temperature gains persist against S1 and S0; the D0 comparison has three positive and three negative deletions. The original numerical gain allowances are about 5.7×10⁻¹¹ mg/g per scenario. They are application-error estimates, not measurement uncertainty; their small size does not resolve assay, training or transfer uncertainty.

| Panel | Reference | Deletion relative-gain range | Deletion A-deterioration range (mg/g) | Absolute component ≥0.10 (points / lower endpoints) | Relative component met with allowance | Bias component met with allowance |
|---|---|---|---|---:|---:|---:|
| primary | S1 | [11.42995%, 21.79836%] | [-0.002329876, 0.024051981] | 0 / 0 of 12 | 10/12 | 12/12 |
| primary | D0 | [27.82078%, 39.66693%] | [0.001630869, 0.016514344] | 0 / 0 of 12 | 12/12 | 12/12 |
| primary | S0 | [38.10581%, 46.26600%] | [-0.068940635, -0.040840933] | 0 / 0 of 12 | 12/12 | 12/12 |
| temperature_stress | S1 | [9.41014%, 16.89491%] | [0.005756754, 0.018776486] | 0 / 0 of 6 | 4/6 | 6/6 |
| temperature_stress | D0 | [-21.57038%, 7.98608%] | [0.004865900, 0.018804562] | 0 / 0 of 6 | 0/6 | 6/6 |
| temperature_stress | S0 | [11.89105%, 36.00142%] | [-0.051755688, -0.020284534] | 0 / 0 of 6 | 5/6 | 6/6 |

These are continuous historical-budget diagnostics, not success probabilities or new increment decisions. The primary S1 relative gain crosses 15%; D0 and S0 stay above it. Primary definite/possible condition-win ranges are 2–3 against S1, 3–4 against D0 and 4 against S0; the original S1 2/4 failure remains. The temperature two-condition panel is never relabeled as meeting the original three-of-four requirement. All deletion gain points remain below 0.10 mg/g, including the favorable S0 comparison (maximum primary gain 0.098131780). Every bias-deterioration upper endpoint stays below 0.05 mg/g. Baseline and deletion metric/allowance ranges, signed-bias differences, relative-component envelopes and headroom are all retained in RESULTS.json, with every individual scenario privately bound.

## Source-observed caffeine variability

Every intended condition/fraction cell has three valid source observations. Sample SD uses n−1 and is in mg/g. Scoring support is three except C07/fraction 10, where it remains two for all arms. Coordinate ranges below are measured beverage grams (the JSON retains kg); fractions with the same label do not necessarily span identical mass intervals. This is dispersion across the recorded collection fractions, combining physical-shot variation, collection-coordinate differences and assay effects, not analytical repeatability at a fixed target interval.

| Condition | Fraction | Observation n / score n | Mean mg/g | Sample SD mg/g | Left edge range g | Right edge range g | Width range g |
|---|---:|---:|---:|---:|---|---|---|
| PRED-C01 | 3 | 3 / 3 | 4.6441339 | 0.1892472 | 10.5579–12.5498 | 16.6028–18.6749 | 5.9125–6.1251 |
| PRED-C01 | 5 | 3 / 3 | 2.9226230 | 0.0735154 | 22.1776–24.1426 | 27.6236–29.7560 | 5.4460–5.6134 |
| PRED-C01 | 7 | 3 / 3 | 2.0599597 | 0.0774794 | 33.0669–35.3787 | 38.4911–40.6495 | 4.7834–5.4294 |
| PRED-C01 | 10 | 3 / 3 | 1.3619359 | 0.1098116 | 49.3805–51.6498 | 54.7838–56.9867 | 5.2953–5.6849 |
| PRED-C02 | 3 | 3 / 3 | 4.5293582 | 0.1926413 | 11.9350–13.0830 | 17.8225–18.7467 | 5.6637–5.8875 |
| PRED-C02 | 5 | 3 / 3 | 2.9590032 | 0.1112248 | 23.5867–24.3759 | 29.2501–29.4905 | 5.1146–5.6634 |
| PRED-C02 | 7 | 3 / 3 | 2.0921392 | 0.0304777 | 34.6875–35.2007 | 40.2086–40.4014 | 5.2007–5.5211 |
| PRED-C02 | 10 | 3 / 3 | 1.3055925 | 0.0405659 | 51.1646–51.5153 | 56.7045–57.0600 | 5.5399–5.6141 |
| PRED-C05 | 3 | 3 / 3 | 4.6544376 | 0.6867032 | 10.7458–15.3452 | 16.4672–21.2956 | 5.7214–5.9504 |
| PRED-C05 | 5 | 3 / 3 | 2.9223515 | 0.3649271 | 22.0808–27.1334 | 27.3736–32.7755 | 5.2928–5.6622 |
| PRED-C05 | 7 | 3 / 3 | 1.9790791 | 0.2418211 | 32.7818–38.1271 | 37.9694–43.4394 | 5.1876–5.3123 |
| PRED-C05 | 10 | 3 / 3 | 1.2256234 | 0.1207010 | 48.4984–54.7321 | 53.7313–60.2084 | 5.2329–5.4789 |
| PRED-C06 | 3 | 3 / 3 | 4.3042907 | 0.3044250 | 12.4511–14.1612 | 18.6404–20.1790 | 6.0178–6.2568 |
| PRED-C06 | 5 | 3 / 3 | 2.8009581 | 0.0447705 | 24.6136–26.2134 | 30.6114–32.1922 | 5.6576–5.9978 |
| PRED-C06 | 7 | 3 / 3 | 1.9421996 | 0.0304281 | 36.1677–38.0291 | 42.1419–43.9787 | 5.6061–6.0440 |
| PRED-C06 | 10 | 3 / 3 | 1.1962061 | 0.0377459 | 53.3715–55.4843 | 58.8164–61.3313 | 5.4449–5.8470 |
| PRED-C03 | 3 | 3 / 3 | 4.7968992 | 0.2590744 | 11.0640–12.9391 | 17.2898–18.6615 | 5.7224–6.2258 |
| PRED-C03 | 5 | 3 / 3 | 2.9681072 | 0.0759114 | 22.9960–24.5070 | 28.5134–29.8735 | 5.3665–5.7416 |
| PRED-C03 | 7 | 3 / 3 | 2.0218405 | 0.0625316 | 34.2838–35.4912 | 40.2350–40.8837 | 5.3925–5.9512 |
| PRED-C03 | 10 | 3 / 3 | 1.2720028 | 0.0391374 | 50.9837–51.5433 | 56.1287–57.2300 | 5.0610–5.6867 |
| PRED-C04 | 3 | 3 / 3 | 4.2686915 | 0.1477423 | 12.8653–14.7709 | 19.2311–21.0645 | 6.0719–6.3658 |
| PRED-C04 | 5 | 3 / 3 | 2.6402726 | 0.0738248 | 25.4465–27.1069 | 31.5731–33.1703 | 6.0634–6.1266 |
| PRED-C04 | 7 | 3 / 3 | 1.7692475 | 0.0437520 | 37.6515–38.9428 | 43.4963–44.6767 | 5.7339–5.8971 |
| PRED-C04 | 10 | 3 / 3 | 1.0541572 | 0.0306701 | 54.6083–55.5726 | 60.1458–61.4929 | 5.5375–5.9541 |
| PRED-C07 | 3 | 3 / 3 | 4.8274656 | 0.0554572 | 11.0697–15.4439 | 17.1100–21.6696 | 5.5088–6.2257 |
| PRED-C07 | 5 | 3 / 3 | 3.0296768 | 0.1142077 | 22.3830–27.2835 | 27.7763–33.3780 | 5.3933–6.0945 |
| PRED-C07 | 7 | 3 / 3 | 1.8146798 | 0.1640863 | 33.3342–40.1668 | 39.8306–46.9821 | 6.4964–7.1614 |
| PRED-C07 | 10 | 3 / 2 | 1.0488748 | 0.2272829 | 51.4633–63.2957 | 58.1656–71.7189 | 6.2406–8.4232 |
| PRED-C08 | 3 | 3 / 3 | 4.1255707 | 0.1761394 | 13.3981–15.2948 | 20.4179–22.3610 | 6.8119–7.0662 |
| PRED-C08 | 5 | 3 / 3 | 2.6039817 | 0.0948754 | 26.8840–28.7033 | 33.5171–34.7714 | 6.0681–6.7639 |
| PRED-C08 | 7 | 3 / 3 | 1.7565219 | 0.0792348 | 39.6881–41.0231 | 45.5505–46.9477 | 5.7469–6.1433 |
| PRED-C08 | 10 | 3 / 3 | 1.0613119 | 0.0179283 | 56.3744–57.6622 | 61.2276–62.6367 | 4.8460–5.3199 |

No SD is unavailable in this admitted cohort. No interpolation, matched-window prediction, new support or whole-cup total was created. Observed dispersion, numerical/coordinate allowances and deletion influence remain separate quantities. Analytical repeatability, recovery/censoring and calibration uncertainty, early-input propagation, training/model-selection uncertainty, and new-condition/cross-source uncertainty remain unestablished. No TDS scatter, FIT residual or generic percentage substitutes for caffeine uncertainty, and no combined interval or noise floor is constructed.

## What this adds and what remains unestablished

1. **Historical contract:** all primary arms adequate; S2’s three increments fail exactly as before.
2. **Descriptive performance:** S2 has lower balanced primary R than every simpler arm, with adverse condition and shot comparisons. S1 already uses TDS indirectly; D0 needs no TDS.
3. **Declared perturbations:** primary average gains persist after any one retained physical-shot deletion, conditional on frozen fits. Temperature S1/S0 gains persist; D0 ordering depends on the deleted shot. This establishes influence within this cohort, not robustness to omitted or new conditions.
4. **Practical complexity:** unestablished. A positive finite sensitivity range does not supply a population-confidence PASS or an intended-use margin. S0 alone cannot establish earned complexity. The historical thresholds are not shown to be wrong; overlap does not establish equivalence.

`SCIENTIFIC_RESULT_DISPOSITION=HISTORICAL_DECISIONS_PRESERVED_WITH_FINITE_COHORT_SENSITIVITY`. `VALIDATION_FRAMEWORK_DISPOSITION`: case-local reduction completed; independent review and software/hosted QA are reported separately in [HANDOFF.md](HANDOFF.md). `CLAIM_CEILING`: retrospective descriptive retained-cohort influence conditional on frozen fits.

Pannusch/Schmieder; Mendeley **10.17632/y2tz67f6ry.1**. Source-derived aggregates retain **CC-BY-NC-3.0** treatment separately from first-party software licensing. Caffeine remains a component of TDS. No whole-cup caffeine validation, mechanism, physical validation, production readiness or unrestricted commercial rights follows.

PHYSICAL_VALIDATION=NOT_ESTABLISHED; MERGE_AUTHORIZED=false; PRODUCTION_ADOPTION_AUTHORIZED=false; NEW_MODEL_FITS=0; NEW_PREDICTIONS=0; NEW_NATIVE_SIMULATIONS=0; NATIVE_EWP_RUNS=0; HISTORICAL_SCORE_LIFECYCLE_INVOCATIONS=0; HISTORICAL_RESULTS_UNCHANGED; NO_AUTOMATIC_SUCCESSOR. One caffeine T04 case and its specific T02 interpretation are complete; the broader queues remain open.
