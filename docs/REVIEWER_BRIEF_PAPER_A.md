# Reviewer brief — Paper A (inventory–kinetics identifiability, espresso case study)

*For an external reviewer of `docs/PAPER_A_DRAFT.md` (and the editorial conversion
draft `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`). Prepared 2026-07-13.*

## How to use this brief

This is a **disclosure register**, not a "do not flag" list. Paper A has been
through four detailed review rounds; the limitations below are already **known and
scoped**. The most useful review does three things:

1. **Assess whether each disclosure is adequate and correctly labelled** — is a
   caveat we call "descriptive" actually being leaned on as if it were validated?
   Is a scope we call "conditional" wider than we admit?
2. **Flag anything genuinely new** — an error, an unsupported claim, or a
   limitation not listed here.
3. **Tell us if any disclosed limitation actually undermines a headline claim**
   rather than merely bounding it.

Re-listing the items in §2 as fresh findings is lower value; testing whether our
handling of them is honest and sufficient is high value.

Authoritative sources this brief summarizes (reviewer may audit): the prior review
`docs/PAPER_A_FOURTH_DETAILED_REVIEW.md`; `docs/REVIEW_BACKLOG.md` (Paper A
section, internal IDs); `docs/ROADMAP.md` §7.1 change log; `docs/HANDOFF_TB_PI_VENUE.md`.

## 1. Maximum defensible claim per result (calibrate against this scope)

The paper is a **methods/limitations case study**, not a validated predictive
model. The strongest each result supports:

- **Identifiability.** Under the tested single-grind, whole-cup observation map,
  inventory and rate are **weakly separated**: the profiled objective has an
  interior numerical minimum, but the 10 %-tolerance set is broad and
  **right-censored** at the upper rate boundary. This is practical weak
  localization, *not* absence of a minimum, and *not* a confidence region (no
  likelihood/noise model).
- **Transfer.** A frozen optimal-grind calibration gives coarse/fine absolute
  MAPE ≈ 3–18 %, but its incremental skill over an O-trained **level-only
  constant** is small (≈ 0.4 pp macro; the mechanism is *worse* on 50 of 108
  held-out points). The defensible statement is "acceptable endpoint error adds
  little skill beyond a transferred level," **not** "transfers reasonably."
- **Joint multigrind fit.** In-sample shared-parameter **compatibility**, with a
  small gain over a shared level-only model. **Not** predictive transfer.
- **Observation operator.** Fraction-resolved scoring localizes rate more strongly
  than integrated aggregates — under the tested operators, in-sample.
- **External Waszkiewicz.** Temporal-shape **objective localization**, shallow and
  high-error (min MAPE ≈ 27 %); the single integrated cup is flat **by
  construction** after profiling one multiplicative level. **Not** an
  absolute-concentration validation.

## 2. Known limitations already disclosed (please assess adequacy, don't re-list)

| Known limitation | Status | Why it is open | Where disclosed / evidence |
|---|---|---|---|
| Solute-specific replicate/RSD weighting (heteroscedastic objective) not performed | **PARTIAL / BLOCKED-EXTERNAL** | condition-level Angeloni total-solids/lipid RSD recovered; solute-specific replicate tables + Schmieder raw workbooks not retrievable | `data/angeloni2023/MANIFEST_UNCERTAINTY.md`; backlog A-MAJ22/A2-08/A4-25 |
| Continuous / grid-converged profile-set → condition-wise C/F prediction envelopes | UNBLOCKED-LARGE, deferred | current set is a finite 10 %-MAPE grid subset; aggregate errors only | backlog A4-07; review §6.12/§7.13 |
| Full endpoint×density transfer estimand (refit O + transfer C/F per endpoint) | UNBLOCKED-LARGE, deferred | current sweep tests the **blind** O-grind residual, not the frozen O→C/F transfer | backlog A4-04; review §6.8 |
| Hessian sensitivity table (FD step, grids, scaling, evaluation point) | deferred | condition number reported at one discretization | backlog A4-17; review §6.15 |
| Discrepancy controls + off-grid same-model sim shown in figures | PARTIAL | controls are in the result bundle + tests, not all plotted | backlog A4-27/28; review §6.38/§6.40 |
| Fig 3/4 tidy source-data export + Fig 4 baseline/envelope redesign | deferred | Fig 4 already carries a level-only baseline panel; envelopes/export owed | backlog A4-10/11 |
| Vector (SVG/PDF) figures | **DONE-as-code** (full production re-render owed) | export path + colour-safe palette + captions added; exact-env render pending | ROADMAP §7.1 (VENUE-2); `docs/figures/PAPER_A_CAPTIONS.md` |
| Journal manuscript conversion (remove internal IDs/function names, Methods equations, references, declarations) | VENUE, in progress | JFE conversion **draft** exists; editorial cleanup + author metadata owed | `docs/submission/PAPER_A_JFE_MANUSCRIPT.md`; `VENUE_CONVERSION_STATUS.md` |
| Systematic Scopus/WoS novelty search | PI-owned | no licensed DB access; open-web seed only | `docs/literature_search/SEARCH_PROTOCOL.md`, `NOVELTY_WORDING_PROVISIONAL.md` |
| Clean tagged release + exact-env production bundle recompute + archival transitive lock | DEFERRED to RC / TB | release packager + env gate + direct-dep lock built; ~30 min PDE recompute + tag/DOI owed | `tools/prepare_paper_release.py`; `RELEASE_RUNBOOK.md`; backlog A4-15 |
| Second-rig / measured per-condition flow (vs the inferred pressure→flow map) | BLOCKED (no data) | needs new measurement/correspondence; transfer is conditional on inferred flow | review §7.7; backlog A4-23/30 |

## 3. Already corrected in prior rounds — please do NOT re-raise as new

These were flagged in earlier reviews and are **fixed** in the current tree (the
4th review was partly stale on several):

- **5th-review (A-01..A-45) P0/P1 fixes now in-tree:** the Waszkiewicz observed-bin
  operator uses an **isotonic monotone-mass reconstruction** (no negative bin/weight,
  mass-balanced — A-03); the primary blind headline is the **named-solute macro-MAPE
  26.3 %** with the TDS proxy (22.7 %) reported separately (A-07); **all
  mechanistic-transfer wording removed** ("endpoint stability, not identified-mechanism
  transfer"; 8.2 % vs 8.6 % null, worse 50/108 — A-08); finite-grid condition-wise
  ranges are stated **reported** vs continuous **deferred** (A-09); the identifiability
  metric is a **profile range ratio** (localization, not identification — A-28); Table 7
  is a **conditional intersection band** 0.60–1.76, not a CI (A-16); the comparator
  ladder is **non-nested in-sample** (A-17); `flow_map_sensitivity_transfer` is now in
  the bundle (A-05); Fig 7 uses NA (not zero) bars and Fig 4 labels its tolerance-set
  ranges (A-23/A-32). **Still genuinely open** (assess as such, don't re-flag as fixed):
  the full endpoint×density *transfer* estimand (A-18), profile grid/threshold
  convergence of prediction ranges (A-15), all-group flow-map sensitivity (A-19),
  design-aware paired-skill uncertainty (A-20), and a clean commit-coherent release
  (A-01/04) — all logged in `REVIEW_BACKLOG.md`.

- Round-before-aggregate precision: refit / joint / geometry / flow and (latest)
  per-condition / endpoint now aggregate from full-precision arrays.
- SSE-vs-MAPE objective labelled consistently; the inverse-Hessian statistic is a
  **local-curvature coupling**, not a correlation.
- The **baseline-relative skill** analysis (`transfer_skill_vs_baselines`) exists
  and is the basis of the transfer wording above.
- Fig 8's "a level rescale cannot remove" title **withdrawn** (a per-group level
  can remove group offsets); Fig 7 "trajectory" → cross-condition correlation (n=9).
- Figure-count contract synchronized (eight figures: six main + two diagnostics).
- "matched 40 g" → "40 mL endpoint proxy"; the single-cup "no rate information"
  carries the **algebraic-by-construction** qualifier.
- Interior-optimum vs open/right-censored tolerance-set wording harmonized.

---

*Cross-referenced from `docs/REVIEW_BACKLOG.md`, `docs/ONBOARDING.md`, and the
Paper A drafts. Companion: `docs/REVIEWER_BRIEF_PAPER_B.md`.*
