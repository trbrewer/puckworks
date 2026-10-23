# Verification and reproduction

Scientific dispositions, independent review, local software checks and hosted CI
are separate. G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Actual base is `81cfcebebf0625992fcbb60b93a9c6e965838b36`; #353 accepted head is
`dd5375985a18ccf2af25bd3001d0f72ea71e1a38`. Read-only EWP main remains
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Remote heads and existing task PRs were
checked at intake. No main delta required reconciliation. The fixed plan and
calculation contract were committed before formal production; RESULT.md records
that exact commit. No EWP checkout, production lock, equation, dependency pin,
Smrke S1, source file, predecessor producer/test or historical bundle changed.

## Completed local checks

- Baseline predecessor tests: 41 passed in 29.33 s. Registry gates: 66 PASS and
  one pre-existing ACKNOWLEDGED_EXCEPTION.
- New and predecessor focused suite: 73 passed in 92.81 s. Six subsequently added
  negative-construction/component-index controls passed in 9.03 s (other tests
  deliberately deselected in that bounded delta run). Total focused coverage is
  38 new plus 41 inherited tests. No supplied preview is a numerical test oracle.
- Mathematical controls cover exact contact and both signs/reversal, synthetic
  scaling with nonzero intercept, shared tau despite overlapping marginal ratios,
  signed division, positive slope/denominator guards, page-origin invariance,
  full-strip support, multiple components, reversed/constant segments, both trace
  allowances, missing/invalid certificates, hull gaps, shared h, parameter
  substitution, trace displacement and actual graphical path order. Negative B
  construction controls retain support/amplitude/intersection/order/arithmetic
  failures without claiming B exclusion.
- Affected availability-register, family-index and data-guide tests: 9 passed.
- Repository Ruff passed. Registry artifacts/build/availability/corpus checks,
  all three manuscript claim checks, lateral-coupling artifact verification,
  both strict evidence scopes, evidence-graph verification, Insight verification,
  status truth, local corpus coverage, README governance and README pulse passed.
  Two archive builds are byte-identical and archive verification passed.
- All 13 new numerical/figure artifacts reproduce byte-for-byte offline with
  network sockets denied and both optional PDF-reader modules unavailable.
  The SVG was visually inspected through a PNG from the same plotting function.
- The 38 protected source/predecessor files authenticate against the fixed hashes.
  All 72 density marginals/statuses replay #352 exactly; coordinate hulls/statuses
  replay #353. Neither predecessor's output supplies scientific input bounds.
- Existing projection owners regenerated the register, family index, data-guide
  generated blocks and Insight Foundry. MANIFEST changes exactly one existing
  Figure 6.2 use field; unrelated bytes and line endings remain identical.
  Insight ID_REGISTRY is byte-identical; no identity or campaign count changed.

The initial environment command ran before pytest installation finished and was
rerun after setup. Initial ancillary QA invocations used wrong script paths/options;
the actual existing commands above passed after correction. These were command
selection errors, not scientific or test failures. No repository dependency changed.
The first producer run reported B's no-certificate disposition because a canonical
sample accounting guard detected JSON insertion order. Using canonical sample order
resolved it without changing geometry, allowances, midpoint/tie-break rules or any
numerical candidate. The one scientific review also suggested an explicit invalid
component-index guard; its bounded fix/test changes no retained result.

## Independent scientific review

[REVIEW.md](REVIEW.md) records one independent AI scientific review, **PASS**, with
no unresolved material findings. Its standard-library checker reconstructs original
decimal operands/transforms and independently computes all 990 determinants,
including B3/D2, plus all nominal witness inputs and 72 source certificates.
It checks calibrations, exact memberships/displacements, components, twelve fixed
parameter pairs, one shared h vector, four intersections, path ordering and affine
identities without calling the new producer or trusting its bounds/success flags.
[review_receipt.json](review_receipt.json) binds reviewed scientific/curated bytes.
This is not human GitHub approval, hosted CI success or physical validation.

## Reproduction and normal QA

```sh
python -m puckworks.analysis.corrochano2017_density_normalization --output /tmp/density-normalization --plot
python docs/analysis/sci_md_corrochano_density_normalization_001/review_check.py
python -m pytest -q tests/test_corrochano2017_density_normalization.py tests/test_corrochano2017_density_shift.py tests/test_corrochano2017_dry_compaction.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
python tools/build_available_data_register.py
python tools/build_local_corpus_family_index.py
python tools/build_espresso_data_guide.py
python -m puckworks.insights write
```

The final ordinary suite was launched after scientific code, tests, outputs and
curated updates were finalized. Its final counts/timing and the exact submitted /
tested head are recorded in the draft PR handoff, together with hosted statuses.
A running/missing check is not a pass; focused results above do not substitute for
that final ordinary-suite record. No unchanged expensive scientific campaign is rerun.

The GitHub connector has no ruleset inspection operation, so the active branch
rules were read with `gh api repos/trbrewer/puckworks/rules/branches/main`.
Classic branch protection returns 404; repository ruleset 19053322 is controlling.
Its required contexts remain quick (3.10), quick (3.12), verify-generated,
paper3-scope-strict and all-scope-strict, with strict base currency. No workflow,
selector, timeout or check is weakened. Hosted receipts and final
OPEN / DRAFT / UNMERGED state with auto-merge disabled belong in the PR handoff.
