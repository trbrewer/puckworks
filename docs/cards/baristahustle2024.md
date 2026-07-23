# Model card: Barista Hustle Cupping Protocols 2024 — sensory QC protocol + 100-point scoresheet

**Paper/thesis:** Barista Hustle, "Barista Hustle Cupping Protocols: A New Scoring System for Coffee," baristahustle.com, dated 10 Jan 2024 (filename `Barista-Hustle-Cupping-Protocols-10_01_2024`). No DOI; commercial/educational publication, not peer-reviewed. Author is a corporate entity; cited literature is secondary (sensory-science review, not new measurement).
**Stage(s):** observables (sensory scoring + TDS/EY collection protocol) · **Kind:** calibration (protocol/reference only — neither runtime nor a fitting-data provider)
**Status:** proposed (card-only)

## Scope and mechanism
Not a model, and not a dataset. Two artifacts: (1) a **cupping brew protocol** — immersion, 55 g/L brew ratio (10 g coffee, ~180 ml water per bowl), fixed crust-break at 5:00, TDS-sample draw at 8:00, sensory scoring once below ~65 °C; and (2) a **100-point sensory scoring rubric** — ten categories (aroma, flavour, aftertaste; sweetness, acidity, bitterness; weight, texture, afterfeel; balance), each scored 7.5–10 at 0.1 resolution, no deductions and no separate "overall," with disqualification if any category falls below 7.5. The remainder of the document is a sensory-science justification (odorant volatility/polarity, titratable vs. pH acidity, bitterness chemistry, astringency, mouthfeel) plus a 37-compound aroma appendix. It defines *how a human panel measures organoleptic quality and collects TDS*, not any physical process in the puck.

## Governing equations
None to implement. There is no extraction, flow, or transport relation anywhere in the document. The only quantitative construct is the **TDS→EY link implicit in the protocol** (grind "to bring your best coffees above 20% extraction yield after 8 minutes"): EY = brew mass × TDS / dose, the standard mass-balance identity already used registry-wide (e.g., cameron2020, pocketscience2024) — not original here, and for an *immersion* cup, not an espresso puck. The ten-category score is an ordinal human judgement with no functional form. Any mapping from puck-side observables to these sensory scores would be a registry-side construction `[RS]`, and the source offers nothing to fit it with.

## Parameters
No model parameters. The transcribable content is a set of **protocol constants** and a **sensory-scale definition**; none are measured coffee outcomes.

| quantity | value | units | source type |
|---|---|---|---|
| brew ratio | 55 | g/L | nominal (protocol spec) |
| dose per bowl | 10 | g | nominal |
| water per bowl | 180 (accept 150–200) | ml | nominal, ±2 g fill tolerance |
| dose weighing tolerance | ±0.1 | g | nominal |
| brew water pH | 7.0–7.4 | — | nominal (spec) |
| brew water buffer | ≤70 | ppm | nominal (spec) |
| crust break time | 5:00 | mm:ss | nominal |
| stirs at crust break | 4 | count | nominal |
| TDS-sample draw time | 8:00 | mm:ss | nominal |
| TDS-sample volume / draw depth | 5 / 1 | ml / cm below surface | nominal |
| scoring start temperature | ~65 (≈10:00) | °C | nominal |
| tasting passes | 65 / 55 / 45 | °C | nominal |
| flavour/aftertaste ceiling temp | <71 | °C | nominal (scald limit, Brown & Diller) |
| acidity/body/balance eval temp | 60–70 | °C | nominal (per SCA) |
| target EY (grind-setting anchor) | >20 @ 8 min | % | nominal (setup target, not a measurement) |
| scoring categories | 10 (3 aroma, 3 taste, 3 tactile, 1 balance) | count | scale definition |
| per-category range / resolution | 7.5–10 / 0.1 | points | scale definition |
| disqualification threshold | <7.5 in any category | points | scale definition |
| negative-trait threshold | <8.0 | points | scale definition |
| specialty expectation | >80 | points | scale definition |
| aroma appendix | 37 compounds (name, chemical class, odour descriptor, volatility order) | — | secondary (Flament 2002; Yang et al. 2016) |
| any measured coffee TDS / EY / sensory result | not provided | — | — |

## Calibration and validation offered by the source
None. No coffees were measured; there are no TDS numbers, no EY numbers, no panel scores, no inter-rater reliability data. The document *asserts* a scale and cites sensory-science literature (Blank/Sen/Grosch 1992, Lingle 2011, Rao & Fuller 2018, Frank/Hofmann bitterness chemistry, Navarini surfactant work, etc.) to justify category choices, but performs no validation of its own scoring system — no correlation to composition, no reproducibility study, no anchor references. As a *measurement standard* it is only face-valid: it prescribes a procedure without demonstrating that following it discriminates coffees reproducibly. Treat it as a protocol document, not evidence.

## Assumptions and validity range
- **Immersion cupping, not espresso.** 55 g/L, no pressure, no puck, no flow — the registry's stages (packing/machine/infiltration/flow/bed_dynamics) have no analogue in this brew. The embedded TDS/EY relation is for a steeped bowl; it does not transfer to an espresso puck.
- **Human sensory instrument.** The ten scores are ordinal panel judgements; the document itself cites large inter- and intra-individual olfactory variability (Keller et al. 2012) and offers no quantitative reliability. Silent on how many panelists, calibration reference sets, or score aggregation.
- **No composition→perception model.** It repeatedly notes perception is not what a puck-side model predicts (perceived acidity tracks *titratable* acidity, not pH; perceived sweetness is largely aroma-driven, not sugar; perceived body is viscosity plus non-viscous factors). These are cautions *against* naïve chemistry→sensory mapping, not a mapping.
- **Protocol constants are targets, not data.** The ">20% EY after 8 min" figure is a grind-setting instruction, not a reported measurement of any coffee.
- Silent on: any numerical coffee result, refractometer make/calibration, TDS-model, grind PSD, and everything downstream of "collect a score."

## Interface mapping
Inputs consumed: none. Outputs produced: none under contracts v0.1. `ShotResultState` carries `EY_pct`, `tds_pct` but no sensory field and no organoleptic dimension; there is no cupping/immersion context anywhere in the stage set. All possible uses are offline and definitional:
- If the **observables** stage is ever extended with a sensory/organoleptic output, this document is a candidate reference for the *category vocabulary and collection procedure* (what "acidity," "bitterness," "afterfeel" would mean and how TDS is sampled) — but not for any values to populate it.
- The TDS-draw procedure (5 ml, 1 cm depth, syringe-filter, post-scoring read) is a **measurement-kernel** reference for the backlog's "scale/measurement kernels" line, again procedural only.
Coupling: none runtime; no data ingest of substance; no adapters (nothing to adapt). A contract extension (a sensory-outcome field) plus a real composition→sensory dataset would both be prerequisites before anything here could be consumed quantitatively.

## Extractable data
Effectively nothing of registry value. Optional, low-priority transcriptions if a sensory/observables *reference* is ever wanted:
- The **protocol-constants table** above → could seed a `data/protocols/` entry documenting the BH immersion-cupping method (procedural metadata, not measurements).
- The **37-compound aroma appendix** (name, chemical class, odour descriptor, volatility rank) → a sensory lexicon, but it is **secondary** (compiled from Flament 2002 and Yang et al. 2016) and unrelated to extraction physics; prefer the primary sources if this is ever needed.
- No raw data, no code, no measured coffee outcomes are published — there is nothing to reproduce or gate against.

## Overlaps and conflicts
- **Open backlog "extraction: multi-class solute chemistry — makes sensory claims testable" (adjacent, does not advance):** this is the *sensory* half that backlog item wants to become testable *against*, but it supplies only a scoring rubric, no composition data and no compound→score mapping — it names the target without providing the linkage. Its titratable-acidity-≠-pH and aroma-driven-sweetness cautions are useful design constraints for that future item.
- **Open backlog "observables: temperature effects; scale/measurement kernels" (adjacent, procedural only):** contributes tasting-temperature staging (65/55/45 °C) and a TDS-draw kernel as *procedure*, not as any model of a temperature or measurement effect.
- **pocketscience2024 / mckeonaloe2022 / cameron2020 (no overlap):** those carry measured EY/geometry on espresso; this carries neither measurements nor espresso. The shared EY = mass·TDS/dose identity is generic and already registered elsewhere.
- Competes with / supersedes: nothing. Duplicates: nothing (it is a protocol, not a lower-fidelity re-do of a registered component).

## Implementation estimate
Effort S *if* the optional reference transcription is ever wanted (protocol constants + aroma list are already reproduced above); otherwise zero. No gate is possible — there is nothing to reproduce. No dependencies. The registry's value ceiling is validation data; this document contributes none.

VERDICT: skip — a human sensory QC protocol and 100-point scoresheet for immersion cupping, with no model, no espresso relevance, and no measured data; useful only as a procedural/vocabulary reference if an observables sensory field is later added, which can be lifted from this card without registering a component — effort S.
