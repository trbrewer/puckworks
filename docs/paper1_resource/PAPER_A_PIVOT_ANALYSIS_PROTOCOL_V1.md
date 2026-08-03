# Paper A — pivot analysis protocol, version 1

**Gate:** P0-G0. Frozen **before** P0-G4 … P0-G9 run.
**Operative plan:** `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md`
**Deviation policy:** append-only. Every later change is dated, justified, and accompanied by an
impact statement. Deviations are never absorbed silently.

---

## 0. The statement that must accompany every result

> **This protocol was frozen after exploratory inspection of the existing campaign.** It limits
> further analytical flexibility and selective reporting. It does **not** provide independent
> confirmation of hypotheses that were generated from the same data.

Every analysis below carries one of these labels, and the manuscript must use them:

| label | meaning |
|---|---|
| **post-selection frozen reanalysis** | same campaign, protocol frozen after the hypothesis was formed — P0-G4, G5, G6, G8, G9 |
| **prospective model-based study** | synthetic, declared model, no new empirical claim — P0-G7 |
| **cross-fitted prospective-protocol emulation** | scored condition excluded from map construction, but same campaign — P0-G9 variants |
| **genuinely prospective empirical test** | data collected *after* this freeze — **none currently exists** |

---

## 1. Hypotheses

**Primary:** H1 (asymptotic classification), H2 (exact geometry and its relevance), H3 (target-map
substitution, grind-specific), H4 (estimation policy). Wordings are fixed in the operative plan §2.

**Secondary:** the design-screen ranking (C-PRO-01) and the observation-operator comparison.

No hypothesis may be added after a result is seen without a dated deviation entry.

---

## 2. Frozen conventions

### 2.1 Objectives

- **Primary:** MAPE, with the exact weighted-median level minimiser (no optimiser).
- **Sensitivity family:** relative-L2, SSE, Huber. These are **sensitivity objectives, not
  interchangeable likelihoods**, and no probabilistic statement follows from any of them.

### 2.2 Operational near-optimal tolerances

Relative: **5 %, 10 %, 20 %**. Absolute: **+0.10 pp** and **+0.25 pp** of MAPE.
The 10 % relative rule remains the headline convention *only* if the classification is invariant
across the family; otherwise the result is reported as threshold-dependent.

**Near-zero `J_min`:** if `J_min < 0.05` pp the relative ratio is declared unstable and only the
absolute convention is used. This is predeclared because noiseless synthetic controls can produce
`J_min ≈ 0`.

### 2.3 Multiplier domains

- **PUB:** `geomspace(0.15, 6.5, 18)` — the published grid.
- **WIDE:** `geomspace(0.15, 500, 40)`.
- Any finite optimum is refined by a bracketed 1-D search; a grid argmin alone is not a reported
  optimum.

### 2.4 Estimand tags

`FULL-PUB`, `FULL-WIDE`, `LOCO-PUB`, `LOCO-WIDE`, `NUM-FULL`. Every reported number carries exactly
one. **No number may migrate between tags without a like-for-like re-run.**

### 2.5 Aggregation

Macro mean over the six variety–solute groups within a grind; pooled = equal-weight mean of coarse
and fine **within each fold**; fold summaries are medians over nine **dependent** folds. The pooled
median is never reconstructed from component medians.

### 2.6 Determinism

Seeds fixed per analysis and recorded in each archive. Environment, package versions and input
hashes recorded. Failures are logged and retained, never dropped.

---

## 3. Analysis-specific freezes

### 3.1 P0-G8 — asymptotic classification

Compute `f_inf` (derived or rigorously converged), profile `I` exactly at the limit, obtain `J_inf`.
Classify each group against each tolerance `T` with a verified numerical error band `ε`:

- `J_inf < T − ε` → **tail_included**
- `J_inf > T + ε` → **tail_excluded**
- `|J_inf − T| ≤ ε` → **boundary_indeterminate**

`ε` is derived from the asymptotic and profiling error, **not** from display precision. Report all
connected components of the near-optimal set, not just its endpoints. The **response shoulder**
(`|∂log ŷ/∂log κ|` crossing a declared threshold) is reported **separately** from the profile
boundary — they are different objects and one `κ` value must not serve both.

### 3.2 P0-G6 — RSI admission

Predeclared: designs, groups, `κ` locations (nominal 1, each group optimum, and points spanning each
acceptable profile), weight convention, profile-width definition including censored profiles.

**Primary metric:** pairwise rank concordance between RSI and inverse exact-MAPE profile width,
reported **stratified by group and `κ`**, never as one pooled correlation.

**Admission criterion, frozen now:** RSI is retained as an ordinal screen only if concordance is
positive in at least **5 of 6 groups** *and* holds at both nominal and optimum `κ`. Otherwise the
algebra is retained and the practical design-ranking claim is removed. A regime-dependent result is
reported as regime-qualified, not globally.

**Controls, both required:** a positive control where the surrogate should work; a negative control
driven by MAPE median switching.

### 3.3 P0-G9 — target map

**Mandatory variants:** current campaign-conditioned map; common O-grind map; **scored-condition-
excluded (cross-fitted) map wherever raw support permits**.
**Mandatory declaration:** any variant that cannot be constructed, and why.
**Mandatory consequence:** if a defensible cross-fitted map cannot be built, **H3 remains
retrospective** and is removed from the title and contribution list.

Adaptation counts and placements are frozen before scoring; if placement is selected, selection is
nested entirely within hydraulic/calibration support. **No target chemical outcome or score may
influence map form, adaptation count, or placement.**

Per prediction row record: which hydraulic observations fitted the map; whether the scored condition
contributed; availability timing (pre-shot / contemporaneous / post-shot); measured vs fitted vs
derived; uncertainty; extrapolation leverage.

### 3.4 P0-G5 — policy comparison, two axes

**Axis A — point estimation:** free-WIDE fit; fixed anchors `κ ∈ {0.5, 1, 2}`; regularised fit
toward `κ = 1` over a frozen penalty grid `λ ∈ {0.01, 0.1, 1, 10}`; independently constrained fit
only if a genuinely external constraint exists.

**Axis B — propagation:** point only; operational-profile envelope; objective-family envelope.

**Tuning rule, mandatory:** either fully nested selection within calibration support, **or** the
frozen no-tuning grid above with **every** candidate reported and no post hoc winner. With nine
conditions nested selection may be unstable — **that instability is a result and is reported**, not a
reason to tune on target scores.

Axis A and Axis B are **never ranked against each other**: a point prediction scored by MAPE and an
envelope with no coverage interpretation are different objects.

### 3.5 P0-G7 — observation-operator study, staged

1. **Noiseless positive controls** — demonstrate the pipeline recovers `I` and `κ` under a design
   known to contain the information. Failure here is a code defect, not a finding.
2. **Same-model recovery** — whole cup; multiple endpoints from matched shots; fractionated;
   optionally combined. True `κ` **below, near and above** the shoulder.
3. **Correlated, heteroscedastic noise** — shot-to-shot, within-shot fraction correlation, assay,
   flow/endpoint, map uncertainty, modelled separately.
4. **Declared mismatch** — separate fine/coarse multipliers; time-varying flow; wrong map;
   grind-dependent geometry; a reduced dynamic-permeability discrepancy term.
5. **Resource-equated budgets** — shots, assays, samples, operator-time index. **Equal observation
   counts are not equal budgets** and are not used as the comparison basis. Report a Pareto frontier.

**Interpretation, frozen:** improvement from time resolution **supports** the observation-compression
explanation *within the tested model class*. Failure to improve does **not** falsify it; it triggers
a branch assessing design adequacy, structural compensation, and mismatch. Publication value is not
asserted for either branch.

### 3.6 P0-G4 — LOCO-WIDE

Every arm × map protocol × objective × fold predeclared. Exact level profiling; global `κ` profile;
complete failure logs. No `FULL-WIDE` number may stand in for a fold median.

---

## 4. Withdrawal rules

Declared now, so that a negative result is not renegotiated later.

| if | then |
|---|---|
| `J_inf` excludes the upper tail, or classification is threshold-dependent | H1's broad weak-localisation headline is removed; lead with the response limit and threshold dependence |
| RSI fails its admission criterion | design-ranking claims removed; algebra and exact MAPE profiling retained |
| cross-fitted map cannot be built, or the coarse benefit collapses under it | H3 demoted to a retrospective case study; removed from title and contribution list |
| no policy wins under calibration-only selection | H4 reports "no clear winner"; no recommendation is made |
| time-resolved operator does not improve recovery under adequate controls | the observation-compression narrative is not forced; branch to structural compensation or design adequacy |
| P0-G10 finds the integrated contribution too narrow | narrow, split, or terminate — a positive novelty finding is not required |

---

## 5. Reporting rules

- Every pooled figure appears with its coarse/fine components and the weighting rule **on the same
  page**.
- No adjective without a declared comparator: "competitive", "useful", "large", "strong" are banned
  unqualified. Report the number.
- No causal "because" linking the map to predictive stability until a mechanism is tested.
- Dependent folds are described, never treated as independent uncertainty.
- Every archive records its estimand tag, evidence type, seeds, hashes, and failure counts.
