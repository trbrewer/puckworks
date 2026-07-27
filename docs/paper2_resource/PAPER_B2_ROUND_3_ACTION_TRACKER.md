# Paper B2 — third-review action tracker

**Source review:** [`PAPER_B2_THIRD_DETAILED_REVIEW_2026-07-26.md`](PAPER_B2_THIRD_DETAILED_REVIEW_2026-07-26.md)
(26 Jul 2026; verdict **major revision before external journal submission**).
**Actioned:** 2026-07-27.

This reviewer performed an independent numerical audit. **Every number in it that we re-derived
reproduced exactly**, which is recorded below because it changes how much of the review can be
acted on directly rather than re-litigated.

---

## Independent re-derivation of the reviewer's audit

| Reviewer value | Our re-derivation | Match |
|---|---|---|
| Leave-in shot-to-full-mean RMSE 0.149151 | 0.149151 | ✅ exact |
| Other-four empirical-template RMSE 0.186439 | 0.186439 | ✅ exact |
| Leave-one-out inflation is exactly `n/(n-1)` = 1.25 | 1.25, identity holds shot by shot | ✅ exact |
| Mean pointwise between-shot SD 0.153950 | 0.153950 | ✅ exact |
| Leave-segment-out at 5 segments: Φ 0.1579 / spline 0.2330 / linear 0.0705 / cubic 0.1355 | identical to 4 d.p. | ✅ exact |
| The full 4/5/6/8/10/16-segment sensitivity table | identical to 4 d.p. across all six rows | ✅ exact |
| Cross-pressure: equal-pressure macro static 0.5239 / Φ 0.3345 | 0.5239 / 0.3345 | ✅ exact |
| Cross-pressure: mean of 57 individual-shot RMSEs 0.5271 / 0.3632 | 0.5271 / 0.3632 | ✅ exact |
| Cross-pressure: pooled shot × time 0.5567 / 0.3927 | 0.5567 / 0.3927 | ✅ exact |

We additionally computed what the review asked for but did not have: **RC-3b at the shot level**
(0.5400 mean individual-shot RMSE), and the segment sensitivity extended to a verdict — **Φ(t) is
not the best interior-gap predictor at *any* tested segment count**, which is stronger than the
review's own summary.

---

## P0 — submission blockers

| ID | Item | Status |
|---|---|---|
| **P0.1** | Withdraw the 0.149 "noise floor" | ✅ **DONE, end to end.** `shot_level_noise_floor()` is **removed** and raises rather than aliasing — a silent alias would let the wrong reading survive in un-updated callers. `shot_level_dispersion()` returns both scales, named: `leave_in_dispersion_rmse_g_per_s` (0.1492) and `other_four_template_rmse_g_per_s` (0.1864), plus the exact `n/(n-1)` identity as a checked field. The two resolvability *verdicts* — `phi_vs_cubic_resolvable` and `difference_exceeds_shot_noise_floor` — are **withdrawn**, not renamed: neither scale is a significance criterion. Manuscript, manifest claim labels, figure text and five tests updated. |
| **P0.2** | Correct the LOSO asymmetry | ✅ **DONE.** "like-for-like" deleted from Methods and from the producer comment. Every comparison now states that the spline is **fully held out** while Φ(t) is **partly target-informed** (its dissolved-mass channel cannot be withheld because the TDS replicates were never shot-matched). The five paired differences are reported — **2 vs 3, SD 0.026, exact sign-flip p = 0.8125** — where previously only the mean appeared. The spline is named correctly as a **same-condition empirical template**: it differs from the raw other-four mean by 0.0004 g s⁻¹. |
| **P0.3** | Remove the interval-holdout headline | ✅ **DONE.** Removed from the abstract, results, discussion and conclusions and demoted to exploratory. New producer `leave_segment_out_sensitivity()` **evidences the withdrawal** rather than asserting it, and three of its values are registered claims. |
| **P0.4** | Genuine per-shot cross-pressure performance | ✅ **DONE.** The docstring claiming the shot-weighted mean answers "what happens to a randomly drawn shot" is corrected — `RMSE(mean curve) ≠ mean[RMSE(shots)]`. `per_shot_cross_pressure()` scores **all 57 included shots** against **all three branches** and returns **four separately named estimands**. The 60-brews-vs-57-included discrepancy is stated, with the exclusion provenance recorded as *incomplete* rather than reconstructed. |
| **P0.5** | Reframe the spectral result | ✅ **DONE.** "drift, not oscillation", the "dominant period" language and the "not a monotone trend" claim are all **explicitly withdrawn in the text**, with the reason: on an 80-point, 1 s series, 80 s and 40 s *are* the first two nonzero Fourier periods. The data field is renamed `dominant_period_s` → `peak_bin_period_s` so the estimand is honest at source; figure titles, axis labels, alt text and manifest claim labels follow. What survives is the defensible part: coherent low-frequency lack of fit in every branch. |
| **P0.6** | Clean Paper B2 release | ⏭ **BLOCKED** — needs a clean tree, a tag and an archival DOI. |
| **P0.7** | Repository-wide semantic audit | ✅ **DONE.** `tests/test_paper_b2_semantic_audit.py` executes the review's own `rg` acceptance test across manuscript, figure code, both analysis modules, the bundle builder and the alt text. A term may appear **only** on a line whose surrounding sentence withdraws it — so the paper can record what it retracted without re-asserting it. The positive half asserts the corrected vocabulary is present. Non-vacuity is tested in both directions. |

## P1 items actioned

- **P1.1** "prespecified" → "fixed-architecture" for the spline (the field is now
  `architecture_fixed_across_folds`). The audit pattern is **deliberately narrow**: "prespecified"
  remains a legitimate parameter-access level in the dependency graph, meaning "declared before
  running", which the review did not object to.
- **P1.3** The post-hoc "7–11 bar band" and "upper-pressure regime" are replaced by the observed
  fact — Φ(t) lowest at **7, 8, 9 and 11 bar**, RC-3b at 1, 2 and 13, static at 3.5–6 — with an
  explicit refusal to infer a boundary near 7 bar.
- **§7.10** "temporal dynamics are required" → the model-relative form, with the statement that the
  tested static branches do not exhaust static spatial heterogeneity, unmeasured boundary
  conditions, preprocessing artefacts or latent machine states.
- **Abstract and conclusions** replaced along the review's lines, without the two withdrawn claims.

## Found by a later re-check, after the first pass (all fixed)

A second sweep across all three papers found four items the first B2 pass had missed. They are
recorded because three of them are the *same class of defect* the review is about — a summary that
contradicts the detail beneath it.

| Item | Review ref | Status |
|---|---|---|
| §5.2 said lag-1 ACF was "approximately 0.99 in every branch" and mean Durbin–Watson "approximately 0.01", while the per-branch values **in the same section** are 0.904–0.969 and a mean of 0.031 | MC13, §7.7 | ✅ Corrected to the real range and mean, and — more importantly — the cross-branch summaries are now **producer fields** (`lag1_acf_min/max`, `durbin_watson_min/max`, `mean_durbin_watson`) with registered claims, so a hand-written gloss can no longer drift from the table beneath it |
| Two Φ(t) target-access cross-references pointed at **§4.3 "Window sensitivity"** instead of §5.3c, the actual parameter-provenance section | §7.7 | ✅ Repointed to §5.3c |
| §2.3 said the shot-level analysis was "the natural next analysis (Limitations, §7)" — it is now **present** (§5.2a) and Limitations is **§8** | §7.4 | ✅ Both corrected |
| The figure module's docstring claimed the bundle was checked against **122 claims** (the manifest had 124 at review time, and 146 after this work), and asserted that "figures therefore cannot disagree with the claims" | MC13, §7.11 | ✅ The count is **removed rather than updated** — a restated count is a thing that drifts — and the guarantee narrowed to what is true: a plotted *value* cannot disagree with a verified one, but a figure can reproduce a value exactly while mislabelling its estimand. This repository has done both, so labels are checked separately by the semantic audit |

The evidence manifest was also stale (124 registered claims on disk vs 146 in the builder); it has
been regenerated and **all 146 verify**.

## The semantic audit was vacuous, three times over (found by mutation-testing it)

The audit reported "16 passed" from the moment it was written, and I reported P0.7 as done on that
basis. Mutation-testing it — reinstating each withdrawn claim and checking the audit fails —
showed it was **substantially weaker than its green result implied**. Three independent scoping
defects, each of which silently exempted real violations:

1. **A ±2-line context window.** These files are paragraph-per-line, so that was a ±2-*paragraph*
   window: 2181 characters containing five different withdrawal markers in the case that exposed
   it. Injecting *"The shot-to-shot noise floor is 0.149 g s⁻¹ and sets the resolution limit"* into
   the manuscript **did not fail the audit**.
2. **The banned phrase contained its own exemption.** "drift, **not** oscillation" carries a
   negation inside it, so the disavowal search always matched. Reasserting it passed. The matched
   text is now excised from the scope before the search.
3. **A disavowal in a neighbouring artefact.** A figure title reading *"Dominant residual period"*
   was excused by the adjacent axis label reading *"not a measured timescale"*. In source, each
   string literal is its own artefact; the scope is now confined to the enclosing literal, found by
   tokenising rather than regex-matching quotes so docstrings behave correctly.

The rule is now: a disavowal must be in the **same sentence** (prose) or the **same string
literal** (source), within 120 characters, and may not be the banned phrase itself. Nine
reinstatement mutations are caught, including all five the review named. Four regression tests pin
the failure modes — including the two *over*-corrections, so the guard cannot be tightened into
uselessness either.

The general lesson is uncomfortable and worth stating: **a guard's passing result says nothing
until the guard has been mutation-tested.** This one was green while missing the exact defects it
was written for.

## Not actioned

- **P1.6 / §7.12 methodological references** — the review is right that seven references are too few
  for a methods paper; choosing them is an author task.
- **P1.7** moving the 110–120 s equilibrium autopsy to a supplement, and **P1.8** the expanded
  supplement plan — both need the supplement itself, which does not yet exist for B2.
- **P2 editorial items** — abstract length, section renumbering, `Q_{\text{cub}}`, figure/table
  duplication.
- **Figure regeneration** — the figure *code* is corrected, but the rendered PNG/PDF/SVG artefacts
  under `docs/figures/paper_b2/` have not been re-emitted.
