# MODEL-PANNUSCH2024-POSITIVE-FV-002 handoff

G2 / NUMERICAL_METHOD_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
The additive research API is `simulate_temperature_history_fv` in
`puckworks/models/pannusch2024/temperature_history_fv.py`; the offline example is
`examples/pannusch_temperature_history_fv.py`.

This work is stacked on **unmerged draft #314**, exact parent
`c7310ea1ac6c41ec2cb8f918584ab41cb485fa60`, targeting
`model/pannusch2024-temp-history-001`. Parent numerical producer
`a8c94caf35bff300519af9bcffb7d4771c5e9553` and its INCOMPLETE disposition remain
unchanged. The new PR contains only 002's delta. Main remains
`95f6b54f1f00fda100fad9c994ac99037e50f801`; EWP's remote main remains
`73ec476ffe6ac626705ca949e28b32935ddf2992`. Final exact head, PR URL, hosted checks
and independent nonhuman exact-head review are recorded on the new draft PR,
avoiding a self-referential commit stamp here. Neither PR is merged; auto-merge
is disabled. No production adoption, parent closure or successor is authorized.

## Numerical representation and scope

The backend evolves cell phase masses and outlet mass with paired upwind face
fluxes and phase exchanges. Every transition subtracts a nonnegative rate from
one donor diagonal and adds it to one receiver off-diagonal. Columns sum to
zero, including the outlet accumulator; the generator is Metzler. Exact
exponentials consequently preserve nonnegativity and total mass. These are
exact-arithmetic properties, not a floating-point certificate or an accuracy
claim. The fixed midpoint method approximates the nonautonomous coefficients.

Fields are **CELL AVERAGES** on liquid/fine/coarse source concentration bases,
in kg/m^3; Mout is kg, Vout is m^3, and fraction concentrations are kg/m^3 of
collected liquid. The first liquid cell starts at its full equilibrium average;
zero inlet concentration sets incoming flux, not first-cell storage. Coarse
capacity includes phi_v2; fine capacity does not. Initial FV inventory equals
the continuum inventory to rounding. There is no nodal endpoint offset or
orphan inlet-grain sink. These differences do not alter the continuum problem.

History, model origin, observers and settings are immutable and explicitly
validated. Primary partitions are independent of observation requests. Interior
observations use the same frozen generator and saved step-start state. Knot
states carry exactly; temperature metadata can jump. Completed integration,
sampled numerical admissibility, per-call accuracy, campaign qualification and
physical validation are separate fields. Failure retains only a checked finite
prefix; unsupported quantities are absent/null with reasons. Failed
admissibility suppresses public fraction concentrations while retaining raw
finite diagnostics. Per-call accuracy remains NOT_ASSESSED.

The unchanged closures use actual prescribed temperature at each midpoint and
superficial q=Q/A, with grind-derived d32. Source fits, geometry, one-time
initial equilibration and the two old APIs are unchanged. Q is fixed SI volume
flow, never converted through temperature-dependent density. The admitted
80–98 C and 1e-6–3e-6 m^3/s envelope is a caller-prescribed numerical domain;
EWP #132/#134's experimental flow restrictions are unresolved. No solved thermal
field, empirical ramp authority, MATLAB equivalence, recovered inventory,
physical extraction yield, TDS percent or taste interpretation is established.

## Reproduce and reduce

Use supported repository dependencies, without a dependency upgrade. From a
fresh clone/checkout containing this stacked branch, choose an external evidence
directory. Within one Git common directory the task authority binds the first
evidence directory and persists attempts: changing output directories cannot
reset its budget. Execute resumes only unattempted cases; four slots remain
reserved for demonstrated corrections, never tuning after outcomes.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python -m tools.pannusch_positive_fv_verification execute \
  --evidence-dir "$EVIDENCE_DIR"

# Saved arrays only; this never launches candidate/reference trajectories.
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
python -m tools.pannusch_positive_fv_verification report \
  --evidence-dir "$EVIDENCE_DIR" --output-dir "$REPORT_DIR"

# Optional retained nodal comparison: add --parent-evidence-dir "$PARENT_EVIDENCE_DIR"
# to report. Missing parent arrays do not trigger a historical rerun.
python -m pytest -q tests/test_pannusch_temperature_history_fv.py \
  tests/test_pannusch_positive_fv_verification.py \
  -m 'not protected_target_integrity'
python examples/pannusch_temperature_history_fv.py
```

The fixed CASES and CONTRACT were committed before qualification. Source hashes
are in SOURCE_IDENTITIES; RESULTS contains every frozen case/channel, signed
inventory diagnostics and numerical counters. Arrays, full logs and private
resource authority stay outside Git. Both execute and report charge numerical
wall time, including failures and reductions. Report mode validates saved
receipt/array/source identities before computing metrics. No second campaign
is part of closeout.

## Source treatment and preservation

Canonical source identities are `pannusch2024/table2_params`,
`pannusch2024/experimental_kinetics`, and literal manifest ID
`pannusch2024 (Mendeley repo)`. Only equations/parameters are scientific inputs.
002 reuses 001's hash-bound receipts for original MATLAB text inspection;
002 does not claim new original/native inspection or execution. No observation
rows, originals, private arrays or logs are redistributed. Pannusch et al.,
DOI 10.1016/j.jfoodeng.2023.111887 and author code/data
DOI 10.17632/y2tz67f6ry.1 retain CC-BY-NC-3.0 source-derived treatment, separately
from first-party software licensing. Existing targets remain source-internal,
target-exposed; no independent holdout is created.

SOURCE_IDENTITIES binds unchanged parent modules/tests/evidence, parameters,
other model code, registry, frozen I-010/I-076 and dependency metadata. Only
current scope/planning notes and their existing generated views change outside
the additive implementation. No registry component or validation badge is added.
EWP is read-only throughout. Parent software receipts and the disclosed local
protected-integrity selection deviation are retained unchanged. All 002 local
pytest selections explicitly exclude protected_target_integrity; required hosted
integrity QA remains separate from scientific work and cannot supply target-derived
values to this numerical qualification.

## Dispositions and resources

**Declared-case numerical capability qualification: VERIFIED.** Mathematical
structure, sampled positivity, independent conservation/quadrature, default
temporal accuracy, spatial accuracy, manufactured consistency and retained
observers/determinism pass. Maximum gated temporal error is 2.172e-8 (allowance
1e-6); maximum candidate inventory residual is 1.061e-13 M* (allowance 1e-8).
Finest source-grid weighted-field difference is 1.689e-3 M* (allowance .005).
Every individual channel and diagnostic remains in RESULTS.json. These results
do not extend 001's qualification or establish empirical accuracy.

Resources: 28/32 full trajectories; 48 segments;
30633 primary candidate propagations; 466990 exponential applications;
436357 diagnostic evaluations. All auxiliary partial exponentials and
GL4/GL8 evaluations are charged within executions. Full trajectories consumed
558.508551 s; two saved-array reports and compact summary bring
aggregate numerical wall time to 587.120921/1800 s. Four correction
slots remain unused. No failure/cancellation/full-bed replay occurred. RESOURCES.json
records auxiliary charges; any additional reviewer numerical work must also be
charged before handoff. No second campaign was run during closeout.

## Software and review evidence

The 002 baseline had 78 applicable unprotected predecessor tests passing. New
small-mesh tests cover the independent balances, API/failure behavior and saved
runner evidence; full qualification is not part of routine CI. Core ruff and
mypy plus explicit new-module mypy pass. Package wheel/sdist inventory and
rights checks pass, and an installed-wheel N=8 API/strict-JSON smoke passes.
The package numerical bytes are unchanged from the built producer head. Current
planning/card views were regenerated using existing generators; no historical
science was regenerated. Final focused test/check receipts accompany the PR.

Valid unchanged-base broad QA receipts are inherited by exact preservation: the
parent's clean baseline, scientific-baseline lane (five passed, seven optional
collection skips), package and generated checks remain scoped evidence. Skips
are not PASS. Parent coverage CI timed out and the unchanged-main receipt has
the same timeout; current hosted CI is reported separately, never waived or
misclassified as FV numerical failure. No workflow, threshold or unrelated test
selection changed. Hosted integrity lanes are ordinary software QA only.

An independent nonhuman exact-head review examines this delta and its unmerged
dependency, separately from software QA/CI. Approval and exact reviewed head
belong to the new PR's receipt. Until that receipt exists review is incomplete.
The report-only G0 exception-handling correction leaves all 28 numerical
identities unchanged; REPORTING_CORRECTION records both observed runner-file
hashes. Original numerical arrays and execution identities are preserved.

Final local affected suite: **237 passed** (66 new small-mesh/API/runner checks,
78 applicable unprotected predecessor checks, 93 generated/metadata/packaging
checks). QA.json binds retained logs. Strict JSON, generated-state freshness,
source preservation and whitespace/path checks pass. Initial small-test rounding
assertions and a status-note phrase failure were corrected before qualification;
original QA failure logs remain outside Git. No numerical threshold changed.
