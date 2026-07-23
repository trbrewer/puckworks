# Model card: Ribes 2020 — three-zone radial extraction yield, bottom paper filter and tamper-base shape (DE1)

**Paper/thesis:** S. Ribes, "Radial Uniformity of Espresso Extractions," slide deck, March 2020. No DOI; not peer-reviewed; community source (Decent ecosystem). 7 slides; no raw data file, no write-up beyond the slides. Predecessor of the April 2021 deck carded as ribes2021.
**Stage(s):** bed_dynamics (radial extraction heterogeneity), observables (partitioned EY) · **Kind:** calibration (data source only)
**Status:** proposed (card-only)

## Scope and mechanism
Not a model. The earlier of Ribes's two destructive-sectioning experiments: spent DE1 pucks are cut with ring cutters into **three annular zones** (center 0–18 mm, middle 18–25 mm, outer 25–29 mm radius — same cutters/radii as ribes2021), each zone's remaining solubles recovered by pouring hot kettle water over the section (slide 2 photo sequence), TDS-measured, and back-computed into a zone EY. Two interventions against a common baseline (flat tamper, no filter): (a) a **V60 paper filter below the puck** (between puck and basket floor — an *outlet-side* modification), and (b) a **convex ("US curve") tamper base** replacing the flat base (a packing-shape modification). Headline findings: at baseline, the outer ring (~1/4 of dose weight) extracts at roughly **half** the center EY (13% vs 25%); the bottom paper filter largely removes the outer deficit and raises shot EY 21% → 24%; the convex tamper worsens the deficit (outer 7%) and lowers shot EY to 20%. Slide 5 adds a speculative geometric argument: the Reneka Micro-Sieve basket's 40 mm perforated diameter gives 33% less perforated area than 49 mm (VST/IMS/Decent) baskets, offered as a candidate cause of its "typical 3-pt EY loss," with a proposal that enlarging perforated area 49 → 53 mm (+17%) would improve uniformity — an untested hypothesis, no experiment behind it.

## Governing equations
None. As with ribes2021, the zone-EY back-calculation is undocumented: no mass-balance chain, no retained-liquid correction, no scaling-to-shot-EY step. The light bar-chart overlays (1%/3%/13% etc.) are deficits to a common ceiling — every column in all three charts sums to **26%** `[RS observation]` (the 2021 deck used 27%, so the ceiling is coffee- or campaign-specific). A plotting construction, not physics; do not transcribe as data.

## Parameters
No model parameters. Measured zone EYs (read from slides 3–4 bar charts; radii from chart axes; replicate count **not provided** — "used twice in a row" on slide 6 refers to the tamping procedure, not replicates):

| condition | tamper base | bottom paper filter | EY center 0–18 mm (%) | EY middle 18–25 mm (%) | EY outer 25–29 mm (%) | shot EY (%) | source |
|---|---|---|---|---|---|---|---|
| baseline | flat | no | 25 | 23 | 13 | 21 | measured |
| bottom filter | flat | V60 paper | 25 | 24 | 22 | 24 | measured |
| convex tamper | US curve | no | 25 | 22 | 7 | 20 | measured |

**Consistency check `[RS]`:** area-weighting the zone EYs (uniform bed; zone area fractions 0.385/0.358/0.257 at 29 mm basket radius) reproduces the stated shot EY to 0.2 pt for baseline (21.2 vs 21) and filter (23.9 vs 24), but gives 19.3 vs the stated 20 for the convex condition — same order of internal slack as the Pullman anomaly on the ribes2021 card. Ribes's "outer = 1/4 of the total dose weight" matches the 0.257 area fraction, so here the mass cut and chart radii are mutually consistent (unlike the 2021 deck's "ca. 30%"). Outer/center EY ratios: 0.52 (baseline), 0.88 (filter), 0.28 (convex).

Protocol scalars (slides 3–4 footers, 6, 7):

| quantity | value | units | source |
|---|---|---|---|
| machine | DE1PRO v1.1, Cafelat 8.0 mm silicone gasket, IMS SI 200 IM screen (no spacer) | — | nominal |
| profile | hybrid "lever-blooming": 90 °C; preinfusion 6.0 mL/s until P > 2.5 bar; bloom 3.0 bar × 6 s; flow rise to 2.5 mL/s over 10 s (smooth); hold 2.5 mL/s × 45 s | — | nominal |
| grinder / setting | Mahlkönig EK43 S, SSP "High Uniformity" burrs (Silver Knight coating), EK 1.6, same setting all shots | — | nominal |
| dose / basket / ratio | 12 g in VST 15 g ridgeless; 1:2.5 | g, — | measured |
| prep | frozen single-dosed beans (Friedhats Ethiopia Semeon Abay); WDT with Londinium tool + Decent funnel, no vertical tapping, hog-tool surface raking; Force Tamper 58.5 mm smooth bases (flat or US curve), applied twice | — | nominal |
| water | Montille, adjusted to 50 ppm alkalinity / 125 ppm total hardness (eq. CaCO₃), Na₂CO₃ + Epsom salts | ppm | nominal |
| TDS metrology | Atago PAL zeroed on the adjusted water; unfiltered samples; room temp after vigorous stirring; 1 point = mean of 3–5 readings | — | nominal |
| Reneka perforated diameter vs precision baskets | 40 vs 49 | mm | nominal |
| n per condition, retained-liquid correction, tamped bed depth, shot time | not provided | — | — |

## Calibration and validation offered by the source
None. No error bars, no replicate counts, no uncertainty statement, no mass-balance closure check. Quality controls are procedural only (frozen single dosing, basket/screen drying, water standardization, 3–5 TDS readings per sample). The 21 → 24% (filter) and 21 → 20% (convex) shifts carry no statistics; treat every number as a point estimate of unknown repeatability. The Reneka/perforated-area argument (slide 5) is explicitly framed by the author as an assumption ("assuming that this could be the cause…") — it validates nothing.

## Assumptions and validity range
- Three annular zones, no axial resolution; sub-structure within zones averaged away.
- Zone-EY method undocumented (immersion recovery efficiency, retained-liquid handling, shot-EY anchoring unknown) — absolute zone EYs are not safely comparable across sources; the robust content is the **pattern** and the intervention **deltas**.
- Unknown n; if n = 1, middle-zone differences (23 vs 24 vs 22%) are within plausible per-shot scatter. Only the outer-zone effects (13 → 22 → 7%) are large relative to any credible noise floor.
- Single machine, single flow profile (2.5 mL/s hybrid lever-bloom), single grind setting, one light-roast coffee, one operator, one basket (VST 15 g at 12 g — an under-dosed configuration; headspace larger than nominal).
- The bottom-filter intervention changes at least three things at once: outlet-boundary flow distribution, fines retention at the exit face, and total bed resistance — the deck cannot separate them. No pressure/flow traces shown, so the resistance change is unquantified.
- Convex-tamper result is for one curvature ("US curve") only; no dose–curvature interaction explored.
- Silent on: shot times, fines migration, temperature effects, replicate variability, whether the paper filter changed debit at fixed profile.

## Interface mapping
Inputs consumed: none. Outputs produced: none under contracts v0.1 — no radial coordinate in BedState/ShotResultState, no inlet- or outlet-distribution descriptor in MachineState. Offline uses only:
- Secondary validation target for a future radially resolved bed_dynamics/extraction variant, alongside pocketscience2024 and ribes2021 — with a distinct role: this is the registry's only radial-EY dataset probing the **outlet boundary** (drainage through basket perforation vs paper interlayer) and **packed-surface shape** (tamper curvature), where the other two probe the inlet side (screens above the puck).
- Prior-shaping caution for brewer2026.streamtube σ: same message as the siblings — boundary-driven radial heterogeneity that a grind-driven lognormal absorbs silently when calibrated on shot-level EY.
Coupling: offline data ingest only. Requires the radial/inlet–outlet-uniformity contract extension already flagged on the pocketscience2024 card before anything can consume it quantitatively.

## Extractable data
- The 3-condition × 3-zone table above → `data/ribes2020_radialEY.csv` (9 zone EYs + 3 shot EYs + zone radii). That is the entire quantitative content; transcription is complete in this card, so a data/ file is optional bookkeeping.
- Raw data: not published; no workbook, no per-shot values. Availability-on-request unknown (same author as ribes2021; plausibly reachable via the Decent community).
- Reneka 40 mm vs 49 mm perforated diameters → one-line addendum to the schulman2011/mckeonaloe2022 basket-geometry ledger (G9); the 3-pt Reneka EY-loss figure is hearsay ("typical loss"), not a measurement — record the geometry, not the loss.
- The hybrid lever-bloom profile steps (slide 7) are fully specified and reproducible on a DE1 — worth noting as protocol metadata if this dataset is ever used as a gate.

## Overlaps and conflicts
- **ribes2021 (closest sibling — complements; same author, same sectioning method, same zone radii):** 2021 tested a contact screen *above* the puck at 19 g in 20 g baskets; this deck tests a paper filter *below* the puck and tamper-base shape at 12 g in a 15 g basket. Together they bracket both boundaries of the puck. Baseline outer/center ratios agree qualitatively (0.52 here vs ~0.65–0.68 there) despite different doses, grinders, and profiles — the outer-ring deficit is reproducible across the author's campaigns. Note: the ribes2021 card's claim of holding "the only 3-zone radial EY data on file" is superseded by this intake; amend on next registry-state revision.
- **pocketscience2024 (complements):** the primary radial dataset (published workbook, n = 5, error analysis) probed dispersion block, puck screen (above), and basket hole coverage. This deck adds the missing outlet-side intervention: a bottom paper filter flattens the profile as strongly as the best inlet-side treatments, evidence that edge deficit is not purely an inlet-delivery phenomenon — the drainage boundary matters too. Consistent in sign with pocketscience's finding that the full-coverage (Sworks) basket reduces edge loss.
- **gap G9 basket/screen resistance (complements):** the bottom-filter result and the Reneka perforated-area geometry both point at the exit boundary as a resistance/uniformity actor; adds motivation, no resistance numbers.
- **cameron2020.extraction_bdf (complements):** quantifies the radial-homogeneity cost at this configuration: 12-pt center-to-outer spread at baseline, 3-pt with a bottom filter, 18-pt with a convex tamper.
- **brewer2026.streamtube (complements/cautions):** as with the siblings — boundary-driven heterogeneity conflated into any σ(φ₁) fitted on shot-level data.
- **abedi2025 / packing stage (weak complement):** the convex-tamper result is the registry's only extraction-level datum on tamped-surface shape; packing components currently have no surface-curvature degree of freedom to validate against it.
- No conflicts with registered components. The 26% vs 27% plotting ceilings between the two Ribes decks are a source-internal presentation difference, not a data conflict.

## Implementation estimate
Nothing to implement. Optional S-effort transcription of the 9-value table into data/ plus the G9 geometry addendum. Gate design if adopted as secondary target: a radially resolved variant calibrated on pocketscience2024 should reproduce, zero-shot and qualitatively, (i) baseline outer/center ≈ 0.5 at this dose/profile, (ii) near-flat profile with an outlet-side permeable interlayer, (iii) worsened deficit under center-biased packing — kept qualitative because the absolute zone EYs rest on an undocumented back-calculation of unknown n.

VERDICT: data-only — no model and slide-grade provenance with unknown n, but the registry's only outlet-boundary and tamper-shape radial-EY interventions, corroborating the sibling decks' outer-ring deficit and extending the boundary-condition picture to the basket exit — effort S
