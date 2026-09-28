# SCI-MD-TRIGONELLINE-DELIVERY-001 implementation plan

G1; RESEARCH_ONLY; NO_GOVERNING_PHYSICS_CHANGE. Owner authorization is the
bounded task brief. The preflight in BASELINE.json and
DATA_AVAILABILITY_PREFLIGHT.json passed before this plan was committed.

The decision is whether a fixed mass-only trigonelline predictor or a constant
concentration adequately predicts the declared later assayed fractions. A
complete numerical rejection of both arms is task SUCCESS. There is no
mechanism, equilibrium, kinetic, inventory, pressure, production, or successor
decision. The three-test selection gate and historical ledger are retained in
SELECTION.json; EVU at selection is 0.960.

## Files and commits

1. Commit this plan, PROTOCOL.md, MODEL_CARD.md, SOURCE_IDENTITIES.json,
   DEPENDENCIES.json, BASELINE.json, DATA_AVAILABILITY_PREFLIGHT.json,
   SELECTION.json, and README.md before implementation or fitting.
2. A: add `puckworks/analysis/pannusch_conditional_trigonelline_delivery.py`
   with the independently qualified trigonelline projection and private,
   separate training / coordinate-only query artifacts; add
   `tests/test_pannusch_conditional_trigonelline_delivery.py`. Record the
   committed protocol identity in INFORMATION_CONTRACT.json. Check and commit.
3. B: add `puckworks/analysis/conditional_trigonelline_delivery.py` and
   `puckworks/analysis/conditional_trigonelline_training.py`, with
   `tests/test_conditional_trigonelline_delivery.py` and
   `tests/test_conditional_trigonelline_training.py`. Complete the task CLI,
   one-score guard, bounded scoring and read-only verification/reporting in the
   pipeline module. Pass the synthetic/analytic tests before any real fit.
   Check and commit.
4. C: prepare once; run the fixed 15-design development; select lambda; fit
   TR-D0 once with its three declared starts and TR-K0 analytically. Retain
   every attempt privately. Publish aggregate DEVELOPMENT.json, EXECUTION.json
   and the two source-derived `models/TR-*.json` files with their rights.
   Check numerical qualification, hash the artifacts, and commit.
5. D: generate all 192 arm/slot predictions without outcome attachment. Freeze
   the exact producer head/tree, protocol, runtime, dependencies, models,
   preprocessing, source identities, support and predictions. Obtain a fresh
   independent review of that exact freeze. The implementer cannot approve it.
   Without approval stop at READY_FOR_INDEPENDENT_REVIEW. Publish only the
   sanitized freeze/review bindings and commit.
6. E: after genuine approval, perform exactly one outcome join and score.
   Retain results and numerical bounds, all arms, shots, conditions and panels.
   Publish aggregate RESULTS.json, RESULT.md and receipt/result bindings;
   keep rows outside Git. Check and commit. No post-score scientific repair.
7. F: reproduce inference and reporting from read-only frozen evidence in a
   clean exact checkout; run final regression/current applicable CI checks;
   add QUALIFICATION.md/JSON and reproducible COMMANDS.md, one CHANGELOG.md
   line and one `docs/task-ledger.md` row. Commit and prepare one draft PR.

Expected diff: three isolated research modules, three new test files, this
task's documentation/aggregate artifacts, one changelog line, and a new ledger
containing only the required header and this task's row. No existing scientific
code, model, observation, interface, test, workflow, source register or EWP
tracked file changes. No merge.

## Dependencies and bookkeeping

Reuse accepted numerical geometry/strict JSON helpers, source resolver and
measured mass coordinate reconstruction, and exclusive receipt conventions.
Adapt the accepted D0 training architecture with task-local species types,
residual scale and budgets. No retained caffeine coefficient, TDS parent,
historical fit, or additional model family enters this task. DEPENDENCIES.json
pins the inspected accepted code; original hashes are in SOURCE_IDENTITIES.json.

Mandatory new bookkeeping is the committed information contract; private
exclusive start/end and one-score receipts; public sanitized source, freeze,
review, execution and result bindings; one changelog line and one ledger row.
The ledger is absent at the verified main tree; no historical rows are invented.
Existing generated status/registry/paper artifacts are verified, not changed:
this task registers no component and changes none of their source authorities.
Any demonstrated mandatory generated drift is reported before expanding this
file list. No new assurance framework.

## Runtime and checks

One session, six hours from 2026-09-27 23:29:20 UTC, ending no later than
2026-09-28 05:29:20 UTC. Real fitting has one cumulative 60-minute budget,
one worker, one BLAS thread, at most 183 iterative starts, 8,000 actual
residual calls per start including numerical Jacobian calls, 12 GiB process
memory and 5 GiB new private evidence. Counters cannot reset on restart.

Use the existing recorded environments, without dependency upgrades. Baseline
Puckworks: 5033 passed, 34 skipped, 0 xfailed; EWP: 1635 tests, 20 skips,
no failures/errors/expected failures. Complete skip reasons and environment
identities are retained. Reuse unchanged evidence by exact hashes under the
minimum-necessary-governance standard; run affected checks before each commit.

Focused tests include all ten owner-named tests, analytic integration and
partition checks, strict species/units/schema rejection, fold exclusion,
original denominator retention, conservative allowance propagation, inference
without the optimizer, and the one-score guard. Final checks are the exact
full Python suites, registry gates, diff checks, current applicable CI commands,
protected-file equality and a clean-checkout saved-model replay. Source,
static, historical release, change-declaration, JSON, boundary and path/secret
checks are retained; EWP native run count stays zero.

Any kill criterion stops the scientific workflow. Missing source, failed
baseline, numerical/budget failure, duplicate/authority conflict, or missing
independent approval cannot be repaired by changing the experiment.
