# Model card: Cordoba 2019 cold-brew factorial characterization

**Paper/thesis:** N. Cordoba, L. Pataquiva, C. Osorio, F. L. Moreno Moreno, R. Y. Ruiz, "Effect of grinding, extraction time and type of coffee on the physicochemical and flavour characteristics of cold brew coffee," *Scientific Reports* **9**, 8440 (2019). DOI 10.1038/s41598-019-44886-w. CC BY 4.0.
**Stage(s):** observables · **Kind:** calibration (offline empirical dataset; no physics executed)
**Status:** **reviewed 2026-07-25 — SKIP.** Cold immersion (20 °C, 14–22 h, unpressurized), no physics model, and its aggregate chemistry is superseded by angeloni2023's resolved per-species espresso data. No component, no gate, no transcription scheduled: **this card is the record.** Revisit only if immersion/cold brewing is admitted to scope, at which point Table 1 becomes a data-only intake.

## Scope and mechanism
Experimental (not mechanistic) study. A 2×2×2 factorial design — grind (coarse 701–900 µm vs medium 501–700 µm), contact time (14 h vs 22 h), coffee origin (Colombian Huila vs Nariño) — is run by **indirect immersion cold brew** (grounds in a filter bag, 20 °C, 60 g coffee / 700 g water) and characterized for total dissolved solids (TDS), extraction yield (EY), total phenolic content (TPC, Folin–Ciocalteu), pH, and total titratable acidity (TA). A hot French-press comparator (42.5 g / 500 g, boiling water) is measured for the same variables. Trained-panel (n = 3) sensory scoring and HS-SPME GC–MS relative-area volatile profiling round out the characterization. No extraction kinetics, mass-transfer, permeability, or packing model is proposed; the only equations are the standard Brix→solids and EY definitions used to reduce the measurements.

## Governing equations
Both from Methods; there is no physical model in the paper.

1. **Brix→soluble-solids (Moreno 2015, their ref 54):** X_S = 0.0087 · B
   - B — refractometer reading [°Brix]; X_S — soluble-solids mass fraction of the brew. Linear single-slope calibration; used to obtain TDS from Brix.

2. **Extraction yield (Wang 2016, their ref 5):** EY (%) = (TDS · W_b / W_gc) · 100
   - TDS — total dissolved solids of the brew (reported as % in Table 1); W_b — total mass of extract/beverage obtained [g]; W_gc — mass of dry ground coffee used [g].
   - *Unit-bookkeeping flag (not resolved by the authors): TDS is tabulated as a percentage yet the formula also multiplies by 100. Taken literally this double-counts the ×100 unless TDS enters as a fraction. This is the ordinary EY = beverage_mass · TDS_fraction / dry_dose relation with an ambiguous factor as printed; transcribe the numbers, not the formula's constant.*

TA and TPC are measurement protocols, not equations: TA = titration of 50 mL extract with 0.1 mol/L NaOH to pH 6.5, reported as mg chlorogenic-acid equivalents per g coffee (NTC 5247); TPC = Folin–Ciocalteu at 750 nm, reported as g/L gallic-acid equivalents. pH measured directly at 19 °C.

## Parameters
| symbol | value | units | source (measured/fitted/nominal/assumed) |
|---|---|---|---|
| Brix→solids slope | 0.0087 | (mass frac)/°Brix | fitted (Moreno 2015 calibration, imported) |
| coffee/water ratio (cold) | 60 / 700 | g / g | nominal (recipe) |
| coffee/water ratio (hot FP) | 42.5 / 500 | g / g | nominal (recipe, ratio-matched) |
| grind — coarse | 701–900 | µm (mean particle size) | measured (granulometric, NTC 2441) |
| grind — medium | 501–700 | µm | measured |
| contact time | 14 / 22 | h | nominal |
| cold-brew temperature | 20 | °C | nominal |
| hot-brew temperature | boiling (French press) | °C | nominal (not stated numerically) |
| sensory panel size | 3 | tasters | measured (design) |
| replication | 2×2×2 factorial, duplicate, triplicate measurement, n = 6 | — | design |
| PSD, porosity, permeability, flow rate, tamp | not provided | — | — (immersion; no bed physics measured) |

## Calibration and validation offered by the source
No model is validated — the paper reports measured effects with one-way ANOVA + LSD (95%, XLStat 2018.1). In their numbers: grind and time were significant (p < 0.05) for EY, TDS, TPC, pH, TA; coffee type significant only for pH and TA; grind was the largest-effect factor. Coarse grind + 22 h gave the highest cold-brew EY/TDS (e.g. Coarse-22h-Huila EY 20.39 %, TDS 2.04 %) and TPC (Coarse-22h-Nariño 1.50 ± 0.37 g/L). Cold-brew EY/TDS at coarse/22 h met or exceeded the hot comparators (Hot-Nariño EY 15.20 %, TDS 1.87 %); cold brews had uniformly higher pH (≈4.8–4.9 vs ≈4.4) and lower TA (≤0.90 vs ≈1.8–2.0 mg/g CGA) than hot. The counter-intuitive coarse>medium EY result is attributed **qualitatively** to caking of the medium grind inside the filter bag reducing diffusivity — an anecdotal mechanism, not measured or modeled, and confounded by the indirect-immersion filter-bag geometry. Panel n = 3 is very small; sensory and GC–MS conclusions are descriptive.

## Assumptions and validity range
- **Regime is cold immersion, not espresso:** 20 °C, 14–22 h, atmospheric pressure, loose grounds in a filter bag — no tamped puck, no pressure, no flow. None of the espresso stages (packing/machine/infiltration/flow) is exercised.
- Grind is two categorical bins (mean-size ranges only); no PSD, no fines fraction, no distribution shape.
- Chemistry is **aggregate**: TPC (lumped phenolics, gallic-acid eq.) and TA (lumped acidity, CGA eq.) — not per-species. pH is a single scalar.
- The caking/diffusivity explanation for coarse>medium is unquantified and specific to the filter-bag method; it does not generalize to a packed bed.
- Silent on: any time-resolved extraction curve (only 14 h and 22 h endpoints), temperature as a continuous variable (only cold 20 °C vs hot), permeability/flow, mass conservation, particle-scale transport.
- Failure mode if repurposed: using these EY/TDS/TA numbers as espresso targets is a regime error; the printed EY constant (Eq. 2) is unit-ambiguous.

## Interface mapping
Inputs consumed: none in physical terms — grind enters only as two labels; no GrindState/BedState/MachineState field is set. Outputs produced: EY_pct, tds_pct — but these are exactly the ShotResultState bookkeeping quantities the pipeline already computes; Eqs. 1–2 are the same definitions, not a new closure. TPC/TA/pH have no ShotResultState field. Couplings: none runtime, none offline — nothing to calibrate an espresso component against. No adapters warranted.

## Extractable data
- **Table 1** → 10 cold-brew conditions + 2 hot conditions × {TDS %, EY %, TPC g/L, pH, TA mg/g CGA}, mean ± 95% CI, n = 6. The only quantitatively clean table; **cold-brew regime**, so of no direct use to the espresso pipeline.
- **Tables 2–3** → global + attribute-level sensory scores (0–5), 10 conditions; panel n = 3.
- **Fig. 3** → HS-SPME GC–MS relative-area (%) volatile profiles for Coarse-14h Huila and Nariño (~34/30 compounds); relative areas only, no absolute quantities, no per-species mass.
- Availability: CC BY 4.0; "data contained within the article"; **no repository, no code, no raw traces**. Transcription is the only route.
- Not worth a data file under current (espresso) scope; flagged for revival only if cold/immersion brewing enters scope (cf. the moka-pot note in the roadmap).

## Overlaps and conflicts
- **cameron2020.extraction_bdf (no contact):** different regime (cold immersion vs pressurized espresso), no kinetics, no c_sat, no bed. Cannot validate or compete.
- **angeloni2023 (data-only) — supersedes on the chemistry axis:** Angeloni ships 66 espresso shots with 8 resolved chemical species (acids, CQAs, caffeine, lipids). This paper offers only lumped TPC + TA + pH on cold brew. For the "multi-class solute chemistry" backlog, Angeloni dominates; Cordoba adds nothing per-species and nothing in-regime.
- **grind backlog (PSD models):** two categorical bins, no PSD — no contribution.
- **"unsaturated flow / caking" backlog hypothesis:** the coarse>medium caking anecdote is thematically adjacent to the fines/incomplete-wetting discussion, but it is qualitative, confounded by the filter-bag method, and immersion-specific — corroborates a narrative at most, provides no data or model to parameterize it.
- **observables: temperature effects backlog:** only cold-vs-hot endpoints, cold-immersion regime — not an espresso thermal kernel.
- No contact with brewer2026.*, wadsworth2026.*, foster2025 (no packing, flow, permeability, or infiltration measured).

## Implementation estimate
No component; no gate. Effort to transcribe Table 1 would be trivial (S), but it lands on no espresso backlog slot and is out of regime, so no transcription is scheduled. Revisit only if immersion/cold or moka-pot brewing is admitted to scope, at which point Table 1 becomes a data-only intake.

VERDICT: skip — a cold-immersion (20 °C, 14–22 h, unpressurized, filter-bag) empirical DOE with no physics model, only the standard Brix/EY definitions already in ShotResultState, and aggregate (TPC/TA/pH) chemistry that angeloni2023 supersedes with resolved per-species espresso data; its lone mechanistic hint (coarse>medium via caking) is qualitative and method-confounded — effort S
