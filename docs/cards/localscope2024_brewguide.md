# Model card: localscope2024_brewguide — "How to Brew the Perfect Espresso" (SEO beginner guide)

**Paper/thesis:** Localscope / "Espresso Sim," *How to Brew the Perfect Espresso: A Complete Beginner's Guide*, undated web page (companion content to an interactive espresso-simulator web app). No DOI; marketing/SEO blog content, non-peer-reviewed, no author, no methods, no references.
**Stage(s):** observables (nominally — nothing maps cleanly) · **Kind:** calibration (nominally; nothing to run)
**Status:** card-only

## Scope and mechanism
A consumer-facing brewing primer enumerating six variables (dose, brew ratio, brew time, grind size, water temperature, roast level), their folk-wisdom "ideal ranges," qualitative interaction rules ("finer grind = longer brew," "high dose resists flow → increases brew time"), and a four-row troubleshooting table (sour/bitter/watery/weak → grind/time/ratio/dose fixes). The page exists to funnel readers to the vendor's simulator ("Launch the Simulator"); embedded "Keywords:" blocks after every section confirm it is SEO copy. There is **no model** in this source: no equations, no measurements, no data, no citations.

## Governing equations
None. The only quantitative construct is the brew-ratio definition (ratio = beverage yield / dose, e.g. 1:2 → 18 g in, 36 g out), which is already the registry's standard construction. The interaction rules in §7 are directional prose with no functional form. Nothing has been simplified away by us; there is nothing to simplify.

## Parameters
No model parameters. Transcribable content is a set of nominal recipe ranges, all uncited folk-standard values (inline transcription per registry convention for vendor/blog sources — no data file warranted):

| quantity | value | units | source type |
|---|---|---|---|
| brew pressure | 9 (asserted "usually") | bar | nominal |
| beverage yield per shot | 25–40 | g | nominal |
| dose (double shot) | 16–20 (start 18) | g | nominal |
| brew ratio ideal / ristretto / lungo | 1:2 / 1:1.5 / ≥1:2.5 | out:in | nominal |
| brew time ideal / too-fast / too-slow | 25–30 / <20 / >35 | s | nominal |
| water temperature ideal / low / high | 89–94 / <88 / >94 | °C | nominal |
| any measured EY, TDS, flow, or sensory outcome | not provided | — | — |

## Calibration and validation offered by the source
None. No measurements, no data, no references, no evidence of any kind. Every claim is asserted. The taste-defect attributions (sour = under-extracted, bitter = over-extracted) are the standard barista heuristic, stated without support.

## Assumptions and validity range
- All ranges are uncited convention; provenance is presumably the general specialty-coffee canon, but no source is named.
- Pressure is stated once (9 bar) with no profile, machine, or basket context.
- Silent on: everything mechanistic — grind PSD, packing, permeability, wetting, transport kinetics, pressure/flow profiles, channeling physics, water chemistry, and any quantitative outcome whatsoever.
- The roast-level and temperature guidance is directional only and partly contradicts finer-grained sources already in the registry (e.g., no temperature dependence data of any kind vs. the measured series elsewhere).

## Interface mapping
Inputs consumed: none. Outputs produced: none under contracts v0.1. The nominal ranges duplicate defaults the registry already carries from measured sources (fixture recipes, MachineState conventions). Couplings: none; no adapter warranted. Nothing here could gate, calibrate, or seed any stage.

## Extractable data
None recommended. No tables or figures contain measured data; the troubleshooting table is qualitative. The linked "interactive espresso simulator" was not inspected (login-gated web app, no model documentation on the page); if the vendor ever publishes the simulator's underlying model, that would be a separate intake target — this page describes only its marketing wrapper.

## Overlaps and conflicts
- **Registry-wide recipe conventions:** the dose/ratio/time/temperature ranges are strictly dominated by measured protocol values already registered (Cameron 2020 recipes with the pressure-node convention, DE1 fixture A traces, Pocket Science 2024 shot logs). Nothing here adds precision or provenance.
- **mckeonaloe2023.md / baristahustle2024.md / abedi2025.md (sibling non-model sources):** those at least contributed a derived observable, a protocol standard, or instrument measurements respectively; this page contributes none of the three. It is the weakest source class yet taken through intake.
- No conflicts worth logging: directional claims (finer → slower flow, hotter → more bitter) are consistent with registered physics at the sign level and carry no magnitudes to conflict with.

## Implementation estimate
Nothing to implement. No gate design possible — no quantitative claims exist to test.

VERDICT: skip — SEO marketing copy with zero equations, data, or citations; every nominal range it states is already covered by measured registry sources — effort S
