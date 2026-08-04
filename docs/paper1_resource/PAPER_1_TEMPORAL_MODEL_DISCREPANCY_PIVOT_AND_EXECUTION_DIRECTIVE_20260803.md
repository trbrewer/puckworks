# Paper 1 — Scientific viability review and temporal-model-discrepancy pivot

**Date:** 3 August 2026  
**Repository:** `trbrewer/puckworks`  
**Reviewed viability head:** `a63c8c97ea2f96033132441abe92edd33bd542e0`  
**Reviewed tree:** `0ee2bcf2df43aa974a29370303d6daaaa3d2696e`  
**Status of formal programme:** P0-G0, P0-G7, P0-G8, and P0-G9 remain open; plan remains candidate

---

## 1. Disposition

```text
PAPER1_VIABILITY_NUMERICAL_RESULTS_ACCEPTED
ORIGINAL_PREDICTION_NOT_EQUAL_KINETIC_IDENTIFICATION_THESIS_RETIRED
PART_A_UNIVERSAL_ENDPOINT_HEADLINE_REJECTED
PART_B_OPERATOR_INFORMATION_CONCLUSION_NOT_ESTABLISHED
STOP_PAPER_1_AND_REPURPOSE_NOT_ACCEPTED_AS_FINAL_DISPOSITION
PIVOT_TO_TEMPORAL_MODEL_DISCREPANCY_SCREEN
ONE_FINAL_SCIENTIFIC_SCREEN_AUTHORIZED
ALL_NONESSENTIAL_GOVERNANCE_REMAINS_PAUSED
NO_FORMAL_P0_GATE_AUTHORIZED
NO_MANUSCRIPT_REDRAFT_AUTHORIZED
```

> The planned Paper 1 does not survive the viability screen. That is a useful result, not a failure.
>
> The broader Paper 1 programme should not yet be terminated. The screen exposes a more defensible
> scientific lead: the current model reproduces smoothed/integrated quantities while exhibiting a
> structured late-stage error against raw fraction-resolved observations.
>
> One bounded solver-focused screen is authorized to determine whether that lead supports:
>
> 1. a strong temporal-validation paper;
> 2. a narrower solver/model-discrepancy note; or
> 3. complete termination of Paper 1.

No further governance cycle is authorized before that scientific decision.

---

# 2. Review of the viability screen

## 2.1 Part A — accepted as a negative result for a universal headline

The six-group endpoint calculation is accepted numerically:

| group | `J_ref` | `J_inf` | scientific reading |
|---|---:|---:|---|
| Arabica:caffeine | 2.8319 | 2.9945 | included at 10% relative; excluded at 0.10 pp |
| Arabica:trigonelline | 2.2431 | 2.2771 | endpoint accepted under all reported conventions |
| Arabica:5CQA | 4.6056 | 5.0944 | endpoint excluded under four of five conventions |
| Robusta:caffeine | 4.8934 | 4.8998 | endpoint accepted |
| Robusta:trigonelline | unresolved | 3.8630 | finite reference minimum unresolved because profile is flat to the boundary |
| Robusta:5CQA | unresolved | 11.7653 | finite reference minimum unresolved because profile is flat to the boundary |

The programme label `H1_DOES_NOT_LEAD` follows the frozen rule. The scientific interpretation is more
specific:

- the large-rate endpoint is **not uniformly acceptable**;
- the behavior is solute- and variety-dependent;
- the two flat Robusta profiles are not evidence that the endpoint is physically excluded; they are
  evidence that the finite reference minimum is not numerically distinguishable over a broad upper
  region;
- margins of `0.02–0.06 pp` cannot support a quantitative empirical claim without per-solute
  replicate uncertainty.

Part A should be retained as a supporting negative/heterogeneity result, not used as the lead of a
paper.

## 2.2 Part B — the declared 0/3 rule result is accepted, but its interpretation is not

The following calculations are accepted as faithfully implementing the exploratory rule:

- no solute met the declared `0.5`-decade localization-improvement threshold;
- relative and absolute accepted-width conventions reverse the operator ordering;
- the current model fits the fraction-resolved shapes substantially worse than the cumulative targets;
- late fraction residuals are structured and predominantly negative;
- high-rate positivity failures are real and are now excluded rather than silently averaged.

However, the statement that held-out prediction “settles” the observation-operator question is not
supported.

### Source-lineage problem

The `CUP_CURVE_3` targets are not independent directly measured cup concentrations. In the source
study, cup component masses at brew ratios 1/1, 1/2, and 1/3 were calculated from each replicate's
fitted extraction-kinetics curve: the measured first fraction was combined with the integral of the
fitted exponential curve over the remainder of the beverage mass.

Therefore `CUP_CURVE_3` is:

```text
a derived, fitted, smoothed functional of the fraction campaign
```

not:

```text
an independent cumulative measurement operator
```

This matters because a smoothed integrated target is intrinsically easier for a smooth mechanistic
model to match than raw interval concentrations. A `1.3–1.6 pp` error on that derived curve and a
`6–12 pp` error on raw fractions are not directly comparable measures of how much kinetic
information the observation operators contain.

### Cross-arm scoring problem

The leave-one-experiment-out analysis scores:

- later raw interval concentrations for `FRACTION_6`; and
- later integrated/smoothed derived quantities for `CUP_CURVE_3`.

The targets differ in noise, smoothing, dimensional aggregation, and source construction. The
difference in held-out MAPE is robust evidence of **model discrepancy against raw temporal shape**.
It is not convention-free evidence that cup observations contain more kinetic information.

### Correct Part B conclusion

Permitted:

> Under the current model, the localization comparison between raw fractions and derived cumulative
> targets is tolerance-dependent, while raw fraction observations expose a substantial structured
> late-stage model discrepancy that the integrated targets suppress.

Not established:

> Fraction observations fail to recover kinetic information that cup observations retain.

Also not established:

> The motivating observation-operator hypothesis is contradicted in principle.

An independent operator comparison would require directly measured cumulative quantities or a
matched generative/error model that accounts explicitly for the derivation and covariance of the
integrated targets.

---

# 3. Corrected scientific decision

## 3.1 Retire the original Paper 1 thesis

Retire as a primary claim:

> Prediction is not kinetic identification because whole-cup observations broadly admit the
> large-rate endpoint, while fraction-resolved observations restore rate localization.

The available evidence does not support that combined claim:

- Part A is heterogeneous and threshold-sensitive;
- Part B does not show a material, convention-robust localization gain;
- the cumulative comparator is derived from the same kinetics campaign;
- the current model does not reproduce the raw temporal shape well enough to cleanly test the
  observation-information hypothesis.

## 3.2 Preserve the strongest surviving lead

The strongest supported lead is:

> Validation against cumulative or integrated extraction metrics can materially understate temporal
> model discrepancy. The current two-grain espresso model closely matches source-derived integrated
> cup quantities while systematically under-predicting late fraction concentrations.

This is a solver/model-validation question, not a governance question.

## 3.3 Provisional paper thesis

Use only as a hypothesis for the next screen:

> **Whole-cup agreement is not temporal validation: late-stage model discrepancy in espresso
> extraction.**

Alternative:

> **Cumulative extraction metrics can conceal late-stage model error in espresso brewing.**

A paper is justified only if the late-tail effect is shot-consistent and a minimal physically
interpretable extension improves held-out fraction predictions without sacrificing integrated
performance or physical admissibility.

---

# 4. Branch and interpretation correction

## 4.1 Do not merge the current decision text unchanged

The numerical artefacts at `a63c8c9` should be preserved. Before eventual merge, correct only the
interpretation:

- replace final disposition `STOP_PAPER_1_AND_REPURPOSE` with
  `PIVOT_TO_TEMPORAL_MODEL_DISCREPANCY_SCREEN`;
- rename or annotate `CUP_CURVE_3` as
  `DERIVED_CUMULATIVE_CURVE_3`;
- record that the source generated these targets by integrating fitted extraction kinetics;
- remove wording that held-out cross-arm MAPE “settles” operator information;
- retain every numerical value and plot;
- retain the conclusion that the original planned thesis does not proceed.

This is a scientific source-lineage correction, not a new assurance cycle.

## 4.2 Working branch

Create:

```text
paper1/temporal-model-discrepancy-screen
```

from exact viability head:

```text
a63c8c97ea2f96033132441abe92edd33bd542e0
```

Do not return for an intermediate review. Complete the full screen below and then report the
scientific decision.

---

# 5. Temporal-model-discrepancy screen

## Phase 1 — establish the source-derived baseline

### 5.1 Reconstruct the cumulative targets

Reproduce the source calculation for every admitted replicate and solute:

```text
cup mass at BR
  = measured first-fraction contribution
    + integral of the replicate-fitted extraction-kinetics curve
```

Verify the reconstructed values against `cup_masses.csv`.

Required output:

```text
max absolute reconstruction error
max relative reconstruction error
number of rows reproduced
all deviations and their cause
```

Label the targets:

```text
DERIVED_FROM_FITTED_KINETICS
NOT_AN_INDEPENDENT_CUP_MEASUREMENT
```

### 5.2 Quantify smoothing/aggregation

For each solute, quantify how the source integration changes the raw data:

- variance of raw fraction residuals;
- variance of cumulative/integrated residuals;
- attenuation of shot-to-shot noise;
- covariance introduced by using one fitted kinetic curve to generate all three brew ratios;
- correlation among the three cumulative targets.

This explains how much of the low cumulative error is attributable to aggregation and source
smoothing.

---

## Phase 2 — determine whether the late-tail discrepancy is robust

Use the primary `GL 1.7` set:

```text
16 shots
5 experiments
3 solutes
fractions 1,2,3,5,7,10
```

Retain the 45-shot all-grind analysis only as a labelled sensitivity.

### 5.3 Shot-level residual analysis

For the current solver, report by solute and fraction:

```text
mean signed relative residual
median signed relative residual
mean absolute relative residual
shot-level negative-residual fraction
experiment-cluster bootstrap 95% interval
```

Cluster by experiment, not by individual fraction row.

Define late fractions:

```text
fraction 7
fraction 10
```

Report both separately and jointly.

### 5.4 Robust late-tail criterion

The discrepancy is considered robust for a solute when:

1. at least 70% of admitted shots have negative residual at fraction 7 or 10;
2. the experiment-cluster bootstrap interval for the mean late residual excludes zero in the
   negative direction; and
3. the mean absolute late residual is at least `2 pp`.

The temporal-tail lead survives when this holds for at least two of the three solutes.

These are exploratory decision thresholds, not inferential confidence limits.

### 5.5 Separate model error from first-point anchoring

Repeat the residual analysis under:

1. exact per-shot full-curve level profiling;
2. first-fraction anchoring;
3. a common level per solute across training shots.

A late-tail pattern that exists only under one level convention is not a robust model-discrepancy
result.

---

# 6. Benchmark models

Compare the current mechanistic solver with two deliberately limited benchmarks.

## 6.1 Source single-exponential benchmark

Use the source's declared extraction-kinetics form.

Purposes:

- establish what the source-fitted curve can reproduce in raw fractions;
- explain the construction of the derived cumulative targets;
- provide a lineage baseline, not an independent validation result.

## 6.2 Flexible two-timescale empirical benchmark

Use one of:

```text
positive biexponential decay
```

or:

```text
positive stretched exponential
```

Select the form before fitting and keep it fixed.

Constraints:

- positive predictions;
- monotone non-increasing concentration;
- no negative inventory or cumulative mass;
- limited shared parameters across shots;
- no per-fraction free parameters.

Purpose:

> determine whether a second timescale or broad rate distribution is sufficient to represent the
> observed late tail.

This benchmark is diagnostic. It is not the proposed final mechanistic model.

---

# 7. One minimal mechanistic extension

Implement exactly one extension after the benchmark result is known.

## Slow-tail subpopulation extension

Extend the current model with a positive, mass-conserving slow-accessible inventory subpopulation:

```text
total initial solute inventory
  = (1-alpha_slow) base population
    + alpha_slow slow population

0 <= alpha_slow <= 0.5
0 < rate_ratio_slow <= 1
```

The slow population uses the same transport structure but a reduced interphase-transfer rate:

```text
kappa_slow = rate_ratio_slow * kappa_base
```

Requirements:

- weights sum to one;
- initial total inventory unchanged;
- concentrations and cumulative extracted mass remain nonnegative;
- cumulative extracted mass cannot exceed initial inventory;
- no shot-specific slow-tail parameters in the primary analysis;
- `alpha_slow` and `rate_ratio_slow` are common by solute across training experiments;
- level/inventory nuisance treatment remains the same as the baseline comparison.

This extension represents unresolved rate heterogeneity or a slowly accessible particle/inventory
fraction. Do not claim that it uniquely identifies fines, permeability evolution, or any other
physical mechanism.

No second mechanistic extension is authorized in this screen.

---

# 8. Cross-validation

Use leave-one-experiment-out validation.

For each solute and model:

1. fit shared kinetic/slow-tail parameters on the training experiments;
2. set held-out shot level from fraction 1;
3. predict fractions 2,3,5,7,10;
4. report all-fraction and late-fraction errors.

Primary metrics:

```text
held-out all-fraction MAPE
held-out late-fraction MAPE for f7/f10
held-out signed late residual
failed-fit count
positivity violations
mass-conservation violations
```

Secondary metric:

```text
error in the source-derived cumulative targets
```

Do not use the derived cumulative metric as the principal model-selection score.

Also report parameter stability across folds:

```text
kappa_base
alpha_slow
rate_ratio_slow
```

A boundary-pinned extension is not interpreted mechanistically.

---

# 9. Decision rules

## `PROCEED_TEMPORAL_VALIDATION_PAPER`

Select when all conditions hold:

1. the robust late-tail criterion is met for at least two solutes;
2. the slow-tail extension reduces held-out late-fraction MAPE by both:
   - at least 30% relative; and
   - at least `2 pp` absolute;
3. held-out all-fraction MAPE improves for at least two solutes;
4. source-derived cumulative-target MAPE worsens by no more than `0.5 pp`;
5. no positivity or mass-conservation failure occurs;
6. fitted slow-tail parameters are not boundary-pinned in most folds.

Candidate thesis:

> A model that appears accurate under integrated espresso metrics can retain a systematic late-stage
> temporal error; a minimal slow-accessible inventory resolves much of that discrepancy.

## `PROCEED_TEMPORAL_DISCREPANCY_NOTE`

Select when:

- the late-tail discrepancy is robust for at least two solutes; but
- the minimal extension does not satisfy the full improvement rule, is unstable, or cannot support a
  unique mechanistic interpretation.

Output:

> a concise validation/methods note documenting the masking effect and the solver-development target.

## `SOLVER_DEVELOPMENT_ONLY`

Select when:

- the late residual exists but is not sufficiently consistent for a publication claim; or
- improvements depend strongly on level policy, objective, or a small number of experiments.

Retain the result as a solver backlog item.

## `STOP_PAPER_1`

Select when:

- the cluster-bootstrap and shot-sign analyses do not confirm a robust late-tail discrepancy for at
  least two solutes; or
- neither the empirical two-timescale benchmark nor the mechanistic extension improves held-out raw
  fraction predictions.

At that point, close Paper 1 and retain the exploratory artefacts as a negative scientific record.

---

# 10. Required artefacts

Use:

```text
docs/paper1_resource/exploratory/temporal_discrepancy/
```

Required files:

```text
PAPER_1_TEMPORAL_DISCREPANCY_DECISION_V1.md
PAPER_A_CUP_TARGET_LINEAGE_AUDIT_V1.json
PAPER_A_TEMPORAL_RESIDUAL_ROBUSTNESS_V1.json
PAPER_A_TEMPORAL_MODEL_COMPARISON_V1.json
PAPER_A_TEMPORAL_MATCHED_DATA_MANIFEST_V1.json
figures/
```

Required figures:

1. shot-level residual heatmap by solute and fraction;
2. mean residual with cluster-bootstrap intervals;
3. observed versus predicted fraction curves for representative and worst cases;
4. held-out late-fraction error by model and solute;
5. integrated-target error versus raw-fraction error;
6. fitted slow-tail parameter distributions across folds;
7. cumulative mass and positivity checks.

Every artefact must state:

```text
EXPLORATORY_SCIENTIFIC_SCREEN
NOT_A_FORMAL_P0_GATE_RESULT
```

---

# 11. Scope restrictions

Do not perform:

- P0-G0 freeze or activation;
- formal P0-G8 execution;
- PR-07 or PR-09 completion;
- claim-ledger or scanner expansion;
- novelty review;
- manuscript drafting;
- title optimization;
- CI-timeout work;
- a second mechanistic extension;
- new experimental-data acquisition.

Implement only what is required to run and reproduce this screen.

---

# 12. Required terminal disposition

Return exactly one of:

```text
PAPER1_TEMPORAL_DISCREPANCY_SCREEN_COMPLETE
```

or:

```text
PAPER1_TEMPORAL_DISCREPANCY_SCREEN_BLOCKED
```

The complete response must include:

- branch head and tree;
- changed paths;
- source-derived cup reconstruction accuracy;
- shot-level late-tail robustness by solute;
- benchmark and mechanistic-model held-out metrics;
- positivity and mass-conservation results;
- selected decision branch;
- links/paths to every JSON, Markdown, and figure;
- test and lint results;
- all exclusions and failures;
- confirmation that formal gates remain open;
- confirmation that no formal P0 result archive was created.

No intermediate review is required. Return only after the full scientific screen is complete.
