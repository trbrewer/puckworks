# P3 — fine-grind EY-dip hypothesis registry (ROADMAP item 2.3)

**Not a component — a living evidence table.** Five mechanisms compete to explain
the non-monotonic extraction-yield dip at fine grinds. This file tracks each
hypothesis, its discriminating observable, and the current registry evidence. It
is maintained as harnesses/components land; the interpretive verdict is CHAT
work that feeds the paper. Source: ROADMAP §1 cluster P3.

Shared external constraint on ALL five: **schmieder2023** measures non-monotonic
cup mass at fixed flow with pressure(grind) — cup mass peaks at GL 1.7 (data in
`data/schmieder2023/cup_masses.csv`). Any surviving mechanism must reproduce it.

| # | hypothesis | card / component | discriminating observable | expected signature | status & current evidence |
|---|---|---|---|---|---|
| 1 | static channeling σ(φ₁) | `brewer2026.streamtube` | fitted σ vs fines fraction / grind | monotone σ(φ₁) relation | **INSTRUMENTED — `gate_p3_channeling_sigma_sweep` (`harness.channeling_sigma_sweep`).** A MONOTONE σ(grind) closure through the fines fraction, fed to the streamtube EY-deficit, turns the monotone base EY(grind) into a PEAKED ensemble EY (peak at gs≈1.5, near schmieder GL 1.7): the deficit is largest at the finest grind (most fines), so static channeling ALONE reproduces the fine-grind dip. Independent/qualitative. |
| 2 | incomplete wetting, tubes at k→0 | `foster2025.machine_mode` / `.infiltration` | per-grind first-drip timing; CT saturation | delayed / partial wetting at fine grinds | **gated & data-validated.** Foster infiltration (first-drip triangle on DE1) + machine mode (Figs 12-15). The "tubes at k→0" atom the lognormal lacks (foster card). Foster's model is sharp-front and **declines the coarse grind** (front visibly non-uniform) → the unsaturated-flow gap **G1** is where this hypothesis actually lives; no continuous-saturation model on file yet. |
| 3 | dissolution–flow instability + saturation ceiling | `lee2023` | pathway-resolved depletion | fast pathway saturates/depletes first | **INSTRUMENTED — `lee2023.feedback` (item 3.4).** `gate_lee_feedback_negative_result` reproduces the paper's behaviour + its negative result: δ=0.035 seed amplifies (pathway EY diverges) at all g; imposed ρ_c=798 gives an interior EY(g) peak with a fine-side decline (weak ~0.2 pp); physical ρ_c=399 only plateaus (no decline). Discriminator: pathway-resolved depletion → one region fully extracted → bitterness signature. Not a data fit. |
| 4 | size-exclusion entrapment | `romancorrochano2017_extraction` | extractable inventory y₀(grind) | inventory falls with coarseness | **INSTRUMENTED — `gate_roman_y0_ceiling_sizeexclusion` (0.5 intake).** Thesis Fig 4.19 y₀(grind) decreases monotonically along the coarsening ladder ΨA→ΨH (31.7→24.3%): finer grinds expose more extractable inventory, coarser entrap it — the size-exclusion signal. Same gate also lands the §5.5 nested-ceiling cross-check (y₀ 0.317 > Cameron 0.245 > Liang 0.215). Independent + qualitative. |
| 5 | flow inhomogeneity + pressure | `pannusch2024.solver` | flow + pressure at fixed grind | qualitative only | **solver gated** (RC-4a/b). But pannusch is a *no-channeling, constant-porosity* model — this is a **pointer, not a mechanism** (card). The fine-grind dip is attributed to flow inhomogeneity + higher pressure, i.e. *outside* the model. |

## Cross-cutting evidence from the harnesses
- **§5.6 dissolution speed** (P1 harness): Waszkiewicz TDS fractions favor
  **near-instant dissolution** (early/peak 0.968) over Cameron's diffusion-limited
  boulders — so a fine-grind dip is unlikely to be pure boulder-diffusion.
- **P2 κ(t) ladder** (rung 4 beats the flat nulls 5.4× on the 9-bar rising flow):
  a **time-dependent bed mechanism** is real in the saturated regime — relevant to
  hypotheses 1/5 (compaction/channeling) but tested on rising flow, not the dip.
- **Foster flow-minimum null** (rung 2): pump+headspace reproduce a mid-shot flow
  minimum with **no bed mechanism** — any dip explanation invoking κ(t) must beat
  this null first.

## What's needed to close P3 (mostly Phase 3 + CHAT)
- Hypotheses 1 (static channeling), 3 (lee2023) and 4 (romancorrochano size-exclusion) are now instrumented. The ONLY remaining un-instrumented mechanism is #2 incomplete wetting, which needs the G1 continuous-saturation (Richards-type) model — no card on file, so it stays open.
- Hypothesis 1 needs a per-grind σ(φ₁) sweep (streamtube × grindmap).
- Hypothesis 2's coarse-grind case needs a continuous-saturation model (gap G1).
- The verdict ("which mechanism survives, and does any reproduce the schmieder
  non-monotonic cup mass") is the CHAT workup feeding the paper.
