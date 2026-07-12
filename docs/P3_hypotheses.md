# P3 — fine-grind EY-dip hypothesis registry (ROADMAP item 2.3)

**Not a component — a living evidence table.** Five mechanisms compete to explain
the non-monotonic extraction-yield dip at fine grinds. This file tracks each
hypothesis, its discriminating observable, and the current registry evidence. It
is maintained as harnesses/components land; the interpretive verdict is CHAT
work that feeds the paper. Source: ROADMAP §1 cluster P3.

Shared external constraint on ALL five: **schmieder2023** — but see the
CORRECTION below before treating it as a clean "cup mass peaks at GL 1.7" target.

> **⚠️ CORRECTION (2026-07-12, from a review of PAPER_OUTLINE).** The earlier
> P3 verdict ("only static channeling reproduces the schmieder peak from physical
> parameters") rested on an **invalid target**. `harness._schmieder_mass_vs_grind`
> averaged `mass_in_cup` across component, **unit** (trigonelline/caffeine/5-CQA
> in **mg**, TDS in **g**), brew ratio, and temperature — a dimensionless-nonsense
> aggregate. The gate passed (software reproducibility) while adjudicating a
> quantity with no coherent unit. The corrected target
> (`harness.schmieder_interior_max_target`, per observable at a fixed condition):
> schmieder's OWN RSM is concave with an interior grind vertex for all four
> observables, **but** the fit is WEAK (adj-R² 0.41–0.75) and the raw cells at
> the one fully-sampled fixed condition (T 89 °C, BR 1/2, flow 2.0) are largely
> **monotone** (a prominent interior max for ≤1/4). Also **GL 1.7 is the FINEST
> grind by Sauter d₃₂** (26.9 µm vs 28.3/29.2), so this is a peak in DIAL, not a
> particle-size fine-grind dip.
>
> **Downgraded verdict (`gate_p3_schmieder_peak_discrimination`):** MODEL
> CAPACITY, not identification. Of the implemented generators, only the
> empirically-calibrated static-heterogeneity closure produces an interior grind
> maximum without a doctored constant (lee needs ρ_c=798; size-exclusion #4 and
> the diffusion null are monotone; incomplete wetting #2 is untested). This
> establishes that channeling is a **viable candidate generator**, NOT that it
> "reproduces the schmieder peak" or "is the mechanism." The σ(φ₁) closure is
> itself empirical (calibrated on cameron grind-deviation data), so this is a
> viability check, not a validation. See the corrected "P3 VERDICT" section.

| # | hypothesis | card / component | discriminating observable | expected signature | status & current evidence |
|---|---|---|---|---|---|
| 1 | static channeling σ(φ₁) | `brewer2026.streamtube` | fitted σ vs fines fraction / grind | monotone σ(φ₁) relation | **INSTRUMENTED — `gate_p3_channeling_sigma_sweep` (`harness.channeling_sigma_sweep`).** A MONOTONE σ(grind) closure through the fines fraction, fed to the streamtube EY-deficit, turns the monotone base EY(grind) into a PEAKED ensemble EY (peak at gs≈1.5, near schmieder GL 1.7): the deficit is largest at the finest grind (most fines), so a static-heterogeneity closure CAN GENERATE an interior maximum (model capacity). NOT "reproduces the dip" — see the CORRECTION box + P3 VERDICT: the target is a weak-R² RSM feature and σ(φ₁) is empirical (partly circular). Qualitative. |
| 2 | incomplete wetting, tubes at k→0 | `foster2025.machine_mode` / `.infiltration` | per-grind first-drip timing; CT saturation | delayed / partial wetting at fine grinds | **gated & data-validated.** Foster infiltration (first-drip triangle on DE1) + machine mode (Figs 12-15). The "tubes at k→0" atom the lognormal lacks (foster card). Foster's model is sharp-front and **declines the coarse grind** (front visibly non-uniform) → the unsaturated-flow gap **G1** is where this hypothesis actually lives; no continuous-saturation model on file yet. **mckeonaloe2021 (SKIP)** articulates the conceptual frame — *pre-wetting* (capillary √t, may leave the puck incompletely wet) ≠ *pre-infusion* (pressure-driven) — which is exactly this hypothesis's failure mode, but it is a single uncalibrated pixel-unit √t trial (superseded by foster2025.infiltration's capillary branch) and, critically, is silent on partial saturation behind the front → it does **NOT** supply the continuous-saturation constitutive data G1 needs. |
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

## P3 VERDICT — a model-capacity result, not an identification

**Harness:** `harness.schmieder_peak_discrimination()` +
`harness.schmieder_interior_max_target()` · **gate:**
`gate_p3_schmieder_peak_discrimination` (QUICK). **Validation strength:**
qualitative / model-capacity. *(Downgraded 2026-07-12 after a review found the
original target dimensionally invalid — see the CORRECTION box at the top.)*

**The schmieder target — corrected, per observable.** The old table averaged
`mass_in_cup` across component, unit (mg solutes + g TDS), brew ratio, and
temperature → no coherent unit; deleted. The right target is schmieder's own
fitted RSM in the grind direction, per observable, at a fixed condition (flow 2.0,
89 °C, BR 1/2), cross-checked against the raw cells:

| observable | RSM concave (β₅<0)? | RSM vertex in [1.4,2.0]? | adj-R² | raw cells (fixed condition) |
|---|---|---|---|---|
| TDS (g) | yes | 1.75 | 0.64 | monotone (prominence −1.1 σ) |
| trigonelline (mg) | yes | 1.81 | 0.60 | monotone (−1.1 σ) |
| caffeine (mg) | yes | 1.70 | 0.41 | flat-topped (+0.04 σ) |
| 5-CQA (mg) | yes | 1.95 | 0.62 | monotone (−1.2 σ) |

So schmieder's RSM *does* encode an interior grind maximum for every observable —
but the fit is WEAK (adj-R² 0.41–0.75; caffeine barely fits) and the raw cells at
the one fully-sampled fixed condition are **largely monotone** (a prominent
interior max for ≤1/4). And **GL 1.7 is the FINEST grind by d₃₂** (26.9 vs
28.3/29.2 µm), so any dial peak is not cleanly a fine-grind dip in particle size.

**Mechanism scoreboard** — generates an interior grind maximum? and under what
parameterization?

| # | mechanism | generates interior max? | parameterization |
|---|---|---|---|
| 1 | static channeling σ(φ₁) | **yes** (vertex gs≈1.5) | empirical σ(φ₁) closure (calibrated, not doctored) |
| 3 | lee2023 dissolution instability | yes | ONLY under doctored ρ_c=798 (2× measured) |
| 4 | size-exclusion y₀(grind) | no (monotone) | measured inventory — different observable |
| — | base / diffusion extraction (null) | no (monotone) | source model |
| 2 | incomplete wetting | **untested** | unimplemented (needs G1 data) |

**Reading — model capacity, not identification.** Of the *implemented* response
generators, the empirically-calibrated static-heterogeneity closure is the only
one that produces an interior grind maximum without a doctored constant. That is
a **viability** result: a static-heterogeneity model *can* generate the shape
schmieder's weak RSM shows. It is **not** an identification — (a) the schmieder
target is a weak-R² empirical surface, not a robust raw signal; (b) σ(φ₁) is
itself empirical, calibrated on cameron grind-deviation data, so reproducing a
grind non-monotonicity is partly circular; (c) incomplete wetting (#2) is
untested and lives in the open G1 gap, discriminated by first-drip DELAY not EY
shape. Do NOT write "channeling is the mechanism" or "reproduces the schmieder
peak." The defensible claim: *among implemented generators, static heterogeneity
is the only viable one under its registered parameterization; incomplete wetting
remains untested; identification requires a corrected observable analysis and a
direct spatial/first-drip discriminator.*

## What's needed to close P3 (mostly Phase 3 + CHAT)
- Hypotheses 1 (static channeling), 3 (lee2023) and 4 (romancorrochano size-exclusion) are now instrumented. The ONLY remaining un-instrumented mechanism is #2 incomplete wetting, which needs the G1 continuous-saturation (Richards-type) model — no card on file, so it stays open.
- Hypothesis 1 needs a per-grind σ(φ₁) sweep (streamtube × grindmap).
- Hypothesis 2's discriminating observable is first-drip DELAY (probed; needs per-grind DE1 first-drip data to settle); a validated model still needs the G1 continuous-saturation constitutive gap closed.
- The verdict ("which mechanism survives, and does any reproduce the schmieder
  non-monotonic cup mass") is **NOT settled** — see the **P3 VERDICT** section:
  it is a MODEL-CAPACITY result (static heterogeneity is the only implemented
  generator that makes an interior max under calibrated params), not an
  identification, because the schmieder target is a weak-R² RSM feature and σ(φ₁)
  is empirical/partly circular. Identification still needs (a) a corrected
  per-observable target analysis with uncertainty and closure-sensitivity, and
  (b) a per-grind DE1 **first-drip DELAY** sweep to test #2 (channeling leaves
  first-drip unchanged; only the wetting atom delays it).

## Hypothesis #2 probe — composite wetting-atom over streamtube + foster

**What this is.** A NON-COMPONENT, exploratory signature probe
(`puckworks/validation/slow/hyp2_wetting_atom.py`) over two already-carded
components (`brewer2026.streamtube` + `foster2025.infiltration`). It is NOT a
model: no registry entry, no gate, no fit. It does NOT implement Richards /
van-Genuchten and pulls NO constants from egidi2018/2023. The G1
continuous-saturation constitutive gap remains **OPEN**. Validation strength:
**qualitative / exploratory** throughout.

**Construction.** Baseline = the task-#1 static-channeling result (streamtube
lognormal-k EY ensemble with the σ(φ₁) closure). The "dry atom" adds a fraction
`w_dry(g)` of tubes at k→0 (non-conducting, zero extraction) — the k→0 atom the
lognormal structurally lacks. `w_dry` is **IMPOSED, not fitted**: a monotone grid
0.20 at g=1.1 falling to 0 by g≈1.7. A signature switch, not a calibration.

**Signature 1 — EY vs grind.** Composite EY = (1−w_dry)·EY_ensemble (the dry
fraction is dead dose). The atom pulls fine grinds down most, shifting the EY
peak coarser (probe: pure-σ peak gs≈1.3 → composite peak gs≈1.7).
⚠️ **Partly circular:** because w_dry was imposed to vanish by g≈1.7, the peak
*necessarily* migrates toward 1.7 — this signature demonstrates the atom *can*
sharpen/shift the peak, but its landing at the schmieder GL 1.7 target is a
consequence of the imposed w_dry shape, not a prediction.

**Signature 2 — first-drip delay (the real discriminator).** The atom reduces the
effective conducting permeability to k_eff = k(g)·(1−w_dry(g)) (a labelled
parallel-conductance proxy) fed to the foster first-drip triangle on DE1 fixture
A. First-drip **delay grows at fine grind**: ≈2.0 s at g=1.1, 0.9 s at 1.3, 0.3 s
at 1.5, 0 by g≥1.7 (observed first drip ≈7.0 s). Static channeling (#1) leaves
the MEAN permeability — hence first-drip — unchanged, so it **cannot** produce a
grind-dependent first-drip delay. This is non-circular: the delay is the atom's
own signature.

**Are #1-only and #1+#2 distinguishable?** By EY alone, weakly (both give a dip;
signature 1 is partly circular). By **first-drip, yes** — only the wetting atom
delays it, and the delay is monotone in fineness.

**Standing verdict.** Static channeling (#1) is **sufficient** for the fine-grind
EY dip. The wetting atom (#2) is **additionally required only if first-drip data
shows a grind-dependent delay** (a per-grind DE1 first-drip sweep would settle
it). Until a G1 constitutive-data paper lands, #2 stays a qualitative probe, not
a model.
