# P3 — fine-grind EY-dip hypothesis registry (ROADMAP item 2.3)

**Not a component — a living evidence table.** Five mechanisms compete to explain
the non-monotonic extraction-yield dip at fine grinds. This file tracks each
hypothesis, its discriminating observable, and the current registry evidence. It
is maintained as harnesses/components land; the interpretive verdict is CHAT
work that feeds the paper. Source: ROADMAP §1 cluster P3.

Shared external constraint on ALL five: **schmieder2023** measures non-monotonic
cup mass at fixed flow with pressure(grind) — cup mass peaks at GL 1.7 (data in
`data/schmieder2023/cup_masses.csv`). Any surviving mechanism must reproduce it.

> **VERDICT (P3 synthesis, `gate_p3_schmieder_peak_discrimination` /
> `harness.schmieder_peak_discrimination`):** of the four instrumented
> mechanisms, **only static channeling (#1) reproduces the schmieder interior
> peak from physical parameters.** Lee (#3) makes an interior EY maximum only at
> a doctored ceiling ρ_c=798 (physical ρ_c=399 plateaus); size-exclusion (#4,
> monotone y₀) and the diffusion/base-extraction null are monotone and cannot
> produce a non-monotonic peak at all. See the "P3 VERDICT" section below.

| # | hypothesis | card / component | discriminating observable | expected signature | status & current evidence |
|---|---|---|---|---|---|
| 1 | static channeling σ(φ₁) | `brewer2026.streamtube` | fitted σ vs fines fraction / grind | monotone σ(φ₁) relation | **INSTRUMENTED — `gate_p3_channeling_sigma_sweep` (`harness.channeling_sigma_sweep`).** A MONOTONE σ(grind) closure through the fines fraction, fed to the streamtube EY-deficit, turns the monotone base EY(grind) into a PEAKED ensemble EY (peak at gs≈1.5, near schmieder GL 1.7): the deficit is largest at the finest grind (most fines), so static channeling ALONE reproduces the fine-grind dip. Independent/qualitative. |
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

## P3 VERDICT — the fine-grind dip is a channeling phenomenon

**Harness:** `harness.schmieder_peak_discrimination()` · **gate:**
`gate_p3_schmieder_peak_discrimination` (QUICK). **Validation strength:**
qualitative / mechanism-discrimination. It compares the SHAPE of each
mechanism's grind response against the schmieder cup-mass shape — NOT the dial
location: grinder dial spaces are non-portable (CLAUDE.md rule 9), so the claim
is "does it make an interior maximum," not "does the peak land on GL 1.7."

**The schmieder target, stated honestly.** Cup mass vs grind (mean over reps),
by target flow (`data/schmieder2023`):

| target flow (mL/s) | GL 1.4 | GL 1.7 | GL 2.0 | interior peak? |
|---|---|---|---|---|
| 1.0 | 96.8 | **97.7** | 96.5 | **yes @ GL 1.7** |
| 2.0 | 90.5 | 96.9 | 97.0 | no (monotone ↑) |
| 3.0 | 90.5 | **94.3** | 94.2 | marginal (0.1 g) |

The non-monotonicity is REAL but WEAK (~1 g on ~97 g) and only unambiguous at the
lowest flow; at flow 2 it is monotone-increasing, at flow 3 the GL 1.7 lead is
within noise. So the target is "a small interior cup-mass peak at GL 1.7 that is
present at low flow" — not a clean flow-monotone story. Do not overclaim a
flow-washout.

**Mechanism scoreboard** (interior maximum in the grind response, and whether it
survives at physical parameters):

| # | mechanism | interior peak? | physical? | reproduces schmieder? |
|---|---|---|---|---|
| 1 | static channeling σ(φ₁) | **yes** (peak gs≈1.5) | **yes** | **YES** |
| 3 | lee2023 dissolution instability | yes | **no** (needs ρ_c=798) | only with doctored ceiling |
| 4 | size-exclusion y₀(grind) | no (monotone 31.7→24.3%) | — | no |
| — | base / diffusion extraction (null) | no (monotone) | — | no |

**Reading.** The fine-grind dip / schmieder non-monotonicity is a **channeling**
phenomenon: a monotone σ(grind) closure through the fines fraction (more fines at
fine grinds → more static channeling → EY deficit largest at the finest grind),
folded against the ordinary surface-area rise, is the *only* mechanism that turns
a monotone base EY(grind) into an interior maximum without a doctored constant.
Lee can make the shape but only by imposing an unphysical saturation ceiling;
size-exclusion inventory and pure diffusion are structurally monotone and cannot
produce non-monotonicity alone. This does not *exclude* #2 (incomplete wetting) —
that mechanism lives in the still-open G1 continuous-saturation gap and is
discriminated by first-drip DELAY, not by the EY/cup-mass shape (see the
wetting-atom probe below). It says: among the mechanisms we *can* run, channeling
is sufficient and uniquely physical for the schmieder cup-mass signature.

## What's needed to close P3 (mostly Phase 3 + CHAT)
- Hypotheses 1 (static channeling), 3 (lee2023) and 4 (romancorrochano size-exclusion) are now instrumented. The ONLY remaining un-instrumented mechanism is #2 incomplete wetting, which needs the G1 continuous-saturation (Richards-type) model — no card on file, so it stays open.
- Hypothesis 1 needs a per-grind σ(φ₁) sweep (streamtube × grindmap).
- Hypothesis 2's discriminating observable is first-drip DELAY (probed; needs per-grind DE1 first-drip data to settle); a validated model still needs the G1 continuous-saturation constitutive gap closed.
- The verdict ("which mechanism survives, and does any reproduce the schmieder
  non-monotonic cup mass") is now SETTLED at the EY/cup-mass level — see the
  **P3 VERDICT** section above (`gate_p3_schmieder_peak_discrimination`): static
  channeling (#1) is the unique physical reproducer. The one live discriminator
  that could still promote #2 is a per-grind DE1 **first-drip DELAY** sweep
  (channeling leaves first-drip unchanged; only the wetting atom delays it).

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
