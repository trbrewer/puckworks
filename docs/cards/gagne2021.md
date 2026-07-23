# Model card: Gagné 2021 — standard vs. low-fines blooming shots (viscosity-decline hypothesis + DE1 shot dataset)

**Paper/thesis:** J. Gagné (Coffee Ad Astra), "A Comparison between Standard and Low-Fines Espresso Shots," Patreon/blog post, 12 Apr 2021. No DOI; not peer-reviewed. Log files and 11 DE1 `.shot` files published alongside the post (links in text). Viscosity data cited from Sobolik et al. (2002), reproduced as a figure.
**Stage(s):** bed_dynamics (resistance-decline mechanism), observables (EY/TDS/temperature/retention measurements) · **Kind:** calibration (data source + hypothesis)
**Status:** proposed (card-only)

## Scope and mechanism
Not a forward model. An 11-shot alternating comparison (6× EG-1 + SSP ultra-low-fines burrs, 5× Niche Zero) on a DE1+ with Rao's blooming profile (flow-controlled 2 mL/s, 30 s bloom at 10–40 s, temperature goals 97.5 → 92 °C), 18 g dose, 1:4 ratio, one washed Colombian coffee, blind randomized refractometry. Both grinders dialed to matched *peak* puck resistance; the observed contrast is the post-peak dynamics. Core mechanistic claim: the monotonic post-bloom decline in puck resistance is driven by the slurry/liquor **viscosity falling as effluent TDS falls** (Sobolik et al. 2002 μ(T, TDS) data), not by wetting (excluded by the 30 s bloom) nor by puck disintegration/channeling (argued against via intact spent pucks and no further degradation at 1:11). Low-fines shots, ground much finer to reach the same peak resistance, release solubles faster and hence decline faster. The post closes with an *inverse* reconstruction: R(t) from DE1 telemetry → relative μ(t) → TDS(t) via Sobolik inversion → cumulative EY(t), endpoint-anchored to each shot's measured filtered EY.

## Governing equations
No equations are printed anywhere in the source; the following are the prose-stated relations that an implementation would use, transcribed faithfully. No equation numbers exist.

1. **Fines–resistance claim (qualitative):** hydraulic resistance of the puck is driven by D10 of the mass-weighted PSD (the particle size at 10% cumulative dose weight), not D50. No functional form given.
2. **Pressure–resistance rule of thumb (attributed to John Buckman / DE1 users):** "the change in pressure goes with the square of the puck resistance," i.e. ΔP ∝ R². Gagné attributes this to porosity reduction under pressure and notes his data "deviate slightly from this." No definition of R is printed; the DE1's live "puck resistance" channel (computed from shower-head flow, or from Acaia scale flow) is used as-is. `[RS]` This is the DE1 firmware's internal resistance definition — carry it as an instrument-defined quantity, not a physical closure.
3. **Viscosity closure (borrowed):** μ(T, TDS) interpolated from Sobolik et al. (2002) tabulated curves (0–50% TDS, 0–80 °C, μ ≈ 10⁻³·⁵–1 Pa·s), **extrapolated in log space to higher temperatures**. Stated anchor: at high water temperature, going from 0% to 10–15% TDS raises μ by ~50%.
4. **Inverse TDS/EY reconstruction:** attribute *all* of R(t)'s post-bloom change to μ(t); invert (3) for TDS(t); EY(t) = cumulative Σ TDS·(flow·dt)/dose. Because only *relative* μ is constrained, the end-of-shot TDS is a free anchor, chosen per shot so EY(t_end) equals the measured VST-filtered EY. Not simplified away here: the DE1's shower-head flow estimate itself drifts (~20% decline near shot end per the Acaia cross-check), which contaminates R(t); Gagné notes this cannot account for the full pressure decline.

Symbols: R DE1-reported puck resistance (instrument units); P pump pressure (bar); TDS total dissolved solids (%); μ dynamic viscosity (Pa·s); T temperature (°C); EY extraction yield (% of dose).

## Parameters
No model parameters. Measured/protocol quantities (means ± stated errors; "figure" = read from chart, approximate `[RS]`):

| symbol / quantity | value | units | source |
|---|---|---|---|
| raw EY, EG-1 + SSP ULF | 26.8 ± 0.2 | % | measured (n=6) |
| raw EY, Niche | 24.8 ± 0.1 | % | measured (n=5) |
| raw EY difference | 2.1 ± 0.3 | % | measured |
| VST-filtered EY, EG-1 | 24.1 ± 0.3 | % | measured |
| VST-filtered EY, Niche | 22.7 ± 0.2 | % | measured |
| filtered EY difference | 1.3 ± 0.3 | % | measured |
| filtered-TDS measurement error (≤ shot 6 / after 3-drop protocol) | ±0.03 / ±0.01 | % TDS | assumed (author-adopted) |
| grinder retention, Niche | 0.18 ± 0.04 | g | measured |
| grinder retention, EG-1 + SSP ULF @1500 rpm | 0.23 ± 0.02 | g | measured |
| WDT-step retention | 0.06 ± 0.03 | g | measured |
| Force Tamper retention | 0.10 ± 0.01 | g | measured |
| drips during bloom, Niche / EG-1 | ≈4.9 / ≈3.85 (figure; axis units not stated, presumably g) | — | measured |
| mean shot temperature, Niche / EG-1 | ≈95.60 / ≈95.43 (figure) | °C | measured |
| stable resistance (shower-head), Niche / EG-1 | ≈0.661 / ≈0.607 (figure) | DE1 units | measured |
| stable resistance (scale), Niche / EG-1 | ≈0.745 / ≈0.698 (figure) | DE1 units | measured |
| peak pressure (both grinders) | ≈5 | bar | measured (figure) |
| normalized pressure at 80 s, EG-1 / Niche | ≈1.8 / ≈2.1 × trough baseline (figure) | — | measured |
| dose / basket / ratio | 18 g, Decent 18 g basket, 1:4 | — | nominal |
| bloom flow / duration | 2 mL/s / 30 s (10–40 s window) | — | nominal |
| temperature goals | 97.5 then 92 | °C | nominal |
| grind settings: Niche / EG-1 | 10.0 (factory zero) / 4.7 @1500 rpm | — | nominal |
| Sobolik μ increase, 0 → 10–15% TDS at high T | ~50 | % | measured (secondary source, figure) |
| reconstructed first-drip TDS | ~13–15 (figure) | % | fitted (anchored inverse) |
| independently measured end-of-shot TDS (similar coffee) | ~2.0 | % TDS | measured (n=1, different session) |
| PSD (D10, D50), bed depth, tamp force, water chemistry | not provided | — | — |

Pressure-node note `[RS]`: DE1 pressures are gauge (pump-referenced); consistent with MachineState convention, no ROADMAP hazard-table entry needed.

## Calibration and validation offered by the source
Protocol quality is high for the source class: alternated shot order, fixed grind settings, blind randomized TDS measurement, explicit per-regime measurement errors, outliers flagged (two peak-resistance outliers marked in every plot). But **the viscosity-decline hypothesis is not validated**: the EY(t) reconstruction is endpoint-anchored to the very filtered-EY measurement it "predicts" — circular by construction, and the author says so ("not to make a precise estimate... but to see if the numbers looked realistic"). Supporting checks are plausibility-level only: reconstructed curve shapes resemble Ribes's EY-vs-ratio measurements (ribes2020/2021 lineage), and one out-of-session TDS spot-check (~2.0%) lands "in the ballpark." The ΔP ∝ R² rule is asserted from community observation with an acknowledged deviation. Sobolik μ data are used far outside their measured temperature range (log-space extrapolation above 80 °C). The temperature and crema observations are single-session correlations with proposed follow-up experiments, not tests. Grade: measured EY/retention/temperature contrasts are **independent within-session data**; every mechanistic claim is **hypothesis-generating**.

## Assumptions and validity range
- Attributes 100% of post-bloom R(t) change to liquor viscosity; compaction/swelling (kappa(t)), fines migration, and flow-sensor drift are acknowledged but not separated — the ~20% end-of-shot flow miscalibration alone contaminates R(t).
- ΔP ∝ R² closure is uncalibrated folklore with admitted deviation; porosity–pressure coupling is invoked but never modeled.
- Sobolik et al. (2002) viscosity: different coffee material, extrapolated in T; oils explicitly ignored ("might play an important role").
- Single coffee, single machine/profile (blooming, 1:4), single operator, n = 5–6 per arm; two shots flagged as pressure outliers; first two shots ran ~0.5 °C cool (thermal settling).
- No PSD measurement exists for either grinder (laser diffraction planned, not done) — the "much less fines" premise is inferred from shot behavior, not measured. D10 claim inherits this.
- Raw-vs-filtered EY gap interpretation (oil refractive-index bias in unfiltered readings) is speculative.
- Silent on: pressure-driven (9 bar) shots, non-blooming profiles, doses ≪ 18 g ("puck might fall apart"), darker roasts (author himself flags), crema physics (no registry stage), channeling regimes.

## Interface mapping
Inputs consumed: none (no runnable component). Outputs produced: none under contracts v0.1.
Couplings: OFFLINE CALIBRATION/gate data only. Realistic consumers: (i) the bed_dynamics backlog item kappa(t) = kappa0·f(P, ε, E) — this source supplies the principal **competing hypothesis** (apparent-kappa decline from μ(TDS(t)), not bed compaction) plus 11 traces on which a discriminating computation can run: drive the registered flow chain with μ(TDS(t)) from the telisromero2001 G10 closures fed by cameron2020.extraction_bdf's c(t), and test whether predicted R-decline rates separate the two grinder arms as observed; (ii) observables measurement kernels — the raw-vs-filtered TDS offset (2.1 vs 1.3 pt grinder contrast) and the ±0.01/±0.03% TDS error model; (iii) grind backlog (grinder transfer functions) — a two-grinder behavioral contrast awaiting PSDs. Adapter needed to parse DE1 `.shot` files → MachineState/ShotResultState traces (same class as the DE1 fixture A ingest).

## Extractable data
- **Published shot logs + 11 DE1 `.shot` files (zipped)** — the highest-value asset: full P(t), flow(t), T(t) traces for a *flow-controlled blooming* profile, complementing DE1 fixture A (pressure-profile class). Links live in the post; acquisition target → data/gagne2021_shots/. Availability of the links five years on should be verified at acquisition.
- Per-shot EY tables (raw + filtered), retention, drips, temperatures: values above transcribed inline per blog-source convention; per-shot values recoverable from the published logs, preferable to figure-reading.
- **Sobolik et al. (2002)** μ(T, TDS) — flag as an ACQUISITION TARGET: a third independent liquor-viscosity dataset for G10, to sit beside telisromero2001/2000 and khomyakov2020 (which already carry a ~40–55% inter-source offset; a third source could adjudicate).
- Normalized-pressure and reconstructed TDS/EY figures: do not digitize — reconstructible from the `.shot` files, and the reconstruction is anchored anyway.

## Overlaps and conflicts
- **bed_dynamics backlog (kappa(t), rising-flow residual):** COMPLEMENT/COMPETE — supplies the viscosity-decline alternative to compaction/swelling, with data to discriminate. This is the card's main registry value beyond the traces.
- **G10 stack — telisromero2001/2000, khomyakov2020 (calibration-providers):** COMPLEMENT. The mechanism here is exactly the runtime hook telisromero2001's gate (ii) was designed to size ("sensitivity study... μ(c,T) vs constant water μ"). Note tension `[RS]`: telisromero2001 concluded the constant-μ error is "likely bound as small" *at beverage TDS (~5–10%)*; Gagné's reconstructed first-drip TDS of ~13–15% and factor-~2 pressure decline argue the early-shot transient is where it matters. Not a conflict of data — a conflict of emphasis to be settled by the discriminating computation above.
- **cameron2020.extraction_bdf:** consistency note — raw EY 26.8% sits uncomfortably near the 29.6% per-bed-volume ceiling at a 1:4 ratio; filtered 24.1% is comfortable. Another reason to prefer the filtered series in any gate.
- **ribes2020/ribes2021 (carded):** the Ribes EY-vs-ratio figure reproduced here is already carded; the reconstructed EY(t) curve-shape "validation" leans on it — do not double-count.
- **pocketscience2024:** same community lineage (Gagné plotted that dataset); complementary axis (radial heterogeneity there, temporal resistance dynamics here).
- **smrke2024 (fines sweep):** COMPLEMENT — independent peer-reviewed evidence on fines vs. EY/time; Gagné adds machine traces but no PSD.
- **wadsworth2026.permeability / grindmap:** the D10-drives-k claim is qualitatively consonant with k(R, φ_p) fines sensitivity; no numbers here to conflict.
- **foster2025.infiltration:** the bloom-drips and capillary-uptake-∝-size² remarks are qualitative and add nothing to the sharp-front model; the 30 s bloom design usefully isolates post-wetting dynamics (a regime foster is silent on).
- Crema and slurry-temperature observations: no registry stage consumes them (same orphan class as andueza2007's foam data).

## Implementation estimate
Effort S for intake: fetch and parse the `.shot` archive, land per-shot summary CSV, flag Sobolik 2002 acquisition. The discriminating computation (μ(TDS(t))-driven R-decline vs. the two grinder arms) is a gate design consuming existing registered components + telisromero2001 closures — effort M, contingent on the traces landing. **LANDED (2026-07-23):** `gate_gagne2021_viscosity_discrimination` (analysis `puckworks/analysis/gagne2021_resistance.py`) computes the observed post-bloom R=P/Q decline (median ~2.7×) and bounds it with the telisromero2001 μ(TDS) closure — the decline is quantitatively matched by a μ decline from ~15% early TDS, so viscosity is **admissible but DEGENERATE** with bed compaction/swelling (the traces do not discriminate; no independent TDS(t)). A cleaner arm-separation / cameron-c(t)-driven variant is still owed.

VERDICT: data-only — a well-controlled 11-shot blind dataset with published DE1 traces that arms the kappa(t)-vs-viscosity-decline discrimination and flags Sobolik 2002 as a third G10 source, but whose own mechanistic chain is endpoint-anchored and circular — effort S.
