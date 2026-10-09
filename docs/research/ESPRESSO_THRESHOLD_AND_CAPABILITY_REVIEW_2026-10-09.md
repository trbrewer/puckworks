# Puckworks and Espresso Whole-Pull: updated independent review

**Date:** 9 October 2026  
**Focus:** threshold validity, useful results obscured by negative labels, model maturity, experimental evidence, and development priorities.  
**Document status:** second-pass review and recommendations; not a new scientific adjudication or execution authorization.  
**Suggested canonical location:** `PW/docs/research/ESPRESSO_THRESHOLD_AND_CAPABILITY_REVIEW_2026-10-09.md`. EWP should link to the canonical document rather than maintain a second independently edited copy.

## 1. Executive conclusion

**The concern warrants action, but the attached review does not establish that most rejected models were actually adequate.** The evidence supports a narrower, useful conclusion: several decisions use insufficiently justified thresholds, some headline labels obscure substantial output-specific successes, and certain numerical eligibility rules obscure conclusions that are stable under the reported sensitivities. These problems should be corrected without converting uncertainty into permission to pass.

The appropriate response is neither blanket relaxation nor another round of elaborate qualification. It is to distinguish:

1. compliance with the original frozen contract;
2. whether numerical and observational uncertainty resolve the scientific question;
3. usefulness for a specified application;
4. the evidence and authorization required for adoption.

Historical failures can remain correct under their contracts while the underlying predictions remain useful. Conversely, a near miss is not automatically evidence of usefulness, and noisy observations do not make inaccurate predictions adequate.

The strongest immediate development action is **task-matched uncertainty and decision analysis of retained predictions**, beginning with the chemistry/MASS cases. This must use each task's actual scored fractions, primary conditions, conditioning inputs and metric—not the pooled scatter of a different dataset or of unscored early fractions.

Three conclusions of the original review require material correction:

- Its broad “at the noise floor” conclusion is unsupported. In MASS-006, fractions 1/2 are conditioning inputs, whereas 3/5/7/10 are scored suffixes. Pooling the much noisier early fractions into the reference scatter does not establish the resolution of the suffix task. MASS-007 uses a different target source altogether. [R4–R6]
- Dissolution-driven stress-free porosity is not an established solution to the pressure-ordering problem. The cited definition makes porosity increase with accumulated dissolved mass; the documented equilibrium law is monotone on its admissible domain. [R9–R10]
- A 5-CQA calibration offset is not an established explanation. The earlier repository review explicitly reports that reconstructing the different FIT/PRED calibration equations preserved the failure. No empirical offset correction is authorized by that observation. [R11]

There is also a substantial positive update: Grudeva task 008 has established matched numerical agreement, and task 009 has corroborated publication discrepancies using both qualified methods. Recommending that 008 not be opened is obsolete. [R1–R3]

**Overall maturity:** a substantial, reusable numerical research platform with useful conditional predictors and source-reconstruction capabilities; not yet a generally validated, coupled whole-shot espresso predictor. `PHYSICAL_VALIDATION=NOT_ESTABLISHED` remains appropriate. [R3–R5, R12]

## 2. Objectives and evidence basis

This review addresses development state, capabilities, experimental comparisons and prioritized corrective actions, with threshold selection as the organizing concern.

### 2.1 Reviewed identities

| Repository | Live main inspected | Relevant state |
|---|---|---|
| PW: `trbrewer/puckworks` | `3afe04dc9e0e0d1537bebe5220eb42d48ef7becd` | Merge of PR #331, Grudeva publication reconciliation 009; 9 October 2026, 18:37:44 UTC |
| EWP: `trbrewer/espresso-whole-pull` | `16eec1dda24ebf658965eddcf1a6fffa81903b32` | Development-guide linkage, PR #202 |

The supplied review inspected an earlier PW main, `37f62d80ce972141b515b48c893244780e6dd097`. Its source file is `puckworks_ewp_independent_review_2026-10-09.md`, SHA-256 `381dca387303283a46a17954e70a426bb25de228af7c62634abf405bb20128cd`. Preserve that file unchanged as the original review. [O, R1]

Evidence notation:

- **[R#]:** repository source inspected directly during this review; references below identify paths and revisions.
- **[O]:** a finding reported by the supplied review, not independently re-executed or fully verified here.
- **[C]:** arithmetic or mathematical deductions explicitly described here.
- **[M#]:** external methodological or primary-paper reference.
- Recommendations are proposals, not already-completed work.

Selected result files, protocols, source-code regions, current status, data guidance and live merge metadata were inspected. No full pytest suite, registry campaign, OpenFOAM run, model fit, archived-array replay or complete replicate-CSV recomputation was executed. The private corpus and detailed private prediction rows were not accessible. The original review's exhaustive-sounding counts and delegated audit findings are therefore not promoted into independently verified findings here.

## 3. Development state: what has changed and what has not

### 3.1 Grudeva numerical comparison is now complete on its declared case

PR #330 is merged as `ab28bd1d20b4fec43d6023a15bc628ee9f0bebcc`. The primary production/comparator pair and all three refinement pairings return `MATCHED_BASELINE_AGREEMENT_ON_DECLARED_CASE`. All eleven comparison families and seven individual histories pass, with no unavailable required comparisons. The work reused saved simulations. [R2]

PR #331 is merged. Task 009 returns `CORROBORATED_PUBLICATION_DISCREPANCY`: 124 input-target rows are retained, comprising 72 included and 52 excluded rows, with zero unavailable. These are repeated evaluations of the publication targets across four inputs, not 124 independent observations. Seventeen same-target, same-direction primary failures persist under both refinements. [R3]

Primary maximum absolute residuals are approximately:

| Publication family | Production P0 | Comparator C0 | Original limit |
|---|---:|---:|---:|
| Figure 3 concentration | 0.0970621 | 0.0969996 | 0.015 |
| Figure 3 front | 0.0134492 | 0.0134552 | 0.008 |
| Figure 4 concentration | 0.1413975 | 0.1413106 | 0.015 |
| Figure 4 arrival | 0.1208498 | 0.1208841 | 0.025 |

These are the comparison's dimensionless quantities. The earliest supported selected discrepancy is at dimensionless `t=3.2`; sparse selected samples do not establish the exact first divergence time. [R3]

The two implementations support a reproducible discrepancy under the declared formulation and parameters. They do not identify its cause, prove the publication wrong, exclude shared input/formulation errors, or establish experimental validity. Further numerical work should require a specific unresolved question—not repeat the completed ladder.

### 3.2 Status reporting is stale

At the inspected PW head, generated `STATE_OF_TRUTH.md` still directs Grudeva work toward task 004 owner disposition and a future matched comparison. That is inconsistent with the merged 008/009 evidence. Some other entries also describe older draft-stage states. [R13]

Correct `docs/status/current.json`, then regenerate the derived status document. Preserve historical task documents as historical records. A successful generator check proves consistency with its input, not that the input reflects the latest scientific state.

### 3.3 Governance already contains useful safeguards against overblocking

The existing Validation Operating Standard separates scientific-result disposition, framework disposition and claim ceiling. It already routes nonmaterial framework defects to a backlog and provides correction paths for unchanged-arithmetic software assembly defects. Its non-retroactivity clause prevents newly invented post-execution blockers; it is not simply a prohibition on learning from old evidence. [R14]

The remedy is to apply and narrowly extend this standard, not create another governance framework. Threshold sizing and decision-resolution analysis need improvement, but the claim that every existing rule forms an absolute one-way ratchet is overstated.

## 4. Maturity and capabilities

| Capability | Demonstrated value | Remaining limitation |
|---|---|---|
| PW component library and Guided Pull | Implemented component models, adapters and source-specific research workflows | Components do not collectively establish an integrated, validated grinder-to-cup model; Guided Pull is a restricted common-scenario chain. [O §§5–6] |
| Grudeva reduced formulation | Qualified numerical methods agree across the declared observations | Publication reproduction remains discrepant; cause and physical validation are unresolved. [R2–R3] |
| Pannusch finite-volume/state/observer work | Reported conservative numerical capabilities, continuation and conditional delivery bounds | Qualification applies to specified numerical contracts, not universal chemistry or unknown initial states. [O §6, Appendix A.4] |
| MASS-006 | Learned early-to-late conditional mapping earned its original criteria | Depends on early assays and supplied mass coordinates; does not predict the hydraulic trajectory. [R6, R15] |
| MASS-007 | Cross-source C2 improves on both simpler controls by about 38–40%, with 11/11 paired wins | Absolute adequacy failed; target chemistry conditions the prediction; independent prospective transfer is not established. [R4] |
| MASS-008 | One-calibration-shot adaptation meets its original adequacy criteria | Additional value over all controls was not established; only eleven unique eligible shots underlie the pair matrix. [R5] |
| Caffeine delivery | All four primary arms meet original adequacy budgets | Additional complexity is a comparator- and application-specific decision; stress-panel performance is mixed. [R7] |
| EWP wetting, porous flow and transport | Research implementation with numerically qualified archival baseline and source-linked comparisons | No generally validated full coupled predictor; several future mechanisms remain candidates. Public CI does not execute the full OpenFOAM solver. [R12] |
| Rheology reductions | Useful hydraulic, allocation and cumulative-delivery approximations on named synthetic cases | Fraction-TDS approximation and spatial resolution remain output-specific limitations. [R8] |

The platform should present this capability matrix before its administrative task history. “Not validated” is necessary but insufficient communication: it should sit alongside what runs, what has been checked, and what can already be used conditionally.

## 5. Experimental data: resolution must match the actual question

### 5.1 Existing collection remains an asset, not an exhausted resource

The canonical data guide records 39 source families and a September census of 31,503 files, 17,859 unique byte contents and approximately 4.48 GB. These are corpus metadata, not counts of independent espresso experiments. Pannusch and Schmieder share lineage; repeated exports, private generated outputs and reused adaptation pairs must not inflate sample size. [R15]

The useful question is not “how many files exist?” but “which independent physical units support this observable under this information contract?” A targeted evidence map should distinguish hydraulic traces, fraction chemistry, wetting observations, material properties and machine telemetry. A missing local file is unavailable evidence, not proof that the dataset does not exist.

### 5.2 The original scatter calculation is not task-matched

The supplied review reports pooled TDS SDs of 0.746 pp for FIT and 0.850 pp for PRED across six fractions. Those values are not independently recomputed here. Its own table shows that fractions 1/2 are substantially noisier than later fractions. [O §7.3]

MASS-006 explicitly uses fractions 1/2 as inputs and scores fractions 3/5/7/10. Its primary PRED panel is C01/C02/C05/C06, not all eight conditions. [R6]

As an illustration only, equal-weight pooling of the original review's rounded TDS SDs for fractions 3/5/7/10 gives approximately **0.371 pp FIT and 0.356 pp PRED**, rather than 0.746/0.850 pp. This arithmetic assumes equal per-fraction degrees of freedom and is not a raw-data recomputation, primary-panel estimate, weighted-RMSE noise floor or acceptance recommendation. It shows why the scored support matters. [C; O §7.3]

Early-assay noise still matters because it propagates through a conditional predictor. It must enter that predictor's uncertainty model, with dependence retained; it cannot simply be pooled into suffix-outcome SD. Likewise, Pannusch scatter cannot establish the error floor of Grudeva suffix measurements.

### 5.3 Required distinctions

Shot-to-shot variation, repeat assay error, uncertainty in a condition mean, calibration uncertainty, input uncertainty, digitization error and numerical sensitivity are different quantities. Replicate scatter can contain real between-shot variation that measured inputs partly explain. A conditional predictor is not constrained by the unconditional SD in the same way as a predictor of one common condition mean. [M1–M2; C]

For independent repeated measurements of a common mean, the standard-error contribution is `s/sqrt(n)`, with additional systematic and calibration terms handled separately. Three shots do not support a precise tail-probability estimate. Fractions within a shot must not be bootstrapped as independent experiments. [M1]

The task metrics also matter: averaging absolute shot biases is not the same statistic as taking the absolute value of an average signed bias. A probability calculation for the latter cannot adjudicate the former. MASS-006 and MASS-007 explicitly retain that distinction. [R4, R6]

The original review's approximately 30% “perfect-model false rejection” statement is therefore not established for the actual task gates. Nor is one replicate SD a deterministic lower bound on every realized RMSE.

## 6. What is wrong with the threshold system—and what is not

### 6.1 Separate requirements from measurement resolution

An engineering tolerance answers “what error can the intended use tolerate?” Uncertainty answers “how well can this assessment determine that error?” They are related but not interchangeable. A useful requirement need not be a fixed multiple of observation noise. When measurement uncertainty is too large, the outcome can be unresolved; the requirement need not be relaxed. [M2]

Every controlling threshold should state:

- the observable, units, scored support, aggregation and information available to the predictor;
- its role: numerical verification, numerical approximation, publication reproduction, empirical adequacy, incremental utility or operational reliability;
- its basis: analytical property, error allocation, source precision or intended-use loss;
- the applicable uncertainty/sensitivity model and what cannot be quantified;
- the decision rule, including inconclusive and partial-output outcomes.

Missing uncertainty should not prohibit exploratory computation. It should limit the claim that a small difference establishes superiority, equivalence or adequacy.

### 6.2 Tight numerical thresholds are not automatically inappropriate

Conservation, coefficient integrity, positivity and observer consistency can legitimately require far tighter tolerances than experimental accuracy. Small numerical defects can become important in other regimes or composed calculations.

Grudeva 007 illustrates a better remedy than global relaxation: its accepted-state correction retains the original coefficient-consistency bound and separately bounds stored-coordinate and evaluation-rounding effects. It preserves the failed receipt and adds a specific admission certificate without rerunning the solver. It does not merely dismiss a small discrepancy. [R16]

The original assertion that an independent comparator and its repairs could not add scientific value is also too strong. Self-convergence cannot detect every shared formulation, observation or implementation error. The completed agreement now supports moving away from undirected refinement; it does not prove that establishing independence was unnecessary.

### 6.3 Different TDS thresholds can be legitimate

A 0.10 pp model-reduction error allowance and a 0.50 pp materiality threshold for a physical effect can coexist: one may be an allocated approximation error below the effect of interest. Units alone do not make them inconsistent.

For RHEOLOGY-007, TR/9-bar fraction error is `0.125818 ± 0.005428 pp`; its lower empirical edge exceeds 0.10 pp. The approximation fails that declared target. Experimental scatter from unrelated coffee measurements does not undo a model-versus-model approximation failure. Its hydraulic, allocation and cumulative-delivery successes should nevertheless remain visible. [R8]

### 6.4 Numerical qualification and scientific decision resolution should be separate

RHEOLOGY-010 reports secondary contrasts of 4.729164 and 4.167558 pp against a 0.10 pp threshold. Their empirical allowances, 0.020039 and 0.024637 pp, exceed the separate 0.020000 pp quality ceiling. [R17]

Subtracting the stated allowances leaves approximately 4.709125 and 4.142921 pp. These are far above the threshold. This is strong evidence of stability under the tested numerical sensitivities, despite failure of the formal precision requirement. The allowances are explicitly empirical—not rigorous continuum bounds or confidence intervals. [C; R17]

A new interpretation can report both facts: **precision criterion not met; materiality conclusion stable under tested sensitivities**. Preserve the original disposition. Do not silently turn the empirical interval into a certified bound.

### 6.5 Improvement, equivalence and adoption are separate decisions

A significant improvement can be too small to justify cost, complexity or extra measurements. A nonsignificant comparison is not proof of equivalence. An observed improvement can be practically interesting without being precisely estimated.

The 0.10 mg/g caffeine gain floor is demanding but not mathematically impossible: S0's baseline error is approximately 0.216 mg/g. More importantly, S2's 41.9% improvement is against S0, whereas its gain over the closer S1 comparator is only 0.0270 mg/g with 2/4 condition wins. D0 also performs better on some stress comparisons. The original review foregrounded the most favorable comparator. [R7]

Use paired, dependence-aware score differences and an independently justified practical margin. For benefit `Delta = R_baseline - R_candidate`, a valid interval wholly above zero supports improvement; a lower endpoint above a practical margin `delta` supports materially useful improvement. Equivalence requires an interval contained inside a predeclared equivalence region, not merely one that includes zero. Account for multiple candidate comparisons when making simultaneous claims. Retain all specified comparators. A count rule may be justified by an application-level reliability objective, but should not be an unexplained substitute for uncertainty analysis.

For illustration, `P(X >= 9)` for `X ~ Binomial(11, 0.75)` is **0.45520**, not approximately 0.55. This corrects the original arithmetic; independence and common success probability are assumptions, not established properties of these cohorts. [C]

### 6.6 Frozen predictions do not eliminate post-selection bias

Keeping predictions unchanged prevents prediction retuning. Selecting new thresholds, subsets or favored cases after seeing outcomes can still bias an assessment.

Retrospective reanalysis is legitimate when labeled honestly. Preserve the original verdict, freeze a common reanalysis policy, include both positive and negative eligible cases, disclose target exposure and report threshold sensitivity. Do not describe the resulting reassessment as fresh blind validation or as leakage-free merely because predictions were frozen.

## 7. Triage of potentially undervalued results

This is a review queue, not a list of automatic verdict reversals.

| Case | Result worth retaining | Correct next interpretation/action |
|---|---|---|
| MASS-007 | C2 R=0.599149 pp; 38–40% gains over C0/C1; 11/11 paired wins | Promising cross-source, assay-conditioned transfer without coefficient refitting. Mean absolute shot bias=0.532635 pp and 7/11 individual adequacy remain limitations. Use Grudeva target uncertainty; do not call it assay-free zero-shot or noise-floor performance. [R4] |
| MASS-008 | A2 R=0.483158 pp and adequate under its contract | Adequacy already succeeded. Reassess increments separately, accounting for eleven reused shots, calibration-choice failures and dependent ordered pairs—not just the 0.000508 pp near miss. [R5] |
| Caffeine-001 | All primary arms adequate; S2 best balanced primary R | Reassess application value against every relevant simpler arm, including S1 and D0; do not infer earned complexity from S0 alone. [R7] |
| MASS-001/002/003 | Reported close adequacy margins and mixed conditioning gains | Reconstruct each task's exact target mask, bias metric and uncertainty before revising interpretation. Later 15% criteria do not automatically replace earlier 20% contracts. [O §8.2] |
| RHEOLOGY-007 | 22/24 decisions pass; useful hydraulics/allocation/cumulative delivery | Retain output-limited capability. A wider approximation budget requires a separate intended-use justification. [R8] |
| RHEOLOGY-010 secondaries | Large modeled contrasts despite precision-ceiling failures | Highest-priority numerical decision-separation example; retain precision caveat and test sensitivity robustness. [R17] |
| Waszkiewicz dynamic comparisons | Reported favorable paired intervals for some models | Inspect split design, effect magnitude, multiplicity and adverse blocked-time results together. Significance alone does not settle adoption. [O §8.2] |
| 5CQA-ASSAY-002 | Reported increment narrowly below 15% | Separate increment assessment from adequacy and persistent bias. No presumed batch-offset correction. [O §8.2; R11] |
| Grudeva 005/007; Pannusch stateful observer | Historical numerical/observation problems generated useful corrections | Check successor coverage and update current status; do not recreate already-resolved tasks. [R2, R16; O Appendix A.4] |
| SCI-LC-001A; XSV-ENS-001; RP-D-LC-001; SCI-MD-008 | Potentially recoverable partial evidence or unasked comparisons | Verify current artifacts and stopping causes first; separate archive classification, sensitivity certification and genuinely new scoring. [O §§8.3–8.7] |

For MASS-007, the 22 early summaries required **98 original assays**. Its result is retrospective, target-exposed and conditional on measured beverage mass. These qualifications do not erase its value; they define the capability actually demonstrated. [R4]

Some results also show that useful decisions need not require the best curve-fitting model. The completed mass-stop decision study reports success for C2, C0 and a fixed rule on its declared offline contract, without establishing incremental C2 decision value. Do not propose repeating that already-answered question. [R15]

## 8. Model-development direction

### 8.1 Preserve the pressure-response problem, correct the proposed solution

The inspected SCI-MD-012 result establishes that the frozen finite-porosity family and universal curve cannot produce turnover on their declared domains. Restoring an admissible root or changing scale parameters cannot repair this structural limitation. [R10]

For the cited universal law,

`Qhat = Phat(4 - 6 Phat + 4 Phat^2 - Phat^3) = 1 - (1 - Phat)^4`,

so

`dQhat/dPhat = 4(1 - Phat)^3 >= 0` for `0 <= Phat <= 1`. [C; R9]

The cited dynamic extension uses `Phi(t) = m_d(t)/m0`. With accumulating dissolved mass, this quantity increases; the original review's statement that dissolution lowers it is incorrect. A falling time trace, cross-pressure ordering at a fixed time and the long-time pressure-response curve are different questions. [R9; M3]

The inspected EWP initialization reads a fixed stress-free porosity and separately configures a source-derived dissolution-indexed permeability branch; its compaction compatibility condition rejects simultaneous use of that branch. This supports investigating a genuinely coupled formulation, but not assuming a missing switch will solve turnover. A complete code-path/open-branch audit remains necessary before implementation. [R18]

First establish whether a proposed state-dependent law can produce the required behavior within physical bounds. Define dissolved, retained and exported mass separately; maintain conservation and avoid double-counting dissolution-induced volume changes. The source identification of dissolved-mass fraction with stress-free porosity is a modeling assumption, not an independently measured geometric closure. Any resulting governing change needs its own verification and evidence comparison.

### 8.2 Grudeva: source reconciliation, not outcome-seeking tuning

Preserve task 009. Investigate equation, parameter-table, nondimensionalization, initial-state, observation and figure-generation differences. Ask for the exact plotted arrays and settings; identify the relevant paper version and permission scope.

The original `phi_lb ≈ 0.03` interpolation is not a measured or author-supplied parameter. A sweep centered on that value is target-informed exploration, not an independent reproduction test. Alternative settings must be justified and labeled; matching one event does not reconcile all profiles, fronts, inventories and concentration targets.

### 8.3 Chemistry: diagnose causes before introducing corrections

Do not adopt an additive 5-CQA offset solely because its bias is systematic. The repository already records differing calibration equations and a reconstruction that preserves the negative finding. The next diagnostic must add genuinely new evidence—such as calibration-curve provenance, dilution/recovery information or a missing observation-map explanation—not repeat that reconstruction. [R11]

Angeloni may support retrospective diagnostics of mapping or inventory assumptions, but cannot be reset to an untouched holdout. Identifiability findings should be scoped to tested models, inputs and observations; they are not evidence that every future kinetic distinction is unobservable. [O §§6–9]

## 9. Prioritized action register

These are proposed tasks. Before starting one, check live main, issues, PRs and evidence links for an already-completed equivalent. Task completion means answering its question reliably, including a negative or unresolved answer—not obtaining a favorable model verdict. No automatic production adoption follows.

### T01 — Correct the enduring review and current capability/status map

**Priority P0; documentation/status scope.** Land this review and preserve the original. Reconcile merged Grudeva 008/009 and other verified successor states in `docs/status/current.json`; regenerate status outputs. EWP links to the canonical review. Keep historical task verdicts intact.

**Acceptance:** current next actions do not request completed work; capability, numerical status, empirical evidence and adoption status are distinguishable. No solver, threshold, historical result or production-lock changes.

### T02 — Build task-matched uncertainty and threshold evidence

**Priority P0; first substantive analysis task.** Start with MASS-006, MASS-007/008 and the chemistry comparisons. Resolve original data and prediction manifests locally. Compute uncertainty on the actual primary scored windows; separate early inputs, suffix targets and stress panels. Deduplicate Pannusch/Schmieder lineage. Distinguish shot variation, assay repeatability, calibration and input propagation. For Grudeva, use its target evidence rather than imported Pannusch scatter.

**Acceptance:** reproducible script plus compact table containing task, source hashes, physical-unit counts, masks, metric, units, uncertainty components and unresolved assumptions. Reproduce historical metrics before interpreting them. Do not claim analytical repeatability when only between-shot variability exists. No new fits or CFD runs are needed for this stage.

### T03 — Amend threshold and decision policy narrowly

**Priority P0; depends on T02's estimand audit, not on favorable results.** Extend existing standards with the requirement/resolution distinction in §6. State practical margins independently of target residuals; justify reliability/count rules; provide unresolved and output-limited outcomes. Retain protected-evidence safeguards.

**Acceptance:** synthetic examples correctly distinguish resolved pass, resolved fail, uncertainty overlap, numerical precision failure with a stable decision, and adequate predictions without justified incremental complexity. Rules do not make noisier data easier to pass. Classify policy and executable-gate changes according to their actual scientific impact, not automatically as editorial G0 work.

### T04 — Reanalyze retained empirical predictions retrospectively

**Priority P1; depends on T02–T03.** Reassess MASS-007, MASS-008, caffeine, MASS-001/002/003 and the 5-CQA increment, retaining all relevant controls and positive cases in the declared eligibility set. Freeze the reanalysis specification before calculating revised decisions. Preserve old results beside the new interpretation.

**Acceptance:** paired changes, uncertainty or justified sensitivity intervals, practical margins, coverage and failure cases are reported. For MASS-008, account for the same shot occurring as calibrator and target; 110 pairs are not 110 independent samples. State that uncertainty conditional on frozen fitted models does not capture every source of training variability. Missing private predictions are a named limitation, never reconstructed from summary tables. No promised outcome or renewed holdout claim.

### T05 — Recover numerical conclusions without discarding precision requirements

**Priority P1; initial example RHEOLOGY-010.** Apply a separately reviewed decision-resolution addendum to retained outputs, keeping the original precision result. Map RHEOLOGY-007's useful outputs without declaring full reduction equivalence. Treat the already-resolved Grudeva replay episode as a reusable regression/certificate example rather than a new campaign.

**Acceptance:** unsupported precision claims remain blocked, but stable output-specific conclusions are visible. Empirical sensitivities remain labeled as such. New simulations occur only for a specific unresolved sensitivity that could affect the intended conclusion.

### T06 — Repair and classify registry gates

**Priority P1; can proceed alongside empirical analysis.** Separate smoke tests, historical/negative-control regressions, analytical verification, source reproduction and empirical adequacy. Inspect the reported tautologies and code/card discrepancies before changing them.

The Cameron gate currently checks one grind and permits a 0.5 EY-pp conservation difference. Add representative-regime and manufactured-defect tests with scale-aware tolerances. The swelling-composition gate deliberately expects a poor historical composition: preserve it as a named negative-control regression where useful, rather than confuse its PASS with scientific adequacy. [R19]

**Acceptance:** representative seeded defects fail the appropriate tests; known adverse results remain visible; registry green does not imply physical validation. Document each tolerance's purpose. Do not mechanically replace every conservation tolerance with machine epsilon or drop every negative-result regression.

### T07 — Reconcile Grudeva source settings and observation interpretation

**Priority P1; builds on completed 009.** Produce an equation/parameter/figure provenance crosswalk. Retain all selected targets and exclusions. Include horizontal as well as vertical digitization uncertainty where steep gradients make this material. Prepare specific author questions about arrays and settings; communication requires the appropriate owner instruction.

**Acceptance:** discrepancy cause is supported or remains explicitly unresolved. Any exploratory alternative is reported against the complete relevant comparison, not selected for one favorable event. No duplicate 008/009 run, automatic parameter sweep, or accusation of publication error.

### T08 — Establish pressure-response mechanism feasibility before adding physics

**Priority P1; principal physics-development direction.** Confirm the exact pressure/flow observation definitions and grouping, including numerical near-ties. Audit existing source and open work. Demonstrate analytically or with a minimal independent prototype whether the proposed coupling can produce the observed behavior within admissible bounds and without pressure-specific retuning.

**Acceptance:** a viable, distinctly new mechanism proceeds to a prospectively defined governing-physics task, or a structural impossibility is recorded and the mechanism is retired. Preserve SCI-MD-012's already-answered monotonicity/root conclusions. A 9-bar reconstruction alone is insufficient evidence of cross-pressure performance.

### T09 — Resolve specific chemistry/source discrepancies

**Priority P1; targeted data/observation-map work.** Prioritize the unresolved 5-CQA bias and any genuinely new Angeloni mapping evidence. Use retained originals and documented calibration/validity conventions; do not repeat completed equation reconstruction. Separate instrument calibration, unit/dilution mapping, inventory assumptions and actual model-form error.

**Acceptance:** cause attribution is demonstrated, bounded or explicitly unidentifiable. No assumed additive correction, omitted adverse rows, re-created holdout or calibration claim inferred solely from a systematic residual. A corrected dataset, if justified, receives a new version and preserves the original.

### T10 — Triage interrupted and procedurally limited campaigns

**Priority P2; verify original-review claims first.** Examine SCI-LC-001A, XSV-ENS-001, RP-D-LC-001 and SCI-MD-008 for already-completed successors and reusable evidence. Separate three activities: classifying completed outputs, bounding an execution defect's effect, and conducting a new scientific comparison.

**Acceptance:** completed subsets can support appropriately limited findings; stopped trajectories remain in coverage accounting. Stops may be state-dependent, so do not treat them as harmless random censoring. A small input drift does not validate a reachable-set argument without a sensitivity bound in the relevant output. Inventory dependence can be a physical property rather than an identity failure, but changing that contract does not automatically authorize a new comparison.

### T11 — Map remaining validation claims to existing evidence before new experiments

**Priority P2; targeted local-corpus work.** For each proposed validation claim, name the missing observable, independent unit, calibration separation, uncertainty or synchronization requirement. Inspect the relevant registered local sources—not another unrestricted corpus sweep. Preserve known pressure-sensor and shared-lineage limitations.

**Acceptance:** each gap is supported, or an existing dataset is assigned a legitimate next use. Only unresolved, decision-relevant gaps motivate a specific Stage F feasibility proposal. Home-lab work remains a separate owner decision; do not present immediate experiments or abandoning predictive modeling as the only alternatives.

### T12 — Apply proportionate execution and review controls

**Priority P2; shared operational improvement.** Generalize the accepted separation between scientific validity and operational interruption. Honor owner-approved removal of arbitrary calculation quotas while retaining machine-safety monitoring, storage checks, progress evidence, checkpoints where practical, and intervention for demonstrated failure or runaway behavior.

**Acceptance:** a timeout/OOM is reported as incomplete execution, not model falsification; operational retries preserve lineage and cannot alter scientific inputs opportunistically. No paid compute, system-wide changes or unapproved resource expansion. Retain ordinary CI and material-defect review; send nonmaterial hardening to the existing backlog. Do not impose an absolute review-round cap that leaves real defects unresolved.

**Sequencing:** T01 first; T02 and T06 can proceed independently. T03 then governs T04/T05. T07 and the feasibility portion of T08 can proceed without waiting for every historical reanalysis. T09–T11 are targeted evidence tasks, not reasons to suspend all development. T12 should reduce overhead across the sequence.

## 10. Enduring reporting rules and limits

For every new or revisited result, report the original contract outcome, effect size, applicable uncertainty/sensitivity, output/domain limits, practical use and claim ceiling. Reuse the existing scientific/framework/claim separation instead of inventing dozens of new global statuses.

Where a defensible interval exists for an error metric and a maximum acceptable error `T` has been justified independently, distinguish an upper bound below `T`, a lower bound above `T`, and overlap. Where the interval is only an empirical sensitivity range, say so. For incremental benefit, distinguish evidence of improvement from evidence that the improvement exceeds the practical margin. A comparison that includes zero does not establish equivalence.

No historical FAIL is rewritten merely because the review dislikes the threshold. No historical PASS is exempt from the same policy audit. No consumed source becomes blind again. No registry PASS, numerical agreement, threshold sensitivity or retrospective reanalysis establishes general physical validation.

This review does not independently verify every source-row count, delegated gate finding or interrupted-campaign claim in the original appendices. Those remain audit candidates. It also does not establish access to the private collection, new assay uncertainty, a Grudeva discrepancy cause, a 5-CQA correction or a viable turnover-producing mechanism.

**Final assessment:** useful results have sometimes been under-communicated, and several acceptance rules merit repair. The most valuable correction is to make decisions match the actual observable, intended use and available resolution—not to make more models pass. The retained evidence is substantial enough to support that work now.

## References and verification locators

Unless specified otherwise, `PW/` paths refer to `trbrewer/puckworks` at `3afe04dc9e0e0d1537bebe5220eb42d48ef7becd`; `EWP/` paths refer to `trbrewer/espresso-whole-pull` at `16eec1dda24ebf658965eddcf1a6fffa81903b32`. Section names identify the inspected content; line numbers are supplied for selected source-code/protocol excerpts. Paths and these full commits form durable source locators.

- **[O]** Original supplied independent review, filename and hash in §2.1. Its `[V]`/`[A]` labels describe that reviewer's work, not new verification here.
- **[R1]** GitHub live `branches/main` metadata for both repositories; PW merge #331. PW PR #330 metadata confirms merged status and merge SHA.
- **[R2]** PW PR #330, “Admission and results”; `PW/docs/analysis/model_grudeva2026_matched_comparison_008/RESULTS.md`. Numerical values and execution claims here are reported retained results, not rerun measurements.
- **[R3]** `PW/docs/analysis/model_grudeva2026_publication_reconciliation_009/RESULTS.md`, family results, maxima and shared-failure/refinement tables.
- **[R4]** `EWP/docs/analysis/sci_md_mass_delivery_007/RESULT.md`, coverage, arm/increment tables, conditioning contract and claim limitations.
- **[R5]** `EWP/docs/analysis/sci_md_mass_delivery_008/RESULT.md`, adequacy, increments and reused-pair limitations.
- **[R6]** `PW/docs/analysis/sci_md_mass_delivery_006/PROTOCOL.md:1–112`, especially FIT/PRED roles and metric definitions.
- **[R7]** `EWP/docs/analysis/sci_md_caffeine_delivery_001/RESULT.md`, all primary comparators and adverse stress-panel comparisons.
- **[R8]** `EWP/docs/analysis/sci_md_rheology_007/RESULT.md:1–62`, output-specific conclusions, 24 decisions and empirical allowances.
- **[R9]** `PW/docs/cards/waszkiewicz2025.md`, Governing equations, Calibration and validation, Assumptions and validity range.
- **[R10]** `EWP/docs/analysis/sci_md_012/RESULT.md`, Structural consequence.
- **[R11]** `PW/docs/research/ESPRESSO_PROGRAMME_REVIEW_2026-10-01.md:306–336`, MASS/chemistry findings and calibration-reconstruction limitation.
- **[R12]** `EWP/README.md:1–95`, current scope, public CI limitation, archival qualification and source-linked comparisons.
- **[R13]** `PW/docs/planning/STATE_OF_TRUTH.md`, generated-source instruction and active queue.
- **[R14]** `EWP/docs/validation/VALIDATION_OPERATING_STANDARD_V1.md:1–132`, disposition separation, material-blocker test, non-retroactivity and correction routing.
- **[R15]** `PW/docs/data/ESPRESSO_DATA_GUIDE.md:1–84`, MASS-stop result, corpus census, access and question-specific use map.
- **[R16]** `PW/docs/analysis/model_grudeva2026_fine_baseline_qualification_007/REPLAY_ADMISSION_CORRECTION.md:1–115`, cause, exact certificate and preserved original gates.
- **[R17]** `EWP/docs/analysis/sci_md_rheology_010/RESULT.md`, secondary contrast/allowance table and qualification limits.
- **[R18]** `EWP/solver/espressoWholePullFoam/espressoWholePullFoam.C:350–382,830–923`, stress-free-porosity initialization and closure compatibility condition; this is not a complete solver audit.
- **[R19]** `PW/puckworks/validation/gates.py:350–380,560–586`, Cameron conservation and deliberate poor-composition diagnostic gate.
- **[M1]** NIST/SEMATECH e-Handbook, “Confidence Limits for the Mean”: https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm
- **[M2]** JCGM 106:2012, *The role of measurement uncertainty in conformity assessment*, official BIPM publication record and abstract: https://www.bipm.org/en/doi/10.59161/jcgm106-2012 . Used for the distinction between specified requirements, uncertainty and acceptance decisions; this is not a claim that espresso model validation is a regulated conformity-assessment exercise.
- **[M3]** Waszkiewicz et al., *Under pressure: poroelastic regulation of flow in espresso brewing*, arXiv source version, Eqs. 16–18: https://arxiv.org/html/2512.21528v1 . The repository card tracks this source basis and separately records the journal publication; journal/preprint equivalence is not newly certified here.
