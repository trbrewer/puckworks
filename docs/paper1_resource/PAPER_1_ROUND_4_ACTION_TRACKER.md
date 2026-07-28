# Paper 1 — round-4 review action tracker

Review: [`PAPER_1_DETAILED_REVIEW_ROUND_4_20260727.md`](PAPER_1_DETAILED_REVIEW_ROUND_4_20260727.md)
(against `352dacd`). Branch `review-round-4-2026-07-27`.

| # | Item | Status |
|---|---|---|
| **P0-1** | Reconcile the completed endpoint analysis everywhere | ✅ **DONE.** §2.4 said the O-refit → C/F transfer estimand was "not evaluated here" while §4 reported it at all three endpoints and the package listed it as outstanding. §2.4 now distinguishes the two estimands and explains *why* they are reported apart — an endpoint shift common to both predictors cancels in the model-minus-null contrast (0.06 pp spread) even when it moves the blind residual (≈ 5 pp). The package's outstanding list is corrected. Repository search for `not evaluated here` returns nothing. |
| **P0-2** | Audit the Wilke–Chang closure against the source | ✅ **DONE.** Archived as `PAPER_A_DIFFUSIVITY_CLOSURE_AUDIT.json`: the card specifies `M_i`, the implementation supplies **solute** molecular weights where the standard correlation uses the **solvent**'s. What remains unresolved is stated rather than resolved by assertion. The numerical check shows the choice is absorbed by the fitted rate — minimum MAPE 2.84 % either way, range ratio 1.43 vs 1.45 — because `h ∝ A·D^(2/3)`, so a D-rescale by `r` is a k-rescale by `r^(2/3)`. Three tests bind it. |
| **P0-3** | Remove the nonexistent Supplementary Table S2 | ✅ **DONE.** The promise is **withdrawn**, not relocated: an intersection computed on an arbitrary volume basis invites exactly the quantitative reading the paragraph rejects. **The checker that passed it is fixed** — it compared only the *number*, so "Table S2" was satisfied by "Note S2". It is now typed (`(kind, number)` pairs) and also fails on non-sequential numbering, which is the condition that made the gap easy to miss. |
| **P0-4** | Correct the Jacobian description; narrow the convergence claim | ✅ **DONE (via the review's second option).** "Analytic Jacobian sparsity pattern" contradicted the record's own warning field and is now "a supplied Jacobian sparsity pattern and a numerically estimated Jacobian", in the manuscripts, the archived record and the producer. The review offered two ways to fix the scope problem — add worst-case panels **or** explicitly retain the representative-panel limitation — and this takes the second: the manuscript now states that the 5-CQA panel, the highest-rate cells, the external time-varying-flow trajectory and the positive-control profiles **have not been swept**. A 5-CQA sweep was attempted and did not complete (that panel is far stiffer; ~40 min for caffeine and still running after ~80 min for 5-CQA), so it is reported as unrun rather than implied. The convergence profile's objective and observable are now stated, including that it is a **relative** objective and therefore not expected to place its minimum where the main text's sum-of-squares panels do. **On the "warnings do not affect the results" argument:** it no longer rests on cross-cell agreement, which two configurations exercising the same numerical path could satisfy while both were wrong. `pannusch2024.solver` now records per-solve termination status, state finiteness, concentration positivity and volume/mass monotonicity, and the sweep was **re-run** with that instrumentation: across all **1458** profiled solves every integration terminated successfully, every state was finite, volume and mass were monotone, and concentrations stayed physical (worst interior liquid +4.5e-07, worst solid −4.5e-09 — an upwind undershoot, not a failed integration). The re-run **reproduced every previously archived cell value exactly**, so the numbers are confirmed rather than replaced, and the six warnings resolve to two unique messages under default filtering. The inlet node is excluded from the positivity check because it carries the Dirichlet condition on a zeroed copy, so its stored value is unconstrained — including it made every solve look unphysical. |
| **P0-5** | Rebuild the supplement as a journal SI | ✅ **DONE.** Rewritten as two documents: the submitted SI (Methods S1–S2, Note S1, Tables S1–S5, Figures S1–S4 — sequential within each type, figures physically bundled into `docs/submission/figures/`, no repository paths, producer names or implementation-status prose), and `PAPER_A_SI_PROVENANCE.md`, which receives everything stripped out. The malformed Table S3 header is fixed. Adjudication prose in capitals was fixed **at source**, in the archived records' `reading` fields, so it cannot regenerate. |
| **P0-6** | Regenerate the reproducibility manifest from the release candidate | ⚠️ **PARTIAL — blocked on the release.** Every generated artifact is current and the manifest regenerates cleanly, but a manifest bound to a *frozen* release requires the release to exist. See P0-7. |
| **P0-7** | Novelty, authorship, declarations, cover-letter assertions | ✅ **DONE (the part that is ours).** The cover letter no longer asserts "all authors have approved the submission" or "we declare no competing interests" while `authors` and `competing_interests` are null. It states only what the front matter supports and prints a **"this letter is not ready to send"** block naming each withheld declaration and why. `--check-submission-ready` reports them separately from ordinary blanks. The remaining fields need the authors, not the repository. |
| **P0-8** | Figure 2 data scope and the caption package | ✅ **DONE.** Both panels are Arabica; the caption said "nine O conditions for each coffee variety (18 condition means per solute)", doubling the apparent scope. Caption, figure suptitle and both panel titles now name the variety, and a test reads the varieties **out of the producer source** and requires the caption to match — including the condition-mean count. Figure S3's "independent inventory assay" is now "orthogonal same-campaign". The rendered figures carry no embedded figure number (the reviewer's contact sheet was stale); re-verified visually. |

## What the round exposed beyond the review

- **The supplementary-reference checker was type-blind.** Fixing the phantom Table S2 mattered less
  than fixing the check that passed it. The same defect shape — comparing an identifier while
  discarding its type — is what let Paper 1's citation audit alias two 2016 Villaverde entries in
  round 3.
- **`overstat\b` never matched anything.** Paper B2's semantic-audit withdrawal regex listed
  `overstat` with a word boundary, so `overstates`, `overstated` and `overstating` all failed to
  match. The alternative had been dead since it was written and nothing noticed, because a
  never-matching allowance only shows up when something legitimate gets flagged.
- **The table-caption detector measured caption *length*, not presence.** A three-line lookback
  could not see a caption that wrapped to four lines, so a correctly captioned table read as
  uncaptioned. Now paragraph-scoped.
- **The SI-reference check ran in one direction only.** It verified that everything the article
  cites exists in the supplement, never the converse — so **seven of the twelve** supplementary
  items (Figures S1–S4, Methods S2, Tables S1 and S4) were defined and physically bundled while no
  reader was ever pointed at them, and the SI's own header asserted "Every item here is cited by
  the main text". Both documents agreed and both were wrong, which is why nothing caught it. All
  seven are now cited at the point they support, and the check is bidirectional.
- **A committed manuscript carried regex debris.** The canonical draft contained
  `§4<!--sec:result3-->.<!--sec:result3-->.]*` — a duplicated section anchor and a stray `]*` from
  a substitution applied as literal text. It predates this round and survived every gate, because
  each one asks whether the *content* is right and this is well-formedness. Now guarded.

## Standing lesson, restated

The gates catch inconsistencies, not consistent falsehoods, and **a guard's passing result says
nothing until it has been mutation-tested.** Every guard added this round was driven with the
defect re-injected: the caption-scope guard against three mutations, the cover-letter guard against
three, the convergence and supplementary-numbering guards against their own prior states.
