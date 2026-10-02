# Handoff — MODEL-GRUDEVA2026-REDUCED-001

One Puckworks branch `model/grudeva2026-reduced-001`, based on
`ca663733c0cd1d171899e137a7256ab29e857f35`; one draft PR referencing #67.
No merge, auto-merge, release/default change, EWP write/run or successor is authorized.

Result: GRUDEVA2026_STANDALONE_NUMERICALLY_VERIFIED_REFERENCE_INCOMPLETE.
Figures 3/4 reproduction fails at unchanged parameters/budgets;
FIG5_REFERENCE_INCOMPLETE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
The source contract, frozen budgets and numerical development record are in
CONTRACT.md; exact numerical metrics/hashes and commands are in RESULTS.md/json.

QA is reported separately from numerical qualification. A clean baseline rerun
passed 5501 tests, skipped 33, deselected 69; registry gates had 65 passes and one
acknowledged exception. An earlier interrupted baseline attempt had documentation
drift and is not claimed as the clean baseline. No red baseline was concealed.

Exact review identity is recorded in the draft PR's independent review receipt
and final delivery, after the final candidate commit exists. This avoids embedding
a circular self-commit hash in a committed artifact. Scientific reuse is bound to
the exact source and input hashes in RESULTS.json; no earlier result bundle was
regenerated or restamped to qualify this task.

## Executed local checks

- Clean baseline: 5501 passed / 33 skipped / 69 deselected; registry 65 PASS,
  one acknowledged exception. Candidate scientific-baseline suite: 5 passed,
  including the unchanged 27-component tour structure after removing the new row,
  Cameron output and full-tour import-order invariance.
- All six final qualification cases rerun after the bounds diagnostic included both
  interior and reconstructed front states. Original numerical metrics unchanged.
- Candidate package built as wheel and sdist; package inventory guard passed;
  clean installed-wheel registry gates, native PUBLIC_ARTIFACT service, rights,
  finite serialization and canonical rendered card link passed; sdist wheel rebuild passed.
- Ruff, mypy (19 configured core modules), registry/generated metadata,
  Paper 3 build/availability/corpus/evidence strict-all reconciliation, Insight
  Foundry and status-source verification passed.
- Changed Python AST/JSON parsing, added-content secret/local-path scan,
  protected-source boundary and whitespace checks passed. No shell source changed.
  Existing Grudeva/Cameron implementations and historical scientific bundles unchanged.
- One interrupted candidate quick run exposed integration metadata expectations;
  those were corrected and targeted tests rerun. The historical I-045 receipt was
  preserved: its global manifest count is now checked at the task baseline,
  with all scoped scientific fields still checked against live state. No receipt
  was regenerated. New runtime-neighbour identities reserve the previous IDs.
- EWP remains clean. Preserved tag v0.1.4-public.1 points to
  26359865621510510e381bc69bb280d2d8dae412. Dependency-lock SHA256 remains
  52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10.

The complete candidate quick suite, hosted checks and independent exact-head review
are reported in the draft PR's final QA/review receipt. At this artifact's preparation
those checks are pending; this file does not claim an unexecuted hosted pass.
Required hosted contexts are read from the active repository ruleset:
`quick (3.10)`, `quick (3.12)`, `verify-generated`, `paper3-scope-strict`,
`all-scope-strict`. Auto-merge must remain disabled.

Current metadata-only generators were updated for the added registry component and
fixtures. The new numerical component creates no experimental campaign or measurement
agenda entry. No shared-scenario adapter or cross-model overlay is enabled.
