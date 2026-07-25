# Model card: Legas Muhammed 2021 — UV-Vis caffeine content and H₂O₂ scavenging, Habru woreda beans

**Paper/thesis:** Legas Muhammed B., Hussen Seid M., Tarekegne Habte A., "Determination of Caffeine and Hydrogen Peroxide Antioxidant Activity of Raw and Roasted Coffee Beans Around Habru Woreda, Ethiopia Using UV-Vis Spectroscopy," *Clinical Pharmacology: Advances and Applications* **13**:101–113 (2021). DOI: 10.2147/CPAA.S311032. Open access (CC BY-NC 3.0).
**Stage(s):** none (nominally *extraction*, as a bean-inventory data candidate only) · **Kind:** n/a (would be calibration at best)
**Status:** proposed (card-only)

## Scope and mechanism
An analytical-chemistry survey, not a process model. Green Arabica cherries from three kebeles
(Bohoro, Wurgisa, Girana) were sun-dried, hulled, split into raw/roasted halves, ground, sieved
<250 µm, and leached (2.5 g in 50 mL distilled water, 60 °C, stirred) for quantification of
caffeine by UV-Vis against a caffeine standard curve, in both the aqueous filtrate and a
dichloromethane liquid–liquid back-extract. A second assay measured hydrogen-peroxide scavenging
of the aqueous extract at 230 nm against ascorbic acid, summarised as IC₅₀. There is no transport
model, no time resolution, no bed, no pressure, and no espresso — a single endpoint leach and a
Beer–Lambert calibration.

## Governing equations
Only analytical relations are used; nothing here is "implemented" in any registry sense.

**(E1) Beer–Lambert calibration, aqueous** (paper, *Calibration Curve … Aqueous Phase*):
`A = 0.2789·C + 0.117`, R² = 0.9956, SD = 0.0352, N = 3, λ_max = 271 nm, linear range C ∈ [1, 6] ppm.

**(E2) Beer–Lambert calibration, dichloromethane** (paper, *Calibration Curve … Dichloromethane*):
`A = 0.1467·C − 0.3352`, R² = 0.9959, SD = 0.072, N = 3, λ_max = 274 nm, linear range C ∈ [4, 20] ppm.

Symbols: `A` absorbance (dimensionless) at the stated λ_max, 1 cm quartz cuvette; `C` caffeine
concentration in ppm (mg L⁻¹). Sample caffeine is obtained by inverting E1/E2 on the measured
absorbance.

**(E3) Method limits** (paper, *Method Validation*): `LOD = 3.3 σ/s`, `LOQ = 10 σ/s`, where `s` is
the calibration slope (absorbance per ppm) and `σ` the standard deviation of the y-intercept of the
regression line.

**(E4) H₂O₂ scavenging** (paper, *Hydrogen Peroxide Scavenging Activity*, transcribed as printed):
`Scavenging (%) = [(A_C − A_S)/A_C]·100`, with `A_C` the absorbance of the control (H₂O₂ in 0.1 M
phosphate buffer, pH 7.4, read at 230 nm after 10 min) and `A_S` that of the sample or standard.

**(E5) IC₅₀ by linear extrapolation** (implicit; Table 4). Per-sample the paper fits
`y = m·x + b` with `y` = % scavenging, `x` = extract concentration in ppm over 20–100 ppm, then
reports `IC₅₀ = (50 − b)/m`. All seven fitted intercepts exceed or nearly equal 50, so **every
reported IC₅₀ lies below the lowest measured concentration (20 ppm) and is an extrapolation**; see
Calibration and validation.

## Parameters
| symbol | value | units | source (measured/fitted/nominal/assumed) |
|---|---|---|---|
| λ_max, water | 271 | nm | measured |
| λ_max, CH₂Cl₂ | 274 | nm | measured |
| aqueous slope / intercept | 0.2789 / 0.117 | ppm⁻¹ / — | fitted |
| DCM slope / intercept | 0.1467 / −0.3352 | ppm⁻¹ / — | fitted |
| ε, water (as printed) | 54.16 | M⁻¹cm⁻¹ | fitted — **printed value is wrong by 10³; see below** |
| ε, DCM (as printed, mislabelled "in distilled water") | 28.49 | M⁻¹cm⁻¹ | fitted — same 10³ error |
| LOD / LOQ, water | 0.42 / 1.26 | ppm | fitted |
| LOD / LOQ, DCM | 1.63 / 4.94 | ppm | fitted |
| caffeine, aqueous (Table 1) | Bohoro 190.82±0.45 raw / 160.05±0.38 roast; Wurgisa 185.38±0.51 / 134.65±0.29; Girana 176.95±0.46 / 125.51±1.50 | ppm in extract | measured (n=3) |
| caffeine, DCM (Table 2) | Bohoro 198.00±2.09 / 184.08±3.05; Wurgisa 145.94±0.79 / 181.64±0.77; Girana 186.42±2.38 / 177.11±3.59 | ppm in extract | measured (n=3) |
| caffeine as mass fraction | 0.50–0.77 (aqueous), 0.68–0.80 (DCM) | % | derived — conversion factor not stated and not self-consistent |
| IC₅₀ (Table 4) | Bo raw 32.17; Bo roast 11.69; Wu raw 26.14; Wu roast 3.12; Gi raw 24.83; Gi roast 11.06; ascorbic acid 6.91 | ppm | fitted (extrapolated; one sign error) |
| % scavenging grid (Table 3) | 7 samples × {20, 40, 60, 80, 100} ppm, mean ± SD | % | measured (n=3) |
| leach conditions | 2.5 g grounds, 50 mL water, 60 °C, stirred, Whatman no. 40, 2× 15 mL wash | — | measured |
| sieve cut | <250 | µm | nominal (single sieve; no PSD) |
| dose basis / roast profile / grind setting / drying time | not provided (roast: "a local coffee roasting machine"; drying: 3 weeks sun) | — | — |
| bean variety | not provided ("without considering their varieties") | — | — |

## Calibration and validation offered by the source
The authors validate the *analytical method*, not any model, and even that validation does not
hold up on inspection. Reporting their own numbers:

- **Linearity** R² = 0.9956 (water, 1–6 ppm) and 0.9959 (DCM, 4–20 ppm), triplicate. Fine as far as
  it goes.
- **Range violation.** Sample caffeine is reported at 124–191 ppm (aqueous) and 145–200 ppm (DCM) —
  20–30× above the top aqueous standard and ~10× above the top DCM standard. The only stated
  dilution is 5 mL → 50 mL (10×), which does not bring the aqueous samples inside the calibrated
  band. Every reported concentration is therefore an extrapolation beyond the linearity check.
- **Molar absorptivity is dimensionally wrong.** Back-computing from the slopes (caffeine
  MW 194.19): 0.2789 ppm⁻¹ → ε ≈ 5.42×10⁴ M⁻¹cm⁻¹ and 0.1467 ppm⁻¹ → ε ≈ 2.85×10⁴ M⁻¹cm⁻¹. The
  paper prints 54.16 and 28.49 — a factor-10³ error. Separately, 5.4×10⁴ M⁻¹cm⁻¹ is ~5.6× the
  accepted caffeine ε near 273 nm (~9.7×10³), so the standard concentrations themselves are
  suspect. The DCM coefficient is also labelled "in distilled water" (copy error).
- **ppm → % conversion is not reproducible.** 124.01→0.50 %, 191.27→0.77 %, 200.09→0.80 % all imply
  ≈248 ppm per 1 %, but 145.15→0.68 % implies ≈213. No conversion basis (extract volume, dry mass)
  is given. The resulting 0.5–0.8 % dry-basis caffeine also sits below the usual Arabica green
  range (~0.9–1.4 %).
- **IC₅₀ values are extrapolations, and one has a dropped sign.** Recomputing (50 − b)/m from
  Table 4 reproduces every reported figure to two decimals — except Wurgisa roasted, where
  (50 − 51.096)/0.3518 = **−3.12 ppm**, reported as +3.12. The headline claim that Wurgisa roasted
  coffee out-scavenges ascorbic acid rests entirely on that sign flip. All seven IC₅₀s lie below the
  20 ppm minimum measured point, and the scavenging regressions are weak (R² 0.79–0.91 for the
  coffees).
- **Internal contradiction on the roast direction.** Aqueous data show roasted < raw at all three
  sites; DCM data show roasted > raw at Wurgisa (181.64 vs 145.94) and at Girana on a per-solvent
  comparison. The stated explanation — caffeine loss from "loss of organic matter resulting from the
  high solubility of caffeine in the extraction solvents" — is a non-sequitur, and roast mass loss
  should if anything *raise* caffeine per gram.
- **Statistics are decorative.** Paired t-tests are run on n = 3 with reported statistics such as
  t₂ = 1886.29 and t₄ = −8.89.61 (sic); Pearson r on three points carries no information.

No external comparison beyond citing other Ethiopian surveys; no held-out samples; no recovery/spike
study; no HPLC cross-check.

## Assumptions and validity range
- Batch leach at 60 °C, ambient pressure, unpacked loose powder, single endpoint. **Silent on** time
  dependence, flow, pressure, porosity, permeability, bed geometry, and every espresso-relevant
  variable.
- Single sieve cut (<250 µm) with no PSD, no fines fraction, no grinder identification — cannot be
  placed on the GrindState axis at all.
- Roast is uncharacterised (no temperature, time, mass loss, or colour), so the raw/roast contrast is
  not attributable to a defined roast level.
- Six samples, one origin region, unspecified variety, n = 3 analytical (not biological) replicates.
- Caffeine only as a species; the H₂O₂ assay is a lumped antioxidant proxy with no compound
  attribution, and no registry stage consumes it.
- Failure modes already realised in the paper itself: out-of-range calibration, ε off by 10³,
  non-reproducible ppm→% conversion, negative IC₅₀ reported as positive, roast direction contradicted
  between solvents.

## Interface mapping
Inputs consumed: none. No GrindState, BedState, MachineState, or MachineState.P_of_t field appears
in the study. Outputs produced: none. There is no contract field for per-species solute inventory
today (the same gap noted for bruno2026 and maille2024), and even if a `SoluteInventory` artifact
existed, this paper would supply a single, error-flagged caffeine number per sample with no
solubility, diffusivity, partition coefficient, or timescale — nothing extraction can be
parameterised from. No adapters worth specifying; no runtime coupling; no offline calibration chain.

## Extractable data
Low value, and only with the caveats above attached. Nothing is published as raw data or code
(no repository; all numbers are transcribe-from-PDF).

- **Table 3** — 7 samples × 5 concentrations × mean±SD % H₂O₂ scavenging. The only genuinely
  complete numeric grid in the paper, but the assay is an antioxidant-capacity measure with no
  registry consumer. **Do not transcribe.**
- **Tables 1–2** — six caffeine values per solvent. Would be a candidate for a green/roasted caffeine
  inventory reference except that the concentrations are extrapolated outside the calibration range
  and the dry-basis conversion does not reproduce. **Do not transcribe.**
- **Table 4** — regressions and IC₅₀. Reproduce only if a "known-error catalogue" is ever wanted:
  the sign-dropped Wurgisa IC₅₀ is a clean worked example of an extrapolated metric reported as a
  headline result.
- Figures 2–5 are spectra and calibration plots already fully described by E1/E2; Figures 6–8 are
  bar charts of Tables 1–3. Nothing to digitize.

## Overlaps and conflicts
- **bruno2026 (data-only) — superseded by it.** Bruno's Table 2 gives four roasted single origins ×
  nine species (caffeine, 3-CGA, 5-CGA, 3,5-diCGA, trigonelline, ferulic, tartaric, citric, acetic,
  in mg/kg) with replicate SDs. That is the roasted-bean inventory the extraction backlog wants;
  this paper offers one species, six samples, with a broken unit chain.
- **maille2024 (calibration) — superseded by it.** Maille supplies per-species extraction timescales
  (λ_fast/λ_slow for caffeine and 3-CQA plus three acids, with CIs and R²) and equilibrium
  concentrations at known brew ratios, i.e. kinetics. This paper has no time axis.
- **schmieder2023** already provides caffeine c₀ and λ on an actual espresso machine
  (c₀ = 9.71 mg g⁻¹, λ = 23.09 g); **angeloni2023** carries the 66-shot per-species dataset flagged
  for the multi-class-solute backlog. Both dominate this source on every axis.
- **Open backlog "extraction: multi-class solute chemistry"** — this paper gestures at the gap
  (caffeine + a lumped antioxidant proxy) but cannot close any part of it: no acids, no sugars, no
  time dependence, no espresso conditions.
- **cameron2020.extraction_bdf** — no interaction. Its lumped per-bed-volume inventory
  (EY ceiling 29.6 %) is untouched by a green/roasted caffeine assay with no dry-mass basis.
- Competes with nothing registered; complements nothing; adds no data the registry can use.

## Implementation estimate
Nothing to implement, nothing to gate, no dependencies. Effort to ingest as data would nominally be
S (two six-row tables plus a 7×5 grid), but the transcription is not worth doing: the caffeine
numbers cannot be converted to a dry-basis inventory with the information given, and the antioxidant
grid has no consumer. Cite only if a per-origin Ethiopian caffeine survey is ever needed as a
qualitative reference, and carry the errors above with it.

VERDICT: skip — an analytical-chemistry survey with no model, no time resolution and no espresso conditions, whose caffeine numbers are extrapolated 10–30× beyond their own calibration range with a 10³ molar-absorptivity error and a non-reproducible ppm→% conversion, and whose headline antioxidant result is a negative IC₅₀ reported as positive; bruno2026, maille2024, schmieder2023 and angeloni2023 already dominate it on solute inventory and kinetics — effort S.
