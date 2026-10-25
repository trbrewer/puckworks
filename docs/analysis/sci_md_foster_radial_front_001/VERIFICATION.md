# Verification receipt — SCI-MD-FOSTER-RADIAL-FRONT-001

Accepted base `236853feb4871dd57d0a6c1a269588db1a88e784` (Puckworks main, PR #361).
EWP remote main `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`; locked dependency
`fc61c4670ec7bf801e40bb391aab16048b8da26b`. Fresh remote identities matched the
review references, so no intervening delta required acceptance. Isolated branch
`sci-md-foster-radial-front-001` preserves unrelated work.

The final submitted/tested head, hosted run links and OPEN / DRAFT / UNMERGED /
auto-merge-disabled confirmation are recorded in the draft PR's description and
handoff. A commit cannot embed its own resulting hash; this receipt binds the
scientific files independently and does not mislabel pending hosted checks PASS.

## Freeze, source and scientific review

PLAN froze at **2026-10-25T01:40:07Z**, after source/primary-scan exposure and
before new numerical reads. SHA-256
`f9678296172593186779f723a4e9f110f567e793188a87d004750f96ffc96dc3`.
This is RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING, not
prospective selection or protected scoring. G1 / NO_GOVERNING_PHYSICS_CHANGE /
RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Actual PDF and all native figure identities/tools/rights are in
[extraction_receipt.json](extraction_receipt.json) and [SOURCE_NOTES](SOURCE_NOTES.md).
Native Figure 8/9 hashes match the supplied reviewed references despite a changed
UL wrapper. Separate extraction with PyMuPDF 1.26.6 / MuPDF 1.26.11 reproduced
all four native figures exactly. The source PDF, original query receipts and
full execution logs remain external. One scoped seven-file Foster collection
query matched the existing snapshot; no census was rerun.

[Independent substantive nonhuman review](REVIEW.md): **APPROVE corrected bounded
result**. One engagement inspected source membership/eligibility, native pixel
visibility, extent semantics, duplicate identity, affine dependence, finite
bounds, figure and conclusions. It found one material primary hidden cap and
five unsupported context cap reads; these were made null. Visible fragments use
the already frozen overlap allowance. Complete G3 compatibility is withdrawn;
primary E/D and G4/G5 are unchanged. No tolerance or source-role retuning.
The exact corrected science/test/figure bindings in
[reviewed_science_hashes.json](reviewed_science_hashes.json) remain authoritative
for this review; no optional review ladder was opened. After review, the staged
whitespace check identified CRLF in the generated result CSV. The only producer
change was `csv.DictWriter(..., lineterminator='\n')`. Byte comparison proves
that single keyword addition is the entire source delta; the CSV differs only
by CRLF→LF. All canonical inputs, numerical JSON, figure and other reviewed
files remain byte-identical. The 23 focused tests and fresh offline reproduction
pass after this serialization-only correction; the earlier source hash in REVIEW
is preserved as the actual reviewed identity, with final hashes below.

The review's separate global LP is corroboration, not strict certification.
Its exact Fraction witness satisfies 549 global inequalities, and independent
rational sign certificates establish the retained conclusions. The portable
[bounded check](independent_check.py) imports no producer arithmetic and can be
rerun with `--pdf SOURCE.pdf --output /tmp/foster-independent`. Its optional
NumPy/SciPy/PyMuPDF dependencies do not enter the offline analysis path.

## Reproduction and focused verification

```bash
python -m puckworks.analysis.foster2025_radial_front --output /tmp/foster-report --plot
python -m pytest -q tests/test_foster_radial_front.py tests/insights/test_foundry.py \
  tests/test_available_data_register.py tests/test_local_corpus_family_index.py \
  tests/test_espresso_data_guide.py tests/test_paper3_corpus.py \
  tests/test_paper_a_model_contract.py
python tools/foster_radial_source.py overlay --output /tmp/foster-overlays
python tools/foster_radial_source.py extract --pdf SOURCE.pdf --output /tmp/foster-source
python docs/analysis/sci_md_foster_radial_front_001/independent_check.py \
  --pdf SOURCE.pdf --output /tmp/foster-independent
```

Offline analysis reads only committed canonical JSON; `--plot` uses the existing
figures extra. PDF/network/extraction packages are unnecessary for numerical
reproduction. JSON and CSV preserve nulls; the flat 90-slot CSV is tested against
the detailed JSON. Fresh processes reproduce the three numerical report files
and comparison image byte-for-byte in the recorded environment. Output image
bytes across different Matplotlib versions are not claimed identical.

Focused tests cover fixed membership/primary roles, native hashes and freeze,
duplicate linkage without endpoint transfer, rule/mixed eligibility, depth sign,
independent E/D/G support, partial obstruction, shared offsets/uncertain scale,
mixed-depiction offsets, per-reading versus preselected minimax, strict/touching/
unresolved/failed qualification, exact finite bounds, outward decimal rounding,
null preservation and deterministic outputs. The independent review separately
checks source overlays and global constraints; tests are not the source authority.

Final focused module: **23 PASS**. Task + existing Insight/discovery tests:
**97 PASS**; corpus/claim-binding affected selection: **46 PASS**. A fresh
combined final process passed **143 tests in 27.51 s**; packaging checks passed
**15/15**. Full configured
Ruff: PASS; configured mypy: PASS (19 modules). Loaded registered components:
**28**, gates **66 PASS / 1 pre-existing ACKNOWLEDGED_EXCEPTION**. No empty-registry
invocation is counted as gate evidence.

Generated registry/build/availability/corpus, Paper A/B/3 claim coverage, evidence
graph verification and both strict scopes, Insight verification, local corpus
coverage (39 mapped/registered), status source and whitespace checks pass.
The broader local-suite and final submitted-head checks are recorded below or in
the PR closeout once completed; scientific qualification is separate from them.

An initial reused PDF environment inherited an older system SciPy and failed
collection (`cumulative_simpson` absent). A dedicated environment satisfying
pyproject.toml fixed that environment issue without changing repository code.
Recorded software: Python 3.12.3, NumPy 2.5.4, SciPy 1.18.1, pytest 9.1.1,
Matplotlib 3.11.2; optional PyMuPDF 1.26.6 / MuPDF 1.26.11, Pillow 13.0.0.
The initial broad local run began before edits and overlapped producer updates;
it is not claimed as exact final-head qualification. Final-head hosted normal
lanes and fresh affected local checks supply the final attribution.

The broad working-tree run completed with **7,188 PASS, 36 skipped, 73 deselected,
3 failures** in 1512.60 s. One family-index check observed an in-flight producer
update and passed fresh after regeneration. Two I-045 live-card assertions still
required the exact historical sentence claiming the fit “validates model FORM.”
Their directly dependent assertions now preserve the exact fitted-to-the-same-
s/H-curves premise and require explicit nonvalidation of model form/prediction.
The historical screen constant, script, result bundle and original evidence
strength remain unchanged. No scientific threshold or test selection changed.
The failure is an active-wording/test dependency, not a numerical result failure.
Fresh affected I-045/family/task checks passed **64 tests, 8 pre-existing
skips** in 19.87 s; full Ruff and staged whitespace checks passed.

## Submitted-head integration correction

The first submitted head `5439b6fa8570343eb2d368f06bc2ae7fa3d5c45b` passed
nine hosted workflows, including scientific baselines. Its quick lanes exposed
two additional integration dependencies: the deep I-045 live-card assertion
still required the withdrawn model-form-validation clause, and the unrelated
frozen Grudeva 009 contract binds `THIRD_PARTY_NOTICES.md` byte-for-byte.
The local run contained the same failures and was stopped after diagnosis;
it is not final-head passing evidence. Earlier tail-only progress observations
missed those failure markers; the full log controls the disposition.

The deep-screen assertion now checks the preserved fitting premise and explicit
nonvalidation clause, matching the two already corrected cheap-screen assertions.
All historical screen constants and result bundles remain unchanged. The Foster
notice was moved verbatim to adjacent [NOTICE.md](NOTICE.md), restoring the global
notices file to its accepted-base bytes. SOURCE_NOTES already contains the full
attribution, article/wrapper license distinction and modification notice.
The Grudeva contract, its tests and all bound historical inputs are unchanged.
These narrow integration corrections leave every reviewed scientific file,
canonical pixel input, numerical output and comparison image byte-identical;
unaffected independent review evidence is reused. No CI selector, timeout,
scientific threshold or source role was changed. Final-head local and hosted
outcomes are recorded in the draft PR description. The corrected affected selection
passed **168 tests / 20 skips** in 25.75 s; full Ruff, Insight verification and
whitespace checks passed before submission.

## Producers and preservation

Ran existing producers: `tools/build_available_data_register.py`,
`tools/build_local_corpus_family_index.py`, `tools/build_espresso_data_guide.py`,
`python -m puckworks.paper3.corpus --splice`, `tools/claim_binding_audit.py --write`,
then `python -m puckworks.insights write`. The new manifest row changes the
corpus count 128→129; existing producers refresh its manuscript projections and
claim-binding fingerprint. No generated section was hand-edited. Insight source
commit hashes account for wider generated diffs; all existing candidate IDs are
preserved and unscored. A narrow existing-producer exclusion prevents the new
retrospective radial row from inheriting false CALIBRATED_FROM edges by family
name. It adds no Foundry/assurance framework or physical measurement capability.

All 128 existing MANIFEST rows and their bytes are preserved; one row is appended.
The five previous Foster CSVs, model/default/parameter files, validation code,
post-saturation result bundle, workflows/selectors/timeouts and package dependency
configuration are unchanged. The active Foster card/provenance now distinguish
radial center variation, extent compatibility, transition sharpness, binary
saturation and full-model validity. Historical entries remain historical.

EWP local HEAD remains `78cbd59c751393cddfe539e4c69e43a224329bca`; working tree
was clean at intake. Only read operations were used, including reading current
remote-main records by exact object ID. Its lock SHA-256 is
`52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`, identical
at local HEAD and the accepted EWP main. No EWP write, execution, dependency
adoption, physics change, merge, author contact, purchase or successor occurred.

## Durable output identities

| artifact | SHA-256 |
|---|---|
| canonical JSON | `12735f86c5cb98a950c9d38e83ebbfbe12613f05c3419b6d83d26ad36e500b31` |
| canonical CSV | `2d3eddaa3b3e978a446539fa91955ddf84e3bc3f45e7be767e2a9a9dafc47168` |
| analysis module | `d4d76b84c80a47ac62081b1a26b5befd8228117416bcc74b68fba4bb4dcd4ed8` |
| scan_results.json | `c116ad4be2889f9b40f3b9b2a92c3b29866d264f0254a8176d3882ed2f0f9e98` |
| scan_results.csv | `35cf633f0b818e39be28825c93299f3ddd10f72a8c8fbc015598de03e4fee302` |
| summary.json | `0fc7b399e9889bf41282b6e95a25357b7228919d814e89db4814b109f8f94518` |
| comparison.png | `2f65d4bc0873c1ffc0192b3bb43fe50d0ce9c42619107845efccbaeda4ccd2f3` |
