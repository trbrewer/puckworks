# Verification and delivery record

Scientific disposition: NOMINAL_READING_MISMATCH for the three declared fixed
scenarios; physical decision unresolved. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Software verification and hosted CI are separate from that scientific result.

## Reproduction and focused checks

Local environment: Python 3.12.3, NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2;
optional source extraction used PyMuPDF 2.0. The numerical producer uses exact
rational arithmetic for input transformations, KC and reading-bound ratios;
JSON retains exact rational bounds as well as floating presentations. Geometry
uses double precision without intermediate display rounding.

```sh
python -m puckworks.analysis.corrochano2017_aspect_ratio --output /tmp/aspect-ratio --plot
cmp /tmp/aspect-ratio/RESULT.json docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001/RESULT.json
cmp /tmp/aspect-ratio/readings.csv puckworks/data/romancorrochano2017/fig6_9_aspect_ratio/readings.csv
cmp /tmp/aspect-ratio/reconstruction.svg docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001/reconstruction.svg
python -m pytest -q tests/test_corrochano2017_aspect_ratio.py
```

Numerical CSV/JSON and SVG reproduced byte-for-byte. Optional exact-PDF native
path extraction also reproduced source_coordinates.csv and source_paths.json
byte-for-byte after verifying the source SHA. The original reconstructed plot was
visually checked. Source pages, raw PDFs, images and overlays remain outside Git.

**18 focused tests passed**, including material/consolidation domains, SI
contract rejection, independent simplified KC algebra, effective particle-volume
conservation, reciprocal chamber exchange, exact equal-consolidation cancellation,
symbolic coarse cancellation, pure geometry versus permeability, shared-axis
scale cancellation and baseline dependence, marginal outer-bound semantics,
supported Darcy-length cancellation at tight relative tolerance, all aliases,
four-condition coverage, original native path identity/deduplication and replay.
No test hard-codes the owner's orientation estimates as an oracle.

The final affected selection below passed **119/119 tests in 31.17 s** after all
corrections and regeneration. All 20 scientific files hashed by the independent
reviewer still matched the reviewed identities before commit.

The broader affected selection ran **118 passed / one failed**. The failure was
the old pressure-flow integration test's assertion that Corrochano had exactly
one dataset scope. It was corrected to require the two named, separately
qualified scopes. The correction plus this task's full focused module passed
**19 tests**; the later duplicate-error-path source check passed all **18 tests**
again. Historical pressure-flow observations, producer and claims are unchanged.
Affected selection:

```sh
python -m pytest -q tests/test_corrochano2017_aspect_ratio.py tests/test_corrochano2017_pressure_flow.py tests/test_available_data_register.py tests/test_local_corpus_family_index.py tests/test_espresso_data_guide.py tests/test_paper3_corpus.py tests/test_paper3_manuscript_consistency.py tests/test_paper_a_model_contract.py
```

Initial development also caught an incorrectly named PDF Quad corner before any
result was emitted: endpoint ordering failed. Using minimum page y for the top
resolved the path-winding issue; independent fill/outline and source-path checks
cover it. This was a software extraction defect, not a scientific outcome.

## Repository integration

Passed: ruff over puckworks/tests and the new extraction tool; 66 registry gates
PASS and one pre-existing ACKNOWLEDGED_EXCEPTION; registry artifacts, Paper3
build, availability and corpus verification; Paper A/B2/3 claim coverage;
lateral-coupling generated verification; evidence-graph generated verification
and strict `paper3`/`all` scope reconciliation; insight verification; local-corpus
coverage; canonical status verification. Two Paper3 archives were byte-identical
and self-verified (159 members). These are working-tree archives on the intake
base, not release archives or new scientific evidence.

Existing producers regenerated manifest-dependent data/register/family/guide,
corpus counts, claim-binding and insight projections. Manifest records increase
120→121; campaign count remains 46. Generated insight changes are discovery
bookkeeping, not triage or successor authorization. Source-commit stamps in those
projections identify their generating base. No new framework or gate is added.

The full local quick selection began on the intake worktree while implementation
continued. Its final result is recorded below; it is not an untouched clean-base
run or a final-commit run. New-module and corrected integration tests are also
covered separately above. Final hosted checks bind the committed candidate.

Full selection: `pytest -q -m 'not slow and not live and not release and not gpu
and not external_data'` completed with **6958 passed, 36 skipped, 72 deselected,
three failed** in 1403.86 s. All three failures were the corpus/manuscript
manifest-count projections read before their regeneration during implementation:
`test_generated_artifacts_and_the_manuscript_block_are_fresh`,
`test_manifest_record_count_matches_manifest_csv`, and
`test_the_manifest_count_is_not_described_as_validation_datasets`.
The current generated projections and all three tests pass in the affected
selection; no scientific output or gate was weakened. This is an in-progress QA
failure followed by a corrected focused verification, not a clean full-suite
pass. Required hosted quick jobs exercise the exact committed candidate.

## Independent scientific review

[REVIEW.md](REVIEW.md) records the one independent reviewer, directly inspected
source and file hashes, independent calculations and disposition. The review
identified duplicated error paths that the first provenance wording had missed.
Both native identities were already retained and the chosen coordinates were
correct. Documentation and duplicate checks were corrected within this task;
the producer, input coordinates and numerical result did not change. No repeated
review of unchanged evidence or new scientific stage was created.

## Hosted status and repository boundaries

Active **Protect main** ruleset 19053322 was read directly at intake and before
publication. It requires `quick (3.10)`, `quick (3.12)`, `verify-generated`,
`paper3-scope-strict`, `all-scope-strict`, with strict up-to-date checks. No
absence-of-checks inference was made from legacy branch protection. The PR and
final handoff retain actual check URLs/conclusions and exact head (or GitHub's
recorded synthetic merge revision). This pre-push record does not claim hosted
checks already passed.

Puckworks intake/main base: `f7bd1686854db990e7c8950ca6e9bd7dd8073bac`.
Read-only EWP context: `aace2cc6b6c2a393d2dbfb0274104192ca6c7203`;
its worktree remained clean and its production Puckworks lock unchanged.
The task uses one draft PR, to remain open/unmerged with auto-merge disabled.
No rescue fit, production adoption or successor follows this bounded result.
