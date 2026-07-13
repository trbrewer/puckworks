# TB / PI / VENUE handoff execution summary

**Repository:** `trbrewer/puckworks`
**Repository baseline inspected:** `main` at `b4de0d971555dcfcf13b24cab5da6e5b8eab9cf4` (2026-07-13)
**Work date:** 2026-07-13
**Scope:** best-effort execution of `docs/HANDOFF_TB_PI_VENUE.md` without repository write access

## Executive result

This handoff produced a repo-applicable patch plus a complete source bundle. It closes or materially advances the unblocked parts of the release, uncertainty-intake, literature-verification, venue-conversion, and vector-figure tasks. It does **not** claim completion of actions that require repository credentials, licensed bibliographic databases, source workbooks that were not retrievable, an exact release environment, or new physical experiments.

| task | status | result |
|---|---|---|
| TB-1 frozen tags + pinned environment | **partial; implementation ready** | Exact direct numerical versions recorded; environment gate, deterministic external release packager, runbook, checksums, and tests added. No Git tags, DOI deposit, complete transitive lock, or full production release build was created. |
| TB-2 replicate uncertainty | **partial; new source data recovered** | All 66 Angeloni conditions and all 132 published total-solids/lipid mean–RSD pairs were transcribed and independently checked. Canonical schemas, intake templates, validator, and weighted-analysis plan added. Named-solute replicate/RSD values and Schmieder raw workbooks remain absent, so weighted manuscript reruns were not performed. |
| TB-3 bundle recompute | **not executed** | The available runner does not match the recorded release stack and the full repository/test data were not locally available. A clean, detached-worktree release tool now performs the recompute once run in the exact environment. |
| TB-4 second rig / measured flow | **not executable here** | Requires correspondence, new measured-flow data, or a new experiment. No synthetic substitute was introduced. |
| PI-1 indexed search | **partial** | Two flagged DOI records were verified and reconciled; an open-web evidence seed, verification log, and bounded novelty language were added. Scopus/Web of Science execution, exports, deduplication, screening, and snowballing remain PI-owned. |
| VENUE-1 manuscript conversion | **partial; venue packages produced** | Paper A JFE title/abstract/keywords/highlights/declarations/cover-letter scaffold and a full editorial conversion draft were produced. Paper B APS DFD 2026 abstract was fitted to the official limits. Paper A still requires scientific/editorial cleanup, final references, author metadata, PI-1, TB-2, and a release DOI. |
| VENUE-2 vector figures + captions | **code and caption work complete; full render pending** | Shared save helper now emits PNG, SVG, and PDF; deterministic vector metadata and a colour-vision-deficiency-safe palette were added. Eight Paper A and five Paper B self-contained captions and regression tests were produced. A complete repository render remains to be run in the exact environment. |

## Deliverables

### 1. Release and reproducibility

Added:

- `docs/reproducibility/paper_release_environment.json`
- `requirements-paper-release.lock`
- `tools/check_release_environment.py`
- `tools/prepare_paper_release.py`
- `docs/reproducibility/RELEASE_RUNBOOK.md`
- `tests/test_release_helpers.py`

The recorded direct stack is:

```text
Python      3.13.13
NumPy       2.5.1
SciPy       1.18.0
Matplotlib  3.11.0
```

The existing strict release workflow has a causal self-reference: a generated tracked bundle stamped with commit `H` becomes one commit stale as soon as that bundle is committed at `H+1`. The new packager treats the Git tag as the immutable **source commit** and creates the generated submission object outside the source worktree. It:

1. requires a clean checkout;
2. verifies the exact direct environment;
3. creates a detached worktree at `HEAD`;
4. computes bundles, figures, source data, and manifests into external staging;
5. runs the existing strict verifiers against the staged bundles;
6. asserts `HEAD == manifest.source_commit == bundle.source_commit` and a clean worktree;
7. overlays generated products onto `git archive HEAD`;
8. writes deterministic `tar.gz` archives, SHA-256 sidecars, and release-provenance JSON.

A synthetic end-to-end integration test of this protocol produced both Paper A and Paper B archives, verified both sidecars, and confirmed generated artifacts were present in the extracted archive. A defect found during that test—Python bytecode dirtying the detached worktree—was fixed by setting `PYTHONDONTWRITEBYTECODE=1`.

**Important limitation:** `requirements-paper-release.lock` is an exact **direct-dependency** pin file, not a full transitive resolution. The runbook requires archiving `pip freeze --all`, a generated `uv.lock`, or an immutable container digest from the actual release environment before the release is considered archival-grade.

### 2. Angeloni uncertainty recovery and data intake

Added:

- `puckworks/data/angeloni2023/angeloni2023_total_solids_lipids_rsd.csv`
- `puckworks/data/angeloni2023/angeloni2023_uncertainty_summary.csv`
- `puckworks/data/angeloni2023/replicate_uncertainty_template.csv`
- `puckworks/data/angeloni2023/MANIFEST_UNCERTAINTY.md`
- `puckworks/data/schmieder2023/replicate_measurements_template.csv`
- `puckworks/data/measurement_uncertainty_summary_template.csv`
- `docs/data_intake/ANGELONI_TRANSCRIPTION_AUDIT.md`
- `docs/data_intake/REPLICATE_UNCERTAINTY_INTAKE.md`
- `tools/validate_replicate_uncertainty.py`
- `tests/test_uncertainty_intake.py`

The Angeloni author-deposited PDF was downloaded and hashed. Tables 1–3 were parsed and checked programmatically:

- 66 sample-to-condition mappings;
- 66 total-solids mean/RSD pairs;
- 66 total-lipid mean/RSD pairs;
- 132 reconstructed standard deviations using `SD = |mean| × RSD / 100`;
- 132 canonical, validator-accepted uncertainty rows for downstream weighting;
- zero transcription mismatches.

The article’s “almost in duplicate” statement is retained as a qualified `n_reported=2`, not treated as a guarantee for every cell. The A21 lipid RSD printed as `0.0%` is explicitly flagged as rounded and must receive a predeclared resolution/variance floor rather than infinite statistical weight.

This recovery **does not** supply raw replicates or condition/analyte-specific uncertainty for caffeine, trigonelline, 3-CQA, 5-CQA, or 3,5-diCQA. The article reports only global analyte RSD ranges for those tables. Consequently, no solute-specific weighted Paper A fit or model–baseline uncertainty comparison was claimed. Schmieder’s supplementary/raw workbooks also remain required for the requested fraction-to-cup uncertainty propagation.

### 3. Literature and novelty

Modified:

- `docs/literature_search/references.bib`
- `docs/PAPER_B_RELATED_WORK.md`

Added:

- `docs/literature_search/DOI_VERIFICATION_2026-07-13.md`
- `docs/literature_search/OPEN_WEB_VERIFICATION_LOG.csv`
- `docs/literature_search/EVIDENCE_MATRIX_OPEN_WEB_SEED.csv`
- `docs/literature_search/NOVELTY_WORDING_PROVISIONAL.md`

Closed bibliographic flags:

- `lee2023`: W. T. Lee, A. Smith, and A. Arshad, “Uneven extraction in coffee brewing,” *Physics of Fluids* 35, 054110 (2023), DOI `10.1063/5.0138998`.
- `waszkiewicz2026`: R. Waszkiewicz et al., “Under pressure: Poroelastic regulation of flow in espresso brewing,” *Physics of Fluids* 38, 063113 (2026), DOI `10.1063/5.0319611`.

The novelty text is deliberately bounded: these papers are applied espresso case studies using established inference concepts, and absence claims are limited to the final screened set. Nothing in the output represents the licensed Scopus/Web of Science search as completed.

### 4. Venue conversion

Added:

- `docs/submission/PAPER_A_JFE_PACKAGE.md`
- `docs/submission/PAPER_A_JFE_HIGHLIGHTS.txt`
- `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`
- `docs/submission/PAPER_B_APS_DFD_2026_ABSTRACT.md`
- `docs/submission/VENUE_CONVERSION_STATUS.md`
- `tools/validate_submission_limits.py`
- `tests/test_submission_limits.py`

Paper A package checks:

- JFE abstract: 237 words (limit 250);
- keywords: 7 (allowed 1–7);
- highlights: 5, with character counts 68, 72, 70, 73, and 63 (limit 85 each);
- declarations and cover-letter core included without inventing authors, funding, conflicts, or AI-use facts.

Paper B APS DFD checks:

- title: 112 characters (limit 300);
- abstract body: 1,874 characters;
- funding line: 70 characters;
- body plus funding: 1,944 characters (limit 2,000).

The Paper A manuscript file is a **full editorial conversion draft**, not an upload-ready manuscript. It intentionally preserves enough source detail for scientific review, but still contains internal cross-references, development/audit language, code-facing provenance, and an unresolved reference-list step. The package checklist identifies these as required editorial removals. It also requires PI-1, TB-2, author metadata, final declarations, final citation audit, and a frozen release DOI before submission.

### 5. Vector figures and captions

Modified:

- `puckworks/figures.py`
- `puckworks/figures_paper_a.py`

Added:

- `docs/figures/PAPER_A_CAPTIONS.md`
- `docs/figures/PAPER_B_CAPTIONS.md`
- `tests/test_figure_exports.py`

Every call through the common `_save` helper retains the requested PNG and additionally emits same-stem SVG and PDF files. The change is backward-compatible: the original path remains the return value. SVG element IDs and vector metadata are stabilized, and PDF/SVG outputs were byte-identical across repeated controlled renders. The palette was changed to an Okabe–Ito-derived set, while figures continue to use markers, line styles, direct labels, and text tokens so colour is not the sole encoding.

The caption files include sample sizes, data split, endpoint operator, fitted/profiler parameters, uncertainty meaning, and evidence tier. Actual production figures were not all rerendered because the exact stack and full repository were unavailable; the code path and smoke tests are complete.

## Validation performed

Final selected test suite:

```text
10 passed
```

Covered:

- deterministic PNG/SVG/PDF export and repeated-render byte stability;
- release-manifest contract, deterministic archive helper, and no-bytecode worktree protection;
- Angeloni table completeness and reconstructed-SD consistency;
- canonical uncertainty validation and zero-variance safeguards;
- JFE and APS submission-limit checks.

Additional checks:

- all added Python files compiled with `py_compile`;
- synthetic end-to-end release preparation generated and verified two archives;
- patch passed `git diff --check`;
- patch applied cleanly to the downloaded baseline subset;
- delivery-file SHA-256 manifest was generated.

The exact release environment gate correctly failed on the execution runner:

```text
expected              observed
Python 3.13.13         Python 3.13.5
NumPy 2.5.1            NumPy 2.3.5
SciPy 1.18.0           SciPy 1.17.0
Matplotlib 3.11.0      Matplotlib 3.10.8
```

This is a successful negative test of the gate, but it prevents a valid production bundle recompute on this runner.

## Work not completed and why

1. **No tags or Zenodo DOI.** These require repository and archive credentials.
2. **No production Paper A/Paper B bundle recompute.** The exact environment was unavailable, direct repository cloning/archive download was blocked in the execution environment, and only the necessary source subset could be reconstructed.
3. **No complete 139-test run.** The full repository was not locally available. The added/modified focused tests pass.
4. **No weighted named-solute reruns.** Required Angeloni solute-specific replicate/RSD data and Schmieder raw/supplementary workbooks were unavailable. Assigning global RSD maxima to individual observations would be scientifically invalid.
5. **No Scopus/Web of Science archive.** Licensed access and PI screening are required.
6. **No TB-4 experiment.** This requires measured flow traces, correspondence, or a second-rig campaign.
7. **No final Paper A upload file.** It still needs scientific review, editorial compression, reference generation, author/declaration metadata, post-TB-2 numerical reconciliation, and a release DOI.

## Recommended follow-on sequence

1. Apply the patch on a branch based on `b4de0d971555dcfcf13b24cab5da6e5b8eab9cf4` or review/resolve any newer changes.
2. Run the full repository test suite, then render all figures and inspect SVG/PDF text/layout manually.
3. Create Python 3.13.13 with the recorded package versions; resolve and archive the complete transitive environment.
4. Run `tools/prepare_paper_release.py --paper all` from a clean committed tree and inspect both release archives and manifests.
5. Obtain the Angeloni named-solute replicate/RSD table and Schmieder raw workbooks; populate the templates and run weighted, robust, and run-level bootstrap sensitivity analyses.
6. Execute and archive the licensed PI-1 search; reconcile the final included set and bibliography; then narrow or retain the provisional novelty wording.
7. Update numerical prose from the frozen reruns, clean the JFE manuscript, insert authors/declarations/references, approve the APS abstract, and deposit the release archives before tagging and DOI assignment.
8. Treat TB-4 as a separate experiment/correspondence decision; do not delay the software/literature/venue work solely for it.

## Safe application

Use the delivery patch from the repository root:

```bash
git switch -c handoff-tb-pi-venue-2026-07-13
git apply --check puckworks_handoff_2026-07-13.patch
git apply puckworks_handoff_2026-07-13.patch
python -m pytest -q
```

Review the patch before committing. The patch was generated from a reconstructed subset of the public repository, so a newer `main` may require ordinary conflict resolution even though no unseen files are deleted.
