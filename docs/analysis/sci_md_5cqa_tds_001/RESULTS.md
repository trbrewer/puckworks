# Results: early-TDS-conditioned 5-CQA interval delivery

**TESTED_TDS_CONDITIONED_FIVE_CQA_FAMILIES_INADEQUATE.** All three new heads fail both engineering adequacy limits in every primary condition. No adequate new arm exists and no complexity increment earns replacement. The approved single evaluation is complete; no further experiment or successor is selected.

SCI-MD-5CQA-TDS-001 / G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY. SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION / PHYSICAL_VALIDATION_NOT_ESTABLISHED.

## Primary adequacy

Every primary condition requires mean shot R ≤ 0.25 mg/g and mean absolute shot bias ≤ 0.125 mg/g. R and signed bias use measured interval-mass weights within each original shot; absolute bias is taken before equal shot and condition averaging. These are engineering budgets, not assay uncertainty, sensory limits or health limits. All arms have complete 48/48 qualified primary support.

| Arm | Balanced R (mg/g) | Balanced absolute bias (mg/g) | Adequate primary conditions | Arm adequacy |
|---|---:|---:|---:|---|
| E0 | 0.36451046 | 0.35013005 | 0/4 | FAIL |
| D0 | 0.36352094 | 0.34029365 | 0/4 | FAIL |
| S0 | 0.40148318 | 0.37850143 | 0/4 | FAIL |
| S1 | 0.38166296 | 0.32894881 | 0/4 | FAIL |
| S2 | 0.41041993 | 0.36442191 | 0/4 | FAIL |

| Condition | Arm | Mean shot R (mg/g) | Mean absolute shot bias (mg/g) | Adequacy |
|---|---|---:|---:|---|
| PRED-C01 | E0 | 0.29572387 | 0.28172298 | FAIL |
| PRED-C01 | D0 | 0.31757525 | 0.28563803 | FAIL |
| PRED-C01 | S0 | 0.36213306 | 0.34140854 | FAIL |
| PRED-C01 | S1 | 0.33214053 | 0.27107268 | FAIL |
| PRED-C01 | S2 | 0.37685064 | 0.33217961 | FAIL |
| PRED-C02 | E0 | 0.32828148 | 0.32714751 | FAIL |
| PRED-C02 | D0 | 0.32971905 | 0.32003076 | FAIL |
| PRED-C02 | S0 | 0.36264410 | 0.35550462 | FAIL |
| PRED-C02 | S1 | 0.32840971 | 0.30629814 | FAIL |
| PRED-C02 | S2 | 0.34746019 | 0.32532317 | FAIL |
| PRED-C05 | E0 | 0.44742293 | 0.41035779 | FAIL |
| PRED-C05 | D0 | 0.43560860 | 0.39515859 | FAIL |
| PRED-C05 | S0 | 0.49178736 | 0.45174451 | FAIL |
| PRED-C05 | S1 | 0.48341530 | 0.41072363 | FAIL |
| PRED-C05 | S2 | 0.49242169 | 0.42452341 | FAIL |
| PRED-C06 | E0 | 0.38661358 | 0.38129191 | FAIL |
| PRED-C06 | D0 | 0.37118084 | 0.36034722 | FAIL |
| PRED-C06 | S0 | 0.38936820 | 0.36534804 | FAIL |
| PRED-C06 | S1 | 0.38268629 | 0.32770078 | FAIL |
| PRED-C06 | S2 | 0.42494718 | 0.37566144 | FAIL |

All tabulated primary failures are definite with conservative numerical bounds. Maximum condition-level R/absolute-bias allowance is below 2.86e-11 mg/g; decisions use unrounded values in [RESULTS.json](RESULTS.json). Every primary condition has three original physical shots and twelve original later-fraction slots. Historical E0/D0 also fail all four conditions; their model and prediction bytes replay unchanged. Their predecessor scoring command was not rerun.

## Composition complexity

Replacement requires candidate adequacy, ≥0.05 mg/g and ≥15% balanced R reduction, definite R improvement in at least three primary conditions, and ≤0.025 mg/g absolute-bias deterioration. Positive R reduction is an improvement; positive bias change is deterioration.

| Comparison | R reduction (mg/g) | Relative R reduction | Definite condition wins | Absolute-bias change (mg/g) | Candidate adequate | Complexity |
|---|---:|---:|---:|---:|---|---|
| S1 vs S0 | 0.01982022 | 4.9367% | 4/4 | -0.04955262 | FAIL | FAIL |
| S2 vs S1 | -0.02875697 | -7.5346% | 0/4 | 0.03547310 | FAIL | FAIL |
| S2 vs S0 | -0.00893675 | -2.2259% | 1/4 | -0.01407952 | FAIL | FAIL |

S1 improves R over S0 in all four conditions, but its 0.01982 mg/g (4.94%) gain misses both material-gain thresholds and it remains inadequate. S2 has worse R than S1 in all four conditions, with absolute-bias deterioration of 0.03547 mg/g; it also fails the S0 comparison. Direct use of early TDS in the composition head therefore earns no replacement in this fixed comparison.

- (A) Adequacy: E0, D0, S0, S1 and S2 all FAIL.
- (B) Pairwise complexity: S1/S0, S2/S1 and S2/S0 all FAIL.
- (C) Least-complex adequate new arm: none.
- (D) More-complex adequate arm earning replacement: none.

Both S1 and S2 receive early TDS through their C2 parent. S2/S1 addresses its additional use in the composition head. This result is not a causal attribution to TDS, proof that every possible 5-CQA model fails, new extraction kinetics, identified transport, or confirmation of H1. An adequate model without a sufficient gain would have been reported as ADEQUATE_INCREMENT_NOT_ESTABLISHED; no new arm meets adequacy here.

## Secondary conditions and retained support

Temperature has 6 original shots and 24/24 windows. Flow has 6 original shots and 23/24 windows; C08 retains twelve original slots with eleven supported. Full flow summaries remain unavailable where the original shot is incomplete. Supported-subset diagnostics do not repair the denominator or rescue the primary result.

| Condition | Arm | Qualified / original slots | Full-condition R (mg/g) | Full-condition absolute bias (mg/g) | Supported-subset R / absolute bias (mg/g) |
|---|---|---:|---:|---:|---|
| PRED-C03 | E0 | 12/12 | 0.47714884 | 0.43566599 | 0.47714884 / 0.43566599 |
| PRED-C03 | D0 | 12/12 | 0.45917690 | 0.43360216 | 0.45917690 / 0.43360216 |
| PRED-C03 | S0 | 12/12 | 0.54608978 | 0.48049137 | 0.54608978 / 0.48049137 |
| PRED-C03 | S1 | 12/12 | 0.52614713 | 0.41731168 | 0.52614713 / 0.41731168 |
| PRED-C03 | S2 | 12/12 | 0.56397124 | 0.46693453 | 0.56397124 / 0.46693453 |
| PRED-C04 | E0 | 12/12 | 0.31878103 | 0.31179595 | 0.31878103 / 0.31179595 |
| PRED-C04 | D0 | 12/12 | 0.30397348 | 0.27064311 | 0.30397348 / 0.27064311 |
| PRED-C04 | S0 | 12/12 | 0.30106413 | 0.28332680 | 0.30106413 / 0.28332680 |
| PRED-C04 | S1 | 12/12 | 0.31584667 | 0.26423412 | 0.31584667 / 0.26423412 |
| PRED-C04 | S2 | 12/12 | 0.33287361 | 0.27817129 | 0.33287361 / 0.27817129 |
| PRED-C07 | E0 | 11/12 | UNAVAILABLE | UNAVAILABLE | 0.47322486 / 0.42535709 |
| PRED-C07 | D0 | 11/12 | UNAVAILABLE | UNAVAILABLE | 0.49251735 / 0.41559373 |
| PRED-C07 | S0 | 11/12 | UNAVAILABLE | UNAVAILABLE | 0.52411757 / 0.46583050 |
| PRED-C07 | S1 | 11/12 | UNAVAILABLE | UNAVAILABLE | 0.53251442 / 0.42901055 |
| PRED-C07 | S2 | 11/12 | UNAVAILABLE | UNAVAILABLE | 0.53319912 / 0.43958538 |
| PRED-C08 | E0 | 12/12 | 0.32251854 | 0.32010285 | 0.32251854 / 0.32010285 |
| PRED-C08 | D0 | 12/12 | 0.28327013 | 0.26560323 | 0.28327013 / 0.26560323 |
| PRED-C08 | S0 | 12/12 | 0.33683837 | 0.25436509 | 0.33683837 / 0.25436509 |
| PRED-C08 | S1 | 12/12 | 0.33541085 | 0.24590622 | 0.33541085 / 0.24590622 |
| PRED-C08 | S2 | 12/12 | 0.33810239 | 0.21436096 | 0.33810239 / 0.21436096 |

All 5 × 96 = 480 original prediction records are retained privately, including five explicit copies of the unsupported flow slot. FIT retained 177 supported intervals out of 180 across all 45 shots and 15 original designs. Exact full-source support, reasons, model feature-extrapolation counts and conservative bounds are in SOURCE_COUNTS.json and RESULTS.json. Original chemistry was unrounded; no imputation, clipping, target-dependent exclusion or nominal-flow substitution. Unknown lot/roast batch and shared Pannusch/Schmieder lineage remain qualifications.

## Development, identities and verification

The pre-fit protocol was committed at `c769074e88a68483878a677f47d016efab5da8c2`. Both S1 and S2 selected lambda 0.0001 on the fixed whole-design FIT development. Balanced held-design R was 0.14420891 (S0), 0.12939172 (S1) and 0.11456431 mg/g (S2). This is development/model selection, not unbiased nested validation: C2 and its hyperparameter have prior selection history. S0 final share is 0.032486760753754416. The final domain ends at 0.06971540000000001 kg and queries begin at m1+m2.

Evaluated producer `5fb08749315ff145f7f68d57b055dd5a79c95f5d`, scientific tree `e9c1ce191c787d31d09429716b2121f47732a1cf`; freeze SHA-256 `f7495e5c75f56698507126be89be1dd4c9a464227c8d7461f0d8655dec1859da`. [Independent review](INDEPENDENT_REVIEW.md) approved exactly this freeze before the sole outcome join. [RESULT_BINDING.json](RESULT_BINDING.json), FREEZE.json, SCORE_RECEIPT.json and SCORE_COMPLETION.json bind the retained evidence. Saved inference subsequently reproduced all 480 records exactly, with zero new fitting, outcome joins or scoring. Report generation read retained scores only.

See [NUMERICAL_SOFTWARE_QUALIFICATION.md](NUMERICAL_SOFTWARE_QUALIFICATION.md), [HANDOFF.md](HANDOFF.md) and [REPRODUCE.md](REPRODUCE.md). No post-score scientific change, retuning, second score, EWP change, production promotion or merge. Numerical qualification is not physical validation; analytical uncertainty is not established. Source-derived models/results retain Pannusch/Schmieder CC-BY-NC-3.0 attribution, Mendeley 10.17632/y2tz67f6ry.1, separately from first-party software licensing. Individual rows and detailed logs remain outside Git.
