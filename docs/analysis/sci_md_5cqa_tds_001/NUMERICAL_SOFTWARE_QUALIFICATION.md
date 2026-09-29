# Numerical and software qualification

SCI-MD-5CQA-TDS-001 / G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY.
SOURCE_INTERNAL / TARGET_EXPOSED /
RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION /
PHYSICAL_VALIDATION_NOT_ESTABLISHED. This is numerical/software qualification,
not physical validation or assay uncertainty.

The numerical operator splits at the parent's five uniform knots and integrates
C2 concentration times the pointwise composition share with 64-point and
128-point Gauss-Legendre quadrature. Independent adaptive quadrature supplies a
second reference. Reported allowances conservatively include discrepancies,
adaptive error estimates, floating-point allowance and the inherited narrow
fraction-3 anchor reconciliation. Maximum total allowance across the 475
supported predictions is 2.039306307053582e-16 kg, below the 1e-9 kg ceiling.
All five copies of the unsupported flow slot remain explicit among 480 records.
No broad mass tolerance, observation clipping or missing-prefix reconstruction.

Focused tests cover analytic constant products; bounded S0 WLS including zero
and upper-bound solutions; S2-to-S1 and constant-logit-to-S0 reductions;
distinguishable synthetic TDS-head dependence at fixed masses without claiming
unique coefficient recovery; knot integration, additivity and product versus
separate means; parent upper bounds; strict species/units/hash/input rejection;
immutable states; no inference optimizer/source-workbook/fallback; retained
parent leakage and matrix rejection; PRED chemistry/metadata poisoning;
source denominators and spill independence; approval, failed-attempt and replay
guards; adequate versus earned complexity; numerical threshold overlaps; and
unchanged frozen predecessor artifacts. The synthetic example is not a physical
shot. Test execution does not add real experiment starts or outcome joins.

The authorized real FIT run used exactly 366 iterative starts (183 each S1/S2)
and 16 analytical S0 fits. All converged; no failed, cancelled, incomplete or
boundary starts. Parent/E0/D0 fit count is zero. Actual residual calls total
50,186, including 47,800 numerical-Jacobian calls; the maximum per start is 235.
Fitting-stage span is 19.458406925201416 seconds; peak fitting-process RSS is
85,724 KiB. One worker and one BLAS thread; 12-GiB process cap and 5-GiB private
evidence ceiling. Detailed starts and logs remain private and cumulatively bound
by the exact freeze. No budget reset or second run directory.

The pre-edit baseline at reviewed main passed 4,976 tests with 65 existing skips,
60 deselections and two warnings. Historical-baseline checks passed five tests
with seven existing skips. Registry: 65 PASS and one ACKNOWLEDGED_EXCEPTION.
No baseline repair was needed. Baseline logs and check identities are in
[BASELINE.json](BASELINE.json).

Post-implementation acceptance: **5,022 passed, 65 skipped, 60 deselected**
with one existing DEV-salt warning. Focused task tests: **46 passed**; affected
predecessor/task tests: **166 passed**. Historical lane: **5 passed, 7 skipped**.
Registry: **65 PASS, 1 ACKNOWLEDGED_EXCEPTION**. Repository and three-module
lint/type checks, generated-state, data-guide and README-governance checks pass.
The exact command/log identities are in
[QA.json](QA.json). Generated-state checks are verification only; no generated
state, registry/default, solver or dependency lock was edited. There is no
native CFD qualification because no solver changed. Source, static/Python,
JSON, scope-boundary, shell-example syntax and secret/local-path checks pass.
All 2,325 pre-existing nonplanning files remain byte-identical to reviewed main;
only ROADMAP, SPRINTS and task-ledger have authorized planning updates. EWP's
head/tree, clean status and archival tag remain unchanged. Its provenance and
locked external dependency were not modified.

Hosted CI is separate acceptance evidence and must be read at the publication
head; a pending, skipped, cancelled or unavailable check is not PASS. See HANDOFF.
