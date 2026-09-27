# SCI-MD-MASS-DELIVERY-007 result

**FROZEN_CONDITIONAL_TRANSFER_INADEQUATE_ON_DECLARED_COHORT.** Fixed primary C2. One independent exact-freeze approval followed by one outcome join; zero fits, optimizer calls or native runs.

G1 / NO_GOVERNING_PHYSICS_CHANGE. [Producer draft PR #292](https://github.com/trbrewer/puckworks/pull/292), [consumer draft PR #198](https://github.com/trbrewer/espresso-whole-pull/pull/198), linked issues [#291](https://github.com/trbrewer/puckworks/issues/291) / [#197](https://github.com/trbrewer/espresso-whole-pull/issues/197). Both drafts remain unmerged.

| Coverage and conditioning | Retained result |
|---|---|
| Source blocks / qualified physical shots / primary eligible shots | 14 / 13 / 11 |
| Original conditioning assays / pooled summaries | 98 / 22 |
| Declared suffix windows / supported per arm | 55 / 55 / 55 / 55 |
| Positive / zero-width suffix vials | 55 / 0 |
| Prefix / suffix beverage mass | 141.94 / 178.88 g |
| Coverage / numerical integration | PASS / PASS |
| Maximum per-interval solute allowance | 1.30476294029e-16 kg; ceiling 1e-9 kg |

| Arm | Equal-shot mean R (TDS pp) | Mean abs(B) (pp) | Signed mean B (pp) | Individually adequate | A |
|---|---:|---:|---:|---:|---|
| C0 | 0.965470231 | 0.831110292 | 0.830450502 | 3/11 (need 9) | FAIL |
| C1 | 1.001235186 | 0.969673066 | 0.969673066 | 2/11 (need 9) | FAIL |
| C2 | 0.599148861 | 0.532634505 | 0.509950024 | 7/11 (need 9) | FAIL |

| Increment | R gain (pp) | Relative gain | Definite paired wins | abs(B) deterioration (pp) | Status |
|---|---:|---:|---:|---:|---|
| I0: C2 vs C0 | 0.366321371 | 37.942275% | 11/11 (need 9) | -0.298475787 | PASS |
| I1: C2 vs C1 | 0.402086326 | 40.159029% | 11/11 (need 9) | -0.437038561 | PASS |

Adequacy requires mean R ≤1.00 pp, mean abs(B) ≤0.50 pp and at least ceil(0.75N) shots satisfying both individually. Each increment requires ≥0.10 pp and ≥15% mean-R gain, ceil(0.75N) definite paired wins and ≤0.10 pp absolute-bias deterioration. All decisions use conservative numerical bounds; [RESULTS.json](RESULTS.json) retains the bounds and each component status. These are new-task working budgets, not measurement uncertainty, confidence intervals or universal coffee-quality standards.

C2 adequacy is **FAIL**; I0/I1 are **PASS / PASS**. No best-performing arm replaces the primary candidate after scoring. C2 earns the second-summary increment against both frozen simpler arms on this cohort, but does not achieve the declared portability adequacy: mean abs(B)=0.532634505 pp exceeds 0.50 pp and only 7/11 shots satisfy both individual budgets (9 required). All three arms are demonstrably inadequate.

| Arm | Mean shot vial-solute RMSE (g) | Mean shot vial-solute MAE (g) | Mean signed suffix error (g) | Mean absolute suffix error (g) | Mean max cumulative suffix error (g) |
|---|---:|---:|---:|---:|---:|
| C0 | 0.029005950 | 0.026679257 | 0.110042448 | 0.110169127 | 0.114329375 |
| C1 | 0.031045641 | 0.030063771 | 0.141875934 | 0.141875934 | 0.141875934 |
| C2 | 0.018961726 | 0.017384866 | 0.071663482 | 0.076018902 | 0.076506114 |

These are secondary delivery diagnostics over exactly the declared suffix. Complete per-shot metrics, cumulative residuals and row predictions remain private. Across-shot summaries give equal weight to shots; biases are made absolute within each shot before averaging.

| Arm | Extrapolated shots | Suffix windows | Features (shot counts) |
|---|---:|---:|---|
| C0 | 1/11 | 4/55 | m2_kg: 1 |
| C1 | 2/11 | 9/55 | m2_kg: 1, q1: 1 |
| C2 | 2/11 | 9/55 | m2_kg: 1, q1: 1 |

Saved GRUDEVA-CLOCK-001 excluded-shot MASS diagnostic on exactly the same 55 suffix vials: equal-shot R=0.420832103 pp, mean abs(B)=0.314583044 pp, signed mean B=0.087754084 pp. **Source-trained diagnostic with different information privileges; not a fair ablation or selection arm.** Source, retained manifest, all selected fold hashes, exclusions and measured geometry verified. No historical scorer or fit-predict routine was invoked; no saved row regenerated. Historical all-vial scores are not compared here.

Source interpretation and limits: accepted SOURCE.json bytes bind exp13.csv and upstream commit. Raw CSV and qualified notebook/thesis interpretation inspected locally; notebook not executed. All 252 original positions remain inventoried privately. Blocks 1–13 and vials 1–16 qualify; the unexplained fourteenth block and terminal vials are preserved and excluded. Positive-mass unavailable chemistry at block 6/vial 3 and block 13/vial 2 invalidates their selected pools without moving boundaries. Their known masses still advance the source coordinate. The independently derived 11-shot/55-vial counts match the planning check.

Pool boundaries used only recorded Weight masses and the exact C2 stored mass means. Each pool is mass-weighted and mass/solute conserving; zero-liquid positions remain explicit. No spout doubling, collection-origin shift, final-yield normalization, imputation or alternative pooling arm. The 22 summaries require 98 original assays: this does not demonstrate operation with exactly two physical assays or a real-time sampling policy. All suffix assays are scoring-only.

The 006 runtime, coefficients, centering, scales, domain and embedded limitations are unchanged. Canonical model identities and file byte hashes are verified separately. Task provenance supplements those historical claims. All declared windows remain in each arm; none was clipped or omitted for extrapolation or errors. Source/measurement/collection differences remain possible explanations of failure.

| Identity | Commit | Tree |
|---|---|---|
| Immutable 006 producer | 0f130d4f2dfca552e56cd7d7e96bb73b8c50f421 | 9f6b5346ea7cfceef4d014c80b235818eee0a23f |
| Evaluated 007 producer | 6190aa1c58851bcf2258d548f45e880439da8f96 | f97685c8a613a36a15b52c9881e87f9178861755 |
| Independently reviewed consumer | 2ae4e05df4c800c349cb538786e3752a60fcd0b0 | e1d9762496f7a6ec3951bff1b2f24fa09fd76bc0 |
| puckworks base | 6edc5b827999bd9896f8d8762406a79c97c893ab | 30a63287c8672c4d1ae53b96698c59bd16baeada |
| espresso-whole-pull base | 022107a2d9e4d10effe970f5d5989abc188fae3f | de805937e9429e954755ba08733f3160b9e713a0 |

The [independent pre-scoring receipt](PRE_SCORE_REVIEW.json) binds the [exact freeze](FREEZE.json). [Prediction manifest](PREDICTION_MANIFEST.json), [consumer equivalence](CONSUMER_EQUIVALENCE.json), [exclusive score start](SCORE_RECEIPT.json), [completion](SCORE_COMPLETION.json) and [result binding](RESULT_BINDING.json) retain the evidence chain. Reports read saved results only. Publication heads, ordinary final review, live base applicability and hosted checks are separate closeout identities; a pre-score approval or head-only PASS is not merge readiness.

All outcomes are retrospective, target-exposed and conditional on collected beverage mass under this source contract. Prior Grudeva work informed the mass-coordinate direction. This is not a fresh blind holdout, independent prospective validation, real-time control, species or hydraulic prediction, whole-cup/inventory closure, or physical mechanism validation. A failed frozen transfer does not reject every mass-coordinate model or future transfer method. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

Pannusch/Schmieder, Mendeley 10.17632/y2tz67f6ry.1: source-derived model/result CC-BY-NC-3.0 treatment is separate from first-party software. Dr. Yoana Grudeva source permission remains PERMISSION_DOCUMENTED without a new SPDX licence. Originals, notebooks/PDFs, source locators and row-level evidence remain in private external storage.

MERGE_AUTHORIZED=false; PRODUCTION_ADOPTION_AUTHORIZED=false; PRODUCTION_DEPENDENCY_LOCK_CHANGED=false; NATIVE_EWP_RUNS=0; NO_SUCCESSOR_AUTHORIZED.
