\
# Paper 1 — PR #224 final pre-freeze completion adjudication

**Date:** 2 August 2026  
**Repository:** [`trbrewer/puckworks`](https://github.com/trbrewer/puckworks)  
**PR:** [#224](https://github.com/trbrewer/puckworks/pull/224), open and unmerged  
**Reviewed head:** [`504af0b`](https://github.com/trbrewer/puckworks/commit/504af0b)  
**Authority mode:** read-only adjudication; no repository file was modified and no scientific gate was run

---

## 1. Disposition

```text
P0_G0_PRE_FREEZE_CLOSURE_NOT_READY
PR_224_CONTINUE_OPEN_AND_UNMERGED
PR_06_ACCEPTED_IN_SUBSTANCE
PR_03A_ENDPOINT_CONSTRUCTION_ACCEPTED_IN_SUBSTANCE
PR_03A_FINAL_ASSURANCE_NORMALISATION_REQUIRED
PR_03B_NOT_REQUIRED_FOR_CURRENT_PROTOCOL
PR_03B_DO_NOT_RUN_IN_PR_224
P0_G8_WIDE_REFERENCED_ENDPOINT_CLASSIFICATION_REQUIRED
DETERMINISTIC_FINAL_COMPLETION_CYCLE_AUTHORIZED
P0_G0_REMAINS_OPEN
PLAN_REMAINS_CANDIDATE
NO_SCIENTIFIC_GATE_AUTHORIZED
FREEZE_COMMIT_F_NOT_AUTHORIZED
ACTIVATION_COMMIT_A_NOT_AUTHORIZED
```

> **Proceed with the deterministic remaining work. Do not spend the next cycle on PR-03b.**
>
> The stable null-basis endpoint is a real scientific correction and should be retained. The central
> P0-G8 result should compare the analytical endpoint with a threshold referenced to the resolved
> finite WIDE calibration domain. Under that architecture, a sharp finite-tail bound is not needed
> for the central claim and the tail onset is reported as unresolved by design.

No further conceptual pivot is required.

---

## 2. What is accepted

### 2.1 PR-03a's endpoint construction

The move from an ill-conditioned full-eigensystem projector to left/right null bases is accepted in
substance:

```text
A1 N = 0
L^T A1 = 0
L^T N = I
P = N L^T
A_s = L^T A0 N
z_inf(T) = N exp(A_s T) L^T z0
```

The reported projector residuals, condition of `L`, complete 27-operator/54-cell coverage, and
agreement with a finite-κ matrix-exponential reference are strong model-structural checks.

The previous discrepancy attributed to a convergence floor is correctly reclassified as conditioning
error in the eigen-projector construction.

### 2.2 PR-06 coverage

PR-06 is accepted in substance. All 54 declared variety–solute–condition cells are represented by 27
operator-distinct cells, with variety deduplication based on the declared model-only operator rather
than on an assumption that two outcomes are interchangeable.

The final archive must retain the complete 54-cell coverage map even when computation is deduplicated.

### 2.3 The reported criterion change

The change from a post-minimum ratio cap to an absolute sanity cap was disclosed before protocol
freeze and without inspecting campaign objectives. It is therefore not a hidden protocol violation.

It must nevertheless **not remain the proof or gate-closing criterion for convergence**. The direct
high-κ sequence is method-limited and should be a diagnostic control. PR-03a must close from the
algebraic fixed-time limit proposition plus verified assumptions and a stable endpoint construction.

---

## 3. A remaining category error: the threshold still uses an unresolved global minimum

The endpoint–tail lemma is correct for a **fixed threshold**:

```text
J(kappa) -> J_inf and J_inf < T
    => there exists K < infinity such that J(kappa) < T for every kappa >= K.
```

However, Protocol V2 currently defines:

```text
J_min = inf over kappa in [0.15, infinity] of J(kappa)
T     = a function of J_min
```

while the finite numerical search ends at `κ = 500`.

Without a quantitative bridge beyond 500, convergence to `J_inf` does not rule out a lower,
previously unseen minimum at a finite `κ > 500` before the eventual endpoint regime. Such a minimum
would change `J_min`, the threshold, and possibly the endpoint classification.

Therefore the statement—

> the endpoint decides inclusion and the finite-κ bound only localises the onset

—is fully valid only after the reference objective is made independent of the unresolved
`(500, infinity)` region, or after that region is certified.

### Decision

Use the first route. Redefine the central P0-G8 estimand as a **WIDE-referenced operational endpoint
classification**.

---

## 4. Required P0-G8 reference-domain architecture

### 4.1 Separate the finite reference domain from the endpoint

Freeze:

```text
D_WIDE = [0.15, 500]

J_WIDE(kappa) = min over I > 0 of MAPE(y, I f(kappa))

J_ref = min over kappa in D_WIDE of J_WIDE(kappa)

J_inf = min over I > 0 of MAPE(y, I f_inf)
```

The threshold families become:

```text
T_rel(q) = (1 + q) J_ref,  q in {0.05, 0.10, 0.20}
T_abs(a) = J_ref + a,      a in {0.10, 0.25} percentage points
```

The accepted set is:

```text
A_T^WIDE-ref = {kappa >= 0.15 : J(kappa) <= T(J_ref)}
```

This is an **operational acceptance set referenced to the best fit in the declared WIDE calibration
domain**. It is not a confidence set and it is not an unrestricted global-profile set.

### 4.2 Endpoint classification

For each group and convention:

```text
U_inf < L_T  -> endpoint_included
L_inf > U_T  -> endpoint_excluded
otherwise    -> endpoint_indeterminate
```

Given a proved fixed-time limit:

```text
endpoint_included
    -> A_T^WIDE-ref is unbounded above

endpoint_excluded
    -> A_T^WIDE-ref is eventually excluded

endpoint_indeterminate
    -> no upper-tail conclusion
```

### 4.3 Required wording

Permitted:

> Relative to the best fit in the predeclared WIDE calibration domain, the operationally accepted
> profile is unbounded above under the declared semi-discrete model.

Permitted, with the scientific consequence:

> Matched whole-cup predictive performance therefore does not provide finite upper localization of
> the model-specific mass-transfer-rate multiplier under that operational criterion.

Not permitted:

- “the unrestricted global profile is unbounded”;
- “the likelihood is unbounded”;
- “the parameter cannot be identified” without the operational qualifier;
- a numerical finite tail onset unless separately certified.

### 4.4 Estimand tag

Add and use a distinct tag, for example:

```text
FULL-WIDE-ENDPOINT
```

or:

```text
WIDE-REF-INF
```

Do not report this result under an estimand tag that implies unrestricted global minimization.

---

## 5. PR-03b decision

PR-03b is no longer required for P0-G0 or the central P0-G8 classification.

Change its audit row to:

```json
{
  "premise_id": "PR-03b",
  "disposition": "NOT-PURSUED-CURRENT-PROTOCOL",
  "resolution_stage": "scoped",
  "blocks_before": [],
  "failure_consequence": "no numerical finite tail onset is reported; endpoint result unaffected"
}
```

Freeze:

```text
tail_onset_status = unresolved_by_design
```

Remove:

- “one derivation cycle is authorised and unused”;
- any suggestion that the current paper may choose after P0-G8 whether to pursue it;
- any requirement that PR-03b complete before `P0_G0_PRE_FREEZE_CLOSURE_READY_PR_OPEN`.

A future sharp output-functional derivation may be treated as:

1. a separately versioned pre-result protocol amendment; or
2. a supplemental/future-study analysis explicitly unable to upgrade the frozen same-campaign
   primary claim.

It must not be selected after seeing the endpoint classifications.

---

## 6. PR-03a: final assurance normalization

The endpoint construction is accepted, but the current archive and producer are not yet adequate as
final gate evidence.

## 6.1 Add the fixed-time singular-limit proposition

State and prove, under the verified assumptions:

- zero is a semisimple eigenvalue of `A1`;
- every nonzero eigenvalue of `A1` lies strictly in the left half-plane;
- `A0` is finite and fixed;
- `P = N L^T` is the spectral slow projector;
- `T > 0` is the declared shot endpoint.

For each fixed `T > 0`:

```text
exp((A0 + kappa A1)T) z0
    -> N exp((L^T A0 N)T) L^T z0.
```

A suitable qualitative remainder has the form:

```text
||r_kappa(T)|| <= C_T/kappa + M_T exp(-c kappa T) ||Q z0||
```

for sufficiently large `κ`.

### Important initial-layer correction

Do **not** claim a uniform `C/κ` state bound on the complete interval `[0,T]` when `Q z0 != 0`.

At `t = 0`:

```text
z_kappa(0) - P z0 = Q z0,
```

which does not tend to zero with `κ`. The convergence is pointwise at every fixed positive time, or
uniform on `[delta,T]` for `delta > 0`.

The existing singular-bound contract says both that the horizon is `[0,T]` and that `z0` is off the
slow manifold. That uniform statement is therefore not established and must be withdrawn or
corrected.

## 6.2 Make the numerical sequence diagnostic, not dispositive

The present pass logic chooses the smallest observed error over `{10²,...,10⁶}` and then applies an
absolute post-minimum cap. A bounded finite sequence can validate a construction but cannot prove an
asymptotic limit.

Revise the archive fields to distinguish:

```text
algebraic_limit_status
endpoint_construction_status
finite_kappa_validation_status
method_conditioning_status
```

The `PR03A_LIMIT_CONVERGENCE_ASSURED` verdict must depend on the first two plus the verified
assumptions. The finite sequence is a supporting diagnostic.

Remove `TAIL_ABS_CAP` from the gate verdict. It may remain as a labelled non-decisive sanity
diagnostic only if its origin and units are recorded.

## 6.3 Correct the exit-code defect

The producer currently returns success when:

```python
result["verdict"].endswith("ASSURED")
```

Both of these strings end with `ASSURED`:

```text
PR03A_LIMIT_CONVERGENCE_ASSURED
PR03A_LIMIT_CONVERGENCE_NOT_ASSURED
```

Therefore the failure verdict also exits zero.

Replace this with exact equality:

```python
return 0 if result["verdict"] == "PR03A_LIMIT_CONVERGENCE_ASSURED" else 1
```

Add an adversarial test that forces one cell to fail and asserts a nonzero exit.

## 6.4 Correct diagnostic terminology

Rename:

```text
singular_gap
```

to something such as:

```text
svd_rank_separation_ratio
```

The current quantity is the ratio of the smallest retained singular value to the largest discarded
one. It is not the fast spectral decay gap.

Also:

- `cond(N)=1` is expected for an orthonormal SVD basis and should not be presented alone as evidence
  of operator conditioning;
- record `cond(L^T N)` before normalization, `cond(L)`, rank-tolerance sensitivity, and reduced
  operator diagnostics;
- require every `f_inf` to be finite, real within tolerance, and strictly positive;
- record SciPy as well as Python and NumPy versions.

## 6.5 Bind claims to generated evidence

The claim that a half-step recomputation differs by `1.1e-16` appears in comments but is not generated
into the archive. Either:

- implement and archive it with the exact method and cells; or
- remove the numerical claim.

A half-step composition using the same matrix-exponential implementation is an internal consistency
check, not an independent accuracy proof. Describe it accordingly.

Add:

```text
--check
```

that regenerates canonical output and byte-compares it with the archive.

Archive:

- command;
- producer path and hash;
- input/model paths and hashes;
- package versions;
- warnings/failures;
- reviewed protocol version;
- complete 54-cell coverage mapping.

---

## 7. PR-06 final closure

Close PR-06 from the stable endpoint/coverage producer, not from the obsolete full-state-bound
verdict.

The final evidence schema must distinguish:

```text
PR-03a endpoint construction
PR-06 complete declared coverage
PR-03b finite onset not pursued
```

The old singular-bound archive currently mixes PR-03 and PR-06 and contains contract strings that do
not describe its implementation. Retain it only as a versioned diagnostic/historical attempt or
regenerate it with a truthful non-operative verdict.

Do not describe the old full-state bound as “valid but loose” unless its fixed-time proof is repaired.
Its current stated uniform `[0,T]` contract is incompatible with an off-manifold initial condition.

---

## 8. Protocol V2 replacements

## 8.1 Outcome vocabulary

Use:

```text
reference_minimum_status:
  resolved | unresolved

endpoint_classification:
  endpoint_included | endpoint_excluded | endpoint_indeterminate |
  limit_construction_failed

upper_tail_status:
  wide_referenced_upper_set_unbounded |
  wide_referenced_eventually_excluded |
  upper_status_indeterminate

tail_onset_status:
  unresolved_by_design | certified_in_separate_analysis | not_applicable
```

Do not serialize an invented `[kappa_c, infinity]` component when the onset is unresolved.

## 8.2 Quantity-specific error budgets

### `J_ref`

```text
E_ref =
    E_finite_response_spatial
  + E_profile_arithmetic
  + E_global_minimum_convergence
  + E_floating_profile
```

### `J_inf`

```text
E_inf =
    E_reduced_endpoint_construction
  + E_endpoint_spatial
  + E_profile_arithmetic_endpoint
  + E_floating_endpoint
```

### Threshold

Propagate the `J_ref` interval only.

### Shoulder

```text
E_shoulder =
    E_derivative_step
  + E_derivative_spatial
  + E_derivative_floating
```

Never add shoulder error to `J_ref` or `J_inf`.

### Explicit exclusions

Do not add any of the following to `J_inf`:

- a finite-κ `C/κ` remainder;
- weighted-median inventory tie width;
- global-minimum isolation error;
- shoulder-derivative error.

## 8.3 Finite-domain topology

Report connected components only on:

```text
D_WIDE = [0.15,500]
```

and report the endpoint/upper-tail result separately.

Use a deterministic fail-closed convergence envelope:

1. nested log grids with fixed sizes, recommended `{40,80,160,320}`;
2. bounded minimization from every detected basin and both domain endpoints;
3. root refinement for every detected threshold crossing;
4. explicit tangency checks;
5. stability checks for `J_ref`, minimizer basins, roots, and finite components;
6. a predeclared empirical convergence envelope based on the final refinements;
7. `reference_minimum_unresolved` if `J_ref` does not stabilize;
8. `finite_topology_unresolved` if secondary components do not stabilize.

Describe the envelope as numerical convergence evidence, not a mathematically certified interval.

A secondary finite-component ambiguity need not block a strict endpoint result once `J_ref` is
resolved. An unresolved `J_ref` must block endpoint classification because it changes the threshold.

## 8.4 Programme-level H1 rule

Recommended frozen rule:

> H1 may lead only if at least five of six groups are `endpoint_included` under the 10% relative
> convention and at least one absolute convention; no group is `endpoint_excluded` or
> `endpoint_indeterminate`; every `J_ref` is resolved; and PR-03a passes. The result is always called
> WIDE-referenced. A finite tail onset is not required and is not claimed.

If classification changes across tolerance conventions, H1 does not lead.

---

## 9. PR-04 — exact weighted-median proposition

Close PR-04 before P0-G0.

For fixed `κ`, with `y_i > 0` and `f_i(κ) > 0`:

```text
MAPE(I;κ)
  = (100/n) sum_i |y_i - I f_i| / y_i
  = (100/n) sum_i [f_i/y_i] |I - y_i/f_i|.
```

Define:

```text
r_i = y_i/f_i
w_i = f_i/y_i > 0.
```

The minimizer set is exactly:

```text
{I : total weight strictly left of I <= W/2
     and total weight strictly right of I <= W/2}.
```

Equivalently, it is the complete weighted-median interval `[I_lower,I_upper]`.

Consequences:

1. a deterministic lower weighted median may be used for serialization;
2. the entire minimizer interval is archived;
3. the objective is exactly constant throughout that interval;
4. the tie width is inventory-level identification information, not objective error;
5. the profiled value is continuous as positive `f` approaches positive `f_inf`.

Required property tests:

- permutation invariance;
- one observation;
- all ratios equal;
- two-point exact flat interval;
- duplicate ratios and exact half-weight ties;
- extreme positive weights;
- common scaling;
- scaling `y` and corresponding inventory;
- scaling `f` and inverse inventory;
- comparison with a direct convex/reference calculation;
- objective constancy across the complete minimizer interval;
- hard failures for nonpositive or nonfinite `y`/`f`.

---

## 10. PR-07 staging

Split PR-07 into:

```text
PR-07a = numerical method and propagation contract, frozen pre-P0-G0
PR-07b = campaign-dependent interval evaluation, performed within P0-G8
```

### PR-07a — pre-freeze

Freeze and, where model-only, verify:

- meshes `{100,200,400}`;
- production mesh;
- endpoint response norm;
- finite-response error estimator and safety factor;
- endpoint mesh estimator;
- floating/reference method;
- derivative steps `{0.04,0.08,0.16}` in `log κ`;
- response-to-profile value-function propagation formula;
- unresolved/failure rules.

The log sensitivity satisfies:

```text
d log(I f)/d log(kappa) = d log(f)/d log(kappa)
```

when `I` is held fixed, so its numerical step/mesh validation is model-only and need not inspect the
campaign-fitted inventory level.

### PR-07b — within P0-G8

After activation, evaluate:

- the `y`-dependent propagation to `J_ref` and `J_inf`;
- the final quantity-specific intervals;
- the shoulder crossing and its numerical envelope.

Use a value-function bound that evaluates the prediction perturbation at both profiled optimizers,
rather than asserting an unproved global 1-Lipschitz statement.

---

## 11. PR-09 raw-support rule

Replace `>= 3 observations` with the complete rule already authorized.

After excluding the scored condition and every upstream object fitted using it, the cross-fitted map
is constructible only when:

1. raw observation-level hydraulic data and lineage are available;
2. the retained quadratic design has full column rank;
3. all pressure support needed by the model remains represented;
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

## 12. Premise-gating control remains incomplete

The code still contains a global test that treats every `OPEN` or `OPEN-BLOCKED` premise as a P0-G0
blocker. PR-15 is `OPEN-BLOCKED` but correctly staged to P0-G10. That legacy test will therefore keep
P0-G0 open even after every pre-freeze premise is resolved.

At the same time, the newer gate-scoped test only treats a pre-freeze premise with disposition
exactly `OPEN` as blocking. It does not catch:

- `implemented-not-proved`;
- `partially-assured`;
- `NOT-ATTEMPTED` if accidentally assigned pre-freeze;
- a future unrecognized nonterminal status.

Replace both with one fail-closed rule.

Recommended schema:

```text
resolution_stage:
  pre_freeze | within_gate | pre_drafting | scoped

terminal pre_freeze dispositions:
  assured | closed | withdrawn_with_scope
```

Then:

```python
pre_freeze_blockers = [
    row for row in premises
    if row["resolution_stage"] == "pre_freeze"
    and row["disposition"] not in TERMINAL_PRE_FREEZE
]
```

P0-G0 may not pass while that list is nonempty.

Add gate-specific enforcement for `within_gate` and `pre_drafting`.

Generate and test the R0a summary from the rows rather than manually maintaining counts.

---

## 13. Closure and provenance are not yet commit-bound

The closure records contain:

```text
evidence_content_commit = null
```

while the integrity test merely checks that the key exists. The manifest also retains
`closed_at_commit` values pointing to the pre-PR base for gates whose bound artefacts were introduced
later.

Therefore P0-G1a, P0-G3a, and P0-R0a are logically reviewed but not yet cryptographically closed.

The R0a closure record is also stale:

- it says the scope is 15 premises while the audit now contains 16;
- its criterion note predates the PR-03a/PR-03b split;
- it hashes only the audit file, while assured premises point to underlying evidence that is not
  hash-bound by that record.

### Required two-step closure

1. **Content commit C** finalizes the deliverables and underlying evidence.
2. **Closure commit D** records `evidence_content_commit = C`, hashes bytes read from C, and contains
   the closure record.
3. A later authority-controlled activation commit may record D as the gate closure commit.

Tests must:

- require a non-null 40-hex evidence content commit for every passed gate before P0-G0 closes;
- verify that commit exists;
- read each deliverable and producer from that commit with `git show C:path`;
- recompute the recorded hashes;
- verify each R0a assured premise's underlying evidence path/hash/locator;
- reject stale evidence counts and premise IDs.

Do not use a current-working-tree hash as a substitute.

---

## 14. Activation-test implementation

Implement the ceremony tests now, but do not create F or A.

Before freeze commit F can be authorized, the tests must establish:

1. exact set equality between the required normative content set and freeze-record entries;
2. full SHA-256 format for every entry;
3. F exists in both `candidate-frozen` and `operative` states;
4. every path exists in F;
5. every digest is recomputed from `git show F:path`;
6. the freeze record itself is read from F and its bytes remain unchanged;
7. current normative content is byte-identical to F;
8. F is an ancestor of activation commit A;
9. A changes only an explicit allowlist of status/closure metadata;
10. post-activation normative change requires a new protocol version and append-only deviation.

Unit-test the helper functions against temporary/fake git histories now so the controls are exercised
before F exists.

F and A remain authority-controlled and are not authorized in PR #224.

---

## 15. Required next-cycle scope

Complete the following in PR #224:

1. revise Protocol V2 to the WIDE-reference/analytical-endpoint architecture;
2. normalize PR-03a assurance and add the fixed-time proposition;
3. fix the PR-03a false-success exit code;
4. retire PR-03b from the current protocol and freeze onset unresolved;
5. repair PR-06 producer/archive consistency;
6. prove and test PR-04;
7. implement PR-07a/PR-07b staging;
8. implement the eight-part PR-09 rule;
9. replace the contradictory premise-blocking tests;
10. repair R0a and passed-gate evidence binding;
11. implement `git show F:path` and activation-history tests;
12. add substantive `--check` paths and canonical regeneration.

This is the final deterministic pre-freeze completion cycle. It should not open another scientific
method-development branch.

---

## 16. Prohibited activity

- no campaign `J`, `J_ref`, `J_min`, `J_inf`, threshold, topology, or classification computation;
- no P0-G8 archive;
- no P0-G4, G5, G6, G7, or G9 scientific execution;
- no PR-03b derivation in PR #224;
- no result-dependent choice of reference domain, tolerance, or topology rule;
- no manuscript title, abstract, results, discussion, or novelty drafting;
- no merge;
- no freeze commit F;
- no activation commit A.

---

## 17. Required terminal disposition

Return:

```text
P0_G0_PRE_FREEZE_CLOSURE_READY_PR_OPEN
```

only when:

- the WIDE-reference/endpoint distinction is complete;
- PR-03a has a correct fixed-time proof and stable generated evidence;
- the numerical high-κ sequence is diagnostic rather than the proof;
- the false-success exit-code bug is fixed;
- PR-03b is explicitly not pursued and onset is unresolved by design;
- PR-06 is reproducible and internally consistent;
- PR-04 is proved and tested;
- PR-07 is staged;
- PR-09 uses the eight-part rule;
- premise gating is genuinely gate-scoped and fail-closed;
- passed-gate evidence is commit-bound;
- activation helpers verify F's tree and A's allowed diff;
- no scientific gate or campaign objective has run;
- PR #224 remains open and unmerged.

Otherwise return:

```text
P0_G0_PRE_FREEZE_CLOSURE_NOT_READY
```

with every residual item.

---

## 18. Paste-ready execution directive

```markdown
# PAPER 1 — PR #224 FINAL DETERMINISTIC PRE-FREEZE COMPLETION

## Authority

- Reviewed head: `504af0b`
- Disposition: `P0_G0_PRE_FREEZE_CLOSURE_NOT_READY`
- Continue PR #224 open and unmerged.
- P0-G0 remains open and the plan remains candidate.
- No scientific gate, campaign objective, freeze commit F, or activation commit A is authorized.

## Governing scientific decision

Retain the stable analytical endpoint, but reference the operational threshold to the resolved finite
WIDE domain:

    D_WIDE = [0.15,500]
    J_ref = min_{kappa in D_WIDE} J(kappa)
    J_inf = exact profiled objective at the analytical endpoint

A strict endpoint result plus proved convergence establishes whether the WIDE-referenced operational
acceptance set is unbounded above. A sharp finite-kappa bound would only localise onset.

PR-03b is NOT required and must not be run in this PR. Freeze:
`tail_onset_status = unresolved_by_design`.

## Mandatory work

1. Protocol V2
   - replace global J_min over [0.15,infinity] with J_ref over D_WIDE;
   - define WIDE-referenced endpoint classification and estimand tag;
   - separate endpoint classification, upper-tail status, finite topology, and tail onset;
   - use quantity-specific error budgets;
   - remove finite-kappa remainder, weighted-median tie width, global-minimum error, and shoulder
     error from J_inf;
   - report finite components only on D_WIDE;
   - freeze a nested-grid fail-closed convergence envelope for J_ref;
   - revise the H1 rule to require resolved J_ref and strict endpoint inclusion.

2. PR-03a
   - add the fixed-positive-time singular-limit proposition;
   - state that convergence is not uniform at t=0 when Qz0 is nonzero;
   - base assurance on algebraic assumptions and stable endpoint construction;
   - demote the high-kappa sequence and absolute tail cap to diagnostics;
   - require finite, real, positive f_inf at every cell;
   - rename singular_gap to svd_rank_separation_ratio;
   - archive rank-tolerance/reduced-operator diagnostics and SciPy version;
   - implement canonical --check;
   - fix the false-success condition:
       verdict == "PR03A_LIMIT_CONVERGENCE_ASSURED"
     rather than `.endswith("ASSURED")`.

3. PR-03b
   - set `NOT-PURSUED-CURRENT-PROTOCOL`, `resolution_stage=scoped`, `blocks_before=[]`;
   - remove the unused-authorization language;
   - do not derive a new bound.

4. PR-06
   - close coverage from the stable endpoint producer;
   - keep all 54 declared cells visible;
   - make producer and archive agree exactly;
   - withdraw or historical-classify the old full-state uniform-bound claim.

5. PR-04
   - prove the weighted-median minimizer interval;
   - prove objective constancy on ties and continuity at the endpoint;
   - archive the full inventory interval;
   - add adversarial/property tests;
   - never add tie width to objective error.

6. PR-07
   - split method freeze (PR-07a) from within-gate campaign propagation (PR-07b);
   - freeze meshes, estimators, safety factors, derivative steps, propagation formula, and failures;
   - keep quantity-specific errors separate.

7. PR-09
   - implement the eight-part raw-support/full-rank/residual-df/covariance rule;
   - otherwise return map_not_constructible and retain H3 as retrospective only.

8. Gate/provenance controls
   - remove the legacy global OPEN/OPEN-BLOCKED P0-G0 test;
   - make every nonterminal pre_freeze disposition block;
   - generate/test the R0a summary;
   - update the stale R0a closure record;
   - require non-null evidence_content_commit before P0-G0 closure;
   - verify evidence with `git show C:path`;
   - bind each assured premise's underlying evidence.

9. Activation helpers
   - exact freeze-record coverage;
   - hash every file from `git show F:path`;
   - verify F existence/ancestry;
   - verify freeze-record bytes from F;
   - enforce A's allowlisted diff;
   - test helpers with synthetic git histories;
   - do not create F or A.

## Prohibited

- No campaign y/J/J_ref/J_inf/threshold/topology/classification inspection.
- No P0 result archive.
- No scientific gate.
- No PR-03b attempt.
- No manuscript drafting.
- No merge, F, or A.

## Terminal response

Return `P0_G0_PRE_FREEZE_CLOSURE_READY_PR_OPEN` only when every mandatory item passes and PR #224
remains open/unmerged. Otherwise return `P0_G0_PRE_FREEZE_CLOSURE_NOT_READY`.
```
