
# Paper 1 — PR #224 WIDE-reference completion adjudication

**Date:** 2 August 2026  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**PR:** [#224](https://github.com/trbrewer/puckworks/pull/224), open and unmerged  
**Reviewed head:** [`8d3e73b`](https://github.com/trbrewer/puckworks/commit/8d3e73b)  
**Authority mode:** read-only adjudication; no repository file was modified and no scientific gate was run

---

## 1. Disposition

```text
P0_G0_PRE_FREEZE_CLOSURE_NOT_READY
PR_224_CONTINUE_OPEN_AND_UNMERGED
P0_G8_WIDE_REFERENCE_ARCHITECTURE_AUTHORIZED
PR_03A_ENDPOINT_CONSTRUCTION_ACCEPTED_IN_SUBSTANCE
PR_03A_FORMAL_ASSURANCE_STILL_OPEN
PR_03B_NOT_PURSUED_CURRENT_PROTOCOL
PR_04_WEIGHTED_MEDIAN_CORE_ACCEPTED_IN_SUBSTANCE
PR_04_FINAL_CLOSURE_WITHHELD_PENDING_CORRECTIONS
PR_07_METHOD_STAGING_REQUIRED
PR_09_RULE_FREEZE_REQUIRED
FINAL_DETERMINISTIC_PRE_FREEZE_COMPLETION_CYCLE_AUTHORIZED
P0_G0_REMAINS_OPEN
PLAN_REMAINS_CANDIDATE
NO_SCIENTIFIC_GATE_AUTHORIZED
FREEZE_COMMIT_F_NOT_AUTHORIZED
ACTIVATION_COMMIT_A_NOT_AUTHORIZED
```

> **Proceed next with the WIDE-referenced P0-G8 architecture, then complete the remaining deterministic proof, implementation, staging, and provenance work in the same PR.**
>
> Do not run PR-03b. Do not run P0-G8. Do not inspect a campaign objective.

The scientific direction remains approved. The central result should ask whether the analytical endpoint is accepted **relative to the best fit in the predeclared finite WIDE reference domain**, not relative to an unresolved global minimum over `[0.15,∞]`.

---

## 2. Progress accepted

### 2.1 The producer exit-code defect is correctly fixed

The former condition:

```python
result["verdict"].endswith("ASSURED")
```

also accepted:

```text
PR03A_LIMIT_CONVERGENCE_NOT_ASSURED
```

because that string ends in `ASSURED`. Exact equality is required and is the correct repair.

Retain an adversarial test that forces a failed cell and asserts a nonzero process exit.

### 2.2 The stable endpoint construction is accepted in substance

The left/right null-basis construction is materially superior to inversion of the complete eigenvector matrix:

```text
A1 N = 0
L^T A1 = 0
L^T N = I
P = N L^T
A_s = L^T A0 N
z_inf(T) = N exp(A_s T) L^T z0
```

The reported conditioning and projector residuals support the construction numerically. The 27 operator-distinct calculations also preserve complete 54-cell coverage through an explicit operator-equivalence argument.

This accepts the **construction**. It does not yet accept the current archive's single verdict as a complete proof of the fixed-time singular limit.

### 2.3 Withdrawal of the old full-state bound is correct

The old archive coupled:

- an off-manifold initial condition; and
- a uniform state-error claim on `[0,T]`.

At `t=0`, the discrepancy is `Q z0`, which does not vanish with `κ`. The uniform claim was therefore not established and should remain withdrawn rather than softened to “valid but loose.”

### 2.4 PR-03b is correctly removed from the current protocol

The current paper will not certify a numerical finite tail onset. Freeze:

```text
tail_onset_status = unresolved_by_design
```

PR-03b must remain:

```text
NOT-PURSUED-CURRENT-PROTOCOL
resolution_stage = scoped
blocks_before = []
```

It must not be reintroduced after viewing P0-G8 classifications.

### 2.5 The weighted-median dimensional correction is correct

For fixed `κ`:

```text
MAPE(I;κ)
  = (100/n) Σ_i |y_i - I f_i|/y_i
  = (100/n) Σ_i (f_i/y_i) |I - y_i/f_i|.
```

The level minimizer is a weighted-median set. If that set is an interval, the objective is constant across it. Its width is in inventory units and cannot enter an objective interval measured in percentage points.

That correction must now be implemented in Protocol V2 and the production profiling interface.

---

## 3. Central blocker: the current endpoint classification is not well-posed

Protocol V2 presently defines:

```text
J_min = inf over κ ∈ [0.15,∞] of J(κ)
T     = a function of J_min
```

but searches the finite profile only to `κ = 500`.

A lower finite minimum could exist in `(500,∞)` before the profile reaches its limiting regime. Such a minimum would lower `J_min`, lower the threshold, and potentially change the endpoint classification.

The endpoint–tail lemma is valid for a **fixed threshold**. It does not prove that a threshold defined by an unresolved global minimum has been calculated correctly.

### Required correction

Make the central estimand explicitly **WIDE-referenced**.

---

## 4. Exact P0-G8 WIDE-reference contract

## 4.1 Domains

Freeze:

```text
D_PUB  = [0.15, 6.5]       # inherited published domain; secondary sensitivity
D_WIDE = [0.15, 500]       # primary finite reference domain
κ = ∞                      # analytical endpoint, evaluated separately
```

`D_WIDE` is a continuous domain. Its minimum is not the minimum of the 40-point diagnostic grid.

The unexamined interval `(500,∞)` is not assigned finite topology. It is represented only through the analytical endpoint and the fixed-time convergence theorem.

## 4.2 Objective definitions

For each of the six variety–solute groups:

```text
J(κ)     = min over I > 0 of MAPE(y, I f(κ))
J_ref    = min over κ ∈ D_WIDE of J(κ)
J_inf    = min over I > 0 of MAPE(y, I f_inf)
```

Report also:

```text
argmin_ref_components
reference_upper_boundary_attained
reference_lower_boundary_attained
```

The endpoint is **not** included in `J_ref`.

## 4.3 Estimand tag

Add a distinct tag:

```text
FULL-WIDE-ENDPOINT
```

Definition:

> Full optimal-grind calibration support; threshold referenced to the continuously minimized profile on `D_WIDE = [0.15,500]`; analytical `κ=∞` endpoint evaluated separately.

Do not reuse `FULL-WIDE` for the endpoint classification. `FULL-WIDE` remains the finite-domain estimand.

Update:

- the plan's estimand table;
- the protocol;
- the manifest's required tags;
- the P0-G8 archive schema;
- claim-ledger delta/reconciliation records;
- figure/table labels.

## 4.4 Threshold families

Use:

```text
T_rel(q) = (1+q) J_ref,   q ∈ {0.05,0.10,0.20}
T_abs(a) = J_ref + a,     a ∈ {0.10,0.25} percentage points
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

Intersect every objective interval with `[0,∞)`.

### Near-zero branch

If `U_ref < 0.05 pp`, mark the relative convention:

```text
relative_threshold_not_applicable_near_zero
```

Do not silently substitute an absolute convention. At programme level this group is not a relative-rule success; it is an explicitly named exception.

## 4.5 Endpoint classification

For each group and threshold convention:

```text
U_inf < L_T  -> endpoint_included
L_inf > U_T  -> endpoint_excluded
otherwise    -> endpoint_indeterminate
```

Given a proved fixed-positive-time limit:

```text
endpoint_included
    -> WIDE-referenced operational acceptance set is eventually included
       and therefore unbounded above

endpoint_excluded
    -> WIDE-referenced operational acceptance set is eventually excluded

endpoint_indeterminate
    -> no upper-tail conclusion
```

## 4.6 Separate result fields

Use separate fields:

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

Do not serialize `[κ_c,∞]` when `κ_c` has not been certified.

## 4.7 Permitted and prohibited wording

Permitted:

> Relative to the best fit in the predeclared WIDE calibration domain, the operationally accepted profile is unbounded above under the declared semi-discrete model.

Permitted consequence:

> Matched whole-cup prediction therefore does not provide finite upper localization of the model-specific mass-transfer-rate multiplier under that operational criterion.

Not permitted:

- “the unrestricted global profile is unbounded”;
- “the likelihood is unbounded”;
- “the parameter cannot be identified” without the operational and model qualifiers;
- “the accepted tail begins at κ = ...”;
- a claim that topology in `(500,∞)` has been enumerated.

---

## 5. Programme-level H1 rule: resolve the existing contradiction

The current logic simultaneously allows “five of six included” and says that any indeterminate group prevents H1 from leading. With no excluded, indeterminate, or failed group, five of six cannot occur: the sixth must also be included.

Freeze a coherent three-level rule:

```text
H1_STRONG:
  6/6 endpoint_included under the 10% relative rule and at least one
  absolute rule; all J_ref resolved; no endpoint exclusion or indeterminacy.

H1_QUALIFIED:
  exactly 5/6 satisfy H1_STRONG at group level; the sixth is
  endpoint_indeterminate or relative_not_applicable_near_zero, never excluded;
  the exception is named in the headline sentence.

H1_DOES_NOT_LEAD:
  any endpoint_excluded group; two or more exceptions; any unresolved J_ref;
  any limit-construction failure; or material reversal across threshold families.
```

Finite secondary-component ambiguity need not block a strict endpoint result if `J_ref` is resolved. An unresolved reference minimum must block the classification because it changes the threshold.

---

## 6. Quantity-specific numerical intervals

Protocol V2 must stop pooling unrelated errors into both `J_ref` and `J_inf`.

## 6.1 `J_ref`

Use:

```text
E_ref_response
E_ref_spatial
E_ref_profile_arithmetic
E_ref_floating
E_ref_search
```

The search term is primarily **one-sided**: a finite optimizer can miss a lower value, but an evaluated candidate supplies an upper bound subject to response error.

A transparent numerical-convergence construction is:

```text
U_ref = best evaluated/refined candidate upper bound
L_ref = max(0, best estimate - E_ref_search - other applicable bounds)
```

This is a fail-closed numerical convergence envelope, not an interval-arithmetic proof of global optimality.

## 6.2 `J_inf`

Use only:

```text
E_endpoint_construction
E_endpoint_spatial
E_endpoint_profile_arithmetic
E_endpoint_floating
```

Do not add:

- a finite-κ `C/κ` term;
- weighted-median tie width;
- finite-domain minimizer-search error;
- shoulder-derivative error.

## 6.3 Shoulder

Use its own budget:

```text
E_shoulder_step
E_shoulder_spatial
E_shoulder_floating
```

It never enters `J_ref`, `J_inf`, or a threshold.

---

## 7. Finite WIDE minimization and topology

Use a deterministic, fail-closed numerical-convergence contract.

### 7.1 Nested grids

Freeze, for example:

```text
40, 80, 160, 320 log-spaced points on D_WIDE
```

The exact sizes may differ, but they must be fixed before the run.

### 7.2 Reference-minimum search

At every refinement:

1. evaluate both domain endpoints;
2. identify every sampled local basin;
3. run bounded scalar minimization inside every basin;
4. retain all tied/near-tied basins;
5. compare minimum value and locations across refinements;
6. compute the predeclared convergence envelope;
7. return `reference_minimum_unresolved` if stability is not achieved.

### 7.3 Threshold crossings

For each threshold:

1. detect every sign change;
2. refine each root;
3. run explicit tangency checks;
4. compare roots/components across nested refinements;
5. retain lower-boundary censoring;
6. report only components inside `D_WIDE`;
7. return `finite_topology_unresolved` rather than inventing a component.

### 7.4 No assurance overclaim

Call the output:

```text
deterministic numerical convergence envelope
```

Do not call it a mathematically certified global interval unless a genuine interval or branch-and-bound proof is implemented.

---

## 8. PR-03a: construction accepted, final assurance still open

## 8.1 Formal fixed-positive-time proposition required

Add a dedicated proof artefact, preferably:

```text
docs/paper1_resource/PAPER_A_FIXED_TIME_SINGULAR_LIMIT_PROPOSITION.md
```

Under the verified assumptions:

- `A1` has semisimple zero eigenvalue;
- every nonzero eigenvalue lies strictly in the left half-plane;
- `A0` is fixed and finite;
- `P = N L^T` is the slow spectral projector;
- `T > 0` is fixed;

prove:

```text
exp((A0 + κA1)T) z0
    -> N exp((L^T A0 N)T) L^T z0
```

as `κ -> ∞`.

The theorem may state a qualitative fixed-time bound such as:

```text
||rκ(T)|| <= C_T/κ + M_T exp(-c κ T)||Qz0||
```

for sufficiently large `κ`.

Do not claim uniform convergence on `[0,T]` for an off-manifold initial condition. Uniform convergence may be claimed only on `[δ,T]`, `δ > 0`.

## 8.2 Verify theorem assumptions at all operator-distinct cells

The endpoint archive must record, per cell:

- semisimplicity/index-one check;
- right/left nullity;
- invertibility and condition of `L^T N` before normalization;
- maximum real part of every fast eigenvalue;
- rank-tolerance sensitivity;
- projector residuals;
- reduced-operator diagnostics;
- finite, real, strictly positive `f_inf`.

A stable endpoint construction plus sampled convergence is not a substitute for verifying the theorem's fast-spectrum assumption at every cell.

## 8.3 Separate verdict fields

Replace the single pass/fail verdict with:

```text
algebraic_limit_status:
  assured | not_assured

endpoint_construction_status:
  verified | failed

finite_kappa_validation_status:
  consistent | method_limited | inconsistent

coverage_status:
  complete | incomplete

overall_PR03a_status:
  assured only if theorem + assumptions + construction + coverage pass
```

The high-κ sequence and any absolute tail cap must not decide the algebraic limit.

## 8.4 The high-κ path is a diagnostic, not an independent proof

Rename “independent verification” to:

```text
full-state finite-κ matrix-exponential diagnostic
```

It uses the same model operator and numerical matrix-exponential implementation. Capture warnings rather than suppressing them silently.

The observed U-shaped error curve may be reported as method limitation. Avoid asserting a universal `O(κ·eps)` law unless it is separately derived.

## 8.5 Reproducibility

Add:

```text
--check
```

that regenerates canonical JSON and byte-compares it with the archive.

Record:

- producer SHA-256;
- every model/input path and SHA-256;
- exact command;
- Python, NumPy, SciPy, and platform;
- warnings;
- complete 54-cell mapping;
- theorem artefact path and SHA-256.

Update `tests/test_paper_a_asymptotic_structure.py`, whose current prose still says PR-03 is merely partially closed and that an explicit constant is owed for P0-G8.

---

## 9. PR-04: core theorem accepted, final closure withheld

The weighted-median minimizer theorem is correct. Three assurance defects remain.

## 9.1 The continuity test is vacuous

The current test perturbs:

```text
f_eps = (1+eps) f_inf
```

A common positive scaling of all predictions is exactly absorbed by:

```text
I_eps = I/(1+eps)
```

so the profiled MAPE is invariant. The test therefore exercises scale invariance, not general continuity.

### Required proof

For positive `f` near positive `f_inf`:

1. all ratios `y_i/f_i` lie in a common compact positive interval;
2. the objective is jointly continuous in `(I,f)`;
3. minimizers remain inside that compact interval;
4. uniform convergence of the objective on that interval implies convergence of the minima.

A Berge-maximum-style argument or a direct uniform-convergence proof is sufficient.

### Required tests

Use nonuniform perturbations:

```text
f_eps = f_inf * (1 + eps*d)
```

with a fixed nonconstant direction `d`, both signs of `eps`, and positivity retained.

Test:

- convergence of the profiled value;
- median-switch cases;
- approach to an exact tie;
- nonuniform perturbations across several directions.

## 9.2 The “smallest tie fixture” claim is false

The current fixture `[1,1,2,2,2,2]` is valid but not smallest.

A three-observation example already gives a non-degenerate flat interval:

```text
r = [1,2,2]
w = [1,1/2,1/2]
```

The weight at `r=1` equals the total weight at `r=2`, so every `I in [1,2]` minimizes the objective.

Correct the explanatory claim and add the three-point fixture.

The statement that exact ties are non-generic under continuous perturbations is reasonable, but a 200-draw random test is a regression diagnostic, not a proof of a measure-zero statement.

## 9.3 Production must expose the complete interval

The production helper currently returns only:

```text
(lower weighted median, MAPE)
```

Add a production function such as:

```text
_mape_profile_level(f,y) -> {
    level_lower,
    level_upper,
    selected_level,
    objective_pp,
    tie_status
}
```

Requirements:

- finite, shape-compatible inputs;
- `y_i > 0`;
- `f_i > 0`;
- deterministic summation/tie rule;
- lower endpoint selected only for serialization;
- complete interval archived;
- hard failure on nonpositive/nonfinite inputs.

Keep `_mape_level` as a compatibility wrapper if needed.

## 9.4 Evidence placement

A test-module docstring is useful, but the load-bearing proposition should also appear in a dedicated proof/method artefact and be linked by exact locator and hash.

Do not overwrite the immutable initial claim ledger to make it look as though PR-04 was already proved. Record a pre-freeze claim-resolution delta or append-only history.

---

## 10. PR-07 staging

Split:

```text
PR-07a: numerical method and propagation contract — pre-freeze
PR-07b: campaign-dependent interval evaluation — within P0-G8
```

## 10.1 PR-07a

Freeze:

- meshes `{100,200,400}`;
- production mesh;
- finite-response and endpoint response norms;
- mesh estimator;
- safety factor;
- floating/reference method;
- derivative steps `{0.04,0.08,0.16}` in `log κ`;
- unresolved/failure statuses;
- value-function propagation formula.

For a prediction perturbation `δf`, use both profiled optimizers:

```text
J(f+δf)-J(f) <= g(f+δf,I_f)-g(f,I_f)
J(f)-J(f+δf) <= g(f,I_{f+δf})-g(f+δf,I_{f+δf})
```

and bound with the larger applicable inventory endpoint. Do not assert an unproved global “1-Lipschitz in f” rule.

The log-response sensitivity does not depend on the fixed inventory scale:

```text
d log(I f)/d log κ = d log f/d log κ.
```

State that directly rather than tying the shoulder to an arbitrarily selected profiled inventory.

## 10.2 PR-07b

After activation, evaluate:

- `y`-dependent propagation to `J_ref`;
- `y`-dependent propagation to `J_inf`;
- final threshold intervals;
- shoulder numerical uncertainty.

Audit staging:

```text
resolution_stage = within_gate
blocks_before = ["P0-G8"]
```

The method must be frozen before P0-G0; the campaign-dependent value must not be computed before activation.

---

## 11. PR-09 raw-support rule

Freeze the complete constructibility rule.

After excluding the scored condition and every upstream object fitted using it, the map is
constructible only if:

1. raw observation-level hydraulic data and lineage are available;
2. the retained quadratic design has full column rank;
3. every pressure basis needed by the model remains represented;
4. residual degrees of freedom are at least two;
5. at least five independent observations remain for the three-coefficient quadratic;
6. the shot-time anchor is independently reconstructible;
7. covariance is finite, positive-semidefinite, and auditable; and
8. no chemical outcome enters construction, selection, or fallback.

Otherwise:

```text
map_not_constructible
H3_RETROSPECTIVE_ONLY
NO_CROSS_FITTED_OR_PROSPECTIVE_MAP_CLAIM
```

This is a P0-G9 branch outcome, not a P0-G0 blocker once the rule is frozen.

---

## 12. Claim, plan, and evidence reconciliation

The following active statements will become stale when the WIDE-reference architecture is implemented:

- the plan's H1 wording and estimand table;
- Protocol V2's compactified-domain `J_min`;
- the manifest's tag vocabulary;
- the initial ledger's C-ALG-02 status and old P0-G6 confirmatory path;
- the initial ledger's finite-domain C-OPS-01 wording;
- the R0a PR-06 evidence path, which still points to the withdrawn singular-bound archive;
- `test_paper_a_asymptotic_structure.py`'s statement that PR-03 still requires a sharp constant for P0-G8.

### Preserve the initial ledger

Do not rewrite historical pre-analysis state silently.

Use one of:

```text
PAPER_A_PREFREEZE_CLAIM_RESOLUTION_DELTA.json
```

or an append-only `resolution_history` preserving:

- initial status;
- current status;
- date/commit;
- evidence path/locator/hash;
- reason for the change;
- affected claims and gates.

The final ledger later incorporates the resolved state under P0-G1b.

### Versioning

Because the estimand changes materially, preferred practice is either:

- a new plan/protocol revision; or
- an explicit dated pre-freeze amendment section with a complete replacement table.

Do not silently change the mathematical target while leaving the old description elsewhere in the normative bundle.

---

## 13. Premise-gating control

Replace the contradictory controls with one fail-closed state machine.

Recommended fields:

```text
resolution_stage:
  pre_freeze | within_gate | pre_drafting | scoped

premise_state:
  unresolved | resolved | scoped | not_applicable

assurance_status:
  assured | partially_assured | withdrawn | external_block
```

P0-G0 rule:

```python
pre_freeze_blockers = [
    p for p in premises
    if p["resolution_stage"] == "pre_freeze"
    and p["premise_state"] != "resolved"
]
```

Every unknown state blocks.

Gate-specific tests must similarly prevent:

- P0-G8 from running/passing with unresolved `within_gate` premises affecting P0-G8;
- P0-G9 from running/passing with unresolved map premises;
- P0-G10/drafting with unresolved `pre_drafting` premises.

### Current status corrections

Until the remaining proof/test work is complete:

```text
PR-03a = partially_assured
PR-04  = partially_assured
PR-07a = unresolved
```

PR-03b remains scoped and nonblocking.

Generate the R0a summary from premise rows; do not maintain counts by hand.

Preserve the initial audit outcome through an initial-state field or append-only resolution history.

---

## 14. Commit-bound closure

The passed-gate records still have:

```text
evidence_content_commit = null
```

and current tests verify working-tree bytes.

Use the required two-step pattern inside the open PR:

### Content commit C

Finalize:

- protocol and plan/amendment;
- proof artefacts;
- initial/delta assurance records;
- endpoint producer/archive;
- weighted-median production helper and tests;
- PR-07 contract;
- PR-09 rule;
- integrity and activation helpers.

### Closure commit D

Record:

```text
evidence_content_commit = C
```

for P0-G1a, P0-G3a, and P0-R0a as applicable.

Tests must:

- verify C exists;
- read each bound path with `git show C:path`;
- recompute every hash from C;
- verify producer and evidence locators;
- reject stale premise counts and IDs.

Remove or null stale `closed_at_commit` values that name a commit unable to contain the evidence. A later authority-controlled activation commit may record D.

P0-G0 itself remains open in PR #224.

---

## 15. Freeze-record and activation helpers

Implement the controls now; do not create F or A.

## 15.1 Independent required-content set

A freeze record cannot prove its own completeness merely by iterating over its own keys.

Declare an independent:

```text
required_normative_content_paths
```

and assert exact set equality with the freeze record.

The activation diff allowlist must prohibit changing this required set.

## 15.2 Content that must be frozen

At minimum include:

- controlling plan or amendment;
- analysis protocol;
- claim and scope baseline/delta artefacts;
- reconciliation and premise records;
- proof artefacts;
- P0-G0 prerequisite closure records;
- endpoint producer and endpoint archive;
- weighted-median production helper/proof/tests;
- P0-G8 producer contract and synthetic self-tests;
- PR-07 method contract;
- PR-09 constructibility rule;
- integrity scanner and integrity tests.

Generated post-freeze scientific result archives are not members at F; they bind their own producer,
inputs, and hashes when produced.

## 15.3 Git-history verification

Tests must:

1. require exact content-set equality;
2. validate every SHA-256;
3. prove F exists;
4. read every file from F with `git show F:path`;
5. recompute every digest from F's tree;
6. read and verify the freeze record from F;
7. require current normative bytes to equal F;
8. prove F is an ancestor of A;
9. enforce A's metadata-only diff allowlist;
10. require a new version and append-only deviation for later normative changes.

Test helpers against synthetic temporary Git histories before F exists.

---

## 16. P0-G8 producer scaffolding before freeze

To make “executable protocol” literal rather than aspirational, add a producer skeleton before F.

Recommended interface:

```text
python tools/paper_a_asymptotic_profile_limits.py --self-test
python tools/paper_a_asymptotic_profile_limits.py --run
python tools/paper_a_asymptotic_profile_limits.py --verify
```

Rules:

- `--self-test` uses only synthetic fixtures;
- `--run` refuses unless the manifest is operative and F verifies;
- `--run` refuses if any affected within-gate premise is unresolved;
- no campaign archive exists before activation;
- `--verify` recomputes semantic and hash bindings.

Synthetic fixtures must cover:

- resolved interior `J_ref`;
- reference minimum at either boundary;
- multiple finite components;
- a tangency;
- unresolved nested-grid convergence;
- endpoint included;
- endpoint excluded;
- endpoint indeterminate;
- near-zero relative threshold;
- six-of-six strong programme result;
- five-of-six qualified result;
- one exclusion;
- finite-topology unresolved with resolved endpoint;
- hard positivity failure.

---

## 17. Authorized next-cycle sequence

Complete, in this order:

1. implement the WIDE-reference architecture across plan/protocol/manifest/schema;
2. implement the coherent programme-level rule;
3. implement quantity-specific errors and the finite WIDE convergence envelope;
4. add the P0-G8 synthetic producer scaffold;
5. write the PR-03a fixed-time theorem and normalize its evidence;
6. repair PR-04 continuity, tie example, production interval, and positivity enforcement;
7. implement PR-07a/PR-07b staging;
8. implement the PR-09 eight-part rule;
9. reconcile active claims through an append-only pre-freeze delta;
10. replace premise gating with one fail-closed state machine;
11. create content commit C;
12. create closure commit D binding C;
13. implement and test freeze/activation history helpers;
14. return for renewed adjudication.

No scientific result may be computed in any step.

---

## 18. Prohibited activity

- no campaign `J`, `J_ref`, `J_inf`, threshold, topology, shoulder, or classification;
- no P0-G8 result archive;
- no P0-G4, G5, G6, G7, or G9 scientific execution;
- no PR-03b derivation;
- no result-dependent adjustment of the WIDE cap, grids, tolerances, or H1 rule;
- no manuscript title, abstract, results, discussion, or novelty drafting;
- no merge;
- no freeze commit F;
- no activation commit A.

---

## 19. Required terminal disposition

Return:

```text
P0_G0_PRE_FREEZE_CLOSURE_READY_PR_OPEN
```

only if:

- WIDE-reference mathematics is complete and internally consistent;
- the P0-G8 synthetic scaffold passes and campaign mode remains locked;
- PR-03a has a fixed-time proof and assumption-bound evidence;
- high-κ diagnostics no longer decide the theorem;
- PR-04 has a non-vacuous continuity proof/test, corrected tie claim, and production interval helper;
- PR-07 is staged;
- PR-09 uses the eight-part rule;
- every active claim surface is reconciled;
- premise gating is stage-aware and fail-closed;
- closure evidence is bound to content commit C;
- activation helpers verify F's committed tree and A's diff;
- no scientific gate or campaign objective has run;
- PR #224 remains open and unmerged.

Otherwise return:

```text
P0_G0_PRE_FREEZE_CLOSURE_NOT_READY
```

and enumerate every residual item.

---

## 20. Paste-ready execution directive

```markdown
# PAPER 1 — PR #224 WIDE-REFERENCE AND FINAL PRE-FREEZE COMPLETION

## Authority

- Reviewed head: `8d3e73b`
- Disposition: `P0_G0_PRE_FREEZE_CLOSURE_NOT_READY`
- Continue PR #224 open and unmerged.
- P0-G0 remains open; the plan remains candidate.
- No scientific gate, campaign objective, freeze commit F, or activation commit A is authorized.

## Governing estimand

Replace the unresolved global threshold with:

    D_WIDE = [0.15,500]
    J_ref  = min_{kappa in D_WIDE} min_{I>0} MAPE(y,I f(kappa))
    J_inf  = min_{I>0} MAPE(y,I f_inf)

Tag the result `FULL-WIDE-ENDPOINT`.

Classify the endpoint from verified J_inf and threshold intervals. A strict included endpoint plus the
fixed-time limit establishes that the WIDE-referenced operational acceptance set is unbounded above.
It does not enumerate topology in (500,infinity) and does not certify a finite onset.

PR-03b remains `NOT-PURSUED-CURRENT-PROTOCOL`;
`tail_onset_status = unresolved_by_design`.

## Mandatory work

1. P0-G8 architecture
   - continuous WIDE reference domain;
   - J_ref and J_inf definitions;
   - FULL-WIDE-ENDPOINT tag;
   - threshold interval propagation;
   - endpoint/upper-tail/onset/intermediate-domain fields;
   - strong/qualified/does-not-lead H1 rule;
   - explicit near-zero branch;
   - quantity-specific error budgets;
   - finite WIDE nested-grid convergence envelope;
   - no invented [kappa_c,infinity] component.

2. P0-G8 producer scaffold
   - synthetic --self-test;
   - operative-status lock on --run;
   - within-gate premise lock;
   - --verify;
   - no campaign archive before activation.

3. PR-03a
   - dedicated fixed-positive-time theorem;
   - no uniform-at-t=0 claim for off-manifold initial data;
   - verify semisimple zero and stable fast spectrum at every operator-distinct cell;
   - separate algebraic, construction, diagnostic, and coverage statuses;
   - high-kappa sequence diagnostic only;
   - capture warnings;
   - canonical --check;
   - input/producer/proof hashes.

4. PR-04
   - retain the weighted-median theorem;
   - prove continuity under general nonuniform positive perturbations;
   - replace the vacuous common-scaling continuity test;
   - correct the false "smallest fixture" statement using r=[1,2,2];
   - add a production helper returning the complete minimizer interval;
   - hard-fail on nonpositive/nonfinite inputs;
   - archive tie interval separately from objective error.

5. PR-07
   - PR-07a method freeze before P0-G0;
   - PR-07b campaign propagation within P0-G8;
   - use a two-optimizer value-function perturbation bound;
   - keep endpoint, reference, and shoulder errors separate.

6. PR-09
   - implement the eight-part raw-support/full-rank/residual-df/covariance rule;
   - otherwise return map_not_constructible and retain H3 as retrospective.

7. Reconciliation and controls
   - update the plan/protocol/manifest through a versioned or explicit pre-freeze amendment;
   - preserve the initial ledger and add an append-only pre-freeze claim-resolution delta;
   - correct PR-06 evidence to the endpoint producer;
   - update stale asymptotic-test prose;
   - replace premise gating with a single stage-aware fail-closed state machine;
   - generate R0a counts;
   - create content commit C and closure commit D;
   - verify every closure artefact from `git show C:path`.

8. Freeze/activation helpers
   - independently declare required normative content paths;
   - exact set equality with the freeze record;
   - include governing code/tests as well as documents;
   - verify every digest from `git show F:path`;
   - verify F ancestry and A's allowlisted metadata-only diff;
   - test with synthetic Git histories;
   - do not create F or A.

## Prohibited

- No campaign y/J/J_ref/J_inf/threshold/topology/shoulder/classification inspection.
- No P0 result archive.
- No scientific gate.
- No PR-03b attempt.
- No manuscript drafting.
- No merge, F, or A.

## Terminal response

Return `P0_G0_PRE_FREEZE_CLOSURE_READY_PR_OPEN` only when every mandatory item passes and PR #224
remains open/unmerged. Otherwise return `P0_G0_PRE_FREEZE_CLOSURE_NOT_READY`.
```

---

## 21. Final recommendation

Yes: the WIDE-referenced architecture is the correct next task.

Complete it before further endpoint assurance language is upgraded. The core Paper 1 proposition then
becomes precise:

> Prediction quality is evaluated against a finite, predeclared calibration domain; kinetic
> localization is evaluated separately by asking whether the analytical large-coefficient endpoint
> remains operationally acceptable relative to that reference.

That directly serves the new thesis without requiring a vacuous full-state remainder bound or an
unresolved global optimization over `(500,∞)`.
