# Paper 1 — Exact-head acceptance and scientific viability screen authorization

**Date:** 3 August 2026  
**Repository:** `trbrewer/puckworks`  
**Pull request:** #224  
**Accepted exact head:** `6fcab844993d3834909984398d4f12abd28aeb0c`  
**Accepted tree:** `ea39fb190aea84654d718fbb1568a4fb90c30b58`  
**Purpose:** stop the assurance/governance loop and determine whether Paper 1 has a compelling scientific result

---

## 1. Disposition

```text
PR03A_FORMAL_ASSURANCE_CORRECTION_EXACT_HEAD_ACCEPTED
PR224_EXACT_HEAD_MERGE_AUTHORIZED
MERGE_METHOD=MERGE_COMMIT
P0_G0_AND_P0_G8_REMAIN_OPEN
PLAN_REMAINS_CANDIDATE
FORMAL_FREEZE_AND_ACTIVATION_PAUSED
ALL_NONESSENTIAL_GOVERNANCE_PAUSED
PAPER1_EXPLORATORY_SCIENTIFIC_VIABILITY_SCREEN_AUTHORIZED
TWO_DECISIVE_ANALYSES_REQUIRED_IN_ONE_CAMPAIGN
```

The corrected PR-03a basis is accepted:

- the fixed-positive-time bound is homogeneous in the initial state;
- rank is declared from the model structure and verified at that cut;
- scaled defective-zero fixtures fail closed;
- the endpoint construction and 54-cell coverage are retained;
- the finite-κ sequence is a diagnostic, not the proof;
- the WIDE-reference architecture is unchanged.

This acceptance is sufficient to run the scientific viability screen. It is not a claim that every
publication-assurance task is complete.

---

## 2. Merge and branch transition

Merge exact head without squash or rebase:

```bash
gh pr merge 224 \
  --merge \
  --match-head-commit 6fcab844993d3834909984398d4f12abd28aeb0c
```

After merge:

```bash
git switch main
git pull --ff-only
git status --short
git switch -c paper1/scientific-viability-screen
```

The merge must preserve:

```text
operative_status = candidate
P0-G0 = open
P0-G8 = open
```

Do not create freeze commit F or activation commit A.

---

## 3. Governing principle for the next campaign

This campaign is **exploratory and decision-oriented**.

It answers:

1. Does the analytical large-rate endpoint remain operationally acceptable for the six existing
   Paper 1 groups?
2. Do fraction-resolved observations provide materially more information about the mass-transfer-rate
   multiplier than cumulative/whole-cup observations from the same experimental campaign?
3. Taken together, do those results support a strong paper, a narrower observation-design paper, or
   stopping Paper 1?

The campaign must produce results, plots, and a decision. It must not produce another protocol,
ledger, gate system, assurance memo, novelty review, or manuscript redraft.

---

# Part A — Existing-campaign WIDE-reference endpoint result

## 4. Scientific question

For each of the six existing variety–solute groups, determine whether the analytical `κ = ∞`
endpoint remains inside the operational tolerance referenced to the best finite fit on:

```text
D_WIDE = [0.15,500]
```

Use the accepted definitions:

```text
J(κ)  = min over I > 0 of MAPE(y, I f(κ))
J_ref = min over κ in D_WIDE of J(κ)
J_inf = min over I > 0 of MAPE(y, I f_inf)
```

Use the existing threshold families without alteration:

```text
T_rel(q) = (1+q) J_ref, q in {0.05,0.10,0.20}
T_abs(a) = J_ref+a,     a in {0.10,0.25} percentage points
```

Per convention:

```text
U_inf < L_T  -> endpoint_included
L_inf > U_T  -> endpoint_excluded
otherwise    -> endpoint_indeterminate
```

Use the accepted `FULL-WIDE-ENDPOINT` estimand and the existing programme rule. Do not estimate a
finite tail onset.

## 5. Required Part A outputs

For each group, report:

```text
group
J_ref and interval
κ_ref or all tied reference basins
J_inf and interval
J_inf - J_ref
J_inf / J_ref
endpoint-to-threshold margin under every convention
endpoint_classification under every convention
reference_minimum_status
finite_wide_topology_status
eventual_upper_status
```

Produce:

1. one six-row results table;
2. one profile figure per group showing:
   - finite WIDE profile;
   - `J_ref`;
   - 10% relative and 0.25-pp absolute thresholds;
   - analytical endpoint marker;
3. one compact six-panel summary figure;
4. one plain-language interpretation limited to what the results show.

## 6. Part A implementation rule

Use the accepted code and constants. No result-dependent change to:

- `D_WIDE`;
- grids;
- tolerances;
- thresholds;
- H1 rules;
- endpoint construction;
- error allocation.

Do not write or modify the formal P0-G8 archive:

```text
PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json
```

Use explicitly exploratory paths, for example:

```text
docs/paper1_resource/exploratory/PAPER_A_VIABILITY_ENDPOINT_V1.json
docs/paper1_resource/exploratory/PAPER_A_VIABILITY_ENDPOINT_V1.md
docs/paper1_resource/exploratory/figures/endpoint_*.png
```

Every exploratory artefact must state:

```text
EXPLORATORY_SAME_CAMPAIGN_VIABILITY_SCREEN
NOT_A_FROZEN_P0_GATE_RESULT
```

---

# Part B — Observation-operator comparison

## 7. Scientific question

Using the same kinetic model and the same experimental campaign, determine whether temporal
fraction observations localize the common rate multiplier more strongly than cumulative cup
observations.

Use the Schmieder/Pannusch lineage because it contains both:

- per-replicate fraction concentrations and fraction/accumulated beverage masses; and
- per-replicate cumulative cup concentrations at brew ratios 1/1, 1/2, and 1/3.

The Pannusch solver already carries cumulative beverage volume and cumulative solute mass, so one
model integration can generate interval-average and cumulative-cup observation operators.

## 8. Matched evidence unit

Build the exact intersection:

```text
experiment × replicate × solute
```

for:

```text
caffeine
trigonelline
5-CQA
```

Use only shots with complete required observations. Report exclusions and never impute a chemical
measurement.

Use:

- measured/scale flow where available;
- measured beverage temperature where available;
- the actual grind level and the corresponding declared grind parameters;
- the source's 20-g dose and brew-ratio definitions;
- beverage density consistently with the solver.

Derive measured-fraction time windows from beverage mass and actual flow. Retain the exact formulas
and a row-level mapping table.

## 9. Observation arms

Run all three arms.

### ARM F — `FRACTION_6`

Six measured interval concentrations:

```text
fractions 1, 2, 3, 5, 7, 10
```

### ARM C — `CUP_CURVE_3`

Three cumulative cup concentrations:

```text
brew ratios 1/1, 1/2, 1/3
```

### ARM E — `CUP_FINAL_1`

The final cumulative cup concentration:

```text
brew ratio 1/3 only
```

`CUP_FINAL_1` is an analytical negative control. With one observation and one free level per shot,
the rate profile should be flat by construction. Prove and test that result rather than presenting it
as an empirical surprise.

## 10. Shared model and nuisance structure

For every arm:

- apply one common mass-transfer-rate multiplier `κ` to both fine- and coarse-grain interphase
  transfer rates;
- use the same `κ` domain `[0.15,500]`;
- use one nuisance inventory/level multiplier per shot in the primary analysis;
- profile each positive level exactly under MAPE;
- weight shots equally, so six fraction rows do not give a shot six times the influence of a
  three-point cup curve.

Verify on synthetic/model-only fixtures that concentrations scale linearly with the nuisance level.

Add one sensitivity analysis using a common level per solute across shots. Label it as an assumption
sensitivity, not the primary result.

## 11. Objectives

Primary:

```text
shot-balanced MAPE
```

Sensitivity:

```text
shot-balanced log-RMSE
```

Both must use the same observations within each arm and preserve positivity.

Do not choose between objectives after viewing which gives the preferred conclusion. Report both.

## 12. Localization metrics

For each solute, arm, and level policy, report:

```text
κ minimizer
J_min
10% relative accepted set
0.25-pp absolute accepted set for MAPE
finite / left-censored / right-censored / disconnected status
log10 accepted width where finite
endpoint or upper-bound status where available
```

Primary comparison:

```text
FRACTION_6 versus CUP_CURVE_3
```

`CUP_FINAL_1` is a negative control and is not counted as evidence that fractions “won.”

## 13. Held-out prediction and stability

Run leave-one-experiment-out evaluation.

For the primary shot-level policy:

1. fit common `κ` on the training experiments;
2. on each held-out shot, use the first observation only to set its level:
   - fraction 1 for `FRACTION_6`;
   - brew ratio 1/1 for `CUP_CURVE_3`;
3. predict the remaining observations;
4. score the held-out temporal shape.

Report:

```text
held-out MAPE
foldwise κ
median and range of log10 κ
right-boundary hit count
failed-fit count
```

No held-out prediction score is required for `CUP_FINAL_1`, because it has no later observation after
the level anchor.

## 14. Required Part B figures

At minimum:

1. profile overlay by solute: `FRACTION_6`, `CUP_CURVE_3`, `CUP_FINAL_1`;
2. accepted-width comparison;
3. leave-one-experiment-out `κ` distribution;
4. representative held-out temporal predictions;
5. a compact summary plot of localization versus held-out error.

Use clear labels and state that the model parameters were originally fitted in the same source
lineage; this is a same-campaign observation-operator study, not independent physical validation.

## 15. Required Part B outputs

Use exploratory paths:

```text
docs/paper1_resource/exploratory/PAPER_A_VIABILITY_OBSERVATION_OPERATOR_V1.json
docs/paper1_resource/exploratory/PAPER_A_VIABILITY_OBSERVATION_OPERATOR_V1.md
docs/paper1_resource/exploratory/figures/operator_*.png
```

Also produce a machine-readable matched-data manifest with source-row identifiers and hashes.

---

# Part C — Paper viability decision

## 16. Material improvement rule

For a solute, call `FRACTION_6` materially more localizing than `CUP_CURVE_3` when either:

1. its accepted log-width is at least `0.5` decades narrower; or
2. it changes a right-censored or endpoint-included profile into a finite upper boundary;

and its held-out temporal MAPE is not worse by more than `0.5` percentage points.

Report the raw metrics even when the binary rule is not met.

## 17. Decision branches

### `PROCEED_STRONG_PAPER`

Use when:

- Part A gives `H1_STRONG` or `H1_QUALIFIED`; and
- `FRACTION_6` is materially more localizing for at least two of three solutes; and
- the improvement is not purchased by materially worse held-out prediction.

Recommended paper focus:

> Whole-cup prediction and kinetic identification are distinct achievements; time-resolved
> observations recover information that aggregate cup measurements discard.

### `PROCEED_NARROW_OBSERVATION_DESIGN_PAPER`

Use when:

- Part A is heterogeneous, threshold-dependent, or does not lead; but
- `FRACTION_6` materially improves localization for at least two of three solutes.

Recommended focus:

> Aggregate and fraction-resolved espresso measurements support different inverse questions.

Do not lead with a universal weak-localization claim.

### `STOP_PAPER_1_AND_REPURPOSE`

Use when:

- Part A is mostly endpoint-excluded or indeterminate; and
- `FRACTION_6` does not materially improve localization for at least two solutes.

Repurpose:

- exact MAPE profiling;
- WIDE-reference machinery;
- endpoint construction;
- selected hydraulic ablations;

into a methods/resource note or repository documentation, and move effort back to solver
development and physical validation.

### `INCONCLUSIVE_REQUIRES_NEW_DATA`

Use only when the current source mapping or model discrepancy prevents a defensible matched
operator comparison. State exactly what new observation or metadata is required.

---

## 18. Final campaign deliverable

Create:

```text
docs/paper1_resource/exploratory/PAPER_1_SCIENTIFIC_VIABILITY_DECISION_V1.md
```

It must contain:

1. a one-paragraph answer to “Is there a worthwhile paper?”;
2. the Part A endpoint table;
3. the Part B observation-operator table;
4. the decisive plots;
5. the selected branch;
6. the strongest defensible paper thesis;
7. the claims that must be abandoned;
8. the minimum next scientific work;
9. an explicit statement that no further governance work should begin until the user reviews the
   scientific result.

---

## 19. Scope restrictions

Do not perform during this campaign:

- P0-G0 freeze or activation;
- PR-07 or PR-09 governance completion;
- claim-ledger expansion;
- protocol revision;
- integrity-scanner expansion;
- indexed novelty review;
- manuscript drafting;
- title polishing;
- CI timeout work;
- new experimental data acquisition;
- additional model families.

Implement only the code and tests needed to run, reproduce, and plot the two analyses.

No review round is required between Parts A and B. Run the complete campaign and return the scientific
decision.

---

## 20. Required terminal disposition

Return exactly:

```text
PAPER1_SCIENTIFIC_VIABILITY_SCREEN_COMPLETE
```

with:

- merge commit and merged PR state;
- viability branch head/tree;
- changed paths;
- Part A six-group numerical summary;
- Part B three-solute/operator numerical summary;
- selected viability branch;
- links/paths to all JSON, Markdown, and figures;
- local tests and any remote checks;
- all failures, exclusions, and caveats;
- confirmation that formal P0 gates remain open;
- confirmation that no formal P0-G8 result archive was created.

If the analysis cannot be completed, return:

```text
PAPER1_SCIENTIFIC_VIABILITY_SCREEN_BLOCKED
```

and identify the concrete scientific/data/implementation obstacle. Do not substitute another
governance task.
