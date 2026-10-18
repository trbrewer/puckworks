# RHEOLOGY-010 decision-resolution scientific addendum

The retained evidence reproduces **all 32 original decisions without discrepancy**.
All 24 E2-versus-C approximation decisions remain PASS, meet the original precision
rule, and have empirical numerical sensitivity envelopes entirely below their
original budgets. This preserves
`E2_CONDUCTANCE_MATCHED_REVERSAL_SUFFICIENT_FOR_TESTED_OUTPUTS`.

The separate NEW-C-versus-OLD-C delivery comparison retains six
`MATERIAL_MODELED_DELIVERY_CONTRAST` decisions and two `UNRESOLVED` decisions.
**All eight secondary empirical envelopes lie entirely above their original
materiality thresholds.** SW_UP and TR_UP fraction-TDS remain contractually
unresolved because their precision allowances exceed the original ceiling;
the modeled delivery contrast nevertheless remains above 0.10 pp throughout
each retained empirical numerical sensitivity envelope. Neither becomes a newly
certified material contrast, historical PASS or complete continuum bound.

This is a target-exposed retrospective, exploratory analysis of already-known
results, including the two unresolved cases. It supplies a more informative
numerical interpretation, not new physical validation, E2 transfer capability
or production eligibility. No native computation or original scoring was run.

## Original result and added interpretation

| Question | Original = reproduced | Precision eligible / ineligible / unavailable | Envelope below / above / overlapping or touching / unavailable |
|---|---|---|---|
| Primary E2 versus C approximation, 24 | 24 PASS, 0 FAIL, 0 UNRESOLVED | 24 / 0 / 0 | 24 / 0 / 0 / 0 |
| Secondary NEW-C versus OLD-C magnitude, 8 | 6 MATERIAL_MODELED_DELIVERY_CONTRAST, 0 BELOW_DECLARED_MATERIALITY_BUDGET, 2 UNRESOLVED | 6 / 2 / 0 | 0 / 8 / 0 / 0 |

All 32 rows have complete compatible retained aggregate evidence. Missing or
extra decisions: zero. Retained M/base, component/refinement, total-allowance,
unit/budget, support and original-label discrepancies: zero. All 50 coverage
records and qualification identities are present. These checks reproduce retained
aggregate arithmetic; they do not re-verify native computations, the original
50-digit campaign, external archives or physical measurements.

`SCIENTIFIC_RESULT_DISPOSITION`: original contractual results preserved, with
separate precision compliance and empirical sensitivity relations as above.
`VALIDATION_FRAMEWORK_DISPOSITION`: the case adapter implements the frozen
mapping and preserves every row; independent pre-analysis review and synthetic
checks passed. Final independent review and candidate QA/CI are recorded in
[HANDOFF.md](HANDOFF.md), separately from scientific outcomes.
`CLAIM_CEILING`: stability only over retained empirical numerical sensitivities
and declared support, conditional on the tested source-conditioned configurations.
`PHYSICAL_VALIDATION=NOT_ESTABLISHED`.

The policy/helper are unchanged at Puckworks merge
`882584d110e1356091435ab8b002fb9abdd35ad6`, accepted tree
`7741920d87c813658941ebc26869c2af19807fad`:

- Policy SHA-256: `db16e68aa0e7fbdb37bfb455c39455928115af65c207fc43ec133424cd72a552`.
- Helper SHA-256: `d9c3d2a6e949e1f617e813dab12680dff58acdd1e4904178910739d4876e7d90`.

Its historical `v1-proposed` text is preserved. The later [owner acceptance](https://github.com/trbrewer/puckworks/pull/335#issuecomment-6192947145),
[actual merge](https://github.com/trbrewer/puckworks/pull/335#issuecomment-6192974851)
and [post-merge receipt](https://github.com/trbrewer/puckworks/pull/335#issuecomment-6193554365)
establish availability for this independently authorized case. Review §6.4/T05
motivates this use; T04's empirical families are not evaluated here.

## Complete primary matrix: 24 approximation decisions

SW = SW_WATER_ANCHORED_90C; TR = TR_LINEAR. E metrics retain fractional units,
not percent; pp means percentage points. Display precision is 12 significant
digits only; [RESULTS.json](RESULTS.json) retains round-trippable full binary64
numbers, every component/variant, source locator, support and both headrooms.
Every primary precision headroom is positive. Satisfaction headroom is b−(M+u);
failure headroom (M−u)−b is separately retained in JSON. Equality is unresolved.

| Law/history | Metric (unit) | M | u | b | Original / reproduced | Precision headroom | Empirical [L, U] | Relation | Satisfaction headroom |
|---|---|---:|---:|---:|---|---:|---|---|---:|
| SW_DOWN | D_TDS_pp (pp) | 0.000686270207401 | 7.58811718774e-05 | 0.1 | PASS / PASS | 0.0199241188281 | [0.000610389035524, 0.000762151379279] | below | 0.0992378486207 |
| SW_DOWN | D_share_mean_pp (pp) | 0.121910131746 | 0.00355434521586 | 1 | PASS / PASS | 0.196445654784 | [0.11835578653, 0.125464476962] | below | 0.874535523038 |
| SW_DOWN | D_share_peak_pp (pp) | 0.193928151534 | 0.0059358091683 | 2 | PASS / PASS | 0.394064190832 | [0.187992342365, 0.199863960702] | below | 1.8001360393 |
| SW_DOWN | E_Qint (fraction) | 0.000208190344379 | 1.84848731551e-05 | 0.01 | PASS / PASS | 0.00198151512684 | [0.000189705471224, 0.000226675217534] | below | 0.00977332478247 |
| SW_DOWN | E_Qpeak (fraction) | 0.000306800315418 | 2.35459056794e-05 | 0.02 | PASS / PASS | 0.00397645409432 | [0.000283254409738, 0.000330346221097] | below | 0.0196696537789 |
| SW_DOWN | E_Spath (fraction) | 6.9498076259e-06 | 2.54217703477e-06 | 0.01 | PASS / PASS | 0.00199745782297 | [4.40763059114e-06, 9.49198466067e-06] | below | 0.00999050801534 |
| SW_UP | D_TDS_pp (pp) | 0.00164161188046 | 0.000370221573704 | 0.1 | PASS / PASS | 0.0196297784263 | [0.00127139030675, 0.00201183345416] | below | 0.0979881665458 |
| SW_UP | D_share_mean_pp (pp) | 0.133421953933 | 0.00434997655046 | 1 | PASS / PASS | 0.19565002345 | [0.129071977383, 0.137771930484] | below | 0.862228069516 |
| SW_UP | D_share_peak_pp (pp) | 0.19114098471 | 0.00670122144353 | 2 | PASS / PASS | 0.393298778556 | [0.184439763267, 0.197842206154] | below | 1.80215779385 |
| SW_UP | E_Qint (fraction) | 0.000265248809768 | 8.18126151738e-06 | 0.01 | PASS / PASS | 0.00199181873848 | [0.00025706754825, 0.000273430071285] | below | 0.00972656992872 |
| SW_UP | E_Qpeak (fraction) | 0.000450828847697 | 2.56798995889e-05 | 0.02 | PASS / PASS | 0.00397432010041 | [0.000425148948108, 0.000476508747286] | below | 0.0195234912527 |
| SW_UP | E_Spath (fraction) | 3.32329328379e-05 | 5.78480263489e-06 | 0.01 | PASS / PASS | 0.00199421519737 | [2.7448130203e-05, 3.90177354727e-05] | below | 0.00996098226453 |
| TR_DOWN | D_TDS_pp (pp) | 0.00182369254714 | 0.000543532051892 | 0.1 | PASS / PASS | 0.0194564679481 | [0.00128016049525, 0.00236722459903] | below | 0.097632775401 |
| TR_DOWN | D_share_mean_pp (pp) | 0.127493429245 | 0.00458628936655 | 1 | PASS / PASS | 0.195413710633 | [0.122907139878, 0.132079718611] | below | 0.867920281389 |
| TR_DOWN | D_share_peak_pp (pp) | 0.194610072548 | 0.00747552145627 | 2 | PASS / PASS | 0.392524478544 | [0.187134551092, 0.202085594004] | below | 1.797914406 |
| TR_DOWN | E_Qint (fraction) | 0.000122359856429 | 1.02005383026e-05 | 0.01 | PASS / PASS | 0.0019897994617 | [0.000112159318126, 0.000132560394731] | below | 0.00986743960527 |
| TR_DOWN | E_Qpeak (fraction) | 0.000247977537285 | 2.37820513382e-05 | 0.02 | PASS / PASS | 0.00397621794866 | [0.000224195485947, 0.000271759588623] | below | 0.0197282404114 |
| TR_DOWN | E_Spath (fraction) | 4.81544715874e-05 | 9.04655166933e-06 | 0.01 | PASS / PASS | 0.00199095344833 | [3.9107919918e-05, 5.72010232567e-05] | below | 0.00994279897674 |
| TR_UP | D_TDS_pp (pp) | 0.000346654671004 | 0.000351106878938 | 0.1 | PASS / PASS | 0.0196488931211 | [-4.452207934e-06, 0.000697761549942] | below | 0.0993022384501 |
| TR_UP | D_share_mean_pp (pp) | 0.11494771845 | 0.00516685365774 | 1 | PASS / PASS | 0.194833146342 | [0.109780864792, 0.120114572108] | below | 0.879885427892 |
| TR_UP | D_share_peak_pp (pp) | 0.205342009354 | 0.00771665575333 | 2 | PASS / PASS | 0.392283344247 | [0.197625353601, 0.213058665107] | below | 1.78694133489 |
| TR_UP | E_Qint (fraction) | 0.000258834204788 | 1.37818063482e-05 | 0.01 | PASS / PASS | 0.00198621819365 | [0.00024505239844, 0.000272616011136] | below | 0.00972738398886 |
| TR_UP | E_Qpeak (fraction) | 0.000564901274584 | 2.63569527523e-05 | 0.02 | PASS / PASS | 0.00397364304725 | [0.000538544321832, 0.000591258227336] | below | 0.0194087417727 |
| TR_UP | E_Spath (fraction) | 7.13278569991e-06 | 1.7662891895e-06 | 0.01 | PASS / PASS | 0.00199823371081 | [5.36649651041e-06, 8.89907488941e-06] | below | 0.00999110092511 |

These six metrics answer different output questions: integrated/peak relative
flow error; mean/peak CORE outlet-share error; cumulative solute path error;
and maximum five-fraction TDS difference. CORE always means inner outlet
flow divided by total flow. Hydraulics/allocation use all native intervals from
0 to 30 s. Delivery is mass-matched on the frozen finite support below.

## Complete secondary matrix: eight delivery-magnitude decisions

MATERIAL abbreviates `MATERIAL_MODELED_DELIVERY_CONTRAST` in this table only.
Original and reproduced labels are identical. These magnitudes compare NEW
annulus-fast C with OLD core-fast C; OLD-C supplies path normalization.
They are modeled contrasts, not approximation errors against measured truth.
Above-budget headroom is (M−u)−b; below-budget headroom b−(M+u) is also in JSON.

| Law/history | Metric (unit) | M | u | b | Original / reproduced | Precision headroom | Empirical [L, U] | Relation | Above-budget headroom |
|---|---|---:|---:|---:|---|---:|---|---|---:|
| SW_DOWN | D_TDS_pp (pp) | 2.99618699365 | 0.00848987128492 | 0.1 | MATERIAL / MATERIAL | 0.0115101287151 | [2.98769712237, 3.00467686494] | above | 2.88769712237 |
| SW_DOWN | E_Spath (fraction) | 0.134545914603 | 0.000257990152801 | 0.01 | MATERIAL / MATERIAL | 0.0017420098472 | [0.134287924451, 0.134803904756] | above | 0.124287924451 |
| SW_UP | D_TDS_pp (pp) | 4.72916388201 | 0.0200386346942 | 0.1 | UNRESOLVED / UNRESOLVED | -3.86346942025e-05 | [4.70912524731, 4.7492025167] | above | 4.60912524731 |
| SW_UP | E_Spath (fraction) | 0.173742158046 | 0.000598928759503 | 0.01 | MATERIAL / MATERIAL | 0.0014010712405 | [0.173143229287, 0.174341086806] | above | 0.163143229287 |
| TR_DOWN | D_TDS_pp (pp) | 3.60511722697 | 0.0122007867156 | 0.1 | MATERIAL / MATERIAL | 0.00779921328441 | [3.59291644025, 3.61731801368] | above | 3.49291644025 |
| TR_DOWN | E_Spath (fraction) | 0.161867626272 | 0.000306891456822 | 0.01 | MATERIAL / MATERIAL | 0.00169310854318 | [0.161560734815, 0.162174517729] | above | 0.151560734815 |
| TR_UP | D_TDS_pp (pp) | 4.16755844865 | 0.0246374865861 | 0.1 | UNRESOLVED / UNRESOLVED | -0.00463748658613 | [4.14292096206, 4.19219593523] | above | 4.04292096206 |
| TR_UP | E_Spath (fraction) | 0.169933299183 | 0.000480814047258 | 0.01 | MATERIAL / MATERIAL | 0.00151918595274 | [0.169452485136, 0.17041411323] | above | 0.159452485136 |

Only six secondary outcomes are contractually qualified material contrasts.
The two negative precision headrooms remain explicit. No universal contractual
materiality statement follows from the eight informative sensitivity relations.
These secondary results neither change the primary aggregate nor grant extra
E2 transfer capability or accuracy in relative predictions of the contrast.

## SW_UP and TR_UP fraction-TDS: unresolved precision, informative envelopes

**SW_UP / D_TDS_pp**: M = `4.72916388200526` pp; u = `0.02003863469420253` pp.
The retained envelope is **[4.709125247311057, 4.749202516699462] pp**, entirely
above b = 0.10 pp. Precision headroom is `-3.863469420252452e-05` pp;
above-budget headroom is `4.6091252473110575` pp.
Original = reproduced decision: **UNRESOLVED**.

**TR_UP / D_TDS_pp**: M = `4.167558448648455` pp; u = `0.02463748658612719` pp.
The retained envelope is **[4.142920962062328, 4.192195935234582] pp**, entirely
above b = 0.10 pp. Precision headroom is `-0.004637486586127185` pp;
above-budget headroom is `4.042920962062328` pp.
Original = reproduced decision: **UNRESOLVED**.

The declared precision ceiling is 20% of 0.10 pp, conventionally written
0.020000 pp. The actual historical binary64 multiplication yields
`0.020000000000000004`; that exact operation was retained, with no padding or
new floating-point tolerance. Both allowances exceed it.

| Original allowance term (pp) | SW_UP | TR_UP |
|---|---:|---:|
| time | 0.004208605290028089 | 0.010539517412587074 |
| axial | 0.007076669089753906 | 0.009737841376759704 |
| both_C_radial | 0.008748474010937812 | 0.004360127796774194 |
| property | 4.886303473838893e-06 | 0.0 |
| arithmetic | 8.881784197001252e-15 | 6.217248937900877e-15 |

For **each** row, both statements hold:

1. The original contractual decision remains UNRESOLVED because numerical
   precision eligibility was not met.
2. The modeled delivery contrast remains above the declared materiality threshold
   throughout the retained empirical numerical sensitivity envelope.

The allowance is an additive sensitivity diagnostic: paired temporal, paired
axial, BOTH-C radial, paired SW property (zero for TR), and maximum retained
independent arithmetic discrepancy. Primary radial refinement instead changes
C while E2 stays at base. Neither unfavorable components nor support were removed,
and no RSS replacement was made. All 32 total allowances exactly reproduce the
historical CPython 3.12 compensated sum in original component order. The secondary
radial term was historically renamed only after summation; sorted JSON key order
was not substituted for that order.

The accepted helper is used separately with sensitivity evidence and compatible
scope. Its range relation is `satisfies` for all 32 appropriately directed
requirements, while **bound resolution remains UNRESOLVED for all 32** and its
bound-based diagnostic contract is `UNAVAILABLE`. This is expected: an empirical
sensitivity envelope does not establish an applicable bound. These outputs never
overwrite the historical adapter. The helper can classify strict-boundary equality
as mathematical violation; all historical equalities remain UNRESOLVED.

## Exact scored support and deliberately unscored tails

UP B_star = **0.015983191 kg**; DOWN B_star = **0.016114389 kg**.
The retained Decimal floor-to-1e-9-kg rule uses 0.95 times the minimum of all
18 qualified C terminals per history, nine OLD and nine NEW, both laws and every
refinement. Its aggregate reproduction and the retained support receipt agree.
The same endpoint serves both laws, all refinements, primary and secondary.

E_Spath maximizes absolute path difference over the union of native mass
breakpoints, zero and endpoint, normalized by reference S(B_star). D_TDS_pp is
the maximum absolute TDS difference across five equal-beverage-mass fractions,
using conservative splits with the first increment included. Native Q*dt supplies
carrier water. No extrapolation, support shortening or favorable terminal crop.

| History | OLD-C coverage | NEW-C coverage | NEW-E2 coverage |
|---|---:|---:|---:|
| UP | 80.088200–91.554776% | 79.628998–94.999994% | 79.649786–95.025698% |
| DOWN | 76.867823–90.603383% | 77.805401–94.999998% | 77.813863–95.018662% |

All 50 retained traces reach support. RESULTS.json keeps each terminal mass,
scored fraction, derived unscored tail and source pointer; tails range from
0.0008366708031060342 to 0.004849374917562314 kg. Success over this support does
not establish whole-shot fidelity. The support seal's historical execution order
is inherited from retained receipts, not newly re-verified against external logs.

## Historical context only: RHEOLOGY-007

The [unaltered 007 result](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_rheology_007/RESULT.md)
retains **22 PASS, one FAIL and one UNRESOLVED**. Its non-exchanging P
construction meets hydraulic and outlet-allocation budgets in all four cases,
and all cumulative-solute path metrics pass. TR/9-bar fraction-TDS genuinely
fails its 0.10 pp approximation budget (reported 0.125818 ± 0.005428 pp);
SW/9-bar fraction-TDS remains unresolved (0.101652 ± 0.006053 pp). These are
historical displayed summaries, not newly scored rows.

The valid failure survives the unresolved sibling: `PARALLEL_PATH_REDUCTION_INSUFFICIENT`
remains. P has independent non-exchanging native axial paths. It is distinct from
010's communicating E2, which has **two radial cells at every axial station**,
not two globally lumped states. Useful hydraulic, allocation and cumulative
results do not establish sufficiency for every delivery observable, internal
field or two-path construction. No 007 score, support or decision was changed.

## Historical context only: RHEOLOGY-011 and mechanism attribution

The [unaltered 011 result](https://github.com/trbrewer/espresso-whole-pull/blob/4284e9460c8057053e95de7cfa2fb3590e68e9db/docs/analysis/sci_md_rheology_011/RESULT.md)
retains **NO_MATERIAL_ARRANGEMENT_CONTRAST_FOR_TESTED_DELIVERY**. All eight tested
resolved-model, distribution-preserving arrangement contrasts remain below
their declared budgets after their empirical allowances. The full conditional
E2 execution was not triggered (`E2_NOT_EXECUTED_CONDITIONAL_GATE`), neither an
E2 pass nor an E2 failure. No new E2 execution is authorized or performed.

010's conductance-matched reversal changes the area-weighted permeability
distribution and associated residence-time behavior as well as radial position.
It does not uniquely isolate lateral position or lateral coupling. 011 separately
relocates an unchanged high/low-permeability distribution and supplies a bounded
null result. The modeled 010 delivery contrasts and 011 arrangement null coexist;
neither erases the other or establishes a universal histogram-only surrogate.

## Unsupported claims and uncertainty still unknown

C remains a source-conditioned computational reference. No physical measurements
are newly compared, no experimental truth or production readiness is established.
The TR industrial-extract transfer and dilute continuation, and SW water anchoring
and 90 C extrapolation, remain assumptions. Relevant property dataset identities
are `g10_liquor_rheology/telisromero2001_tables` and `sobolik2002/rheology`.
This task inspected their guide metadata and historical source-use receipts,
not the restricted underlying tables. It directly inspected public retained
aggregate JSON evidence. No claim of external-data absence or exhaustion is made.

Measurement, training, source-model, parameter and untested discretization/continuum
uncertainty remain unrepresented. The numerical allowance covers specified tested
sensitivities only; it is not total uncertainty, a rigorous continuum limit,
confidence coverage, population reliability or all-discretization convergence.
Engineering budgets are not experimentally established taste limits or validated
consumer tolerances. No unique mechanism, arbitrary geometry/history transfer,
whole-shot equivalence, measured speedup or stronger E2 capability follows.
No result is unresolved through envelope overlap or missing retained aggregate
support in this 32-row population; two remain unresolved through failed precision,
and bound/physical claims remain unsupported for every row.

## Reproduction and review evidence

The [frozen protocol](PROTOCOL.md), [input manifest](INPUT_MANIFEST.json) and
[independent pre-analysis review](PRE_ANALYSIS_REVIEW.md) precede evaluation.
The manifest binds EWP `4284e9460c8057053e95de7cfa2fb3590e68e9db`, 25 retained
source/contract/context files and five policy sources with SHA-256 hashes;
840 JSON pointers identify the declared 32-row crosswalk. No plots, external
traces, native fields or restricted property tables supplied missing values.
Synthetic fixtures were authored independently, before the evaluation, and
63 focused tests initially passed. Final test/review/CI evidence and exact commands
are in [HANDOFF.md](HANDOFF.md). A metadata-only addition of the required three
dispositions left every case and count unchanged; deterministic reevaluation is
reproduction of aggregates, not a new scientific campaign.

EWP and historical source files remain unchanged. The case does not modify the
policy/helper, public vocabulary, existing scorers, acceptance thresholds,
dependencies or default behavior. Draft PR only; auto-merge disabled.

`PHYSICAL_VALIDATION=NOT_ESTABLISHED`; `MERGE_AUTHORIZED=false`;
`PRODUCTION_ADOPTION_AUTHORIZED=false`; `NEW_NATIVE_SIMULATIONS=0`;
`NATIVE_EWP_RUNS=0`; `NO_AUTOMATIC_SUCCESSOR`.
