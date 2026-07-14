# PUBLICATION_STRATEGY_REVIEW

**Strategic review of the Puckworks publication portfolio**  
**Prepared:** July 14, 2026

---

## Executive decision

The current two-paper plan is close to the right publication strategy, but it does not yet organize the Puckworks work into the strongest possible scholarly portfolio.

The recommended near-term portfolio is:

| Publication | Recommendation | Central contribution |
|---|---|---|
| **Paper 1 — The Cup Hides the Clock** | Complete, tighten, and submit | Whole-cup observations can confound extractable inventory with kinetic rate; fractions and orthogonal measurements restore information |
| **Paper 2 — One Flow Curve, Many Causes** | Rebuild from the strongest portion of the current Paper B | A flow trace can require time dependence without uniquely identifying a bed mechanism; perturbations discriminate better than one unperturbed trace |
| **Paper 3 — Puckworks executable review/resource** | Develop as a distinct methods/software publication | A provenance-aware component registry can prevent invalid observable merges, compare competing model lineages, preserve negative results, and convert disagreement into experiment design |
| **Future Paper 4 — Spatial concentration and control mode** | Defer until the physics and data are stronger | Physical lateral coupling, control-mode dependence, spatial measurement, and genuine stability/convergence analysis |

The preferred answer to the paper-count question is therefore:

> **Three near-term publications is the strongest portfolio. One paper would be too broad; the current two are not quite the right two; four or more papers from the existing evidence would be premature.**

The most important strategic actions are:

1. **Complete Paper A now, under a strict scope freeze.**
2. **Do not complete the present broad Paper B merely because it is already drafted.**
3. **Fork Paper B now into a focused temporal-inference paper and a methods/resource-paper evidence set.**
4. **Preserve the N-tube work as a future physics program rather than forcing it into the current manuscript.**
5. **Treat Puckworks itself as a scholarly contribution rather than only as supporting code.**

The guiding principle should be:

> **Preserve all analyses, but publish each claim in the paper where it has the clearest scientific question, strongest evidence chain, and correct audience.**

---

# 1. Portfolio-level assessment

## 1.1 The project has three distinct scholarly contributions

The repository currently contains three contributions that are related but should not be forced into one narrative:

### A. Observation design and practical identifiability

The strongest current scientific result is that a matched whole-cup endpoint can be reconstructed while leaving extractable inventory and kinetic rate poorly separated. Fraction-resolved observations and orthogonal inventory information restore useful parameter information.

This is the core of Paper A.

### B. Dynamic system identification from flow traces

The strongest current Paper B result is that an observed flow trace may require temporal flexibility relative to specified static nulls, while still failing to distinguish among multiple underlying physical mechanisms. Controlled perturbations are more informative than additional fitting of the same unperturbed trace.

This should become the core of a narrower Paper B.

### C. Executable evidence management

Puckworks is not merely a set of scripts supporting two papers. It is an emerging executable review and evidence system with:

- stage-specific model components;
- typed data and state contracts;
- explicit unit and observable conventions;
- model cards and source provenance;
- evidence classifications;
- matched-observable comparison;
- null-model ladders;
- recorded negative results;
- claim bundles and reproducibility manifests; and
- experiment recommendations generated from model disagreement.

Neither current paper adequately communicates this contribution.

The repository explicitly frames itself as a component registry rather than a single “mega-model,” and it contains a substantial set of registered model components and source-card lineages. That is a legitimate methods and research-infrastructure contribution if presented with appropriate evidence-tier distinctions and a clean release.

Relevant repository resources include:

- [README](https://github.com/trbrewer/puckworks/blob/main/README.md)
- [ROADMAP](https://github.com/trbrewer/puckworks/blob/main/docs/ROADMAP.md)
- [PUBLIC_VALUE](https://github.com/trbrewer/puckworks/blob/main/docs/PUBLIC_VALUE.md)
- [PAPER_OUTLINE](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_OUTLINE.md)
- [SUBMISSION_TARGETS](https://github.com/trbrewer/puckworks/blob/main/docs/SUBMISSION_TARGETS.md)

---

## 1.2 The shared intellectual theme is real, but not sufficient for one paper

Papers A and B share a broad lesson:

> Integrated observations can be accurately reconstructed while remaining weakly discriminating about hidden mechanisms or parameters.

That lesson is scientifically valuable. It is not, however, enough to make the current full scope of both papers one coherent manuscript.

Paper A centers on:

- chemical extraction observables;
- inventory-rate compensation;
- practical identifiability;
- endpoint versus temporal fractions;
- orthogonal constraints; and
- prediction relative to a simple baseline.

The strongest part of Paper B centers on:

- machine and bed dynamics;
- temporal model comparison;
- static versus time-varying closures;
- pressure transfer;
- sign constraints; and
- discriminating perturbations.

These papers have different observables, mathematical questions, data structures, validation standards, and likely reviewers. Combining them would create a long collection of case studies rather than a focused argument.

---

## 1.3 The current two-paper split also leaves a central contribution unpublished

The existing “two papers plus possible methods note” strategy was operationally sensible early in the project. The project has now accumulated enough architecture, model curation, provenance work, observable-contract corrections, and evidence-governance methodology that the methods contribution should no longer be treated as an optional note.

The repository’s most distinctive feature may ultimately be that it provides an executable system for asking:

- Are two models referring to the same physical quantity?
- Are their units and state definitions compatible?
- Is a result a verification, reconstruction, prediction, capacity demonstration, or exploratory synthesis?
- Does a more complex model outperform a simple null?
- Which observation would distinguish the surviving explanations?
- Can a claim be regenerated from a pinned artifact rather than copied from a notebook?

That contribution is not fully owned by either Paper A or Paper B.

---

# 2. Paper A assessment

## 2.1 Strategic verdict

**Paper A is fundamentally the correct paper and is publication-worthy.**

It should be completed and submitted, but its center of gravity must remain:

> **observation resolution, practical identifiability, and experimental design**

rather than:

> **successful mechanistic transfer across grind conditions**

The current transfer results are useful, but mainly because they reveal how low absolute error can coexist with weak incremental skill relative to a simple level-only baseline.

---

## 2.2 The scientific question is strong and generalizable

Paper A asks:

> What can a final-cup measurement actually tell us about the amount of extractable material and the rate at which it was released?

This is broader than espresso. It is an applied inverse-problem result relevant to food processing, reaction engineering, transport, pharmacokinetics, and any system in which a time-integrated observation is used to infer latent inventory and rate parameters.

The paper’s strongest evidence chain is:

1. **Matched whole-cup profile:**  
   The inventory-rate objective has an interior numerical minimum but a broad near-optimal region, with the rate extent reaching the tested upper domain boundary.

2. **Objective cross-check:**  
   The compensation appears under both the formal SSE analysis and the predictive MAPE view, once the implementations are correctly separated.

3. **Temporal-resolution result:**  
   Fraction-resolved observations localize the rate much more strongly than the corresponding aggregate.

4. **Same-model exact-cup control:**  
   A controlled simulation separates information loss caused by aggregation from information loss caused by missing intermediate experimental data.

5. **Orthogonal constraint:**  
   A same-campaign inventory measurement narrows the admissible rate range.

6. **Prediction-versus-null comparison:**  
   The mechanistic cross-grind prediction has low absolute MAPE but only a small advantage over an O-trained level-only constant.

These are not disconnected sensitivity analyses. Together they support one publishable conclusion:

> **Good endpoint reconstruction does not imply parameter localization, and parameter localization depends strongly on the observation operator.**

The profile-analysis framing should remain consistent with the practical-identifiability literature. In particular:

- an interior numerical optimum is not the same as a well-localized parameter;
- a profile reaching the tested domain boundary is domain-censored;
- an arbitrary objective-tolerance set is not automatically a confidence interval; and
- prediction ranges propagated over a tolerance set should not be called statistical intervals unless they have a calibrated probabilistic interpretation.

A useful methodological reference is:

- Raue et al., “Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood,” *Bioinformatics* 25(15), 1923–1929.  
  [Article](https://academic.oup.com/bioinformatics/article/25/15/1923/213246)

---

## 2.3 Why Paper A remains interesting despite the apparent simplicity of the confounding

A likely reviewer reaction is:

> Of course an amount parameter can compensate for a rate parameter in an integrated measurement.

Paper A should anticipate that objection with a compact analytical explanation rather than with additional empirical complexity.

A useful conceptual approximation is:

\[
C_{\mathrm{cup},j} \approx I_j\,F_j(k;x),
\]

where:

- \(C_{\mathrm{cup},j}\) is the final-cup concentration or extracted amount for solute \(j\);
- \(I_j\) is the available extractable inventory;
- \(F_j\) is the extracted fraction;
- \(k\) is the kinetic-rate scale; and
- \(x\) denotes the operating conditions and observation endpoint.

For a single integrated endpoint, changes in \(F_j(k;x)\) can often be absorbed by changes in \(I_j\). Temporal fractions instead observe the shape of \(F_j(t)\), which a single multiplicative inventory adjustment cannot generally reproduce.

That short derivation would transform the paper from:

> “A numerical profile happened to be flat”

into:

> “The observation operator creates a predictable confounding structure; the real-data and same-model results show its practical consequences; and the proposed measurements break it.”

---

## 2.4 The transfer result should be retained, but reframed

The current cross-grind result is scientifically useful because it separates absolute predictive error from mechanistic value.

The retained diagnostic indicates approximately:

- mechanistic C/F macro-MAPE: **8.23%**;
- O-trained level-only baseline: **8.59%**;
- apparent advantage: **0.36 percentage points**;
- mechanistic model worse than the constant in **5 of 12** variety × solute × held-out-grind summaries, and approximately **50 of 108** held-out points in the fuller accounting.

The exact differences should be regenerated from full-precision point predictions, but the strategic implication is already clear:

> The paper should not use low absolute MAPE alone as evidence that the mechanistic rate structure transfers across grind.

Instead, the transfer result should be described as:

- modest absolute endpoint error;
- deterministic variation across a declared near-optimal set;
- limited incremental skill over a level-only null; and
- evidence that good aggregate predictions can persist despite weak parameter localization.

This actually strengthens the paper’s main thesis.

---

## 2.5 What Paper A should not claim

Paper A should not be presented as:

- universal validation of the source extraction mechanism;
- identification of a universal kinetic rate;
- robust mechanistic transfer across grinders or grind conditions;
- proof that whole-cup observations never contain rate information;
- evidence that the source model is intrinsically wrong; or
- a conventional confidence-interval analysis unless a likelihood and calibrated threshold are established.

The correct claim is conditional:

> Under the tested model, datasets, objective functions, parameter domains, and matched whole-cup observation operator, inventory and rate are weakly separated; additional temporal or orthogonal measurements increase information.

---

## 2.6 Recommended Paper A title and positioning

Recommended title:

> **The cup hides the clock: observation resolution governs practical identifiability in espresso extraction**

Possible subtitle:

> **A multi-solute case study in endpoint aggregation and experimental design**

The phrase “cross-dataset case study” is accurate but not the strongest lead. The general observation-design result should appear first.

Likely venue positioning:

- food-process modeling;
- food engineering;
- chemometrics;
- applied inverse problems;
- transport-informed experimental design.

The repository’s submission analysis appropriately favors venues such as *Journal of Food Engineering* when the paper is framed as identifiability and observation design rather than as an espresso-specific curve fit.

---

## 2.7 Recommended Paper A structure

### Introduction

1. Integrated measurements are common and convenient.
2. Endpoint agreement can mask weak parameter identifiability.
3. Espresso extraction provides a useful multi-solute, transport-limited case.
4. The paper asks which measurements distinguish inventory from rate.

### Minimal theory

1. Define the observation operator.
2. Show the approximate inventory × extracted-fraction factorization.
3. Explain why temporal fractions contain shape information.
4. Distinguish parameter localization from predictive stability.

### Data and methods

1. Source datasets and evidence classifications.
2. Matched endpoint conventions.
3. Profile construction and tested parameter domains.
4. Objective functions.
5. Cross-grind transfer and level-only baseline.
6. Orthogonal inventory measurement.
7. Descriptive leave-one-condition-out sensitivity.
8. Reproducibility and source-data contracts.

### Results

1. Matched whole-cup compensation profile.
2. Fraction-versus-aggregate localization.
3. Same-model exact-cup information-loss control.
4. Orthogonal inventory constraint.
5. Prediction ranges and null-relative transfer.
6. Limited external temporal-shape sensitivity, preferably supplementary.

### Discussion

1. Endpoint fit, identifiability, prediction, and null-relative skill are different.
2. The observation operator is part of the scientific model.
3. What measurement would most efficiently break the confounding?
4. Limits of the present datasets and approximations.
5. General implications for food-process inference.

---

## 2.8 Recommended Paper A figure set

The paper currently contains more figures than the core argument needs. A stronger main text would use approximately four or five figures.

### Main Figure 1 — Observation map and study design

Show:

- time-resolved fractions;
- integrated final cup;
- inventory parameter;
- kinetic-rate parameter; and
- orthogonal inventory information.

Purpose:

> Make the inferential problem visually obvious before presenting any objective surface.

### Main Figure 2 — Inventory-rate profile

Show:

- the objective surface;
- profiled objective;
- tested parameter domain;
- upper-bound censoring; and
- clearly separated SSE and MAPE analyses.

Purpose:

> Establish weak practical localization under the whole-cup observation.

### Main Figure 3 — Information restoration

Show:

- fraction-resolved profile;
- aggregate profile;
- same-model exact-cup result; and
- a common normalization or declared threshold.

Purpose:

> Demonstrate that observation resolution, not merely model mismatch, drives the information loss.

### Main Figure 4 — Orthogonal inventory information

Show:

- beverage-only admissible profile;
- same-campaign inventory constraint;
- resulting conditional rate range; and
- clear statement that the inventory tolerance is assumed rather than measured unless a measured uncertainty is available.

Purpose:

> Show how a different measurement type breaks the compensation.

### Main Figure 5 — Prediction and null comparison

Show together:

- held-out predictions or errors;
- deterministic range across the declared tolerance set;
- level-only baseline; and
- pointwise or grouped win/loss comparison.

Purpose:

> Prevent low absolute error from being mistaken for strong mechanistic evidence.

### Supplementary material

Move to the supplement:

- detailed endpoint-volume sensitivity;
- geometry sensitivity;
- seed-level simulation diagnostics;
- residual plots;
- alternative objective thresholds;
- external Waszkiewicz alignment profiles;
- expanded leave-one-condition-out results; and
- secondary comparator ladders.

---

## 2.9 Paper A completion criteria

Paper A should be considered submission-ready only when the following are complete:

### Scientific

- The central claim is stated as practical identifiability under a declared observation operator.
- The primary named-solute convention is used consistently.
- Proxy/TDS results are separated and labelled as sensitivities.
- The transfer result includes a level-only null.
- The finite tolerance-grid ranges are not called confidence intervals.
- The upper-domain censoring is explicit.
- The Table 7 inventory result is described as a conditional constraint, not an independently estimated uncertainty interval.

### Numerical

- Full-precision point predictions are exported.
- Profile results are checked for rate-grid, domain, and threshold sensitivity.
- Endpoint sensitivity reruns the complete calibration-and-transfer estimand, not only a blind residual calculation.
- Rounded intermediate values are eliminated from manuscript summaries.
- The Waszkiewicz observation operator enforces physically nonnegative collection masses through a defensible monotone or nonnegative-flow reconstruction.

### Reproducibility

- One clean command recomputes the manuscript-facing results.
- The result bundle, figures, source data, manuscript, and manifest refer to the same clean commit.
- Every figure has complete source-data export.
- Strict verification fails when the worktree is dirty or artifacts are stale.
- A tagged release and archive DOI are created.

### Manuscript

- Internal review identifiers and task-ledger language are removed.
- Methods are written as scientific procedures and equations, not function names.
- Captions are self-contained.
- References and declarations are complete.
- The abstract leads with the observation-design result.

---

# 3. Paper B assessment

## 3.1 Strategic verdict

The current Paper B contains a publication-worthy paper, but it is not yet organized as the strongest possible publication unit.

The present draft combines:

1. a grind-response/RSM and static-heterogeneity audit;
2. temporal inference from machine and flow traces; and
3. exploratory N-tube flow concentration.

These three streams are related at a high level, but they have different:

- data sources;
- observables;
- model classes;
- standards of proof;
- maturity levels; and
- target audiences.

The strongest scientific paper lies in the temporal-inference stream.

---

## 3.2 Result 1: useful audit, weak headline for a physics paper

The corrected Schmieder analysis is valuable and should be preserved.

The achieved-predictor response surface has a conditional interior vertex near grinder dial 1.74, but:

- the raw central-condition endpoint values do not show a simple strong inverted-U pattern;
- grinder dial is not a universal physical particle-size coordinate;
- cup outcomes are reconstructed from fraction-resolved kinetics rather than direct whole-cup endpoint measurements;
- within-setting variability is heterogeneous;
- the confidence range is conditional on the chosen polynomial form; and
- static heterogeneity demonstrates model capacity, not mechanism identification.

The important scholarly lessons are:

- fitted surfaces should be checked against raw observations;
- target and achieved operating variables are not interchangeable;
- units and observable definitions are part of the scientific model;
- a model’s ability to produce a feature does not identify that model as the cause; and
- corrections should be preserved as part of the evidence record.

These are especially strong as methods/resource-paper demonstrations.

The source study should be represented accurately:

- 15 experimental settings;
- generally three extraction repetitions per setting;
- six repetitions at the center;
- ten consecutive fractions; and
- response-surface analysis based on set grind plus achieved flow and temperature.

Primary source:

- Schmieder et al., *Foods* 12(15), 2871.  
  [Article](https://www.mdpi.com/2304-8158/12/15/2871)

---

## 3.3 Result 2: the real Paper B

The strongest and most coherent Paper B question is:

> What can an integrated flow trace establish about machine and porous-bed dynamics, and what remains unidentifiable without perturbation?

The existing evidence supports a clear null-first sequence:

1. **Machine-only demonstration**  
   A dip-and-recovery curve can arise without changing bed properties. Therefore, curve shape alone is not diagnostic of bed evolution.

2. **Static nulls on the rising-flow trace**  
   Constant and static closures fail to reproduce the temporal behavior adequately.

3. **Time-varying branch**  
   A time-varying porosity or permeability trajectory substantially improves reconstruction.

4. **Flexible empirical temporal null**  
   A cubic or other non-mechanistic temporal curve can perform similarly over some scoring windows.

5. **Inference limit**  
   The trace supports temporal flexibility relative to the specified static nulls, but does not uniquely identify a physical mechanism.

6. **Sign constraints**  
   Isolated resistance-increasing swelling or fines branches have the wrong sign for a rising-flow contribution under imposed fixed pressure.

7. **Cross-pressure analysis**  
   Leave-one-pressure-out behavior can test whether the equilibrium calibration is dominated by one pressure and can reveal residual fingerprints across the campaign.

8. **Discriminating intervention**  
   Pressure steps, reversals, spent-puck rebrew, and spatial end-state measurements make different predictions across the surviving mechanisms.

This is a strong systems-identification paper because it distinguishes:

- reconstruction;
- necessity relative to declared nulls;
- mechanism uniqueness;
- cross-condition stability; and
- experiment design.

The most valuable positive contribution is not “the curve is ambiguous.” It is:

> **A disciplined inference ladder can determine what one curve rules out, what it supports, what remains unresolved, and which intervention would resolve it.**

Relevant repository resource:

- [PROTOCOL_kappa_t_discrimination.md](https://github.com/trbrewer/puckworks/blob/main/docs/PROTOCOL_kappa_t_discrimination.md)

---

## 3.4 The temporal comparison must remain conditional

The time-resampling result should not be described as a bootstrap of the full model-comparison procedure unless the models are refitted inside each resample.

If the procedure resamples blocks from already-computed squared-loss sequences, it is more accurately:

> a conditional, fixed-prediction block resampling of loss differences.

That distinction matters because it does not propagate:

- model-fitting uncertainty;
- parameter-selection uncertainty;
- temporal-model form uncertainty; or
- preprocessing uncertainty.

A central range crossing zero means the comparison is not resolved under that procedure. It does not establish equivalence or statistical indistinguishability.

The ordering’s sensitivity to the scoring window is scientifically important. It means the appropriate claim is:

> Time variation is supported relative to the tested static baselines, but the available trace does not robustly select one temporal representation across reasonable scoring choices.

Block-resampling interpretation should be cautious when one structured, phase-varying trace is treated with methods developed for dependent stationary observations.

Reference:

- Künsch, “The Jackknife and the Bootstrap for General Stationary Observations,” *Annals of Statistics* 17(3).  
  [Article](https://projecteuclid.org/journals/annals-of-statistics/volume-17/issue-3/The-Jackknife-and-the-Bootstrap-for-General-Stationary-Observations/10.1214/aos/1176347265.full)

---

## 3.5 Cross-pressure evidence is useful but limited

Displaying genuine leave-one-pressure-out results is a major improvement.

The evidence can support:

- within-campaign stability of the equilibrium calibration;
- pressure-specific residual fingerprints;
- identification of pressures at which particular branches fail; and
- prioritization of pressure perturbations.

It does not by itself establish:

- a universal pressure law;
- independent external validation;
- uniqueness of the temporal mechanism; or
- transfer to a different machine, coffee, basket, dose, or preparation protocol.

The language should remain:

> within-campaign held-out pressure assessment

rather than:

> independent external prediction.

---

## 3.6 Result 3: N-tube concentration is not yet a journal-level physics result

The N-tube model is useful as a hypothesis generator. It shows that a particular constructed system can exhibit strong pathway concentration under some combinations of:

- near-choke nonlinearity;
- fixed-total-flow control;
- weak or absent homogenizing exchange;
- chosen initial heterogeneity;
- selected closure; and
- numerical settings.

The current evidence does not yet support a general physical claim about espresso channeling.

Key limitations include:

- no validated physical lateral coupling operator;
- ambiguous or transient collapse-event definitions;
- sensitivity of collapse timing to timestep, tube count, seed, and configuration;
- endpoint saturation that can hide trajectory differences;
- control-mode dependence;
- limited balance diagnostics;
- no demonstrated base-state stability theory;
- no spatially resolved validation data; and
- possible mismatch between “one dominant numerical tube” and physically meaningful channeling.

The current work should be used for:

- conference visualization;
- hypothesis generation;
- experiment design;
- identifying numerical and physical requirements for a future model; and
- motivating spatial measurements.

It should not determine the title, abstract, or central claim of the current Paper B.

---

## 3.7 Recommended narrower Paper B title and thesis

Recommended title:

> **One flow curve, many causes: null-first inference for machine and porous-bed dynamics in espresso**

Alternative:

> **What an integrated flow trace can identify in an evolving porous bed**

Primary claim:

> **An integrated flow trace can establish the need for temporal dynamics relative to specified static nulls, but it does not uniquely identify the underlying bed mechanism; controlled perturbations provide greater discrimination.**

---

## 3.8 Recommended narrow Paper B structure

### Introduction

1. Flow-curve shapes are often interpreted mechanistically.
2. Similar shapes can arise from machine and bed processes.
3. Reconstruction is not mechanism identification.
4. The paper uses a null-first ladder and held-out pressure tests.
5. The ultimate objective is discriminating experiment design.

### Data and observable definitions

1. Foster machine-model demonstration.
2. Waszkiewicz flow/TDS pressure campaign.
3. Clear separation between measured traces, published model curves, and digitized reconstructions.
4. Pressure, flow, time, and concentration conventions.
5. Scoring windows and preprocessing.

### Model-comparison ladder

1. Machine-only branch.
2. Constant/static bed branches.
3. Time-varying mechanistic branch.
4. Flexible temporal null.
5. Residual and window-sensitivity analysis.

### Cross-pressure assessment

1. Shared calibration.
2. Leave-one-pressure-out procedure.
3. Per-pressure held-out metrics.
4. Residual fingerprints.
5. Scope of inference.

### Sign and compatibility constraints

1. What an isolated resistance-increasing branch can or cannot produce under fixed pressure.
2. Why this does not eliminate swelling or fines from a coupled machine-bed system.
3. Optional concise failed-composition result.

### Discriminating experiments

1. Pressure step.
2. Pressure reversal.
3. Spent-puck rebrew.
4. Spatial or depth-resolved end-state measurement.
5. Predicted direction or hysteresis for each surviving mechanism.

### Discussion

1. What one trace supports.
2. What it cannot identify.
3. Why perturbation is more valuable than another fit.
4. Limits of the present campaign.
5. Implications for porous-media inference and espresso measurement.

---

## 3.9 Recommended narrow Paper B figure set

### Main Figure 1 — Machine null and observed rising-flow case

Show:

- machine-only dip/recovery demonstration; and
- separate observed rising-flow case.

Purpose:

> Establish that curve shape is not mechanism-specific and define the target trace.

### Main Figure 2 — Null-first temporal ladder

Show:

- constant/static branches;
- time-varying mechanistic branch;
- flexible empirical temporal null;
- residual structure; and
- explicit scoring window.

Purpose:

> Establish what temporal complexity is required relative to declared nulls.

### Main Figure 3 — Cross-pressure held-out assessment

Show:

- genuine LOPO results;
- per-pressure residual fingerprints;
- shared-calibration result as a separate comparator; and
- no conflation between the two.

Purpose:

> Test within-campaign robustness and identify where candidates fail.

### Main Figure 4 — Mechanism-by-perturbation prediction matrix

Show predicted responses to:

- pressure step;
- pressure reversal;
- rebrew;
- flow-control versus pressure-control;
- spatial end state; and
- possibly first-drop timing.

Purpose:

> End the paper with a falsifiable experimental program.

### Supplementary figures

Move to the supplement:

- block-length sensitivity;
- scoring-window sensitivity;
- parameter provenance;
- residual autocorrelation diagnostics;
- alternative time-varying closures;
- detailed sign tests; and
- optional RSM context if retained at all.

---

## 3.10 Material to remove from narrow Paper B

Remove from the main paper:

- the full Schmieder RSM/grind-response analysis;
- the broad evidence matrix spanning unrelated observables;
- the N-tube floor test and concentration trajectories;
- the fine-grind anomaly as a central narrative;
- extensive software-function references;
- internal review management language; and
- open task ledgers.

Retain only content that directly advances the temporal-inference question.

---

## 3.11 Narrow Paper B publication threshold

With current data, the narrow paper can support a credible applied process-modeling or systems-identification publication if claims remain conditional.

A stronger fluid-physics submission would benefit substantially from one of the following:

1. execution of the proposed pressure-step, reversal, or rebrew experiment;
2. a stronger formal observability and perturbation-design analysis; or
3. a physical lateral model with defensible stability, balance, and convergence evidence.

The highest-value upgrade is a controlled perturbation experiment because it changes the paper from:

> multiple mechanisms remain compatible with one trace

to:

> a designed intervention separated the mechanisms.

For conference communication, the temporal story should be used without the RSM lead and without claiming a channeling instability.

Relevant venue-planning resource:

- [SUBMISSION_TARGETS.md](https://github.com/trbrewer/puckworks/blob/main/docs/SUBMISSION_TARGETS.md)

---

# 4. The Puckworks methods/resource paper

## 4.1 Strategic verdict

Puckworks itself should become a distinct scholarly output.

This should be more substantial than a minimal code note. The strongest concept is an:

> **executable, provenance-aware review of espresso process models**

that makes model assumptions, observables, evidence levels, and incompatibilities operational rather than merely descriptive.

---

## 4.2 Proposed titles

Preferred:

> **Puckworks: an executable, provenance-aware evidence registry for espresso process models**

Alternative:

> **An executable review of espresso process models: observables, evidence, and discriminating experiments**

Alternative emphasizing software methodology:

> **Puckworks: typed observable contracts and evidence-aware comparison for coupled food-process models**

---

## 4.3 Primary contribution

The methods paper should claim:

> Published espresso models use differing state definitions, parameter conventions, observables, experimental windows, and evidence standards. Puckworks represents them as provenance-tracked components with typed interfaces and explicit evidence labels, enabling matched-observable comparison without silently merging incompatible quantities.

This is more distinctive than claiming only that the repository implements several models.

---

## 4.4 Why the resource paper is publication-worthy

The project has already performed scholarly work that is usually hidden:

- reconciling conflicting definitions;
- distinguishing target from achieved operating conditions;
- separating direct measurements from reconstructed endpoints;
- identifying incompatible saturation and inventory semantics;
- preserving pressure-node distinctions;
- assigning model components to process stages;
- recording assumptions and validity ranges;
- distinguishing verification from independent prediction;
- testing models against simple nulls;
- preserving failed transfer and composition results;
- enforcing source-data and release contracts; and
- turning disagreement into experiment recommendations.

These are generalizable practices for executable reviews and multi-model scientific repositories.

Relevant technical resource:

- [contracts.py](https://github.com/trbrewer/puckworks/blob/main/puckworks/contracts.py)

---

## 4.5 Recommended methods/resource paper contents

### 1. Corpus and inclusion criteria

Complete an indexed literature search and state:

- databases searched;
- search terms;
- date range;
- inclusion and exclusion criteria;
- eligible model classes;
- eligible data types; and
- how duplicate or derivative models are handled.

The current repository corpus is useful, but it should not be called systematic until the search protocol is completed.

Relevant resource:

- [PAPER_B_RELATED_WORK.md](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_B_RELATED_WORK.md)

### 2. Process-stage taxonomy

Present the system as a chain such as:

1. machine and boundary conditions;
2. infiltration and wetting;
3. packing and geometry;
4. porous flow;
5. bed evolution;
6. extraction and transport;
7. observables and measurement operators.

Distinguish:

- calibration-only components;
- runtime components;
- observational adapters; and
- diagnostic or exploratory components.

### 3. Typed contract architecture

Explain:

- state variables;
- units;
- coordinate conventions;
- pressure locations;
- concentration definitions;
- inventory semantics;
- saturation semantics;
- missing-data behavior; and
- rules preventing silent field repurposing.

### 4. Evidence taxonomy

Define clearly:

- code verification;
- source-curve reproduction;
- post-fit reconstruction;
- within-campaign held-out prediction;
- independent external evidence;
- qualitative capacity demonstration;
- sign or compatibility test;
- exploratory synthesis; and
- proposed experiment.

### 5. Reproducibility architecture

Describe:

- model cards;
- source cards;
- data manifests;
- frozen numerical-result bundles;
- claim registries;
- figure source-data exports;
- clean release manifests;
- strict verification; and
- artifact hashing.

### 6. Demonstration 1 — Observable and unit linting

Use the mixed-unit or mismatched-observable episode to show how an invalid result can appear scientifically plausible until the contract is corrected.

The point should not be autobiographical. It should be methodological:

> A model registry needs executable observable definitions because prose-level similarity is insufficient.

### 7. Demonstration 2 — Null-first model comparison

Use the temporal flow ladder to show:

- machine-only null;
- static bed null;
- temporal mechanistic candidate;
- flexible empirical temporal null; and
- experiment selection.

### 8. Demonstration 3 — More physics can worsen a reconstruction

Use the failed extraction-plus-swelling composition to show why:

- additional mechanisms are not automatically explanatory;
- component validity does not guarantee composition validity; and
- negative results should be preserved.

### 9. Experiment-design output

Show how incompatible model predictions produce recommended measurements:

- fractions;
- pressure steps;
- reversals;
- rebrew;
- spatial end states;
- control-mode comparisons; and
- first-drop timing.

### 10. End-to-end named-shot scorecard

Use one named configuration to show every stage as:

- directly observed;
- calibrated;
- verified;
- reconstructed;
- independently tested;
- extrapolated; or
- open.

This should not be marketed as a universal digital twin. Its value is transparent evidentiary accounting.

Relevant resource:

- [PUBLIC_VALUE.md](https://github.com/trbrewer/puckworks/blob/main/docs/PUBLIC_VALUE.md)

---

## 4.6 Software and resource readiness requirements

Before journal submission, Puckworks should have:

- a stable versioned public API;
- clear installation instructions;
- tutorial workflows;
- an example that runs without private files;
- a documented path for adding a model or dataset;
- automated quick tests;
- separately identified slow scientific benchmarks;
- clear code and data licensing;
- a clean archived release and DOI;
- contribution guidelines;
- issue templates;
- changelog and semantic versioning;
- a corpus-search protocol;
- at least one external reproduction or user;
- explicit statements of which components are verified, calibrated, or exploratory; and
- strict clean-build artifact checks.

Possible publication routes include:

- an executable-review or methods journal;
- a software journal such as JOSS, subject to feature-completeness, documentation, testing, open-development history, and community contribution requirements;
- SoftwareX; or
- a domain methods venue.

JOSS scope and expectations:

- [Journal of Open Source Software — About](https://joss.theoj.org/about)

---

# 5. Future Paper 4: spatial concentration and control mode

## 5.1 Strategic verdict

The current N-tube work should not be discarded. It should be treated as the first stage of a future research program.

A future publishable question is:

> How do machine control mode and lateral hydraulic coupling govern the amplification or suppression of flow heterogeneity in a dynamically evolving, near-choke porous bed?

This could become a strong porous-media or fluid-physics paper, but only after the model and validation program mature.

---

## 5.2 Required scientific advances

A future paper would need:

### Physical model

- defensible lateral exchange;
- clear local and global conservation laws;
- explicit coupling between permeability, porosity, and extraction;
- matched pressure-control and flow-control boundary conditions;
- clear relationship between numerical tubes and physical spatial regions.

### Mathematical analysis

- a defined base state;
- linear stability, transient growth, or finite-time amplification analysis where appropriate;
- distinction between instability, localization, and thresholded first passage;
- sensitivity to initial perturbation spectrum.

### Numerical analysis

- full-trajectory convergence;
- event-time interpolation;
- independent integrator comparison;
- timestep and spatial-resolution refinement;
- balance diagnostics at every step;
- sensitivity to tube count, seed, closure, control mode, and lateral strength.

### Experimental evidence

- spatially resolved flow or wetting;
- depth-resolved porosity or extraction;
- imaging or tracer data;
- repeated shots;
- controlled pressure and flow modes; and
- a definition of “channeling” tied to measurable physical structure.

Until those requirements are met, the N-tube result is best used as:

- a conference visual;
- a technical note;
- a hypothesis generator;
- a grant figure; and
- a guide to spatial experiment design.

---

# 6. Correct number of papers

## 6.1 Why one paper is not recommended

One combined paper would be too broad and would likely contain:

- multi-solute extraction;
- practical identifiability;
- endpoint and fraction observation operators;
- machine hydraulics;
- bed permeability and porosity;
- temporal model selection;
- pressure transfer;
- swelling and fines;
- static heterogeneity;
- spatial concentration; and
- research-software architecture.

The likely result would be:

- a diffuse introduction;
- excessive methods;
- multiple unrelated result streams;
- difficulty selecting appropriate reviewers;
- a weak central claim; and
- dilution of Paper A’s strongest result.

---

## 6.2 Why the present two papers are not the best two

The current two-paper split leaves the methods/resource contribution largely unpublished.

It also overloads Paper B with:

- an RSM audit;
- temporal flow inference; and
- exploratory spatial dynamics.

The best two-paper fallback is therefore not the current A+B arrangement.

---

## 6.3 Preferred three-paper portfolio

### Paper 1

**Observation resolution and practical identifiability**

Owns:

- inventory-rate compensation;
- fraction-versus-cup information;
- orthogonal inventory constraint;
- endpoint prediction versus null; and
- measurement-design implications.

### Paper 2

**Temporal system identification and discriminating perturbations**

Owns:

- machine-only null;
- static versus temporal flow reconstruction;
- empirical temporal comparator;
- pressure holdout;
- sign constraints; and
- perturbation design.

### Paper 3

**Executable model registry and evidence architecture**

Owns:

- component taxonomy;
- typed contracts;
- model and data provenance;
- evidence levels;
- reproducibility architecture;
- unit/observable correction case;
- negative-result preservation; and
- experiment recommendation.

---

## 6.4 Why four or more papers are premature

The following do not currently justify standalone papers:

- the conditional RSM vertex;
- the mixed-unit correction alone;
- the current static-heterogeneity capacity result;
- the N-tube concentration calculation;
- the first-drop analysis from one campaign;
- a grinder-dial transfer comparison without controlled physical particle-size calibration; or
- the failed composition result by itself.

These can support:

- methods demonstrations;
- supplementary analyses;
- technical notes;
- conference presentations; or
- future work.

They should not be split into minimal publishable units.

---

## 6.5 Resource-constrained two-paper fallback

If only two journal publications are realistic, the preferred pair is:

1. **Paper A — The Cup Hides the Clock**
2. **Puckworks methods/resource paper**, using the temporal “one curve, many causes” analysis as the principal application

This fallback communicates more of the project’s distinctive contribution than Paper A plus the current broad Paper B.

The cost is that the temporal inference receives less space as a standalone scientific paper.

---

# 7. Sunk-effort strategy

## 7.1 Complete Paper A

Paper A is close enough to the correct publication unit that the existing effort should be converted directly into a submission.

Impose a scope freeze:

> No new main-text analysis should be added unless it changes the conclusion about which observations localize the rate or materially changes the null-relative predictive result.

The remaining work is primarily:

- clean release;
- conventional Methods;
- uncertainty and precision cleanup;
- figure consolidation;
- exact source-data exports;
- corrected observation operators; and
- concise theory and positioning.

---

## 7.2 Do not finish the current broad Paper B and split it later

That would create avoidable rework.

The present Paper B’s structural problem is not a missing robustness check or a weak paragraph. It is that three research units are combined in one manuscript.

The correct action is to fork now.

---

## 7.3 Recommended allocation of existing Paper B material

| Existing material | Recommended destination |
|---|---|
| Achieved-predictor RSM refit | Methods/resource paper |
| Mixed-unit and observable correction | Methods/resource paper |
| Broad evidence matrix | Methods/resource paper or dashboard |
| Machine-only dip/recovery demonstration | Narrow Paper B |
| Rising-flow temporal ladder | Narrow Paper B |
| Flexible temporal comparator | Narrow Paper B |
| Scoring-window and block-length sensitivity | Narrow Paper B supplement |
| Cross-pressure LOPO | Narrow Paper B |
| Pressure residual fingerprints | Narrow Paper B |
| Fixed-pressure swelling/fines sign constraints | Narrow Paper B, concise section |
| Failed extraction-plus-swelling composition | Resource paper case study or narrow B supplement |
| N-tube floor tests | Future Paper 4 / technical note |
| N-tube control-mode sensitivity | Future Paper 4 |
| Full current draft | Internal technical synthesis and provenance record |

This preserves nearly all of the work.

The only thing being abandoned is the assumption that every completed analysis must appear in one submitted article.

---

## 7.4 Preserve the broad Paper B as a technical synthesis

The present comprehensive draft remains valuable as:

- an internal synthesis;
- a source of supplementary analyses;
- a negative-results record;
- a roadmap for future experiments;
- a trace of how conclusions changed; and
- an onboarding document for collaborators.

It does not need to be the submitted journal manuscript to justify the effort invested in it.

---

## 7.5 Develop the resource paper in parallel, but do not rush it

The resource paper can reuse substantial existing work:

- architecture;
- model cards;
- source cards;
- evidence matrix;
- unit and observable correction;
- result bundles;
- manifests;
- failed composition;
- null ladders; and
- experiment protocols.

It should not duplicate the detailed scientific claims of Papers A and B.

Its role is to explain:

- how the system represented the claims;
- how invalid comparisons were prevented or corrected;
- how evidence tiers were assigned;
- how the analyses were regenerated; and
- how disagreement produced a testable experiment.

---

# 8. Claim ownership and duplication control

A formal claim-allocation table should be maintained.

| Claim | Owning publication |
|---|---|
| Whole-cup inventory-rate confounding | Paper A |
| Fractions restore kinetic information | Paper A |
| Same-model exact-cup aggregation control | Paper A |
| Orthogonal inventory measurement narrows rate | Paper A |
| Cross-grind mechanism barely exceeds level-only null | Paper A |
| Machine-only dynamics can mimic a dip/recovery | Narrow Paper B |
| Static closures are inadequate for the selected rising-flow trace | Narrow Paper B |
| Time variation is supported but unique mechanism is unresolved | Narrow Paper B |
| Cross-pressure residual fingerprint | Narrow Paper B |
| Pressure-step/reversal/rebrew discrimination | Narrow Paper B |
| Observable and unit contracts prevent invalid comparisons | Resource paper |
| Evidence-tier framework | Resource paper |
| Component registry and typed interfaces | Resource paper |
| Clean claim bundles and artifact provenance | Resource paper |
| More physics can worsen a reconstruction | Resource paper |
| Current N-tube control-dependent concentration | Technical report / future Paper 4 |
| Physical channel-concentration mechanism | Future Paper 4 |

The same dataset may appear in more than one publication only when:

- the scientific question is different;
- the analysis is not duplicated as the primary result;
- the prior paper is cited;
- the ownership of each numerical claim is clear; and
- the later paper does not imply that previously published evidence is new.

---

# 9. Recommended execution sequence

## Phase 1 — Freeze and finish Paper A

### Immediate tasks

1. Freeze main-text scope.
2. Select four or five main figures.
3. Write the analytical confounding explanation.
4. Establish the primary named-solute convention.
5. Regenerate full-precision transfer and baseline results.
6. Correct and rerun the external mass-alignment observation operator.
7. Complete profile-grid/domain/threshold checks.
8. Produce complete figure source data.
9. Build a clean commit-coherent release.
10. Convert internal draft language into a journal manuscript.
11. Select the target journal.
12. Obtain an external statistical or inverse-problem review.

### Decision gate

Submit when:

- the main conclusion is unchanged under the declared sensitivity checks;
- all artifacts are clean and coherent;
- figures match the manuscript;
- the null comparison is visible; and
- all claims have explicit evidence classifications.

---

## Phase 2 — Recut the Paper B conference and manuscript story

### Immediate tasks

1. Create a blank narrow-B outline.
2. Move only the temporal-inference content into it.
3. Use the machine null as setup, not as external data validation.
4. Plot genuine LOPO results prominently.
5. Rename conditional block resampling accurately.
6. Add scoring-window and block-length sensitivity.
7. Build the perturbation-prediction matrix.
8. Remove the RSM lead.
9. Remove the N-tube claim from the main manuscript.
10. Define the strongest feasible experiment.

### Conference story

Use:

> machine null → temporal ladder → cross-pressure fingerprint → discriminating intervention

Do not use:

> RSM anomaly → broad mechanism catalog → N-tube channeling claim

---

## Phase 3 — Design one high-leverage experiment

The most valuable experimental campaign would combine:

- time-resolved fractions;
- pressure and flow logging;
- at least two controlled pressure histories;
- a pressure step, reversal, or spent-puck rebrew;
- repeated shots;
- endpoint chemistry;
- measured beverage mass or density;
- carefully recorded dose, basket, grinder, and preparation;
- and, where possible, spatial or depth-resolved end-state information.

One campaign could strengthen:

- Paper A’s observation-design result;
- narrow Paper B’s mechanism discrimination;
- first-drop analyses;
- pressure-transfer analysis;
- the named-shot scorecard; and
- the resource paper’s end-to-end example.

This is higher leverage than adding another retrospective fit to an existing integrated trace.

---

## Phase 4 — Mature Puckworks as a citable research resource

### Engineering tasks

1. Define stable public APIs.
2. Separate quick tests from slow scientific benchmarks.
3. Add end-to-end tutorials.
4. Add a model-contribution guide.
5. Add a dataset-contribution guide.
6. Complete license review.
7. Create clean example data paths.
8. Add strict artifact-coherence verification.
9. Archive a tagged release.
10. Obtain external reproduction.

### Scholarship tasks

1. Complete systematic corpus search.
2. Define inclusion/exclusion criteria.
3. Audit model-card evidence levels.
4. Distinguish verification from validation in every component.
5. Select three resource-paper case studies.
6. Write the statement of need.
7. Prepare the named-shot evidence scorecard.
8. Choose software/methods venue.

---

## Phase 5 — Develop the spatial-concentration program only after the core portfolio is moving

### Near-term tasks

- preserve the current N-tube code and figures;
- write a technical note documenting assumptions;
- define physical lateral operators;
- improve balance diagnostics;
- improve persistent-event definitions;
- test control modes under matched conditions;
- identify experimental spatial observables; and
- seek collaboration with imaging or porous-media specialists.

### Decision gate for a future paper

Proceed only when at least one of the following is achieved:

- spatial validation data;
- a defensible physical lateral operator with convergence;
- a genuine stability or transient-growth result;
- experimentally validated control-mode dependence; or
- a clearly measured concentration pathway tied to the model state.

---

# 10. Tasking matrix

## 10.1 Paper A tasking

| Priority | Task | Output | Acceptance criterion |
|---|---|---|---|
| P0 | Freeze Paper A scope | Approved one-page scope | No new main-text result without PI approval |
| P0 | Rebuild clean artifact set | Tagged release | Manuscript, figures, bundle, manifest, and source data share one clean commit |
| P0 | Correct primary observable convention | Revised text/tables | Named solutes primary; proxy separate |
| P0 | Regenerate transfer and baseline at full precision | Machine-readable table | No averaging of rounded intermediate values |
| P0 | Fix external mass observation operator | Corrected analysis | No negative collection masses or negative cup weights |
| P1 | Add minimal analytical identifiability argument | Methods/theory subsection | Explains why endpoint aggregation induces compensation |
| P1 | Check profile grid/domain/threshold sensitivity | Supplementary table/figure | Main conclusion stable or limits explicitly stated |
| P1 | Consolidate figures | Four or five main figures | Every main figure directly supports central claim |
| P1 | Complete source-data exports | Figure source-data package | Every plotted value exported |
| P1 | Convert to journal prose | Submission draft | No review IDs, function-name Methods, or task ledger |
| P2 | External statistical review | Review memo | Profile and uncertainty language approved |
| P2 | Venue-specific formatting | Journal package | Meets selected journal requirements |

---

## 10.2 Narrow Paper B tasking

| Priority | Task | Output | Acceptance criterion |
|---|---|---|---|
| P0 | Create a new narrow-B outline | Approved outline | One central question: what one flow trace can identify |
| P0 | Extract temporal content from current B | New manuscript branch | RSM and N-tube removed from main narrative |
| P0 | Audit Foster provenance | Corrected text/caption | Published model curve is not called measured data |
| P0 | Reframe block resampling | Revised methods/results | Called conditional fixed-prediction resampling unless models are refitted |
| P0 | Plot genuine LOPO | Main figure/table | Held-out and shared-calibration results clearly separated |
| P1 | Add scoring-window sensitivity | Supplementary analysis | Claim does not depend on one arbitrary window |
| P1 | Add block-length sensitivity | Supplementary analysis | Central conclusion characterized across plausible block lengths |
| P1 | Build perturbation matrix | Main figure | Surviving mechanisms make explicit contrasting predictions |
| P1 | Define a feasible experiment | Protocol | Pressure step/reversal/rebrew design with measurable outcomes |
| P1 | Clean result bundle | Tagged artifact | Current code, bundle, figures, and manuscript coherent |
| P2 | Decide submission threshold | PI decision | Submit current conditional study or wait for intervention data |
| P2 | Select venue | Target memo | Claims and framing matched to venue |

---

## 10.3 Resource paper tasking

| Priority | Task | Output | Acceptance criterion |
|---|---|---|---|
| P0 | Define statement of need | One-page concept | Explains why a registry is needed instead of a monolithic model or notebook |
| P0 | Complete corpus-search protocol | Search appendix | Reproducible databases, terms, dates, and inclusion criteria |
| P0 | Audit evidence labels | Updated model cards | No component is called validated without appropriate evidence |
| P1 | Stabilize public API | Versioned release | Core interfaces documented and backward-compatibility policy stated |
| P1 | Create tutorials | Documentation | New user can add a model and run a comparison |
| P1 | Add external reproducibility path | Example workflow | Runs without private files |
| P1 | Select three case studies | Paper outline | Observable linting, null-first comparison, failed composition |
| P1 | Build named-shot scorecard | Figure/table | Every stage labelled by evidence status |
| P1 | Create archive DOI | Release artifact | Versioned code and data archived |
| P2 | Obtain external user/reproduction | Independent report | At least one researcher reproduces a workflow |
| P2 | Select methods/software venue | Venue memo | Scope and software maturity align with venue |

---

## 10.4 Future spatial paper tasking

| Priority | Task | Output | Acceptance criterion |
|---|---|---|---|
| P1 | Redefine concentration events | Analysis note | Persistent event with recrossing/hysteresis criteria |
| P1 | Add trajectory convergence | Numerical report | Shared-time trajectory norms and independent integrator |
| P1 | Add balance diagnostics | Test suite | Local/global conservation checked through time |
| P1 | Develop physical lateral coupling | Model note | Parameters tied to measurable physics |
| P2 | Analyze base-state amplification | Theory note | Stability or transient-growth framework |
| P2 | Design spatial experiment | Protocol | Measurable spatial outcome linked to model state |
| P3 | Collect validation data | Dataset | Repeated, spatially resolved campaign |
| P3 | Reassess publication | Go/no-go memo | Evidence supports a physical, not merely constructed, claim |

---

# 11. Decision rules for adding or splitting papers

A new paper should be created only when it has all of the following:

1. one central scientific question;
2. one coherent evidence chain;
3. a result that stands without extensive dependence on another manuscript’s methods;
4. a distinct audience or contribution;
5. at least one falsifiable main claim;
6. enough evidence to survive removal of project-internal context; and
7. a clean claim-ownership boundary.

A result should remain supplementary or internal when it is primarily:

- a sensitivity check;
- a one-dataset conditional fit;
- a capacity demonstration;
- a numerical artifact audit;
- a failed composition without a broader methodological lesson;
- a hypothesis generator without discriminating data; or
- a claim that depends on several unvalidated assumptions.

---

# 12. Recommended project-level narrative

The broader Puckworks effort can be communicated through a unified umbrella narrative even though the results are split across papers:

> Espresso is a coupled machine, porous-bed, transport, extraction, and measurement problem. Many published models can reproduce selected observables, but reproduction alone does not establish parameter identifiability or mechanism uniqueness. Puckworks makes models, observables, assumptions, and evidence levels explicit; compares mechanisms against simple nulls; preserves negative results; and identifies the measurement or perturbation that would most reduce uncertainty.

Within that umbrella:

- **Paper A** asks what endpoint chemistry can identify.
- **Paper B** asks what a flow trace can identify.
- **Paper 3** explains how the evidence system makes those questions executable.
- **Future Paper 4** asks how spatial concentration emerges under control and coupling.

This is a stronger program than presenting two large espresso-modeling case studies.

---

# 13. Final answers to the four strategic questions

## Question 1 — Are Papers A and B the correct papers, and are they still interesting?

### Paper A

**Yes.**

It is the strongest near-term paper. Its central result is credible, generalizable, and publication-worthy when framed as:

- practical identifiability;
- observation resolution;
- null-relative prediction; and
- experimental design.

### Paper B

**Partly.**

The temporal “one flow curve, many causes” result is compelling and publication-worthy.

The current combined manuscript is not the best paper because it mixes:

- an RSM and data-contract audit;
- temporal systems identification; and
- exploratory spatial concentration.

Those should be redistributed.

### Portfolio-level omission

The current papers do not adequately present Puckworks itself as an executable review, provenance system, and evidence architecture.

---

## Question 2 — Is two papers the correct number?

**Three near-term publications is the recommended number.**

- One paper is too broad.
- The current two are not the strongest two.
- Four or more papers from present evidence would be premature.

Preferred portfolio:

1. Paper A;
2. narrow temporal Paper B;
3. Puckworks methods/resource paper.

---

## Question 3 — Should different papers be written?

**Yes.**

The recommended papers are:

1. **The Cup Hides the Clock**  
   Observation resolution and practical identifiability.

2. **One Flow Curve, Many Causes**  
   Null-first temporal inference and perturbation design.

3. **Puckworks**  
   Executable review, typed observable contracts, provenance, evidence tiers, and experiment recommendation.

4. **Future spatial/control paper**  
   Only after physical lateral coupling, convergence, and spatial data are available.

---

## Question 4 — Should the current Papers A and B be completed first because of sunk effort?

### Paper A

**Complete it now.**

The manuscript is the correct publication unit and needs a scope freeze rather than another expansion cycle.

### Current broad Paper B

**Do not finish it unchanged and split it afterward. Fork it now.**

The work is not lost:

- the temporal core becomes a stronger scientific paper;
- the RSM and contract corrections become resource-paper demonstrations;
- the failed composition becomes a negative-result case study;
- the N-tube work becomes the basis of a future physics program; and
- the current broad draft remains a valuable technical synthesis.

The correct sunk-effort principle is:

> **Reuse the work, not necessarily the current manuscript structure.**

---

# 14. Recommended immediate direction to the team

1. **Freeze Paper A and assign a submission owner.**
2. **Create a new branch and blank outline for narrow Paper B.**
3. **Move RSM and evidence-governance material into a resource-paper folder.**
4. **Move N-tube material into a future-spatial-paper or technical-note folder.**
5. **Create and maintain the claim-ownership table.**
6. **Prioritize one clean, commit-coherent release pipeline.**
7. **Design one high-leverage perturbation-and-fraction experiment.**
8. **Begin the systematic corpus search required for the resource paper.**
9. **Seek one external statistical reviewer for Paper A and one porous-media/system-identification reviewer for narrow Paper B.**
10. **Use conference communication to test the narrowed narratives before journal submission.**

---

# 15. Supporting resources

## Repository resources

- [Puckworks README](https://github.com/trbrewer/puckworks/blob/main/README.md)
- [Paper A draft](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_A_DRAFT.md)
- [Paper B draft](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_B_DRAFT.md)
- [Reviewer brief — Paper A](https://github.com/trbrewer/puckworks/blob/main/docs/REVIEWER_BRIEF_PAPER_A.md)
- [Reviewer brief — Paper B](https://github.com/trbrewer/puckworks/blob/main/docs/REVIEWER_BRIEF_PAPER_B.md)
- [Paper outline](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_OUTLINE.md)
- [Public value assessment](https://github.com/trbrewer/puckworks/blob/main/docs/PUBLIC_VALUE.md)
- [Submission targets](https://github.com/trbrewer/puckworks/blob/main/docs/SUBMISSION_TARGETS.md)
- [Roadmap](https://github.com/trbrewer/puckworks/blob/main/docs/ROADMAP.md)
- [Paper B related-work scaffold](https://github.com/trbrewer/puckworks/blob/main/docs/PAPER_B_RELATED_WORK.md)
- [Kappa(t) discrimination protocol](https://github.com/trbrewer/puckworks/blob/main/docs/PROTOCOL_kappa_t_discrimination.md)
- [Contracts implementation](https://github.com/trbrewer/puckworks/blob/main/puckworks/contracts.py)
- [PI/venue handoff](https://github.com/trbrewer/puckworks/blob/main/docs/HANDOFF_TB_PI_VENUE.md)

## Supporting literature

- Raue et al., “Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood,” *Bioinformatics*.  
  [Article](https://academic.oup.com/bioinformatics/article/25/15/1923/213246)

- Grandvalet and Bengio, “No Unbiased Estimator of the Variance of K-Fold Cross-Validation,” *Journal of Machine Learning Research*.  
  [Article](https://www.jmlr.org/papers/volume5/grandvalet04a/grandvalet04a.pdf)

- Künsch, “The Jackknife and the Bootstrap for General Stationary Observations,” *Annals of Statistics*.  
  [Article](https://projecteuclid.org/journals/annals-of-statistics/volume-17/issue-3/The-Jackknife-and-the-Bootstrap-for-General-Stationary-Observations/10.1214/aos/1176347265.full)

- Schmieder et al., fraction-resolved espresso extraction study, *Foods* 12(15), 2871.  
  [Article](https://www.mdpi.com/2304-8158/12/15/2871)

- Foster et al., machine/bed dynamics work in *Physics of Fluids*.  
  [Article](https://pubs.aip.org/aip/pof/article/37/1/013383/3332668/Dynamics-of-liquid-infiltration-into-an-espresso)

- Journal of Open Source Software scope and submission expectations.  
  [JOSS About](https://joss.theoj.org/about)

---

## Bottom line

The work should not be compressed into one paper, and it should not remain locked into the present two-manuscript structure.

The strongest strategy is:

> **Finish Paper A, recut Paper B around temporal inference, develop Puckworks as a distinct executable-review/resource paper, and defer spatial concentration until the physical and experimental basis is stronger.**

This preserves the sunk effort while materially improving:

- scientific clarity;
- claim strength;
- venue fit;
- reviewer alignment;
- reproducibility;
- citation potential; and
- the long-term identity of the Puckworks project.
