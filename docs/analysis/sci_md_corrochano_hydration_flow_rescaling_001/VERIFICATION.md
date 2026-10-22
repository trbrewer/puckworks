# Verification and handoff record

Scientific disposition: supported complete-envelope discrepancy for caption and
prose ratios on PRIMARY and SECONDARY. RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Software, scientific review and hosted infrastructure have separate dispositions.

## Identities and environment

Actual intake/base: d4eb54ce4bd0eb21a0968d3c37f43ad4ef8ccd16.
Read-only EWP main: f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516.
PR350/215 merged at live intake; current code/PR search found no equivalent.
Plan/source freeze:3a5a6c41 (full identity available in Git history).
No changes to EWP, dependency pins, prior numerical results or production defaults.
The independent review binds the scientific candidate and file hashes in
REVIEW.md. Final tested head/base and hosted job URLs belong to the draft PR's
handoff receipt; hashes permit unchanged scientific evidence to be reused.

Local environment: Python3.12.3, NumPy2.5.4, SciPy1.18.1,
Matplotlib3.11.2; optional exact-copy extractor PyMuPDF2.0. No dependency pin
changes. Routine numerical calculation is exact Fraction arithmetic from
retained decimal coordinates/reported flows; signs never use display rounding.

## Completed checks

- Baseline registry:66 PASS, one pre-existing ACKNOWLEDGED_EXCEPTION.
  Both prior Corrochano analysis modules:31 tests passed.
- New focused module:18 tests passed. Meaningful synthetic controls cover
  nonzero affine intercept, exact ratio/direction, steep horizontal uncertainty,
  interior extrema, vertical repeated-x segments, endpoints/gaps, inverse full
  support, shared-axis outer inclusion, three-trace completeness, signed interval
  subtraction, strict sign versus zero/touch/display rounding and every request.
  Independently inspected source facts check transformations/effective stroke,
  chunks/legends/duplicates, joins and positive transformed support. No test
  requires the motivating60s separation.
- Final affected selection:137 passed in32.48s. Includes new and both prior
  Corrochano modules, available register, local corpus family index, espresso
  guide, corpus/manuscript consistency and Paper A model-contract checks.
- Optional exact-PDF re-extraction: coordinates.csv and paths.json byte-identical.
  PDF identity/content confirmed separately; full source/logs remain external.
- Offline producer: RESULT.json, envelopes.csv, pairs.csv, readings.csv,
  pair_support.csv and comparison.svg byte-identical in a fresh output directory.
  Original two-panel reconstruction visually inspected; local VizSpec validated.
- Ruff across puckworks/tests and extractor passes. Registry artifacts/build,
  availability/corpus, all three manuscript claim-coverage checks, lateral
  discrimination generated artifacts, evidence graph verification and strict
  paper3/all reconciliation, insights, status truth and corpus coverage pass.
  Two Paper3 archives are byte-identical and self-verify.
- Normal full local quick suite was started with the current workflow selector:
  `pytest -q -m 'not slow and not live and not gpu and not external_data'`.
  It was still running when this candidate record was written. Its **actual
  completion**, final tested revision and required hosted conclusions are
  recorded in the PR handoff receipt, without implying a pass from startup.

Affected test command:

```sh
python -m pytest -q tests/test_corrochano2017_hydration_flow.py tests/test_corrochano2017_aspect_ratio.py tests/test_corrochano2017_pressure_flow.py tests/test_available_data_register.py tests/test_local_corpus_family_index.py tests/test_espresso_data_guide.py tests/test_paper3_corpus.py tests/test_paper3_manuscript_consistency.py tests/test_paper_a_model_contract.py
```

Offline reproduction:

```sh
python -m puckworks.analysis.corrochano2017_hydration_flow --output /tmp/hydration-flow --plot
```

Optional source audit (never invoked by routine tests):

```sh
python tools/extract_corrochano2017_hydration_flow.py SOURCE.pdf --output /tmp/source-audit
```

## Corrections, independent review and CI

The pre-production tick-residual check correction0.04→0.05pt is recorded in
SOURCE_RECONCILIATION; reading allowances and comparison surface did not change.
During implementation the first CSV writer rejected heterogeneous same-clock/
proxy support fields; a union of field names fixed serialization before a
complete result was delivered. No calculated sign or source contract changed.
Initial affected run:136 passed/one failed because the existing claim-binding
document was stale after manifest-count regeneration. Its existing producer
regenerated it, and the full affected selection then passed137/137. The old
pressure-flow test now requires its named scopes as a subset, permitting the
new separately qualified dataset without changing historical labels/results.

The one independent AI scientific reviewer directly inspected source PDF and
native stream, independently computed all45 envelope/405 pair rows with a
separate Decimal60 implementation (no producer import), and checked complete
support/decision logic. See REVIEW.md for its disposition and hash receipt.
Minor review findings corrected: explicit source URL and raw-path hash-scope
locators; plotted envelope bars now sit at their exact proxy abscissae. The
scientific reading contract, retained coordinates and numerical comparisons
were unchanged by these provenance/presentation corrections. This is not human
GitHub approval or independent experimental validation.

The live active ruleset19053322 requires quick(3.10), quick(3.12),
verify-generated, paper3-scope-strict and all-scope-strict, with strict base
currency. A legacy branch-protection response is not the authority. Required
hosted completion is checked on the final pushed head and reported in the PR;
this pre-push record does not claim those jobs already ran. Infrastructure
failures are separate; existing policy requires one same-head retry for timeout
or cancellation, preserving the first outcome and never weakening science.

Manifest122 records (prior121), campaign denominator unchanged46. Existing
register/family/guide/corpus/claim-binding/insight producers refreshed affected
projections; no generated file was hand-edited, no generic framework added and
no discovery candidate scored. PDF/renders/full logs remain external; compact
source facts and original figure are durable repository artifacts.

Deliver exactly one open draft PR, unmerged, auto-merge disabled. No successor.
