
# Paper 1 — PR #224 consolidated WIDE-reference pass authorization

**Date:** 2 August 2026  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**PR:** [#224](https://github.com/trbrewer/puckworks/pull/224), open and unmerged  
**Reviewed head:** [`070e1e6`](https://github.com/trbrewer/puckworks/commit/070e1e6)  
**Authority mode:** bounded pre-freeze protocol work only

---

## 1. Disposition

```text
P0_G8_WIDE_REFERENCE_CONSOLIDATED_PASS_AUTHORIZED
PR_224_CONTINUE_OPEN_AND_UNMERGED
SCOPE_LOCKED_TO_WIDE_REFERENCE_SECTIONS_4_TO_7
NO_NEW_OUT_OF_SCOPE_COMPLETION_REQUIREMENTS_THIS_CYCLE
P0_G0_REMAINS_OPEN
PLAN_REMAINS_CANDIDATE
NO_SCIENTIFIC_GATE_AUTHORIZED
NO_CAMPAIGN_OBJECTIVE_AUTHORIZED
FREEZE_COMMIT_F_NOT_AUTHORIZED
ACTIVATION_COMMIT_A_NOT_AUTHORIZED
```

> **Proceed with one consolidated pass implementing the WIDE-referenced P0-G8 architecture.**

This cycle is intentionally limited. It does **not** include:

- the remaining PR-03a fixed-time theorem or evidence normalization;
- PR-07 staging;
- PR-09 constructibility;
- premise-state-machine repair;
- commit-bound closure;
- freeze/activation-history controls;
- P0-G8 producer execution;
- any campaign result.

Those items remain outstanding, but they are **not acceptance criteria for this pass**.

A newly noticed matter outside this scope will be logged for a later cycle and will not change this
cycle's disposition, unless it directly makes one of the architecture requirements below internally
false or non-executable.

---

## 2. Governing estimand

Replace the unresolved global reference with a finite, continuous WIDE reference domain and a
separate analytical endpoint.

```text
D_PUB  = [0.15, 6.5]
D_WIDE = [0.15, 500]
κ = ∞  = analytical endpoint, evaluated separately
```

For each of the six variety–solute groups:

```text
J(κ)  = min over I > 0 of MAPE(y, I f(κ))
J_ref = min over κ ∈ D_WIDE of J(κ)
J_inf = min over I > 0 of MAPE(y, I f_inf)
```

Mandatory interpretation:

- `J_ref` is the continuously minimized objective on `D_WIDE`, not the minimum of a diagnostic grid.
- `κ = ∞` is not included in `J_ref`.
- No finite topology is claimed for `(500,∞)`.
- The endpoint is used only to classify eventual behavior relative to the WIDE-referenced threshold.
- A finite tail onset is not estimated.

Add the estimand tag:

```text
FULL-WIDE-ENDPOINT
```

Definition:

> Full optimal-grind calibration support; threshold referenced to the continuously minimized profile
> on `D_WIDE = [0.15,500]`; analytical `κ=∞` endpoint evaluated separately.

Retain `FULL-WIDE` for finite-domain results only.

---

## 3. Thresholds and endpoint classification

Freeze both threshold families:

```text
T_rel(q) = (1+q) J_ref,  q ∈ {0.05,0.10,0.20}
T_abs(a) = J_ref + a,    a ∈ {0.10,0.25} percentage points
```

If:

```text
J_ref ∈ [L_ref,U_ref]
```

then:

```text
T_rel(q) ∈ [(1+q)L_ref,(1+q)U_ref]
T_abs(a) ∈ [L_ref+a,U_ref+a]
```

All objective and threshold intervals are intersected with `[0,∞)`.

Per group and convention:

```text
U_inf < L_T  -> endpoint_included
L_inf > U_T  -> endpoint_excluded
otherwise    -> endpoint_indeterminate
```

Given the separately required fixed-positive-time limit:

```text
endpoint_included
  -> WIDE-referenced operational acceptance set is eventually included
     and therefore unbounded above

endpoint_excluded
  -> WIDE-referenced operational acceptance set is eventually excluded

endpoint_indeterminate
  -> no upper-tail conclusion
```

Near-zero rule:

```text
if U_ref < 0.05 pp:
    relative result = relative_threshold_not_applicable_near_zero
```

Do not silently replace the relative convention with an absolute convention.

---

## 4. Required result fields

The archive/schema contract must separate:

```text
reference_minimum_status:
  resolved | unresolved

finite_wide_topology_status:
  resolved | unresolved

endpoint_classification:
  endpoint_included | endpoint_excluded | endpoint_indeterminate |
  limit_construction_failed

eventual_upper_status:
  wide_referenced_upper_set_unbounded |
  wide_referenced_eventually_excluded |
  upper_status_indeterminate

tail_onset_status:
  unresolved_by_design | certified_in_separate_analysis | not_applicable

intermediate_domain_status:
  not_characterized_by_design
```

For the current protocol:

```text
tail_onset_status = unresolved_by_design
intermediate_domain_status = not_characterized_by_design
```

Never serialize an invented component such as `[κ_c,∞]`.

Finite connected components are reported only within `D_WIDE`.

---

## 5. Programme-level H1 rule

Use the following closed rule.

### Group-level success

A group succeeds when:

- `J_ref` is resolved;
- the endpoint construction succeeds;
- it is `endpoint_included` under the 10% relative convention;
- it is `endpoint_included` under at least one absolute convention; and
- it is not `endpoint_excluded` under either absolute convention.

### Group-level exception

A group is an exception when:

- `J_ref` is resolved;
- the endpoint construction succeeds;
- it is not excluded under the 10% relative or either absolute convention; but
- it fails the success rule because one required convention is indeterminate or the relative
  convention is `relative_threshold_not_applicable_near_zero`.

### Group-level failure

A group fails the H1 programme rule when:

- `J_ref` is unresolved;
- endpoint construction fails;
- the 10% relative convention is `endpoint_excluded`; or
- either absolute convention is `endpoint_excluded`.

### Programme result

```text
H1_STRONG:
  6/6 group-level successes.

H1_QUALIFIED:
  exactly 5/6 group-level successes and exactly one group-level exception.
  The exception is named in the same headline sentence.

H1_DOES_NOT_LEAD:
  any group-level failure;
  two or more exceptions;
  any unresolved J_ref;
  or any endpoint-construction failure.
```

Every threshold-family result remains displayed, even when it does not determine the programme label.

---

## 6. Quantity-specific numerical intervals

Do not reuse one pooled error sum for unrelated quantities.

### 6.1 Reference minimum

```text
E_ref_response
E_ref_spatial
E_ref_profile_arithmetic
E_ref_floating
E_ref_search
```

The finite search supplies an evaluated candidate upper bound and a fail-closed numerical convergence
envelope:

```text
U_ref = best evaluated/refined candidate + applicable evaluation error

L_ref = max(
    0,
    best evaluated/refined candidate
    - applicable evaluation error
    - E_ref_search
)
```

This is described as a **deterministic numerical convergence envelope**, not a mathematically
certified global interval.

### 6.2 Analytical endpoint

```text
E_endpoint_construction
E_endpoint_spatial
E_endpoint_profile_arithmetic
E_endpoint_floating
```

```text
J_inf ∈ [
    max(0, J_inf_hat - E_inf),
    J_inf_hat + E_inf
]
```

Do not add to `J_inf`:

- a finite-κ `C/κ` remainder;
- weighted-median inventory tie width;
- finite-domain search error;
- response-shoulder error.

### 6.3 Response shoulder

Keep a separate budget:

```text
E_shoulder_step
E_shoulder_spatial
E_shoulder_floating
```

It does not enter `J_ref`, `J_inf`, or a threshold.

---

## 7. Finite WIDE minimization and topology contract

Freeze one deterministic, fail-closed numerical procedure on `D_WIDE`.

### 7.1 Nested grids

Use exactly:

```text
40, 80, 160, 320 log-spaced points on [0.15,500]
```

Any numerical stopping tolerances needed by the implementation must be assigned explicit values in
the protocol during this pass and tested only on synthetic objective functions before freeze.

### 7.2 Reference-minimum search

At every refinement:

1. evaluate both domain endpoints;
2. identify every sampled local basin;
3. run bounded scalar minimization in every basin;
4. retain tied or near-tied basins;
5. compare the best value and minimizer locations across refinements;
6. calculate the predeclared search-convergence envelope;
7. return `reference_minimum_status = unresolved` if the frozen stability criteria are not met.

The minimum of the 40-point grid is never reported as `J_ref`.

### 7.3 Threshold topology

For every threshold:

1. detect every sign change on each nested grid;
2. refine every detected root;
3. run explicit tangency checks;
4. compare roots and components across refinements;
5. retain lower-boundary censoring;
6. report components only within `[0.15,500]`;
7. return `finite_wide_topology_status = unresolved` if the frozen stability criteria fail.

An unresolved `J_ref` blocks endpoint classification because it changes the threshold.

Unresolved secondary finite topology does **not** erase an otherwise resolved endpoint classification,
but it is reported prominently and prevents any claim of complete finite-domain topology.

### 7.4 Synthetic architecture tests

No campaign data may be used. Add synthetic tests covering at least:

- one interior minimum;
- a minimum at each boundary;
- two tied or near-tied minima;
- multiple accepted components;
- a threshold tangency;
- an unresolved refinement sequence;
- endpoint included;
- endpoint excluded;
- endpoint indeterminate;
- the near-zero relative branch;
- `H1_STRONG`;
- `H1_QUALIFIED`;
- `H1_DOES_NOT_LEAD`.

These tests may exercise pure functions or a synthetic-only scaffold. They must not create the
campaign P0-G8 result archive.

---

## 8. Normative consistency within this pass

Update only the active surfaces needed to make this architecture singular and internally consistent:

1. `PAPER_A_PIVOT_ANALYSIS_PROTOCOL_V2.md`;
2. the H1 and estimand passages of `PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md`;
3. manifest estimand/tag/schema declarations affected by the change;
4. archive/schema and integrity tests for the new fields;
5. an append-only pre-freeze claim-resolution delta, if the immutable initial ledger contains the
   displaced global-estimand wording.

Do not rewrite the immutable initial ledger as if the WIDE-reference estimand had been the original
pre-analysis state.

Remove or supersede every active assertion that simultaneously says:

```text
J_min is over [0.15,∞]
```

and:

```text
the finite search ends at 500
```

Historical review/adjudication files remain historical and need not be rewritten.

---

## 9. Explicitly deferred work

The following are outside this cycle and must not be used to withhold
`P0_G8_WIDE_REFERENCE_ARCHITECTURE_COMPLETE_PR_OPEN`:

- PR-03a fixed-time theorem;
- PR-03a verdict-field split and `--check`;
- production `_mape_profile_level`;
- PR-07 staging;
- PR-09;
- premise gating;
- commit-bound closures;
- freeze/activation Git-history tests.

They remain required before P0-G0 can ultimately freeze, but they belong to later bounded cycles.

---

## 10. Prohibited activity

- no campaign `y`, `J`, `J_ref`, `J_inf`, threshold, topology, shoulder, or classification;
- no P0-G8 result archive;
- no P0 scientific gate;
- no PR-03b work;
- no changes to `D_WIDE`, threshold families, H1 rule, or nested-grid sizes based on campaign output;
- no manuscript drafting;
- no merge;
- no freeze commit F;
- no activation commit A.

---

## 11. Required terminal disposition

Return:

```text
P0_G8_WIDE_REFERENCE_ARCHITECTURE_COMPLETE_PR_OPEN
```

only when:

- §§2–8 above are implemented;
- all synthetic architecture tests pass;
- no active normative surface retains the displaced global-estimand definition;
- no campaign objective or scientific gate has run;
- PR #224 remains open and unmerged.

Report:

- exact head and tree;
- changed paths;
- the final formulas and result vocabulary;
- the exact numerical stability tolerances selected;
- synthetic-test coverage;
- complete test and static-check results;
- confirmation that no P0 result archive exists.

Otherwise return:

```text
P0_G8_WIDE_REFERENCE_ARCHITECTURE_NOT_READY
```

and list only unmet requirements from this document.

---

## 12. Paste-ready execution block

```markdown
# PAPER 1 — PR #224 CONSOLIDATED WIDE-REFERENCE PASS

## Authority

- Reviewed head: `070e1e6`
- Disposition: `P0_G8_WIDE_REFERENCE_CONSOLIDATED_PASS_AUTHORIZED`
- Scope is locked to the WIDE-reference architecture in §§2–8 of the authorization.
- PR #224 remains open and unmerged.
- P0-G0 remains open; the plan remains candidate.
- No scientific gate, campaign objective, merge, F, or A is authorized.

## Required architecture

    D_WIDE = [0.15,500]
    J_ref  = min_{kappa in D_WIDE} min_{I>0} MAPE(y,I f(kappa))
    J_inf  = min_{I>0} MAPE(y,I f_inf)

Use tag `FULL-WIDE-ENDPOINT`.

The endpoint is separate from J_ref. No finite topology is assigned to (500,infinity), and:

    tail_onset_status = unresolved_by_design
    intermediate_domain_status = not_characterized_by_design

Implement:

1. threshold intervals from J_ref;
2. separated reference/topology/endpoint/eventual-tail/onset fields;
3. the frozen H1_STRONG / H1_QUALIFIED / H1_DOES_NOT_LEAD rule;
4. quantity-specific J_ref, J_inf, and shoulder error budgets;
5. nested 40/80/160/320 log-grid minimization and finite topology on [0.15,500];
6. fail-closed unresolved branches;
7. synthetic-only tests for minima, components, tangencies, endpoint classes, near-zero behavior, and
   programme outcomes;
8. singular consistency across the active plan, protocol, manifest/schema, tests, and append-only
   claim-resolution delta.

## Deferred and nonblocking for this pass

Do not work on PR-03a theorem, PR-07, PR-09, premise gating, closure provenance, or activation
history unless a minimal field-name edit is strictly required by the WIDE-reference schema.

## Prohibited

No campaign y/J/J_ref/J_inf/threshold/topology/shoulder/classification.
No P0 archive or gate.
No PR-03b.
No manuscript drafting.
No merge, F, or A.

## Terminal response

Return `P0_G8_WIDE_REFERENCE_ARCHITECTURE_COMPLETE_PR_OPEN` only when the locked scope is complete
and PR #224 remains open/unmerged; otherwise return
`P0_G8_WIDE_REFERENCE_ARCHITECTURE_NOT_READY`.
```
