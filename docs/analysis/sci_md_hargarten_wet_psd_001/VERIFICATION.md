# Verification and reproduction

Scientific result, independent review, software checks and hosted CI are separate.
G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Actual base `853cc0b609e0abaf9713579f7c0237a859692400`, with #354 merged.
Plan/contract commit `64c6a1a9d19c8f90b53964e3ac00bbaa8da7d890` preceded formal
outputs. No main advancement needed reconciliation. EWP was read-only at
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Final submitted/tested head and
final hosted receipts are recorded in the single draft PR handoff, avoiding a
self-referential commit hash in this file. Leave OPEN / DRAFT / UNMERGED,
auto-merge disabled.

## Scientific evidence and independent review

The single [independent AI scientific review](REVIEW.md) passed after two source
ordinate corrections and three unsupported overlapping-marker dispositions,
all before formal Part C outputs. The independent checker reconstructs all ten
CDF-excess certificates and every reported table from original coordinates, with
Fraction arithmetic and exact integer-root log-diameter bounds. It imports no
producer and reads outputs only after independent reconstruction. Review hashes
are retained in review_receipt.json. This is not human GitHub approval.

All20 producer artifacts (RESULT.json, nine CSV/JSON pairs, comparison.svg)
reproduce byte-for-byte with network sockets disabled and PyMuPDF/fitz unavailable.
Numerical source is retained coordinates/contract only; matplotlib is needed only
for the figure. Original source inspection/extraction is a separate optional step.
The figure was visually inspected. The independent checker also rejected separate
alterations to a contrast bound, condition outcome, certified witness excess and
ratio endpoint. A 2x uniformly scaled synthetic CDF remains non-excluding at its
matched supported cutoffs.

## Local software checks

- Focused new+predecessor suite: **59 passed**, 67.23 s (21 new,38 predecessor).
  Initial focused check before the checker existed:20 passed,1 deselected.
- Available-register/family-index/data-guide tests: **9 passed**,0.20 s.
- Affected corpus-projection tests: **12 passed**,0.47 s.
- Registry gates: **66 PASS,1 ACKNOWLEDGED_EXCEPTION** (pre-existing exception).
- Repository Ruff: PASS. No runtime component, accepted gate, dependency default,
  hydraulic model, EWP file or production lock changed.
- Generated registry/build/availability/corpus, three manuscript claim audits,
  lateral-coupling verification, both strict evidence scopes, graph verification,
  Insight Foundry, status truth and local corpus coverage: PASS after affected
  corpus-count regeneration described below.
- Two archive builds byte-identical; archive contents/hash verification passed.
- All protected scalar/predecessor files authenticate against retained SHA256s.
  Unrelated MANIFEST lines/endings and append-only Insight IDs are preserved.
- Ordinary offline suite: **7,078 passed,2 failed,32 skipped,72 deselected**,
  1,483.68 s. The two generated-document failures and corrections are retained below;
  this run is not relabelled PASS. Both affected test files then passed **56 tests**,
  24.15 s. The focused suite above includes the new tests, which were added after
  ordinary-suite collection. Required hosted checks run the final submitted head;
  their exact statuses and links are recorded in the final PR handoff.

Tests cover panel-specific log axes, fraction/percentage-point units, physical-bin
mapping remaining unsupported, nominal shared-calibration CDF feasibility,
monotonicity/plateaus/gaps/tails, known uniform scaling, positive excess, exact-zero
and overlapping non-exclusions, positive witnesses despite missing rows,
incomplete coverage, quantile brackets/ratios/intersections and inconsistent CDF
inputs that cannot create vacuous exclusion. Scientific empty intersections are
distinct from bad input/numerical exceptions; no such exception occurred in the
retained-input production run.

## Preserved failures and corrections

1. Publisher direct PDF download returned HTTP403; TUM published article copy
   succeeded. This is access-path failure, not unavailable scientific evidence.
2. Initial local suite stopped in collection: seven Matplotlib import errors
   (`numpy.core.multiarray failed to import`),63 deselected,12.32 s. The new venv
   had inherited a system NumPy1-compiled Matplotlib while loading NumPy2. Isolating
   the venv and installing declared dependencies fixed the environment. No test,
   selector, repository requirement or scientific input was softened.
3. The compact plan was committed while the registry preflight was still running,
   rather than after it finished; it subsequently passed66+1. This is a process
   ordering deviation, not material target information flow or a science change.
4. Independent source review found the five retained reading/support corrections
   in source_corrections.json. The first formal output uses corrected readings.
   No cutoffs, quantiles, axis/read allowances or outcomes were retuned.
5. Initial generated corpus and Paper3 numeral checks detected the new manifest
   record (123→124). Existing `python -m puckworks.paper3.corpus --splice` updated
   its two projections and four prose counts; both checks then passed. Empirical
   campaign count stays46; the reprinted article is not a new campaign.
6. A focused command named nonexistent `tests/test_paper3_claim_coverage.py` and
   ran no tests. The existing corpus test file passed12 tests; the actual claim
   coverage module passed with zero unaccounted numerals. An initial Ruff unused
   test import was removed. These are ordinary command/lint corrections.
7. `git diff --check` treats the modified MANIFEST line's inherited CRLF as
   whitespace; `git -c core.whitespace=cr-at-eol diff --check` passes while preserving
   unrelated source bytes. The plot xlabel was clarified to distinguish thin raw
   ratio enclosures from thick λ≥1 intersections, with no numerical change.

8. The completed ordinary suite reported a stale corpus block before the earlier
   regeneration and a stale claim-binding audit fingerprint after the manuscript
   count update. Corpus verification passed on the submitted implementation;
   `python tools/claim_binding_audit.py --write` regenerated its two audit artifacts.
   Rerunning both complete affected test files passed56 tests. Scientific inputs,
   reviewed outputs, test selectors and accepted gates did not change. Full failed
   run and correction-run log SHA256s are retained in verification_record.json.

These failures are not scientific hypothesis failures. No timeout/cancellation is
reported as passing. Hosted infrastructure retries follow the repository's single
same-head retry policy, with final details retained in the PR if needed.

## Commands and dependencies

Environment used: Python3.12, NumPy2.5.4, SciPy1.18.1, matplotlib3.11.2,
pytest9.1.1; extraction only: PyMuPDF2.0 and openpyxl3.1.5 for the holdings check.
No new runtime dependency was added. Numerical producer and independent checker
use the Python standard library; figure uses the existing `figures` extra.

```sh
python -m pip install -e '.[dev,figures]'
python -m puckworks.analysis.hargarten2020_wet_psd --output /tmp/hargarten-psd --plot
python docs/analysis/sci_md_hargarten_wet_psd_001/review_check.py
python -m pytest -q tests/test_hargarten2020_wet_psd.py tests/test_corrochano2017_density_normalization.py
python -m pytest -q tests/test_available_data_register.py tests/test_local_corpus_family_index.py tests/test_espresso_data_guide.py tests/test_paper3_corpus.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -m ruff check puckworks/ tests/
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
```

Affected owner regeneration commands:

```sh
python tools/build_available_data_register.py
python tools/build_local_corpus_family_index.py
python tools/build_espresso_data_guide.py
python -m puckworks.insights write
python -m puckworks.paper3.corpus --splice
python tools/claim_binding_audit.py --write
```

Required protected checks, refreshed by `python -m puckworks.statusdoc --audit-ruleset`:
quick(3.10),quick(3.12),verify-generated,paper3-scope-strict,all-scope-strict.
Hosted CI is not implied by local PASS; final exact-head status and links live in
this task's draft PR handoff. Auto-merge must remain disabled.
