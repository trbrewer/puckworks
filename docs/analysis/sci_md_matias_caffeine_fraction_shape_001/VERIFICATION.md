# Verification and handoff

Actual implementation base: `49cf29104ede7b20eae0cf48b71caa56ce1c34a0`, live
Puckworks main at intake; PR #363 was already merged. Work used an isolated
branch/worktree and preserved the existing main checkout and other local work.
No numerical Matias intake was found in the committed tree or bounded configured
external-source search. The accessible collection contains a byte-identical
pinned paper PDF; it is not an absent/exhausted collection.

Tested scientific packet identity:
`fdb531f2806114feec1dab388a0e6751e1a18b07c49086127bdfc7d96cffc2e8`.
[artifact_sha256.json](artifact_sha256.json) defines this SHA256 over sorted
relative-path/file-hash pairs, including code, tests, source geometry, recovery
scripts, review and numerical/figure outputs. It excludes itself and this
operational record, avoiding a self-referential commit identity. The final
submitted commit is recorded in the draft PR closeout, rather than embedding its
own unknown hash. [review.json](review.json) separately binds its inspected code,
source and output identities. No timestamps or machine paths enter numerical JSON/CSV.

## Offline reproduction and independent method

From a source checkout with the existing optional figures extra:

```bash
python -m puckworks.analysis.matias2023_caffeine_fraction_shape \
  --output /tmp/matias-fraction-shape --plot
python -m pytest -q tests/test_matias_caffeine_fraction_shape.py
python docs/analysis/sci_md_matias_caffeine_fraction_shape_001/review_packet.py \
  --output /tmp/matias-independent.json
```

The offline calculation needs neither network, original PDFs, private mounts,
pypdf nor PyMuPDF. It uses committed literal geometry and shared calibration.
The CLI generates PLAN, SOURCE_NOTES, VizSpec, RESULT, results JSON, five CSVs
and the optional comparison image. This operational verification and the original
source-overlay/review receipts remain separate from newly reproduced scientific
outputs. Reproduction here matched all **11 generated files byte for byte**, including
the plot. No cross-version Matplotlib image-byte guarantee is claimed.

Optional source authentication (original paper.pdf/source.tar in SOURCE_DIR):

```bash
python tools/recover_matias2023_figure.py --source-dir SOURCE_DIR \
  --output /tmp/matias-geometry.json
python docs/analysis/sci_md_matias_caffeine_fraction_shape_001/review_packet.py \
  --source-dir SOURCE_DIR --output /tmp/matias-source-review.json
```

The first source tool uses PyMuPDF; the second uses pypdf and independently
reparses raw streams. All paper/archive/member identities match PLAN. The paper
embeds byte-identical drawing streams; source/member render and annotated
source_overlay.png were visually inspected, including F02 hidden endpoints and
F10 clipping. [REVIEW.md](REVIEW.md) records one same-session source/mathematical
independent-method review, not a separate human audit. Exact 3-variable LP vertex
enumeration reproduces every decisive objective without calling the producer;
all source witness and lower-certificate constraints pass.

## Local checks

- **31 scientific contract tests pass.** Constant/geometric zero cases;
  independently bounded non-geometric positive case; increasing beta=0 boundary;
  exact shift invariance; valid-band widening; interior excursion; full ordered
  pair count; independently specified HiGHS LP; direct original-strip/intercept
  intersection and interval residuals; finite-bin integral including k=0;
  covered/clipped/missing support; nonpositive/nonfinite rejection; P endpoint
  quantifiers/empty inner; directed transform enclosure; and synthetic aggregation
  curvature without a source rescue fit.
- **117 affected checks pass in 3.64 s**, including the 31 task checks, data
  register/guide/family-index checks, Insight Foundry checks and Paper 3 corpus.
- Loaded registry: **28 components, 66 PASS, one pre-existing
  ACKNOWLEDGED_EXCEPTION**. No model/validation changes or evidence promotion.
- Configured Ruff (`puckworks/ tests/`, also tools and the review script) and
  mypy's 19 configured modules pass. `git diff --check` passes.
- Registry artifacts, Paper 3 build/availability/corpus, Paper A/B2/3 claim
  coverage, lateral-coupling artifacts, evidence-graph reconciliation/verification,
  Insight verification, status truth, local-corpus coverage and README governance
  pass. Two Paper 3 archives are byte-identical and self-verification passes.
- Existing producers regenerated available-data register, family-index binding,
  data guide, Insight snapshots and Paper 3 corpus denominators/count prose.
  The historical 39-family external snapshot is unchanged; the new packaged
  Matias row is reconciled outside that dated inventory. Insight IDs/candidate
  identities are unchanged; the broad diff includes current-base provenance
  refresh and one extra species-concentration dataset, not new discovery machinery.

The full local quick lane completed in **1,529.87 s** with **7,279 passed,
36 skipped, 73 deselected and three failures**. The three construction-time
failures were the global-notice hash, stale claim-binding audit, and missing
README reference for the newly manifested Matias card. The first two pass their
fresh targeted rerun (**2 passed in 12.61 s**); the README bibliography was then
updated with the authenticated journal citation and card/source link; its complete
affected suite passes **54 tests in 41.97 s**. This original broad run is not relabelled a pass. Unchanged
science is reused, and required hosted CI checks the submitted head. No selector,
assertion, coverage floor, timeout or acceptance threshold was changed.

## Resolved construction-time QA

The initial optional plot attempt encountered a system Matplotlib/NumPy ABI
mismatch; upgrading Matplotlib inside the isolated task environment resolved it.
A nonessential system Axes3D-import warning does not affect these 2D figures.
The source-recovery TeX-path assertion initially omitted the literal `./` in
`graphicspath`; correcting it to the authenticated source string resolved the
assertion before any geometry intake was accepted. No source coordinates changed.

Adding a MANIFEST row made generated corpus counts stale; the existing corpus
producer/splicer repaired them. An expanded affected-test invocation used a
nonexistent test filename and ran no tests; a subsequent invocation overlapped
the final card edit/regeneration and reported 2 stale-snapshot failures / 115 passes.
The final serialized 117-check run passes. The broad construction-time run also caught downstream metadata failures: adding a notice to the global THIRD_PARTY_NOTICES file violated an unchanged historical Grudeva hash, and the claim-binding audit was stale after the corpus-count splice. The global file was restored exactly; Matias attribution/CC BY 4.0 remain in its packaged SOURCE_NOTES/PROVENANCE and MANIFEST. The claim-binding audit was regenerated with its existing producer. Both affected tests were rerun successfully. The README-reference failure was corrected by adding the Matias citation; the complete local-run disposition is recorded above. Initial citation drafts exceeded the unchanged 52,000-byte README cap (52,315 and 52,003 bytes); concise citation wording and two shortened contributor instructions reduce it to 51,988 bytes. Evidence-strength wording and the cap remain unchanged. The final bound/reference/link checks pass (3/3); the complete final README rerun passes **54 tests in 41.97 s**. These are disclosed construction-time
QA failures, not scientific exclusions or reasons to weaken checks. Exact science
and the independent review remain unchanged after bounded presentation/metadata
corrections.

Environment: Python 3.12.3, NumPy 2.5.4, SciPy 1.18.1, pytest 9.1.1,
Matplotlib 3.11.2; optional source tools PyMuPDF 2.0 and pypdf 6.21.2.
No PDF-parser/rendering dependency was added to the scientific package.

## Preserved authority and hosted state

Unchanged base subtree identities:

| Scope | Git tree |
|---|---|
| puckworks/models | 344bd8b2a70408f359d67e9aca5a62e34723d1b8 |
| puckworks/validation | 2c4d0d19cd86c82d610b6aab408f869e51cf8d94 |
| puckworks/data/khamitova2020 | 0e85dca03c4963e4fe4afb4c160b40a6fd2f8340 |
| accepted Khamitova analysis bundle | a4e865b8afd376b65ff529a11bf53e75c4b91b07 |

EWP remote main: `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.
EWP dependency pin: `fc61c4670ec7bf801e40bb391aab16048b8da26b`.
Lock SHA256: `52b15ceef87d503a3e77c6e3c1cbed785185d2dde0b79647e5fbe309395d2f10`.
Both EWP checkouts inspected remain unchanged/read-only. Its analytical
NO_EXPERIMENTAL_VALIDATION reference was not rerun or reinterpreted.

Hosted CI is **NOT_YET_RUN_AT_PACKET_CREATION**; this immutable evidence packet
precedes its submission. Final actual head and observed workflow results are
reported on the draft PR and in the handoff. Live branch runs are available at
[GitHub Actions](https://github.com/trbrewer/puckworks/actions?query=branch%3Aresearch%2Fsci-md-matias-caffeine-fraction-shape-001).
A pending/running/failed workflow is never described here as passed by inference.
Leave OPEN / DRAFT / UNMERGED with auto-merge disabled.

Scientific disposition: complete source support and exact positive N/G/P_outer
minima; P_outer/P_inner bound every declared endpoint realization. G/P are
conservative correlated-geometry relaxations. Unequal-volume robustness and
physical validation are NOT_ESTABLISHED; practical adequacy is unadjudicated.
No production adoption or automatic successor. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
