# Independent exact-freeze pre-score review

**Decision: APPROVED for one predeclared frozen PRED score, with no retuning.**

Task: SCI-MD-TRIGONELLINE-DELIVERY-001. Reviewer: independent Codex review
agent `independent_trigonelline_review`, not a human reviewer. I did not
implement, fit, select, modify, or freeze this candidate. The review request
was not treated as approval. This decision follows inspection and the checks
recorded below. There are **no unresolved blocking findings**.

Reviewed head: `de31200f272711ca6b2e9fc5dc7c4881c406ab56`.
Reviewed tree: `dd6fd3c9d835ef9793ba88a47661c6abb37e4613`.
Freeze SHA-256: `6f1b1afc73615eafb9b463b49089a1069d60179ea96b2a02a2951a9ec22f0b12`.

This is G1, RESEARCH_ONLY, NO_GOVERNING_PHYSICS_CHANGE. Approval does not
authorize fitting, prediction repair, rescoring, EWP consumption, native
execution, production or registry changes, merge, adoption, or a successor.
The scientific outcome remains NOT_ADJUDICATED until the sole authorized
score completes. Physical validation and analytical uncertainty remain
NOT_ESTABLISHED. SOURCE_INTERNAL, TARGET_EXPOSED, retrospective and
campaign-separated limitations remain mandatory.

## Evidence and substantive findings

I read the repository rules, onboarding, governance standard, controlling
task documents, all three new modules and their tests, inherited D0 runtime
and training implementation, and the actual source, serialization, geometry
and receipt mechanisms used. The change contains 21 added task-local files;
accepted existing scientific code and production files are unchanged.

All 646 frozen artifact bindings and 53 code/protocol bindings match the
exact checkout. The immutable protocol commit precedes the first real-fit
receipt. Relevant accepted dependency files are byte-identical at the
caffeine publication, evaluated producer and accepted-main identities named
in DEPENDENCIES.json. Actual first-party imports are covered by the freeze.
The source files and all ten source registers match their recorded hashes.
Both baseline suite logs match the hashes recorded in BASELINE.json; their
exit records are zero. The parent is performing final full regression
separately; this approval does not claim that pending suite has completed.

The source projection selects trigonelline independently as MATLAB
`cAlcaloids(:,2)` and HPLC column T, with the declared source mg/g to internal
kg/kg conversion. I independently reconciled all 180 FIT slots against the
FIT MATLAB and original HPLC cached masses. PRED originals were **hashed
only**. For their identity, finite/valid status and HPLC formula
reconciliation I inspected the retained target-blind audit implementation,
its aggregate report and its hash binding; I did not rerun a PRED chemical
read. Neither PRED concentration values nor patterns entered my review.
The report retains the unavailable analytical-uncertainty and censoring
limits rather than replacing them with numerical budgets.

The frozen population is 45 FIT physical shots in 15 original designs and
180 intended slots, including the three unsupported measured prefixes.
There are 177 supported windows; every design has at least two physical
shots with at least three windows. Every complete original design is
excluded from its training fold. I reconstructed training-only transforms,
domain limits, support masks, weights and provenance for all 77 saved
development/final models. The fixed lambda grid, three starts, coefficient
bounds, residual scale, penalty, optimizer settings and tie rules match
the declared inherited D0 architecture. No caffeine coefficient or chemical
input enters this task's mass-only inference.

Without optimizing, I independently evaluated all 183 retained parameter
vectors using separately written 96-point split-knot quadrature. Their
objective values differ from the retained values by at most
`5.551115123125783e-16`. Every selected start is the declared minimum with
the declared tie rule. Saved fold inference reproduces every development
metric exactly, and the predeclared selection returns lambda `0.0001`.
Both final FIT qualifications reproduce exactly. Public development and
execution evidence reconcile with the private artifacts after the declared
aggregation.

Durable receipts reconcile to 183/183 converged iterative starts, 16 analytic
fits, 25,875 actual residual calls including 24,240 numerical-Jacobian calls,
178 maximum calls per start, 5.2541000079363585 seconds total optimizer wall
time, a 56.57155203819275-second fitting-clock span, and 84,592 KiB recorded
peak RSS. Each retained numerical-Jacobian count is 15 times its Jacobian
evaluation count, and residual totals reconcile with optimizer evaluations.
Initial parameters, coefficient bounds, paired receipts and fixed budgets
were checked. Review verification calls are separate from those scientific
counts; this review made zero new fit or optimizer calls.

The actual `verify` CLI and guarded in-process replay reproduce all 192
arm/slot predictions and states exactly. Both arms retain 48/48 primary,
24/24 temperature and 23/24 flow support. Every supported interval is
numerically qualified; the maximum interval allowance across the checked
development/PRED evidence is `2.6897619180896414e-16` kg. Prediction artifacts
contain no attached observed outcome fields. Review replay made no writes
to the frozen run, no outcome join, and no score or report call.

The scorer uses original physical-shot mass-weighted RMSE and absolute
shot bias, retains original shot/condition denominators, propagates numerical
allowances, and applies the frozen 0.25/0.125 mg/g adequacy limits and all
four complexity requirements. Incomplete secondary support cannot become
a complete-scope success. Exact approval and an exclusive receipt precede
the outcome join; ten independently constructed invalid approval variants
were rejected. The report path consumes the retained completed score.

## Independent verification and limits

- Focused repository tests: **23 passed, 2 deselected**. The two deselections
  are the synthetic iterative-fit and analytic-fit tests, deliberately
  excluded to keep this review free of new fitting. They are not skips and
  this is not a claim to have rerun the complete 25-test suite.
- Independent synthetic checks: 128 piecewise-logistic integral checks
  against a 70-digit analytic antiderivative, partition additivity, both
  directions of the four-ULP anchor rule, chemical-input rejection, invalid
  intervals, serialized-state tampering, 100 independently calculated
  mass-weighted metric/allowance cases, missing-window handling and threshold
  adversaries. All pass. These are synthetic verification, not observations.
- My first antiderivative reference used double precision and suffered
  cancellation near a nearly flat saturated segment. The two failed
  diagnostic logs are retained. Replacing only my independent reference
  arithmetic with 70-digit Decimal resolved that reference defect; all
  differences then fell inside the unchanged candidate's allowances.
  No candidate code, artifact, threshold or numerical rule changed.
- PRED outcome quality is bounded by the inspected, hash-bound source
  qualification evidence. I did not independently reparse its chemistry.
  No experimental PRED performance, fresh-blind validation, independent-source
  validation, measurement uncertainty, whole-cup closure or physical mechanism
  has been established by this review.

The review scripts, aggregate outputs and logs are retained beside this
report. Their exact hashes are recorded in `review.json`. The checkout and
frozen artifacts remained unchanged throughout review.
