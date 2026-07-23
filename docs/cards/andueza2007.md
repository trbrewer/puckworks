# Model card: Andueza 2007 — coffee/water ratio effect on espresso physicochemistry + sensory

**Paper/thesis:** Andueza, S.; Vila, M.A.; de Peña, M.P.; Cid, C. "Influence of coffee/water ratio on the final quality of Espresso Coffee." *J. Sci. Food Agric.* **87**(4), 586–592 (2007). (DOI not printed on the provided copy; likely 10.1002/jsfa.2720 — unverified, do not cite as fact.)
**Stage(s):** extraction · observables · **Kind:** calibration (data source only, at most; nothing runtime)
**Status:** card-only

## Scope and mechanism
Empirical brew-ratio study — no model. Three ground coffees (A100 = 100 % Colombian Arabica; A20:R80 = 20:80 Arabica/Robusta; A20:R80 with 50 % Torrefacto Robusta) were brewed at three doses (6.5 / 7.5 / 8.5 g) into a **fixed 40 ± 2 mL** cup on an experimental *prototype* espresso machine (92 °C, 9 atm, 21 ± 3 s, 38 mm holder), and characterized for physicochemistry (pH, density, viscosity, surface tension, foam index/persistence, total solids, extraction %, soluble solids, lipids, caffeine, trigonelline, 5-CQA), 13 relative-% headspace volatiles, and a trained 10-judge descriptive/flavor-profile sensory panel. Twenty espressos per condition were **pooled** before analysis; ANOVA + Tukey per coffee. The stated aim is to select a preferred coffee/water ratio per coffee/roast from sensory rejection thresholds — not to model any physical process.

## Governing equations
None. Nothing to implement. The only quantitative definitions are registry-standard identities already in use elsewhere:
- Extraction (%) = 100 × (total solids in 40 mL cup) / (dry dose) — the EY mass-balance (cf. cameron2020, mckeonaloe2023, baristahustle2024).
- Foam index (%) = 100 × (foam volume) / (total beverage volume); persistence = time for the liquid line to reappear.

No transport, kinetic, dissolution, flow, or rheology relation appears anywhere in the paper.

## Parameters
No model parameters. Fixed experimental constants (the operating point any transcribed value would inherit):

| symbol | value | units | source |
|---|---|---|---|
| beverage volume (fixed) | 40 ± 2 | mL | nominal (protocol) |
| dose (design variable) | 6.5 / 7.5 / 8.5 | g | nominal |
| brew ratio (by volume) | ≈ 1:6.2 / 1:5.3 / 1:4.7 | g:mL | derived (dose : 40 mL) |
| inlet water temp | 92 (erogation 86 ± 2) | °C | nominal (imposed) |
| relative water pressure | 9 | atm | nominal (imposed) |
| extraction time | 21 ± 3 | s | measured (bracketed 18–24 s selection window) |
| holder filter diameter | 38 | mm | nominal |
| analytical replicates (n) | 6 | — | measured (of the pooled brew, not per-shot) |

## Calibration and validation offered by the source
No model, so nothing to validate. Statistical treatment is ANOVA + Tukey (p < 0.05) on the physicochemical/sensory means, with **n = 6 = analytical replicates of a pooled 20-shot brew** — i.e. instrument/assay repeatability, *not* shot-to-shot variability. There is no per-shot data, no flow trace, no time resolution, and no external comparison beyond narrative references to the authors' own earlier pressure/temperature/grind studies.

## Assumptions and validity range
- **Non-standard prototype machine**; flow conditions are not portable to any registry fixture (contrast DE1 fixture A used registry-wide).
- **Volume-based dosing** (fixed 40 mL cup), so "ratio" here is g:mL, not the mass ratio the registry works in; brew mass unknown (density given, so convertible ±).
- **Pooled brews** (20 shots mixed per condition) → no shot variability, no channeling signal, no traces.
- Only **three dose points** over a narrow, tight range (6.5–8.5 g).
- Robusta-heavy and **Torrefacto (sugar-added roast)** blends dominate two of three coffees — exotic relative to specialty-espresso registry sources.
- Beverage viscosity/density/surface tension measured on the **cooled (20 °C) finished cup** (post-emulsion, single Ostwald point, no shear-rate, no concentration or temperature series) — not in-bed liquor at brew temperature.
- Volatiles reported as **relative %** of total, not absolute concentrations — not usable as extraction targets.
- Silent on: everything mechanistic (grind PSD, packing, wetting, flow, transport kinetics), time dependence, and any coffee/machine outside this box.

## Interface mapping
Inputs consumed: none from the shot chain (dose, ratio, coffee identity are protocol inputs, not contract fields). Outputs produced: none under contracts v0.1. At most, Table 1 numbers could be read as loose `ShotResultState(EY_pct, tds_pct)` and beverage-property samples at three ratios. Couplings: offline only; nothing here is runtime, and no adapter is warranted.

## Extractable data
Assessed and **not recommended** for `puckworks/data/`:
- **Table 1** (physicochemistry, 3 coffees × 3 ratios): the EY / TDS / caffeine / trigonelline / 5-CQA / lipids series vs dose is **superseded** (see Overlaps). Transcription hazard noted regardless: in the provided text extraction, Table 1's third coffee (Torrefacto) shows only its 6.5 g column — the 7.5/8.5 columns were truncated in OCR and would need the original PDF.
- **Table 2** (13 volatiles): relative %, not absolute — no calibration value.
- **Table 3** + **Figure 1** (sensory descriptive ratings and flavor-profile % judges): subjective panel output; no physics consumer (sensory protocol/scoring already covered by baristahustle2024).
- The one genuinely **non-duplicated** content is the foam index / persistence and surface-tension series vs dose — but the registry has **no foam/crema or surface-tension stage or backlog slot**, so this is orphan data with no consumer.
- Raw data / code: none published (2007 print-era paper); tables/figure are the only record.

## Overlaps and conflicts
- **schmieder2023 (supersedes, chemistry):** DoE espresso on a DE1 with **brew ratio varied (4 levels)** and per-fraction caffeine / trigonelline / 5-CQA / TDS — the same species Andueza reports, on standard equipment with time resolution and an RSM fit. Higher fidelity on Andueza's exact axis.
- **pannusch2024 (supersedes, chemistry):** mechanistic multi-class transport for caffeine / trigonelline / CGA / TDS with fitted closures — again the same solute set, with a model attached.
- **angeloni2023 / egidi2024 (dominate, per-species):** richer 8-species and EY/TDS campaigns across T × p × grind; non-overlapping design, but far more solute detail than Andueza's 3 named compounds.
- **liang2021 (covers EY-vs-ratio):** characterizes extraction yield's brew-ratio dependence (flat in immersion, with a retention/measurement kernel) more rigorously than Andueza's ~1-pt EY dip across three pooled doses.
- **telisromero2001 / telisromero2000 / khomyakov2020 (dominate, G10 rheology):** the coffee-liquor viscosity/density stack — μ(T, X_w) and ρ/C_p/k/α closures plus an independent viscosity dataset across concentration and temperature. Andueza's single 20 °C finished-cup Ostwald point adds nothing to G10.
- **cameron2020.extraction_bdf (no competition):** Andueza has no model; its EY values (~19.8–22.3 %) sit well below cameron2020's 29.6 % ceiling and merely confirm plausibility.
- No conflict with any registered component; nothing here models anything, and every transcribable series is either superseded or has no registry consumer.

## Implementation estimate
None warranted. No model to port, no gate to build (nothing to reproduce), and no data slot to fill that a higher-fidelity source does not already fill. If a brew-ratio chemistry dataset is ever wanted, schmieder2023 is the intake; if beverage rheology, the telisromero/khomyakov stack; if EY-vs-ratio, liang2021.

VERDICT: skip — empirical brew-ratio study on a non-standard prototype rig with no model, whose chemistry (caffeine/trigonelline/5-CQA/TDS/lipids vs dose) is superseded by schmieder2023 and pannusch2024, whose EY-vs-ratio is covered by liang2021, and whose single-point 20 °C beverage rheology adds nothing to the telisromero2001/2000 + khomyakov2020 G10 stack, leaving only foam/surface-tension series that no registry stage consumes — effort –
