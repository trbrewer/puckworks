# Mass-only 5-CQA delivery: completed frozen comparison

**TESTED_FIVE_CQA_FAMILIES_INADEQUATE**. Both predeclared families definitely
fail the engineering adequacy budgets on complete primary evidence. The strict
saved-model research API is implemented, tested, independently reviewed and
scored once. G1 / NO_GOVERNING_PHYSICS_CHANGE. This completed negative result
ends the authorized comparison; it does not authorize another family.

## Primary result

Each entry averages the original three physical shots. R is mean shot
mass-weighted RMSE; A is mean absolute shot bias, both mg/g. Every primary
condition retains 12/12 windows. Limits are R <= 0.25 and A <= 0.125.

| Condition | E0 R | E0 A | D0 R | D0 A | Adequacy E0 / D0 |
| --- | ---: | ---: | ---: | ---: | --- |
| PRED-C01 | 0.295723871 | 0.281722982 | 0.317575254 | 0.285638030 | FAIL / FAIL |
| PRED-C02 | 0.328281479 | 0.327147515 | 0.329719055 | 0.320030765 | FAIL / FAIL |
| PRED-C05 | 0.447422925 | 0.410357787 | 0.435608603 | 0.395158590 | FAIL / FAIL |
| PRED-C06 | 0.386613577 | 0.381291909 | 0.371180838 | 0.360347217 | FAIL / FAIL |
| Balanced | 0.364510463 | 0.350130048 | 0.363520937 | 0.340293651 | FAIL / FAIL |

Both R and A exceed their limits in every primary condition. Signed shot
biases are negative throughout the primary panel; the models underpredict.
All condition numerical allowances are below 2.87e-11 mg/g and are included
in the decisions. These are definite failures, not rounded or unresolved
threshold overlaps. Exact values, bounds and every condition are retained
in [RESULTS.json](RESULTS.json), copied from the sole retained score.

## D0 increment

| Requirement | Frozen result | Decision |
| --- | --- | --- |
| Adequate in every primary condition | 0/4 conditions pass | FAIL |
| Balanced R reduction >= 0.05 mg/g | 0.000989525380 mg/g; bounds [0.000989525323, 0.000989525437] | FAIL |
| Relative balanced R reduction >= 15% | 0.271466935%; lower bound 0.271466919% | FAIL |
| Definite R improvement in >= 3/4 conditions | 2/4 (C05, C06); C01 and C02 worsen | FAIL |
| Balanced A worsening <= 0.025 mg/g | -0.009836397679 mg/g; bounds [-0.009836397736, -0.009836397622] | PASS |

The last criterion passes because absolute bias improves. It cannot rescue
the failed adequacy or other increments. The tested flexible architecture
combines curve shape and mass conditioning; their contributions cannot be
separated by this two-arm comparison.

## Secondary conditions and support

| Panel / condition | Supported / original windows | E0 R | E0 A | D0 R | D0 A | Scope |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| temperature_stress / PRED-C03 | 12/12 | 0.477148837 | 0.435665986 | 0.459176897 | 0.433602156 | Full condition; both FAIL |
| temperature_stress / PRED-C04 | 12/12 | 0.318781031 | 0.311795954 | 0.303973478 | 0.270643112 | Full condition; both FAIL |
| flow_stress / PRED-C07 | 11/12 | 0.473224856 | 0.425357086 | 0.492517345 | 0.415593730 | Supported-subset diagnostic only |
| flow_stress / PRED-C08 | 12/12 | 0.322518535 | 0.320102852 | 0.283270133 | 0.265603232 | Full condition; both FAIL |

Temperature retains 24/24 windows; both arms fail C03 and C04. Flow retains
23/24 windows. C07 has one interval above the training mass domain: no full
C07 or balanced full-flow point estimate is reported. Even assigning zero
bias to its incomplete shot, the original-three-shot C07 lower bounds on A
are 0.194704 (E0) and 0.196170 (D0) mg/g, which already exceed 0.125.
C08 has 12/12 windows and both arms fail. All three C08 shots extrapolate
m2 beyond the FIT feature range; they remain in the result. Primary and
temperature have no feature-range extrapolation. E0 carries the same
coordinate diagnostics but does not condition its curve on m1/m2.
Secondary results cannot rescue primary failure or establish full-flow adequacy.

FIT retains all 15 designs and 45 physical shots: 177/180 supervised windows.
Three missing measured prefixes remain excluded, with original slots and reasons
retained. Primary is 12 shots/48 windows, temperature six shots/24 windows,
and flow six shots/24 original windows. Original-vial geometry includes
unassayed intervening vials; no missing prefix was reconstructed. Derived
upper support is 0.06971540000000001 kg. Modeled gaps and remaining_5cqa
are model integrals, not measured whole-cup delivery or inventory closure.

## Development, identities and execution

Fifteen whole-design FIT development folds selected D0 lambda 0.0001 from
the fixed four-value grid. Development R is 0.201171202 mg/g for E0 and
0.182372860 for selected D0; these are selection estimates, not unbiased
nested validation. [DEVELOPMENT.json](DEVELOPMENT.json) retains all candidates.
No PRED concentration affected fitting, support, preprocessing or selection.

The frozen producer is `cadb7aeaa00630ad311970610ec5763ad4ffc9a3`, tree
`f570fab32f9105cc77e9cc3eb89b5a952448e9f6`. Source, model and prediction
bindings are in [FREEZE_BINDING.json](FREEZE_BINDING.json),
[FREEZE.json](FREEZE.json) and [SOURCE_IDENTITIES.json](SOURCE_IDENTITIES.json).
A fresh independent Codex agent approved this exact freeze before scoring;
[review.json](review.json) is the genuine receipt, with no unresolved finding
and no correction requested. It is not a human review or hosted PR approval.

Exactly 231 experimental starts completed: E0 48/48, D0 183/183; 25,092
actual residual calls, including 23,137 numerical-Jacobian calls; maximum
161 per start versus the 8,000 ceiling. No failed or boundary starts.
Fitting-stage wall time is 38.974016 seconds of 60 minutes, one worker and
one BLAS thread, peak fitting RSS 82,664 KiB under a 12-GiB process cap.
The score and outcome join each ran once. Maximum evaluated-interval
allowance is 2.0385947088335044e-16 kg, below 1e-9 kg.
The original blocked attempt used zero experimental budget; its 1418.985946
seconds and all evidence remain unchanged. The continuation started
2026-09-28 22:48:20 UTC with a six-hour limit; its G0 prerequisite finished
in about 20 minutes, within 90 minutes. Final QA and hosted CI are reported
separately in [QUALIFICATION.md](QUALIFICATION.md).

## Limits and reuse

SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE. This is a later-campaign
research comparison, not fresh blind or independent validation. Numerical
qualification is not physical validation or assay uncertainty. Budgets are
engineering research choices, not assay, health or sensory thresholds.
No identified extraction kinetics, transport, universal transfer or first-ever
5-CQA modeling claim follows. Pannusch/Schmieder are one shared lineage.

The strict 5CQA API accepts measured m1/m2 and cumulative interval endpoints
only. [COMMANDS.md](COMMANDS.md) provides a runnable saved-model example and
the six task stages. Verify replays inference; report reads this retained score.
Source-derived models/results retain CC-BY-NC-3.0 attribution to
Pannusch/Schmieder, Mendeley DOI 10.17632/y2tz67f6ry.1, separately from software
licensing. Original binaries, detailed rows and logs remain private.
No production adoption, registry/default promotion, EWP change, merge or
successor is authorized. No post-score science was changed.
