# Verification and handoff

Scientific findings, software checks, independent review and hosted CI have
separate dispositions. The scientific outcome is in [RESULT.md](RESULT.md):
one conditional partial-bundle contrast, no qualified persistent temporal
comparison, and no physical validation. A passing test does not strengthen
that scientific evidence.

Actual Puckworks base: `52df324ee809249eacad1233e407434260e22d46`.
Read-only EWP base: `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.
The isolated task worktree preserves unrelated work. All 42 protected files
in [SOURCE_IDENTITIES.json](SOURCE_IDENTITIES.json) remain byte-identical to
that base, including Figure 3, its two consumers and accepted endpoint
evidence. EWP is unchanged. Historical receipts and their verifier were not
rewritten, and source endpoint fits were not rerun.

## Completed local verification

- The isolated current-worktree environment passed 207 affected tests. These
  cover the S1 reconstruction and analytical risks, loader compatibility,
  Figure 3 consumers, register/family/guide generation, normal insight
  projections and README governance.
- Ruff passed across `puckworks`, `tests` and the independent checker. Mypy
  passed its normal 19-file scope. Strict all-scope validation, status truth,
  registry/build/availability/corpus projections, evidence-graph reconciliation
  and verification, insights verification and README governance passed.
- The registry retains 66 passing gates and its pre-existing acknowledged
  exception. There is no scientific-status promotion.
- Full native reconstruction and analysis reproduced all 22 checked files
  byte for byte in a separate directory with socket networking denied.
  Exact rational arithmetic and outward rounding preserve the sign decisions.
  Reproduction commands are in RESULT.md; the machine receipt records hashes.
- The independent review inspected the actual image, ticks, masks, clipping,
  representative crossings/gaps, phases and identity limits. Its separate
  checker recomputed all four supported windows and the only strict contrast
  without importing producer functions. The final rerun exactly reproduced
  the committed receipt, SHA256
  `e401972a860508f6fb277c10c515cef7e1eaf65765e68c422b6fe9418dda0233`.
  [REVIEW.md](REVIEW.md) records the resolved material findings and claim limits.

The full normal local quick suite uses:

```sh
python -m pytest -q -m 'not slow and not live and not gpu and not external_data' \
  --junitxml=isolated-quick-report.xml --durations=15
```

It was running when this record was created. Its actual completion and final
tested head are recorded in the PR handoff; startup is not a passing result.
The isolated environment is Python 3.12 with the current worktree installed
editable. [VERIFICATION.json](VERIFICATION.json) records exact versions,
commands, log hashes, reproduction hashes and dispositions.

## Preserved failures and corrections

The initial focused run had one failure because the DOCX caption text is split
across XML runs; reading concatenated XML text corrected the test. A broad
local run then found three stale-projection assertions before regeneration.
That run was interrupted after 2,754 passes, three failures, 26 skips and 73
deselections when subprocess imports were found to resolve an older installed
Puckworks copy. It is not reported as a current-root suite pass. The normal
generator refreshed the projections, and an isolated editable installation
removed the environment ambiguity.

A README check also caught a byte-budget overrun in the new Smrke sentence;
shortening it preserved the correction to the unsupported exclusive
permeability claim. A pulse mismatch in the reused environment disappeared
with the correct installation. The final 207-test selection includes these
previous failures. Full failed logs remain in the external evidence directory,
with identities and resolutions in VERIFICATION.json. Scientific producer
corrections and withdrawn initial witnesses have their separate preserved
identities in the data family's CORRECTION.md; they are not hidden by test status.

## Hosted CI and final handoff

The live enforced ruleset requires `quick (3.10)`, `quick (3.12)`,
`verify-generated`, `paper3-scope-strict` and `all-scope-strict`. The final
submitted head, run URLs, conclusions and PR state belong to the PR handoff
receipt, avoiding a self-referential commit hash. This pre-push record does
not claim hosted checks have run.

Preserve every failed hosted attempt. Under the existing policy, retry a
cancelled or timed-out job once on the same head and report any remaining
infrastructure incompleteness separately. This task changes no CI budget,
selector, coverage requirement or dependency lock. It authorizes one open
draft PR, unmerged, with auto-merge disabled, and no successor study.
