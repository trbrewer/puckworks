# Independent read-only review

A fresh reviewer session read the pinned implementation, 002 plan and changes,
without inspecting private shot records, fitting models or scoring targets.
It independently verified the published 001 unflagged C0 reference values.

Before freezing, the reviewer checked whole-object exclusion, unchanged surviving
fold IDs, source/cache identities, isolated output paths, model skip contracts,
C0 reproduction code, all eight declared contrasts and reporting definitions.
It identified a stale-prediction-cache gap; this was fixed by binding caches to
task/cohort/windows/plan/evaluator/all CV model hashes and checking those identities
at report/comparison. Audit receipts also require the complete current inventory.
The combined focused suite passed **55 tests** independently.

Pre-fit code review cleared, conditional on a committed freeze and successful
actual C0 reproduction. Scientific evaluator/helpers and the entire 001 bundle
have no diff from pinned `65f51c63856677eccc4ba5a45ce555ea0c4eab99`.
Resume contracts additionally bind the exact runtime; malformed model artifacts
are preserved privately and refitted rather than accepted as resumable.

Actual C0/numerical receipts and final result claims are reviewed below.

The actual C0 continuity review passed: committed receipt RMSE
1.2084042519074556, NRMSE 1.6547408859936399 and zero per-window difference from
001's cached C0 match the frozen plan/cohort. The reviewer also checked the final
runtime/malformed-cache resume addition; all 14 then-affected tests passed.
No private records or targets were opened by the reviewer. The numerical audit
and final-claim review is recorded below.

The reporting/path review passed all **57 focused tests**, including independent
synthetic matched-shot lookup and equal-user averaging, 35/7 fit accounting,
48-model inventory and 90 parameter-bound entries. The relative-output repair
changes path resolution only. The reviewer also checked all eight per-fold
contrasts: released prediction fold scores only, first minus second, both metrics
and both subsets. The completed exported-value and claim review follows.

## Final independent review — cleared

No remaining concrete defect was found. The same independently initialized,
read-only reviewer ran all **57 focused/release tests** and checked the pinned
scientific helpers and complete 001 bundle remain unchanged. It verified the
freeze and model-before-score commit identities, C0 receipt and final C0 scores,
all 48 public model/audit identities and every scored aggregate hash.

Independent arithmetic checks covered 384 score rows (maximum fold/user aggregate
difference 4.44e-16), 32 aggregate contrasts and 160 fold contrasts (maximum mean
difference 8.33e-16), 192 matched-survivor rows, 90 parameter-bound rows, 12 nested
training-objective comparisons, an independent n=1 peak formula and the
35.499337337806104 core-hour total. All new matched scores equal SCORES.csv; all
overall original scores match the published 001 unflagged breakdown.

The M0R recommendation, pressure-varying fold reversal, AR uncertainty, recovery
sensitivity, residual flags and post-hoc/conditional-input limitations agree with
the artifacts. The reviewer inspected all three rendered public figures, including
suppression gaps, isolated markers, normalized capacity curves and the 002-only
tick-label repair. No private raw records were inspected, models refitted or
targets rescored. Bootstrap interval implementation and provenance were reviewed;
intervals were not independently recalculated from private predictions.

Separate execution checks: the full local offline suite passed **8,120 tests**,
with 33 skipped and 97 deselected; Ruff and diff checks passed. Registry gates
returned **66 PASS and one existing ACKNOWLEDGED_EXCEPTION**. All nine hosted CI
workflows passed on the earlier `bc1513c` PR head. Final-head CI status is reported
in the draft PR's checks and final completion report; this document does not
anticipate that result.
