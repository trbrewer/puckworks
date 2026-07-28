# Paper B2 — round-4 review action tracker

Review: [`PAPER_B2_FOURTH_DETAILED_REVIEW_2026-07-27.md`](PAPER_B2_FOURTH_DETAILED_REVIEW_2026-07-27.md)
(against `352dacd`). Branch `review-round-4-2026-07-27`.

| # | Item | Status |
|---|---|---|
| **6.1 / P0.1** | Resolve the exact duplicate `12-8-6` / `12-8-6_alt` | ✅ **DONE, and the provenance question is answered rather than deferred.** The review listed three possibilities; the source archive decides it. `measurements_time_dependent/12-8-6.txt` is an **exact line-for-line prefix** of `12-8-6_alt.txt`, which carries 42 further samples recorded after the shot ended (mass runs to −175 g as the scale is cleared). Two distinct brews cannot agree sample-for-sample on 1447 consecutive raw acquisitions: this is **one physical brew stored twice** (case 1), and the 100 s truncation makes the processed pair exactly equal. Declared in `puckworks.data.WASZ_TRACE_ALIASES`; the shot-level analyses now score **56** distinct trajectories, not 57, and 13 bar has **six** shots. Three gates added, all mutation-tested. |
| **6.2 / P0** | The Foster null is not "machine-only" and does not have "no evolving bed" | ✅ **DONE.** The card confirms sharp-front infiltration into an initially dry bed, so the wetted fraction and hydraulic path length **do** evolve. Abstract, introduction, contribution statement, §3.1 heading, §5.1, Figure 1 caption, alt text and the public claims now say **machine–wetting** and **no extraction-driven bed change**, naming what is actually held fixed: the saturated-bed constitutive law. Both retired terms are in the semantic audit, so they cannot return. |
| **6.3 / P0** | Correct the cross-pressure estimand in the manuscript, not only in code | ✅ **DONE.** New **Table 3c** gives all four estimands with what each one is; Table 3a is retitled **"pressure-level MEAN-CURVE reconstruction error"**. The claim that the shot-count-weighted mean-curve average answers "what happens to a randomly drawn shot" is withdrawn in the text that made it. The values the review computed independently are reproduced exactly after deduplication: shot means 0.523 / 0.364 / 0.547, pooled 0.552 / 0.394 / 0.619. |
| **6.4 / P0** | Figure 4 reasserts the interpretation the Results withdraw | ✅ **DONE, across every surface the acceptance criterion names.** Panel (c) plots the **spectral index k** with the frequency resolution stated (1/80 Hz), and the period appears only as a parenthetical window property. Caption, figure title, panel label, docstring, alt text and the exported CSV **column names** (`peak_bin_index_k`, `frequency_resolution_hz`, `power_in_slowest_quarter_of_available_bins`) all changed; PNG/PDF/SVG re-rendered. The analysis code comment that asserted "drifting rather than oscillating" is corrected at source. |
| **6.5 / P0** | The reproducibility record is not tied to the reviewed manuscript | ⚠️ **PARTIAL — blocked on the release.** The bundle was recomputed, all **156** claims verify, and the manifest regenerates cleanly; but `git_dirty=true` and `release_fresh=false` by construction while the work is uncommitted. A frozen release must be built from a clean checkout at the final manuscript commit. |
| **6.6 / P0** | Fix the rank-change field and add a definition-level test | ✅ **DONE.** `len(set(winners)) - 1` is replaced by adjacent-transition counting. The producer, the bundle, the standalone results JSON, the manuscript, the **figure** (which now reads the producer's field instead of recomputing its own) and the manifest all carry **3** from one definition. The regression test uses the review's re-entrant sequence `A, A, B, B, A`, for which the old expression gives 1 and the correct answer is 2. |

## What the round exposed beyond the review

- **The exported source data was a reader-visible surface nobody audited.** `dominant_period_s`
  survived as a CSV column name after the manuscript had withdrawn the reading, because the
  semantic audit's surface list covered prose and code but not exports. It does now.
- **Regenerating a stale artifact exposes what it was hiding.** `ALT_TEXT.md` had drifted from its
  generator; regenerating it immediately surfaced a *pre-existing* P0.5 violation that had been
  masked by the staleness. A stale generated file is not merely out of date — it suppresses the
  guards that would fire on its current content.
- **A prohibited phrase that wraps across a line was invisible.** Every space in the audit's
  patterns was a literal space, so the Figure 4 caption's `Dominant residual\nperiod` — a claim the
  manuscript had already withdrawn in its own §5.4 — passed. Pattern spaces now compile to `\s+`.
  This is the third scoping bug found in that guard by mutation-testing it against itself.

- **The duplicate reaches one place that is deliberately *not* deduplicated.** The equilibrium
  static fit averages per pressure, so its 13-bar mean is over seven records covering six brews.
  It is left that way on purpose: that fit *reproduces the source's published calibration*
  (P_c 12.394 vs 12.39), and the source computed theirs over both copies, so deduplicating would
  break the reproduction that makes it a verification rather than an independent fit. The price is
  measured rather than assumed — dropping the alias moves P_c by **+2.4e-4 bar** and Q_c by
  **−5.2e-4 g s⁻¹**, three orders below the reported precision — and a test pins that bound. The
  duplicated brew is also never a held-out unit (the leave-one-out runs over 9-bar shots only), so
  no held-out estimate is contaminated by its twin remaining in the calibration.

## Standing lesson, restated

A verification manifest can confirm a number against a bundle while both carry the same wrong
definition — which is exactly how `n_rank_changes` survived. **Value-matching cannot catch a
definition error;** only a test that states the definition independently can.
