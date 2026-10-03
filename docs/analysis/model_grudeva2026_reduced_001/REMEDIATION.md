# PR #308 — bounded failure-reporting correction

Same MODEL-GRUDEVA2026-REDUCED-001 / G2 lane; this delta is
NO_GOVERNING_PHYSICS_CHANGE. The original numerical-method declaration and
scientific evidence remain historical, unchanged records.

Reviewed starting head: `401ef26fede33b9949562884fe8686b75d6c0548`.
Original base: `ca663733c0cd1d171899e137a7256ab29e857f35`.
The exact new candidate head, executed QA and focused independent delta-review
receipt are recorded on [the same draft PR #308](https://github.com/trbrewer/puckworks/pull/308)
after the commit exists; this avoids a circular self-commit identifier.

## Corrected output contracts

- `puckworks/models/grudeva2026/__main__.py`: any failed numerical run,
  unsupported/error status, quick gate or requested refinement check takes
  precedence over execution mode. The disposition and exit code agree.
  Run status/reasons and failed gate details survive compact reporting;
  empty inventories and unavailable comparison support cannot hide the original
  failure behind an indexing/reduction exception. Every run's quick gate counts.
- `puckworks/models/grudeva2026/quantities.py`: only populated COMPLETED results
  produce dimensional outputs. Other statuses return None for every dimensional
  field with specific reasons, original numerical status/reasons, convergence
  status and PHYSICAL_VALIDATION=NOT_ESTABLISHED. Original Result arrays remain
  available unchanged. Completed right-censored windows and unassessed single-run
  refinement remain eligible; zero discharge and denominator semantics persist.
- A successful single run retains SINGLE_RUN_COMPLETE_REFINEMENT_NOT_ASSESSED.
  Exit zero after successful requested refinement means numerical verification
  only. It does not turn publication FAIL/INCOMPLETE statuses into reproduction.

Immediate consumer inspection found no production caller of dimensional_outputs;
its public export and tests are the current call paths. The CLI consumes the
native reference producer. The Laboratory consumes that producer independently,
retaining scientific_result and reference_qualification; it consumes neither
changed output path. No Laboratory, registry or common-scenario redesign.

## Verification and evidence reuse

Synthetic negative-path tests monkeypatch structurally valid producer summaries
and replace the existing small Result fixture; they are not new solver
observations. The pre-fix run exposes the reported failures. Focused quick tests:
34 passed, three unchanged slow tests deselected. Ruff and configured mypy pass.
Full repository/hosted QA and focused delta review are recorded in the PR receipt
at the new exact head, not preclaimed here.

[REMEDIATION_REUSE.json](REMEDIATION_REUSE.json) binds the original RESULTS.json
and all six scientific_result hashes to the reviewed starting head, separates
the two changed reporting/helper hashes from unchanged calculation dependencies,
and records a reporting-only replay of the archived arrays. It verifies the
case parameters/controls, all prior compact run fields, refinement metrics and
publication comparisons unchanged. Eighteen completed dimensional reports
(six runs, three scaling/denominator configurations) preserve all prior values
exactly. No expensive numerical sweep was repeated or historical file restamped.
The unchanged kernel, solver, verification/budgets, producer, gates, source
fixtures and mathematical contract supply the calculation/input identity proof.

Run affected fast tests with:

```bash
python -m pytest -q tests/test_grudeva2026_cli.py tests/test_grudeva2026.py -m "not slow"
```

Historical disposition remains
GRUDEVA2026_STANDALONE_NUMERICALLY_VERIFIED_REFERENCE_INCOMPLETE.
Figure 3: FAIL; Figure 4: FAIL; Figure 5: FIG5_REFERENCE_INCOMPLETE.
These output fixes neither explain nor resolve the publication mismatch.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Issue #67 remains incomplete; draft PR,
auto-merge disabled, no merge or successor. No EWP, defaults or old-model changes.
