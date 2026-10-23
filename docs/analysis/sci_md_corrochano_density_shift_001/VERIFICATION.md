# Verification and reproduction

Scientific disposition, independent scientific review, local software checks and
hosted CI are separate. G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY /
RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Actual base: `e21631e741ff739aaf4a6b9c58e5e11b161436cc` (current main, #352 merged).
Read-only EWP main: `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.
Canonical remote refs and task PR/branch/content searches were refreshed at intake.
Only historical density-shift scope statements were found, no existing implementation.
No EWP checkout, production lock or data-authority file was changed.

## Before formal production

- All four accepted input SHA256 values match #352's retained RESULT.json.
  The task-local calculation contract preserves hashes for all 22 accepted source,
  predecessor analysis, producer and test files.
- Inherited dry-compaction tests: 21 passed in 22.89 s.
- Other Corrochano and affected registration/guide tests: 58 passed in 3.11 s.
- Registry gates: 66 PASS, one pre-existing ACKNOWLEDGED_EXCEPTION.
- Full-graph strict evidence reconciliation and repository Ruff checks passed.
- New analytical controls: 17 passed, three formal/replay tests deliberately
  deselected before the plan commit. The exposed B1/E2 values are not test oracles.
- Ordinary baseline selection: 7022 passed; 32 skipped; 72 deselected; 8 pre-existing
  warnings in 1425.48 s. New task files were authored while this original selection
  ran; the candidate full suite is reported separately.
- Plan/contract commit before formal production:
  `b7a0364eecf46c57d768bc1e6a68b8af968b825a`. No new formal comparison ran earlier.
  Protected paths also match #352 tested head through the merge byte-for-byte.
- Environment reused externally: Python 3.12.3; NumPy 2.5.4; SciPy 1.18.1;
  Matplotlib 3.11.2. Repository dependencies and pins are unchanged.

The independent reviewer prepared a separate original-coordinate checker before
formal production, without executing new comparisons until the plan commit notice.
This task reuses the predecessor's retrospective workflow, not a protected-data
scoring lifecycle. No new governance machinery or uncertainty framework is added.

## Reproduction

```sh
python -m puckworks.analysis.corrochano2017_density_shift --output /tmp/density-shift --plot
python -m pytest -q tests/test_corrochano2017_density_shift.py tests/test_corrochano2017_dry_compaction.py
python docs/analysis/sci_md_corrochano_density_shift_001/review_check.py
```

Normal production needs only retained CSV/JSON geometry and the unchanged inherited
helpers. No network, original PDF or optional PDF reader is required. The existing
Matplotlib plotting option supplies the original local-VizSpec SVG. Exact rational
classification precedes six-decimal outward display rounding.

## Hosted policy and final identity

Active ruleset 19053322 was re-read at intake through the GitHub API (the connector
does not expose rulesets). Required contexts remain `quick (3.10)`, `quick (3.12)`,
`verify-generated`, `paper3-scope-strict` and `all-scope-strict`, with strict base
currency. No check, selector or timeout is weakened. A timed-out/cancelled job is
retried once on the exact same head under governance section 8; infrastructure
status is separate from scientific findings.

The final submitted/tested head, hosted run URLs, and verified OPEN/DRAFT/UNMERGED
state with auto-merge disabled are recorded in the PR handoff. This file does not
infer hosted success from local execution. Independent AI scientific review is
recorded separately in REVIEW.md and is not human GitHub approval.

## Completed candidate checks

- New plus inherited dry-compaction tests: **41 passed in 29.59 s** (20 new,
  21 predecessor). Analytical oracles cover the new dependency and decision logic;
  accepted B1/E2 values are only a diagnostic, never a regression oracle.
- Other Corrochano/registration/guide/corpus/model-contract checks: **104 passed
  in 27.20 s**. One initial command named a nonexistent test file and collected no
  tests; the corrected command passed. This was command selection, not a test or
  scientific failure.
- All five CSVs, RESULT.json and comparison.svg reproduce byte-for-byte with
  network access denied and both optional PDF readers unavailable. The original
  SVG was visually inspected via a PNG render of the same plotting function.
- Ruff, registry artifacts/build/availability/corpus, all three manuscript claim
  coverage checks, lateral-coupling artifact verification, both strict scopes,
  evidence-graph verification, Insight Foundry verification, status truth, local
  corpus coverage, README governance and README pulse verification all pass.
- The existing availability-register/family-index/data-guide producers and Insight
  Foundry writer regenerated affected projections. Insight fingerprints propagated
  the changed card and one manifest use field; no evidence label, stable candidate
  ID, dataset count or campaign denominator changed. MANIFEST still has 123 rows.
  Only this existing dataset's gate_use field changes; unrelated mixed line endings
  are preserved. No generated projection was hand edited.
- Independent scientific review: **PASS**, no unresolved material findings; all
  23 reviewed scientific/curated files and 22 preserved predecessor hashes match.
  Review's two nonsemantic findings are resolved in the same lane.

The final ordinary suite uses the unchanged selector
`not slow and not live and not gpu and not external_data` and was started after
the scientific code, tests, fixed inputs, outputs and curated capability changes
were finalized. Its completed counts/timing and the final exact tested/submitted
head are recorded in the PR handoff alongside hosted-check URLs. Later review
formatting and this verification receipt do not change those scientific files.
The baseline and focused checks above are completed evidence; this paragraph does
not substitute them for that final ordinary-suite result. No unchanged expensive
scientific campaign was rerun.
