# VAL-INFRA-DECISION-RESOLUTION-001 handoff

Implementation is opt-in; policy is proposed pending normal owner acceptance
and merge. This G1 prospective scientific-policy extension has ordinary
engineering implementation controls. `NO_GOVERNING_PHYSICS_CHANGE`;
`SYNTHETIC_VERIFICATION_ONLY`. It is informed by disclosed retrospective T02
evidence, not target-blind calibration or independent empirical validation.

- `SCIENTIFIC_RESULT_DISPOSITION`: no empirical adjudication performed; synthetic
  examples demonstrate declared value/contract/evidence distinctions only.
- `VALIDATION_FRAMEWORK_DISPOSITION`: implemented; QA, independent nonhuman review
  and candidate-specific CI are recorded separately below and in the draft PR.
- `CLAIM_CEILING`: no total-uncertainty, statistical-inference, equivalence,
  certificate-authentication, historical-rescoring or adoption capability.

`PHYSICAL_VALIDATION=NOT_ESTABLISHED`; `MERGE_AUTHORIZED=false`;
`PRODUCTION_ADOPTION_AUTHORIZED=false`; `NATIVE_EWP_RUNS=0`;
`NO_AUTOMATIC_SUCCESSOR`.

## Identity and implementation boundary

Fresh remote main and actual #334 merge:
`7975fbc39a649cb757702131e2b91b13439c7192`, tree
`b0f27837d8fc0706c328feeafb1cccc62c22b360`.
Isolated branch: `val-infra/decision-resolution-001` from that main.
EWP read-only reference: `4284e9460c8057053e95de7cfa2fb3590e68e9db`, tree
`d9d9faaa56f22ab0bd7f47c43174024d15ada192`.
Final head/tree and PR-test-merge identities belong in the candidate-bound PR
receipt, avoiding a self-referential committed hash. PR remains draft, unmerged,
auto-merge disabled. No EWP changes or companion PR are needed: this supplement
links the exact existing EWP standard and review checklist.

Changed files:

- `docs/governance/DECISION_RESOLUTION_POLICY.md`: sole canonical supplement.
- `puckworks/validation/decision_resolution.py`: immutable compact declarations,
  pure value relations, explicit contract/evidence evaluation, exact counts,
  controlling conjunction and deterministic serialization.
- `tests/test_decision_resolution.py`: first-party synthetic verification.
- `examples/decision_resolution.py`: runnable deterministic SYNTHETIC report.
- This handoff; minimal links in `docs/CURRENT.md` and the current SCI-GOV-001.

No production gate wiring, public exports/schema/vocabulary changes, dependency
or lock changes, source resolver, fitting/scoring/solver calls or new service.
The existing package initializer still registers built-in components when
Puckworks is imported; the helper adds only standard-library imports and no
source/producer execution. Example imports generate no output; its CLI writes
only stdout or the explicitly requested new output file.

## Verification commands and readable synthetic output

Use an existing environment with the repository's dev dependencies, Python
3.10–3.13; this task used Python 3.12.3 with existing NumPy 2.5.3/SciPy 1.18.1.
No dependency installation or upgrade was necessary. From the checkout:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=.
python -m pytest -q tests/test_decision_resolution.py
python -B -m examples.decision_resolution --output /tmp/decision-resolution-synthetic.json
python -m pytest -q tests/test_gate_runner.py tests/test_public_api.py \
  tests/test_grudeva_one_shot_calibration.py tests/test_grudeva_pooled_tail_delivery.py \
  tests/test_pannusch_conditional_tail_delivery.py \
  -m 'not slow and not live and not gpu and not external_data'
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -m ruff check puckworks/ tests/ examples/decision_resolution.py
python -m mypy
python -m mypy puckworks/validation/decision_resolution.py examples/decision_resolution.py
python -m puckworks.statusdoc --verify
python -m tools.readme_governance verify
python -m puckworks.paper3.registry_artifacts --verify
python -m puckworks.paper3.build verify
git diff --check
```

The output includes each requirement, threshold purpose/basis/approval, scope,
units, point/range, evidence basis and assumptions, unknown components, quality,
count members, completeness, both verdicts and exact failed controlling IDs.
The following compact matrix matches the observed final demonstration and the
independently specified test expectations; all rows pass their assertions
(`C` contractual; `R` bound-resolution; U unresolved; NA unavailable):

| Synthetic case | Input/expected relation | Expected = observed C / R | Claim/completeness limit |
|---|---|---|---|
| A/B/C upper | <=5; [3,5] / [6,8] / [4,6] | PASS/PASS; FAIL/FAIL; U/U | Declared synthetic bound only |
| A/B/C lower | >=5; [6,8] / [2,4] / [4,6] | PASS/PASS; FAIL/FAIL; U/U | Same scope restriction |
| D equality | [5,5] | <=,>= PASS/PASS; <,> FAIL/FAIL | No epsilon or rounding |
| E same endpoints | >=0.10; [1.97,2.03] | bound PASS/PASS; sensitivity PASS/U | Labels cannot upgrade evidence |
| F precision/stability | allowance .03 <= .02; contrast 2.0, [1.97,2.03] >= .10 | FAIL/U | `precision` fails; sensitivity stability only |
| G precision/overlap | same precision failure; [.07,.13] >= .10 | FAIL/U | Precision failure and boundary crossing |
| H adequacy/increment | [3.9,4.1] <=5; [.20,.30] >=.50 | overall FAIL/FAIL | `increment` fails; adequacy PASS retained |
| I controlling count | N8 k6; D/P 5/5, 5/7, 6/8 | FAIL/FAIL; U/U; PASS/PASS | Missing members included in P |
| I complete-support | 6/8 count, two missing; separate coverage | FAIL/FAIL | `coverage` fails; incomplete assessment |
| I diagnostic count | favorable metric; noncontrolling 5/5 count | PASS/PASS | Diagnostic count does not add a gate |
| J disagreement | point11 <=10; [9,12] overlaps | FAIL/U | Contract failure preserved |
| J point-only | point9 <=10; measurement uncertainty unknown | PASS/U | No invented interval |
| K full witness | q=(12+x)/2, x in [0,2]; <=5 | FAIL/FAIL | Full denominator; observation/assessment incomplete |
| K subset/mismatch | incompatible subset, units or scope | NA/NA | Diagnostic arithmetic only |
| L failed identity/payload | large apparent favorable margin | NA/NA | Reliance blocked; no stable-effect claim |

None of the illustrative numerical requirements has approved espresso practical
justification. Contractual and synthetic bound relations do not confer it.

## Reused conventions and preserved boundaries

Inspected MASS-006's accepted `conditional_tail_scoring.upper/conjunction` and
material-gain helpers, MASS-007's `leq/conjunction`, support/full-scope failure
bounds, and MASS-008's `leq/combine/at_least` and explicit adequacy/increment sets.
The local scalar functions preserve these comparison/count/conjunction semantics
without importing scorer pipelines that depend on source adapters and fitting.
No historical scorer was refactored or run on historical evidence.
GateResult's retained reporting/identity convention is reused; public GateStatus,
GateResult schema and `GateSuiteResult.passed` semantics are unchanged. A software
PASS/SKIP/no-error summary is not scientific resolution.

Historical results, protocols, thresholds, receipts, models and dated October 9
review are unchanged. No private corpus was inspected; data-guide/catalog and
accepted public aggregate context were read only. Synthetic fixtures have explicit
SYNTHETIC physical-unit identities. EWP stays unchanged. No frozen Paper A/Insight
Foundry extensions, active-queue cleanup, #321/#333 merge, #67 closure, stopped
campaign restart, protected scoring, native run, release or successor occurred.

## Baseline, QA and review evidence

Fresh remote/recent/open-PR searches by ID and purpose, local branch/history
searches and inspection of 87 accessible checkout roots found no completed or
active equivalent. #321 and #333 remain unrelated open work.

#334 actual merge is the base above; its PR head was
`a950c5bb70659361a78e00469d30db88997b9fab`, PR base
`3cd308ac5bed39acff3d995108b5178a53c982ee`. The quick job checkout log independently
identifies PR-test-merge `0c16c06e7fd897c14fd362085d24c8fccf119095`, distinct from
both the PR head and actual-main merge. PR-head/check receipts do not substitute
for actual-main push evidence.
[Actual-main quick run 38566098387](https://github.com/trbrewer/puckworks/actions/runs/38566098387)
attempt 1: four Python quick jobs, quality and quality-mypy succeeded;
min-deps job 115859044400 was **cancelled**, not PASS. Its annotation says
“The job has exceeded the maximum execution time of 30m0s”; the retained log
reached 99% without an assertion failure shown. Classified as
`CI_INFRASTRUCTURE_INCOMPLETE`, not invalid historical science. One same-head
failed-job rerun under SCI-GOV-001 §8 succeeded: attempt 2 min-deps job
115906883628 completed with **6,447 passed, 67 skipped, 63 deselected** in
1,614.49 seconds. The run is now successful, reusing its unaffected successful
jobs. Attempt 1 remains a cancellation, not a retroactive PASS. Other actual-main
push workflows also succeeded: scientific-baseline 38566098824, packaging
38566098325, experience 38566098440, paper3-evidence 38566098359,
generated-artifacts 38566098375 and notebook-smoke 38566098337.
No selectors, timeouts, tests, coverage or protection were weakened.

Untouched-base local decision/count/gate regressions: **59 passed, 1 deselected**
(normal offline selector). Initial new-test attempt stopped at collection because
`request` is a reserved pytest parameter name; after correction, 108 passed and
one assertion expected ValueError instead of the actual correct TypeError for a
Boolean threshold. After correcting that test, **109 passed**. Static checks also
identified unused imports and example annotations, corrected in the same lane.
These are test/static development corrections, not scientific or infrastructure
failures. External task-local logs preserve the attempts.

Independent nonhuman review initially requested three corrections: bound-count
contracts must check requested uncertainty components before deciding; count
member entries must be immutable; mixed Decimal/float comparisons must not depend
on or change ambient Decimal context. Its bounded correction review also confirmed
that count/coverage roles must reject scalar bases bypassing member accounting.
All four corrections are tested. Final independent review **PASS**: 117 focused
tests plus 676 independently constructed numeric/context cross-checks passed;
no material findings remain in the reviewed scope. This is not human acceptance.
The preserved initial review and addendum are bound by content hashes in the PR.

Final affected new/existing decision/count/gate/API/status/data-guide checks:
**191 passed, 1 deselected**, including **117 new tests**. Full repository Ruff,
maintained 19-file mypy, additional helper/example mypy, status/README governance,
Paper 3 generated/build checks, local document links and whitespace checks pass.
The final example emits 27 deterministic synthetic cases. The initial full
offline suite passed: **6,644 passed, 33 skipped, 72 deselected**, 10 warnings,
1,398.02 seconds (23:18). It collected the initial implementation before the
bounded review corrections; its unaffected evidence is reused, with all affected
tests rerun on the corrected content as above. The final candidate's hosted suite
provides a separate complete run. Warnings are retained (existing SciPy,
Matplotlib and development-salt warnings); no warning/test was suppressed.
No author self-review is called independent review. Candidate CI and exact
head/base/test-merge identities are recorded in the draft PR's final receipt.
The first commit command stopped because the isolated clone lacked a Git author
identity; the retry reused the existing repository's configured identity for the
command only, without a global configuration change. No test or science failed.
