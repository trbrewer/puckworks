# Trigonelline mass-only delivery: retained result

**Scientific disposition: TRIGONELLINE_MASS_SHAPE_EARNED.** TR-D0 passes both
preregistered adequacy budgets in every primary condition and earns its
complexity over TR-K0. The constant control fails primary adequacy. This is
a completed scientific comparison; final software/publication qualification
is reported separately in QUALIFICATION.md. Task outcome: SUCCESS once those
completion checks and the draft PR are retained.

RESEARCH_ONLY; NO_GOVERNING_PHYSICS_CHANGE. SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION. The result qualifies
mass-only later-fraction prediction for this frozen campaign and domain.
It does not establish physical validation, equilibrium, kinetics, solver
physics, universal transfer, whole-cup closure, inventory closure or H1.
Trigonelline is a constituent of TDS, not additional TDS. Analytical
measurement uncertainty remains NOT_ESTABLISHED.

## Primary comparison

All 48 original primary windows across 12 physical shots are source-valid,
supported and numerically qualified. Each condition uses its three original
shots. R is the mean shot mass-weighted RMSE; A is the mean absolute shot bias.
Limits are R <= 0.25 mg/g and A <= 0.125 mg/g in every condition. Verdicts use
the retained unrounded numerical bounds, not the display formatting below.
Exact floating-point values, signed biases, allowances and denominators are
in RESULTS.json. Rows below show the actual lower and upper numerical bounds;
these are application allowances, not analytical uncertainty or confidence intervals.

| Condition | Arm | R bounds (mg/g) | A bounds (mg/g) | Adequacy |
| --- | --- | --- | --- | --- |
| PRED-C01 | TR-K0 | [0.7280005206176877, 0.7280005206746262] | [0.07439973505807833, 0.07439973511501684] | FAIL |
| PRED-C01 | TR-D0 | [0.1907143364393302, 0.19071433649627376] | [0.013624158125842353, 0.013624158182785893] | PASS |
| PRED-C02 | TR-K0 | [0.7002056973865309, 0.7002056974436806] | [0.038332969660902855, 0.03833296971805088] | FAIL |
| PRED-C02 | TR-D0 | [0.132395558783977, 0.13239555884112666] | [0.029449420043757592, 0.029449420100905233] | PASS |
| PRED-C05 | TR-K0 | [0.8018033127769755, 0.8018033128341269] | [0.16774237021790592, 0.16774237027505565] | FAIL |
| PRED-C05 | TR-D0 | [0.12003830418085505, 0.12003830423800828] | [0.09454131573394736, 0.09454131579109856] | PASS |
| PRED-C06 | TR-K0 | [0.6880011816184884, 0.6880011816755248] | [0.04476445170487779, 0.044764451761913376] | FAIL |
| PRED-C06 | TR-D0 | [0.09504993989812682, 0.09504993995515862] | [0.03899860126515303, 0.03899860132218391] | PASS |

| Balanced primary metric | TR-K0 | TR-D0 |
| --- | --- | --- |
| R (mg/g) | 0.7295026781284552 | 0.13454953485410706 |
| A (mg/g) | 0.08130988168897521 | 0.04415337382070924 |
| Signed mean B (mg/g; not the adequacy bias metric) | -0.029361182240235557 | -0.026655168903433946 |

Balanced R improvement is 0.5949531432743481 mg/g, with bounds
`[0.5949531432172789, 0.5949531433314174]`. Relative improvement is
81.555991651834%, with conservative lower bound
81.555991647201%. All four conditions are
definite R wins. Both the 0.05 mg/g and 15% requirements pass.
D0 minus K0 balanced A is -0.03715650786826597 mg/g,
with bounds `[-0.03715650792533411, -0.03715650781119783]`; bias improves,
so the allowed 0.025 mg/g deterioration budget passes.

## Secondary panels and limits

Secondary panels did not select models or alter thresholds. Full condition
metrics below remain undefined when any original slot is unsupported.

| Condition | Arm | Original / qualified slots | R bounds (mg/g) | A bounds (mg/g) | Adequacy |
| --- | --- | --- | --- | --- | --- |
| PRED-C03 | TR-K0 | 12 / 12 | [0.8528961789093655, 0.852896178966304] | [0.11456457534036431, 0.11456457539730285] | FAIL |
| PRED-C03 | TR-D0 | 12 / 12 | [0.09957908442295538, 0.09957908447989608] | [0.09013644717066849, 0.09013644722760913] | PASS |
| PRED-C04 | TR-K0 | 12 / 12 | [0.7288489692777023, 0.7288489693347375] | [0.09176848334369411, 0.09176848340072877] | FAIL |
| PRED-C04 | TR-D0 | 12 / 12 | [0.04930844129470556, 0.04930844135173436] | [0.04101976865990991, 0.04101976871693786] | PASS |
| PRED-C07 | TR-K0 | 12 / 11 | UNDEFINED: incomplete support | UNDEFINED: incomplete support | FAIL |
| PRED-C07 | TR-D0 | 12 / 11 | UNDEFINED: incomplete support | UNDEFINED: incomplete support | INCOMPLETE_SUPPORT |
| PRED-C08 | TR-K0 | 12 / 12 | [0.6258976731487269, 0.6258976732056654] | [0.16696580937086103, 0.16696580942779948] | FAIL |
| PRED-C08 | TR-D0 | 12 / 12 | [0.17627541872169014, 0.17627541877862227] | [0.09227833407986324, 0.09227833413679537] | PASS |

Temperature support is 24/24; TR-D0 passes both conditions and TR-K0 fails.
Flow support is 23/24. C07 has one OUTSIDE_COMMON_TRAINING_MASS_DOMAIN slot
in each arm, retained explicitly. C07 and the full flow panel have no complete
R/A summary. Its supported-subset diagnostics are labeled separately in
RESULTS.json and cannot supply a complete-scope success. K0 is still a definite
flow failure: the two complete C07 shots already give a full-original-condition
R lower bound of 0.5377437611694161 mg/g, above the limit. D0 flow adequacy is
INCOMPLETE_SUPPORT. C08 D0 passes, with all three C08 shots extrapolating
the training range of m2; no primary or temperature shot extrapolates a
feature range. The same feature-range flags are retained for both arms.

## Source, fitting and numerical qualification

The 45-shot, 15-design FIT campaign retains all 180 intended target slots:
177 supported and three UNAVAILABLE_MEASURED_MASS_PREFIX. Every design retains
at least two physical shots with at least three qualified windows. No vial
mass, missing observation, unassayed interval or chemical outcome was filled.
Original dilution/HPLC reconstructions and all source hashes are unchanged.
Pannusch and Schmieder share source lineage and are counted once.

Fixed whole-design development selected lambda 0.0001. Mean held-design R
was 0.157496492600071 mg/g for selected D0 versus 0.7931349509560043 for K0.
These development values are selection diagnostics, not independent validation.
All 183 permitted iterative starts converged; zero failed or boundary starts.
There were 16 analytic K0 fits, 25,875 actual residual calls including 24,240
numerical-Jacobian calls, and at most 178 calls per start. Optimizer wall time
was 5.2541000079363585 s; the cumulative fitting-clock span was
56.57155203819275 s. One worker and one BLAS thread were used; recorded peak
RSS was 84,592 KiB. No rescue fit or counter reset occurred.

Maximum PRED interval allowance was 2.0388003927031585e-16 kg versus the
1e-9 kg limit. All supported intervals passed split-at-knots refinement and
independent adaptive integration. The inherited explicit source-anchor rule
was preserved; no clipping, geometry repair or tolerance expansion was used.
Per-shot results and all original denominators are retained privately in
shot_results.json, bound by SCORE_COMPLETION.json. Source originals and
row-level observations/predictions remain outside Git.

## Immutable experiment and authority

Reviewed scientific producer: `de31200f272711ca6b2e9fc5dc7c4881c406ab56`; tree
`dd6fd3c9d835ef9793ba88a47661c6abb37e4613`. Freeze SHA-256:
`6f1b1afc73615eafb9b463b49089a1069d60179ea96b2a02a2951a9ec22f0b12`.
The fresh independent Codex reviewer approved exactly this freeze before
any outcome join. Its unchanged report and approval are INDEPENDENT_REVIEW.md
and review.json. The later reporting/publication identities are separate;
none changes the 53 frozen code/protocol files or 646 pre-score artifacts.

Exactly one approved outcome join and one scientific score completed.
SCORE_RECEIPT.json and SCORE_COMPLETION.json bind the immutable predictions,
review, retained result and private shot/outcome files. Reporting reads this
retained result; saved-model verification does not optimize or rescore.

Source-derived models and results: CC-BY-NC-3.0, Pannusch/Schmieder, Mendeley
10.17632/y2tz67f6ry.1; not MIT. No source originals are redistributed.

MERGE_AUTHORIZED=false; PRODUCTION_ADOPTION_AUTHORIZED=false;
NATIVE_EWP_RUNS=0; NO_SUCCESSOR_AUTHORIZED.
