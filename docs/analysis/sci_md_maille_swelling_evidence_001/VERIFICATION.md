# Verification and delivery record

SCI-MD-MAILLE-SWELLING-EVIDENCE-001. Scientific interpretation, source access,
software checks and CI infrastructure are separate. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Identities and scope

Both main refs were freshly fetched before work and matched the reviewed bases:
Puckworks`4f378aa6757e9d61c4231d078aa4e7718736a394`,
EWP`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.
Exact-task and broader Maille PR searches found only distinct2024 extraction/
historical work, not this implementation. The isolated Puckworks branch is
`research/sci-md-maille-swelling-evidence-001`. EWP content is unchanged and its
working tree remains clean; only its remote main metadata was refreshed.

The plan/native readings were fixed before formal derived comparisons, after
public-source inspection. [intake_freeze.json](../../../puckworks/data/maille2021/swelling_evidence_001/intake_freeze.json)
retains the original hashes and the later explanatory mapping clarification.
This is retrospective/target-exposed, not a prospective preregistration or holdout.

No production code, Mo card/constants/implementation, governing equations, locks,
defaults, CI files or accepted Hargarten/Maille2024 result bundles changed.
The reported zero Mo solver runs counts **task-specific scientific analyses**;
ordinary pre-existing regression tests/registry gates may execute Mo. No new Mo
comparison/sweep, diffusivity/entrainment fit, hydraulic closure or OpenFOAM run.

## Scientific and numerical checks

- Independent reviewer opened and rehashed both authenticated PDFs and the actual
  Figure4/individual-particle/before-after artwork. Axis arrows, concentration vol%,
  all24 left markers, eight graphical time joins and unpooled right cluster agree.
- All supported denominators are positive. Exact rational calibration corners
  enclose the shared-anchor dependencies. No independent lab-error assumption.
- Independent direct arithmetic reproduces all48 interval pairs and the decisive
  O01-lower>O08-upper certificate. Strict K gap:
  `9224897900390625/2774174018 m^-3` (about3,325,277.304356408).
  R intersection is necessary-only `[158/87,134/65]`.
- Five analytical controls pass: common scaling preserves both invariants;
  linear concentration versus size violates the cubic invariant; touching intervals
  are non-excluding; missing/nonpositive denominators stay unsupported; shared
  calibration interiors lie inside the outer bounds; a shape-quantile change can
  independently violate R. These are mathematical controls, not science validation.
- Network-denied/PDF-reader-disabled regeneration reproduced RESULT.json,
  intervals.csv and comparison.svg byte-for-byte. Independent reviewer replay
  also matched all three. The plot was visually inspected for units/claim scope.
- No quantitative microscopy segmentation was admitted. Source caption/scale/
  correspondence were checked, but bubble-obscured coffee boundaries, projection
  and focus uncertainty prevent a numerical geometric-growth bound. Copied outlines
  and repeated depictions never supply new measurements.
- Hargarten diameter/area/volume semantics and preparation/clock differences were
  checked against accepted contracts and original methods. Mo's equilibrium formula
  is a model interpretation only. C_M and D_W remain unbounded and unchanged.

[REVIEW.md](REVIEW.md) and [review_receipt.json](review_receipt.json) record one
independent AI scientific review, **PASS_AFTER_BOUNDED_CORRECTIONS**. Two defects
were corrected: inward rounding in narrative summaries, and making the conditional
scale-equivariant measurement map explicit. The formal readings/allowances and
numerical results were unchanged. The same review records a subsequent metadata-only
addition of the exact public thesis PDF locator. No material finding remains open;
this is not human GitHub approval or independent physical validation.

The final whitespace check found standard CSV CRLF endings and Matplotlib SVG
trailing spaces. They were normalized without changing any cells or drawing
commands. [verification_record.json](verification_record.json) preserves the
reviewer's original hashes and proves each final difference is an invertible
formatting change (plus appended correction records). The producer change only
normalizes its output whitespace. Final formatted replay is byte-identical and
the26focused tests pass again; unchanged scientific review evidence is reused.

## Local checks

- Task controls plus affected register/corpus/guide tests: **26 passed**.
- README tests: **54 passed** after correcting a missing source-card reference
  and trimming adjacent prose to retain the existing 52,000-byte limit. The first
  focused run had two failures (reference coverage and size); neither test was weakened.
- Repository Ruff and independent checker lint: PASS.
- Project mypy: PASS (19 source files; existing untyped-body informational note).
- Registry gates: **66 PASS, 1 ACKNOWLEDGED_EXCEPTION**, pre-existing exception.
- Register/family/data-guide generators, corpus splice, claim-binding audit and
  Insight Foundry regeneration: completed. Corresponding focused tests and
  Foundry verification pass. Existing local snapshot remains39 families; this new
  public-source intake is not retroactively inserted into that old inventory.
- Registry/build/availability/corpus generated checks, all three manuscript numeral
  audits, lateral-coupling artifacts, evidence-graph artifacts, strict paper3/all
  scopes, status-source verification and README governance: PASS.
- Two existing scientific archive builds compared byte-for-byte and archive
  verification passed.
- Broad offline regression suite was started before the new five tests existed;
  its collection contains the existing tests. Final result is recorded in the
  delivery PR together with the separately executed new/affected tests. It is not
  described as a new clean-base scientific experiment or an exact-head full-suite
  replay. Unchanged test/source identities support reuse after metadata-only edits.

One manifest row/source card is added. Generated dataset records increase125→126,
and the generator's distinct dataset-source families46→47: one2021 source family,
not three independent campaigns from journal/poster/thesis. No registered runtime
component or evidence strength is promoted. Generated insight line references and
corpus counts are ordinary projections, not new scientific claims or a framework.

## Reproduction

Python≥3.10; install existing`.[dev,figures]` extras for tests/plotting. No new
dependency or lock change. Numerical producer/checker use standard-library arithmetic.

```sh
python -m puckworks.analysis.maille2021_swelling_evidence --output /tmp/maille-replay --plot
python docs/analysis/sci_md_maille_swelling_evidence_001/review_check.py --output /tmp/maille-replay
python -m pytest -q tests/test_maille2021_swelling_evidence.py tests/test_available_data_register.py tests/test_local_corpus_family_index.py tests/test_espresso_data_guide.py tests/test_paper3_corpus.py
python -m pytest -q -m 'not slow and not live and not gpu and not external_data'
python -m ruff check puckworks/ tests/ docs/analysis/sci_md_maille_swelling_evidence_001/review_check.py
python -m mypy
python -c 'from puckworks.registry import run_all_gates; run_all_gates()'
```

The existing generators used are`tools/build_available_data_register.py`,
`tools/build_local_corpus_family_index.py`,`tools/build_espresso_data_guide.py`,
`python -m puckworks.paper3.corpus --splice`,
`tools/claim_binding_audit.py --write`, and`python -m puckworks.insights write`.
Source PDFs and artwork are required only for optional source reinspection,
not offline reproduction. Their rights and exact hashes remain in provenance.

## Hosted CI and final handoff

The live ruleset audit identifies required checks: quick(3.10), quick(3.12),
verify-generated, paper3-scope-strict and all-scope-strict. CI configuration,
timeouts, selectors, tolerances, floors and requirements are unchanged.
This committed record predates submission; the delivery PR binds its final
submitted/tested head, required/optional hosted jobs and URLs without embedding
a self-referential commit hash. Pending jobs are not passes.

For cancellation/timeout, preserve the run and retry once at the same head under
the existing policy. Repeated infrastructure incompleteness remains reported,
not a scientific failure or a reason to change this task's CI. Leave the PR
OPEN/DRAFT/UNMERGED with auto-merge disabled. No merge or successor is authorized.
