# Espresso development guide

**ESPRESSO-DEVELOPMENT-GUIDE-001 · reviewed 2026-10-06 · G0 · NO_GOVERNING_PHYSICS_CHANGE.**
This is the cross-repository development guide; cards, result bundles and existing
planning authorities retain their responsibilities. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

## At a glance

**What has been developed?** PW provides runnable components, source adapters,
verification tools, a Cameron-based Guided Pull, standalone wetting/extraction
models, empirical fraction-delivery predictors and new prescribed-flow/temperature
research APIs. EWP implements sharp-front wetting, porous flow, optional machine
coupling, stress-dependent permeability, conservative extraction/transport and cup
accounting. Recent state continuation, envelopes and conditioning are substantive
engineering advances even when no governing physics changed.

**What can they do, and how mature are they?** Guided Pull explores a bounded
saturated single-solute configuration; it does not predict wetting, taste or arbitrary
coffee recipes. Several research APIs have strong analytical and declared-case
numerical evidence. Pannusch stateful-004 still fails its temporal-decrease criterion.
Grudeva's standalone reduced implementation has bounded numerical verification but
does not reproduce the selected publication figures; its conservative comparator
still lacks spatial qualification. EWP's frozen R0 is a numerically qualified
calibration baseline. Implementation, merge, numerical accuracy, empirical adequacy
and deployment are separate achievements.

**How do they compare with experiments?** The programme uses multiple sources,
including Cameron, Pannusch/Schmieder, Grudeva and Waszkiewicz. Their observations,
information privileges and exposure differ. The audited Cameron configuration has
large figure residuals. MASS-007 improves over both simple controls but fails its
absolute transfer contract; later adaptation and stopping results answer different
questions. EWP's corrected WP03 runs converge with reversed pressure ranking.
Neither corpus size nor passing tests establish physical validity.

**Leading next decision:** correct Guided Pull's pressure/evidence/observable
disclosure using the source-to-report trace below, preserving numerical behavior.
The code calls its input overpressure, the SI specifies 5 bar, and the main paper
labels the reference recipe 6 bar static pressure. Resolve or explicitly expose
that source ambiguity; do not guess a one-bar conversion. This is actionable
reader-facing work without a new scientific campaign.

The [frontier](#near-term-frontier) is a proposal, not execution authority. Only
this guide, its EWP pointer, navigation and checks are authorized here. No fits,
new scores, solver campaigns, parameter changes, acquisitions, experiments,
contact, dependency refresh, merge or successor are authorized. Existing negative
decisions stand until a substantive new premise changes their question.

## Objectives, baseline and review method

The owner's four objectives are to understand **what was developed**, **what it
actually predicts and its maturity**, **agreement with eligible observations**, and
**justified next actions**. Their operational purpose is to choose the next bounded
action that changes a useful prediction or resolves a material uncertainty.

### Reviewed identities and lifecycle

GitHub commit/PR metadata was accessed on **2026-10-06**. Both main heads are
unchanged from the supplied second-review baseline; there is no intervening main
delta to relabel as newly reviewed execution.

| Role | Reviewed identity | Meaning |
|---|---|---|
| PW merged main | [`f08677b177d9569068941cbb602c7b88f3aca769`](https://github.com/trbrewer/puckworks/commit/f08677b177d9569068941cbb602c7b88f3aca769); tree `1c372d9845e4f71997d0939de12ff5cc368d1df4` | Guide's source/card/result baseline |
| EWP merged main | [`73ec476ffe6ac626705ca949e28b32935ddf2992`](https://github.com/trbrewer/espresso-whole-pull/commit/73ec476ffe6ac626705ca949e28b32935ddf2992); tree `8ced37ad5b294616b8935d92a57e3845321d5eed` | EWP source, decisions and dependency baseline |
| PW #321 open candidate | [`bd976d2d4b7fc516c005765befedf5911a89ab2e`](https://github.com/trbrewer/puckworks/commit/bd976d2d4b7fc516c005765befedf5911a89ab2e); tree `dd65c7202d12e55b5307e31c40fe773fd7c09a34` | Draft, open, unmerged. Reviewed delta from `28fe6c36873fa52965b9413dd3ab7d2b6316a773`, including correction and archive-only closeout |
| EWP production PW pin | `fc61c4670ec7bf801e40bb391aab16048b8da26b`; tree `1d553e44ee2f7480a5df521560801b478618cc84` | [Locked external dependency][ewp-lock], not moving PW main or #321 |
| EWP available-data authority | `a3428a4d4ad571ef3168a70e8a04620fca5d3520`; leverage/SCI-MD analysis authority `2058d0e947ee9eb92c52d64f6165b810f1fb4732` | [Available-data authority][ewp-data-authority] and [leverage programme][ewp-leverage] are evidence pins, not production adoption |
| Historical local Cameron/native audit | PW `713c3c229568bb189c548f4c8a490b69a6319bef`; EWP `f15a417cbf3c7528ac734537bb844cab6dc98287` | Original producer identities, corrections and exact execution bindings in [October 1 §B][october-review]; never restamped to current main |

Live metadata confirms PW [#304](https://github.com/trbrewer/puckworks/pull/304),
[#310](https://github.com/trbrewer/puckworks/pull/310),
[#317](https://github.com/trbrewer/puckworks/pull/317),
[#318](https://github.com/trbrewer/puckworks/pull/318),
[#319](https://github.com/trbrewer/puckworks/pull/319) and
[#320](https://github.com/trbrewer/puckworks/pull/320) are **merged**. Their merge
commits are respectively `15479363`, `5745f615`, `58b6cd2f`, `28c32df8`,
`4f652dee` and `f08677b1`. Old result prose saying draft/unmerged records its
publication-time state. Merge does not upgrade its scientific disposition.

The [generated active queue](../planning/STATE_OF_TRUTH.md) at the PW main pin
still lists Guided Pull, Laboratory, Grudeva-001, stateful-004 and
prefix-conditioned-006. Its pending-merge wording for 004/006 is stale against
GitHub. #321 has its own candidate planning update; that update is not merged
authority. Live substantive open items also include #67 (Grudeva), #70
(Laboratory), #48 (Guided Pull), #96 (data programme), #311 (Foster) and #313
(Pannusch temperature); open issue state alone does not mean implementation is
absent. EWP main records SCI-MD-011 as merged and SCI-MD-012 complete, superseding
the older local checkout's pending-review wording. [Project state][ewp-state]
retains the bounded SCI-ED-003 owner decision and unauthorized Stage F/D.

Before using this task ID, repository guides/cards/results and GitHub issues/PRs
were searched for `ESPRESSO-DEVELOPMENT-GUIDE`, `ESPRESSO_DEVELOPMENT_GUIDE` and
development-guide equivalents. No equivalent current cross-repository guide was
found. The dated [October 1 synthesis][october-review], [data guide][data-guide],
[CURRENT index](../CURRENT.md), existing issue families and result bundles are
reused, not replaced. New here: the four-question decision guide, public call-path
audit, current #321 qualification distinction, question-specific eligibility map
and R1–R15 dispositions. No new scientific result or new successor ID is assigned.

### Evidence actually inspected and limits

**Source inspected:** repository instructions/contribution/rights/planning records;
the call paths and headers linked below; relevant cards, manifest/register/snapshot;
primary [Cameron publisher text/SI](https://doi.org/10.1016/j.matt.2019.12.019)
and actual Fig. 5 image; [Grudeva EJAM](https://doi.org/10.1017/S095679252500018X) §5 and
actual Figures 3–5 images. Cameron combined PDF SHA-256 is
`85c8f50a3b8baa5ccdf1253b65df0dd4080776cfa573e056d2acff94d50410e5`
(Fig. 5 PDF p.13; SI S1/S2 p.23, S3/S4 p.24, S5 p.25). Grudeva article SHA-256
is `5b9e41e85591dce8a32b923663ee3ccf9e00c0ac34dc17659864ff7417326a29`
(§5 PDF p.18; Figures 3–5 pp.19–20). No redigitization or source-image redistribution.
Grudeva supplementary E.2 was inspected by REFERENCE-002's producer, **not here**;
any follow-on depending on its exact scheme must reopen the authorized primary
text, not infer it from a card. Other paper-dependent proposals below retain their
unresolved source prerequisites.

**Producer result inspected:** all numerical/empirical results below are prior
producer results unless explicitly labelled otherwise. Their linked bundles bind
execution commits, configurations, commands, selectors and limitations. This guide
did not run their commands, fit, rescore, execute source notebooks/macros/pickles,
read protected target values or launch PW/EWP scientific campaigns.

**Independently executed here:** Git/GitHub identity and lifecycle queries;
non-scoring existing inventory queries; documentation/software checks listed at
handoff. The configured corpus and private manifest were available. Six bounded
`inventory_local_corpus.py query` selections matched the existing snapshot:
Cameron 2/2, Pannusch 559/559, Grudeva2025 3/3, Waszkiewicz 13/13, Visualizer
592/592, Telis-Romero 2/2 files. Only identity/structure was returned; private
locators were suppressed. These are neither observation counts nor a new corpus
census. Snapshot identity remains
`f46181ee8c461fab055b73511148dd26888c7c5b3cb1bc908aad6ab9db2bb766`.
Underlying measurements were not reopened for comparison. Other families below
are **catalog/producer-record only** in this session.

**Analytical deduction:** the fixed-parameter static monotonicity calculation
below was checked against the implementation; it already appears in earlier
programme decisions. **Unresolved inference:** source pressure-node equivalence,
physical applicability of synthetic state sets, several experimental input joins
and new-task tolerances remain unresolved.

<a id="review-input-limit"></a>
**October 5 review limitation.** The original attachment is identified by the
owner as SHA-256
`593b8eb2d095b107fe999cdc70dd641a45a54aed7a022f3af565e3d217c325bf`.
Neither that attachment nor a separately identifiable second-review document was
available in the bounded review-input search. Consequently this guide audits the
owner-supplied correction summary and R1–R15 mapping, not an invented full-text
review. Those stable recommendation IDs are used below; original section/page
numbers, verbatim wording and second-review identity remain **UNRESOLVED**.
The supplied review's reported executions are not ours. Add the exact original
section crosswalk when the documents become available; preserve both opinions as
historical documents. This limitation does not prevent source-supported corrections.

## How to judge a capability or a proposed task

Keep seven questions separate: is it implemented; is its code verified; are its
numerics qualified for this configuration; is its error adequate for the named
observations; does it transfer; does it improve a useful decision; and is it
available through the intended product/deployment? A registered PW component is
not automatically called by Guided Pull, and PW main is not EWP's dependency pin.

Use the existing evidence distinctions: analytical verification; source-model
reconstruction; numerical-reference figure comparison; fitted measurement
comparison; within-campaign held-out testing; exposed cross-source transfer; and
untouched prospective confirmation. Dataset ownership does not establish
independence. Pannusch/Schmieder's shared lineage must not be doubled, but grouped
held-out subsets can still answer narrower predictive questions.

Match the observation operator before interpreting agreement:

| Quantity | Required match |
|---|---|
| Pressure and flow | Absolute/gauge/differential reference **and** sensor node; pump/line/basket/puck-face; Darcy velocity versus pore velocity, volumetric flow and mass flow; prescribed forcing versus predicted response |
| Inventory and geometry | Actual dry dose; bulk/grain/liquid reference volumes; hydraulic/storage/intraparticle porosity; source material and preparation |
| Clock and collection | Pump start, wetting, first drip, scale and vial clocks; actual finite collection windows; prescribed inlet volume versus measured cup mass |
| Chemistry | Instantaneous outlet concentration versus mass/volume-weighted fraction concentration; cup solute versus solid loss including retained liquid; analyte and dilution/recovery basis |
| Endpoints | Fixed time versus fixed beverage event: R0 at 30 s is not its 40 g event; EY and TDS share mass accounting and are not independent confirmations |

Measurement uncertainty, raster-reading allowance, numerical error, inter-source
spread and a task's decision tolerance are different quantities. Do not turn
source spread into a probabilistic interval or call an engineering budget assay
precision. Compare equally informed controls on common eligible support, group
by actual shots/conditions/campaigns, preserve missingness and adverse cases, and
freeze calibration/testing roles before scoring. Improving over a baseline can
coexist with failed absolute adequacy.

The existing [minimum-necessary governance standard](../governance/MINIMUM_NECESSARY_GOVERNANCE_STANDARD.md)
and [EWP three-test gate][ewp-data-first] control proposals: new information,
different consequences for plausible outcomes, and useful grinder-to-cup relevance.
Two failed tests preclude starting without a named owner exception. Repeated
missing-input blockers require addressing that information boundary, not another
renamed score or surrogate. The [frontier](#near-term-frontier) applies these tests
without authorizing work. Analytical components need analytical/numerical oracles;
not every engineering task needs a new measurement.

## Capability and evidence matrix

Quantitative results below are **producer result inspected**; source-only gate
criteria are explicitly labelled. Entry points are source-inspected, not executed
for this guide. Full component coverage remains in
the [registry](../../puckworks/models/__init__.py) and [cards](../cards/); these rows
select decision-relevant capabilities rather than reproduce the registry.

| Capability / executable entry point | Prescribed or measured inputs | Predicted observables | Implementation / numerical status | Evidence type / exposure | Best relevant quantitative result and configuration | Applicability limits / availability | Next blocker |
|---|---|---|---|---|---|---|---|
| **Guided Pull**: public `puckworks.product.simulate_pull`, report serializers/rendering; [implementation](../../puckworks/product/_pull.py) | Dose, target beverage, EK43 dial, constant overpressure, named model profile; temperature recorded only | Constant model flow, duration, liquid/grain concentrations, cup solute, EY/TDS; target beverage is imposed | Merged orchestration; Cameron verification inherited | Exploratory/source-linked simulation; no independent cup validation | Reference audit below is **20 g/40 g/5 bar**, not the product's **9-bar** presets | Only Cameron executes as primary; coverage/lenses do not imply other components ran; no wetting, dynamic pressure or flavor | Pressure/evidence labels and source-reproduction disclosure |
| **Cameron standalone**: [`extraction_bdf.simulate_shot`](../../puckworks/models/cameron2020/extraction_bdf.py); [card](../cards/cameron2020.md) | Source phase fractions/radii, flux-versus-dial table, dose, pressure, grain inventory; optional explicit flux/time | Saturated two-population diffusion/dissolution, outlet and cup extraction | F13 inventory repair merged; conservation and bounded grid qualification; source reproduction unresolved | Code verification; publisher homogeneous curve and published experimental means (source-exposed) | N40/M24, GS 1.1–2.3, 20 g/40 g, 5-bar overpressure, `c_s0=118`: **7.102391 / 6.480780 EY pp RMSE**, respectively [audit][cameron-audit] and [§C][october-review] | Source-specific EK43/material; numerical default error is not experimental accuracy | Source configuration/normalization, without retuning inventory |
| **Pannusch legacy multispecies**: [`solver.simulate_fractions`, `simulate_fractions_qt`](../../puckworks/models/pannusch2024/solver.py); [card](../cards/pannusch2024.md) | Flow, temperature, geometry/grind, species parameters and initial concentrations, fraction bounds | Finite fraction concentrations for caffeine/trigonelline/5-CQA/TDS | Merged source reconstruction; legacy and newer FV paths separate | Post-fit/source-internal; shared Pannusch/Schmieder campaign; exposed transfer work | Current Paper A: matched **40 g**, optimal-grind calibration→coarse/fine holdout; **8.44% vs 8.83% pooled MAPE**, model worse on **62/132** observations (44 records) [manuscript](../PAPER_A_DRAFT.md) | Endpoint inventory/rate weakly separated; advantage neither established reproducible/useful nor established absent; no automatic Guided Pull/EWP use | Eligible input/observer bridge and incremental utility |
| **Pannusch Q/T FV-003**: [`simulate_flow_temperature_history_fv`](../../puckworks/models/pannusch2024/flow_temperature_history_fv.py) | Prescribed positive SI Q(t), uniform T(t), fixed source geometry/species, windows | Phase states, delivered solute, prescribed volume, finite fraction concentration | Merged; `VERIFIED_ON_DECLARED_CASES`; arbitrary runtime accuracy `NOT_ASSESSED` | Synthetic analytical/reference numerical qualification, no experimental history conditioning | 32-trajectory matrix; worst default/Radau fixed-scale error **8.20e-5**, joint target **5e-4**; N400→800 spatial allowance **.005** [003](../analysis/model_pannusch2024_flow_temp_fv_003/RESULTS.md) | Q 1–3e-6 m³/s, T 353.15–371.15 K, supported histories; no hydraulic prediction | Actual source-authorized Q/T and collection semantics |
| **Pannusch stateful-004**: [`simulate_stateful_fv`, `branch_stateful_fv`](../../puckworks/models/pannusch2024/stateful_fv.py) | Explicit liquid/fine/coarse states, immutable full plan or checked checkpoint, future forcing | Continued/branched chemistry, local/root delivery and volume accounting | Merged; **IMPLEMENTED_QUALIFICATION_INCOMPLETE** | Synthetic continuation, reference, conservation and mesh checks | Synthetic N400/GS 1.7 history, short [2.737002188183808,2.74] s fraction errors at h=.04/.02/.01: **7.99e-5 / 2.03e-4 / 8.36e-5 C***; temporal-decrease fails despite absolute **5e-4** budget [004](../analysis/model_pannusch2024_stateful_fv_004/RESULTS.md) | Admissible supplied arrays are not measured post-wetting states | Remaining temporal qualification for any accuracy-dependent use |
| **Pannusch envelope-005**: [`build_delivery_response`, `bound_delivery`, `contrast_deliveries`](../../puckworks/models/pannusch2024/state_envelope.py) | Declared initial-state set, prescribed histories/window, engineering allowances | Fixed-operator extrema, shared-state contrast and checked witnesses | Merged engineering capability; does not repair 004 | Synthetic set-valued numerical evidence | Caffeine GS 1.7 N400/h=.02, [7,17] s: A−B **[-9.534715e-8,8.574470e-7] kg**, no material difference at **1e-6 kg** [005](../analysis/model_pannusch2024_state_envelope_005/RESULTS.md) | Engineering allowance-conditional bound; no probability, continuum or physical certificate | Defensible real state set/measurement bands and useful decision |
| **Pannusch prefix-conditioned-006**: [`condition_on_fractions`, `bound_future_delivery`](../../puckworks/models/pannusch2024/prefix_conditioned.py) | Original joint state set and early solute-mass bands with explicit plan/clock provenance | Later finite-window delivery bounds, compatibility, witnesses | Merged; `ENGINEERING_CAPABILITY_VERIFIED` on declared fixed operators | Synthetic early-band conditioning; no observed assays used | N400/h=.02, early [7,10)/[10,12), target [12,17): width **1.502879e-5→8.516895e-6 kg** (43.329%); mesh lower-end shift **−7.126e-9 kg** exceeds epsilon **1e-9 kg** [006](../analysis/model_pannusch2024_prefix_conditioned_006/RESULTS.md) | Four operators qualify separately; sensitivity is outside fixed-operator bound | Empirical band/input authority and discretization budget |
| **Common-past-007 candidate**: `common_past_contrast` [candidate source][007-source] | Same original state set and common prescribed past, early bands, two future plans | Joint B−A bounds and paired replays | **Unmerged #321**; latest fixed-operator `ENGINEERING_CAPABILITY_VERIFIED` | Synthetic producer closeout; historical failure retained | N400/h=.01 unconditioned outer interval **[-3.39206446e-7,4.21982867e-7] kg**; minimum gap **2.4537163e-13 kg**; all eight current comparisons no material difference at **1e-6 kg** [closeout][007-closeout] | Historical prefix failure unresolved; transport root cause undetermined; no general execution reliability or physical claim | Owner lifecycle decision; no adjacent extension automatically justified |
| **Grudeva EJAM**: [`reduced.simulate`](../../puckworks/models/grudeva2026/reduced.py), standalone CLI/native Laboratory route; [card](../cards/grudeva2026_2.md) | Fixed Darcy flux; phase inventories, diffusivity; dimensional scales only if explicitly supplied | Wetting/desaturation fronts, outlet and phase/cup inventories | Reduced-001 numerically verified on declared support; Figures 3/4 fail; reference-002/003 incomplete | Analytical + published **numerical** reference, not experimental validation | Eq.76/77/Table-2 case: exit **6.5043092876** versus raster **6.3834586466 ± .0100251**, frozen budget **.025** [001](../analysis/model_grudeva2026_reduced_001/RESULTS.md) | No variable-flow/pressure/Foster coupling; no dimensional EY without dose/scales | Comparator bed qualification and raw-baseline observer; Figure 5 full fields/settings unavailable |
| **Grudeva permissioned port**: [`grudeva2025.reduced.make_coffee`](../../puckworks/models/grudeva2025/reduced.py); [card](../cards/grudeva2025.md) | Source first-drip time, fitted material/chemistry, empirical post-drip flow | Front progression and vial solute delivery; hydraulics partly prescribed | Merged direct port; post-fit aggregate/fraction predicates, distinct from independent EJAM-001/002/003 | Published port with documented code/data permission; no SPDX license inferred from article rights | No qualified error result audited here. Source-inspected N150/Nt800 predicate requires total within 5% and at least 8/13 vials within 1 SD; these are criteria, not a new result | No tested common-scenario inventory bridge; source flow is not predicted; not called by Guided Pull | Source/configuration reconciliation and qualified observer before any new comparison |
| **Foster wetting/machine**: [`infiltration`](../../puckworks/models/foster2025/infiltration.py), [`machine_mode`](../../puckworks/models/foster2025/machine_mode.py); [card](../cards/foster2025_2.md) | Recorded-pressure route or fitted machine/headspace/material parameters | Front, ponding, saturation, post-saturation headspace; distinct pump/bed/outlet flow | Merged post-saturation completion; bounded numerical/source reconstruction | Analytical and fitted same-campaign CT/model curves | Independent global water residual **9.195e-12** against normalized **1e-6** budget in declared completion case [result](../analysis/model_foster2025_postsat_001/RESULTS.md) | Hydraulic description useful without chemistry; source fit is not cross-rig wetting prediction | Material/input transfer and appropriate observed front/flow |
| **Waszkiewicz / structural components**: [`poroelastic`](../../puckworks/models/waszkiewicz2025/poroelastic.py), [Wadsworth card](../cards/wadsworth2026.md) | Source pressure/material fit; dissolution history or measured structural descriptors | Source-conditioned flow/permeability | Merged components; reconstruction/analytical checks, not universal laws | Same-rig post-fit hydraulics; separate structural observations | Static refit **Pc≈12.39 bar, Qc≈1.897 g/s**; tamped-law+adapter screen **7 fail/4 pass/1 unresolved** across 12 permeabilities [screen](../analysis/sci_val_tamped_k_001/RESULT.md) | No universal grinder dial, dry-to-wet mapping or Cameron hydraulic substitution | Identifiable source/material transfer |
| **Empirical delivery / stopping APIs**: [MASS-006 model/entry points](../analysis/sci_md_mass_delivery_006/README.md), [stopping API](../analysis/model_eng_mass_stop_001/README.md) | Measured early chemistry, collected mass coordinate and explicit source/exposure contract | Conditional later delivery; engineering stopping sets/envelopes | Implemented research APIs; empirical and engineering dispositions separate | Campaign-separated learning, exposed cross-source transfer, retrospective observed-boundary decisions | MASS-007 C2 **R=.599148861 TDS pp**, versus C0/C1 **.965470231/1.001235186**; absolute adequacy fails. Stop C2/C0/fixed **11/11** primary success, no earned C2 decision increment [007][mass7], [stop][stop-result] | Not real-time two-assay operation; 98 assays pooled to 22 inputs; no pressure-to-mass prediction | New discriminating decision/input premise, not replay of closed score |
| **EWP**: [`espressoWholePullFoam.C`][ewp-solver], [R0 config][ewp-r0] and optional headers | Geometry, permeability/closure, inventory/release law, pressure/machine/flow boundary; density/viscosity and numerical controls | Wetting, pressure/flow fields, transport, retained inventories and cup outputs | Merged OpenFOAM platform; R0 numerical calibration qualification; bounded extension evidence | Synthetic/reference checks and exposed source-linked comparisons | WP03 mass RMSE **4.761347/9.964731/10.491558 g** at **5/9/11 bar**, reversed ranking [WP03][ewp-wp03]; R0 30 s **40.957867483 g**, EY **23.938453103%**, distinct 40 g event EY **23.624029229%** [§D][october-review] | No general physical validation; static stress law is not displacement/mesh mechanics; current full EWP `NOT_VALIDATED`; PW pin unchanged | Matched/identifiable mechanism decision, not automatic diffusion or hydraulic replacement |

EWP also retains a positive bounded hydraulic result: the optional dissolution-indexed
permeability branch passed its governed 9-bar source reconstruction and 8-bar
no-retuning **same-campaign** flow-shape gates ([WP02-001][ewp-wp02]). That does
not establish independent transfer or override WP03's later cross-pressure failure.
Its scalar/indexed chemistry uses inventory release laws, not a resolved intragrain
diffusion model. Optional bulk/zone viscosity and pressure-history capabilities
have separate numerical comparisons; the [RHEOLOGY evidence][ewp-rheo8] does not
establish fresh-espresso material accuracy. These components must not be bundled
into one hydraulic or chemical acceptance claim.

## Question-specific data eligibility

This is the guide's scoped **non-scoring availability preflight**, using existing
[MANIFEST](../../puckworks/data/MANIFEST.csv), [capability register](../../puckworks/data/AVAILABLE_DATA_REGISTER.json),
[snapshot](../../puckworks/data/LOCAL_CORPUS_SNAPSHOT.json), [data guide][data-guide],
[EWP use map][ewp-data-map] and [active leverage ledger][ewp-ledger]. It is not a
new register or authority promotion. Source availability is separate from eligibility.
`UNKNOWN` means the inspected records do not establish the field. Missing access
in a later environment means `KNOWN_EVIDENCE_UNAVAILABLE_IN_THIS_ENVIRONMENT`.
Rights below summarize the existing source records; they grant no new permissions.

| Question / existing dataset IDs | Grouping and required inputs/operator | Availability / rights inspected here | Exposure / roles | Exact support and exclusion |
|---|---|---|---|---|
| Hydraulic pressure response: `waszkiewicz2025/traces_per_brew`, `waszkiewicz2025/traces_time_dependent`, `waszkiewicz2025/equilibrium_windows`, `waszkiewicz2025/brewer_quadratic` | **56 distinct brews/11 conditions**; 57 labels include known alias. Line pressure, source-derived basket correction, scale mass and smoothed derivative; frozen endpoint_100s or declared transient window | Packaged subsets + external identities checked; deposit data CC-BY-4.0; upstream GPL code not ingested | Source-internal/exposed; calibration and grouped tests already consumed; no untouched confirmation | Conditional grouped hydraulic predictions against equal-information B0/B1; prescribed pressure cannot also validate pressure. 110–120 s source window has an ended-shot defect. SCI-MD-010/011/012 and dynamic-resistance decisions stand |
| Wetting/headspace: `foster2025_2/fig12_14_curves`, `foster2025_2/fig15_flow`, `foster2025_2/params`; `de1_fixtureA` | Same CT campaign, fitted parameters; measured front/headspace versus model-reproduced curves; clock shift and pump/bed/outlet distinctions; independent-shot count **UNKNOWN** here | Catalog/card/producer results only; per-source rights, no blanket redistribution | Post-fit CT / numerical curve verification; not independent second campaign | Test recorded front or source reconstruction with the appropriate operator; Figure 15 model curve is not a new experimental flow trace; no direct chemistry validation |
| Structure/wetting change: `wadsworth2026/table1_full`, `vacaguerra2023a/dry_porosity_validation`, `maille2024/psd_dispersion`, `hargarten2020/swelling_progress` | Separate materials/rigs; total vs connected/dry/operating porosity, PSD dispersion method; Wadsworth 22 rows/21 nonmissing k are not 22 espresso shots | Catalog/accepted results only; Wadsworth CC-BY-4.0, Hargarten source CC BY-NC; Vaca/Maillé source-specific terms | Static descriptors, operator/prior/sensitivity evidence; not same-shot wet permeability | Separate conditioned priors; two porosity supports qualified for EWP. No universal dial map, pooled permeability distribution or synchronized structure/pressure/chemistry join [prior][ewp-prior] |
| Bulk extraction: `cameron2020/fig5_grind_deviation`, `cameron2020/psd_figure2` | Source 20-g/40-g reference, seven grind settings; actual dose and phase volumes; EY curve vs experimental means separately; raw replicate IDs **UNKNOWN** here | Primary publisher/SI and image inspected; existing derived records; no redistribution of restricted pages | Source-fitting/reconstruction target already exposed | Preserve audited configuration-specific residuals; not a new recipe score, universal pointwise error or independent flow+EY confirmation |
| Fraction/species delivery: `pannusch2024/experimental_kinetics`, `schmieder2023/raw_fractions` | Shared lineage, count shots once; 45 FIT shots/15 designs and March 24-shot PRED campaign in qualified records; actual vial masses, species assay/recovery basis, finite fraction windows and clocks | External identities checked; qualified workbook/source reconstruction reused; CC-BY-NC-3.0 source-derived treatment, originals external | FIT assignments differ by task: all 45 train MASS-006 only; PRED source-internal/target-exposed; historical roles preserved | Conditional measured-mass early-to-late tests, with grouped controls. C01 supplies 36 partial analyte/fraction observations; unresolved primed samples, inventory and clock/Q joins prevent direct EWP absolute closure. Programmed flow and scale derivative do not establish puck-face Q |
| Cross-source bulk/fraction delivery: `grudeva2025/exp13_vial_stats` with accepted external `exp13.csv` binding in [MASS-007 SOURCE](../analysis/sci_md_mass_delivery_007/SOURCE.json) | 14 blocks, **13 qualified shots**, 11 eligible for MASS-007; 98 assays→22 pools, 55 suffix vials. Historical aggregate label “14 shots” is not current shot eligibility | External identity checked; permission documented separately from article CC-BY; no new SPDX license or raw export | Distinct source from Pannusch; retrospective and target-exposed; 008 reuses shots across 110 ordered pairs | Frozen cross-source delivery and recorded-boundary stopping already evaluated. No untouched holdout, 110 independent experiments, exactly two physical assays, spout doubling or new kinetics attribution |
| Endpoint transfer: `angeloni2023/bioactives`, `angeloni2023/inventories`, `angeloni2023/total_solids` | Distinct from Pannusch; optimal-grind target calibration, coarse/fine within-campaign holdout: 44 sample records/132 named-solute observations; mass-matched cups, inventory/rate and inferred grind-to-flow map | **Catalog and public aggregate results only; protected/raw targets not inspected** | Exposed, target-specific calibration followed by within-campaign held-out prediction; no renewed untouched-holdout entitlement | Existing endpoint/baseline conclusion only; no fresh score or future calibration authorized. Shared EY/TDS and fitted inventory must not be counted as independent evidence |
| Alternative extraction sources: `moroney2015/data`, `mo2023_2/yield_strength_figs6_9`, `maille2024/normalized_curves`, `maille2024/equilibrium_concentrations`, `smrke2024/figures` | Source-specific beds/materials, deep/shallow conditions, finite-cup denominator, replicate normalization, plotted endpoint vs time series; shot joins often **UNKNOWN** | Catalog + completed producer results only; primary/SI access must be checked for a reopened question; rights per manifest | Previously examined source comparisons, some fitted; no unexposed cohort inferred | Moroney deep calibration inadequate (not an executed transfer rejection); Mo flow/cup source contract and numerics unresolved; Maillé maximum-selection denominator blocked; Smrke tested response/fines increments failed. Each reopening needs new source/observable/defect evidence |
| Operating history: `visualizer/hydraulic_timeseries`; `visualizer/user_outcomes` separate | Deduplicate logical shot/version identities; repeated contributor/cohort grouping; coffee/grind/dose, machine/sensor node, pump vs cup flow, derivation and controller feedback; missing fields **UNKNOWN** | External hashes checked; owner-attested permission, no raw redistribution; [private-work public record][ewp-visualizer] inspected, private models/targets not opened | Self-selected recent-public corpus; earlier within-contributor empirical tests and native exercises completed | Descriptive or carefully matched hydraulic use can be valuable without chemistry. Existing 6,655-shot/213-cohort evaluation is not new work. No pooled causal constitutive slope, qualified puck boundary, population representativeness or user-TDS chemistry gate |
| Rheology: `g10_liquor_rheology/telisromero2001_tables`, `sobolik2002/rheology` | Temperature, concentration basis, measured-table vs refitted/computed values; industrial extract/material grouping; independent espresso-shot count **UNKNOWN** | Telis-Romero identities checked; other source metadata/producer synthesis only; source-specific rights | Property support and computational sensitivity, not fresh-espresso calibration | F15 basis repair completed; source-domain alternatives can bound a sensitivity question. Inter-source spread does not justify symmetric probabilistic ±50%; [RHEOLOGY-008][ewp-rheo8]/[011][ewp-rheo11] are computational reductions/contrasts, not empirical validation |

## Adjudicated review findings

Original claims below are **paraphrases of the supplied review/task summary**,
identified by R numbers and correction topics; see the [document-access limitation](#review-input-limit).
They are not quotations or a silent rewrite of either reviewer's opinion.

### R1–R2: Cameron disclosure and the pressure/product contract

**Confirmed implementation/documentation mismatch:** the public exports in
[`product/__init__.py`](../../puckworks/product/__init__.py) lead to
`PullRecipe → evaluate_domain → simulate_pull → _simulate_pull_impl →
extraction_bdf.simulate_shot → pull_run_to_json / pull_run_to_markdown /
render_pull_report`. Dose and beverage convert g→kg; `pressure_bar` passes
unchanged to `darcy_flux` and `simulate_shot`. No hidden ±1-bar or bar→Pa conversion
occurs on this path. Both presets use 20 g/40 g/9 bar/93°C; temperature is
recorded-only. The solver treats pressure as overpressure and scales source flux
by `p_bar/P_REF`, where `P_REF=5.0`.

The inspected primary source supports this narrower account: main text p.638 and
Fig.5 p.642 label the recipe **6 bar static/water pressure**; SI S1 specifies
**5 bar pump overpressure**; S3 derives Darcy flux from measured shot time and
Eq.26; S5 computes alternative **3/5/7/9-bar overpressure** fluxes by scaling.
Those alternatives are model explorations, not four independently measured
pressure campaigns. The inspected material does not establish the gauge reference
and instrument node needed to turn this difference into a universal conversion.
The code's asserted 5↔6 correspondence is a source interpretation, not a measured
pressure-transfer calibration.

The product's `_PRESSURE_EVIDENCE_BAR=(6,9)` therefore lacks a traceable
same-convention empirical qualification. At 5 bar the current domain checker warns
(strict mode rejects); a value within 6–9 is in its declared interval. Neither
label resolves source reproduction. Detailed traces say prescribed pump
overpressure, while the recipe summary says only “bar” and the evidence finding
says “Pump pressure.” This warrants a **source/observable disclosure correction**,
not changing P_REF or silently subtracting one bar.

Other bounds need the same separation. GS evidence 1.1–2.3 corresponds to S3's
seven shot-time settings; hard GS 1.0–2.5 spans microstructure knots. Dose 15–25 g
and beverage 25–60 g are product intervals; the SI's dose 16/18/20/22/24-g table
is a model geometry exploration, the primary reference is 20/40 g, and general
café ranges are not validation of every combination. Hard dose 100 g,
beverage 500 g and pressure 20 bar are code admission ceilings, not demonstrated
physical applicability or a proof of numerical safety throughout. Preserve
source-supported conditions, computational admission and unqualified extrapolation
as different labels. No runtime bound/default changes occur here.

**Retained empirical inadequacy, rejected inventory “repair”:** original producer
[local audit][cameron-audit] and [October 1 §C][october-review] report
**7.102391 EY-pp RMSE** against the homogeneous publisher curve and
**6.480780 pp** against experimental means for N40/M24, GS 1.1–2.3,
20 g/40 g/5-bar overpressure, default grain concentration 118 kg/m³. The
alternate `118/0.8272` inventory gives **3.839735/3.321602 pp**, without proving
a repair. RMSE does not establish each measured point's error or a universal
pointwise deficit, and these scores do not apply to the 9-bar product preset.
The **24.467473%** operative inventory ceiling does not exclude 18–23% EY.
One-SD figure bars, ±.03-pp producer reading allowance and numerical error stay
separate. F13/F14/F15 are completed repairs; none is a new recommendation.

### R3: Grudeva's actual numerical frontier

**Original claim:** a roughly factor-2.2 discrepancy offers an untouched
normalization fix. **Revised:** superseded by completed
[REFERENCE-002](../analysis/model_grudeva2026_reference_002/RESULTS.md) and
[CONSERVATIVE-003](../analysis/model_grudeva2026_conservative_003/RESULTS.md).
002's comparator failed conservation/refinement; 003 repaired actual paired
exchange and moving-volume accounting. Its largest normalized global residual
is **6.143021e-14**. With normal controls of 512 bed cells, 3200 radial
shells and dimensionless dt=.002 through t=8, doubling bed cells changes smooth
outlet by **.00430093**
against **.001**, and cup by **.00042562** against **.00005**. Local algebra
`.00016` versus `.00008` is not a demonstrated canonical factor-two correction.
No division of published outputs or fixture change follows.

Source §5 and actual Figures 3/4 confirm numerical full/reduced comparisons,
not experimental observations. Figure 5 requires qualified full-model fields,
settings and observation grid; its error curve is insufficient. The next unresolved
decision is whether a spatially qualified independent route and neutral raw-state
baseline observer can distinguish implementation discrepancy from source settings.
It is conditional on a useful comparison need and primary-SI access, not another
re-extraction audit: 002 already reproduced the retained figure coordinates.

### R4–R5, R7 and R15: engineering, empirical value and closed questions

**Original overgeneralizations:** all extraction evidence is one campaign;
negative/no-physics work is no development; a new envelope or conditioning step
necessarily advances prediction. **Revised:** shared Pannusch/Schmieder lineage
limits that source, not Grudeva, Cameron, Waszkiewicz or every programme test.
The [capability matrix](#capability-and-evidence-matrix) credits merged Q/T,
state continuation and set-valued research tools within their exact contracts.
005/006's checked extrema do not validate real-data conditioning or cure 004.
At #321's **new** head, [archive-only closeout][007-closeout] establishes the
declared fixed-operator engineering capability; the earlier incomplete disposition
remains historical, and the failed historical prefix/transport cause remain
unresolved. No automatic adjacent extension is selected.

**Stronger current transfer authority:** the [Paper A manuscript](../PAPER_A_DRAFT.md)
and its committed aggregate bundle supersede the concise
[transfer note](../ANALYSIS_transfer.md)'s 8.2%/8.6%, 50/108 summary. At the matched
40-g endpoint, optimal-grind-calibrated predictions on all 44 coarse/fine sample
records (132 solute observations) have pooled MAPE **8.44% versus 8.83%**, with
the model worse on **62/132**. The paired difference is **−.394 pp**; the primary
clustered sensitivity range **[−.829,+.004] pp** is uncalibrated and there is no
predeclared practical margin. It establishes neither a reproducible/useful
advantage nor its absence. The primary 26 condition-within-variety clusters are
a declared dependence assumption, not proof of 26 independently sampled units.
This is within-campaign held-out prediction after target-specific calibration,
not untouched cross-campaign confirmation. No result was recomputed here.

[MASS-006][mass6] learned a useful source-internal conditional mapping;
[MASS-007][mass7] failed absolute cross-source adequacy while improving over
C0/C1 by **37.942275%/40.159029%** in mean R. R is each shot's
mass-weighted RMS TDS error, then averaged on the declared support, not pooled
independent vial replicates. Its mean absolute shot bias
**.532634505 pp** exceeds the frozen **.50 pp** budget, and **7/11** individually
adequate shots fall short of 9. [MASS-008][mass8] earns one-calibration-shot
adequacy (**9/11** calibration choices), but all three material increments fail.
[Stopping-decision-001][stop-result] achieves 11/11 primary successes at the
frozen recorded-boundary requirement of at least .100 g additional solute and
2.0 mass % suffix TDS, yet C0
matches C2's zero observed endpoint regret. Matching the simpler policy is useful
decision evidence; it does not reverse 007's error failure or prove equivalence
outside the declared decision. Historical “no successor” records consumed authority,
not a standing owner refusal to authorize future useful work.

### R6: existing EWP hydraulics, monotonicity and retirement

**Original claim:** add stress-dependent permeability to fix the pressure ranking.
**Revised:** it already exists in [poroelasticCompaction.H][ewp-poro]. For fixed
positive A, k0, Pc, mu and L, and fixed 0<Phi<1, the static implementation is

```text
Q(ΔP) = A*k0*Pc/(mu*L) * J(ΔP/Pc)
J(X) = integral from 0 to X of (1-s)^3/(1-Phi*s) ds
J'(X) = (1-X)^3/(1-Phi*X)
dQ/dΔP = A*k0/(mu*L) * (1-X)^3/(1-Phi*X) >= 0, 0 <= X <= 1.
```

The derivative is positive below 1 and zero at 1; the denominator remains positive.
This is the analytical integral evaluated by `poroelasticIntegral`'s finite-Phi
series and used by `poroelasticPuckFlow`; its derivative matches
`poroelasticPermeabilityRatio`. The code truncates the series with a relative
term criterion and iteration cap; this deduction concerns the stated static law,
not an independent floating-point qualification. At fixed parameters it can saturate
but cannot turn downward. This does **not** prove monotonicity of every transient
coupled configuration where state, geometry, forcing or coefficients change.
Stress-dependent permeability is not full displacement mechanics, and mechanical
porosity is not automatically transport storage.

[WP03-002][ewp-wp03] corrected a discrete convergence gate; the retained
[comparison JSON][ewp-wp03-json] reports mass RMSEs **4.761347, 9.964731, 10.491558 g**
at **5, 9, 11 bar**. Original alignment is `solver_time=source_time+3 s`, density
**965 kg/m³**, linear interpolation without extrapolation, source/model overlap
**0–27/3–30 s**. Source order is 5>9>11; model order 11>9>5; flow and mass Spearman
are −1. These linked producer runs have serial/MPI, time-refinement, conservation
and per-iteration qualification; they were not rerun here. The original evidence
snapshot is `9c52c94edb27b461b6e7a4d471d29f3cef9d053e`; executable identities and
exact telemetry corrections remain in the report. This rejects the tested
cross-pressure reconstruction, not every configuration or all poroelastic physics.

[SCI-MD-010][ewp-md10] already compared reduced Darcy with equally trained
baselines across 56 brews/11 held-pressure folds; no stable advantage was earned.
[SCI-MD-011][ewp-md11] retained universal P1 wrong pressure response and finite-Phi
E2C blocked. [SCI-MD-012][ewp-md12] located the coupled endpoint-envelope failure,
found a within-bounds root witness, and established that root repair cannot change
the adoption decision. **RETIRE_E2C_FROM_CURRENT_DEVELOPMENT_PRIORITY_NO_REPARAMETERIZATION_TEST**
stands. The deduction above is explanatory reuse, not a new closure proposal.
Any later mechanism needs an identifiable role, matching observable and simpler
baseline. Intragrain chemistry and hydraulic change need separate questions;
Spearman +1 or a newly selected 5-g threshold alone would not validate either.

### R8–R10 and R13–R14: data, uncertainty and process

**Original claims:** lack of public files proves absent/exhausted data; pooled
pressure/flow identifies a hydraulic law; inter-source viscosity implies ±50%
probability; document/branch counts prove governance caused slow science.
**Revised:** none follows. The [eligibility matrix](#question-specific-data-eligibility)
and [completed index](#completed-and-negative-work-index) preserve available
evidence and prior use. [Visualizer's private-work record][ewp-visualizer]
includes descriptive, matched empirical and native work beyond the initial boundary
stop. A new hydraulic question must account for sensor/flow meaning, controller
feedback, coffee/grind/dose, duplicates and repeated cohorts before interpreting
a slope; chemistry is not required for every hydraulic description. Same-shot
fitted conductance is not an untouched holdout or a measured permeability map.

Source viscosity disagreement is material-/basis-/domain-dependent sensitivity
information. It is not automatically symmetric uncertainty with a probability
model. Suitable analytical, numerical, unit and regression contracts must remain
strong even when empirical tests fail. No branch-count/test-file quotas, new
PASS exceptions, package relocation, automatic experiment programme or standing
physics authority follow from this guide. Process causality was not measured.

## R1–R15 disposition crosswalk

These are the stable recommendation references supplied with the task; original
review section numbers remain subject to the [input limitation](#review-input-limit).
“Proposed” below confers no authority.

| ID / original proposal as supplied | Disposition and development consequence | Controlling evidence |
|---|---|---|
| R1 Cameron reproduction disclosure/gate | **Retain/narrow:** exact 20-g/40-g/5-bar residuals; no arbitrary empirical gate or inventory change | [Cameron audit][cameron-audit], pressure finding above |
| R2 pressure correction / hydraulic substitution | **Split/revise:** source/observable/product contract first; any hydraulic replacement separate and material/rig matched | Primary SI + call path; [Waszkiewicz card](../cards/waszkiewicz2025.md) |
| R3 Grudeva factor correction | **Supersede repeat:** 003's spatial/observer frontier; no factor assumption or fixture repair | [003](../analysis/model_grudeva2026_conservative_003/RESULTS.md) |
| R4 evidence/verification classification | **Retain concept:** purpose/exposure distinctions in this guide; no new schema | [Decision logic](#how-to-judge-a-capability-or-a-proposed-task), existing registry |
| R5 close negative task families | **Revise:** compact synthesis and scoped reopening criteria; preserve history and useful negative evidence, no blanket archival | [Completed index](#completed-and-negative-work-index), leverage ledger |
| R6 new stress/hydraulic mechanism | **Replace:** acknowledge existing law; retired E2C; identify a distinct testable mechanism before proposing implementation | [SCI-MD-012][ewp-md12], WP03 |
| R7 sequence chemistry/hydraulics | **Retain sequencing:** isolate mechanisms and observables; no indefinite total freeze | EWP strategy and gate; frontier dependencies |
| R8 pressure experiments | **Defer:** demonstrate the remaining named gap; source-condition and marginal-value design first | [SCI-ED-003][ewp-ed3], eligibility matrix |
| R9 Visualizer hydraulic inference | **Conditional:** source-qualified descriptive/matched use, deduplication and equal-information baselines; no pooled causality | [Private-work record][ewp-visualizer] |
| R10 package/module relocation | **Defer:** compatibility, consumer and dependency evidence required; no moves in this task | [API policy](../API.md), [production lock][ewp-lock] |
| R11 navigation / destructive cleanup | **Split:** guide/navigation now; deletion, branch cleanup and archival separately reviewed | CURRENT index and this bounded diff |
| R12 physics-first explanation | **Retain/stage:** source-to-observable explanations and links; no sprawling rewrite | Capability matrix and thin EWP pointer |
| R13 test quotas | **Replace quotas:** risk/capability-appropriate analytical, numerical and empirical tests; known inadequacy visible | Existing governance/CI and frozen numerical contracts |
| R14 standing physics authorization | **Proposal only:** owner-granted bounded task scope remains necessary | Current user scope; EWP Stage F/D remain unauthorized |
| R15 decisive test and fresh data | **Revise:** require a discriminating oracle and nonduplication; existing data or analytical oracle may suffice | Three-test gate and reopening premises below |

## Near-term frontier

Only the guide/navigation work is **authorized and implemented in this delivery**.
The following five ranked items are **proposed, not launched**. Existing completed
work is not reopened by this list. Issue references identify related work, not
authorization or a new queue entry. Ranking retains pressure disclosure first;
new empirical scoring and numerical extensions are conditional because current
source joins and closed decisions do not yet justify them. #321's new engineering
qualification reduces the case for another adjacent synthetic extension.

### 1. Leading actionable task: source-traceable Guided Pull disclosure

- **Decision/question:** can the product faithfully describe its pressure input,
  supported recipe conditions and unresolved Cameron reproduction without changing
  the computed shot? Related existing issue: **#48**. New premise relative to
  merged F13/F14/F15 and the dated synthesis: the explicit SI→domain→preset→solver→report
  mismatch established above. This changes how an owner interprets predictions.
- **Scope:** `_pull.py` labels/help, product documentation and affected report tests;
  permitted future work is explanation and traceability. Exclude equations, bounds,
  constants, defaults, public field semantics and numeric behavior; a proposed
  semantic/runtime correction requires its own reviewed scope.
- **Inputs/oracle/baseline:** inspected publisher/SI, exact current call path and
  same serialized recipe. Compare all affected labels against source reference/node
  and prove unchanged numerical inputs/outputs with the existing compatibility
  checks. No empirical fit, grouping or new holdout; exposure is source inspection.
- **Prerequisites/metrics:** source-supported versus computational versus
  extrapolated conditions explicit on every affected surface; retain exact audit
  configuration and units. Text traceability and unchanged numeric/API contract,
  not a new empirical tolerance. Sensor/reference equivalence remains explicitly
  unresolved if the primary text cannot settle it.
- **Outcomes:** success is consistent truthful reporting; negative is a documented
  source contradiction requiring qualified wording; unavailable evidence leaves a
  named source question; stop before pressure conversion or changed model behavior.
  Dependency: this guide's finding; resource class **G0, small source/docs/software**.
  **PROPOSED; follow-on edits not authorized here.**

### 2. Existing-data comparison eligibility: conditional fraction prediction

- **Decision/question:** can a mechanistic finite-fraction predictor add useful
  accuracy or decision value beyond an equally informed empirical/conservation
  baseline on an existing source? Reuse **#70/#96** and the existing C01/input-mapping
  decisions, not a new model family. MASS-006/007/008 and stopping-decision are
  completed; the original two-assay/stopping questions are not new.
- **New premise required:** an already-held, source-qualified same-shot input or
  observation join that closes flow/clock, inventory/state or assay basis without
  fitting the evaluation outcomes. None is established by this guide. Candidate
  source IDs are Pannusch `experimental_kinetics`/Schmieder `raw_fractions` and the
  existing C01 supports; inspect authorized primary methods/source code before
  claiming that join. Do not reinterpret scale derivative as inlet Q.
- **Scope/controls:** first use existing preflight/adapter/result paths to decide
  eligibility only; a later authorized score may compare the chosen kernel with
  C0 or conservation bounds using the same early assays, measured mass, geometry
  and training privileges. Group shots and source conditions; keep FIT/PRED and
  earlier exposure explicit. No target reuse for calibration, acquisition,
  new inventory predictor, repeated 007 score or source-role change here.
- **Numerical/decision prerequisite:** qualify the specific finite-window observer
  and source scales before scoring; if 004 is needed, its temporal failure matters.
  An empirically justified absolute error/decision budget is **unresolved**; historical
  MASS thresholds cannot simply be imported into a different estimand.
- **Outcomes:** eligible join plus distinct consequential claim supports drafting
  one bounded comparison; negative preserves source ineligibility or later simpler
  model sufficiency; unavailable source means known evidence unavailable; stop if
  the comparison remains the same closed decision or all outcomes select the same
  action. **BLOCKED on a substantive new input/observer premise; G1 if later
  authorized; no score authorized.** This fails the new-information gate until
  the premise exists. Circuit breaker prevents another inventory/clock workaround.

### 3. Only numerical prerequisites selected by that comparison

- **Decision/question:** can the required observer meet a justified numerical
  budget without changing the physical model? Reuse **#67** for Grudeva or the
  existing stateful-004 lane; choose only the route actually needed by item 2.
  Predecessors: 003 conservative balance passes/bed refinement fails; 004 temporal
  decrease fails. 005/006/007 fixed-operator certificates do not resolve either.
- **Substantive new premise:** a demonstrated discretization/observer defect or a
  newly selected comparison requiring its unresolved observable. “Try finer” or
  another envelope is insufficient. Primary Grudeva SI E.2 and the exact executed
  source must be inspected before a scheme-dependent proposal; access is not
  established here. For Pannusch use the frozen short-window case and independent
  actual-time reference, not empirical outcome tuning.
- **Scope/oracles/baseline:** component-local numerical/observer work only, if
  authorized; preserve phase inventories, actual raw states, clocks, forcing and
  parameters. Independent analytical limits/manufactured transport and a qualified
  reference are controls with identical inputs. No publication-output multiplier,
  changed fixture, physical-law modification, reference promotion or empirical fit.
- **Metrics/outcomes:** retain the existing method-specific allowances and complete
  support; distinguish conservation, event displacement, smooth profiles and finite
  cup/fraction delivery. 003's `.001` outlet and `.00005` cup and 004's `5e-4`/decrease
  requirements are historical numerical contracts, not assay error. Success earns
  only the needed numerical qualification; failure preserves incomplete status;
  unavailable primary/raw state blocks comparison; stop at the separately frozen
  bounded resource cap. **BLOCKED/PROPOSED; G2 numerical work requires separate
  authority**, dependent on item 2 or an independently demonstrated material defect.

### 4. EWP mechanism decision after source/observation matching

- **Decision/question:** is there an identifiable hydraulic hypothesis that can
  change a useful prediction beyond the completed fixed/evolving-resistance and
  poroelastic tests? Predecessors SCI-MD-010/011/012 and Visualizer PLAY/boundary
  work are completed or blocked as recorded. Reuse the existing
  **EWP-RWB-001-PRESSURE-SENSOR-BOUNDARY-INTERFACE-RECONCILIATION** proposal if its
  source semantics can be resolved; do not rerun pooled corpus regression.
- **New premise/inputs:** documented sensor/flow/controller semantics and a
  materially different identifiable response, or another eligible observation of
  the proposed mechanism. Waszkiewicz per-brew hydraulic data and permissioned
  Visualizer histories are candidates for different questions, not interchangeable
  controls. Their primary rig/method documentation must support the mapping;
  the missing authority remains **unresolved**, not a request for a new experiment.
- **Scope/baseline:** first specify the source/operator/claim in existing analysis
  paths. Any later hydraulic test keeps chemistry separate, gives B0/B1 or an
  appropriate fixed-resistance baseline the same forcing/training information,
  groups real shots/conditions and preserves exposure. No E2C reparameterization,
  automatic Waszkiewicz substitution, diffusion port, viscosity distribution,
  production adoption or solver execution under this guide.
- **Prerequisites/outcomes:** dimensional/node/clock consistency, identifiable
  parameter role and numerical error below a decision-relevant budget; that new
  budget is **not yet justified**. Success selects a bounded discriminating test;
  negative retains simpler representation; unavailable metadata stops that transfer
  claim; stop if root restoration cannot affect adoption or multiple mechanisms
  are confounded. **PROPOSED, blocked pending new semantics/hypothesis; G1 source
  decision before any G2 implementation**, independently justified from item 2.

### 5. Bounded reader-facing simplification

- **Decision/question:** can a new reader find current capability, input semantics,
  evidence and blocker without mistaking historical lifecycle text for live state?
  Reuse **#41/#48/#70** and CURRENT. New information is the merged/candidate/pin
  crosswalk in this guide, not a scientific result. The guide and minimal navigation
  are **authorized here**; wider report/landing-page changes remain **proposed**.
- **Scope/oracle/baseline:** link current explanations to existing cards/results,
  and later correct only demonstrated stale reader-facing claims. Compare with
  current source and GitHub metadata, preserve dated records and generated owners.
  No module moves, branch deletion, mass archival, new generator/status schema or
  quotas. Grouping/empirical tolerance are not applicable.
- **Outcomes/checks:** success is resolving links and accurate current-versus-
  historical wording; negative means retain a page whose consolidation would lose
  material distinctions; missing deployment/human-acceptance evidence stays pending;
  stop when cleanup becomes destructive or claims require new science. **G0 small
  docs task**, using existing documentation tests, with no claim of physical progress.

New experiments are conditional only after the named source review fails to supply
a decision-changing observable. [SCI-ED-003][ewp-ed3] already defines M01 plus
contextual M02 as a future minimum candidate; Stage F/D remain unauthorized.
Any later design must justify conditions, replication, calibration/final-test
separation, randomization/blocking and measurement uncertainty from its decision.
An original 5/7/9-bar proposal would not directly reproduce WP03's 5/9/11-bar comparison.
No same shots may serve as both a fitted permeability map and untouched confirmation.

## Completed and negative work index

| Existing work | Preserve / reopen only on |
|---|---|
| [October 1 synthesis][october-review], [Cameron audit][cameron-audit], PW#304/EWP#201 | F13 phase/area inventory, F14 comparator and F15 water-fraction conversion completed. Released-source sparse Octave execution and balance attribution completed. New source/configuration or demonstrated remaining defect required; no repeat “runtime unavailable” claim |
| [Grudeva001](../analysis/model_grudeva2026_reduced_001/RESULTS.md), [002](../analysis/model_grudeva2026_reference_002/RESULTS.md), [003](../analysis/model_grudeva2026_conservative_003/RESULTS.md) | Numerical-reference mismatch retained; figure re-extraction answered; conservative comparator still spatially incomplete. Reopen only with distinct qualified source/numerical premise |
| [Pannusch003](../analysis/model_pannusch2024_flow_temp_fv_003/RESULTS.md), [004](../analysis/model_pannusch2024_stateful_fv_004/RESULTS.md), [005](../analysis/model_pannusch2024_state_envelope_005/RESULTS.md), [006](../analysis/model_pannusch2024_prefix_conditioned_006/RESULTS.md), [candidate007][007-closeout] | Credit bounded capabilities; keep parent temporal and continuum limitations. No adjacent extension without decision value |
| [MASS006][mass6], [007][mass7], [008][mass8], [stopping][stop-result] | Learning earned, zero-shot absolute transfer inadequate, adaptation adequate without material increments, stopping adequate without C2 increment. New cohort/input privilege/decision required, explicitly exposed |
| [Caffeine](../analysis/sci_md_caffeine_delivery_001/RESULT.md), [trigonelline](../analysis/sci_md_trigonelline_delivery_001/RESULT.md), [5-CQA](../analysis/sci_md_5cqa_delivery_001/RESULT.md) | Simpler caffeine adequate; trigonelline mass-shape gain positive; tested 5-CQA families inadequate. No programme-wide “all negative” or assay-bias explanation |
| [Fraction window][ewp-window], [flow history][ewp-flow], [input mapping][ewp-mapping], [data fusion][ewp-fusion], [C01 §E][october-review] | O1=O0 exact null; flow authority ineligible; 21 mappings unqualified; complementary source-conditioned support only. New source semantics/join needed, not a renamed normalization |
| [Moroney](../analysis/sci_md_moroney_transfer_001/RESULT.md), [Mo](../analysis/sci_md_mo_transfer_001/RESULT.md), [Maillé](../analysis/sci_md_maille_transfer_001/RESULT.md), [Smrke](../analysis/sci_md_smrke_transfer_001/RESULT.md) | Deep calibration inadequate; Mo source/numerics blocked; Maillé denominator blocked; tested Smrke common/fines forms inadequate. Resolve the named defect/join before another transfer claim |
| [WP03][ewp-wp03], [SCI-MD010][ewp-md10], [011][ewp-md11], [012][ewp-md12], [dynamic resistance][ewp-dynamic] | Converged wrong ranking, reduced Darcy no stable advantage, P1 wrong response, E2C retired from priority; no root-only reopening |
| [RHEOLOGY008][ewp-rheo8], [011][ewp-rheo11] | Coarsest tested communicating E2 qualifies against computational C; arrangement contrast below budgets in tested delivery. Neither experimental truth nor exact invariance; do not combine with extraction-mechanism acceptance |
| [Visualizer prior programme][ewp-visualizer], [SCI-ED003][ewp-ed3], [leverage ledger][ewp-ledger] | Corpus not generally exhausted. Boundary/onset/machine questions already examined; new sensor semantics or distinct decision needed. Laboratory feasibility/execution still requires owner authority |

## Maintaining this guide

Update after a material merge, qualification change, newly eligible source,
completed decision or changed limitation. Recheck live main/PR metadata; amend
only affected capability/eligibility/disposition rows and the leading action.
Keep producer pins, historical thresholds and adverse executions intact. Cite
the current status date separately from the evidence date. If a recommendation
is authorized later, record that in the existing issue/queue rather than treating
this guide as permission. Do not hand-edit generated STATE_OF_TRUTH or duplicate
this full guide in EWP. Replace EWP's branch-aware link with a main link only after
the canonical guide merges.

Use existing documentation/link/generated-artifact checks; preserve the frozen
release, runtime/API/parameter/defaults, historical bundles and dependency lock.
No mandatory generator, recurring audit, prose-freezing test or new lifecycle
schema is introduced. The delivery handoff records actual check commands/results
and outstanding acceptance requirements; checks are software evidence only.

[october-review]: ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md
[cameron-audit]: ../analysis/cameron_local_audit_20260930.md
[data-guide]: ../data/ESPRESSO_DATA_GUIDE.md
[mass6]: ../analysis/sci_md_mass_delivery_006/RESULT.md
[mass7]: ../analysis/sci_md_mass_delivery_007/RESULT.md
[mass8]: ../analysis/sci_md_mass_delivery_008/RESULT.md
[stop-result]: ../analysis/sci_md_mass_stop_decision_001/RESULT.md
[007-source]: https://github.com/trbrewer/puckworks/blob/bd976d2d4b7fc516c005765befedf5911a89ab2e/puckworks/models/pannusch2024/common_past_contrast.py
[007-closeout]: https://github.com/trbrewer/puckworks/blob/bd976d2d4b7fc516c005765befedf5911a89ab2e/docs/analysis/model_pannusch2024_common_past_contrast_007/CLOSEOUT.md
[ewp-lock]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/dependencies/puckworks.lock.json
[ewp-state]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/PROJECT_STATE.md
[ewp-data-authority]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/provenance/AVAILABLE_DATA_AUTHORITY.json
[ewp-leverage]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/provenance/EXISTING_DATA_LEVERAGE_PROGRAMME.json
[ewp-ledger]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/data_leverage/DATA_LEVERAGE_LEDGER.csv
[ewp-data-first]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/strategy/DATA_FIRST_SCIENTIFIC_DEVELOPMENT_PLAN.md#4-three-test-task-selection-gate
[ewp-data-map]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/EXTERNAL_ESPRESSO_DATA.md
[ewp-solver]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/solver/espressoWholePullFoam/espressoWholePullFoam.C
[ewp-poro]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/solver/espressoWholePullFoam/poroelasticCompaction.H
[ewp-r0]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/config/reference_R0.json
[ewp-wp03]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/wp03/WP03_002_RESULTS.md
[ewp-wp03-json]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/validation/wp03/WP03_002_CORRECTED_COMPARISON.json
[ewp-md10]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/sci_md_010/RESULT.md
[ewp-md11]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/sci_md_011/RESULT.md
[ewp-md12]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/sci_md_012/RESULT.md
[ewp-ed3]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/sci_ed_003/RESULT.md
[ewp-prior]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/ewp_porosity_permeability_prior_001/RESULT.md
[ewp-visualizer]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/data_leverage/VISUALIZER_PRIVATE_WORK_RECORD.md
[ewp-rheo8]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/sci_md_rheology_008/RESULT.md
[ewp-rheo11]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/sci_md_rheology_011/RESULT.md
[ewp-dynamic]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/xsv_waszkiewicz_dynamic_hyd_001/RESULT.md
[ewp-window]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/obs_pannusch_fraction_window_001/RESULT.md
[ewp-flow]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/sci_md_pannusch_flow_history_001/RESULT.md
[ewp-mapping]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/xsv_pannusch_ewp_input_mapping_001/RESULT.md
[ewp-fusion]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/analysis/sci_data_fusion_001/RESULT.md

[ewp-wp02]: https://github.com/trbrewer/espresso-whole-pull/blob/73ec476ffe6ac626705ca949e28b32935ddf2992/docs/wp02/WP02_001_EFFECTIVE_PERMEABILITY_BRANCH.md
