# Task QA and review

Scientific: TWO_ASSAY_MASS_INADEQUATE_ON_DECLARED_OBSERVED_WINDOWS. Numerical: QUALIFIED on all 161 declared windows per arm. Software checks and independent/hosted statuses are distinct from that scientific failure.

The independently authored PRE_SCORE_REVIEW.json approved the exact freeze before the sole score. Substantive final result review and hosted CI use separate exact-candidate receipts linked on the two task PRs. The final review records both candidate/base identities; it does not authorize merging. This document records local evidence and does not substitute for live hosted status.

Focused producer tests: 54 pass. Historical numerical/model/operator checks: 132 pass. Source preflight valid; Ruff passes; registry gates pass (65 plus one acknowledged historical exception). Scientific-baseline integrity: 5 pass, 7 skipped, 4863 deselected. The complete offline quick-suite log is retained privately; its completed result and hash are recorded with the exact-candidate PR closeout.

EWP consumer parity with exact detached runtime: 7 pass. Source manifest and corrected static check pass. Full Python suite: 1619 tests, 9 skipped, PASS. Historical baseline, governing-physics declaration, task change contract, release finalization, WP03/B/C, rheology 005/006 and pressure-boundary checks all PASS. No native solver execution is included.

Preserved bounded nonsemantic defects: the first offline quick run missed PYTHONPATH for a subprocess in the isolated worktree (one generated-readme import failure); the affected test passed with PYTHONPATH=. and a correctly configured complete quick run follows. An earlier resource-heavy baseline attempt was interrupted before the single-thread run. EWP initially lacked the CLI executable mode; c0c6ea1 fixes that mode and regenerates manifest/package QA only. Corrected static validation passes. Initial failure logs remain private. Consumer text and all scientific artifacts/predictions are unchanged; the independent reviewer verified the bounded correction before approval.

JSON, shell syntax, production/history boundary, secret and local-path checks pass for the implementation. Publication deltas receive focused consumer/programme, source/static, JSON and boundary checks; outcomes are recorded in exact-candidate PR closeout. Full logs and source-derived row artifacts remain outside public Git.
