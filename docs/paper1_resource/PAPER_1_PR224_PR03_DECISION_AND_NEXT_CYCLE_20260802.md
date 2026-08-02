# Paper 1 — PR #224 PR-03 decision and next pre-freeze cycle

**Date:** 2 August 2026  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**PR:** [#224](https://github.com/trbrewer/puckworks/pull/224), open and unmerged  
**Reviewed head:** [`e74d94d`](https://github.com/trbrewer/puckworks/commit/e74d94d)  
**Authority mode:** read-only adjudication; no repository file was modified and no scientific gate was run

---

## 1. Disposition

```text
P0_G0_PRE_FREEZE_CLOSURE_NOT_READY
PR_224_CONTINUE_OPEN_AND_UNMERGED
PR_06_ACCEPTED_IN_SUBSTANCE
PR_03_SPLIT_REQUIRED
PR_03A_QUALITATIVE_LIMIT_AND_ENDPOINT_CONSTRUCTION_AUTHORIZED
PR_03B_ONE_OUTPUT_FUNCTIONAL_TAIL_BOUND_ATTEMPT_AUTHORIZED
P0_G8_ENDPOINT_CLASSIFICATION_RETAINED
P0_G8_FINITE_TAIL_ONSET_CLAIM_NARROWED
P0_G0_REMAINS_OPEN
PLAN_REMAINS_CANDIDATE
NO_SCIENTIFIC_GATE_AUTHORIZED
FREEZE_COMMIT_F_NOT_AUTHORIZED
ACTIVATION_COMMIT_A_NOT_AUTHORIZED
```

> **Decision:** do not abandon P0-G8 and do not make the paper wait indefinitely for a sharp full-state remainder bound.
>
> Split PR-03 into:
>
> 1. **PR-03a — qualitative convergence and trustworthy analytical endpoint**, which remains a pre-freeze requirement; and
> 2. **PR-03b — quantitative finite-κ output bound and certified tail onset**, for which exactly one output-aware derivation cycle is authorized.
>
> Revise Protocol V2 now so that the central P0-G8 classification is based on the analytical endpoint and verified continuity at infinity. A finite-κ remainder must control only the **location of the tail onset**, not the numerical uncertainty of `J_inf` itself.

This is not a retreat from the thesis. It is a correction to what the available mathematics can and cannot support:

- the endpoint can decide whether the operational near-optimal set is eventually admitted or excluded;
- a sharp remainder can additionally identify a finite `κ_tail`;
- a loose remainder should produce `tail_onset_unresolved`, not make the endpoint calculation vacuous.

---

## 2. Assessment of the reported work

## 2.1 PR-06 is accepted in substance

The model-only audit covers all:

```text
9 conditions × 2 varieties × 3 solutes = 54 declared cells
```

through 27 operator-distinct calculations. The deduplication is appropriately structural: the operator pencil depends on condition and solute, while variety enters through campaign outcomes that the module does not read.

No scientific cell may be dropped later. The full 54-cell table must remain visible even where computation is deduplicated.

### Conditions on final PR-06 closure

The shared producer/archive must first be made self-consistent:

1. the archive currently lists both `PR-03` and `PR-06` under `premises_closed`, although its final verdict keeps PR-03 open;
2. the producer currently emits `PR03_BOUND_ESTABLISHED`, while the committed archive says `PR03_BOUND_ESTABLISHED_BUT_NOT_FIT_FOR_PROPAGATION`;
3. the archived contract says `M = cond2(V_fast)`, while the implementation uses a Lyapunov constant multiplied by an oblique-projector factor;
4. the archived remainder formula describes `exp(||P A0 P||T)`, while the implementation substitutes a computed slow-semigroup norm;
5. Protocol V2 declares the verification sequence `{10²,10³,10⁴,10⁵,10⁶}`, while the producer evaluates only `{10²,10³,10⁴}`.

The producer must reproduce the archive byte-for-byte or through a declared canonical serialization. No manual post-generation verdict patch is acceptable.

---

## 2.2 The refusal to close PR-03 is correct

A median looseness of approximately `4.9×10^13` is not a minor conservatism. It makes the current state-level estimate unusable for finite-tail localization.

More importantly, finite checks at 27 cells and three multipliers do not by themselves establish the displayed formula as a theorem. Before even considering sharpness, the derivation must address:

- the `Q A0 Q` term in the fast dynamics;
- the difference between a final-time slow-semigroup norm and the supremum/integral required by a Duhamel bound;
- coordinate conditioning when a Lyapunov inequality is solved in a fast eigenbasis;
- the numerical stability of projectors built by inverting a highly conditioned full eigenvector matrix;
- the non-negligible projector commutation residual reported in the archive;
- the initial layer and its path to the scalar cup output;
- the protocol-declared high-κ verification points at `10⁵` and `10⁶`.

Accordingly, the present result is best described as:

```text
a verified conservative envelope on the sampled fixtures,
with a promising structural limit,
but not yet a complete sharp output-error theorem.
```

The programme was right not to relabel that as fit for P0-G8.

---

## 3. The false dichotomy: tighter bound versus narrower P0-G8

The correct action is **both, but at different levels**:

1. **Narrow the secondary claim now.** Do not promise a certified finite onset `[κ_c,∞]` unless a sharp bound supports it.
2. **Retain the central endpoint classification.** A strict endpoint result still establishes eventual upper-tail inclusion or exclusion once convergence is proved.
3. **Attempt one genuinely output-aware derivation.** If it succeeds, report a certified onset. If it does not, report `tail_onset_unresolved` and proceed with the endpoint result.
4. **No third derivation cycle.** The paper should not become a treatise on worst-case semigroup constants.

This approach is more conservative than Protocol V2, but it preserves the scientifically important distinction between prediction and identification.

---

## 4. Why the current Protocol V2 propagation rule should be changed

Protocol V2 defines `κ = ∞` as an analytical endpoint and separately derives a finite-κ remainder of the form

```text
|f(κ) - f_inf| <= B_f(κ),   B_f(κ) -> 0 as κ -> ∞.
```

At the endpoint itself, the asymptotic remainder is zero. It is therefore **not an uncertainty contribution to an analytically computed `J_inf`**.

The endpoint interval should include uncertainty from:

- construction and numerical evaluation of the reduced operator;
- spatial discretisation;
- floating-point and linear-algebra error;
- exact-profile numerical arithmetic;
- any independent endpoint-validation discrepancy admitted by the protocol.

It should not include:

- a `C/κ` finite-κ remainder evaluated at an arbitrary finite proxy;
- weighted-median inventory tie width;
- global-minimum isolation error, which belongs to `J_min`;
- shoulder-derivative error, which belongs only to the shoulder.

Protocol V2 currently combines all six components into both `J_min` and `J_inf`. Replace that with **quantity-specific error budgets**.

### 4.1 Endpoint error budget

```text
E_inf =
    E_reduced_operator
  + E_spatial_endpoint
  + E_floating_endpoint
  + E_profile_arithmetic_endpoint
```

Then:

```text
J_inf ∈ [J_inf_hat - E_inf, J_inf_hat + E_inf]
```

### 4.2 Global-minimum error budget

```text
E_min =
    E_finite_response
  + E_spatial_profile
  + E_floating_profile
  + E_profile_arithmetic
  + E_global_minimum_isolation
```

### 4.3 Finite-tail-onset budget

```text
B_J(κ) = frozen propagation of B_f(κ) into the profiled objective
```

This is used only to certify that the endpoint classification holds uniformly for every
`κ >= κ_tail`.

### 4.4 Shoulder budget

```text
E_shoulder =
    E_response_derivative
  + E_step_convergence
  + E_spatial_derivative
```

It is never added to `J_min` or `J_inf`.

---

## 5. Endpoint classification without a finite onset

Add the following elementary lemma to the protocol.

## Endpoint–tail lemma

Let `J` extend continuously to the compactified endpoint `κ = ∞`.

- If `J_inf < T`, then there exists a finite `K` such that `J(κ) < T` for every `κ >= K`.
- If `J_inf > T`, then there exists a finite `K` such that `J(κ) > T` for every `κ >= K`.
- If the verified intervals overlap, no upper-tail conclusion is permitted.

Thus the interval rules remain:

```text
U_inf < L_T  -> endpoint_included
L_inf > U_T  -> endpoint_excluded
otherwise    -> endpoint_indeterminate
```

Given a proved `J(κ) -> J_inf`:

```text
endpoint_included  -> upper_near_optimal_set_unbounded
endpoint_excluded  -> upper_near_optimal_set_eventually_excluded
endpoint_indeterminate -> upper_classification_indeterminate
```

No numerical value of `K` is required for those qualitative conclusions.

The quantitative onset is reported separately:

```text
tail_onset_certified(kappa_tail)
tail_onset_unresolved
not_applicable_endpoint_excluded
```

### Consequence for manuscript language

Permitted when the endpoint is strictly included:

> Under the declared semi-discrete model and operational tolerance, the profiled near-optimal set is unbounded above; matched whole-cup prediction therefore does not provide finite upper localization of the mass-transfer-rate multiplier.

Not permitted without a sharp finite-tail bound:

> The profile enters its accepted upper tail at `κ = ...`.

This preserves the paper’s central thesis while preventing false precision.

---

## 6. Required split of PR-03

## PR-03a — qualitative limit and endpoint construction

**Resolution stage:** pre-freeze  
**Blocks:** P0-G0/P0-G8  
**Required outcome:** `PR03A_LIMIT_CONVERGENCE_ASSURED`

PR-03a must establish:

1. the affine pencil and index-one fast/slow structure algebraically;
2. a stable right/left slow basis;
3. a well-conditioned reduced operator;
4. existence of a finite constant proving `f(κ) -> f_inf`;
5. continuity of the exact MAPE profile at the endpoint;
6. trustworthy numerical evaluation of `f_inf` at all 27 operator-distinct cells;
7. complete coverage of all 54 declared cells;
8. an endpoint numerical-error bound that does not use a finite-κ proxy.

### Stable endpoint construction

Prefer:

```text
N = basis for ker(A1)
L = basis for ker(A1^T), normalized so L^T N = I
A_s = L^T A0 N
z_inf(T) = N exp(A_s T) L^T z0
```

and verify:

```text
A1 N = 0
L^T A1 = 0
L^T N = I
P = N L^T
P^2 = P
A1 P = P A1 = 0
```

Use a structural/local-block derivation, rank-revealing QR/SVD, or ordered real Schur method. Do not make the endpoint depend on inversion of the complete, highly conditioned eigenvector matrix.

### Formal convergence proof

The present finite constant may be sufficient to prove convergence even if it is useless for onset localization. However, the written proof must correctly include the full fast operator and time-integral terms. Sampled agreement is verification evidence, not the proof itself.

---

## PR-03b — quantitative output-functional bound

**Resolution stage:** optional enhancement within the frozen P0-G8 contract  
**Does not block P0-G0 once PR-03a is assured**  
**Exactly one new derivation cycle is authorized**

Possible outcomes:

```text
PR03B_OUTPUT_BOUND_FIT_FOR_TAIL_CERTIFICATION
PR03B_OUTPUT_BOUND_VALID_BUT_TAIL_ONSET_UNRESOLVED
PR03B_OUTPUT_BOUND_DERIVATION_FAILED
```

Only the first permits a numerical `κ_tail`.

### Required mathematical route

Do not repeat the full-state product-of-norms derivation. Carry the scalar cup functional through the slow–fast reduction.

In stable slow/fast coordinates:

```text
x_s' = A_ss x_s + A_sf x_f
x_f' = A_fs x_s + (κ A_ff + A_ff0) x_f
f(T) = c_s^T x_s(T) + c_f^T x_f(T)
```

Evaluate the composite interaction directly, for example through:

```text
A_sf A_ff^{-1} A_fs
```

or the group/Drazin inverse of `A1`, instead of bounding
`||A_sf|| · ||A_ff^{-1}|| · ||A_fs||` separately.

A strong candidate route is:

1. derive the first-order slow-operator correction using the group inverse;
2. carry the cup-output row vector and the initial-layer contribution explicitly;
3. evaluate the first-order change of the reduced matrix exponential with its Fréchet derivative;
4. bound the higher-order remainder under a predeclared Neumann/resolvent condition;
5. verify on normal, strongly non-normal, off-manifold, and known-asymptotic fixtures;
6. evaluate all 27 cells in higher precision or against a higher-precision reduced reference;
7. never fit a constant to the observed high-κ output errors.

The Fréchet derivative is appropriate because it gives the first-order sensitivity of the matrix exponential to an operator perturbation. The derivation must remain model-only.

### Hard stop

After this one output-aware route:

- if a rigorous finite `κ_tail` can be obtained, retain it;
- if the bound remains too loose, freeze `tail_onset_unresolved`;
- do not open another pre-freeze bound-tightening cycle;
- do not demote a valid endpoint result merely because onset could not be localized.

---

## 7. Protocol V2 changes required now

## 7.1 Replace the P0-G8 outcome vocabulary

Replace:

```text
tail_included
tail_excluded
boundary_indeterminate
```

with two fields:

```text
endpoint_classification:
  endpoint_included | endpoint_excluded | endpoint_indeterminate |
  limit_construction_failed

upper_tail_status:
  upper_set_unbounded | eventually_excluded | upper_status_indeterminate

tail_onset_status:
  certified | unresolved | not_applicable
```

A legacy display alias may be retained only if its definition is explicit.

---

## 7.2 Revise the programme-level H1 rule

Recommended frozen rule:

> H1 may lead only when at least five of six groups are `endpoint_included` under the 10% relative convention and at least one absolute convention, no group is `endpoint_excluded`, no group is `endpoint_indeterminate`, PR-03a passes, and `J_min` is numerically resolved for all groups. A certified finite tail onset is not required. Any exception is named in the same sentence.

If PR-03b fails, the paper states that the accepted upper region is unbounded but its finite onset was not certified.

---

## 7.3 Remove weighted-median tie width from `J`

For fixed `κ`:

```text
MAPE(I;κ)
  = (100/n) Σ_i |y_i - I f_i(κ)| / y_i
  = (100/n) Σ_i [f_i(κ)/y_i] |I - y_i/f_i(κ)|.
```

With positive `y_i` and `f_i`, this is a positive weighted absolute-deviation objective. Its minimizers are the weighted-median set of:

```text
r_i = y_i/f_i
weights w_i = f_i/y_i.
```

If the minimizer is an interval, the objective is exactly constant on that interval. Therefore:

```text
weighted-median tie width is an inventory-identification result,
not an objective-error term.
```

Use a deterministic lower weighted median for serialization, archive the complete minimizer interval, and set analytical profile error to zero. Bound only floating/order-statistic arithmetic.

This formal proposition closes PR-04 and should be implemented in the next cycle.

---

## 7.4 Choose the global-isolation contract

For this paper, choose the **deterministic convergence-envelope** route rather than claiming interval-certified global optimization of the complete 601-state model.

Freeze:

- compactified coordinate;
- nested grids, for example 40/80/160/320 points;
- local-minimum and crossing refinement from every detected basin;
- independent optimizer starts from every nested-grid basin;
- stability tolerances for `J_min`, minimizer locations, roots, and components;
- an envelope equal to the maximum change across the final accepted refinements, with a fixed safety factor;
- mandatory `global_minimum_unresolved` or `topology_unresolved` when stability is absent.

Describe the result as a **fail-closed numerical convergence envelope**, not a mathematical interval proof.

Separate:

```text
minimum_status
finite_component_topology_status
endpoint_classification
tail_onset_status
```

An unresolved decorative finite component must not be allowed to masquerade as an unresolved endpoint, but an unresolved global minimum must block endpoint classification because it changes `T`.

---

## 7.5 Replace the κ-tail requirement

Do not require a certified `[κ_c,∞]` component for the central classification.

If PR-03b succeeds, solve for a conservative `κ_tail` such that:

```text
B_J(κ) < verified endpoint-to-threshold margin
for all κ >= κ_tail.
```

If it does not:

```text
upper_set_unbounded
tail_onset_unresolved
```

is the correct result.

---

## 8. PR-07 staging

Implement the staging now.

### Pre-freeze

Freeze:

- meshes;
- endpoint and profile response norms;
- mesh estimator;
- safety factor;
- floating-point/reference method;
- derivative step family;
- response-to-objective propagation formula;
- failure status.

### Within P0-G8 after activation

Evaluate:

- the campaign-dependent propagation to `J_min` and `J_inf`;
- the shoulder derivative uncertainty;
- the final quantity-specific intervals.

Use:

```text
resolution_stage = within_gate
blocks_before = ["P0-G8"]
```

for campaign-dependent values, while retaining pre-freeze closure of the method specification.

---

## 9. PR-09 raw-support rule

Replace the current `>=3` rule with the previously authorized eight-part rule.

The cross-fitted map is constructible only when, after excluding the scored condition and every upstream object fitted with it:

1. observation-level raw hydraulic data and lineage are available;
2. the retained quadratic design matrix has full column rank;
3. all required pressure support remains represented;
4. residual degrees of freedom are at least two;
5. at least five independent observations remain for the three-coefficient quadratic;
6. the shot-time anchor is independently reconstructible;
7. covariance is finite, positive-semidefinite, and auditable; and
8. no chemical outcome enters construction, selection, or fallback.

Otherwise return:

```text
map_not_constructible
H3_RETROSPECTIVE_ONLY
NO_CROSS_FITTED_OR_PROSPECTIVE_MAP_CLAIM
```

PR-09 remains a P0-G9 branch outcome, not a P0-G0 blocker once this rule is frozen.

---

## 10. Activation integrity still required

Before freeze commit F is authorized, tests must:

1. establish exact set equality between normative content and the freeze record;
2. read every frozen file from F using `git show F:path`;
3. recompute each SHA-256 from F’s tree;
4. prove every path existed in F;
5. verify current normative bytes remain identical to F;
6. require F to be an ancestor of activation commit A;
7. enforce an activation-diff allowlist;
8. require a new protocol version and deviation for any post-activation normative change.

Working-tree hash checks alone are insufficient.

---

## 11. Additional consistency repairs

Before renewed adjudication:

- change the singular-bound archive from `premises_closed: ["PR-03","PR-06"]` to a schema that distinguishes PR-06 closure, PR-03a support, and PR-03b fitness;
- make the producer generate the committed verdict and fitness block;
- update the contract strings to the actual derivation;
- align the verification sequence with Protocol V2;
- avoid treating output differences near the matrix-exponential noise floor as asymptotic-order evidence;
- add tests that fail if a finite-κ remainder enters the `J_inf` endpoint budget;
- add units/dimension tests preventing inventory tie width or shoulder error from entering objective intervals;
- retain the original loose-bound result as an informative superseded/diagnostic artefact or as a clearly versioned baseline.

---

## 12. Authorized next-cycle scope

The next cycle in PR #224 is authorized to complete:

1. PR-03a proof and stable endpoint construction;
2. one PR-03b output-functional derivation attempt;
3. PR-04 formal weighted-median proposition and property tests;
4. PR-07 staging and quantity-specific error budgets;
5. Protocol V2 endpoint/tail split, tie-width correction, and global-isolation contract;
6. PR-09 eight-part raw-support rule;
7. producer/archive consistency repairs;
8. activation verification against `git show F:path`.

No campaign objective may be computed or inspected.

---

## 13. Required terminal disposition

Return:

```text
P0_G0_PRE_FREEZE_CLOSURE_READY_PR_OPEN
```

only if:

- PR-03a is formally and numerically assured;
- PR-03b has completed exactly one attempt and its outcome is honestly recorded;
- PR-06 producer/archive consistency is repaired;
- PR-04 is proved and tested;
- PR-07 is correctly staged;
- the P0-G8 endpoint/tail split and quantity-specific error budgets are implemented;
- the global-minimum convergence envelope is frozen and fail-closed;
- PR-09 uses the eight-part rule;
- activation tests verify F’s committed tree;
- no scientific gate or campaign objective has run;
- PR #224 remains open and unmerged.

Otherwise return:

```text
P0_G0_PRE_FREEZE_CLOSURE_NOT_READY
```

and enumerate each residual item.

---

## 14. Paste-ready execution directive

```markdown
# PAPER 1 — PR #224 ENDPOINT/TAIL SEPARATION AND FINAL PRE-FREEZE CLOSURE

## Authority

- Reviewed head: `e74d94d`
- Disposition: `P0_G0_PRE_FREEZE_CLOSURE_NOT_READY`
- Continue PR #224 open and unmerged.
- P0-G0 remains open and the plan remains candidate.
- No scientific gate, campaign objective, freeze commit F, or activation commit A is authorized.

## Scientific decision

Do not abandon P0-G8. Split PR-03:

- PR-03a: qualitative convergence and trustworthy analytical endpoint — pre-freeze blocker.
- PR-03b: sharp output-functional finite-tail bound — one attempt authorized; inability
  to certify a finite onset returns `tail_onset_unresolved` and does not invalidate a
  strict endpoint classification.

A finite-kappa C/k remainder must not be added to J_inf at kappa=infinity. It controls
only finite-tail onset.

## Mandatory work

1. PR-03a
   - prove the full singular-limit convergence, including QA0Q and all Duhamel terms;
   - construct the endpoint with stable left/right null bases, not a full ill-conditioned
     eigensystem inversion;
   - verify the reduced operator and endpoint error across all 27 operator-distinct /
     54 declared cells;
   - prove continuity of the exact MAPE profile at infinity.

2. PR-03b — one attempt only
   - carry the scalar cup functional through the slow-fast derivation;
   - use the composite slow-fast-slow operator or A1 group/Drazin inverse;
   - include the initial layer explicitly;
   - use a Frechet-derivative or equivalent first-order matrix-exponential correction;
   - bound the higher-order remainder without fitting constants to observed errors;
   - return fit, unresolved, or failed; do not open a third derivation cycle.

3. Protocol V2
   - separate endpoint classification, upper-tail status, and tail-onset status;
   - use endpoint inclusion plus proved convergence to establish an unbounded upper
     near-optimal set;
   - require a sharp bound only for a numerical kappa_tail;
   - replace the pooled error budget with quantity-specific budgets;
   - remove weighted-median tie width and shoulder error from J intervals;
   - freeze a deterministic nested-grid convergence envelope for J_min and finite
     topology, with fail-closed unresolved outcomes.

4. PR-04
   - state and prove the positive weighted-median proposition;
   - archive the complete minimizer interval;
   - make deterministic lower-median selection a serialization convention only;
   - add tie, scaling, extreme-weight, n=1, and positivity property tests.

5. PR-07
   - freeze mesh, estimator, safety factor, propagation, derivative-step, and failure
     rules before P0-G0;
   - stage campaign-dependent values within P0-G8.

6. PR-09
   - replace >=3 with the eight-part raw-support/full-rank/residual-df/covariance rule;
   - otherwise return map_not_constructible and keep H3 retrospective.

7. Reproducibility and activation
   - make the singular-bound producer reproduce its archive and actual verdict;
   - distinguish PR-06 closure, PR-03a assurance, and PR-03b fitness;
   - align the high-kappa sequence with the protocol;
   - verify exact freeze-record coverage and every hash from `git show F:path`;
   - enforce F ancestry and an activation-diff allowlist.

## Prohibited

- No campaign y/J/J_min/J_inf/threshold/topology/classification inspection.
- No P0 result archive.
- No scientific gate.
- No constant fitted to the observed 27-cell errors.
- No manuscript drafting.
- No merge, F, or A.

## Terminal response

Return `P0_G0_PRE_FREEZE_CLOSURE_READY_PR_OPEN` only when every mandatory item
passes and PR #224 remains open/unmerged. Otherwise return
`P0_G0_PRE_FREEZE_CLOSURE_NOT_READY`.
```

---

## 15. Final recommendation

Proceed with items 3, 4, 5, 7, and 8 immediately. Invest in **one** tighter output-functional derivation, but do not make a finite onset a condition for the paper’s central endpoint result.

The correct scientific claim is:

> a strict analytical endpoint plus proved convergence establishes whether the operational upper near-optimal set is unbounded; a sharp remainder determines only where that tail begins.

That is the strongest claim the current evidence architecture can support without either vacuity or false precision.
