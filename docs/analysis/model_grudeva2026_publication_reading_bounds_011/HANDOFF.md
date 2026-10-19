# 011 reproduction and owner handoff

This addendum completes only the supported reading-bound propagation in R-06/T07.
The original 009 nominal-coordinate result, source crosswalk and historical
hash-bound evidence remain unchanged. Full-reference 010, PR #333 and issue #67
retain their separate scope. No automatic successor is selected.

The exact candidate head/tree, final independent review and hosted check status
are recorded in the draft PR body. This file gives the enduring reproduction
instructions; it is not evidence that later candidate checks have already passed.

## Reproduction

Use the original owner-configured evidence parent, verified against predecessor
root hashes. Do not relocate evidence, scan unrelated directories or publish
private paths. The existing roots are 006 spatial-resolution, 007 fine-baseline,
005 baseline-observation and model-grudeva2026-bed-accuracy-004 beneath that parent.
The unchanged 008 admission helpers verify identities, complete arrays, manifests,
receipts, sources, environment and accepted qualification. A missing archive is
known evidence unavailable here, not nonexistent evidence.

The execution environment is the retained Python 3.12.3, NumPy 2.5.3, SciPy
1.18.1, single-thread BLAS/OpenMP configuration; the exact runtime/source hashes
are in 009 CONTRACT.json and checked by the 011 runner. No dependencies or
production defaults change. Use a fresh non-overwriting output directory:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
python -m puckworks.analysis.grudeva2026_publication_reading_bounds_011 \
  --evidence "$GRUDEVA_EVIDENCE_PARENT" \
  --output "$GRUDEVA_NEW_011_OUTPUT" \
  --review docs/analysis/model_grudeva2026_publication_reading_bounds_011/METHOD_REVIEW.json
python tools/grudeva2026_publication_reading_bounds_011_report.py \
  "$GRUDEVA_NEW_011_OUTPUT/results.json" \
  "$GRUDEVA_NEW_011_REPORT"
```

Exit 0 means the declared readout calculations completed, including adverse
scientific findings; it does not mean publication agreement. Exit 3 means partial
horizontal/paired availability, preserving retained-value and unaffected results.
An uncaught contract/implementation failure exits nonzero and retains completed
checkpoints; investigate it separately from scientific findings. No invocation of
the completed 008/009 wrappers, solver, full reference or qualification campaign
is necessary or authorized. Reproduction instructions do not automatically
authorize acquiring missing evidence or rerunning historical campaigns.

`retained.json` preserves A/B before archive admission, `partial.json` checkpoints
each input, and `results.json`/`rows.csv` retain the complete calculation. Published
RESULTS.json/ROWS.csv keep all 124 original records nested under `original`, all
new fields and reasons. Range pieces preserve one-sided limits; hulls do not
establish attainability. Decimal arithmetic is deterministic; execution time is
recorded separately. Expanded numerical enclosures remain null because the
necessary instantaneous/continuum allowances are unestablished.

## Verification and interpretation

```bash
python -m pytest -q tests/test_grudeva2026_publication_reading_bounds_011.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
ruff check puckworks/ tests/ tools/grudeva2026_publication_reading_bounds_011_report.py
mypy
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
```

The focused tests are synthetic and read no expensive scientific archives.
Ordinary automated regression, permitted fixture reads and historical regression
computations are QA. They do not feed protected targets into this analysis.
Keep the existing selectors and hosted checks unchanged. QA.json records actual
outcomes, failures and infrastructure limits separately; METHOD_REVIEW.json is
the independent method audit. The final candidate review is linked from the PR.

Original historical accounting is 124 requested, 72 included, 52 excluded, zero
unavailable. Each input has 17 original failures and one pass. New signed
separation, threshold enclosure and demonstrated compatible-witness sensitivity
are different fields. A threshold-ambiguous hull alone proves no sensitivity;
zero inclusion proves no equality or reconciliation. Comparator temporal
completeness is conditional on the declared event-split discrete interpolant;
continuum accuracy remains unestablished even when every readout calculation
completes. Four input evaluations do not multiply the source observation count.

Source-derived reference readings retain Grudeva, Moroney & Foster attribution,
DOI 10.1017/S095679252500018X, CC-BY-4.0. 004's adapted reference permission
lineage remains separate. No private correspondence, PDFs, full arrays, logs or
owner locators are published. The original figure-producing configuration,
revision, arrays and plotting/readout remain unresolved; no causal diagnosis or
author-error conclusion follows. FIG5_REFERENCE_INCOMPLETE is unchanged.

Leave one PW PR draft, unmerged, auto-merge disabled. EWP main, source, dependency
lock and defaults remain read-only. Historical solvers, fixtures, qualification
receipts, external archive locations, mass/H1 findings and protected-target
controls are preserved. No fit, parameter alternative, source re-extraction,
author contact, native/OpenFOAM execution, lab work, production adoption,
unrelated Fasano change or automatic successor. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
