# Retired candidates

IF-5 human triage is complete and both waves of cheap screens have run
([`IF5_HUMAN_TRIAGE_DECISION.md`](IF5_HUMAN_TRIAGE_DECISION.md)). Retirements below.

**Withdrawn retirement — I-045 (2026-08-05).** I-045 was recorded here as RETIRE on 2026-08-05 and
the row was **removed the same day** on exact-head review: the screen had applied a local reading
of *independent* (an independent measurement modality) instead of the definition ROADMAP §0 fixes
(data not used in fitting the thing being tested). Under the governing definition the screen
returns **SURVIVE**, and a survivor does not belong in this file. The corrected record is
[`screens/I-045/`](screens/I-045/); the reasoning is in the ROADMAP §7.1 entry for that date. The
withdrawal is recorded here rather than erased, because a retirement that turned out to be wrong
is exactly the thing a future reader needs to be able to find.

This file exists because a retirement is a result. Retired candidates are preserved so the same
idea is not rediscovered, re-argued, and re-funded in six months; a high retirement rate is
evidence of useful selection, not failure (blueprint §3.3, §10.4).

## Record format

One row per retirement. The `reopen condition` is mandatory: a candidate retired for lack of data
is a different thing from one retired because the effect was not there, and only the row can say
which.

| candidate | retired at (commit) | reason | result bundle | reopen condition |
|---|---|---|---|---|
| **I-024** — can one transport state explain every measured species at once? | snapshot `c1b7d79`, screened on `insights/if5-wave1-cheap-screens` | Per-species transport freedom buys **nothing** held out, anywhere in the campaign's declared 0.3–19.7 % bioactive RSD band. An exact finite-grid sweep — 24 shared-rate breakpoints, 25 fixed-selection intervals, 51 evaluated points, with C1/C3 provably monotone between breakpoints and each interval's C2 vertex evaluated — puts the best achievable `Z_independent / Z_shared` at **1.0008** against a 0.70 threshold, and above 1 everywhere (per-species fits are slightly *worse* out of sample). The rate grid was expanded ×4 until the worst-case C3 moved by 2×10⁻⁴; the independent per-species rates span 0.257–26.0, a 100× range, and still buy nothing. A free per-species **amplitude** term — a condition-independent multiplicative scale that may be inventory, assay scale **or** multiplicative model error, which this screen cannot separate — reduces the RMS standardised held-out residual by 44–87 % depending on the assumed RSD. | [`screens/I-024/`](screens/I-024/) | A **fraction-resolved** species dataset for this campaign. The cup-integrated endpoint provably discards the rate information (`ANALYSIS_transfer` positive control), which is why a 100× spread in fitted rate produced no held-out separation; timed fractions would be a different and answerable question. **Not** reopened by solute-specific replicate RSD — that would sharpen C1 and C2 but cannot move C3, which fails across the whole declared band. **Not** reopened by a claim that species kinetics differ in the literature: this screen bounds what *this campaign at this observable* can resolve. |
| **I-040** — which strength is load-bearing where the manifest says 'independent + post_fit + same_campaign'? | snapshot `c1b7d79`, screened on `insights/if5-wave1-cheap-screens` | Every active use preserves the split. 27 consumers of `waszkiewicz2025/traces_time_dependent` enumerated two independent ways (static AST + dynamic tracing) and attributed by hand; **0** state a strength stronger than the half their assertion rests on. The one half-A gate reaches the dataset only via `steady_state_curve()` (`[-1]` per trace) and cannot touch the trajectory; PV-02's evidence selection explicitly EXCLUDES that gate from the post-fit claim as "a different observable". | [`screens/I-040/`](screens/I-040/) | A **new or edited** consumer of this dataset that states a strength stronger than its load-bearing half — most plausibly a new gate scoring against the 9-bar trajectory while citing the "independent within-rig" half. Re-running `python -m puckworks.analysis.screen_i040_evidence_halves` detects it: the coverage check fails on any consumer the table does not cover, and the promotion check fails on any over-claim. **Not** reopened by a dispute about whether the manifest's own half-A label is correct — that is a question about the cell, was deliberately not adjudicated here, and belongs with I-045. |

## Rules

- A candidate is retired by a **decision**, never by a generator and never by silence. The
  decision record lives in `docs/insights/screens/I-xxx/decision.md`.
- The reason states what was found, not that interest was lost. "Effect disappears under raw
  replicate analysis" is a reason; "deprioritised" is not.
- A retirement whose screen produced a defensible negative result is **publishable material** —
  route it to the negative-result track rather than filing it here and forgetting it.
- Retiring a candidate does not retire its tension rows. The atlas is regenerated from the
  authorities; if the underlying tension persists, the row comes back, and that is correct.
