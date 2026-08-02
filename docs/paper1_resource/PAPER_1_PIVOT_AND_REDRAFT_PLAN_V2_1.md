# Paper 1 — pivot and redraft plan, revision 2.1

> [!WARNING]
> **SUPERSEDED AND NOT OPERATIVE.** Reviewed in `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_1_REVIEW_20260801.md`,
> which found that this revision corrected the science but was not yet executable: it delegated
> normative content to a superseded file, sequenced its "from the start" controls last, asserted an
> implication from a response limit to profile localisation without the asymptotic objective, and was
> policed by an integrity test that did not implement the checks it advertised. Use
> **`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2.md`**. Retained only for the audit trail.


**Prepared:** 1 August 2026
**Supersedes:** `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2.md` (v2) and `…_PLAN.md` (v1), both retained for
the audit trail and **not operative**
**Actions:** `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_REVIEW_20260801.md`
**Status:** proposal for review. **No manuscript file has been modified and the redraft has not
started.**

---

## 0. Disposition of the second review

Every checkable claim was verified against the repository before acceptance. All hold. The review is
accepted in full; the findings below are recorded as defects in my plan, not differences of
emphasis.

| # | Finding | Verified | Disposition |
|---|---|---|---|
| 3.1 | A finite response limit does **not** imply weak localisation — that depends on `J_inf` vs `(1+δ)J_min` | yes, logically; and I never computed `J_inf` | **Accepted.** H1 made conditional |
| 3.2 | The 10 % near-optimal rule is arbitrary and load-bearing | yes | **Accepted.** Threshold family moved into the gate |
| 3.3 | H2's weighted-L2 geometry is not the curvature of the production MAPE objective | yes | **Accepted.** H2 separated; validation now required, not optional |
| 3.4 | The fitted parameter is not "extraction rate" | yes — it multiplies `A1`/`A2`, the Sherwood prefactors in `Sh = A·Re^B·Sc^⅓` | **Accepted.** Terminology fixed throughout |
| 3.5 | H3 is a target-input substitution ablation, not "hydraulic attribution" | yes — the map is `(40/τ_gran)·(k_r(p)/k_r(9))·(μ_ref/μ)` from **target-grind** campaign data | **Accepted.** H3 recast; use-case taxonomy added |
| 3.6 | Fine effect is "near-zero median, heterogeneous", not "small" | yes — range −0.671 to +0.086 | **Accepted** |
| 3.7 | The pooled **median** is not the mean of the component medians | yes — (1.234 − 0.037)/2 = **0.5985**, archived pooled median is **0.524** | **Accepted.** My sentence was loose |
| 3.8 | M0−M2 is a policy contrast, not a pure rate effect | yes — the level is re-profiled under each policy | **Accepted** |
| 3.9 | The unifying thesis reintroduces withdrawn claims | yes | **Accepted.** Thesis rewritten |
| 3.10 | The title overstates all four of its nouns | yes | **Accepted.** Title changed |
| 3.11 | The paper risks being two loosely connected papers | yes | **Accepted.** Narrative spine adopted; observation-operator experiment added |
| 5.3 | Gate-ID collision | yes — **6** bare `G3`/`G4` references colliding with `P0-G3`/`P0-G4` | **Accepted.** Legacy gates renamed `NUM-*` |
| 7 | Ten internal defects | yes — "the four findings below" above an 11-row table; **3** stale bare `G5` references; "enormously"; the step-6/step-7 contradiction; the circular manuscript dependency | **All accepted and fixed** |

### What I take from this round

V2 fixed v1's *scientific* overclaims and then failed on its own *internal consistency* — stale gate
numbers from the previous scheme, a self-contradicting sequence, and a gate that depended on the
manuscript it forbade writing. A plan whose controls do not agree with each other cannot enforce
anything. §9.7 adds a machine check so this class of defect is caught mechanically rather than by a
reader.

---

## 1. Terminology, fixed first

Three ambiguities caused several of the overclaims. Fixed once, used consistently.

| use exactly | never write | why |
|---|---|---|
| **mass-transfer-rate multiplier** (or *common kinetic multiplier*), symbol `κ` | "extraction rate", "the rate" | it multiplies `A1`/`A2`, the Sherwood prefactors in `Sh = A·Re^B·Sc^⅓`, giving the lumped coefficient `h = Sh·D/d₃₂`. It is not a flow rate, not a measured extraction rate, and not established as a physical constant |
| **large-mass-transfer-coefficient limit** | "saturation" (unqualified) | "saturation" reads as a physical claim about espresso |
| **cross-grind prediction** | "transfer" (for evaluation) | |
| **target-grind flow-map substitution** | "hydraulic transfer", "hydraulic attribution" | the map is supplied at prediction time, not carried across |
| **operational near-optimal set** | "confidence interval", "acceptable set" | it is a declared tolerance convention |

`κ = 1` is the **inherited source normalisation**, not a validated physical value.

---

## 2. Revised hypotheses

### H1 — model response limit, and conditional profile classification

> Within the declared two-grain model, the matched whole-cup response approaches a **finite limit**
> as the common mass-transfer-rate multiplier increases. **Whether this produces one-sided practical
> localisation depends on the asymptotic profiled objective `J_inf` relative to a declared
> operational tolerance**: the upper acceptable set extends indefinitely only if
> `J_inf ≤ (1+δ)·J_min`. Under the current 10 %-relative rule and a finite scan to `κ = 500`, five of
> six campaign profiles are right-censored and one is finite. **Final classification requires `J_inf`
> and threshold sensitivity, neither of which has been computed.**

v2's "becomes weakly or one-sidedly localised" is withdrawn. Response saturation is a model
property; profile localisation additionally depends on the observations, residuals, objective,
nuisance profiling and tolerance. Conflating them would recreate exactly the mechanism-versus-
inference error this pivot exists to remove.

**Scope boundary:** the limit is a property of the declared model. Whether real espresso occupies
that regime is untested.

### H2 — exact local scale–rate geometry, and its relevance tested

> For `ŷ_i = I·f_i(κ)` with `s_i = ∂log f_i/∂log κ` at a declared nominal point and fixed positive
> weights, the two-column weighted log-sensitivity Gram determinant is exactly `W²·Var_w(s)`, and
> profiling the scale direction under the corresponding **weighted-L2 surrogate** leaves the Schur
> complement `W·Var_w(s)`. This is a **local screening geometry, not the Hessian of the production
> MAPE objective**; its practical relevance is assessed against actual MAPE profiles, and downgraded
> if it fails to track them.

The production level fit and score use MAPE, whose profiled objective is piecewise linear in the
level and is not represented by that Gram matrix. A proof alone is insufficient if RSI is used to
explain real localisation — so validation is now a pass condition, with a **designed failure case**
required so the diagnostic is demonstrably capable of disagreeing.

### H3 — grind-specific target-flow-map substitution

> Under the current **campaign-conditioned map protocol**, replacing the O-grind flow map with the
> target-grind flow map produces a positive M1−M2 contrast for **coarse** targets in all nine folds
> (median +1.234 pp), and a **near-zero, heterogeneous, usually opposite** effect for **fine**
> targets (median −0.037 pp, range −0.671 to +0.086, 7/9 negative). This is an **input-ablation
> result within the declared model**. Its prospective interpretation depends on map provenance,
> availability, uncertainty, and held-out construction.

"Attribution" is withdrawn. The map is `(40/τ_gran)·(k_r(p)/k_r(9))·(μ_ref/μ(T))`, built from
per-granulometry shot times (20/13/35 s) and per-granulometry conductivity polynomials — **target-
grind campaign measurements**. No target *concentration* reaches any predictor, but the map is
target-domain information, and three materially different use cases have been conflated:

1. **zero-target-data transfer** — no coarse/fine data at all;
2. **hydraulically adapted prediction** — cheap target flow measurements available, chemistry not;
3. **retrospective reconstruction** — the target shot's flow already known.

The present result is case 3 or a version of case 2, not case 1.

### H4 — estimation policy

> A mass-transfer-rate multiplier that is weakly localised under the declared objective and
> observation operator **should not be interpreted as a uniquely learned kinetic quantity.** Fixed,
> regularised, externally constrained, free-fit and profile-propagated treatments are **competing
> estimation policies** whose predictive consequences must be compared under a frozen,
> target-independent protocol. The current `κ = 1` result is campaign- and grind-specific.

M0−M2 is restated as *"incremental predictive effect of allowing the multiplier to vary, with the
inventory level re-profiled under each policy"* — two estimation procedures, not two physical
systems.

### Unifying thesis

> **Whole-cup predictive adequacy and kinetic parameter identification are different achievements.**
> In this campaign, source-calibrated predictions conditioned on target-grind flow information can
> remain numerically competitive while the common mass-transfer-rate multiplier is weakly localised
> by the endpoint observation operator. The magnitude and even the direction of the target-flow-map
> effect are grind-specific, and its prospective value depends on how the map is obtained.

### Narrative spine — what makes this one paper, not two

The review's diagnosis is right: H1/H2/H4 and H3 need a single question. It is an
**observation-information** question, and the campaign supplies it:

1. the source model was calibrated against **time-resolved, fractionated** kinetics (Schmieder);
2. Paper 1 uses **matched whole-cup endpoints**, which compress that temporal information;
3. under that operator, inventory and the multiplier can compensate, especially near the large-
   coefficient limit;
4. prediction can nevertheless remain stable, because target-side flow information sets the endpoint
   residence time;
5. **the information that supports prediction is not the information that identifies kinetics**;
6. prospective measurements should therefore be chosen according to which of the two is wanted.

---

## 3. Corrections carried from v2

| v2 said | corrected |
|---|---|
| "the four findings below" | eleven findings; count stated |
| "helps coarse prediction enormously" | +1.234 pp median (9/9 folds), stated without an adjective |
| "fine-grind effects are small" | median near zero, **heterogeneous**, usually opposite; range −0.671 to +0.086 |
| "Both pooled numbers are means of two opposite results" | *within each fold* the pooled contrast is the equal-weight mean of coarse and fine; the reported pooled **median** is the median of those fold averages and **must not** be reconstructed from the component medians — (1.234 − 0.037)/2 = 0.5985 ≠ 0.524 |
| "rate recalibration alone" | incremental predictive effect of allowing `κ` to vary, with the level re-profiled under each policy |
| bare `G3`/`G4`/`G5` gate references (9 in total) | legacy numerical gates renamed **`NUM-TIME-01`**, **`NUM-ENV-01`**; novelty is **`P0-G10`** everywhere |
| "no manuscript file modified until all P0 gates close" + "model description may proceed" | controlled **source artefacts** may proceed; **manuscript sections** may not |
| P0-G3 requires a scope table *in the manuscript* | standalone `PAPER_A_MODEL_SCOPE_MATRIX.md` first; integrated later |
| "nothing in the results narrative begins before step 6" (with G10 at step 7) | no results narrative begins until **all** blocking gates close, **including P0-G10** |
| "H2 is model-general" | the **algebraic identity** is general under the declared factorisation; its application and design rankings are model- and operator-dependent |
| "a dimensionless group makes the result transferable" | provides a model-internal similarity coordinate and a hypothesis for comparison; transferability needs external data |

---

## 4. Title

v2's title is withdrawn: "cannot localize" is categorical when one profile is finite, "extraction
rate" is not the fitted quantity, "saturation" reads physically, and "attribution" implies causal
separation not achieved.

> **Separating Prediction from Mass-Transfer-Rate Identification in Whole-Cup Espresso Modeling**
>
> *subtitle if needed:* **Large-Coefficient Limits, Sensitivity Geometry, and Grind-Specific Flow
> Inputs**

Branch after the gates: if P0-G9 establishes a genuinely prospective adaptation result, hydraulics
may rise to title level; if it stays descriptive, use *"Weak Localisation of a Mass-Transfer-Rate
Multiplier from Whole-Cup Espresso Measurements"* and keep hydraulics as a results section.

Finalised only after **P0-G8, P0-G9 and P0-G10**; H4 wording after **P0-G5**.

---

## 5. Evidence hierarchy — two dimensions

v2's single A–E ladder let "algebraic" and "model-structural" both read as tier A, which invites
readers to treat them as equally strong physical evidence. Replaced with a type × robustness grid.

| claim | evidence type | robustness | boundary |
|---|---|---|---|
| Gram/Schur identity | algebraic | established under stated coordinates and weights | **not** MAPE curvature |
| finite large-coefficient response limit | model-structural | numerical now; algebraic if P0-G8 succeeds | same equations and spatial operator; not physical validation |
| coarse target-map contrast | empirical descriptive | refit-stable under the current map protocol | dependent folds; map provenance pending |
| fine target-map contrast | empirical descriptive | heterogeneous, near-zero median | sign and magnitude vary by fold |
| five right-censored profiles | operational profile result | threshold- and objective-dependent | finite scan until `J_inf` is evaluated |
| RSI design ranking | prospective model-based | **unresolved** | nominal-`κ`, budget, noise and mismatch dependent |
| original −0.394 pp comparison | empirical descriptive | weak refit stability | historical secondary only |

---

## 6. What we are not claiming

Carried forward and extended.

1. That real espresso reaches the large-coefficient regime.
2. That `κ` is a physical kinetic constant, or that `κ = 1` is externally validated.
3. That the acceptable set is mathematically unbounded — only right-censored at `κ = 500`.
4. That hydraulics are the unique or causal mechanism of cross-grind prediction.
5. That particle geometry has been excluded — it was frozen, not varied.
6. That freezing is universally preferable to fitting.
7. That the target map is available in a zero-target-data prospective workflow.
8. That the weighted-L2 geometry predicts MAPE profile behaviour — untested.
9. Structural non-identifiability, reserved for a proof of exact non-uniqueness.
10. Any "first" or "to our knowledge" claim, until P0-G10.
11. **Symmetrically**: that the effect is absent, or that fitting is harmful.

---

## 7. Gates

### 7.1 New: P0-G0 — protocol and analysis freeze

Every policy, threshold, map variant and design in this plan was chosen **after** seeing the current
results. That is a material post-selection risk and it is now gated.

**Question:** are the next analyses protected against target-driven tuning and selective reporting?

**Deliverable:** `PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V1.md` recording primary and secondary hypotheses;
candidate anchors and why; regularisation forms and strength-selection rules; profile thresholds;
objective-family set; target-map variants and their fitting support; primary contrasts and
aggregation weights; decision **and withdrawal** rules; permitted exploratory outputs; code and data
hashes.

**Pass:** committed **before** P0-G4…G9 run; later changes logged as **deviations**, not absorbed.

### 7.2 Legacy numerical gates, renamed

The old `G3`/`G4` collided with the new `P0-G3`/`P0-G4`. Renamed and closed:

| id | question | status |
|---|---|---|
| **`NUM-TIME-01`** | Is the plateau a BDF artefact or structural to the declared semi-discrete model? | **PASSED** for the tested model and envelope; physical generalisation untested |
| **`NUM-ENV-01`** | Do the **full-support** contrasts survive mesh and tolerance change? | **PASSED**, full-support only; says nothing about fold medians |

Neither name may be reused, and neither is sufficient to begin drafting.

### 7.3 P0 gates — non-directional pass criteria

No gate requires a favourable result. Each requires that the work be *done* and the claims follow.

| gate | pass criterion |
|---|---|
| **P0-G0** | protocol frozen and committed before new runs |
| **P0-G1** | machine-readable claim ledger exists **from the start** and is regenerated at the end; every number carries unit of analysis, estimand tag, source hash, aggregation rule, exact wording; cross-file tests pass |
| **P0-G2** | every pooled headline is shown with its components **and weighting rule**; where directions reverse, the pooled directional claim is removed or explicitly labelled an aggregation. **Homogeneity is not required** |
| **P0-G3** | standalone `PAPER_A_MODEL_SCOPE_MATRIX.md`; every claim tagged algebraic / numerical-model-structural / empirical / physical; no temporal-integrator check described as physical validation |
| **P0-G4** | every fold re-fit on the frozen wide domain with profile diagnostics and failure logs; H4 revised or withdrawn accordingly. **No sign-stability outcome required** |
| **P0-G5** | policies and tuning frozen under P0-G0; any strength selected on calibration data only, preferably nested; level re-profiled under each policy. Pass = comparison completed, **even if no policy wins** |
| **P0-G6** | identity proved; RSI compared with actual MAPE profiles across groups and `κ`; **a designed failure case included**; claims downgraded if the surrogate does not track the objective |
| **P0-G7** | equal-budget and multi-`κ` designs under noise and model mismatch; synthetic recovery across whole-cup, multi-endpoint and time-resolved operators; rank, profile width, parameter error and prediction error all reported |
| **P0-G8** | large-coefficient response **and objective** limits derived or rigorously computed; **response shoulder and profile-acceptance boundary defined separately**; thresholds 5/10/20 % plus absolute increments; `J_inf/J_min` and `J_inf − J_min` per group; classification stated as invariant, partly invariant, or threshold-dependent |
| **P0-G9** | full provenance and **timing** diagram (pre-shot / contemporaneous / post-shot); current, held-out-condition, limited-adaptation and physics-only map variants where feasible; map uncertainty; condition-level decomposition of the fine reversal; explicit prospective use case. H3 retained, narrowed or demoted accordingly |
| **P0-G10** | indexed search log and closest-work matrix complete. Pass = a bounded contribution statement is supportable **or** the paper is narrowed, split, or terminated. **No positive novelty finding is required** |

---

## 8. Execution: parallel workstreams

A single linear order was inefficient and produced the step-6/step-7 contradiction. Replaced.

**Step 0 — this document plus P0-G0.** No new scientific runs before the protocol is frozen.

| workstream | contents | notes |
|---|---|---|
| **A — positioning** | **P0-G10 starts immediately**, not last | a provisional memo early; if novelty is too narrow this redirects effort *before* expensive analyses |
| **B — mathematics and limits** | P0-G6 + P0-G8 together | derive response and objective limits; separate the two shoulders; prove the identity; test it against MAPE |
| **C — target information and policy** | P0-G9 → P0-G4 → P0-G5, in that order | the map protocol must settle before policy performance means anything; the free-fit domain before free-vs-constrained comparison |
| **D — prospective design** | P0-G7, after B defines the diagnostics | includes the observation-operator experiment below |

**Convergence:** final P0-G1, P0-G2, P0-G3 reconciliation only after all analyses are frozen; then
final P0-G10; then drafting and R0–R5.

### 8.1 The decisive addition: a synthetic observation-operator comparison

This is the single most valuable new analysis the review proposes, and it is what turns the paper
from a retrospective audit into a general result. Using the declared model with **known**
parameters, generate:

- time-resolved fractionated observations resembling the source kinetic campaign;
- one whole-cup endpoint per condition;
- multiple endpoint masses from matched shots;

with **equalised observation counts** and predeclared noise and mismatch. Profile the level and `κ`
under each design.

**It is falsifiable, and that is the point.** If time-resolved observations recover `κ` while
whole-cup endpoints do not, the observation-compression explanation is directly supported. **If
neither localises `κ`, the explanation is wrong** and the thesis must move toward deeper structural
compensation. Either outcome is publishable; the current plan cannot distinguish them.

### 8.2 A scientific opportunity in P0-G9

Rather than treating target information as an embarrassment, ask the operationally useful question:
**how much cheap target-grind hydraulic information is needed before source-calibrated chemistry
predictions improve?** An adaptation curve — zero, one, two, several, full target measurements —
would make H3 prospective instead of retrospective.

### 8.3 Drafting rule

**May proceed now:** methods source notes, data provenance, derivations, numerical appendix — as
**standalone controlled artefacts**, not manuscript sections.
**May not proceed:** results narrative, title, abstract, discussion, contribution list — until every
blocking gate closes, **P0-G10 included**.

---

## 9. Review plan

§9.1–9.6 are carried from v2 unchanged: evidence matched to premise type; the five-part termination
rule; editorial rounds may always flag factual errors; R3 scoped to one machine; the
claim–premise–test matrix; estimand tags (`FULL-PUB`, `FULL-WIDE`, `LOCO-PUB`, `LOCO-WIDE`,
`NUM-FULL`).

### 9.7 New: mechanical plan-integrity check

v2's defects were all mechanically detectable — stale gate ids, a self-contradicting sequence, a
banned phrase, a miscounted list. A test now scans the **operative** plan for:

- deprecated terminology (unqualified "extraction rate", "cannot localize", "hydraulic attribution",
  unqualified "saturation", "physical verification" of a numerical result);
- bare legacy gate ids (`G3`/`G4`/`G5`) that collide with the `P0-G*` scheme;
- gate ids referenced but not defined, and vice versa;
- internal contradictions in the drafting rule.

A plan whose own controls disagree cannot enforce anything, and I should not be the one checking
that by eye.

---

## 10. Risks

| risk | severity | mitigation |
|---|---|---|
| ~~Plateau is a BDF artefact~~ | ~~fatal~~ | retired — `NUM-TIME-01` |
| Real espresso does not occupy the large-coefficient regime | high — bounds H1 | scope every statement to the declared model; state the external-validation gap |
| **`J_inf` may lie above the tolerance, making profiles bounded after all** | **high — could reverse H1's headline** | P0-G8, first |
| Target map unavailable prospectively, or uses scored-condition hydraulics | high — changes the use case | P0-G9 provenance plus held-out and limited-adaptation maps |
| Weighted-L2 geometry does not predict MAPE profiles | high — removes H2's practical role | P0-G6 direct validation with a designed failure case |
| The 10 % threshold drives the 5/6 classification | high — H1 wording | `J_inf` plus threshold family |
| **Post hoc selection among anchors, penalties, losses, maps, designs** | **high — optimistic bias** | **P0-G0 freeze**, nested selection, deviation log |
| Dependent folds read as independent uncertainty | high | descriptive language retained |
| Static map hides time-varying permeability, fines, poroelasticity, channeling | high — model form | map-form sensitivity; explicit scope; external literature |
| Fine-grind common-map advantage is error cancellation | high — H3 interpretation | condition-level residual and map-perturbation analysis |
| H1/H2/H4 and H3 do not form one paper | high — publication | the §2 narrative spine; branch decision after P0-G9 |
| Exact algebra presented as novelty despite variable-projection literature | reputational | early P0-G10; narrow language |
| "Useful" or "competitive" asserted without a comparator | moderate | declare comparators or report numbers without adjectives |
| Artefact, prose and manuscript claims diverge again | high — governance | generated claim ledger, cross-file tests, §9.7 |

---

## 11. Provisional contribution statement

Deliberately provisional; to be shortened or weakened if P0-G6…G10 do not support every clause.

> This study separates endpoint prediction from kinetic parameter identification in a whole-cup
> espresso extraction model. For a multiplicative inventory–multiplier factorisation it derives an
> exact weighted sensitivity-spread identity and distinguishes the Gram determinant from the
> profiled local weighted-L2 curvature. It characterises the model's large-mass-transfer-coefficient
> endpoint limit and determines when the asymptotic profiled objective permits one-sided practical
> localisation under declared operational tolerances. Refit-aware cross-grind ablations show that
> substituting a campaign-specific target-grind flow map has a stable effect for coarse targets but a
> near-zero, heterogeneous, usually opposite effect for fine targets. Synthetic observation-operator
> and limited-adaptation studies test which additional measurements improve kinetic localisation and
> which target-side hydraulic data improve conditional prediction. All conclusions are scoped to the
> declared model, objective, information protocol, machine, coffees and campaign.

---

## 12. Immediate sequence

1. **P0-G0** — freeze the analysis protocol. *Nothing else starts first.*
2. **Workstream A** — begin P0-G10 positioning in parallel from day one.
3. **Workstream B** — P0-G8 (`J_inf` and the two shoulders) then P0-G6 (H2 validation).
4. **Workstream C** — P0-G9 → P0-G4 → P0-G5.
5. **Workstream D** — P0-G7 including §8.1.
6. Reconciliation: P0-G1, P0-G2, P0-G3; final P0-G10.
7. Drafting per the architecture in the review's §12; then R0–R5.

**P0-G8 is first among the analyses** because `J_inf` can reverse H1's headline classification, and
it is now cheap: the operator is linear and the exact-in-time path already exists.
