# Paper 1 — PR #224 PR-03a exact-head review

**Date:** 3 August 2026  
**Repository:** `trbrewer/puckworks`  
**Pull request:** #224, open and unmerged  
**Reviewed head:** `596223fb23957364b54d90799e2cd2ba4d902a80`  
**Reviewed tree:** `e77286b468c385ac4d21666f1f5629bb96107b52`  
**Parent:** `bb88809bdf8bc477093ccbe14bb59b4232cafff9`  
**Review mode:** exact-head, read-only

---

## 1. Disposition

```text
PR03A_FORMAL_ASSURANCE_NOT_READY
PR03A_QUALITATIVE_FIXED_TIME_LIMIT_ACCEPTED_IN_SUBSTANCE
PR03A_STABLE_NULL_BASIS_ENDPOINT_ACCEPTED_IN_SUBSTANCE
PR03A_QUANTITATIVE_BOUND_STATEMENT_REPAIR_REQUIRED
PR03A_SEMISIMPLICITY_VERIFIER_REPAIR_REQUIRED
ONE_BOUNDED_PR03A_CORRECTION_COMMIT_AUTHORIZED
PR_224_CONTINUE_OPEN_AND_UNMERGED
P0_G0_REMAINS_OPEN
P0_G8_REMAINS_OPEN
PLAN_REMAINS_CANDIDATE
NO_SCIENTIFIC_GATE_AUTHORIZED
NO_CAMPAIGN_OBJECTIVE_AUTHORIZED
FREEZE_COMMIT_F_NOT_AUTHORIZED
ACTIVATION_COMMIT_A_NOT_AUTHORIZED
```

> The stable endpoint construction, model-only coverage, diagnostic/proof separation, and
> fixed-positive-time qualitative limit are substantial progress. Exact-head formal assurance is
> nevertheless withheld because the written quantitative theorem is not homogeneous in `z0`, and
> the new largest-gap semisimplicity rule can falsely accept a defective zero eigenvalue under
> block-scale separation.

These are PR-03a corrections. They do not reopen the accepted WIDE-reference architecture.

---

## 2. What is accepted in substance

The following work is accepted and should be retained:

1. the left/right null-basis endpoint
   `N exp((L^T A0 N)T)L^T`;
2. the rejection of a uniform-at-`t=0` convergence claim for off-manifold initial data;
3. the separation of:
   - algebraic limit;
   - endpoint construction;
   - finite-κ diagnostic;
   - coverage;
   - overall PR-03a status;
4. the demotion of the high-κ sequence to a diagnostic;
5. model-only coverage of 27 operator-distinct cells representing all 54 declared cells;
6. the corrected exact-equality process exit rule;
7. the canonical `--check` path and generated provenance;
8. the explicit state transition for the eventual-upper premise, subject to final PR-03a acceptance.

The current proof contains the correct core mechanism: a Hurwitz fast block, a Lyapunov decay estimate,
an `L1` bound on the fast component, and a Grönwall estimate for the slow component. The qualitative
conclusion for every fixed positive time is defensible once the assumptions are correctly verified.

---

## 3. Blocking defect A — the quantitative theorem is not homogeneous in the initial state

The theorem states that there are constants `C_T` and `M_T` derived from operator and basis quantities
such that:

```text
||r_kappa(T)|| <= C_T/kappa + M_T exp(-gamma kappa T)||Qz0||.
```

But the proof defines:

```text
K = (2M/gamma)[v(0) + c T exp(aT) u(0)]
```

and then defines `C_T` using both `K` and `sup u`. Since:

```text
u(0) = ||L^T z0||
v(0) = ||M^T z0||
```

both `K` and `sup u` depend linearly on `z0`. Therefore the displayed `C_T` is not a constant derived
only from the operator, basis, and `T`.

The error is exposed by scaling. Replacing `z0` by `alpha z0` multiplies the residual by `|alpha|`,
whereas the displayed first term `C_T/kappa` does not change.

### Required repair

Use either of these mathematically coherent formulations.

#### Preferred operator-level formulation

Derive constants independent of `z0` and state:

```text
||r_kappa(T)||
    <= (C_T/kappa)||z0||
       + M_T exp(-gamma kappa T)||Qz0||.
```

For example, bound:

```text
u(0) <= ||L^T|| ||z0||
v(0) <= ||M^T|| ||z0||
K    <= K_T ||z0||
```

with:

```text
K_T = (2M/gamma)[||M^T|| + c T exp(aT)||L^T||],
```

and carry this through the slow and fast estimates.

#### Acceptable fixed-input formulation

State explicitly:

```text
||r_kappa(T)||
    <= C_{T,z0}/kappa
       + M_T exp(-gamma kappa T)||Qz0||.
```

This proves convergence for each fixed `z0`, but it is not the operator-level quantitative bound
currently claimed.

### Required test/document corrections

- Add a scaling fixture showing the residual is homogeneous in `z0`.
- Remove the test wording that says the numerical fixture verifies “exactly the `C_T/kappa` bound.”
  It verifies first-order `O(1/kappa)` behavior for that fixture.
- Bind the archive to the corrected theorem hash.
- Regenerate the claim-resolution delta and premise evidence.

The qualitative matrix limit may remain, but the quantitative “Moreover” statement must be corrected.

---

## 4. Blocking defect B — the largest-gap rank rule can falsely accept a defective zero

The current `_separated_rank()` chooses the largest adjacent singular-value ratio. The producer
asserts that a defective zero produces no such separated gap. That assertion is false in general.

An explicit counterexample is:

```text
J0 = [[0,1],
      [0,0]]

A1 = block_diag(J0, [-10^9]).
```

Zero is defective because of the Jordan block. Yet:

```text
singular_values(A1)   = [10^9, 1, 0]
singular_values(A1^2) = [10^18, 0, 0]
```

Under the current largest-gap routine:

```text
rank_A1         = 1
rank_A1_squared = 1
semisimple      = True
```

The fast scale creates a larger gap before the Jordan singular value than at the true
nonzero/zero cut. The existing Jordan-2 and Jordan-3 fixtures use comparable block scales, so they do
not expose this false positive.

### Required repair

Do not infer the model rank from the globally largest gap.

For this model, freeze the structurally derived fast rank:

```text
expected_fast_rank = 400
expected_slow_nullity = 201
```

Then, at the **expected cut**, require all of the following:

1. `A1` has a declared and sufficiently large retained/discarded separation;
2. `A1^2` has the same expected rank;
3. the null-basis construction uses the same expected rank;
4. the ordered-Schur fast-mode count is the same expected rank;
5. the left/right slow pairing is nonsingular and acceptably conditioned;
6. projector identities pass;
7. every disagreement returns `not_assured`.

A model-derived structural-rank proof should be archived. The SVD gap is then a verification of the
declared cut, not a procedure for discovering whichever cut has the largest scale separation.

An equivalent robust implementation based on a frozen expected zero-cluster dimension and an ordered
Schur slow-block check is acceptable, provided it rejects the scaled-Jordan counterexample.

### Required adversarial tests

At minimum:

```text
block_diag(Jordan2(0), [-10^6])
block_diag(Jordan2(0), [-10^9])
block_diag(Jordan2(0), [-10^12])
block_diag(Jordan3(0), stable fast block with large scale separation)
```

Every case must return non-semisimple or fail-closed.

Also add tests that deliberately force disagreement among:

```text
semisimplicity rank
null-basis rank
Schur fast-mode count
expected structural rank
```

and require an overall `not_assured` result.

---

## 5. Required terminology correction

The proof says the output functional “lies in `ker(A1)`.” A linear output row is a covector, not a
state vector.

Use one of the precise formulations:

```text
the output covector lies in ker(A1^T);
```

or:

```text
the output covector annihilates the fast subspace, equivalently e_out Q = 0.
```

The producer already records the latter numerical check. This is a wording correction, not a change
to the endpoint construction.

---

## 6. Eventual-upper precondition state

Changing:

```text
EVENTUAL_UPPER_PRECONDITION_CURRENT:
    unresolved -> assured
```

was within the authorized PR-03a exception **if and only if** formal assurance closed.

Because exact-head acceptance is withheld, the next correction commit may leave the final value as
`assured` only when:

- the theorem statement is corrected;
- the semisimplicity verifier is repaired;
- all 27 cells pass the repaired checks;
- the 54-cell mapping remains complete;
- the archive is regenerated;
- `--check` passes; and
- all adversarial tests pass.

Otherwise the state must be `unresolved`.

No endpoint classification, threshold, H1 rule, WIDE formula, grid, or tolerance may change.

---

## 7. Untracked campaign scratch material

The user reports that:

```text
docs/paper1_resource/scratch/
```

contains a preliminary campaign `J_inf` task and is untracked.

It is not part of reviewed commit `596223f`, so it does not contaminate this exact-head review.
Nevertheless, it is inside the repository tree and belongs to work explicitly prohibited during the
pre-freeze cycle.

Before the next exact-head submission:

- move that directory outside the repository;
- do not commit or inspect its campaign output in this cycle; and
- return a clean `git status --short`.

No campaign-derived scratch artefact may be hidden by a committed ignore rule and left inside the
controlled repository workspace.

---

## 8. CI runtime

The narrow CI margin is noted but is not a PR-03a scientific blocker because the reported exact head
is green.

Do not mix timeout, matrix, sharding, or workflow changes into the PR-03a correction commit. Treat CI
runtime resilience as a later bounded infrastructure cycle.

---

## 9. Authorized correction scope

Create one normal commit on top of:

```text
596223fb23957364b54d90799e2cd2ba4d902a80
```

Do not amend, rebase, squash, force-push, merge, or create F/A.

Authorized paths are limited to:

1. `PAPER_A_FIXED_TIME_SINGULAR_LIMIT_PROPOSITION.md`;
2. `tools/paper_a_endpoint_construction.py`;
3. focused PR-03a tests;
4. `PAPER_A_ENDPOINT_CONSTRUCTION.json`;
5. PR-03a premise/audit and claim-resolution evidence;
6. the one precondition-state line/comment in `wide_reference.py`, if required;
7. integrity/source-surface declarations strictly required by these files.

No WIDE-reference architecture item may change.

---

## 10. Required validation

Run at minimum:

```text
python tools/paper_a_endpoint_construction.py --check

ruff check \
  tools/paper_a_endpoint_construction.py \
  tests/test_paper_a_pr03a_limit.py

pytest -q tests/test_paper_a_pr03a_limit.py
pytest -q tests/test_paper_a_wide_reference.py tests/test_paper1_plan_integrity.py
pytest -q
```

The correction must additionally demonstrate:

- the scaled-Jordan counterexample is rejected;
- the expected-rank cross-check fails closed;
- the corrected bound is homogeneous in `z0`;
- all 27 operator-distinct cells pass;
- all 54 declared cells remain covered;
- no scientific result archive exists;
- no campaign objective was run or inspected;
- the working tree is clean;
- PR #224 remains open and unmerged.

---

## 11. Required terminal disposition

Return:

```text
PR03A_FORMAL_ASSURANCE_CORRECTION_COMPLETE_PR_OPEN
```

only when every requirement above passes.

Otherwise return:

```text
PR03A_FORMAL_ASSURANCE_CORRECTION_NOT_READY
```

and list only the residual items from this review.

---

## 12. Paste-ready execution directive

```markdown
# PAPER 1 — PR #224 PR-03A FORMAL-ASSURANCE CORRECTION

## Authority

- Reviewed head: `596223fb23957364b54d90799e2cd2ba4d902a80`
- Disposition: `PR03A_FORMAL_ASSURANCE_NOT_READY`
- Continue PR #224 open and unmerged.
- P0-G0 and P0-G8 remain open; the plan remains candidate.
- No campaign objective, scientific gate, merge, F, or A is authorized.

## Mandatory correction A — theorem homogeneity

Replace the displayed quantitative bound with either:

    ||r_kappa(T)||
      <= (C_T/kappa)||z0||
         + M_T exp(-gamma kappa T)||Qz0||

with operator-derived constants, or an explicitly fixed-input
`C_{T,z0}/kappa` formulation.

Carry `||z0||` through K and sup-u. Update the proof, archive hash, wording, and tests.
The numerical fixture demonstrates O(1/kappa) behavior; it does not verify an unscaled universal
C_T/kappa bound.

## Mandatory correction B — semisimplicity

Do not select rank from the globally largest SVD gap.

Freeze and archive the model-derived structural rank:

    expected_fast_rank = 400
    expected_slow_nullity = 201

At that cut require consistent A1 rank, A1^2 rank, null-basis rank, Schur fast count, slow-pairing
invertibility, and projector identities. Any disagreement is not_assured.

Add scaled defective fixtures, including:

    block_diag(Jordan2(0), [-1e9])

which the current rule falsely accepts.

## Terminology

Replace “output functional lies in ker(A1)” with:
“output covector lies in ker(A1^T)” or “e_out Q = 0.”

## State

The eventual-upper precondition may be `assured` only if the corrected theorem and repaired
assumption verifier pass at all cells. Otherwise it is `unresolved`.

## Workspace

Move the untracked campaign scratch directory outside the repository. Return a clean working tree.
Do not inspect, commit, or use campaign output.

## Prohibited

- No change to D_WIDE, J_ref, J_inf, thresholds, H1, grids, topology, tolerances, budgets, or archive
  programme-result logic.
- No P0-G8 result archive or scientific gate.
- No PR-03b, PR-07, PR-09, CI-workflow change, manuscript drafting, merge, F, or A.

## Terminal response

Return `PR03A_FORMAL_ASSURANCE_CORRECTION_COMPLETE_PR_OPEN` only when the bounded correction is green,
the archive regenerates, the scaled-Jordan fixture is rejected, the working tree is clean, and PR
#224 remains open/unmerged. Otherwise return
`PR03A_FORMAL_ASSURANCE_CORRECTION_NOT_READY`.
```
