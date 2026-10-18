# Retained 5-CQA gain stability and RMSE decomposition

**L12 retains a positive primary RMSE gain over both matched single-assay controls in every declared physical-shot deletion. L2M versus L1M does not.** The benefit over L1M consistently comes from a favorable centered-residual contribution offsetting an adverse squared-mean-error contribution; both contributions favor L12 over L2M. All historical inadequacy and complexity decisions remain unchanged.

Gain is reference R minus candidate R; positive favors the candidate. In the tables, **C_B** means **Contribution from squared mean shot error**, and **C_V** means **Contribution from within-shot centered residual variation**. Each is calculated per paired shot before nested averaging, and C_B + C_V equals the balanced RMSE gain. All values are mg/g; ranges contain deletions only, with baseline reported separately.

| Primary comparison | Baseline gain | Twelve-deletion gain range | Positive points / positive numerical lower endpoints | Baseline C_B | Baseline C_V |
|---|---:|---:|---:|---:|---:|
| L12 / L1M | +0.046212975 | [+0.036349266, +0.054390519] | 12/12 / 12/12 | -0.023311719 | +0.069524694 |
| L12 / L2M | +0.051972584 | [+0.043943295, +0.058180029] | 12/12 / 12/12 | +0.012736410 | +0.039236173 |
| L2M / L1M | -0.005759608 | [-0.012086135, +0.002050320] | 2/12 / 2/12 | -0.033123367 | +0.027363759 |

L12/L1M has C_B<0 and C_V>0 in all 12 deletions, with those signs also supported by their separate numerical endpoints. C_V always more than offsets C_B. L12/L2M has both contributions positive in all 12. L2M/L1M also has C_B<0 and C_V>0 in all 12, but the favorable contribution is insufficient in 10; its baseline net gain is negative. None of these statements identifies a causal or correctable assay mechanism.

**TESTED_EARLY_ASSAY_FAMILIES_INADEQUATE** is preserved. There is no earned two-assay route. Every arm remains inadequate in all 12 primary deletion scenarios; each scenario leaves three originally failing conditions untouched. PHYSICAL_VALIDATION=NOT_ESTABLISHED and ANALYTICAL_UNCERTAINTY=NOT_ESTABLISHED.

## Temperature is a separate diagnostic

| Temperature comparison | Baseline gain | Six-deletion gain range | Positive points / positive numerical lower endpoints | Baseline C_B | Baseline C_V |
|---|---:|---:|---:|---:|---:|
| L12 / L1M | -0.001114821 | [-0.014466032, +0.016138820] | 2/6 / 2/6 | -0.012469599 | +0.011354777 |
| L12 / L2M | +0.048763010 | [+0.040772304, +0.058721390] | 6/6 / 6/6 | +0.019539199 | +0.029223811 |
| L2M / L1M | -0.049877832 | [-0.063738642, -0.024633484] | 0/6 / 0/6 | -0.030450001 | -0.019427831 |

L12/L1M retains its adverse baseline of -0.001114821440 mg/g: C03 improves, C04 worsens. Its squared-mean-error contribution is adverse in all six deletions; the centered-residual contribution is positive in four and negative in two. It does not consistently offset the adverse contribution. L12/L2M has a positive gain and both contributions positive in all six. L2M/L1M is adverse in all six, with C_B always negative and C_V negative in five, positive in one; that favorable exception does not offset C_B. Every stated contribution sign is supported by the corresponding numerical endpoints. Temperature cannot rescue primary failure, and no three-of-four win rule is applied to two conditions.

| Panel / comparison | C_B deletion range | C_V deletion range |
|---|---:|---:|
| Primary: L12 / L1M | [-0.027788152, -0.017646319] | [+0.057061120, +0.082046359] |
| Primary: L12 / L2M | [+0.009792064, +0.014653390] | [+0.030179518, +0.044002362] |
| Primary: L2M / L1M | [-0.039057827, -0.028461224] | [+0.018641532, +0.035268316] |
| Temperature: L12 / L1M | [-0.023693340, -0.004965874] | [-0.004667764, +0.031265665] |
| Temperature: L12 / L2M | [+0.010959225, +0.026845351] | [+0.013926953, +0.037908367] |
| Temperature: L2M / L1M | [-0.043589350, -0.020298395] | [-0.040962974, +0.015112693] |

## Baseline conditions and distinct bias quantities

These are baseline condition aggregates, not condition-specific deletion summaries. L12 improves all four primary conditions against either reference. L2M/L1M is adverse in C02, C05 and C06; in C06 both contributions are adverse. Temperature L2M/L1M is adverse in both C03 and C04.

| Condition | Comparison | Baseline gain | Baseline C_B | Baseline C_V |
|---|---|---:|---:|---:|
| PRED-C01 | L12 / L1M | +0.086264473 | -0.046401239 | +0.132665712 |
| PRED-C01 | L12 / L2M | +0.050661844 | +0.008008572 | +0.042653272 |
| PRED-C01 | L2M / L1M | +0.035602628 | -0.050025566 | +0.085628195 |
| PRED-C02 | L12 / L1M | +0.047072370 | -0.029441570 | +0.076513940 |
| PRED-C02 | L12 / L2M | +0.058878796 | +0.015984236 | +0.042894560 |
| PRED-C02 | L2M / L1M | -0.011806427 | -0.041097714 | +0.029291287 |
| PRED-C05 | L12 / L1M | +0.024599758 | -0.015064178 | +0.039663936 |
| PRED-C05 | L12 / L2M | +0.034375435 | +0.009244509 | +0.025130926 |
| PRED-C05 | L2M / L1M | -0.009775677 | -0.023199967 | +0.013424290 |
| PRED-C06 | L12 / L1M | +0.026915300 | -0.002339888 | +0.029255188 |
| PRED-C06 | L12 / L2M | +0.063974258 | +0.017708323 | +0.046265935 |
| PRED-C06 | L2M / L1M | -0.037058958 | -0.018170223 | -0.018888735 |
| PRED-C03 | L12 / L1M | +0.016753214 | -0.022477971 | +0.039231185 |
| PRED-C03 | L12 / L2M | +0.026877784 | +0.008309707 | +0.018568077 |
| PRED-C03 | L2M / L1M | -0.010124570 | -0.029235548 | +0.019110978 |
| PRED-C04 | L12 / L1M | -0.018982857 | -0.002461226 | -0.016521631 |
| PRED-C04 | L12 / L2M | +0.070648236 | +0.030768692 | +0.039879545 |
| PRED-C04 | L2M / L1M | -0.089631093 | -0.031664453 | -0.057966640 |

At temperature C04, L12/L1M improves A by 0.003653494 mg/g even though its squared-mean-error contribution is adverse. The quantities have different aggregation and denominators: signed B change, mean abs(B) deterioration, and the RMSE-scale B² contribution must remain separate.

| Panel / comparison | Baseline signed B change (candidate-reference) | Baseline A deterioration | Deletion A-deterioration range |
|---|---:|---:|---:|
| Primary: L12 / L1M | -0.038684972 | +0.038684972 | [+0.030815951, +0.044862379] |
| Primary: L12 / L2M | +0.015276169 | -0.015276169 | [-0.017564339, -0.012230711] |
| Primary: L2M / L1M | -0.053961141 | +0.053961141 | [+0.047899627, +0.062426718] |
| Temperature: L12 / L1M | -0.013091055 | +0.013091055 | [+0.002135563, +0.026206192] |
| Temperature: L12 / L2M | +0.021163048 | -0.021163048 | [-0.027783263, -0.012720689] |
| Temperature: L2M / L1M | -0.034254103 | +0.034254103 | [+0.021204982, +0.049734024] |

The signed-B deletion ranges and all separate numerical enclosures are in [RESULTS.json](RESULTS.json). No calibrated, recentered or otherwise corrected predictor was fitted or evaluated.

## Historical acceptance and crossed margins

Historical primary balanced R/A reproduces exactly at unrounded precision: L1M 0.343708141 / 0.215687390; L2M 0.349467750 / 0.269648531; L12 0.297495166 / 0.254372362 mg/g (displayed to nine decimals). Every arm fails both R<=0.25 and A<=0.125 in every primary condition. All three final comparisons fail.

Each original material comparison also requires >=0.05 mg/g gain, >=15% relative reduction, >=3/4 strict definite condition wins and <=0.025 mg/g A deterioration. Candidate adequacy, gain_status and final status are preserved separately. Both L12 comparisons would have to pass to earn two assays. The original relative component is upper(R_candidate-0.85*R_reference, u_candidate+0.85*u_reference, 0); ratio denominator guards do not alter it.

| Primary comparison | Historical absolute / relative / wins / A-budget | Deletions passing absolute / relative / wins / A-budget | Deletion definite wins | Final comparison |
|---|---|---|---:|---|
| L12 / L1M | FAIL / FAIL / PASS / FAIL | 3/12 / 2/12 / 12/12 / 0/12 | 3–4 | FAIL baseline and 12/12 deletions |
| L12 / L2M | PASS / FAIL / PASS / PASS | 10/12 / 5/12 / 12/12 / 12/12 | 4–4 | FAIL baseline and 12/12 deletions |
| L2M / L1M | FAIL / FAIL / FAIL / FAIL | 0/12 / 0/12 / 0/12 / 0/12 | 1–2 | FAIL baseline and 12/12 deletions |

Thus absolute and relative gain margins can cross under deletion even where gain sign is stable. L12/L1M never meets the A-deterioration budget; L12/L2M always does. The original 15% failure for L12/L2M remains the historical decision despite five diagnostic deletions passing that component. L2M/L1M never meets any material-gain component. No component is numerically UNRESOLVED in these families.

Temperature scalar budgets are diagnostic only: L12/L1M passes neither gain margin in any deletion and passes the A budget in 5/6; L12/L2M passes absolute gain in 2/6, relative gain in 1/6 and A budget in 6/6; L2M/L1M passes neither gain margin and passes A budget in 1/6. These are not temperature material-value adjudications.

## Evidence, support and numerical interpretation

All eight named retained inputs and the public evidence chain authenticated. The historical STARTED receipt is intentional; the separately authenticated COMPLETE record records exactly one original scientific score. The analysis specification was committed before any new empirical reduction; historical result and schema exposure was disclosed. All 23 admitted input/authority files were rehashed unchanged afterward. Original workbook qualification is reused, not repeated.

Exactly three matched arms remain: L1M uses m1,m2,q1; L2M uses m1,m2,q2; L12 uses all four, forecasting from m1+m2. The assays are measured 5CQA interval averages. All share the historical 42 eligible FIT shots from the original 45 and three q2 INVALID_SPILL exclusions. Historical E0/D0/A1/L1 are contextual; historical L1 is not L1M.

All 24 original PRED shots and 96 observation slots remain in population metadata, with original fractions 3/5/7/10 and intervening vial-mass coordinates. Primary/temperature/flow support is 48/48, 24/24 and 23/24 per arm. Each primary deletion retains 11 shots/44 windows; temperature retains five/20. The same entire physical trajectory is omitted across arms. The affected condition averages two remaining shots, while conditions retain equal weights. These logical masks neither remove source records nor change historical acceptance.

Flow has baseline diagnostics only. Full-flow point metrics and decomposition remain unavailable. C07 L1M remains INCOMPLETE_SUPPORT; L2M and L12 retain definite failure from original-three-shot-denominator A lower bounds 0.166164611 and 0.154031495 mg/g. Supported-subset baseline gains are +0.028039227, +0.041608824 and -0.013569597 mg/g for L12/L1M, L12/L2M and L2M/L1M, respectively. These retain all six shots and equal condition weights; the incomplete shot uses three supported windows. They are not full four-window results.

Authenticated predictions and raw JSON states verify the detailed flags and unchanged published totals:

| Arm | Primary flagged /12 | Temperature flagged /6 | Flow flagged /6 |
|---|---:|---:|---:|
| L1M | 9 | 5 | 6 |
| L2M | 3 | 3 | 3 |
| L12 | 9 | 5 | 6 |

Every flagged shot remains included. State feature-domain comparisons used raw JSON only; no model loading or conditioning occurred. Detailed shot flags and deletion flag summaries are verified privately, not unverified in this execution. Flags do not establish transfer validity or in-domain accuracy.

Historical metric/decision reproduction has maximum discrepancy zero and no decision discrepancy. The independent deletion identity has maximum discrepancy 7.98e-17 mg/g. The direct fraction route checks 96 unique observation slots and 288 prediction slots (285 supported), using stored concentration and the total allowance once. Its R/B/allowance, V and paired-contribution checks have 113 nonzero arithmetic differences with maximum 9.37e-17, within the declared arithmetic-only tolerance. No point V needed roundoff clamping.

R²=B²+V holds on measured fraction supports. R², B² and V have units (mg/g)²; C_B and C_V have units mg/g. Outward-rounded interval arithmetic propagates retained R/B allowances, signed B squares, differences, positive-denominator division and actual nested weights. V enclosures intersect V>=0 explicitly; no unconstrained V lower endpoint was negative in this core execution. A negative point V would be a separate inconsistency, never excused by prediction allowances.

Baseline net-gain allowances are about 5.70–5.71e-11 mg/g; each deletion uses its own allowance. Public JSON retains the direct net enclosure separately from the wider independently propagated contribution enclosures. All point-sign counts above match numerically resolved signs. Display rounding and the 512-ulp reconciliation tolerance never enter threshold comparisons. The helper compares supplied evidence and does not authenticate inputs or propagate errors.

## Completion and remaining limits

| Component | Status |
|---|---|
| RMSE decomposition | COMPLETE |
| detailed extrapolation verification | COMPLETE |
| direct fraction cross check | COMPLETE |
| historical metric decision reproduction | COMPLETE |
| primary deletion sensitivity | COMPLETE |
| temperature deletion sensitivity | COMPLETE |

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL. Retained numerical-allowance conclusions, historical contractual decisions and stability within the exact finite deletion family are distinct. The accepted policy helper labels deletion extrema as sensitivity evidence, leaving broader resolution unresolved. They are not confidence intervals, population reliability bounds or prediction intervals for future shots.

Training/model-selection, assay/calibration, input-measurement and new-condition/cross-source uncertainty remain unquantified. V is measured-support residual variation, not assay variance, irreducible noise, unbiased sample variance or continuous-curve shape error. No n-1 correction applies. These algebraic associations identify no calibration defect, common batch offset, instrument fault, inventory mismatch or correctable causal mechanism.

The comparative benefit can coexist with inadequate absolute predictions and no earned complexity. Failure to earn complexity establishes neither absence of benefit nor equivalence. No independently justified intended-use practical-value basis is added. No physical validation, production adoption or successor follows. This completes one October 9 T04 case and one bounded 5-CQA T02 interpretation, not either broader queue.

[Protocol](PROTOCOL.md) · [input identities](INPUT_MANIFEST.json) · [machine result](RESULTS.json) · [independent review](INDEPENDENT_REVIEW.md) · [reproduction](REPRODUCE.md) · [handoff and verification](HANDOFF.md). Source-derived aggregates: Pannusch/Schmieder, CC-BY-NC-3.0, Mendeley DOI 10.17632/y2tz67f6ry.1; first-party software licensing is separate. Individual shot results, complete deletion vectors, per-condition deletion extrema, residuals and actual private paths remain outside Git.
