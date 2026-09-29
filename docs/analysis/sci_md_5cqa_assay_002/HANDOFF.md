# Research handoff

**TESTED_EARLY_ASSAY_FAMILIES_INADEQUATE.** All three arms fail both R and mean
absolute-bias budgets in every primary condition on complete qualified support.
No adequate minimum tested early-assay contract, material single-assay placement
value, or earned two-assay complexity is established. This qualified negative
result completes SCI-MD-5CQA-ASSAY-002; no successor is selected.

Balanced primary R for L1M/L2M/L12 is 0.343708141 / 0.349467750 /
0.297495166 mg/g. L2M worsens R versus L1M. L12 improves R in all four conditions
versus either single-assay arm, but its gain over L1M is only 0.046212975 mg/g
(13.4454%) and its absolute-bias deterioration is 0.038684972 mg/g. Against L2M,
its 0.051972584 mg/g absolute gain passes that margin, but 14.8719% misses the
15% relative margin. L12 remains inadequate; neither comparison earns two assays.
See [complete result and matrix](RESULTS.md) and [retained score](RESULTS.json).

| Binding | Identity |
| --- | --- |
| Reviewed implementation base | `e6567a392e6d0c340cad71cbe744100b515e0e31` |
| Pre-fit contract commit | `c0d294670923ab4d8805e0837002cd304470f974` |
| Evaluated producer | `fbac5634d0c90bf36ac557297ddacf4d7142f916` |
| Evaluated tree | `beae94a6430de645695e4db8fbf5f7b92731feb8` |
| Approved freeze SHA-256 | `90b1156e06f8c5a51b8027846a01b630302733bed6941ad20e45c49eeefab73e` |
| Independent receipt SHA-256 | `cdc0ca9e0014530b218b51326841c83c461c2c19a5e28921c0ad9063f4a2847b` |
| Retained results SHA-256 | `8e5383f61e32d67a422737f025b52a8ecf0b61f00b267e7ce946385a12c32b39` |
| L1M semantic model SHA-256 | `cf828806d7f4695fc88e8d847666d467367918c5f4ab7ca3309cc1a7d19269ec` |
| L2M semantic model SHA-256 | `e2344204abcb6d154360834d65ea132e5fefadfcf92c1181191523f22305370f` |
| L12 semantic model SHA-256 | `c735e3a2cf95f29c53b8b5b24b00e4f2eaf0d5f50ead47aa405bce885c663d95` |

The actual nonhuman independent reviewer approved this exact freeze before the
single outcome join and score. This is not human or hosted PR approval. Their
[report](INDEPENDENT_REVIEW.md) and [receipt](INDEPENDENT_APPROVAL.json) are copied
byte-for-byte. Review independently verified every start objective, fitted-model
transform, held-fold score and supported prediction integral without fitting or
accessing later PRED chemistry. The sole advisory concerns display priority when
source support and numerical qualification both fail; this hypothetical branch
is unreachable on the complete qualified primary freeze and changes no decision.
It is preserved without a post-score code correction.

All 549 authorized starts completed with no failure or boundary hit. Three
independent lambda selections chose 0.0001. [Development](DEVELOPMENT.json),
[execution](EXECUTION.json) and [qualification](QUALIFICATION.md) retain their
scope and accounting. EXECUTION_PRE_SCORE.json and SOURCE_COUNTS.json are the
unchanged pre-score snapshots; SCORE_COMPLETION.json binds exactly one completed
score. Verify replayed all 288 prediction/status records and states exactly with
zero optimizer calls, new outcome joins or score calls. Report read retained scores.

Source qualification retains 42 eligible FIT shots from the original 45,
15 designs, 168 intended/165 supported fitting slots and 164 held-fold slots.
All 24 original PRED shots remain. Each arm retains 48/48 primary, 24/24 temperature
and 23/24 flow support. C07 remains incomplete; its L2M/L12 absolute-bias lower
bounds establish failure with original denominators, while L1M remains incomplete
there. C08 mass-feature extrapolation and all chemical extrapolation flags remain.
Historical E0/D0/A1/L1 models, predictions, scores and conclusions are unchanged;
no historical fitter, prediction generator or scorer was invoked. New L1M is the
matched-cohort control and does not replace #299's L1 conclusion.

The new strict research API, saved models and [source-free synthetic example](synthetic_saved_model_example.py)
cover all three information contracts. [Reproduction](REPRODUCE.md) documents the
six actual stages and registered private locators. Prepare/develop/freeze/score
have executed once; only verify/report may repeat. Model loading and supplied
interval inference require no originals, private evidence, network or optimizer.
Original data, observations, individual predictions, shot results and logs remain
outside Git. Source-derived artifacts retain Pannusch/Schmieder CC-BY-NC-3.0,
Mendeley DOI 10.17632/y2tz67f6ry.1, separately from software licensing.

Local full-suite QA at the scientific producer passed 5,108 tests, with 65 existing
skips, 60 deselections and one existing development-salt warning. Focused new and
predecessor tests passed 154. Additional normal/historical/registry/static/type,
generated-state, claim/evidence, source/privacy and packaging outcomes are recorded
in [QA.json](QA.json) with exact commands and log hashes. The existing optional-Taichi
acknowledged exception is separate from registry passes. Publication adds reports,
retained model/aggregate evidence and the three ordinary planning records only;
all scientific code, contracts, source bindings, tests and frozen artifacts remain
exact. Final publication review binds that concrete candidate separately.

Hosted CI is separate from local QA and scientific adequacy. The draft PR's live
checks supply its actual hosted status; pending is not PASS. No merge or auto-merge
is authorized. EWP remains unchanged and read-only; NATIVE_EWP_RUNS=0.
SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION.
PHYSICAL_VALIDATION=NOT_ESTABLISHED; ANALYTICAL_UNCERTAINTY=NOT_ESTABLISHED;
PRODUCTION_ADOPTION_AUTHORIZED=false; MERGE_AUTHORIZED=false;
NO_SUCCESSOR_AUTHORIZED. No production, default, dependency-lock, registration,
release, laboratory, acquisition or external-contact action follows.
