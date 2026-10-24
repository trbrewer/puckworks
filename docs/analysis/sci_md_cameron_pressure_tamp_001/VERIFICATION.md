# Verification record

Actual base: `72769feddee3fc38a4f716643bca9c567a595919` (live main, PR #358).
EWP reference main: `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.
Both live references matched the supplied identities at intake on 2026-10-24.
An isolated `analysis/sci-md-cameron-pressure-tamp-001` worktree preserves unrelated work.
Final submitted/tested head and hosted check URLs/results are recorded in the PR
closeout, rather than embedding a commit's own hash in its tree.

## Scientific and local checks

- [One independent AI review](REVIEW.md): **accepted**. Actual source figure and
  native paths inspected; separate Decimal corner enumeration checks all 36
  rows, representative arithmetic and all claims. Three small source-record
  corrections were closed in that same review; contrast results did not change. After review, the CSV writer was set explicitly
  to LF line endings to satisfy the whitespace check; JSON, all numbers and the
  figure remain byte-identical to the reviewed artifacts.
- Downloaded SI/main PDFs have the authenticated hashes in SOURCE_NOTES. Native
  re-extraction with recorded PyMuPDF 2.0 reproduces observations.json byte-for-byte.
  All five numerical/figure outputs reproduce byte-for-byte from the committed
  qualified observations using only Python's standard library.
- **82 focused tests passed** in the supported project environment: the seven
  new scientific-risk checks, available-data register, family index, data guide,
  data loaders, README governance and Paper 3 corpus checks. New checks cover
  design/series/source-object accounting, short end-dash anchors, missing-bar
  propagation, direct signed arithmetic, shared calibration/offset cancellation,
  no double-counted marker allowance in B, outward rounding/signs and reproduction.
- Registered gates: **66 PASS, 1 acknowledged existing exception**. No gate,
  acceptance tolerance, production model or physics was modified.
- Ruff on all changed Python files, whitespace check, local corpus coverage
  (39 mapped/registered families), Insight verification, Paper 3 registry/build,
  availability/corpus verification, Paper A/B/3 claim coverage, and evidence-graph
  verification plus both strict scopes: **passed**.
- Environment for repository checks: Python 3.12.3, NumPy 2.5.4, SciPy 1.18.1,
  pytest 9.1.1. A first focused invocation in the separate PDF-tool environment
  inherited unsupported system NumPy 1.x and reported five missing-`trapezoid`
  failures in unchanged model tests (65 passed). The identical selection passed
  70/70 in the supported environment, then the final selection including the
  affected corpus checks passed 82/82. No source/test/gate relaxation was made.
- A broad local suite was started at the base before edits, while later files
  were still being updated; it is not claimed as final-head qualification.
  Final full-suite attribution belongs to the exact-head hosted checks below.

Commands (from the checkout; use an environment satisfying pyproject.toml):

```bash
python -m puckworks.analysis.cameron2020_pressure_tamp --output /tmp/cameron-s2
PYTHONPATH=. python tools/extract_cameron_s2.py --pdf "$CAMERON_SI_PDF" --output /tmp/cameron-s2-native
cmp puckworks/data/cameron2020/s2/observations.json /tmp/cameron-s2-native/observations.json
python -m pytest -q tests/test_cameron2020_pressure_tamp.py \
  tests/test_available_data_register.py tests/test_local_corpus_family_index.py \
  tests/test_espresso_data_guide.py tests/test_data_loaders.py \
  tests/test_readme_governance.py tests/test_paper3_corpus.py
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
```

## Generated surfaces and preservation

Only affected producers ran: `tools/build_available_data_register.py`,
`tools/build_local_corpus_family_index.py`, `tools/build_espresso_data_guide.py`,
`python -m puckworks.paper3.corpus --splice`, then
`python -m puckworks.insights write`. The corpus producer was required by the new
manifest row: 126→127 records, with campaign/component counts unchanged. It also
refreshes its existing manuscript count projections. No generated block was
hand-edited. Insight source/commit fingerprints cause wider generated diffs;
its append-only registry retains every prior ID. New discovery seeds are neither
scored nor executed and do not authorize a successor.

All 126 previous manifest rows compare equal to the base. Existing Smrke data,
S1 analysis/result bundle and Figure 3, Cameron Figure 5 CSV, source audit and
gate-correction evidence, consolidated-input permeability result bundle, model
and validation directories, .github policies and dependency declarations/locks
compare unchanged. Cameron's main card gains only an S2 pointer; its accepted
physics/numerical evidence is preserved. EWP received no writes. Restricted
publisher PDFs, page renders, raw streams, environments and private logs are
outside Git. No successor analysis or model fit was executed.

## Hosted closeout

The live **Protect main** ruleset 19053322 requires `quick (3.10)`, `quick (3.12)`,
`verify-generated`, `paper3-scope-strict` and `all-scope-strict`. These checks are
required for this delivery; no CI policy or threshold was changed. The PR body
and its final closeout identify their final head, any synthetic merge tested,
results and URLs. This document does not turn an unobserved pending run into a pass.
The delivered PR must remain **OPEN / DRAFT / UNMERGED**, auto-merge disabled.

**PHYSICAL_VALIDATION=NOT_ESTABLISHED.**
