# Paper 1 — PR #224 pre-freeze structural-closure authorization

**Date:** 2 August 2026  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**PR:** [#224](https://github.com/trbrewer/puckworks/pull/224), open and unmerged  
**Reviewed head:** [`0bbf1266c743c91b5d5bd2582110072d84b5d3ed`](https://github.com/trbrewer/puckworks/commit/0bbf1266c743c91b5d5bd2582110072d84b5d3ed)  
**User-reported tree:** `a6fd917`  
**Authority mode:** read-only adjudication; this document authorizes a bounded follow-on cycle but does not freeze or activate the plan

---

## 1. Disposition

```text
P0_G0_PRE_FREEZE_STRUCTURAL_CLOSURE_AUTHORIZED
PR_224_CONTINUE_OPEN_AND_UNMERGED
P0_G0_REMAINS_OPEN
PLAN_REMAINS_CANDIDATE
P0_G8_AND_ALL_SCIENTIFIC_GATES_REMAIN_UNAUTHORIZED
FREEZE_COMMIT_F_NOT_AUTHORIZED
ACTIVATION_COMMIT_A_NOT_AUTHORIZED
```

> **Take on PR-03 and PR-06 now, but do so within an expanded pre-freeze closure cycle in PR #224.**
>
> PR-03 and PR-06 alone are not sufficient to make P0-G0 freeze-ready. The same cycle must close or correctly stage PR-04 and PR-07, repair three substantive P0-G8 protocol defects, and correct several gate/provenance controls.

The V2.2.1 assurance repair and R0a premise-audit design are accepted. R0a did exactly what it was intended to do: it exposed assumptions before activation. Protocol V2 is materially stronger than V1, and the scientific pivot remains approved. No further conceptual pivot is authorized or required.

---

## 2. Authorized work

### 2.1 PR-03 — explicit singular-limit remainder bound

Authorized: derive, implement, and independently test the analytical remainder bound for

```text
dz/dt = (A0 + κ A1) z
```

without using campaign chemical outcomes.

The existing nonzero-eigenvalue gap is encouraging but is not, by itself, a complete norm bound for a potentially non-normal matrix. Closure requires all of the following.

#### Required mathematical contract

1. **Fix the norm, output operator, and time horizon.**
   - State the state-space norm.
   - State the output norm used for `f`.
   - State the shot-time interval over which the bound is uniform.

2. **Prove or verify an index-one fast/slow decomposition.**
   - Verify that the zero eigenvalue of `A1` is semisimple.
   - At minimum, check `rank(A1) = rank(A1^2)` to declared numerical tolerances, or provide an equivalent projector proof.
   - Construct left/right slow projectors and verify projector identities and residuals.

3. **Bound fast-subspace decay in norm.**
   - Do not infer a semigroup bound solely from `max Re λ`.
   - Provide an explicit constant `M` and rate `γ` such that
     `||exp(t A1) Q|| <= M exp(-γ t)` on the fast subspace, in the declared norm.
   - Report non-normality/conditioning diagnostics and the numerical precision used.

4. **Include the `A0` coupling.**
   - Bound slow-to-fast and fast-to-slow coupling terms.
   - Include the initial-layer term unless the initial state is proved to lie on the slow manifold.
   - Derive an explicit finite-`κ` output bound, not merely big-O notation.

5. **Produce condition-specific constants.**
   - Report `M`, `γ`, projector conditioning, coupling norms, and the final remainder constant at every structurally distinct declared condition.
   - If varieties are algebraically duplicate at this stage, prove and record the duplication rather than silently reducing coverage.

6. **Independent verification.**
   - The predeclared high-`κ` sequence may verify the analytical bound.
   - It must not be used to fit the constant after observing violations.
   - A bound failure returns `PR03_BOUND_FAILED`; it is not repaired by enlarging the constant post hoc without a protocol deviation.

7. **Propagation interface.**
   - Provide the fixed formula by which the response-level bound will be propagated into the `J_inf` interval during P0-G8.
   - Do not compute `J_inf` or inspect campaign objective values in this cycle.

#### Required adversarial tests

- a diagonal normal fast block;
- a strongly non-normal but stable fast block;
- a defective or nearly defective zero eigenvalue that must fail the semisimplicity check;
- an off-manifold initial condition with a visible initial layer;
- a slow/fast coupling case with known asymptotics;
- a case in which spectral abscissa alone would understate transient growth;
- float64 versus higher-precision or interval-reference comparison on a reduced fixture.

---

### 2.2 PR-06 — all-condition analytical-limit coverage

Authorized: extend the analytical limit and verification control across the full declared P0-G8 model-only support.

#### Required coverage

The audit must cover the exact protocol support:

```text
9 calibration conditions × 2 varieties × 3 solutes
```

If some of those 54 cells share an identical operator or normalized response, the implementation may deduplicate computation only after proving the equivalence and retaining the full 54-cell coverage table.

#### Required outputs

The PR-06 artefact may contain:

- condition, variety, and solute identifiers;
- affine-structure residuals;
- rank/nullity and projector diagnostics;
- spectral/semigroup constants;
- analytical-versus-high-κ response errors;
- the applicable remainder bound;
- pass/fail/indeterminate status;
- producer, inputs, command, environment, and hashes.

It must not contain:

- campaign `y`;
- `J(κ)`, `J_min`, `J_inf`, or thresholds;
- tail classifications;
- profile components;
- shoulder locations;
- manuscript-language decisions.

#### Pass rule

PR-06 closes only if every declared cell:

1. admits the same declared limit construction;
2. passes structural and semigroup prerequisites;
3. converges to the analytical endpoint within the independently derived bound; and
4. has no unreported exception or silently widened tolerance.

Any failed cell keeps P0-G0 open and narrows the permissible H1 scope; no cell may be dropped.

---

## 3. Additional pre-freeze items that must be addressed in the same cycle

## 3.1 PR-04 cannot remain “implemented-not-proved”

Protocol V2 makes exact weighted-median profiling load-bearing for P0-G8, while R0a records the proposition as implemented but not proved and defers it to P0-G6. P0-G6, however, is downstream of P0-G8. The dependency is therefore backwards.

Before freeze:

1. state and prove the weighted-median proposition under `y_i > 0` and `f_i(κ) > 0`;
2. characterize the complete minimizer interval;
3. prove that the objective is constant over that interval;
4. retain deterministic lower-median reporting as a presentation convention only; and
5. add property tests against a direct convex/reference calculation, including ties, extreme weights, scaling, `n=1`, and positivity failures.

PR-04 should become `assured-algebraically` before P0-G8 is authorized.

---

## 3.2 PR-07 needs a frozen propagation procedure and correct staging

The current evidence concerns cup concentration, not yet `J_inf` or the response derivative. Resolve this in one of two explicit ways:

### Preferred disposition

Mark PR-07 as:

```text
disposition = OPEN-WITHIN-P0-G8
blocks_before = P0-G8
blocks_before_P0-G0 = false
```

and freeze, before P0-G0 closes:

- meshes;
- response norm;
- the exact mesh-error estimator;
- safety factor;
- convergence/failure criterion;
- formula propagating response error into `J_inf`;
- derivative-step/mesh interaction;
- rule returning `numerical_error_unresolved`.

The numerical value that depends on campaign `y` is then evaluated only inside P0-G8 after activation.

### Alternative disposition

Complete a model-only response/derivative mesh audit now and leave only the frozen objective propagation for P0-G8. Do not inspect any campaign objective.

---

## 4. Required corrections to Protocol V2

## 4.1 Remove the dimensionally invalid weighted-median tie-width term

Protocol V2 correctly says that the objective is identical across a weighted-median minimizer interval. It later lists “weighted-median tie width” as an error component added to `J_min` and `J_inf`.

That is not valid:

- tie width is in inventory-level units;
- `J` is in percentage points;
- the tie interval creates no exact-objective uncertainty.

Replace it with:

```text
exact-profile analytical error = 0
exact-profile numerical error = bounded floating-point/summation/order-statistic error
inventory minimizer interval = retained separately; never added to J
```

Add a units test that prevents any inventory-width quantity from entering an objective-error sum.

---

## 4.2 Make `J_min` isolation genuinely global or weaken the claim

The current topology algorithm begins from 40 WIDE-grid points, brackets sign changes, and flags near-grid tangencies. That does not guarantee that it has found:

- every local minimum;
- a narrow threshold component contained entirely between adjacent grid points;
- a tangency away from a sampled local minimum; or
- the global minimum used to build the threshold.

Freeze one of these contracts:

### Contract A — certified global isolation

Use compactified coordinates and a branch-and-bound or interval-enclosure method that gives lower and upper bounds on every unresolved interval, with a declared termination tolerance.

### Contract B — deterministic convergence envelope

Use nested predeclared grids and bounded scalar refinement on every interval; require stability of the minimum, local extrema, roots, and components across successive refinements; apply a conservative convergence envelope; return `topology_unresolved` if stability is not achieved.

Do not label an empirical grid-refinement envelope a mathematical verification interval.

---

## 4.3 Certify the interval between κ=500 and infinity

The domain includes `κ = ∞`, but the finite topology grid stops at `κ = 500`. Endpoint inclusion alone does not locate the start of an eventual upper-tail component or exclude a hole beyond 500.

Use the analytical remainder bound to derive a finite `κ_tail` such that the classification margin is certified for every `κ >= κ_tail`. Then:

- represent the certified tail as `[κ_tail, ∞]`;
- search the finite compact interval `[0.15, κ_tail]`;
- report any unresolved gap;
- do not invent a `κ_c` from endpoint classification alone.

A compactified coordinate such as `u = 1/κ` may be used, provided the endpoint and interval-error rules are explicit.

---

## 5. Correct the premise-gating logic

The current test treats every `OPEN` and `OPEN-BLOCKED` premise as a global P0-G0 blocker. That is too broad and conflicts with the declared gate graph.

Add an explicit field such as:

```json
"resolution_stage": "pre_freeze | within_gate | pre_drafting | scoped"
```

or:

```json
"blocks_before": ["P0-G0", "P0-G8", "P0-G9", "P0-G10"]
```

Then enforce the earliest affected stage.

Recommended classifications:

| premise | required stage |
|---|---|
| PR-03 | pre-freeze / before P0-G8 |
| PR-04 | pre-freeze / before P0-G8 |
| PR-06 | pre-freeze / before P0-G8 |
| PR-07 | frozen method before P0-G0; numerical evaluation within P0-G8 |
| PR-09 | within P0-G9 |
| PR-15 | before P0-G10 and manuscript drafting |
| physically untestable premises | scoped; never converted into repository “passes” |

The control must still fail closed at the correct stage. This is not permission to override a premise; it is a correction from global to gate-scoped enforcement.

---

## 6. Decision on PR-09 raw-support sufficiency

The existing `>= 3 observations` rule is not sufficient for the declared quadratic conductivity fit plus coefficient-covariance propagation. Three observations can identify three coefficients algebraically but leave zero residual degrees of freedom and no empirical covariance estimate.

Freeze this rule instead:

```text
cross-fitted map constructible only when, after removing the scored condition and every
upstream quantity fitted with it:

1. raw observation-level hydraulic data and lineage are available;
2. the retained quadratic design matrix has full column rank;
3. every pressure basis needed by the model remains represented;
4. residual degrees of freedom n_eff - rank(X) >= 2;
5. the retained support contains at least five independent observations for a
   three-coefficient quadratic;
6. the nominal shot-time anchor is independently reconstructible without the scored condition;
7. covariance is finite, positive semidefinite, and auditable; and
8. no chemical outcome enters construction, selection, or fallback.
```

If any required grind/variety lacks that support, return:

```text
map_not_constructible
H3_RETROSPECTIVE_ONLY
NO_PROSPECTIVE_OR_CROSSFITTED_CLAIM
```

Do not fabricate pseudo-observations from published coefficients, and do not count polynomial coefficients as raw observations.

PR-09 is a legitimate P0-G9 branch outcome, not a reason to prevent P0-G0 from freezing once the decision rule is complete.

---

## 7. Decision on PR-15

Leave PR-15:

```text
OPEN-BLOCKED-EXTERNAL
resolution_stage = pre_drafting
affected_gate = P0-G10
```

It must block:

- novelty wording;
- contribution claims;
- title/abstract finalization;
- manuscript drafting governed by P0-G10.

It must not block P0-G0 or P0-G8 because the manifest gives P0-G10 its own gate and no P0-G0 dependency. The current global-premise test should be corrected accordingly.

No indexed-novelty conclusion may be inferred from a general web search.

---

## 8. Governance and provenance corrections required before the PR can be accepted

### 8.1 Remove the operative plan from `superseded_plans`

`PAPER_1_PIVOT_AND_REDRAFT_PLAN_V2_2_1.md` is currently both `operative_plan` and a member of `superseded_plans`. Remove it from the superseded list and add an adversarial test asserting disjointness.

### 8.2 Correct impossible `closed_at_commit` provenance

The P0-G1a, P0-G3a, and P0-R0a closure records point to the pre-PR base commit even though their changed deliverables and closure records are introduced in PR #224. Do not retain a commit claim that cannot contain the bound artefacts.

Use a non-self-referential two-step pattern:

1. content commit C creates/finalizes the baseline artefacts;
2. closure commit D records `evidence_content_commit = C`, hashes the artefacts from C, and marks the gates passed.

The closure record need not claim its own containing commit. The manifest’s eventual activation commit can identify D after D exists.

Tests must verify each bound artefact by reading it from the recorded content commit, not merely from the current working tree.

### 8.3 Complete activation verification

Before F is authorized, tests must establish:

- exact set equality between required normative content and freeze-record entries;
- every SHA-256 is full and correct;
- F exists;
- every frozen path exists in F;
- each hash recomputed from `git show F:path` matches;
- current normative content remains byte-identical to F;
- activation commit A changes only an allowlisted status/closure surface;
- F is an ancestor of A;
- any later normative change requires a new version and deviation.

Current-tree hash checking alone is not enough.

---

## 9. Allowed and prohibited activity

### Allowed

- PR-03 derivation and structural/numerical verification;
- PR-06 all-condition model-only coverage;
- PR-04 formal proof and tests;
- PR-07 method completion and model-only mesh/derivative controls;
- protocol corrections listed above;
- premise-stage and gate-graph repair;
- PR-09 source-support inventory without scoring chemical outcomes;
- closure/provenance and activation-test repair;
- unit, property, adversarial, static, and integrity tests.

### Prohibited

- P0-G8 execution;
- campaign `J`, `J_min`, `J_inf`, threshold, topology, or classification inspection;
- generation of `PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json`;
- P0-G4, G5, G6, G7, or G9 scientific execution;
- post-result tuning of constants, grids, tolerances, support rules, or branch rules;
- title, abstract, results, discussion, or novelty drafting;
- freeze commit F or activation commit A;
- merging PR #224 before renewed adjudication.

---

## 10. Required terminal disposition

Return exactly one of:

```text
P0_G0_PRE_FREEZE_CLOSURE_READY_PR_OPEN
```

only if:

- PR-03 has an explicit, independently verified bound with constants;
- PR-06 covers every declared cell;
- PR-04 is formally assured;
- PR-07 is correctly specified/staged;
- all three P0-G8 protocol corrections are implemented;
- premise blocking is gate-scoped;
- PR-09 uses the revised raw-support rule;
- PR-15 is scoped to P0-G10/drafting;
- operative/superseded-plan disjointness is enforced;
- closure provenance is truthful and commit-verifiable;
- activation tests verify F's tree and exact content coverage;
- no scientific gate or campaign objective was run;
- PR #224 remains open and unmerged.

Otherwise return:

```text
P0_G0_PRE_FREEZE_CLOSURE_NOT_READY
```

with every unmet item and keep all scientific gates blocked.

---

## 11. Paste-ready execution directive

```markdown
# PAPER 1 — PR #224 PRE-FREEZE STRUCTURAL-CLOSURE CYCLE

## Authority

- Reviewed head: `0bbf1266c743c91b5d5bd2582110072d84b5d3ed`
- Disposition: `P0_G0_PRE_FREEZE_STRUCTURAL_CLOSURE_AUTHORIZED`
- Continue PR #224 open and unmerged.
- P0-G0 remains open; the plan remains candidate.
- No P0 scientific gate, freeze commit F, or activation commit A is authorized.

## Objective

Complete the pre-freeze mathematical, numerical, protocol, and provenance prerequisites
needed for a renewed P0-G0 adjudication.

## Mandatory work

1. Close PR-03 with an explicit singular-limit remainder bound:
   - fixed state/output norm and time horizon;
   - semisimple zero-eigenvalue/index-one check;
   - verified slow/fast projectors;
   - non-normal semigroup constant M and rate gamma;
   - A0 coupling and initial-layer terms;
   - condition-specific constants;
   - independently bounded high-kappa verification;
   - fixed response-to-J propagation formula.

2. Close PR-06 over all 9 conditions x 2 varieties x 3 solutes.
   Retain every cell and every failure. Do not access campaign chemical outcomes.

3. Close PR-04 before P0-G8:
   - formal weighted-median proposition;
   - complete minimizer interval;
   - constant objective over ties;
   - deterministic lower-median convention;
   - adversarial/property tests.

4. Correctly stage PR-07:
   - freeze meshes, norm, estimator, safety factor, propagation formula,
     derivative/mesh interaction, and unresolved rule;
   - evaluate any campaign-dependent numerical term only within P0-G8 after activation.

5. Repair Protocol V2:
   - remove weighted-median tie width from the J error budget;
   - add genuine global-minimum/component isolation or a fail-closed deterministic
     convergence envelope;
   - certify the tail beyond kappa=500 using the analytical remainder bound and derive
     a finite kappa_tail.

6. Replace global premise blocking with gate-scoped resolution stages.
   PR-09 belongs to P0-G9; PR-15 belongs to P0-G10/pre-drafting.

7. Replace PR-09's >=3 rule:
   - raw observation lineage required;
   - full-rank quadratic design;
   - at least two residual degrees of freedom and at least five independent observations;
   - independently reconstructible shot-time anchor;
   - finite auditable covariance;
   - otherwise `map_not_constructible` and H3 remains retrospective.

8. Fix governance/provenance:
   - remove V2.2.1 from `superseded_plans`;
   - replace impossible closure-commit claims with a content-commit/closure-commit pattern;
   - verify closure artefacts from the recorded commit tree;
   - enforce exact freeze-record coverage and `git show F:path` hash checks;
   - add activation-diff and ancestry checks.

## Prohibited

- No campaign J/J_min/J_inf/profile/topology/classification inspection.
- No P0 result archive.
- No scientific gate.
- No post-result tuning.
- No manuscript drafting.
- No merge.
- No F or A.

## Terminal response

Return `P0_G0_PRE_FREEZE_CLOSURE_READY_PR_OPEN` only when every mandatory item
passes and the PR remains open/unmerged; otherwise return
`P0_G0_PRE_FREEZE_CLOSURE_NOT_READY`.
```
