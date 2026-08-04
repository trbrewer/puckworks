# Retired candidates

IF-5 human triage is complete and the Wave-1 cheap screens have run
([`IF5_HUMAN_TRIAGE_DECISION.md`](IF5_HUMAN_TRIAGE_DECISION.md)). Retirements below.

This file exists because a retirement is a result. Retired candidates are preserved so the same
idea is not rediscovered, re-argued, and re-funded in six months; a high retirement rate is
evidence of useful selection, not failure (blueprint §3.3, §10.4).

## Record format

One row per retirement. The `reopen condition` is mandatory: a candidate retired for lack of data
is a different thing from one retired because the effect was not there, and only the row can say
which.

| candidate | retired at (commit) | reason | result bundle | reopen condition |
|---|---|---|---|---|
| **I-010** — does anything consume pannusch2024.closures, and does it survive outside its declared range? | snapshot `c1b7d79`, screened on `insights/if5-wave1-cheap-screens` | A consuming path exists (a direct import, `solver.py:30`) and the held-out result is insensitive to it. Over 72 independent `angeloni2023` points with everything frozen, the three admissible one-at-a-time closure swaps move the median prediction by 2.97 % / 0.83 % / 0.01 % against a predeclared U = 4.70 % derived from the campaign's own replicate RSD. The artifact is driven strictly inside its declared T and Q range. The whole artifact reaches the consumer as three scalars (`h1`, `h2`, `K`), which is why. | [`screens/I-010/`](screens/I-010/) | **(a)** A second **pure-water** viscosity correlation declared over 88–98 °C enters the corpus — μ(T) is the most influential closure on the path and is the one this screen could not test; the bound run here puts a TR2001-extrapolation-sized μ error at ~8.9 %, above U. **(b)** A second Sherwood correlation is registered, making `sherwood_h` substitutable — the card already flags its fitted params as lacking generality. **(c)** A consumer appears that reads the artifact at a finer observable than a cup-integrated endpoint (timed fractions), where the swaps are not integrated away. **Not** reopened by the blind accuracy gap against angeloni — that is `ANALYSIS_transfer`'s standing result, not this screen's subject. |
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
