# Code review

Reviewer: Codex, nonhuman implementation author. This is an author code review,
not an independent review or fabricated human approval. Normal PR owner review
remains pending on the draft. CODEOWNERS names @trbrewer; the live Protect-main
ruleset requires a PR and named checks, with zero mandatory approving reviews.
No G1 pre-scoring review process applies to this G0 synthetic capability.

Reviewed the final numerical producer hashes recorded in RESULTS.json and the
runner hash recorded in JOINT_REPAIR_CORRECTION.json. Documentation-only edits
reuse that numerical evidence. Review focus and outcomes:

- Inner/outer rows have the required signs; all original cell, phase and total
  constraints remain present. Actual inner constraints and the stricter replay
  search reserve are separate. Empty inner and nonempty outer states do not
  become incompatibility/compatibility certificates. Exact nonunique fixtures,
  nonzero-error counterexamples, duplicates and near-dependent rows cover this.
- Infeasibility requires a positive independently checked phase-I weak-duality
  lower bound, or exact singleton/original-set contradiction. All observation
  rows enter the original-kg finite-box certificate. Status 2 alone is rejected.
  An explicit independent rational dual proves the manufactured joint conflict.
- Reconstruction checks representable states. The initial full campaign exposed
  rejected boundary witnesses and failed repair LPs. The bounded correction
  checks a box projection against ALL original and actual inner rows, with no
  phase/total rebalancing. A test rejects an inventory-feasible state that violates
  one observation. Initial results, raw masses and repair work remain visible.
- HiGHS tolerances propose candidates/duals only; no primal feasibility tolerance
  certifies observations. Binary-rational residual and dual checks use original
  coordinates, directed conversion and explicit underflow rejection. Search
  margins and mass-change caps are exposed. Bad signs, loose duals, status/clock
  limits and epsilon below numerical resolution fail honestly.
- Every accepted witness replays all windows through unchanged dynamics and
  requires whole-interval band containment; overlap is rejected. Complete
  extremum gaps include response, relaxation, reconstruction and replay error.
  Coefficient error remains an engineering estimate, not an interval certificate.
- Empty native queries delegate exactly to 005. Fine comparison retains native
  identities and explicit equal-child pullback; it does not introduce fine-cell
  freedom. Native cache restoration validates identity and never propagates.
- Campaign counters persist across corrections, all native calls have external
  deadlines, failed calls remain charged, and arrays/records are immutable.
  Full-mesh code is separate from ordinary N<=12 tests. No dependency, registry,
  workflow, test selector or coverage-floor change is present.

Bounded findings corrected on this branch: the generating harness accepts a
valid early PLANNED_STOP; actual inner/search sets are separated; a projected
candidate must pass every joint row; repair-call accounting counts actual LP
invocations. Regression tests and the named correction receipts substantiate
these changes. No remaining author-identified blocker to the declared engineering
capability was found. Human/independent review and exact-head hosted CI are
separate states and are not inferred from this review.
