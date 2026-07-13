# Reviewer brief — Paper B (limits of mechanism discrimination, espresso flow/bed-dynamics)

*For an external reviewer of `docs/PAPER_B_DRAFT.md`. Prepared 2026-07-13.*

## How to use this brief

This is a **disclosure register**, not a "do not flag" list. Paper B has been
through five detailed review rounds; the limitations below are already **known and
scoped**. The most useful review does three things:

1. **Assess whether each disclosure is adequate and correctly labelled** — e.g. is
   a result we call "exploratory" or "reconstruction score" being used elsewhere as
   if it were validated or a proven instability?
2. **Flag anything genuinely new** — an error, an unsupported claim, or a
   limitation not listed here.
3. **Tell us if any disclosed limitation actually undermines a headline claim**
   rather than merely bounding it.

Re-listing §2 items as fresh findings is lower value; testing whether our handling
is honest and sufficient is high value. Note especially: **Result 3 (N-tube) is
explicitly an exploratory simulation**, not a stability result — please review it
as such rather than against the standard for a validated instability claim.

Authoritative sources this brief summarizes: the prior review
`docs/PAPER_B_FIFTH_DETAILED_REVIEW.md`; `docs/REVIEW_BACKLOG.md` (Paper B section,
internal IDs); `docs/ROADMAP.md` §7.1 change log; `docs/HANDOFF_TB_PI_VENUE.md`.

## 1. Maximum defensible claim per result (calibrate against this scope)

The central thesis is deliberately about **limits**: within the datasets and the
implemented model set, integrated observables can show model capacity,
incompatibility, and a need for temporal flexibility while remaining **insufficient
to identify a unique physical mechanism**. Per result:

- **Result 1 (RSM).** A stable **conditional** grind vertex near 1.74 — conditional
  on the selected seven-term achieved-predictor form, one campaign's design
  support, and reconstructed cup endpoints. **Not** proof the physical response has
  an interior maximum.
- **Result 2 (κ(t) ladder).** Φ(t) beats every constant null but **ties** a
  flexible cubic → *time variation is required, the mechanism is not identified.*
  The per-timestep RMSEs are **reconstruction scores on one trace with ≈0.99
  residual autocorrelation**, not held-out predictive validation. The block
  interval is a **conditional resampling of fixed loss differences** (it does not
  refit either branch); a straddling interval is "not resolved," not
  "indistinguishable."
- **Cross-pressure LOPO.** The two-parameter equilibrium calibration is **not
  dominated by any single pressure**. This is **not** physical validation of the
  residual-vs-pressure pattern (donor trajectories held fixed).
- **Result 3 (N-tube channeling).** **Exploratory simulation.** One configuration
  (gs 1.1, 9 bar, N=200); floor- and control-law-dependent; the lateral term is a
  **homogenizing proxy, not a physical coupling operator** (card-blocked). The
  switching "convergence" is convergence of the collapse-time event **under Euler
  refinement on the output grid**, not a grid-independent full-trajectory result.
  **Not** a proven instability.
- **Jensen/heterogeneity.** The direct deficit is **−4.64 to −1.38 EY-pt**,
  evaluated against EY(E[K_eval]) (post-clipping mean), not EY(1).

## 2. Known limitations already disclosed (please assess adequacy, don't re-list)

| Known limitation | Status | Why it is open | Where disclosed / evidence |
|---|---|---|---|
| Real trajectory-convergence study (common physical-time grid, norms, event-time error vs spatial+temporal refinement, higher-order/adaptive solver) | UNBLOCKED-LARGE, deferred | current study is collapse-time under explicit-Euler refinement only | backlog B5-08; review §2.1(6) |
| Block-length sensitivity for the Result-2 conditional interval (4/8/16/24 s) | deferred | one 8 s block length used | backlog B5-18 |
| Physical N-tube balances (solute inventory, pressure-work, lateral-flux, age) | UNBLOCKED-LARGE, deferred | current "conservation" is a **numerical-invariant** audit, not physical balances | backlog B5-24/25/26; review §2.1(7) |
| Physical transverse-Darcy lateral-exchange operator + Jacobian/Lyapunov growth | **CARD-BLOCKED** (rule 1) | no card exists for the physical lateral operator (= gap G-lat / PV-14) | backlog B5-29 / B-AR10 |
| RSM advanced uncertainty: leverage-adjusted (HC2/HC3) wild bootstrap, post-selection, design-support, first-stage endpoint propagation | UNBLOCKED-LARGE, deferred | RSM intervals are **conditional** on the selected form + reconstructed endpoint | backlog B5-13/14/15/16 |
| Stochastic seed count (16; ≥100 or exact order-statistic intervals) | PARTIAL | 16 seeds; event-time variability now reported (not called "tight") | review §2.1(7); backlog B5-10 |
| Template prose/figures from the frozen bundle + full dependency manifest | deferred | figures currently recompute; some headline numbers still authored | backlog B5-33/34/35/36 |
| Complete per-panel source data + figure reworks (Fig 3/5 layout, Fig 4 ablation) | deferred | partial source data exported | backlog B5-39/40/44 |
| Vector (SVG/PDF) figures | **DONE-as-code** (full render owed) | export path + colour-safe palette + captions added | ROADMAP §7.1 (VENUE-2); `docs/figures/PAPER_B_CAPTIONS.md` |
| Journal manuscript conversion (remove internal IDs/roadmap refs/function names/open-gap ledger; Methods, references, declarations) | VENUE | APS DFD 2026 abstract fitted to limits; full journal conversion owed | `docs/submission/PAPER_B_APS_DFD_2026_ABSTRACT.md`; `VENUE_CONVERSION_STATUS.md` |
| Systematic Scopus/WoS novelty search | PI-owned | no licensed DB access; open-web seed only | `docs/PAPER_B_RELATED_WORK.md`; `SEARCH_PROTOCOL.md` |
| Clean tagged release + exact-env production bundle recompute | DEFERRED to RC / TB | release packager + env gate built; tag/DOI + ~1 min recompute-at-tag owed | `tools/prepare_paper_release.py`; backlog B5-01 |

## 3. Already corrected in prior rounds — please do NOT re-raise as new

Fixed in the current tree (the 5th review was partly stale on some):

- Jensen calculation: formula `E[EY(K)] − EY(E[K_eval])`, deficit range −4.64..−1.38,
  post-clipping mean shift reported (code + prose).
- Result-2 block step relabelled a conditional resampling of fixed losses;
  "statistically indistinguishable" → "not resolved by this conditional interval."
- Stale RC-3b cross-pressure numbers regenerated from the bundle
  (0.516→0.525, 0.510→0.519, 0.522→0.530).
- Schmieder-derived CSV: 36 exp-15 "DoE Corner Point" design-summary rows pinned
  as explicitly separate from the 576 valid runs (schema-contract test).
- N-tube switching claim scoped to collapse-time-under-Euler; "tight distribution"
  dropped; event-time variability reported.
- N-tube **end-state classifier** now uses explicit top-1-share/N_eff/persistence
  thresholds (single-channel / oligarchic / distributed / transient); a high
  top-decile share no longer mislabels a distributed state as concentration.
- Result-2 **residual diagnostics figure** (Fig 6, supplementary): residual-vs-time
  + ACF-by-branch, making the coherent non-white lack-of-fit visible.
- Both flagged DOIs verified (lee2023 10.1063/5.0138998; waszkiewicz2026
  10.1063/5.0319611).
- Earlier rounds: achieved-predictor RSM refit, deletion + wild-bootstrap
  diagnostics, data-driven Fig 2 + status dictionary, swelling sign-vs-magnitude
  narrowing, Result-3 downgraded to model-capacity / exploratory.

---

*Cross-referenced from `docs/REVIEW_BACKLOG.md`, `docs/ONBOARDING.md`, and
`docs/PAPER_B_DRAFT.md`. Companion: `docs/REVIEWER_BRIEF_PAPER_A.md`.*
