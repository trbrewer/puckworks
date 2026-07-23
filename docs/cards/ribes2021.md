# Model card: Ribes 2021 — three-zone radial extraction yield, BPLUS contact screen (DE1)

**Paper/thesis:** S. Ribes, "Espresso Extraction Radial Uniformity — BPLUS Contact Screen," slide deck, April 2021. No DOI; not peer-reviewed; vendor-adjacent (BPLUS is the tested product and a BPLUS stirrer is used in prep). 5 slides; no raw data file, no write-up beyond the slides.
**Stage(s):** bed_dynamics (radial extraction heterogeneity), observables (partitioned EY) · **Kind:** calibration (data source only)
**Status:** proposed (card-only)

## Scope and mechanism
Not a model. A destructive-sectioning experiment measuring extraction yield in **three annular zones** (center 0–18 mm, middle 18–25 mm, outer 25–29 mm radius) of spent DE1 pucks, comparing shots with vs. without a BPLUS contact screen placed **above** the puck, in two 20 g baskets (VST and Pullman). After each shot the puck is sectioned with ring cutters; each zone's remaining solubles are recovered by pouring hot water from a kettle (slide 2 photo sequence) and TDS-measured; zone EYs are back-computed. The mechanism probed: uneven top-surface water delivery (shower-screen impingement) under-extracts the perimeter; a contact screen redistributes inlet flow. Headline: without the screen, outer-zone extraction is limited to ~2/3 of center-zone extraction; with the screen the profile flattens and shot EY rises 2–3 points.

## Governing equations
None. Zone-EY back-calculation from immersion TDS is implied but nowhere written: no mass-balance chain, no retained-liquid correction, no scaling-to-shot-EY step is documented (contrast pocketscience2024, where the full workbook is published). The bar-chart light overlays (2%/4%/10% etc.) are deficits to a common 27% ceiling — every column sums to 27% in all four charts, so 27% is evidently a reference maximum EY used for plotting `[RS observation]`; its origin (max soluble content? best zone?) is not stated. A plotting construction, not physics; do not transcribe as data.

## Parameters
No model parameters. Measured zone EYs (read from slides 3–4 bar charts; radial coordinates from chart axes; replicate count per condition **not provided** — possibly n = 1):

| basket | contact screen | EY center 0–18 mm (%) | EY middle 18–25 mm (%) | EY outer 25–29 mm (%) | shot EY (%) | source |
|---|---|---|---|---|---|---|
| VST 20g | no | 25 | 23 | 17 | 22 | measured |
| VST 20g | yes | 26 | 24 | 22 | 24 | measured |
| Pullman 20g | no | 25 | 24 | 16 | 21 | measured |
| Pullman 20g | yes | 25 | 24 | 23 | 24 | measured |

**Consistency check `[RS]`:** area-weighting the zone EYs (uniform bed, zone area fractions 0.385/0.358/0.257 at 29 mm basket radius) reproduces shot EY within 0.3 pt for three conditions but gives 22.3% vs. the stated 21% for Pullman/no-screen — either the sectioning cut is not exactly at the chart radii by mass, replicates were averaged differently, or a rounding artifact. Also, Ribes states the outer zone is "ca. 30% of the total dose weight" vs. the 25.7% area fraction — the mass cut and the chart radii are not fully consistent; carry both numbers.

Protocol scalars (slide 5):

| quantity | value | units | source |
|---|---|---|---|
| machine / profile | DE1PRO v1.1, "Easy Blooming": 90 °C, bloom exit 2.5 bar, max 7.5 bar | — | nominal |
| shower hardware | S22A Ultem prototype + IMS CI 200 IM screen, 9.6 mm protrusion into basket | — | measured |
| grinder | Levercraft Ultra, SSP HU burrs, 100 RPM, setting 2.0 (100 µm above chirp) | — | nominal |
| dose / ratio | 19 g in 20 g basket, 1:2.0 | g, — | measured |
| prep | Levercraft WDT (8×0.4 mm needles) + BPLUS stirrer; PorcuPress v1 (109×0.8 mm); Bravo flat tamper 58.5 mm, 26 lbf | — | nominal |
| water | Montcalm: 4 ppm alkalinity, 10 ppm total hardness (eq. CaCO₃) | ppm | nominal |
| TDS metrology | Atago PAL, unfiltered, room temp, 3–5 readings averaged per sample | — | nominal |
| n per condition, retained-liquid correction, tamped bed depth | not provided | — | — |

## Calibration and validation offered by the source
None. No error bars, no replicate counts, no mass-balance closure check, no uncertainty statement anywhere in the deck. The 22→24% (VST) and 21→24% (Pullman) shot-EY increases are called "significant" without any statistics to support the word. All quality controls are procedural (frozen single-dosed beans, basket drying, TDS-reading averaging). Treat every number as a point estimate of unknown repeatability.

## Assumptions and validity range
- Three-zone radial resolution, no axial resolution; sub-structure within zones averaged away.
- Zone-EY method undocumented: immersion recovery efficiency, retained-liquid handling, and the shot-EY anchoring step are all unknown — cross-source comparison of absolute zone EYs (e.g., against pocketscience2024) is unsafe; the *pattern* (outer deficit, screen flattening) is the robust content.
- Unknown n; if n = 1 per condition, per-shot EY scatter of ±0.5–1 pt (typical for this workflow) is the same order as the middle-zone effects.
- Single machine (DE1PRO), single shower-screen geometry with an unusually deep 9.6 mm protrusion, single grind setting, single coffee, one operator. The screen effect is specifically the *contact-screen-above-puck* configuration; no dispersion-block or basket-hole-pattern variation.
- Very light prep confound: "light polishing" tamp only when the screen is absent — the no-screen condition differs in two ways, not one.
- Vendor adjacency (BPLUS product under test) is a provenance caveat, though the direction of the effect matches the independent pocketscience2024 result.
- Silent on: pressure/flow traces for these shots, puck resistance change from the screen, fines migration, temperature.

## Interface mapping
Inputs consumed: none. Outputs produced: none under contracts v0.1 — no radial coordinate exists in BedState/ShotResultState and no inlet-distribution descriptor in MachineState. Offline uses only:
- Secondary validation target for a future radially resolved bed_dynamics/extraction variant, alongside pocketscience2024: any two-zone or three-zone model that reproduces pocketscience's sign structure should also reproduce this deck's monotone center>middle>outer profile without a screen and its flattening with one.
- Prior-shaping caution for brewer2026.streamtube σ: same message as pocketscience2024 — a boundary-driven radial heterogeneity component that a grind-driven lognormal absorbs silently.
Coupling: offline data ingest only. Requires the same radial/inlet-uniformity contract extension flagged on the pocketscience2024 card before any component can consume it quantitatively.

## Extractable data
- The 4-condition × 3-zone table above → `data/ribes2021_radialEY.csv` (12 zone EYs + 4 shot EYs + zone radii). That is the entire quantitative content; transcription is already complete in this card, so a data/ file is optional bookkeeping.
- Raw data: not published, no workbook, no per-shot values. Availability-on-request unknown (author active in the Decent community; plausibly reachable).
- Shower-screen protrusion (9.6 mm) is a rare hardware datum — note it wherever headspace volume matters (machine backlog, Foster Eqs. 2–7 headspace term).

## Overlaps and conflicts
- **pocketscience2024 (closest sibling — complements):** same machine class (DE1), same destructive-sectioning idea, same qualitative finding (screen above puck mitigates edge under-extraction; edge deficit large without it). Ribes adds a **third radial zone** — the only 3-zone radial EY data on file, showing the deficit is concentrated in the outer 25–29 mm ring while the 18–25 mm middle is nearly flat — plus a VST-vs-Pullman comparison and a bloom-profile shot style. Pocketscience remains the primary dataset (published raw workbook, n = 5, error analysis); Ribes is corroboration at finer radial resolution and lower evidentiary grade.
- **cameron2020.extraction_bdf (complements):** further quantifies the cost of radial homogeneity — ~8–9 EY-pt center-to-outer spread without a screen, ~3 pt with.
- **brewer2026.streamtube (complements/cautions):** as with pocketscience2024, boundary-driven heterogeneity that σ(φ₁) conflates with grind-driven heterogeneity.
- **schulman2011 / mckeonaloe2022 / gap G9 (complements, weakly):** VST-vs-Pullman is a basket comparison at extraction level, but both are traditional-taper 20 g baskets and the no-screen difference (17% vs 16% outer) is within plausible noise — this does not discriminate basket geometry and does not inform G9 resistance.
- **foster2025.infiltration (complements):** non-uniform inlet delivery evidence, same as pocketscience2024; the 9.6 mm shower protrusion is a concrete headspace/inlet geometry datum.
- No conflicts with registered components; the Pullman/no-screen internal inconsistency (22.3 reconstructed vs. 21 stated) is a source-internal flag, not a registry conflict.

## Implementation estimate
Nothing to implement. Optional S-effort transcription of the 12-value table into data/. Gate design if adopted as secondary target: a radial extraction variant calibrated on pocketscience2024 should predict, zero-shot, the qualitative Ribes profile (outer/center EY ratio ≈ 0.65–0.7 without screen, ≥ 0.85 with) — a cheap cross-source generalization check, kept qualitative because Ribes's absolute zone EYs rest on an undocumented back-calculation.

VERDICT: data-only — no model and slide-grade provenance with unknown n, but the registry's only three-zone radial EY measurements, independently corroborating pocketscience2024's screen/edge findings at finer radial resolution — effort S
