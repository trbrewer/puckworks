# Model card: abedi2025 — dry coffee-powder rheology characterization (TA Instruments blog)

**Paper/thesis:** B. Abedi, "Coffee Powder Rheology: The Rheological Journey of Coffee Powders from Bean to Brew," TA Instruments / Waters Corporation, "Rheology is Fun!" blog series, June 2, 2025. No DOI; vendor application blog, non-peer-reviewed, no methods section.
**Stage(s):** packing · **Kind:** calibration (nominally; nothing to run)
**Status:** card-only

## Scope and mechanism

Comparative dry-powder rheology characterization of coffee grounds on TA Instruments powder-rheometer accessories: compressibility vs normal stress, wall friction angle against stainless steel, confined flow energy vs rotor tip speed, and shear-cell cohesion / flow function. Two comparisons: fine vs coarse grind of one medium roast, and coarse grind of medium vs dark roast. All connections to espresso (hopper flow, dosing, tamping, puck formation, channeling, over-extraction) are qualitative narrative, not modeled or tested. There is **no model** in this source — it is a measurement showcase for the instrument line.

## Governing equations

None presented. The reported quantities are standard powder-characterization definitions (given here only so the numbers in Parameters are unambiguous; nothing is implementable):

- (A1, ours) Wall friction angle: φ_w = arctan(τ_w / N₁), the slope of a linear fit of wall shear stress τ_w vs normal stress N₁ (Fig 2, fitted over N₁ ≈ 0–10 kPa).
- (A2, ours) Compressibility: C(N₁) = percent volume reduction under normal stress N₁ (Figs 3, 8; reported at N₁ = 20 kPa).
- (A3, ours) Flow function: FF = σ₁ / σ_c, major principal (consolidation) stress over unconfined yield strength, from shear-cell yield-locus Mohr-circle construction (Figs 5, 6). Cohesion c = shear-stress intercept of the yield locus.
- Confined flow energy (Figs 4, 9): total energy (mJ) for a blade traversing the confined powder bed at a given tip speed; instrument-protocol quantity, no closed form given.

Nothing has been simplified away by us; there is nothing to simplify.

## Parameters

All values are figure annotations read from the published plots; no tables, uncertainties, or repeats are given anywhere.

| symbol | value | units | source |
|---|---|---|---|
| φ_w, fine medium roast (vs stainless steel) | 13.4487 | deg | measured (Fig 2 annotation) |
| φ_w, coarse medium roast (vs stainless steel) | 9.35069 | deg | measured (Fig 2 annotation) |
| C at 20 kPa, coarse medium roast | 13.40 | % | measured (Figs 3, 8) |
| C at 20 kPa, fine medium roast | ≈ 40 (curve read; printed label illegible in intake copy) | % | measured (Fig 3) |
| C at 20 kPa, coarse dark roast | 16.15 | % | measured (Fig 8) |
| Fine, consolidation 6000 Pa: cohesion / UYS / σ₁ / FF | 2035.97 / 9238.79 / 14993.8 / 1.62292 | Pa / Pa / Pa / — | measured (Fig 6) |
| Fine, consolidation 9000 Pa: cohesion / UYS / σ₁ / FF | 1981.42 / 8836.19 / 19423.9 / 2.19823 | Pa / Pa / Pa / — | measured (Figs 5, 6) |
| Fine, consolidation 15000 Pa: cohesion / UYS / σ₁ / FF | 1498.79 / 8112.19 / 32923.2 / 4.05848 | Pa / Pa / Pa / — | measured (Fig 6) |
| Coarse, consolidation 9000 Pa: σ₁ / FF | 33660.9 / 4.82867 | Pa / — | measured (Fig 5; cohesion and UYS annotations for coarse not legible in intake copy) |
| Confined flow energy | trends only: fine ≈ 27–40 mJ falling with tip speed 10–100 mm/s; coarse ≈ 40–57 mJ rising; dark roast slightly above medium (≈ 40–85 mJ over 10–155 mm/s) | mJ | measured (Figs 4, 9; no point values annotated) |
| Grind PSD (both grinds) | not provided | — | — |
| Coffee origin, dose, moisture, sample mass | not provided | — | — |
| Wall material roughness / coupon spec | not provided ("stainless steel" only) | — | — |
| Lateral stress ratio K (Janssen) | not provided (not measured) | — | — |

Erratum flag: Fig 9's caption says "**Un**confined flow energy" while the surrounding prose and Fig 4 say "confined flow energy" for the same test type — internal inconsistency in the source; the prose reading (confined) is almost certainly intended.

## Calibration and validation offered by the source

None. Single-run figure annotations; no repeats, no error bars, no comparison to any independent measurement, brewing outcome, or literature value. Every espresso-relevant claim (fine grounds → denser puck → slower flow → over-extraction; coarse → channeling; tamping improves flow function → better extraction) is untested narrative. The one internal-consistency element is the Fig 6 consolidation sweep, where FF rises monotonically with consolidation stress (1.62 → 2.20 → 4.06 over 6–15 kPa) — a plausible trend, but note cohesion is non-monotonic across the same sweep (2036 → 1981 → 1499 Pa) and no explanation or uncertainty is offered.

## Assumptions and validity range

- **Grinds are uncharacterized.** "Fine" and "coarse" have no PSD, no grinder, no setting, no d50. The values cannot be placed on any GrindState axis, which blocks quantitative reuse.
- **Dry powder only.** All measurements are pre-wetting. Nothing here transfers to the saturated puck under brew conditions; this is not coffee-liquor rheology (G10 concerns the liquid phase and is untouched).
- **Stress range under-spans espresso.** Consolidation/normal stresses are 6–20 kPa. A typical 10–20 kgf tamp on a 58 mm basket is ≈ 37–74 kPa, and 9 bar brew pressure loads the bed at ≈ 900 kPa — 1.5–2 orders above the measured range. All tamping/brewing implications are extrapolation.
- Single unspecified coffee per comparison; roast degree defined only as "medium"/"dark"; moisture and surface oil uncontrolled (both invoked in the narrative as explanations).
- Wall friction measured against one unspecified stainless-steel surface; portafilter/basket surface finish dependence unknown.
- Silent on: temperature, humidity, aging/degassing, dose-scale effects, any wetted or pressurized regime.

## Interface mapping

Inputs consumed: none map — GrindState carries no mechanical-property fields (cohesion, φ_w, FF, compressibility), and no registered component consumes them.
Outputs produced: none reach any contract. BedState.porosity could in principle be informed by a compressibility curve, but only with the stress–porosity relation for a *characterized* grind at tamp-relevant stress, which this source lacks on both counts.
Couplings: none viable, runtime or calibration. The only future home would be a tamping-mechanics component (Janssen-type wall stress transmission: needs φ_w **and** lateral stress ratio K; K is not measured here) — no such backlog item currently exists. Adapter question is moot.

## Extractable data

- The full quantitative content of the source is the ~15 figure-annotation values already transcribed into the Parameters table above. A separate `puckworks/data/` file is not warranted for a source of this provenance; this card is the transcription of record.
- No tables, no raw data, no code, no methods document. Figures only; the underlying test protocols are TA Instruments internal.
- If wall-friction values are ever needed at higher fidelity, the correct acquisition target is the peer-reviewed powder-flow literature on roasted coffee (Freeman FT4-class studies with reported PSDs), not this blog.

## Overlaps and conflicts

- **brewer2026.pack_generator (packing, calibration):** complement in principle, none in practice — the pack generator is purely geometric (overlapping spheres) and consumes no mechanical powder properties. Nothing here feeds it.
- **wadsworth2026.permeability (packing, calibration):** no overlap; k(⟨R⟩, φ_p) is geometric. This source's compressibility narrative (fine packs denser) is qualitatively consistent with the tamped-regime gap discussion but adds no usable stress–porosity closure.
- **Gap G10 (coffee-liquor rheology):** *not* addressed — dry-powder rheology, wrong phase. Do not count this against G10.
- **pocketscience2024 radial-evenness candidate gap:** the wall-friction narrative (fine grounds resist portafilter walls → uneven tamping) is a qualitative mechanism sketch in the same territory, hypothesis-level only, no radial measurements.
- Competes with and supersedes nothing.

## Implementation estimate

Nothing to implement. Revisit only if a tamping-mechanics / Janssen stress-transmission backlog item is opened, in which case the φ_w pair here serves as an order-of-magnitude prior while a properly characterized measurement (with PSD and K) is acquired. No gate applicable.

VERDICT: skip — vendor blog with figure-annotation-level data on uncharacterized grinds at sub-tamp stresses, feeding no contract, component, or backlog item; the salvageable point values are preserved in this card so nothing is lost — effort S.
