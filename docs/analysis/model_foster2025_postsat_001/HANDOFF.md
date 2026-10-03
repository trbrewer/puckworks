# MODEL-FOSTER2025-POSTSAT-001 owner handoff

G2 / GOVERNING_PHYSICS_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Issue [#311](https://github.com/trbrewer/puckworks/issues/311), draft
[PR #312](https://github.com/trbrewer/puckworks/pull/312). Draft PR only;
no merge/auto-merge, release, public publication, branch deletion, production
adoption, EWP changes, laboratory work or automatic successor is authorized.

## Result and limits

The existing component implements the missing published post-saturation stage,
with H carried from the localized event, s=L and retained p_c. Both frozen
source representations pass reference reconstruction separately. Numerical
verification, conservation, accuracy, independent-method agreement, equilibrium
and compatibility pass; see RESULTS.json for every metric and identity.
This establishes neither independent experimental nor physical validation.
Pump/bed/outlet quantities are hydraulic water, not TDS/EY/solute/beverage mass.

The first report attempt failed on a list/scalar reducer error; trajectories
were retained and reporting was replayed without solving again. Its first
completed diagnostic reported an entry finite-difference derivative error of
4.908335040159066e-6 normalized. That diagnostic remains explicitly
NOT_QUALIFIED_AS_DENSE_OUTPUT_DERIVATIVE. The source contract specifies state
trajectory budgets, not differentiability accuracy of a LSODA dense
interpolant. The correction records the actual RHS passed to the integrator at
entry and compares it independently with Eq. 29 at roundoff. No finite-difference
derivative API is supplied, and the failed estimate is retained in RESULTS.json.
No source-reference threshold, parameter, observer, support or mask changed.

Independent review of `7edb4b40f1fdabb4f58fae095284099dcafadb84` found one
material reporting defect (R1): replay could accept an unsuccessful cached
oracle and extrapolate its partial dense output. All twelve retained executions
were successful; the defect did not invalidate their numerical evidence.
The correction requires a successful END receipt and cached result, and verifies
each independent scalar trajectory's complete support and initial state before
evaluation. Seventeen synthetic tests cover failed/unfinished caches and partial
or mismatched support without running trajectories. Reports were replayed from
the unchanged successful caches; the reporter hash is updated in RESULTS.json.
The initial REQUEST_CHANGES receipt and corrected-head addendum belong to the
same independent nonhuman review and are retained in the PR closeout receipt.

## Reproduction and resource use

Run from a repository checkout containing the pinned baseline history:

```sh
python -m puckworks.analysis.foster2025_postsat \
  --output-dir OUTPUT_DIRECTORY \
  --execution-log EXTERNAL_EXECUTION_LOG \
  --cache-dir EXTERNAL_ARRAY_DIRECTORY
```

A fresh reproduction performs eight trajectory executions. `--reuse-trajectories`
recomputes reports from the same solver-source cache. `--final-source` was used
for this task's last four trajectories: D coarse/fine/finer and F fine. The
independent baseline/scalar/equilibrium/rate checks were reused with exact initial
state matching. All final production trajectories bind solver source
`3964b8c6afd63d953d30360b2768b7bfab0c73e3ed173ff03d08f597604d2e72`.

For report-only replay of this task's mixed-source retained cache, use both flags:

```sh
python -m puckworks.analysis.foster2025_postsat \
  --output-dir OUTPUT_DIRECTORY \
  --execution-log EXTERNAL_EXECUTION_LOG \
  --cache-dir EXTERNAL_ARRAY_DIRECTORY \
  --reuse-trajectories --final-source
```

Actual task use at handoff freeze: **12/12 trajectory executions**,
**73.603635/600 numerical seconds** including report reduction, its failed
attempt, corrected report replay and 0.842758 seconds of independent review.
Four final-source
executions were retained after the observational entry-RHS correction. The
ordinary unit/regression tests are separate QA, not qualification sweeps. No
qualification execution remains available; a numerically material review defect
would require an honest incomplete disposition, not an automatic budget extension.
The final four runs' accepted time/state arrays are exactly identical to their
initial counterparts: the source delta only records the entry RHS. Baseline and
independent trajectories retain their original execution bindings; none is
restamped as a rerun. Exact deterministic report replay also passes.
Raw arrays, pickle caches and complete logs stay outside Git. RESULTS.json is the
deterministic numerical payload; this handoff carries variable execution/QA state.

The baseline and 001/002/003 Grudeva source/evidence, dataset CSVs, infiltration
source, EWP checkout/lock/defaults and v0.1.4-public.1 tag are preserved. Source PDF
was read from the existing external corpus; SHA-256
`ddbf26bc7e302c084ac3e7ce66fc0c7a629e6a942bd6419c106a1dd8d5021ed1`.
DOI: [10.1063/5.0245167](https://doi.org/10.1063/5.0245167). No PDF is redistributed.

## Software, CI and review status

- Focused current-dependency QA: 130 tests pass, plus 17 cache-replay tests
  (including live consumers and
  historical I-045/I-090 scope). The frozen historical receipts are not rewritten.
- Initial broad baseline QA: 5475 passed, 65 skipped, one failure in I-040's
  dynamic Waszkiewicz trace. An isolated pristine-baseline I-040 audit passes.
  The attempted full archive-only baseline run is not an accepted baseline:
  missing Git history caused 67 failures / 3 errors (5348 passed / 123 skipped).
  No unrelated code is repaired by this task.
- Minimum dependency QA: 128 focused tests passed on NumPy 2.0 / SciPy 1.13;
  all 34 final interface tests and 17 replay tests also pass in that environment.
- Ruff and mypy pass. Scientific-baseline QA: 5 passed / 7 skipped. All registry
  gates pass. Generated registry, insights, evidence-graph and status checks pass.
- Packaging/rights/generated checks: 126 tests pass. Wheel/sdist build, installed
  wheel smoke and registry gates pass. JSON finite-value, secret/path and diff
  checks pass; full logs remain external.
- An extra all-module mypy invocation (outside the configured 19-module target)
  reports 140 errors in 32 files, identical by file/message to the pinned baseline.
  This unrelated baseline debt is preserved; configured mypy passes.
- Full broad QA, final hosted CI and the independent review addendum are recorded
  separately in the head-bound closeout receipt on PR #312. They are not inferred
  from the numerical PASS. The first reviewed head had 22 successful hosted jobs,
  six still running and two scheduled-main-only skips at handoff freeze.

## Owner decision

Review the draft and its separate result/QA/CI/review dispositions. This task
selects no successor and grants no merge or production-adoption authority.

## Execution bindings

| Executions | Evidence | Solver source SHA-256 |
|---|---|---|
| 1–8 | pinned baseline, D coarse/fine/finer, F fine, independent post, equilibrium, perturbation | `781ae7f565a3dca55879d8bcd0a0d101421382471b60151e63af485927bc743e` (production source during initial bundle; baseline has its separate pinned source hash in RESULTS.json) |
| 9–12 | final-source D coarse/fine/finer and F fine | `3964b8c6afd63d953d30360b2768b7bfab0c73e3ed173ff03d08f597604d2e72` |

The baseline commit/source and independent initial state are separately checked;
independent scalar equations do not call the production RHS or observers.
