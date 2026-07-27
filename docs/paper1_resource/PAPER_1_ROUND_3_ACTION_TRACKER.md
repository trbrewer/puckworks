# Paper 1 / Paper A — third-review action tracker

**Source review:** [`PAPER_1_DETAILED_REVIEW_ROUND_3_20260726.md`](PAPER_1_DETAILED_REVIEW_ROUND_3_20260726.md)
(26 Jul 2026; verdict **major revision before submission**).
**Actioned:** 2026-07-27. **Canonical source:** `docs/PAPER_A_DRAFT.md`; the JFE conversion is a
synced view.

Owner-types: **[mech]** repo-mechanical · **[author]** author judgment · **[analysis]** new
computation · **[external]** needs an artefact we cannot produce (DOI, indexed search, third-party
reproduction).

---

## Verification of the review's load-bearing claims

Every claim below was checked against the tree before acting on it. **All confirmed.**

| Review claim | Check | Result |
|---|---|---|
| Reference generator reports 33 resolved / 0 unmatched while ≥6 cited works are omitted (P0-2) | ran `tools/paper_a_references.py`; audited the six named works | **CONFIRMED** — 33/0; Raue 2009, Transtrum 2015, Tönsing 2014, Kuhn 2017, Sánchez-López 2014/2016 all present in `references.bib`, all absent from the list |
| Rendered list exposes raw TeX, literal `others`, `--` page ranges | read the generated block | **CONFIRMED** — `K\"unsch`, `Bia\las`, `\L`, `others` ×20, `1890--1900` |
| Package carries the retired title, a stale 237-word abstract, 7 keywords, 5 repo-facing Highlights, obsolete status (P0-1) | diffed manuscript vs package | **CONFIRMED** — every row of the review's table |
| `PAPER_A_P0-5_RESULTS.md` says 18-point grid; JSON says 29 (MC3) | read both | **CONFIRMED** — and every archived fraction is an exact 29th (0.759 = 22/29, 0.345 = 10/29); none is a multiple of 1/18 |
| Manifest is dirty, stale, not matched to head (P0-5) | read `paper_a_manifest.json` | **CONFIRMED** — `git_dirty=true`, `bundle_matches_head=false`, `release_fresh=false`, `timestamp_utc=null` |
| Consistency gate passes despite all of the above (P0-6) | ran it | **CONFIRMED** — 5 banned + 6 required phrases, nothing else |
| Supplement does not exist (P0-3) | listed `docs/submission/` | **CONFIRMED** |
| 16 of 18 panel × objective near-optimal sets reach a boundary | recomputed from the JSON | **CONFIRMED exactly**; the objective minimum is interior in 13 of 18 |

---

## P0 — submission blockers

| ID | Item | Owner | Status |
|---|---|---|---|
| **P0-1** | Synchronize every submission-facing representation | [mech] | ✅ **DONE.** `docs/submission/paper_a_front_matter.yaml` is now the single source; `tools/paper_a_front_matter.py` generates the manuscript title block, the canonical draft's title, the package, the Highlights file and a **new generated cover letter**. `tests/test_paper_a_front_matter.py` asserts exact title/abstract/keyword equality and fails on drift. The package's embedded cover-letter draft — which opened by submitting the retired title — is replaced by a pointer. |
| **P0-2** | Fix the reference generator's false clean pass | [mech] | ✅ **DONE.** Detector rewritten: Unicode-aware author tokens, `et\s+al` spanning line breaks, grouped years (`2011, 2015`). 33 → **39 references**, all six named works included. Renderer now maps TeX accents to real characters (Künsch, Białas Ł., Tönsing, Sánchez-López), renders `others` as "et al.", and converts `--` to en dashes. **Additional defect found and fixed beyond the review:** the matcher accepted ANY author, so two 2016 entries listing Villaverde meant `"Villaverde et al. (2016)"` resolved correctly only by accident of `.bib` ordering — now lead-author-only, with ambiguity reported rather than silently bound. Twelve citation-form tests plus a deletion test over **every** cited entry. |
| **P0-3** | Build the promised supplement | [mech]/[analysis] | ◑ **PARTIAL.** `tools/paper_a_supplement.py` generates `PAPER_A_JFE_SUPPLEMENT.md` from the archived bundles: Note S1 (identifiability), Note S2 (the Table 7 dimensional audit), **Table S1** (all 6 panels × 3 objectives × 4 thresholds, with `k/29` denominators), **Table S5** (external panel under both losses). **Table S3** now carries the completed endpoint propagation (see P0-4). **S6 (numerical convergence) remains an explicit NOT-YET-AVAILABLE stub** naming exactly what must be run, and recording that the convergence currently reported in the main text is of a *different* quantity. The consistency gate fails if the article cites an item the supplement does not define. |
| **P0-4** | Propagate 38/40/42 mL through the transfer-versus-null benchmark | [analysis] | ✅ **DONE — RUN AND ARCHIVED.** `transfer_skill_vs_baselines` is now parameterised by `v_target` (it previously baked in 40 mL, which is *why* the sweep could not be propagated), and `endpoint_propagation_benchmark()` runs the complete 9-step procedure at each endpoint. Result archived in `PAPER_A_ENDPOINT_PROPAGATION.json`, reported as **Table 4a** in the manuscript and **Table S3** in the supplement. **See the finding below** — it is not a clean robustness result. |
| **P0-5** | Clean, fresh reproducibility manifest and release | [external] | ⏭ **BLOCKED.** Requires a clean checkout, a full slow rerun, a tag and an archival DOI. `tools/paper_a_consistency.py submission` enumerates all four manifest failures plus the metadata gaps and exits non-zero; it will pass only when the release is genuinely fresh. |
| **P0-6** | Expand the consistency gate beyond phrase checking | [mech] | ✅ **DONE.** Rewritten as a **submission contract** composing the specialised checkers (front matter, citations, cross-references) and adding placeholder/process-language bans, supplementary-target resolution, grid-record agreement and figure-label policy. Two modes: `verify` (CI, currently **green**) and `submission` (release gate, correctly **red** — 16 blockers). `tests/test_paper_a_submission_contract.py` injects each drift class the review found and requires the contract to catch it. |
| **P0-7** | Complete submission metadata and the novelty record | [author]/[external] | ◑ **TRACKED, NOT RESOLVABLE HERE.** All 11 fields are explicit nulls in the front-matter YAML and enumerated by `--check-submission-ready`; declarations are generated from them rather than scattered as `[insert …]`. **The novelty sentence has been hedged** — it no longer says "following the documented search", which read as final while the indexed search was still owed. |

## Major comments

| ID | Item | Status |
|---|---|---|
| **MC1** | Abstract too long; "interior minimum" reads as universal | ✅ 313 → **238 words**; the interior-minimum statement is restricted to the illustrative caffeine panel and the cross-panel summary reports **16 of 18** boundary-reaching cases (verified). "95 % resampling interval" → "clustered percentile range". |
| **MC2** | Exact level factorization vs approximate compensation | ✅ §3.2 rewritten: the factorisation is stated as **exact** and design-independent; the valley is attributed to near-collinear sensitivity directions under this design, not to approximate linearity. |
| **MC3** | 18-vs-29-point record | ✅ Note corrected to 29 with the evidence (every fraction an exact 29th); counts printed as `k/29`; contract test binds JSON, note and manuscript. |
| **MC4** | Model/numerical specification | ✅ **DONE.** `d32` defined (Sauter mean, its two-class formula, grind-specific, 84 µm centre value — **read from the implementation, not guessed**); Wilke–Chang unit convention stated (g mol⁻¹, K, Pa s, cm³ mol⁻¹ → m² s⁻¹); normalised RMSE defined as a percentage of the **mean observation**; the stencil and boundary treatment stated. **Spatial-mesh and solver-tolerance convergence RUN** — see below. |
| **MC5** | Separate the resampling estimands | ✅ New **Table 5**: six quantities by resampling unit, whether the fit is repeated, held-out fraction, estimand, point estimate, range and inferential status. Terminology standardised; the OOB refit interval is explicitly **not** an interval for the −0.36 pp difference. |
| **MC6** | External panel must show the weaker loss | ◑ Prose and Table S5 now report both losses and read the panel at the weaker one; "always constrains the rate" → "retains weak, loss-dependent rate structure". ⏭ The **main figure panel** still plots MAPE only. |
| **MC7** | Lead Table 7 with non-commensurability | ✅ Reversed. The section now opens with "not demonstrably commensurate", states that **no quantitative rate intersection is claimed**, gives the 4.8–16.3 mg mL⁻¹ range, and demotes the numerical intersection to the supplement. Standing name: "orthogonal same-campaign inventory assay". |
| **MC8** | Remove repository scaffolding | ✅ Registry IDs → author–year; 23 producer/function names → method descriptions; file paths → supplementary references; gap "G6" and the revision-history sentence removed; **all HTML anchors stripped from the article**; data-availability replaced with a release statement. |
| **MC9** | Moderate categorical claims | ✅ "almost always" → "commonly"; "decided by temporal shape" → a design-based statement naming other routes; dataset roles made precise in the conclusions. |
| **MC10** | "mass-transfer-rate multiplier" | ✅ Defined at first use with the explicit warning that it is not a first-order rate constant; "rate multiplier" thereafter. |
| **MC11** | Make the benchmark contract explicit | ✅ Five-point contract stated, headline moved to the **first paragraph** (8.23 / 8.59 / −0.36 pp / 50 of 108), and the point that beating one constant would not prove mechanism made explicit. |

## The endpoint propagation result (P0-4)

| endpoint | model | null | difference | primary clustered range | model worse on |
|---|---:|---:|---:|---:|---:|
| 38 mL | 8.17 % | 8.59 % | −0.421 pp | **[−0.79, −0.03] — excludes zero** | 51 of 108 |
| **40 mL** | **8.23 %** | **8.59 %** | **−0.361 pp** | **[−0.72, +0.03] — includes zero** | **50 of 108** |
| 42 mL | 8.20 % | 8.59 % | −0.392 pp | [−0.78, +0.01] — includes zero | 49 of 108 |

The review's decision rule had three branches. **The result lands between the first two**, so both
halves are reported:

- The **effect size is stable**: −0.36 to −0.42 pp, a spread of 0.06 pp. That is an order of
  magnitude smaller than the ≈5 pp movement the same endpoint range produces in the *blind*
  optimal-grind residual — the contrast the review correctly insisted was a different estimand.
  Here both predictors are re-derived at each endpoint, so a shift common to both cancels.
- The **inferential reading is not endpoint-invariant**: at 38 mL the primary clustered percentile
  range excludes zero, with an upper bound of −0.03 pp. The manuscript now says so explicitly.

One check worth recording: the level-only null is **8.59 % at all three endpoints**. That is not a
coincidence but a correctness check — the constant is fitted to measured concentrations, which do
not depend on where the solver terminates. Had the baseline moved too, the sweep would not have
been doing what the analysis claims. A test asserts it.

## The PDE convergence study (MC4.4)

**Why it was initially skipped, and why that reasoning was wrong.** It was recorded as "not run"
and folded into slow-PDE work. That does not hold up: the endpoint propagation is also a slow PDE
campaign and was run. The real cause was that MC4.4 sits under the review's P1 list and was
deprioritised without testing the assumption that it was expensive.

Testing it showed the assumption was wrong in a useful way. A single solve is **0.17 s** at the
production `NZ = 200`, so the whole-cup and early/middle/late fraction comparisons were seconds of
work and could have been delivered immediately. What is genuinely expensive is the part the review
cares most about — the **profile minimum location and range ratio** — which needs an 18-rate ×
9-condition sweep per cell, and at `NZ = 400` the BDF Jacobian carries 1202 states. The full 3 × 3
sweep took ~35 minutes.

**Result: the production configuration is converged, by a wide margin.**

| quantity | worst-case relative deviation across all 9 cells |
|---|---:|
| whole-cup concentration | 0.0004 % |
| late fraction (the most discretization-sensitive sub-interval) | 0.0013 % |
| profile range ratio | 0.0204 % |
| **location of the profiled minimum** | **identical (0.884) in all nine cells** |

The identifiability conclusion is therefore not a numerical artefact: the broad, boundary-reaching
near-optimal set is a property of the design and the data, not of the mesh or the tolerance. Even
100 axial nodes reproduces the 400-node answer, so the production grid of 200 is already well
beyond what these outputs need.

Two things recorded rather than smoothed over:

- **scipy emitted 6 `RuntimeWarning`s** during the sweep, all from `num_jac` — its *numerical*
  Jacobian estimator. The solver supplies a sparsity pattern but not an analytic Jacobian. They are
  archived, not suppressed. They do not affect the values: nine cells agreeing to ≤ 0.021 % with an
  invariant profile minimum is not what a corrupted integration looks like.
- **The stencil attribution is not cited.** The implementation's docstring credits Carver & Hinds
  (1978), but that is not on the source card and its bibliographic metadata was not verified here,
  so it does not enter the manuscript or the reference list. The citation gate caught the attempt
  the moment I made it. The scheme is described by name instead, which is what MC4.4 asked for; an
  author who wants the attribution should verify the reference.

The study is a **read-only diagnostic**: `NZ` and the solver tolerances are patched in a context
manager rather than parameterised, so no gated component is refactored.

## Found by a later re-check (all fixed)

Three defects in my own earlier work, caught by re-checking rather than by re-running the same
gates. Two are worth recording because of *how* they hid.

**The abstract's final sentence was never updated.** After the endpoint sweep I reported that I had
replaced "The cross-grind benchmark remains conditional on the endpoint proxy" with the actual
result. I had not: the edit used `str.replace()` **without an assert**, the anchor did not match the
wrapped YAML, and it silently did nothing. The front-matter drift check still reported *0 drifted
renderings* — correctly, because the manuscript and the single source agreed. **They agreed on the
wrong text.** A consistency gate verifies consistency, not correctness; nothing in the repository
could have caught this, and only re-reading the rendered abstract did. The sentence now states the
finding, and the abstract is 234 words.

**A `textwrap` rewrite corrupted two compound words.** Re-emitting the YAML block scalar split
`mass-transfer-rate` and `solute-by-variety` on their hyphens; a folded block scalar rejoins with a
space, so the abstract read "mass- transfer-rate". Fixed with `break_on_hyphens=False`, and the
repair is now asserted.

**One of my own edit scripts wrote before its verification failed.** It performed the substitution,
wrote the file, and only then hit a failing round-trip assert — so a partial state landed on disk.
The final version builds the candidate in memory, verifies the round-trip *and* that every other
field is byte-identical, and only then writes.

## Deliberate divergence from the review

**HTML anchors.** The review's hygiene gate is "no HTML anchor comments". `tools/paper_a_xref.py`
used those anchors to catch a stale cross-reference that names a *real but wrong* section — the
exact MC9 defect of the previous round. Deleting the mechanism outright would have discarded that
check. The policy is therefore **split by file**: the submitted article is anchor-free and its
references are resolved against its own heading table plus a pinned `CANONICAL_NUMBERS` map; the
canonical working draft — which already carries an explicit strip-before-submission repository
note — keeps the annotated form and the full check.

## Not actioned

- **20–30 % main-text word reduction** (MC8) — an author judgment about voice, not a correctness fix.
- **Figure redesigns** beyond removing embedded numbers — MC6's two-loss panel, the Figure 3 forest
  plot, and the S1–S4 changes need design decisions.
- **P2 items 22–26** — new baselines, a mass-based endpoint operator, prospective design work.
