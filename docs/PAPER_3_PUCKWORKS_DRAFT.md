# Puckworks: an executable, provenance-aware evidence registry for espresso process models

**Working manuscript draft — 15 July 2026**  
**Authors:** [Author names and affiliations to be inserted]  
**Corresponding author:** [Name and email to be inserted]

> **Draft status.** This manuscript was developed from `PAPER_3_PUCKWORKS_OUTLINE.md`, the Puckworks source tree, model and dataset cards, evidence tables, public-claim schema, release runbook, and the retained broad synthesis in `PAPER_B_DRAFT.md`. The present corpus is described as **curated**, not systematic. Repository counts are a snapshot and must be regenerated from a frozen release before submission. Demonstration figures are specified but not embedded. Statements about software readiness distinguish current functionality from work still required for a citable release.

## Abstract

Published espresso models describe different parts of the brewing process with incompatible state variables, units, pressure locations, concentration conventions, inventory bases, experimental windows, and standards of evidence. Combining them by matching similarly named quantities can produce numerically plausible but scientifically invalid results. We present Puckworks, an executable, provenance-aware registry that represents espresso process models as stage-specific components with typed state carriers, explicit assumptions and validity ranges, source and dataset cards, validation gates, evidence labels, and reproducible claim producers. Puckworks is not a monolithic “digital twin.” A simulation is a declared configuration of components and adapters, and each output retains the provenance and evidence status of the weakest load-bearing link. In the current development snapshot, the registry contains 25 components across grind, packing, machine, infiltration, flow, extraction, and bed-dynamics stages, supported by 70 dataset-manifest records. We demonstrate the architecture in three cases. First, observable linting exposes incompatible saturation concentrations (170, 212.4, and 224 kg m⁻³), distinct pressure nodes, and an invalid mixed-unit aggregation of named-solute masses and total dissolved solids. After correction, raw total-dissolved-solids-derived extraction-yield cells are ordered across three grinder settings, while a conditional response-surface vertex remains a separate fitted object. Second, a null-first temporal-flow workflow preserves distinctions among machine capacity, static baselines, imported temporal trajectories, flexible in-sample curves, and held-out pressure assessments. Third, adding an imported swelling branch to a shared-porosity composition worsens reconstruction error from approximately 0.116 to 0.648 g s⁻¹, worse than a constant baseline, illustrating that component validity does not guarantee composition validity. A named-shot scorecard then shows how Puckworks reports observed, calibrated, verified, reconstructed, extrapolated, and open stages without presenting an unsupported end-to-end prediction. The contribution is a general method for executable reviews of coupled process models: make observable semantics and parameter provenance operational, preserve negative results, separate verification from validation, and translate model disagreement into discriminating experiments.

**Keywords:** scientific software; executable review; provenance; evidence registry; typed contracts; espresso; coupled process models; reproducibility; model validation; negative results

## 1. Introduction

Espresso brewing has become a compact testbed for coupled process modeling. A single shot can involve grinder-dependent particle populations, tamped-bed geometry, pump and headspace dynamics, unsaturated infiltration, Darcy or Forchheimer flow, deformation and fines transport, heat and mass transfer, multicomponent dissolution, and measurement operators that convert local fields into pressure, flow, beverage mass, total dissolved solids, or named-solute concentrations. Published studies usually isolate one or a few of these processes, as they should. Difficulty arises when results from different lineages are assembled as though their inputs and outputs were already commensurate.

Two models may both use a symbol called concentration while referring to different volumes, species, inventories, or saturation limits. A pressure trace may refer to the pump outlet, headspace, basket gauge, or pressure drop across the wet bed. Grinder “dial 1.7” is not a portable physical coordinate across grinder models or burr calibrations. A model may have passed a numerical reproduction test but never have been compared with independent experimental data. A fitted reconstruction, a held-out prediction, and a qualitative sign test may all appear as “validation” in prose even though they support different verbs. These differences are not editorial details: they determine whether a coupled calculation has a coherent physical meaning.

Puckworks was developed to make those distinctions executable [1]. The repository describes itself as a component registry rather than a mega-model. Each component is assigned to a process stage, linked to a paper or project source, documented with assumptions and a validity range, and, where possible, associated with gates. Components exchange structured state objects rather than unlabelled arrays. Source cards and data-manifest rows preserve the path from publication to executable input. Public claims are generated by named functions, carry units and evidence labels, and include caveats and validity ranges. Release tooling checks not only numerical regeneration but also source-commit identity, a clean working tree, environment versions, and artifact hashes. The current corpus spans machine and infiltration models [2], poroelastic and fines-evolution models [3,4], extraction-kinetics and integrated brewing models [5–10], particle swelling [11], and equilibrium desorption [12].

The scholarly contribution is therefore not simply that several espresso equations have been implemented. It is an executable review architecture for a literature in which models cannot safely be compared or composed until observable meaning, parameter provenance, boundary conditions, and evidence strength are explicit. The same problem occurs in many coupled food-process, filtration, reactive-transport, and porous-media repositories.

This paper describes the architecture and demonstrates why it matters. We first define the current curated corpus and process-stage taxonomy. We then present the typed-contract, evidence, provenance, and release layers. Three demonstrations show observable and unit linting, null-first model comparison, and preservation of a failed composition. We conclude with an experiment-design workflow and a named-shot scorecard that exposes, rather than fills, gaps in an end-to-end chain.

## 2. Scope of the resource and corpus construction

### 2.1 Current corpus status

The current repository corpus is a curated development collection assembled to support explicit comparison and integration tasks. It is **not** described as a systematic review because an indexed search protocol with databases, complete queries, date limits, duplicate handling, screening records, and exclusion reasons has not yet been completed. The corpus is useful for methods development and domain synthesis, but completeness and prevalence claims would be premature.

At the snapshot used to prepare this draft, the registry source contains 25 registered components and the data manifest contains 70 records [1]. The stage distribution is shown in Table 1. These counts are descriptive of one repository state and should be regenerated from the release artifact cited by the final paper.

**Table 1. Registry snapshot used for this draft.**

| Registry stage | Number of components | Typical role in the current corpus |
|---|---:|---|
| Grind | 1 | grinder-setting or particle-size calibration |
| Packing | 2 | bed geometry and permeability calibration |
| Machine | 2 | pressure/flow boundary generation or calibration |
| Infiltration | 2 | wetting-front runtime or calibration analogue |
| Flow | 5 | Darcy/Forchheimer runtime and flow-related calibrations |
| Extraction | 8 | single- or multi-solute runtime models and calibration closures |
| Bed dynamics | 5 | poroelasticity, swelling, fines migration, heterogeneity, synthesis |
| Observables | 0 | reserved stage; observable logic currently resides mainly in adapters and harnesses |
| **Total** | **25** | 11 runtime, 13 calibration, 1 synthesis |

The presence of an empty observables stage is informative. It records an intended architectural boundary that the current implementation has not yet fully promoted into first-class components. Similarly, the component dataclass comment currently lists `runtime` and `calibration`, while one registered component uses `synthesis`. This is not hidden as a harmless detail; it is schema debt to resolve before a stable public API.

### 2.2 Inclusion logic for the curated corpus

A publication or dataset enters the current resource when it contributes at least one of the following:

- an executable process model relevant to espresso or a directly transferable packed-bed operation;
- a constitutive or calibration relation required by a registered runtime model;
- a dataset that can verify an equation, reproduce a source curve, calibrate a component, or test a prediction;
- an alternative mechanism that competes for the same observable;
- a measurement operator or convention needed to compare model output with data; or
- a mathematically explicit but parameter-blocked model whose absence is itself important for experiment design.

A source is not excluded merely because it lacks code or numeric parameters. Instead, the card records whether it is implementable, parameter-blocked, data-only, qualitative, or superseded for a particular purpose. Derivative models are linked to their lineage rather than counted as independent evidence when they reuse the same equations or calibration data. Data records specify source artifact, extraction method, published units, registry units, retained uncertainty, access or license, gate use, validation strength, and caveat.

### 2.3 Planned systematic-search upgrade

Before making a systematic or exhaustive claim, the project should preregister or publish a search protocol covering bibliographic databases, grey-literature sources, query strings, date range, language rules, eligible model and data classes, duplicate/derivative handling, two-stage screening, adjudication, and a flow diagram. The protocol should distinguish papers that model espresso directly from transferable coffee, packed-bed, filtration, rheology, and extraction studies. It should also record searches that yield no usable constitutive data, because negative searches explain why a contract field remains open.

## 3. Registry architecture: components rather than a mega-model

### 3.1 A configuration is the unit of simulation

Puckworks decomposes the system into components. A runtime calculation selects one component for each occupied runtime stage and may consume parameters generated by offline calibration components. This design avoids the assumption that the most detailed equation from every paper should be combined into one universal solver. Composition is explicit, and omission is allowed: a study of infiltration need not instantiate a multisolute extraction model, while an extraction comparison can consume a recorded flow trace rather than a machine model.

The conceptual process graph is:

$$
\text{grind and material characterization}
\rightarrow \text{packing/geometry}
\rightarrow \text{machine boundary conditions}
\rightarrow \text{infiltration/wetting}
\rightarrow \text{porous flow}
\leftrightarrow \text{bed evolution}
\leftrightarrow \text{extraction/transport}
\rightarrow \text{observables}.
$$

The arrows are not all one-way. Swelling or dissolution can alter porosity and permeability; flow controls residence time; extraction changes inventories; machine pressure responds to hydraulic load. Puckworks makes a coupling an explicit configuration decision rather than an implicit consequence of importing two modules.

### 3.2 Component metadata

The current `Component` record contains:

| Field | Purpose |
|---|---|
| `name` | stable component identifier |
| `stage` | registry stage |
| `kind` | operational class such as runtime, calibration, or synthesis |
| `paper` and `doi` | source provenance |
| `module` | executable implementation location |
| `assumptions` | load-bearing model assumptions |
| `valid_range` | stated or inferred domain of use |
| `gates` | executable checks returning pass/fail plus diagnostics |
| `notes` | unresolved caveats, lineage, or adapter requirements |

A gate may verify a closed-form limit, reproduce a published curve, compare with a fitted dataset, or test an independent measurement. Passing a gate therefore does not have one universal scientific meaning. The evidence label belongs with the gate result.

### 3.3 Operational roles

The paper distinguishes five roles even though not all are first-class enum values in the current code:

1. **Runtime component:** advances or evaluates the process state for a configuration.
2. **Calibration component:** estimates a parameter or mapping used by another component.
3. **Observational adapter:** maps model state to the exact observable and unit used by a dataset.
4. **Diagnostic/exploratory component:** probes capacity, regime, sensitivity, or failure without being a validated runtime replacement.
5. **Synthesis component:** combines registered mechanisms under an explicitly new composition rule.

Promoting these roles into a versioned schema is a release-readiness task. In particular, adapters should be discoverable and testable objects rather than logic buried in analysis functions.

## 4. Typed contract architecture

### 4.1 Contract design principles

The current contract schema is version 0.6. It uses Python dataclasses to carry named state between stages. The evolution rule is add fields without changing their meaning; repurposing a field requires a breaking schema version. Optional values use an explicit missing state rather than a numeric sentinel. Comments specify expected units and semantics, and selected high-risk conversions have executable guards.

This is a typed state interface, not yet a full dimensional type system. A float annotated in a dataclass can still be supplied in the wrong unit. Puckworks therefore combines named fields, documented units, adapters, runtime assertions, and data-manifest metadata. A future release could add a units package or static dimensional checking without changing the semantic rule.

### 4.2 Core state carriers

**Table 2. Current state contracts and their main semantic obligations.**

| Contract | Selected fields | Required interpretation |
|---|---|---|
| `GrindState` | setting, fines fraction, boulder/fines/mean radii | grinder setting is device-specific; radii are SI lengths; missing PSD moments remain missing |
| `BedState` | dose, depth, area, porosity, Darcy permeability, inertial permeability, $\kappa$, heterogeneity, depth profiles | porosity type must be documented; permeability is SI; scalar and spatial states are not interchangeable |
| `FlowLaw` | $k$, inertial permeability $k_I$, closure | distinguishes Darcy from a named Forchheimer closure |
| `PumpHeadspace` | shut-off pressure, maximum flow, pipe resistance, headspace height, temperature ratio, capillary pressure | generates machine pressure nodes rather than consuming a recorded trace |
| `MachineState` | pressure function, recorded profiles, pump outlet, headspace, basket pressure, bed drop | pressure nodes must remain distinct; do not apply two corrections to the same segment |
| `SoluteInventory` | per-species amount, unit, basis, source, evidence strength, optional extractable fraction | total roasted content is not automatically extractable inventory |
| `ShotResultState` | extraction yield, TDS, shot time, beverage mass, traces | aggregate outputs require named observable definitions; per-solute extension remains a roadmap item |

### 4.3 Pressure-node identity

A pressure value without a location is incomplete. Puckworks distinguishes at least:

- pump outlet pressure $p_p$;
- headspace or bed-top pressure $p_h$;
- basket gauge pressure $P_{\text{basket}}$; and
- pressure drop across the wetted bed $\Delta P_{\text{bed}}$.

These quantities can differ because of pipe resistance, valves, headspace compression, filters, and outlet losses. Applying a pipe correction to a trace that already represents basket pressure, then subtracting it again when computing bed pressure drop, silently double-counts resistance. The contract stores nodes separately and requires an adapter to declare the source node. One currently used DE1 fixture still has open pressure-node identity; Puckworks reports that gap rather than selecting a convenient interpretation.

The present schema also illustrates why documentation and executable units must converge. A legacy pressure callback is documented in bar gauge, while explicit node fields are documented in pascals. A stable release should either normalize all runtime fields to SI or require typed unit wrappers at the boundary.

### 4.4 Permeability and inertial-flow units

Permeability is especially hazardous because some inertial closures contain exponentials or power laws in $k$. An off-SI value can produce a plausible number while changing the closure by orders of magnitude. Puckworks therefore asserts a broad SI window,

$$
10^{-18} < k < 10^{-6}\ \text{m}^2,
$$

before using the relevant Forchheimer relations. The window is not a scientific prior on espresso permeability; it is a guard against supplying values in square micrometres or table-scaled units to an SI formula. The manifest retains both published and registry units so the conversion is auditable.

### 4.5 Concentration, inventory, and saturation semantics

The extraction corpus contains at least three saturation-concentration values: 170, 212.4, and 224 kg m⁻³. They arise from different model lineages or source configurations and are paired with different inventory references and dissolution laws. They are configuration fields, not replicate estimates of one quantity to average.

Likewise, an “initial soluble concentration” may mean solute per bed volume, solute per grain volume including internal pores, or a named-solute inventory; equilibrium-desorption formulations make the inventory basis especially consequential [12]. `SoluteInventory` explicitly carries the basis and an optional extractable fraction. Total roasted-bean content from a chemistry source remains a prior or cross-check until an extractability mapping is supplied. A consumer must not substitute total content for extractable solid inventory simply because the units can be converted.

Saturation also has multiple meanings. Foster’s infiltration model uses a binary wet/dry front; extraction models may assume a fully saturated bed from the start; concentration models may use a solubility ceiling; and a future Richards-type model would require continuous water saturation and relative permeability. Puckworks does not place these meanings into one field named `saturation`.

### 4.6 Missing data and no silent repurposing

A missing field is represented as missing, not as zero. Zero permeability, zero fines fraction, zero extractability, and unknown values have different scientific meanings. Arrays for depth-resolved porosity and fines inventories are separate from scalar bed fields because a scalar multiplier cannot safely host a spatial state. When a model needs an absent quantity, the configuration must provide an adapter, adopt an explicit assumption, or remain blocked.

The rule against repurposing is central. Once `k_m2` means Darcy permeability in square metres, it cannot later carry a dimensionless permeability multiplier. Once an inventory amount is documented as total roasted content, it cannot silently become extractable content. Schema evolution occurs by adding a new field or a new contract version.

## 5. Evidence taxonomy

### 5.1 Evidence labels are not one scalar score

Puckworks records evidence as a set of named categories rather than a single “validated” flag. Some categories are stronger for prediction; others answer different questions, such as whether code reproduces an equation or whether a mechanism has the correct sign. Table 3 defines the vocabulary used in this paper.

**Table 3. Evidence categories and permitted interpretations.**

| Evidence category | What was done | What it supports | What it does not support |
|---|---|---|---|
| Code verification | numerical identities, limits, conservation, convergence, or parity checks | implementation behaves as specified | agreement with a real system |
| Source-curve reproduction | reimplementation matches a curve generated or fitted in the source | faithful transcription and source-model capacity | independent validation |
| Post-fit reconstruction | model is scored on data used to fit its parameters | descriptive fit and residual structure | out-of-sample prediction |
| Within-campaign held out | a condition is excluded from a defined calibration but other campaign information is reused | conditional transfer within that rig/campaign | independent external generalization |
| Independent external | prediction is compared with a distinct measurement not used for fitting | evidence of transfer on the tested observable/domain | universality outside that domain |
| Qualitative capacity | model can generate a sign, shape, peak, or ordering | mechanistic possibility under assumptions | quantitative explanation or identification |
| Sign/compatibility | conservation, monotonicity, or direction conflicts with an observation | exclusion or constraint of a specified isolated branch | absence of the process in a coupled system |
| Exploratory synthesis | components are combined under a new composition rule | behavior of that proposed composition | inherited validation from the parts |
| Negative validation | a model, transfer, or composition fails a declared check | boundary of applicability; prevents silent tuning | proof that every related mechanism is false |
| Proposed experiment | models make different directional predictions under an intervention | a falsifiable data-collection plan | empirical evidence before the experiment is run |

The labels constrain language. A source-curve reproduction “reconstructs” or “reproduces”; a held-out result “predicts within the campaign”; a capacity result “can generate”; a sign test “is incompatible under the stated assumptions.” The registry does not promote a result to a stronger verb because it appears in a public-facing graphic.

### 5.2 Evidence vectors for components and claims

A component can carry several evidence entries. For example, an extraction solver may have mass-conservation verification, reproduce a source fit, and read low against an independent extraction-yield range. These entries should coexist rather than collapse into the strongest or weakest badge. The claim layer then selects the evidence relevant to a particular statement.

The public schema uses four visual badges—`OBSERVED`, `RECONSTRUCTED`, `PREDICTED`, and `EXPLORATORY_SIMULATION`—while preserving the underlying evidence-strength label unchanged. Every numeric public claim also carries units, source dataset identifiers, validity range, a primary caveat, a reproduction command, and a named producer that regenerates the value. A claim whose numeric field has no producer mapping fails validation as hard-coded.

## 6. Provenance and reproducibility architecture

### 6.1 Model and source cards

A card is written before or alongside implementation. It records the source citation, scope, governing equations, parameters and provenance, calibration and validation offered by the source, assumptions, validity range, interface mapping, extractable data, overlaps and conflicts, and implementation verdict. Cards are interrogative documents: they expose missing constants, source inconsistencies, and observable mismatches before code makes them harder to see.

A card can conclude “data-only,” “parameter-blocked,” or “skip.” Such outcomes are part of the executable review. For example, the Fasano Part II porosity model provides a valuable structural template but no numerical constitutive functions; inventing those values would create an undocumented model rather than implement the paper [4].

### 6.2 Dataset manifest

Each dataset record includes:

- dataset identifier;
- source card and exact source artifact;
- extraction method, such as repository pull, transcription, or digitization;
- units as published and units in the registry;
- whether uncertainty was retained;
- access or license information;
- gate or analysis use;
- validation strength; and
- a caveat.

This structure distinguishes, for example, a digitized model curve from a measured trace, a standard deviation from unreplicated points, and a source repository that cannot be redistributed from one licensed for inclusion. The current 70-row manifest is a provenance inventory, not a guarantee that every row provides independent validation.

### 6.3 Gates, analysis harnesses, and generated results

Component gates are small executable checks tied to a named evidence object. Harnesses perform cross-component comparisons only after constructing matched observables and configurations. Generated result bundles separate expensive computation from plotting: analyses run once, serialize machine-readable outputs with source-commit provenance, and figures consume those outputs rather than refitting in the rendering layer.

This separation addresses a common reproducibility failure in scientific plotting, where a figure script contains hidden preprocessing, refits a model with different options, or hand-types a headline number. In Puckworks, manuscript-facing values should trace to a result path in a named producer.

### 6.4 Claim registry

A public or manuscript claim record includes the scientific question, headline, plain-language interpretation, numeric result, units, uncertainty or sensitivity, evidence strength, badge, components, source datasets, validity range, caveat, practical implication, reproduction command, and producer. Structural checks enforce that every numeric value has a unit and a producer path. Grinder-dial comparisons require a non-portability warning.

The claim registry is not only a communications layer. It catches scientific drift when an upstream analysis changes. Regeneration can show that a stored number no longer matches the producer, that a source dataset was removed, or that a caveat no longer matches the evidence category.

### 6.5 Release contracts

The release runbook uses external staging so generated artifacts do not dirty the detached source worktree. A valid archive should satisfy

```text
source tag commit == manifest.source_commit == bundle.source_commit
```

and report numerical verification, release freshness, a clean tree, and a matching bundle commit. Figures are archived in raster and vector forms with source-data exports. Archives receive deterministic checksums. The direct numerical environment for the current paper workflow is recorded as Python 3.13.13, NumPy 2.5.1, SciPy 1.18.0, and Matplotlib 3.11.0; a complete transitive lock or immutable container digest is still recommended for archival recreation.

The distinction between a passing analysis and a valid release is deliberate. A working-tree manifest can report successful numerical verification while also reporting a dirty repository or stale bundle. That state supports development but not an archival claim. Tag creation, author approval, repository publication, Zenodo deposition, and DOI registration remain explicit human actions.

### 6.6 External community corpus: governance, attribution, and honest scope

Two classes of data enter Puckworks. The first is the per-paper published datasets recorded in the manifest (§6.2). The second, added during this development cycle, is a large external community corpus of home- and prosumer-machine shot records retrieved under an explicit research-use grant from the data owner. This corpus is treated differently from a published dataset, and the difference is itself a provenance record.

**Scope and honest framing.** The community corpus is an *external ecological stress test* and *reference population*—an operating-envelope and model-domain coverage audit—not an independent validation of latent puck physics. Following the project’s data-use taxonomy, it supports (A) data and measurement sanity checks, (B) domain-coverage description, and (C) ecological stress testing of model outputs against a wide operating population, but **not** (D) controlled independent validation of unobserved bed state, because the records carry commanded and achieved machine channels rather than calibrated internal fields. Manuscript language for this corpus is constrained accordingly: “reference population,” “operating envelope,” “coverage audit,” and “hypothesis-generating association,” never “validation,” “ground-truth permeability,” or “proof of mechanism.” Controlled datasets remain the anchor for every gate; the population extends relevance, it does not replace an independent gate.

**Privacy posture.** Only a normalized record is retained. Directly identifying fields—contributor name, barista, free-text notes, and account identifier—are dropped at ingestion; a salted one-way hash is kept solely for de-duplication and repeated-shot cohorting. The salt is held outside version control and is not redistributed. The raw corpus is never committed and is not part of any release archive; publications draw on code and aggregates only.

**Attribution requirement.** The data-owner grant is conditional on attribution. Any publication or public artifact that uses this corpus must credit the Visualizer coffee-analytics platform as the data source and collectively acknowledge the contributing users whose shots make up the population. This requirement is recorded here as a load-bearing provenance obligation, not an optional courtesy, and is carried into the Acknowledgments and Software-and-data-availability statements of any paper that reports corpus-derived results.

**Freeze discipline.** Corpus-derived numbers are not reported in this draft. Before any paper-grade statistic, the corpus must be frozen as a named snapshot—retrieval cutoff, API and serializer version, harvester commit, and normalizer version—and its quality atlas published, exactly as §6.2–§6.5 require for every other artifact.

## 7. Demonstration 1: observable and unit linting

### 7.1 Why prose-level similarity is insufficient

The first demonstration asks what happens when a comparison aligns quantities because their labels sound similar. Four hazards are considered: saturation concentration, inventory basis, pressure node, and aggregate chemistry. Each can produce a plausible number with an invalid interpretation.

**Table 4. Observable-linting cases.**

| Hazard | Plausible but invalid operation | Contract response |
|---|---|---|
| $c_{\mathrm{sat}}=170, 212.4, 224$ kg m⁻³ | average or substitute values across model lineages | retain as per-model configuration with source and inventory convention |
| pressure called “P” | treat pump, headspace, basket, and bed-drop pressure as identical | require named pressure node and one explicit adapter |
| soluble inventory | convert total roasted chemistry directly to extractable inventory | carry basis and unknown extractable fraction; block substitution |
| named-solute mass and TDS | average mg trigonelline/caffeine/5-CQA with g TDS | require one observable, component, unit, brew ratio, and conditioning set |
| grinder dial | use the same numerical dial across grinder models | require grinder-specific calibration or PSD adapter |

### 7.2 Mixed-unit chemistry example

The Schmieder dataset reports trigonelline, caffeine, and 5-caffeoylquinic acid cup masses in milligrams and TDS mass in grams, across brew ratios and operating conditions [5]. An aggregate that averages these columns has no coherent unit. It can still produce a smooth grind response because every input varies systematically with the experiment. Smoothness does not rescue the observable.

The corrected adapter selects TDS, converts it into TDS-derived extraction yield using the nominal 20 g dose, and conditions the comparison on the intended central operating cells. The resulting raw cell means are 18.27%, 19.38%, and 19.62% at dial settings 1.4, 1.7, and 2.0. The middle-minus-coarse contrast is −0.24 extraction-yield points with a Welch 95% interval of −0.42 to −0.06. Thus the selected raw cells are ordered and do not contain a middle-setting maximum.

The study’s fitted response surface remains a different object [10]. A refit using achieved flow and temperature gives an adjusted $R^2$ of approximately 0.64 and a conditional grind vertex near 1.74. The vertex is conditional on the retained quadratic model and experimental design; it does not override the raw-cell ordering. Puckworks preserves both results with different evidence labels: observed cell comparison and fitted response-surface reconstruction.

This case illustrates the value of executable observable definitions. The correction did not merely change a unit label. It changed which scientific claim the data could support and prevented a model-capacity result from being mistaken for a feature directly present in the selected raw cells.

### 7.3 Pressure and saturation examples

The same logic applies to pressure and concentration. A Foster machine model consumes and generates several pressure nodes [2], whereas the Waszkiewicz equilibrium relation is stated in terms of basket pressure [3]. A recorded trace with unresolved node identity cannot be passed into both models without an explicit assumption. Similarly, the 170, 212.4, and 224 kg m⁻³ saturation values belong to different extraction configurations [6–9]. Puckworks reports them side by side with their inventory and dissolution conventions. It does not create a “consensus” saturation concentration from incompatible definitions.

### 7.4 A live observable-contract catch during ingestion

The preceding cases are static hazards in comparing published models. The same contract discipline also operates on live ingested data, and during this development cycle it caught an invalid result before that result reached any analysis.

The community-corpus normalizer (§6.6) enforces an observable contract on every retrieved shot: a flow or weight channel is a usable trace only if it carries a valid time base, the sample count is the number of real samples, and a missing time base is represented as missing rather than as zero (§4.6). An early version of the harvester read the per-shot time base from the wrong location in the source payload. Every retrieved record therefore arrived with plausible hydraulic channel values but no valid time base, and the contract reported `n_samples = 0` with an explicit `missing:timeframe` flag rather than silently accepting the numerically populated channels or coercing the time axis to zero.

Because the contract refused to treat “values present, no time base” as a usable trace, the entire first batch of roughly eleven thousand records was flagged unusable, discarded, and re-retrieved only after the ingestion path was corrected and covered by a contract test. Had the normalizer instead coerced the missing time base to zero, the records would have passed downstream length and range checks and produced smooth but entirely spurious flow statistics across the whole population. This is the same principle as the saturation, pressure-node, and inventory cases of Table 4—a plausible number with an invalid interpretation—operating on ingested rather than published data. It is the concrete sense in which the registry’s observable contract catches an invalid result: not by detecting an implausible value, but by refusing to let a structurally incomplete observable masquerade as a complete one.

## 8. Demonstration 2: null-first model comparison

The companion temporal-inference paper develops the scientific result [13]; here the same workflow demonstrates how the registry controls comparison semantics. A published machine-only curve is first used as a capacity null, not as evidence about a different measured apparatus. A measured 9-bar trace is then scored on one declared interval against a best constant, a static pressure-dependent model, an imported temporal trajectory, and a flexible cubic. Parameter provenance specifies which coefficients were fitted to the scored trace, elsewhere in the same campaign, or in donor studies.

On the 15–95 s interval, the best constant has RMSE 0.573 g s⁻¹, the static branch 0.648 g s⁻¹, the imported empirical temporal branch 0.116 g s⁻¹, and the four-parameter cubic 0.096 g s⁻¹. The registry attaches different interpretations to these numbers. The constant is an in-window null; the static result is a transferred equilibrium reconstruction; the temporal trajectory uses no coefficient fitted directly to the scored flow trace but imports same-campaign information; and the cubic is an in-sample flexibility bound. A moving-block calculation is labeled as an interval on fixed loss sequences, not a full model bootstrap.

Cross-pressure LOPO evaluation is similarly explicit about what is held out. The equilibrium point at each pressure is omitted from the two-parameter calibration, but the 9-bar dissolved-mass trajectory and donor assumptions remain. The label is therefore “within-campaign held out,” not “independent validation.” The mean held-out RMSEs are 0.534, 0.347, and 0.525 g s⁻¹ for the static, empirical temporal, and donor-coupled branches, respectively. Per-pressure rankings vary and residuals remain structured.

The methodological lesson is that a comparison table needs more than rows of errors. It needs the observable contract, fit/evaluation split, parameter provenance, evidence label, residual diagnostic, and scope. Without these fields, the lowest number invites an identifying claim that the analysis does not support.

## 9. Demonstration 3: more physics can worsen a reconstruction

### 9.1 The shared-porosity composition

A synthesis component combines an extraction-linked porosity-opening trajectory [3] with an imported particle-swelling trajectory [11] by assigning both to one shared porosity state. When the swelling factor is neutral, the synthesis reduces exactly to the extraction-only temporal branch. This reduction is a software verification of the composition.

Adding the imported swelling branch flattens the predicted flow. Over the same 15–95 s interval, reconstruction RMSE becomes 0.648 g s⁻¹. That is worse than the best constant baseline, approximately 0.573 g s⁻¹, and much worse than the extraction-only temporal trajectory, approximately 0.116 g s⁻¹.

### 9.2 Interpretation

The failure is preserved rather than tuned away. It shows that component validity does not imply composition validity. Each component may be internally correct with respect to its own paper, but the composition adds a new scientific assertion: that the two porosity effects act on the same state, with compatible reference volumes, geometry, timescales, and boundary conditions, and can be combined by the selected rule. That assertion needs its own evidence.

The result does **not** show that swelling is absent from espresso. It diagnoses one shared-porosity composition using one transferred swelling parameterization on one 9-bar trace. Possible failure sources include parameter transfer, fixed-height geometry, initial state, control mode, double counting of porosity, incompatible normalization, or the composition rule itself. The evidence badge is exploratory simulation and the result is negative validation of that configuration.

### 9.3 Why negative results belong in the registry

A conventional workflow may respond to this failure by adding a scale factor until the curve improves. Puckworks instead stores the unrepaired result, its configuration, and its caveat. A future alternative composition can then be compared against the failed baseline. This prevents complexity from receiving automatic evidentiary credit and allows negative results to define the boundary between reusable components and unsupported coupling assumptions.

## 10. From model disagreement to experiment design

Puckworks treats unresolved disagreement as an output. The registry identifies which observable or intervention would most efficiently separate surviving models. Table 5 summarizes current examples.

**Table 5. Disagreement-to-measurement map.**

| Ambiguity | Models or assumptions that remain compatible | Discriminating measurement |
|---|---|---|
| whole-cup extraction endpoint | inventory and kinetic rate can compensate | timed fractions or named-solute trajectories |
| dip-and-recovery flow shape | machine/headspace and evolving bed can both generate it | pressure-node-resolved machine null; inert load; first-drop timing |
| rising flow at fixed nominal pressure | dissolution opening, omitted machine effects, coupled matrix processes | pressure step plus independent bed-state measurement |
| fines migration versus local compaction | both can raise resistance in forward flow | matched-$\lvert\Delta P\rvert$ flow reversal and outlet-deposit imaging |
| dissolution opening versus stress-state evolution | both can alter late-shot permeability | spent-puck rebrew with controlled unload/rest |
| integrated outlet flow | different spatial pathways can integrate to one curve | depth-resolved porosity/fines or pathway-resolved flow |
| pressure- versus flow-control interpretation | same resistance change appears in different measured channels | matched preparation under both control modes with full node logging |
| incomplete wetting versus extraction kinetics | delayed outlet appearance can coexist with strong first liquid | per-grind first-drop timing plus saturation imaging and early fractions |

The process can be formalized:

1. enumerate configurations that remain compatible with the current observable;
2. generate intervention predictions with all unobserved assumptions exposed;
3. identify a response sign, hysteresis, spatial pattern, or timing feature on which the configurations disagree;
4. check that the measurement operator observes that feature directly;
5. rank candidate experiments by discrimination, feasibility, and required new parameters; and
6. register the proposed experiment with no evidence badge implying that data already exist.

This workflow changes the role of an executable review. It does not merely summarize what the literature has modeled. It identifies which missing measurement prevents adjudication and provides a reproducible prediction matrix for collecting it.

## 11. End-to-end named-shot evidence scorecard

### 11.1 Purpose and configuration

An end-to-end example is useful only if it exposes every weak link. The current proposed scorecard uses an illustrative configuration centered on a DE1 fixture, a nominal grinder setting of 1.7, 20 g dose, 40 g beverage, a coffee/chemistry lineage associated with the Schmieder–Pannusch data, and temperatures from 80 to 98 °C. The numerical dial label is not a portable physical coordinate; until a grinder-specific PSD adapter is supplied, the scorecard must mark the cross-grinder mapping as open rather than treat “1.7” as matched.

The scorecard is an evidentiary ledger, not a digital twin. It answers: which stage can run, where its parameters came from, what evidence supports it, what extrapolation is being made, and what measurement is still missing for this exact shot?

### 11.2 Stage-by-stage accounting

**Table 6. Draft named-shot scorecard. Statuses describe the current evidence chain, not universal model quality.**

| Stage | Selected component or input | Current evidence status | Load-bearing caveat / promotion path |
|---|---|---|---|
| Named preparation | 20 g in / 40 g out; nominal dial 1.7; 80–98 °C | specified | grinder and coffee lineage must be physically matched, not matched by dial number |
| Machine boundary | recorded DE1 fixture pressure/weight/flow | observed trace | exact pressure-node identity remains open |
| Infiltration | Foster recorded-pressure sharp-front adapter | independently gated on first-drop/dead-volume bracket for the fixture | sharp binary saturation; fine-grind/source-domain limitation |
| Packing/permeability | literature prior plus fitted fixture multiplier $\kappa\approx1.196$ | calibrated; per-shot fitted | not an independent permeability prediction; outlet/screen resistance may be absorbed |
| Flow law | Darcy baseline with Forchheimer diagnostic | verified closure; extrapolation flag | estimated $Fo_F\approx0.86$–5.7 places the fixture near or beyond inertial onset, so unflagged Darcy use is unsafe |
| Bed dynamics | selected static or temporal branch | reconstruction or exploratory, depending configuration | no direct porosity/strain measurement on the named shot |
| Aggregate extraction | Cameron-type runtime | numerically verified and source-gated | absolute EY/TDS reads low against independent literature brackets in current comparison |
| Named-solute extraction | Pannusch-type four-solute solver and flow/temperature adapter | post-fit reconstruction; adapter verification | fitted to its source campaign; no independent four-solute cup for the named fixture |
| Ramp sensitivity | pressure-to-flow adapter audit | verification; approximately 6.6% shift in the current audit | sensitivity is adapter-dependent, not an observed shot effect |
| Final exact cup | TDS plus caffeine, trigonelline, and chlorogenic-acid-family measurement | **open** | run the capstone shot, retain fractions or full cup, and predeclare whether $\kappa$ may be refitted |

The table prevents an occupied software slot from being read as an independently validated stage. For example, the extraction solver can run and pass numerical gates while its absolute prediction remains low relative to an external range. The flow closure can be dimensionally verified while the named fixture lies outside the comfortable Darcy regime. The full chain therefore ends in an open cell rather than a synthetic “predicted cup” badge.

### 11.3 Promotion experiment

The highest-value promotion is a measured named shot with full pressure-node metadata, beverage mass, TDS, caffeine, trigonelline, and chlorogenic-acid-family output, preferably with timed fractions. The protocol should predeclare whether permeability is fixed from prior calibration or refitted per shot. A result with per-shot refitting tests reconstruction; a result with a frozen permeability tests prediction. Both are useful if labeled correctly.

## 12. Discussion

### 12.1 An executable review is more than a model collection

The central object in Puckworks is not the solver but the evidence-bearing interface among source, state, observable, data, and claim. A repository that implements many models without preserving these relationships can increase, rather than reduce, scientific ambiguity. The risk grows with component count because more variables share familiar names while retaining incompatible meanings.

Puckworks addresses this by making semantic friction visible. A blocked adapter, an unknown pressure node, a missing extractability factor, or a failed composition is a legitimate output. The architecture rewards refusing an invalid merge.

### 12.2 Verification, calibration, reconstruction, and prediction

Scientific software papers often report a test suite without explaining what the tests establish. Puckworks separates software verification from empirical evidence. Conservation, convergence, source-curve reproduction, and independent validation can all be automated, but they answer different questions. The evidence taxonomy should accompany every benchmark table and public claim.

This separation also clarifies model reuse. A component verified against its source equations may be safe to use in a sensitivity analysis while remaining unsuitable for an absolute prediction. A calibrated component may be appropriate within one campaign but require a new calibration on another rig. A negative external result can coexist with correct implementation.

### 12.3 Composition creates a new model

The failed extraction-plus-swelling demonstration illustrates a general principle. Connecting two validated components creates a new model with new state-identification, normalization, and coupling assumptions. Those assumptions require reduction tests, conservation checks, sensitivity analysis, and empirical evidence. Validation does not compose automatically.

This point is especially important for multiphysics repositories. A “more complete” configuration can double count a state change, mix reference volumes, or violate a boundary condition while producing a smooth output. Simple baselines and exact reduction limits should remain visible in every composition study.

### 12.4 Generalization beyond espresso

The architecture applies to other domains in which heterogeneous literature models are assembled around shared process stages: drying, filtration, chromatography, fermentation, reactive transport, battery porous electrodes, and biomedical perfusion. The transferable practices are:

- represent model roles and stages explicitly;
- define observable and state semantics before comparison;
- retain source and parameter provenance at field level;
- use evidence labels that constrain verbs;
- generate claims from executable producers;
- treat negative results and blocked compositions as first-class records; and
- convert model disagreement into a measurement recommendation.

The domain-specific contract fields will differ, but the evidence problem is the same.

## 13. Limitations and submission readiness

### 13.1 Scientific and corpus limitations

The corpus is not systematic and may omit relevant models, datasets, or non-English literature. Model maturity is uneven: some components have independent data, some only source reproduction, and some are exploratory project syntheses. The registry is concentrated on espresso-relevant conditions and cannot be assumed to represent all coffee extraction or packed-bed regimes.

The typed contracts are semantic Python dataclasses rather than a formal unit/ontology system. Several adapters remain embedded in harnesses. The stage taxonomy does not yet capture every observational role as a first-class component. Evidence labels are curated and require reviewer judgment; they reduce ambiguity but cannot remove it.

The demonstrations are selected cases, not a quantitative estimate of how frequently semantic errors occur in the literature. The named-shot scorecard is illustrative and contains open lineage and pressure-node issues. It should not be presented as a validated end-to-end prediction.

### 13.2 Software/resource readiness table

**Table 7. Current state versus submission requirement.**

| Area | Present in current snapshot | Required before journal submission |
|---|---|---|
| Installation | editable-install quickstart in README | tested clean installation on supported Python versions; packaged release |
| Public API | component registry and schema version 0.6 | documented stable API, semantic versioning, deprecation policy |
| Tutorials | onboarding and internal workflows referenced | public tutorials that run without private or local-only files |
| Add-a-model path | README steps and card template | complete contributor tutorial with example PR and validation checklist |
| Roles/schema | runtime, calibration, synthesis in use | first-class adapter/diagnostic roles; resolve `kind` vocabulary inconsistency |
| Tests | gates and test suite; quick and slow analyses exist | CI-separated quick tests and archived slow scientific benchmarks |
| Data provenance | 70-row manifest snapshot with licenses/caveats | release-frozen manifest; audit every redistributable artifact and license |
| Claims | producer-backed public-claim schema | manuscript claim bundle regenerated in CI with source-data exports |
| Release tooling | environment check, external staging, checksums, manifest checks | clean tagged archive, full dependency lock or container digest, DOI |
| Corpus method | curated cards and related-work notes | indexed search protocol, screening record, inclusion/exclusion appendix |
| External use | not established in this draft | at least one documented external reproduction or user workflow |
| Governance | roadmap and runbook | contribution guide, issue templates, changelog, code of conduct as appropriate |

The paper should be submitted as a resource/methods article only after the release artifact satisfies the same strict checks the manuscript describes. A software-journal route additionally requires evidence that the tool is feature-complete for its stated purpose, documented, tested, openly developed, and usable by contributors outside the originating team.

## 14. Conclusions

Puckworks addresses a problem that appears whenever heterogeneous process models are made executable together: similarly named quantities, parameters, and validation claims are not necessarily compatible. The registry represents models as provenance-tracked stage components, exchanges state through versioned contracts, records dataset transformations in a manifest, labels evidence at the claim level, and requires manuscript numbers to be regenerated by named producers.

The demonstrations show why these controls matter. Observable linting prevents incompatible concentration, pressure, inventory, grinder, and chemistry quantities from being silently merged. Null-first comparison distinguishes machine capacity, static inadequacy, temporal reconstruction, flexible in-sample fit, and conditional held-out assessment. A failed extraction-plus-swelling composition shows that adding mechanisms can worsen a result and that validation does not automatically transfer through composition. The named-shot scorecard then exposes the exact stages that are observed, calibrated, verified, reconstructed, extrapolated, or open.

The broader contribution is a pattern for executable reviews: preserve meaning at interfaces, preserve evidence strength in language, preserve negative results, and make the next discriminating experiment part of the output. Puckworks should not be judged by the number of models it can run, but by whether it prevents an invalid comparison from looking scientifically complete.

## Software and data availability

Puckworks is hosted at <https://github.com/trbrewer/puckworks>. The final manuscript should cite a versioned archival release and DOI rather than only the moving repository URL. The cited archive should include source cards, data manifest, component registry, contracts, tests, generated result bundles, figure source data, environment metadata, release provenance, and checksums.

Source datasets retain their original licenses and access conditions, which are recorded per manifest row. Files that cannot be redistributed should be represented by retrieval instructions, hashes or derived summaries where permitted, and gates that fail clearly when the source is absent. The final release should include one complete example that runs without private files.

The external community corpus (§6.6) is retrieved under a research-use grant, is not redistributed, and is represented only by code and privacy-preserving aggregate summaries; the raw records are never included in any archive. Any reported corpus statistic must carry the attribution required by that grant (see Acknowledgments).

## Author contributions

[To be completed using the target journal’s contribution taxonomy.]

## Funding

[To be completed.]

## Competing interests

[To be completed.]

## Acknowledgments

[To be completed.] **Required, not optional:** any version of this paper that reports results derived from the external community corpus (§6.6) must credit the Visualizer coffee-analytics platform as the data source and collectively acknowledge the contributing users whose shots constitute the reference population, per the data-owner research-use grant.

## Figure specifications and draft captions

### Figure 1. Puckworks architecture

A directed graph from source paper and source artifact to model/source card, dataset manifest, registered component, typed contract, configuration, gate/harness, generated result bundle, claim producer, figure/source-data export, and archived release. Process stages appear as a second horizontal layer. Arrows distinguish data provenance, runtime state, calibration, and evidence. Caption: Puckworks is a registry and evidence system; a configuration selects components and adapters rather than instantiating every model.

### Figure 2. Process-stage and evidence map

**Panel a:** Current component counts by stage and role. **Panel b:** evidence taxonomy showing that verification, reconstruction, held-out prediction, independent evidence, capacity, sign tests, and exploratory synthesis are different dimensions, not one undifferentiated validation score. **Panel c:** a small component card showing source, assumptions, valid range, gates, and caveats.

### Figure 3. Observable and unit linting

**Panel a:** incompatible $c_{\mathrm{sat}}$ and inventory conventions retained as separate configurations. **Panel b:** pressure-node diagram for pump outlet, headspace, basket, and bed drop. **Panel c:** invalid mixed-unit chemistry aggregation crossed out; corrected TDS-derived extraction yield shown with raw replicate cells. **Panel d:** raw-cell ordering and separately labeled conditional response-surface vertex. The caption states that the fitted vertex is not present as a maximum in the selected raw cells.

### Figure 4. Null-first comparison as a registry workflow

A ladder from machine-only capacity to constant/static null, imported temporal candidate, flexible temporal null, held-out pressure assessment, sign test, and proposed intervention. Each rung carries parameter provenance and evidence label. Scientific details are cited to the companion temporal paper; the figure emphasizes comparison architecture.

### Figure 5. Negative composition result

**Panel a:** component graph for extraction-linked opening and swelling sharing porosity. **Panel b:** exact reduction to the extraction-only branch when swelling is neutral. **Panel c:** measured trace and predictions showing the combined branch flattening. **Panel d:** RMSE comparison: extraction-only approximately 0.116, best constant approximately 0.573, composite approximately 0.648 g s⁻¹. Caption: the result diagnoses this composition, not the existence of swelling.

### Figure 6. Disagreement-to-experiment map

Matrix connecting unresolved comparisons to timed fractions, first-drop timing, pressure steps, reversal, rebrew, control mode, and spatial end states. Each recommendation links back to the model card that supplies the directional prediction.

### Figure 7. Named-shot evidence scorecard

A stage-by-stage horizontal chain for the illustrative 20 g/40 g configuration. Every block is labeled observed, calibrated, verified, reconstructed, extrapolated, or open. Open pressure-node identity, grinder adapter, inertial-flow flag, low absolute extraction prediction, and absent exact four-solute cup are visibly retained. The final block is “measurement required,” not a synthetic cup prediction.

## Supplementary material plan

- **Supplement S1:** Corpus-search protocol and screening form; completed flow diagram when available.
- **Supplement S2:** Full component inventory generated from the frozen registry, with stage, role, source, assumptions, validity range, and gates.
- **Supplement S3:** Complete dataset manifest and data dictionary.
- **Supplement S4:** Contract schema, version history, field-level units, missing-data behavior, and adapter ledger.
- **Supplement S5:** Evidence-label decision guide with worked examples and allowed manuscript verbs.
- **Supplement S6:** Observable-linting notebooks/tests for saturation concentration, pressure nodes, inventory basis, chemistry units, and grinder mapping.
- **Supplement S7:** Null-first demonstration configuration and source-data export; science cross-referenced to the companion paper.
- **Supplement S8:** Shared-porosity composition reduction test and negative-result bundle.
- **Supplement S9:** Named-shot machine-readable scorecard and promotion-experiment protocol.
- **Supplement S10:** Clean-build release manifest, environment lock, archive hashes, and independent reproduction report.

## Appendix A. Current component snapshot

The current source snapshot contains the following registered identifiers. The release version should generate this table automatically rather than maintain it by hand.

| Stage | Role | Component identifier |
|---|---|---|
| Extraction | runtime | `cameron2020.extraction_bdf` |
| Bed dynamics | runtime | `brewer2026.streamtube` |
| Packing | calibration | `brewer2026.pack_generator` |
| Flow | calibration | `brewer2026.lb_reference` |
| Flow | calibration | `brewer2026.lb_taichi` |
| Packing | calibration | `wadsworth2026.permeability` |
| Extraction | runtime | `pannusch2024.solver` |
| Extraction | calibration | `pannusch2024.closures` |
| Extraction | runtime | `grudeva2025.reduced` |
| Extraction | calibration | `liang2021.desorption` |
| Extraction | calibration | `moroney2016.surrogate` |
| Bed dynamics | synthesis | `brewer2026.coupled_kappa_t` |
| Bed dynamics | calibration | `fasano2000_partI.fines_migration` |
| Extraction | runtime | `mo2023_2.coupled_bed` |
| Bed dynamics | runtime | `mo2023_2.swelling` |
| Extraction | runtime | `romancorrochano2017.extraction` |
| Flow | calibration | `lee2023.feedback` |
| Flow | runtime | `wadsworth2026.inertial` |
| Grind | calibration | `wadsworth2026.grindmap` |
| Bed dynamics | runtime | `waszkiewicz2025.poroelastic` |
| Machine | runtime | `foster2025.machine_mode` |
| Infiltration | runtime | `foster2025.infiltration` |
| Infiltration | calibration | `sourcing2026.g1_glassbead_analog` |
| Machine | calibration | `sourcing2026.g3_pump_characteristic` |
| Flow | calibration | `sourcing2026.g10_liquor_rheology` |

## Appendix B. Minimal machine-readable claim record

A manuscript-facing quantitative claim should be exportable in a structure equivalent to:

```yaml
claim_id: stable identifier
question: scientific question
result:
  value_name: generated numeric value
units:
  value_name: physical unit
producer:
  module: executable module
  function: generating function
  result_path: location in returned result
components: [registered component identifiers]
datasets: [manifest identifiers]
evidence_strength: named taxonomy value
badge: observed | reconstructed | predicted | exploratory simulation
validity_range: explicit domain
caveat: primary limitation
reproduction: one-line command or workflow target
source_commit: filled at export
```

The exact serialization may change, but every field is load-bearing. A graphic or abstract number without this record should be treated as untracked.

## References

1. Puckworks contributors. *Puckworks: a component registry for espresso process models*. Software repository. <https://github.com/trbrewer/puckworks>. [Version, archive DOI, and access date to be inserted for submission.]
2. Foster J, Lee W, Moroney K, Prjamkov D, Salamon M, Smith A, Petrassem-de-Sousa J, Vynnycky M. Dynamics of liquid infiltration into an espresso bed using time-resolved micro-computed tomography: insights from experiment and modeling. *Physics of Fluids*. 2025;37:013383. doi:10.1063/5.0245167.
3. Waszkiewicz P, Myck M, Białas K, Puciata-Mroczynska A, Dzikowski M, Szymczak P, Lisicki M. Under pressure: poroelastic regulation of flow in espresso brewing. *Physics of Fluids*. 2026;38:063113. doi:10.1063/5.0319611.
4. Fasano A, Talamucci F, Petracco M. The espresso coffee problem. In: Fasano A, editor. *Complex Flows in Industrial Processes*. Boston: Birkhäuser/Springer; 2000. p. 241–280.
5. Schmieder B, Pannusch S, Vannieuwenhuyse L, Briesen H, Minceva M. Influence of flow rate, particle size, and temperature on espresso extraction kinetics. *Foods*. 2023;12:2871. doi:10.3390/foods12152871.
6. Cameron MI, Morisco D, Hofstetter D, Uman E, Wilkinson J, Kennedy Z, Fontenot H, Lee TC, Hendon CH, Foster JM. Systematically improving espresso: insights from mathematical modeling and experiment. *Matter*. 2020;2:631–648. doi:10.1016/j.matt.2019.12.019.
7. Moroney KM, Lee WT, O’Brien SBG, Suijver F, Marra J. Asymptotic analysis of the dominant mechanisms in the coffee extraction process. *SIAM Journal on Applied Mathematics*. 2016;76(6):2196–2217. doi:10.1137/15M1036658.
8. Grudeva Y, Moroney KM, Foster JM. A multiscale model for espresso brewing: asymptotic analysis and numerical simulation. *European Journal of Applied Mathematics*. 2026;37:496–519. doi:10.1017/S095679252500018X.
9. Lee WT, Smith A, Arshad M. Uneven extraction in coffee brewing. *Physics of Fluids*. 2023;35:054110. doi:10.1063/5.0138998.
10. Pannusch VB, Schmieder BKL, Vannieuwenhuyse L, Minceva M, Briesen H. Model-based kinetic espresso brewing control chart for representative taste components. *Journal of Food Engineering*. 2024;367:111887. doi:10.1016/j.jfoodeng.2023.111887.
11. Mo J, Navarini L, Suggi Liverani F, Ellero M. Modelling swelling effects in real espresso extraction using a 1-dimensional coarse-grained model. *Journal of Food Engineering*. 2024;365:111843. doi:10.1016/j.jfoodeng.2023.111843.
12. Liang J, Chan KC, Ristenpart WD. An equilibrium desorption model for the strength and extraction yield of full immersion brewed coffee. *Scientific Reports*. 2021;11:6904. doi:10.1038/s41598-021-85787-1.
13. [Authors]. One flow curve, many causes: null-first inference for machine and porous-bed dynamics in espresso. Companion manuscript in preparation.

## Repository provenance used to develop this draft

The draft draws on `PAPER_3_PUCKWORKS_OUTLINE.md`, `README.md`, `contracts.py`, `registry.py`, the component registrations, model/source cards, `MANIFEST.csv`, the evidence matrix and dictionary, public claim schema and seeded claims, the release runbook, the publication strategy review, claim-ownership map, and the temporal, response-surface, composition, and named-shot analyses recorded in the repository. Internal paths are retained here for drafting provenance; the submitted paper should replace moving paths with a frozen archive citation and supplement index.
