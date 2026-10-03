# MODEL-FOSTER2025-POSTSAT-001 owner handoff

G2 / GOVERNING_PHYSICS_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Issue [#311](https://github.com/trbrewer/puckworks/issues/311). Draft PR only;
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

Actual task use: **12/12 trajectory executions**, **56.082319/600 numerical
seconds** including report reduction and its failed attempt. Four final-source
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

- Focused current-dependency QA: 130 tests pass (including live consumers and
  historical I-045/I-090 scope). The frozen historical receipts are not rewritten.
- Initial broad baseline QA: 5475 passed, 65 skipped, one failure in I-040's
  dynamic Waszkiewicz trace. An isolated pristine-baseline audit passes; full
  pristine-baseline and final-source regression are being compared. No unrelated
  code is repaired by this task.
- Minimum dependency QA: 128 focused tests passed on NumPy 2.0 / SciPy 1.13;
  two subsequent interface assertions are rerun in the same environment.
- Ruff and mypy pass. Scientific-baseline QA: 5 passed / 7 skipped. All registry
  gates pass. Generated registry, insights, evidence-graph and status checks pass.
- Packaging/rights/path and full final broad QA: pending; full logs remain external.
- Hosted CI: pending draft PR.
- Independent exact-head review: pending; requested review is nonhuman and must
  bind the final commit, numerical evidence and actual resource log. Review and
  CI receipts will be linked from the PR at the reviewed head.

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
