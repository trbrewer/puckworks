# Verification record

Scientific disposition, independent review and software/CI status are separate.
G1 / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL /
NO_GOVERNING_PHYSICS_CHANGE / PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Actual intake base: bf65fa3d9bd9664545bb3fb4e1e97fc1e0ebc94b.
Read-only EWP main: f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516.
PR351 was verified merged. Final tested head and hosted job receipts are recorded
in the PR handoff, avoiding a self-referential commit identity in this file.

Python3.12.3, NumPy2.5.4, SciPy1.18.1, Matplotlib3.11.2; optional exact-source
extractor PyMuPDF2.0. Installed in a task-local external virtual environment;
repository dependency pins and defaults are unchanged. Routine analysis uses
exact Fraction arithmetic and compact retained CSV/JSON only, without network/PDF.

## Pre-comparison checks

- Source PDF SHA256 matches the requested exact copy; journal copy identified
  separately. Raw operands, composed coordinates, API geometry and stroke checked.
- Clean-base affected Corrochano regression tests:49 passed in3.05s.
- Registry gates:66 PASS, one pre-existing ACKNOWLEDGED_EXCEPTION.
- Pre-score synthetic/source/registration tests:16 passed (five formal-result/replay
  tests deliberately not run until the plan/contract commit).
- Availability, family index, guide, corpus/manuscript consistency and model-contract
  checks:88 passed in30.13s.
- Formal comparisons were not run before the plan/source/contract commit.
  Plan SHA256 is bound in contract.json and tested.

The full normal suite was started before the source work; subsequent source and
registration additions occurred while it ran. It is therefore a pre-score working
suite receipt, not falsely described as a pristine-base full replay. It completed with7001 passed,32 skipped,72 deselected and8 warnings in1403.04s.
No failures. The final full candidate suite was then started with the same selector;
its actual completion and exact tested head are reported in the PR handoff.

## Reproduction

```sh
python -m puckworks.analysis.corrochano2017_dry_compaction --output /tmp/dry-compaction --plot
python -m pytest -q tests/test_corrochano2017_dry_compaction.py
```

Optional exact-source audit (source stays outside Git):

```sh
python tools/extract_corrochano2017_dry_compaction.py SOURCE.pdf --output /tmp/dry-source-audit
```

## Hosted policy

Active ruleset19053322 was read at intake. Required contexts are quick(3.10),
quick(3.12), verify-generated, paper3-scope-strict and all-scope-strict, with strict
base currency. No check is weakened or bypassed. Hosted outcomes belong to the
final pushed head and are reported in the PR handoff; this paragraph alone makes
no hosted pass claim. Existing same-head retry policy applies to timeout or
cancellation, separately from scientific results.

## Completed candidate checks

- Focused new tests:21 passed in22.22s. Synthetic controls cover transforms,
  duplicate handling, all inverse crossings and plateaus, two-axis full support,
  gaps/short curves, same-sample subtraction, missing membership, incomplete
  separation, endpoint combinations, force-offset cancellation, exact sign before
  display rounding, all156/12 requests, registration and offline replay.
- Routine producer works with PDF modules unavailable and with network disabled.
  All six CSVs and RESULT.json reproduce byte-identically; SVG rendering repeats
  deterministically and was visually inspected as an original four-panel analysis.
- Ruff across puckworks/tests and optional extractor passes. Registry artifacts,
  build, corpus, availability, all three manuscript claim-coverage checks,
  lateral-coupling artifacts, evidence graph, paper3/all strict scope, insights,
  status truth and local corpus coverage pass.
- Manifest123 records (prior122), existing campaign denominator46 unchanged.
  Only directly affected register/family/guide/corpus/claim-binding/insight
  projections were regenerated with their existing producers. No unrelated
  research calculation or historical scientific result was regenerated.
- Initial `corpus --write` printed a report (unsupported option), so the documented
  `--splice` invocation performed the actual update. No scientific inputs changed.
- All formal calculations followed plan/contract commit
  ffb9a4d922fd0cef96c53a5e23324a3ae8d5fde9. No contract retuning occurred.

Final affected selection:158 passed in54.90s (new module plus three prior
Corrochano modules and registration/corpus/manuscript checks). Optional exact-PDF
re-extraction reproduced coordinates.csv and paths.json byte-for-byte. Fresh
numerical/CSV and SVG replay also matched. Scientific review is recorded separately
in REVIEW.md. Final hosted contexts and
final worktree state are verified at handoff rather than inferred from local tests.
