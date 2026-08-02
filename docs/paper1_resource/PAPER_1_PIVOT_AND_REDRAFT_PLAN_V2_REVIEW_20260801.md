# Review of `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2.md`

**Review date:** 1 August 2026  
**Document reviewed:** [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2.md`](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2.md)  
**Immutable reviewed implementation snapshot:** [`894dd31de9beba8fc477c9aad148087a955d877e`](https://github.com/trbrewer/puckworks/commit/894dd31de9beba8fc477c9aad148087a955d877e)  
**Prior review:** [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_REVIEW_20260801.md`](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_REVIEW_20260801.md)  
**Recommended disposition:** **CONDITIONALLY APPROVE THE SCIENTIFIC DIRECTION; REQUIRE A FOCUSED V2.1 PLAN-INTEGRITY AND INFERENCE PATCH BEFORE THE PLAN BECOMES OPERATIVE OR RESULTS DRAFTING BEGINS.**

---

## 1. Executive assessment

Revision 2 is a substantial and intellectually honest improvement over revision 1. It accepts the prior review's central findings, corrects the two artefact defects at the reviewed commit, separates fold-level from group-level evidence, exposes the coarse/fine reversals, withdraws the universal “freeze rather than fit” rule, distinguishes the Gram determinant from the profiled Schur complement, and restores the boundary between model-structural verification and physical validation.

The scientific pivot is now credible. The strongest prospective paper is no longer a small benchmark-comparison paper. It is a paper about the distinction between **whole-cup predictive performance** and **identification of a model-specific mass-transfer-rate multiplier**, with a grind-specific target-flow-map ablation as an empirical case study.

V2 should nevertheless **not yet be made operative without amendment**. The remaining problems are narrower than those in V1, but several are load-bearing:

1. A finite high-rate response limit does **not by itself imply** weak or one-sided parameter localisation. That conclusion depends on the asymptotic profiled objective relative to the declared acceptance tolerance.
2. H2 is an exact weighted-least-squares geometry, whereas the production calibration uses MAPE. The identity is valid, but its inferential relevance to the actual profile must be tested rather than assumed.
3. The “target-side hydraulic map” is a campaign-specific target-grind flow model constructed from fitted hydraulic-conductivity relations and measured per-grind shot times. It is label-external, but it is not automatically target-independent or available in a genuinely prospective use case.
4. “Hydraulic attribution” remains too causal. The analysis is currently a **target-input substitution ablation** within the declared model.
5. The proposed title still overstates the result: “cannot localize” is categorical, “extraction rate” is not the exact parameter, “saturation” can be read physically, and “attribution” implies more than the contrast identifies.
6. The gate system contains numbering collisions, incorrect cross-references, circular acceptance conditions, and a sequence that contradicts the stated rule that all ten P0 gates block the results narrative.
7. The analyses proposed after inspecting the current results create a material post-selection risk. Candidate policies, thresholds, map variants, losses, and decision rules must be frozen before the next runs.
8. The novelty gate is scheduled too late. A preliminary literature screen already shows that espresso inverse modelling, kinetic parameter estimation, variable projection, profile-based practical identifiability, and prediction under parameter uncertainty are established. The novelty must therefore be application-specific and demonstrated, not asserted.

### Recommended central research question

> **What can matched whole-cup espresso measurements support: reliable prediction, identification of a mass-transfer-rate multiplier, or both—and what target-side information is required for cross-grind prediction when kinetic localisation is weak?**

### Recommended central thesis, subject to the gates

> **Whole-cup endpoint prediction and kinetic parameter identification are different achievements. In the declared espresso model, the large-rate response approaches a finite limit, and the campaign's endpoint data may preserve useful predictions while weakly localising a common mass-transfer-rate multiplier. Cross-grind accuracy is also sensitive to how target-grind flow information is supplied, with a strong coarse-grind effect and a heterogeneous fine-grind effect. These conclusions are conditional on the model, observation operator, objective, target-information protocol, and campaign.**

This formulation unifies H1–H4 without claiming that the present model has established a universal physical property of espresso.

---

## 2. What V2 has corrected successfully

The following changes are correct and should be retained.

### 2.1 Model verification is no longer presented as physical validation

V2 correctly states that the matrix-exponential path verifies the high-rate plateau **within the declared semi-discrete model** and rules out a BDF time-integration artefact. It no longer treats agreement between two temporal paths as validation of wetting, evolving permeability, spatial heterogeneity, channeling, poroelasticity, or real espresso kinetics.

This is the right epistemic boundary. The exact-in-time solution remains scientifically valuable, but it is exact only for the same declared equations and spatial operator.

### 2.2 The fold/group conflation is repaired

V2 correctly separates:

- the one positive **fold-level** pooled M0−M2 contrast, obtained when 93.4 °C/6 bar is omitted; and
- the **group-level** Arabica-caffeine result.

The unsupported causal linkage between them is withdrawn.

### 2.3 The coarse/fine reversals are now exposed

The revised table is the most important correction in V2:

| contrast | coarse | fine | pooled |
|---|---:|---:|---:|
| M1−M2 | median +1.234 pp; 9/9 positive | median −0.037 pp; 7/9 negative | median +0.524 pp; 9/9 positive |
| M0−M2 | median −0.483 pp; 9/9 negative | median +0.155 pp; 6/9 positive | median −0.205 pp; 8/9 negative |

This changes the scientific interpretation from a uniform transfer benefit to a grind-specific result. The corrected commit also adds `disaggregated_by_target_grind` and `pooling_warning` to the refit archive, and adds `hydraulic_map_by_arm` plus corrected contrast labels to the information-parity archive.

### 2.4 H4 is no longer a universal freeze rule

V2 correctly replaces “freeze rather than fit” with the defensible principle that an unlocalised fitted value should not be interpreted as a learned kinetic quantity. It also recognises fixed, regularised, externally constrained, and profile-propagated treatments as alternatives.

### 2.5 H2 distinguishes the correct mathematical objects

V2 correctly distinguishes:

- the weighted Gram determinant, `W² Var_w(s)`;
- the profiled Schur-complement curvature under the corresponding weighted-L2 geometry, `W Var_w(s)`; and
- the per-observation sensitivity-spread normalisation, `sqrt(Var_w(s))`.

It also correctly avoids Fisher-information language in the absence of a declared likelihood.

### 2.6 Estimand tags and evidence-type matching are useful governance improvements

The proposed `FULL-PUB`, `FULL-WIDE`, `LOCO-PUB`, `LOCO-WIDE`, and `NUM-FULL` tags directly address prior mixing of incomparable quantities. The revised premise-assurance table is also sound: algebraic, numerical, provenance, inferential, physical, and novelty premises require different evidence.

---

## 3. Remaining blocking scientific and inferential findings

## 3.1 H1 still states a stronger implication than the mathematics supports

### Finding

H1 says that when a calibration profile extends into the plateau, the rate multiplier “becomes weakly or one-sidedly localised.” A finite response asymptote makes that outcome possible, but does not guarantee it.

Let `J_p(k)` be the objective after profiling the inventory/level parameter, let `J_min` be its minimum, and let `J_inf = lim_{k→∞} J_p(k)`. Under an operational tolerance `δ`, the upper acceptable set extends indefinitely only when the asymptotic objective satisfies the declared rule, for example:

`J_inf <= (1 + δ) J_min`

for a relative tolerance. If `J_inf` lies above that threshold, the profile can remain upper-bounded even though every predicted response has saturated.

### Why this matters

The model-response shoulder and the profile-objective acceptance set are distinct objects:

- **response saturation** is a model property;
- **profile localisation** depends additionally on the observations, residual pattern, objective, nuisance profiling, and tolerance.

Conflating them would recreate the same mechanism-versus-inference error that V2 otherwise works hard to remove.

### Required correction

Replace “becomes” with a conditional statement. The paper must calculate or tightly approximate `J_inf` for every group and compare it with each declared tolerance.

### Recommended H1 wording

> **Within the declared two-grain model, the matched whole-cup response approaches a finite limit as the common mass-transfer-rate multiplier increases. This response limit can produce one-sided practical localisation, but does so only when the asymptotic profiled objective remains within the declared acceptance tolerance of its minimum. Under the current 10%-relative operational rule and the finite scan to `k = 500`, five of six campaign profiles are right-censored and one is finite; final classification requires the asymptotic objective and threshold-sensitivity analysis.**

### Acceptance condition

H1 may use “one-sided” or “unbounded acceptable set” only after the asymptotic objective is evaluated. Until then, “right-censored at `k = 500` under the stated operational rule” is the correct language.

---

## 3.2 The 10% near-optimal rule remains arbitrary and load-bearing

### Finding

The headline “five of six” classification is defined by a 10% increase over the minimum objective. That is an operational convention, not a confidence set, and V2 does not yet show whether the classification survives plausible alternative conventions.

### Required action

Add the following to P0-G8 rather than leaving it as a submission-stage sensitivity:

1. report relative tolerances of at least 5%, 10%, and 20%;
2. report one or more absolute-MAPE increments, such as +0.10 and +0.25 percentage points, if numerically meaningful;
3. report `J_inf/J_min` and `J_inf−J_min` for each group;
4. preserve the phrase **operational near-optimal set**, not confidence interval;
5. state whether the 5/6 classification is invariant, partly invariant, or threshold-dependent.

### Pitfall

A multiplicative tolerance can behave oddly when `J_min` is very small. The plan should predeclare how zero or near-zero minima would be treated, even if they do not occur in this campaign.

---

## 3.3 H2's exact geometry is not the curvature of the production MAPE objective

### Finding

The identity in H2 is exact for a two-column, fixed-weight, local weighted-L2 geometry. The production level fit and score use MAPE, whose profiled objective is piecewise linear in the level and is not represented by that Gram matrix.

The current H2 wording acknowledges “the corresponding local weighted least-squares geometry,” which is good, but P0-G6 only requires a proposition and proof. That is insufficient if the manuscript uses RSI to explain or predict actual MAPE profile localisation.

### Required distinction

Define explicitly:

- `s_i(k0) = ∂ log f_i(k) / ∂ log k |_(k0)`;
- fixed positive weights `w_i` and `W = Σw_i`;
- the parameter coordinates used;
- whether the observation scale is raw concentration, relative residual, or log concentration;
- that `W Var_w(s)` is a **surrogate local curvature after profiling the scale direction**, not the Hessian of MAPE.

### Required validation

For all six groups and multiple values of `k`, compare the surrogate diagnostic with actual profile behaviour using at least:

- finite-difference local slopes or widths of the profiled MAPE curve;
- rank correlation between RSI/`RSI_total` and actual profile width across candidate designs;
- failure cases where the surrogate and MAPE disagree;
- sensitivity to the fixed weights.

### Decision rule

- If RSI tracks actual MAPE profile behaviour adequately, retain it as a validated screening diagnostic.
- If it does not, retain the algebra as a mathematical observation but remove claims that it predicts practical localisation under the production objective.

### Additional recommendation

Run a predeclared loss-sensitivity comparison using relative-L2 and another robust objective. Do not use this to manufacture a likelihood; use it only to show whether the qualitative shoulder and design conclusions are objective-family dependent.

---

## 3.4 The fitted parameter is not simply “extraction rate”

### Finding

The implemented parameter is a common multiplier applied to the source model's `A1` and `A2` mass-transfer prefactors. It is not water flow rate, not a directly measured extraction rate, and not necessarily a unique physical kinetic constant.

The proposed title's phrase “Extraction Rate” is therefore too broad and potentially confusing, especially in a paper where flow rate and residence time are also central.

### Required terminology

Use one exact term consistently, preferably:

- **mass-transfer-rate multiplier**; or
- **common kinetic multiplier**, with an explicit first-use definition.

Avoid using “rate” alone where it could mean volumetric flow rate.

### Additional terminology problem

V2 uses “transfer” in at least three senses:

1. interphase mass transfer in the extraction model;
2. cross-grind predictive transfer; and
3. target-side hydraulic information supplied at prediction time.

Use separate terms:

- **large-mass-transfer-coefficient limit** for H1;
- **cross-grind prediction** for evaluation; and
- **target-grind flow-map substitution** or **target-side hydraulic adaptation** for H3.

---

## 3.5 H3 is an input ablation, not yet hydraulic attribution

### Finding

M1 and M2 differ by the flow map used at prediction time, so M1−M2 cleanly identifies the effect of that substitution **within the declared model and supplied inputs**. It does not establish a causal hydraulic mechanism independent of grind geometry, puck structure, fines, map-fitting assumptions, or error cancellation.

The current target flow map is derived from the Angeloni card's per-granulometry fitted hydraulic-conductivity polynomials, measured per-granulometry shot times, and a viscosity correction. Those inputs are specific to the target grinds and campaign. No coarse/fine concentration is fitted in M0/M1/M2, which prevents direct label leakage, but the map is still target-domain information derived from target-grind experiments.

### Why this matters

There are at least three materially different use cases:

1. **Zero-target-data transfer:** no coarse/fine hydraulic or chemical data are available.
2. **Hydraulically adapted prediction:** inexpensive target-grind flow measurements are available, but target chemistry is not.
3. **Retrospective reconstruction:** the target shot's flow history or a map fitted using the scored target conditions is already known.

All are valid questions, but they are not the same achievement.

### Required action: information-flow audit

P0-G9 must record for every input:

- its physical meaning;
- whether it comes from the source model, O-grind calibration, target-grind campaign, or scored target shot;
- when it would be available in a real prediction workflow;
- whether the scored condition contributed to fitting that input;
- whether the input is measured, fitted, assumed, or derived;
- its uncertainty and model-form alternatives.

### Required target-map variants

At minimum, distinguish:

- **current campaign-conditioned map**;
- **held-out-condition target map**, reconstructed without the scored target condition where the data permit;
- **limited-adaptation map**, fitted from a predeclared small number of target hydraulic measurements;
- **independent or physics-only map**, if supportable;
- **common O-grind map** as the no-target-adaptation baseline.

The current result should be described as **conditional cross-grind prediction given a campaign-specific target-grind flow map** until these variants are tested.

### Recommended scientific opportunity

Rather than treating target information as an embarrassment, the paper could test a useful practical question:

> **How much inexpensive target-grind hydraulic information is required before source-calibrated chemistry predictions improve?**

An adaptation curve—zero, one, two, several, and full target hydraulic measurements—would turn H3 into a prospective and operationally meaningful result.

---

## 3.6 The fine-grind result is near-zero in median, not uniformly “small”

### Finding

The fine M1−M2 median is −0.037 pp, but the fold range is −0.671 to +0.086 pp. “Small” is reasonable for the median but not for every fold. Likewise, “enormously” for the coarse effect is rhetorical and lacks a predeclared practical margin.

### Required wording

Use:

> **The fine-grind median is near zero and usually favours the common map, but the fold-level magnitude is heterogeneous.**

For coarse targets, report the exact absolute contrast and, if desired, a transparently calculated relative reduction against the corresponding baseline. Do not use “large,” “strong,” or “practically important” without a declared comparator or practical threshold.

### Required diagnostic analysis

For the fine reversal, examine fold-, group-, and condition-level M1−M2 contributions against:

- residence time and distance outside O-grind hydraulic support;
- temperature, pressure, and on/off-grid status;
- solute and variety;
- map-predicted flow and endpoint time;
- model sensitivity to the kinetic multiplier;
- residual sign and evidence of error cancellation.

The current common-map advantage on fine targets may reflect compensation between map error and model-form error rather than evidence that the target map is physically worse.

---

## 3.7 The pooled-summary sentence needs mathematical precision

V2 says, “Both pooled numbers are means of two opposite results.” Fold by fold, the pooled contrast is the equal-weight mean of coarse and fine contrasts. However, the displayed **median pooled contrast is not the arithmetic mean of the displayed coarse and fine medians**. For example, `(1.234 − 0.037)/2 = 0.5985`, not 0.524.

### Required replacement

> **Within each fold, the pooled contrast is the equal-weight average of coarse and fine contrasts, whose typical directions oppose. The reported pooled median is the median of those fold-specific averages and should not be reconstructed by averaging the two displayed component medians.**

The artefact should include an explicit `pooling_formula` field and retain fold-specific component contrasts.

---

## 3.8 M0−M2 is a rate-treatment-policy contrast, not a pure physical rate effect

M0 and M2 share the target map, but they differ in whether `k` is fixed or fitted, and the level is re-profiled under each policy. Describing this as “rate recalibration alone” is understandable at the arm-design level, but can be read too causally.

Use:

> **incremental predictive effect of allowing the mass-transfer multiplier to vary, with the inventory/level re-profiled under each policy**

This wording makes clear that M0−M2 compares two estimation procedures, not two otherwise identical physical systems.

---

## 3.9 The unifying thesis reintroduces claims V2 has elsewhere withdrawn

The thesis says the model can “transfer useful composition predictions through target-side hydraulic information.” Three issues remain:

1. “transfer” is ambiguous because target-domain information is supplied;
2. “useful” has no adequacy criterion;
3. the hydraulic benefit is coarse-driven and is not yet prospective under a held-out map protocol.

### Recommended replacement

> **Whole-cup predictive adequacy and kinetic parameter identification are different achievements. In this campaign, source-calibrated model predictions conditioned on target-grind flow information can remain competitive while the common mass-transfer multiplier is weakly localised by the endpoint observation operator. The magnitude and even direction of the target-flow-map effect are grind-specific, and its prospective value depends on how the map is obtained.**

“Competitive” must still be tied to named comparators and uncertainty; otherwise use “numerically stable” or simply report the scores.

---

## 3.10 The current title remains overclaimed

### Current title

> *When Whole-Cup Espresso Measurements Cannot Localize Extraction Rate: Saturation, Sensitivity Geometry, and Hydraulic Attribution*

### Problems

- **“Cannot localize”** is categorical, whereas one profile is finite and the other classifications depend on an operational tolerance and finite scan.
- **“Extraction rate”** is not the exact fitted quantity.
- **“Saturation”** can be read as a physical claim about real espresso rather than a model response limit.
- **“Hydraulic attribution”** implies causal separation that has not been achieved.
- The title makes H3 coequal with H1/H2 before the target-information protocol and fine reversal are resolved.

### Recommended default title

> **Separating Prediction from Mass-Transfer-Rate Identification in Whole-Cup Espresso Modeling**

### Recommended subtitle, if needed

> **Large-Rate Limits, Sensitivity Geometry, and Grind-Specific Flow Inputs**

### Alternative if P0-G9 establishes a genuinely prospective adaptation result

> **Whole-Cup Espresso Prediction under Weak Kinetic Localisation: Target-Side Hydraulic Adaptation and Sensitivity-Guided Experiment Design**

### Alternative if P0-G9 remains descriptive

> **Weak Localisation of a Mass-Transfer-Rate Multiplier from Whole-Cup Espresso Measurements**

In that branch, hydraulics should remain a result section rather than a title-level contribution.

---

## 3.11 The paper still risks becoming two loosely connected papers

H1/H2/H4 concern rate–inventory compensation, practical localisation, and estimation policy. H3 concerns a grind-specific target-flow-map ablation. The paper will feel fragmented unless both are tied to one information question.

### Recommended narrative spine

1. The source model was developed against time-resolved/fractionated extraction kinetics.
2. Paper 1 uses matched whole-cup endpoints, which compress the temporal information.
3. Under that observation operator, inventory and a common kinetic multiplier can compensate, especially near the model's large-rate limit.
4. Prediction may nevertheless remain stable because target-side flow information determines endpoint residence time.
5. The information that supports prediction is therefore not necessarily the information that identifies kinetics.
6. Prospective measurements should be selected according to whether the objective is prediction or kinetic inference.

### Decisive recommended experiment

Add a synthetic **observation-operator comparison** using the same declared model and known parameters:

- fractionated/time-resolved concentration observations resembling the source kinetic campaign;
- one whole-cup endpoint per condition;
- multiple endpoint masses from the same or matched shots;
- equalised observation counts and plausible noise scenarios.

Profile the same level and kinetic multiplier under each design. This directly tests whether weak localisation arises from whole-cup integration rather than from optimisation failure or the parameterisation alone.

If time-resolved observations recover `k` while whole-cup endpoints do not, the paper gains a strong, interpretable result. If neither localises `k`, the thesis must shift toward deeper model-structural compensation.

---

## 4. Hypothesis-by-hypothesis disposition

| item | V2 assessment | recommendation |
|---|---|---|
| **H1** | Directionally right and properly model-scoped, but the implication from response plateau to profile localisation is too strong | **Retain after conditional rewrite, asymptotic-objective calculation, and tolerance sensitivity** |
| **H2** | Algebraically sound under a fixed-weight weighted-L2 geometry | **Retain; explicitly separate from MAPE and validate as a screening diagnostic** |
| **H3** | Correctly disaggregated, but “attribution” and prospective-transfer implications remain too strong | **Rename as a target-flow-map input ablation; promote only if held-out/limited-adaptation tests succeed** |
| **H4** | Correct principle; present campaign statement remains tied to one anchor and objective | **Retain as an estimation-policy question, not a freeze recommendation** |
| **Unifying thesis** | Strong conceptual direction, but “useful transfer through hydraulics” outruns the present protocol | **Rewrite around prediction versus identification and conditional target information** |

### Recommended revised hypothesis set

#### H1 — model response limit and practical profile classification

> Within the declared model, the matched whole-cup response approaches a finite limit as the common mass-transfer-rate multiplier increases. Whether this creates one-sided practical localisation depends on the asymptotic profiled objective relative to a declared operational tolerance. The current finite scan and 10%-relative rule right-censor five of six campaign profiles; final classification requires `J_inf` and threshold sensitivity.

#### H2 — exact local scale–rate geometry

> For the multiplicative form `ŷ_i = I f_i(k)`, define `s_i = ∂log f_i/∂log k` at a declared nominal point and fixed positive weights. The two-column weighted log-sensitivity Gram determinant is `W² Var_w(s)`, and profiling the scale direction under the corresponding weighted-L2 surrogate leaves the Schur complement `W Var_w(s)`. This is a local screening geometry, not the Hessian of the production MAPE objective; its practical relevance is assessed against actual MAPE profiles.

#### H3 — grind-specific target-flow-map substitution

> Under the current campaign-conditioned map protocol, replacing the O-grind flow map with the target-grind flow map produces a positive M1−M2 contrast for coarse targets in all nine folds, but a near-zero, heterogeneous, usually opposite effect for fine targets. This is an input-ablation result within the declared model. Its prospective interpretation depends on target-map provenance, availability, uncertainty, and held-out construction.

#### H4 — consequence for estimation policy

> A mass-transfer multiplier that is weakly localised under the declared objective and observation operator should not be interpreted as a uniquely learned kinetic quantity. Fixed, regularised, externally constrained, free-fit, and profile-propagated treatments are competing estimation policies whose predictive consequences must be compared under a frozen, target-independent protocol. The current `k = 1` result is campaign- and grind-specific.

---

## 5. Gate-system review and revised pass criteria

V2 is right to introduce ten P0 gates, but the gate system needs a plan-integrity patch before execution.

### 5.1 Add P0-G0: protocol and analysis freeze

Because the current policies, thresholds, and diagnostics were designed after examining the results, add a gate before new computations.

**P0-G0 question:** Are the next analyses protected against target-driven tuning and selective reporting?

**Required artefact:** a versioned protocol recording:

- primary and secondary hypotheses;
- candidate fixed anchors and why they were chosen;
- regularisation forms and strength-selection rules;
- profile thresholds;
- objective-family sensitivity set;
- target-map variants and fitting support;
- primary contrasts and aggregation weights;
- decision rules, including withdrawal rules;
- allowed exploratory outputs;
- code and data commit hashes.

**Pass criterion:** the protocol is committed before running G4–G9, and subsequent changes are logged as deviations rather than silently absorbed.

---

### 5.2 Revised gate table

| gate | assessment of V2 criterion | revised non-directional pass criterion |
|---|---|---|
| **P0-G1 — claim reconciliation** | Correct objective, but scheduled too late | Machine-readable claim ledger exists from the start and is regenerated at the end. Every number has a unit of analysis, estimand tag, source hash, aggregation rule, and exact wording. Internal cross-file tests pass. |
| **P0-G2 — disaggregation** | “Survive” can imply that components must agree | Every pooled headline is accompanied by its components and weighting rule. If directions reverse, the pooled directional claim is removed or explicitly labelled as an aggregation. No gate requires homogeneity. |
| **P0-G3 — model/physical scope** | Circular because it requires a table “in the manuscript” while the manuscript is frozen | Create a separate model-scope source artefact first. Pass when every claim is tagged algebraic, numerical/model-structural, empirical, or physical, and no temporal-integrator check is described as physical validation. Integrate into the manuscript later. |
| **P0-G4 — widened-domain LOCO** | Necessary; should precede policy comparison | Every fold is re-fit on the predeclared wide domain, with profile diagnostics and failure logs. H4 is revised or withdrawn according to the result; no sign-stability outcome is required. |
| **P0-G5 — rate-treatment policies** | Lists policies but lacks selection governance | Candidate policies and tuning rules are frozen under G0. Any regularisation strength or policy choice is selected on calibration data only, preferably nested. Profile propagation uses envelopes or a justified weighting rule. Pass means the comparison is completed and H4 follows it, even if no policy wins. |
| **P0-G6 — H2 mathematical scope** | Proof alone is insufficient | Identity, coordinates, weights, and assumptions are proved and tested; RSI is compared with actual MAPE profiles across groups and `k`; failures are reported. Claims are downgraded if the surrogate does not track the production objective. |
| **P0-G7 — design robustness** | Correct direction but should test the observation operator directly | Equal-budget and multi-`k` designs are evaluated under noise and model-mismatch scenarios. Synthetic recovery compares whole-cup, multiple-endpoint, and time-resolved observations. Rank, profile width, parameter error, and prediction error are reported. |
| **P0-G8 — limit and shoulder** | “Objectively” is too strong; one dimensionless group may not exist | Derive or compute the large-rate response and objective limits. Distinguish response-sensitivity shoulder from profile-acceptance boundary. Predeclare conventions and sensitivity. Use one or several physically meaningful dimensionless groups only if the equations support them. |
| **P0-G9 — hydraulic audit** | Correct but underspecified | Full provenance/timing diagram; current, held-out, limited-adaptation, and independent/physics-only map variants where feasible; parameter/map uncertainty; condition-level decomposition; explicit prospective use case. H3 is retained, narrowed, or demoted according to these results. |
| **P0-G10 — novelty** | “Affirmative novelty statement” creates confirmation bias and the gate is too late | Indexed search log and comparison matrix are complete. Pass means a bounded contribution statement is supportable **or** the paper is narrowed, split, or terminated. No gate requires a positive novelty finding. |

---

### 5.3 Gate-ID collision must be removed

V2 uses `P0-G3` for model-versus-physical scope and `P0-G4` for widened-domain refits, but then refers to legacy “G3” and “G4” as already passed numerical checks. This creates apparently contradictory statuses:

- `P0-G3` is “partly done,” while “G3” is “PASSED”;
- `P0-G4` is open, while legacy “G4” is described as closed or limited to full-support contrasts.

Retire the old names or rename them explicitly, for example:

- `NUM-TIME-01` — BDF versus exact-in-time path;
- `NUM-ENV-01` — spatial/temporal numerical envelope.

Do not reuse `G3` or `G4` after the P0 gate system is introduced.

---

## 6. Recommended execution sequence

A single linear order is inefficient. Use parallel workstreams after the V2.1 patch and protocol freeze.

### Step 0 — V2.1 plan-integrity patch and P0-G0

Before new scientific runs:

- repair gate IDs and cross-references;
- adopt exact parameter terminology;
- condition H1 on `J_inf` and tolerance;
- recast H3 as an input ablation;
- freeze candidate analyses and decision rules;
- create the initial claim ledger and model-scope artefact.

### Workstream A — novelty and paper positioning

Start P0-G10 immediately, not last. Produce a provisional positioning memo early and a final update after the results. If the novelty is too narrow, this should redirect effort before expensive analyses are completed.

### Workstream B — mathematical and observation-operator analysis

Run P0-G6 and P0-G8 together:

- derive the response and objective limits;
- define response and profile shoulders separately;
- prove the scale–rate identity;
- test its relationship to MAPE profiles;
- establish dimensionless or spectral coordinates only if justified.

### Workstream C — target-information and policy analysis

Run in dependency order:

1. P0-G9 target-map provenance and use-case audit;
2. P0-G4 widened-domain LOCO refits;
3. P0-G5 frozen policy comparison.

The map protocol should be settled before interpreting policy performance, and the free-fit domain should be settled before comparing free and constrained policies.

### Workstream D — prospective design

Run P0-G7 after the mathematical diagnostics are defined. Include the dynamic-versus-whole-cup observation-operator comparison, equal budgets, multiple true `k` values, and model-mismatch scenarios.

### Convergence

Complete final P0-G1, P0-G2, and P0-G3 reconciliation only after all analyses are frozen. Then perform final P0-G10 positioning, followed by manuscript drafting and R0–R5 review.

### Drafting rule

Methods source notes, data provenance, derivations, and numerical appendices may be prepared in controlled standalone artefacts. The results narrative, title, abstract, discussion, and contribution list wait until all blocking gates close.

---

## 7. Internal plan corrections required in V2.1

These are straightforward but must be fixed because they indicate that the plan's own controls are not yet self-consistent.

| location | issue | correction |
|---|---|---|
| §0 opening | Says “the four findings below,” but the table contains eleven entries | Replace with “the findings below” or state the actual count |
| §0 row 3.10 | Says novelty framing waits for G5 | Change to P0-G10; title may also depend on G8 and G9 |
| §5 item 9 | Says no first claim until G5 | Change to P0-G10 |
| §6 | Says title finalised after G5 | Change to after P0-G8, P0-G9, and P0-G10, with H4 wording after P0-G5 |
| §7 gate table and following paragraph | Reuses G3/G4 for legacy numerical gates | Assign unique `NUM-*` IDs and retire ambiguous legacy labels |
| document status vs §7 | Says no manuscript file is modified until all P0 gates close, but methods/model description may proceed | Distinguish controlled source artefacts from manuscript sections, or allow non-results manuscript sections explicitly |
| P0-G3 | Requires a model-scope table “in the manuscript,” creating a circular dependency | Require a standalone scope artefact first; integrate after gates close |
| §7 priority | Says a dimensionless group “makes the result transferable” | Replace with “provides a model-internal similarity coordinate and a hypothesis for comparison”; transferability still requires external data |
| §11 sequence | Says all ten gates block results, but “nothing in the results narrative begins before step 6” while G10 is step 7 | Change to “no results narrative begins until all blocking gates, including G10, close” |
| §11 | Puts novelty last | Start preliminary novelty review immediately and finalise after the analyses |
| §1 | “helps coarse prediction enormously” | Replace with the exact contrast and a declared practical interpretation |
| §2 H3 | “fine-grind effects are small” | Replace with “median near zero, heterogeneous, and usually opposite” |
| §4 risks | Says H2 is model-general | Limit this to the algebraic identity under the declared multiplicative factorisation; application and design rankings are model/operator dependent |

---

## 8. Required action register

## P0-A — V2.1 plan patch before operative status

### P0-A1 — Repair terminology, title, gate references, and status logic

**Objective:** Make the plan internally executable and prevent ambiguous gate closure.  
**Method:** Apply the corrections in §7; introduce unique gate IDs; rewrite H1/H3/thesis/title as recommended.  
**Deliverable:** `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1.md` plus a machine-readable diff checklist.  
**Check:** automated search rejects deprecated phrases including unqualified “extraction rate,” “cannot localize,” “hydraulic attribution,” and ambiguous legacy `G3/G4` IDs.

### P0-A2 — Freeze the analysis protocol

**Objective:** Prevent post hoc policy, threshold, map, and design selection.  
**Method:** Commit P0-G0 protocol before new runs.  
**Deliverable:** `PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V1.md/json`.  
**Checks:** candidate set, primary outcomes, aggregation, decision rules, and deviations are versioned; no target score is used to tune a policy or map unless labelled oracle/exploratory.

### P0-A3 — Create the initial claim and scope ledgers

**Objective:** Make every claim traceable before computations proliferate.  
**Deliverables:** `PAPER_A_CLAIM_EVIDENCE_LEDGER_V2.json` and `PAPER_A_MODEL_SCOPE_MATRIX.md`.  
**Checks:** every headline candidate has a claim ID, evidence type, estimand, unit, aggregation rule, map protocol, source hash, and falsification/withdrawal rule.

---

## P0-B — Mathematical and profile work

### P0-B1 — Derive the large-rate response and profiled-objective limits

**Objective:** Separate response saturation from practical localisation.  
**Method:** Derive the `k→∞` limit analytically where possible; otherwise use the exact-in-time operator and a rigorously converged asymptotic calculation. Profile the level at the limit.  
**Deliverable:** per-group `J_min`, `J_inf`, response limit, and classification under each predeclared tolerance.  
**Pitfalls:** assuming monotonicity without proof; confusing arithmetic noise with convergence; forcing one scalar dimensionless group when several eigenmodes or grain classes govern the limit.  
**Checks:** finite-`k` predictions converge to the derived limit; falsification control in the responsive regime remains sensitive.

### P0-B2 — Define response shoulder and profile boundary separately

**Objective:** Eliminate arbitrary or conflated “shoulder” language.  
**Method:** Use a predeclared response-elasticity metric for the model shoulder and a separate objective-tolerance rule for profile acceptability. Report sensitivity to conventions.  
**Deliverable:** response-sensitivity maps and profile classifications for all groups.  
**Check:** changing the operational threshold cannot silently change a categorical headline.

### P0-B3 — Complete and validate H2

**Objective:** Establish what the exact identity does and does not explain.  
**Method:** formal proof; symbolic/numerical check; multi-`k` RSI/Schur calculations; comparison against actual MAPE profiles.  
**Deliverable:** proposition, proof, diagnostic-validation archive, and downgrade rule.  
**Check:** at least one designed negative/failure case is included so the diagnostic is demonstrably capable of disagreeing with profile localisation.

---

## P0-C — Target-flow-map and policy work

### P0-C1 — Build the full information-flow and map-provenance audit

**Objective:** Establish the exact achievement represented by M1−M2.  
**Method:** trace every map coefficient, shot-time anchor, viscosity closure, condition, and fitting support; classify availability as pre-shot, contemporaneous, or post-shot.  
**Deliverable:** diagram plus table for M0/M1/M2 and all proposed variants.  
**Checks:** no target concentration reaches any predictor; auxiliary target hydraulic reuse is explicitly recorded rather than hidden.

### P0-C2 — Test prospective target-map construction

**Objective:** Determine whether the coarse benefit survives a realistic target-information protocol.  
**Method:** compare full campaign-conditioned, held-out-condition, limited-adaptation, and independent/physics-only maps. Construct learning curves versus number and placement of target hydraulic observations.  
**Deliverable:** grind-specific score and uncertainty tables, map-error diagnostics, and use-case statement.  
**Termination rule:** if the benefit disappears under a defensible prospective map, H3 is demoted to an oracle/campaign-conditioned sensitivity and removed from the title and contribution list.

### P0-C3 — Run LOCO-WIDE

**Objective:** Test whether fold-level policy conclusions depend on the published rate cap.  
**Method:** refit all relevant arms in every fold on the frozen wide domain; preserve full profiles and optimizer diagnostics.  
**Deliverable:** `LOCO-WIDE` archive with coarse, fine, pooled, group, and condition decompositions.  
**Check:** all comparisons are like-for-like; no `FULL-WIDE` number substitutes for a fold median.

### P0-C4 — Compare rate-treatment policies under nested selection

**Objective:** Replace the `k = 1` anecdote with a defensible policy analysis.  
**Minimum candidates:** free-wide fit; predeclared fixed anchors; regularisation toward the inherited/source value; independent constraint if available; profile-envelope propagation.  
**Method:** tune any hyperparameters only within calibration support, preferably by nested LOCO; re-profile level in every policy.  
**Deliverable:** grind-specific policy comparison with complexity, calibration use, target information, and failure modes.  
**Decision rule:** H4 reports the full result, including no clear winner or grind-dependent winners.

---

## P0-D — Prospective design and publication-value work

### P0-D1 — Compare observation operators synthetically

**Objective:** Test the paper's central claim that whole-cup prediction can coexist with weak kinetic localisation because endpoint integration discards rate information.  
**Method:** generate data with known parameters under time-resolved fractions, single endpoint, and multiple endpoints; equalise budgets; add predeclared noise and mismatch.  
**Deliverable:** parameter-recovery, profile-width, and prediction-error comparisons.  
**Falsification:** if time-resolved observations do not improve recovery, the observation-compression explanation is weakened and must be revised.

### P0-D2 — Equal-budget, multi-rate design evaluation

**Objective:** Convert RSI from a nominal design ranking into a tested prospective recommendation.  
**Method:** evaluate candidate T/p/endpoint designs at rates below, near, and beyond the shoulder; include shot/assay cost as well as point count.  
**Deliverable:** Pareto table for parameter localisation and predictive accuracy.  
**Check:** no claim that two conditions “beat” nine unless the compared budget and objective are explicit.

### P0-D3 — Complete the novelty matrix

**Objective:** Establish a narrow, defensible contribution.  
**Method:** indexed search across espresso extraction modelling, parameter estimation, practical identifiability, separable nonlinear estimation, profile propagation, and experiment design.  
**Deliverable:** search log, inclusion/exclusion table, closest-work matrix, and approved contribution paragraph.  
**Decision rule:** narrow, split, or terminate claims if no non-trivial contribution remains; do not require an “affirmative” outcome.

---

## 9. Risk register additions

V2's risk table should add the following.

| risk | severity | mitigation |
|---|---|---|
| Target map is not available prospectively or uses scored-condition hydraulic information | high; changes the use case | P0-G9 provenance and held-out/limited-adaptation maps |
| Weighted-L2 sensitivity geometry does not predict MAPE profile behaviour | high for H2's practical role | P0-G6 direct surrogate-versus-profile validation |
| Operational 10% threshold drives the 5/6 classification | high for H1 wording | `J_inf` plus threshold-family sensitivity |
| Post hoc selection among anchors, penalties, losses, maps, and designs | high; optimistic bias | P0-G0 protocol freeze, nested selection, deviation log |
| Dependent folds are treated as independent uncertainty estimates | high inferential risk | retain descriptive language; use appropriate clustered/resampling analyses only where justified |
| Static target flow map hides time-varying permeability, fines movement, poroelasticity, or channeling | high physical/model-form risk | map-form sensitivity, dynamic-flow diagnostics, explicit scope, external literature |
| Common-map fine advantage is error cancellation | high for H3 interpretation | condition-level residual and map perturbation analysis |
| One dimensionless group is forced onto a multi-mode/two-grain system | moderate | derive from equations; permit a vector or spectral criterion |
| H1/H2 and H3 do not form one paper | high publication risk | observation-information narrative; branch decision after G9 |
| Exact algebra is presented as methodological novelty despite established variable projection/identifiability literature | reputational | early P0-G10 and narrow contribution language |
| “Useful” or “competitive” is asserted without a practical comparator | moderate | define comparator set and adequacy criterion or report numbers without adjectives |
| Artefact, prose, and manuscript claims diverge again | high governance risk | generated claim ledger, cross-file tests, immutable source hashes |

---

## 10. Evidence hierarchy recommendation

The current single A–E ladder mixes fundamentally different evidence types. “A — algebraic” and “A — model-structural” do not have the same meaning, and readers may incorrectly treat both as equally strong physical evidence.

Use two dimensions instead:

1. **Evidence type:** algebraic; numerical/model-structural; empirical-descriptive; inferential; physical/external; exploratory.
2. **Robustness status:** established; verified within scope; refit-stable; heterogeneous; sensitivity-only; unresolved.

Example:

| claim | evidence type | robustness | boundary |
|---|---|---|---|
| Gram/Schur identity | algebraic | established under stated coordinates/weights | not MAPE curvature |
| finite large-rate response limit | model-structural | numerical now; algebraic if G8 succeeds | same equations/operator; not physical validation |
| coarse target-map contrast | empirical descriptive | refit-stable under current map protocol | dependent folds; target-map provenance pending |
| fine target-map contrast | empirical descriptive | heterogeneous/near-zero median | sign and magnitude vary |
| five right-censored profiles | operational profile result | threshold- and objective-dependent | finite scan until `J_inf` is evaluated |
| RSI design ranking | prospective model-based | unresolved | nominal-rate, budget, noise, and mismatch dependent |

This format prevents “high tier” from being confused with broad external validity.

---

## 11. Preliminary novelty assessment

This is not a substitute for P0-G10, but it is enough to determine that the novelty must be narrow.

### Closely adjacent established work

- **Pannusch et al. (2024)** developed a model-based kinetic espresso brewing control framework and parameter-estimation workflow for representative compounds across temperature and flow conditions.
- **Schmieder et al. (2023)** measured fractionated extraction kinetics under controlled flow rate, particle size, and temperature—the richer temporal observation operator from which the source model's kinetics were estimated.
- **Barletta et al. (2025)** explicitly framed espresso percolation as an inverse problem and analysed local inverse solvability through Jacobian rank before learning an inverse map.
- **Golub–Pereyra/variable-projection methods**, including the O'Leary–Rust implementation, long predate this work for models with linear and nonlinear parameter blocks.
- **Raue et al. (2009)** established profile-based diagnosis of practical non-identifiability and its use in experiment design.
- **Simpson and Maclaren (2023)** explicitly connect identifiability, estimation, and prediction through profile-wise uncertainty propagation.
- Recent espresso studies also show that fines, microstructure, evolving permeability, and poroelastic/dissolution coupling can materially affect flow, strengthening the need to scope static hydraulic-map interpretations.

### Claims that should not be presented as broad novelty

- introducing inverse modelling to espresso;
- introducing parameter profiling or variable projection;
- first distinguishing prediction from parameter identification;
- first using sensitivity/Jacobian rank for inverse problems;
- proving a generally new weighted-variance identity without a much deeper literature check;
- establishing hydraulics as the unique mechanism of cross-grind prediction.

### Plausible narrow contribution

Subject to the remaining gates, the paper may be able to claim the following conjunction:

1. an espresso-specific analysis of how matched whole-cup integration affects localisation of a common mass-transfer-rate multiplier;
2. a transparent exact scale–rate sensitivity identity, used as a local diagnostic and tested against the actual profile objective;
3. a model-structural large-rate endpoint limit linked explicitly—but conditionally—to practical profile classification;
4. a refit-aware, grind-disaggregated target-flow-map ablation revealing a strong coarse effect and heterogeneous fine effect;
5. a prospective comparison of observation operators and limited target-side hydraulic adaptation.

The fifth item is especially important. Without it, the paper risks reading as a careful retrospective audit of one model and campaign. With it, the paper can provide a general experimental-design insight that is concrete, falsifiable, and useful.

---

## 12. Recommended manuscript architecture

The V2 structure is broadly sound, but I recommend making the observation-information question explicit and keeping hydraulics subordinate until G9 closes.

1. **Introduction: prediction is not kinetic identification**  
   State the practical espresso problem and the observation-operator question. Position the source model's time-resolved calibration against the present whole-cup use.

2. **Data, model, parameters, and information available at prediction time**  
   Define the mass-transfer-rate multiplier exactly. Include the target-map provenance/timing diagram and model-scope matrix.

3. **Scale–rate compensation and local sensitivity geometry**  
   Derive the factorisation, determinant, Schur complement, and diagnostic limits. Separate weighted-L2 geometry from MAPE.

4. **Large-rate model limit and practical profile classification**  
   Present the response limit, asymptotic objective, tolerance sensitivity, and campaign profiles.

5. **What the observation operator preserves and discards**  
   Compare whole-cup, multiple-endpoint, and time-resolved synthetic designs. This should become the conceptual bridge from mathematics to application.

6. **Conditional cross-grind prediction and target-flow-map ablations**  
   Lead with coarse/fine decomposition. Report current and prospective/held-out map protocols separately.

7. **Estimation-policy consequences**  
   Compare free, fixed, regularised, constrained, and profile-propagated treatments without universal advice.

8. **Prospective experimental and adaptation designs**  
   Equal-budget designs for kinetic localisation and minimal target hydraulic adaptation for prediction.

9. **Discussion**  
   Distinguish model structure, campaign evidence, physical assumptions, and external validity. Address error cancellation and dynamic hydraulic physics.

10. **Conclusions**  
    State only the narrow, gate-supported result.

The original −0.394 pp comparison should remain secondary, as V2 proposes.

---

## 13. Provisional contribution statement after successful gates

> **This study separates endpoint prediction from kinetic parameter identification in a whole-cup espresso extraction model. For a multiplicative inventory–rate factorisation, it derives an exact weighted sensitivity-spread identity and distinguishes the Gram determinant from the profiled local weighted-L2 curvature. It then characterises the model's large-rate endpoint limit and determines when the asymptotic profiled objective permits one-sided practical localisation under declared operational tolerances. Refit-aware cross-grind ablations show that substituting a campaign-specific target-grind flow map has a stable effect for coarse targets but a near-zero, heterogeneous, usually opposite effect for fine targets. Finally, synthetic observation-operator and limited-adaptation studies test which additional measurements improve kinetic localisation and which target-side hydraulic data improve conditional prediction. All conclusions are scoped to the declared model, objective, information protocol, machine, coffees, and campaign.**

This paragraph is deliberately provisional. It should be shortened or weakened if G6–G10 do not support every clause.

---

## 14. Final recommendation

### Decision

**Approve V2 as the scientific basis for further work, but do not yet mark it operative.** First issue a focused V2.1 amendment that repairs the title and terminology, makes H1 logically conditional, recasts H3 as a target-input ablation, removes gate-ID collisions, fixes internal cross-references, freezes the post-review analysis protocol, and brings novelty work forward.

### Blocking items before results drafting

1. V2.1 plan-integrity patch and P0-G0 protocol freeze.
2. Exact target-map provenance, timing, and realistic prospective variants.
3. Asymptotic profiled objective and threshold sensitivity for H1.
4. Explicit validation of H2's weighted-L2 diagnostic against MAPE profiles.
5. LOCO-WIDE and frozen/nested rate-treatment policy comparison.
6. Observation-operator recovery experiment and equal-budget design analysis.
7. Early and final novelty positioning.
8. Final machine-readable claim, disaggregation, and scope reconciliation.

### Strategic emphasis

The most compelling paper is not “the rate is unidentifiable” and not “hydraulics transfer.” It is:

> **Whole-cup espresso measurements can support prediction without uniquely supporting the kinetic interpretation commonly attached to a fitted rate multiplier; the information required for prediction and the information required for kinetic identification are different, testable, and designable.**

That claim is interesting, practically relevant, and potentially publishable—but only if the next analyses directly demonstrate the role of the observation operator and establish exactly what target-side information is available in a prospective prediction.

---

## 15. Sources reviewed

### Repository sources

- [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2.md`](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2.md)
- [Implementation commit `894dd31de9beba8fc477c9aad148087a955d877e`](https://github.com/trbrewer/puckworks/commit/894dd31de9beba8fc477c9aad148087a955d877e)
- [`PAPER_A_ABLATION_REFIT_STABILITY.json` at the reviewed commit](https://raw.githubusercontent.com/trbrewer/puckworks/894dd31de9beba8fc477c9aad148087a955d877e/docs/paper1_resource/PAPER_A_ABLATION_REFIT_STABILITY.json)
- [`PAPER_A_INFORMATION_PARITY.json` at the reviewed commit](https://raw.githubusercontent.com/trbrewer/puckworks/894dd31de9beba8fc477c9aad148087a955d877e/docs/paper1_resource/PAPER_A_INFORMATION_PARITY.json)
- [`paper_a_information_parity.py` at the reviewed commit](https://raw.githubusercontent.com/trbrewer/puckworks/894dd31de9beba8fc477c9aad148087a955d877e/tools/paper_a_information_parity.py)
- [`angeloni_bracket.py`](https://github.com/trbrewer/puckworks/blob/main/puckworks/validation/slow/angeloni_bracket.py)
- [`angeloni2023.md` model card](https://github.com/trbrewer/puckworks/blob/main/docs/cards/angeloni2023.md)
- [`PAPER_A_TRANSFER_CORPUS_CONTRACTS.json`](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_A_TRANSFER_CORPUS_CONTRACTS.json)
- Prior review: [`PAPER_1_PIVOT_AND_REDRAFT_PLAN_REVIEW_20260801.md`](https://github.com/trbrewer/puckworks/blob/main/docs/paper1_resource/PAPER_1_PIVOT_AND_REDRAFT_PLAN_REVIEW_20260801.md)

### Preliminary adjacent literature

- Pannusch et al., **Model-based kinetic espresso brewing control chart for representative taste compounds** (2024), *Journal of Food Engineering*: [article](https://www.sciencedirect.com/science/article/abs/pii/S0260877423004855)
- Schmieder et al., **Influence of Flow Rate, Particle Size, and Temperature on Espresso Extraction Kinetics** (2023), *Foods*, DOI 10.3390/foods12152871: [article](https://www.mdpi.com/2304-8158/12/15/2871)
- Barletta et al., **Inverse modeling of porous flow through deep neural networks: the case of coffee percolation** (2025): [arXiv](https://arxiv.org/abs/2511.11194)
- O'Leary and Rust, **Variable Projection for Nonlinear Least Squares Problems**: [NIST record](https://www.nist.gov/publications/variable-projection-nonlinear-least-squares-problems)
- Raue et al., **Structural and practical identifiability analysis of partially observed dynamical models by exploiting the profile likelihood** (2009), *Bioinformatics*: [article](https://academic.oup.com/bioinformatics/article/25/15/1923/213246)
- Simpson and Maclaren, **Profile-Wise Analysis** (2023), *PLOS Computational Biology*: [article](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011515)
- Smrke et al., **The role of fines in espresso extraction dynamics** (2024), *Scientific Reports*: [article](https://www.nature.com/articles/s41598-024-55831-x)
- Mo et al., **Exploring the link between coffee matrix microstructure and flow properties using combined X-ray microtomography and smoothed particle hydrodynamics simulations** (2023), *Scientific Reports*: [article](https://doi.org/10.1038/s41598-023-42380-y)
- Waszkiewicz et al., **Under pressure: poroelastic regulation of flow in espresso brewing** (2025 preprint): [arXiv](https://arxiv.org/abs/2512.21528)

**Literature note:** This is a focused review screen, not the systematic indexed search required by P0-G10.
