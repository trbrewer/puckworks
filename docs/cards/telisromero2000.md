# Model card: Telis-Romero 2000 coffee-extract thermophysical properties

**Paper/thesis:** Telis-Romero, J., Gabas, A.L., Polizelli, M.A., Telis, V.R.N.
"Temperature and water content influence on thermophysical properties of coffee
extract." *International Journal of Food Properties* 3(3) (2000) 375–384.
DOI: 10.1080/10942910009524643.
**Stage(s):** flow (liquor density closure) · observables (thermal-property
closures for the "temperature effects" backlog) · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
Empirical correlations for four thermophysical properties of aqueous coffee
extract — density ρ, specific heat C_p, thermal conductivity k, thermal
diffusivity α — as simultaneous functions of temperature T (30–82 °C) and water
content X_w (0.49–0.90 mass fraction, wet basis). Measured on one industrial
soluble-coffee extract batch (51 °Brix, COCAM, Brazil; 47.6 % moisture as
received) diluted with distilled water: 10 water contents × 4 temperatures = 40
points per property. ρ by pycnometry; k and C_p in one coaxial-cylinder cell
(Bellet et al. 1975) at steady and unsteady state respectively; α directly by
Dickerson's (1965) transient method. This is the companion paper to the
registered telisromero2001 rheology card (same material system, same group) and
closes the acquisition target flagged in that card's Extractable-data section.
No mechanism — pure property fits.

## Governing equations
All fits with T in **°C** and X_w a **mass fraction** (0–1), unlike
telisromero2001 where X_w is a percentage — see normalization hazard below.
Two forms per property: a direct polynomial/linear fit, and a water-referenced
form that carries the temperature dependence through pure-water properties
(ρ_w, k_w, α_w at T).

- (1) ρ = 1422.57 − 451.98 X_w − 0.16 T  [kg/m³], r² = 0.981
- (2) ρ = ρ_w(T) · (1.44 − 0.46 X_w)  [kg/m³], r² = 0.967
- (3) C_p = 1439.65 + 2633.72 X_w + 1.99 T  [J/(kg·°C)], r² = 0.993
- (4) k = 0.154 + 0.391 X_w + 1.48×10⁻⁴ T  [W/(m·°C)], r² = 0.986
- (5) k = (k_w(T) · ρ/ρ_w(T)) · (0.0556 + 0.794 X_w)  [W/(m·°C)], r² = 0.923
- (6) α = 7.92×10⁻⁸ + 5.93×10⁻⁸ X_w + 0.0212×10⁻¹⁰ T  [m²/s], r² = 0.944 —
  **suspected exponent typo, see below**
- (7) α = 9.11×10⁻⁸ + (α_w(T) − 9.77×10⁻⁸) X_w  [m²/s], r² = 0.931
- (8) α = k/(ρ C_p) — definition, used by the authors as a cross-check, not a fit
- (9) Δ%error = (α_cal − α_exp)·100/α_exp — error metric for the (8)-vs-measured
  comparison

Symbols: ρ extract density (kg/m³); ρ_w pure-water density; C_p specific heat
(J/kg·°C); k thermal conductivity (W/m·°C); k_w pure-water conductivity; α
thermal diffusivity (m²/s); α_w pure-water diffusivity; X_w water mass fraction
(wet basis); T temperature (°C). The water-referenced forms (2), (5), (7)
require external ρ_w(T), k_w(T), α_w(T) tables (standard steam/water data; not
supplied in the paper).

**Suspected typo in Eq. (6), documented at intake:** as printed, the temperature
coefficient 0.0212×10⁻¹⁰ contributes only ~1.1×10⁻¹⁰ m²/s over the full 30→82 °C
span, ~100× too small to reproduce the temperature spread in Figure 5
(≈1.9×10⁻¹⁰ m²/s per °C: e.g. 1.16→1.26×10⁻⁷ at X_w = 0.49). With the
coefficient read as 0.0212×10⁻⁸ (= 2.12×10⁻¹⁰ per °C), Eq. (6) reproduces
Figure 5 endpoints within plotting accuracy (X_w = 0.90, 82 °C → 1.50×10⁻⁷
predicted vs ≈1.47–1.50 plotted; X_w = 0.49, 30 °C → 1.15×10⁻⁷ vs ≈1.16
plotted). Implement the corrected coefficient; record both. (Same failure class
as the grudeva2025 Issue 2a pressure-unit typo.)

## Parameters
| symbol | value | units | source (measured/fitted/nominal) |
| --- | --- | --- | --- |
| Eq. 1 intercept | 1422.57 | kg/m³ | fitted (r² = 0.981) |
| Eq. 1 X_w coeff. | −451.98 | kg/m³ | fitted |
| Eq. 1 T coeff. | −0.16 | kg/(m³·°C) | fitted |
| Eq. 2 coefficients | 1.44, −0.46 | – | fitted (r² = 0.967) |
| Eq. 3 intercept | 1439.65 | J/(kg·°C) | fitted (r² = 0.993) |
| Eq. 3 X_w coeff. | 2633.72 | J/(kg·°C) | fitted |
| Eq. 3 T coeff. | 1.99 | J/(kg·°C²) | fitted |
| Eq. 4 intercept | 0.154 | W/(m·°C) | fitted (r² = 0.986) |
| Eq. 4 X_w coeff. | 0.391 | W/(m·°C) | fitted |
| Eq. 4 T coeff. | 1.48×10⁻⁴ | W/(m·°C²) | fitted |
| Eq. 5 coefficients | 0.0556, 0.794 | – | fitted (r² = 0.923) |
| Eq. 6 intercept | 7.92×10⁻⁸ | m²/s | fitted (r² = 0.944) |
| Eq. 6 X_w coeff. | 5.93×10⁻⁸ | m²/s | fitted |
| Eq. 6 T coeff. | 0.0212×10⁻¹⁰ as printed; 0.0212×10⁻⁸ suspected correct | m²/(s·°C) | fitted (typo flag above) |
| Eq. 7 coefficients | 9.11×10⁻⁸, 9.77×10⁻⁸ | m²/s | fitted (r² = 0.931) |
| copper cell ρ′, C_p′ | 8890 / 8886; 403.4 / 406.6 | kg/m³; J/(kg·°C) | measured (water / glycerin calibration; apparatus constants, not extract properties) |
| ρ_w(T), k_w(T), α_w(T) | not provided | – | external water-property tables required for Eqs. 2, 5, 7 |

## Calibration and validation offered by the source
- Fit quality is r² on the authors' own 40-point grids only: 0.981 (Eq. 1),
  0.967 (2), 0.993 (3), 0.986 (4), 0.923 (5), 0.944 (6), 0.931 (7). No held-out
  data, no independent dataset, no replicate batches. This is post-fit
  reconstruction at best — the weakest rung.
- Apparatus calibration: coaxial cell calibrated with distilled water and
  glycerin; the two calibrations agree on the copper constants within ±2 %.
- Internal consistency check (Eqs. 8–9): α computed as k/(ρC_p) from the
  measured triplet is systematically **lower than directly measured α — mean
  −11.35 %, s = 3.87 %**, worsening at higher T. The authors attribute this to
  convection in the Dickerson cell inflating the direct α measurements. So the
  direct-α correlations (6)/(7) and the (ρ, C_p, k) set are mutually
  inconsistent at the ~11 % level, and the authors' own explanation implies the
  direct α data are the biased ones.
- Authors' recommendation (Conclusions): use Eqs. 2, 3, 5, 7 — i.e. the
  water-referenced forms for ρ, k, α despite their *lower* r², presumably for
  better temperature behavior via water properties. The card does not upgrade
  this to a validated claim; it is a stated preference.

## Assumptions and validity range
- Material caveat (inherited verbatim from telisromero2001): industrial
  soluble-coffee extract, not fresh espresso liquor — no emulsified oils,
  suspended fines, or dissolved CO₂; industrial extraction hydrolyzes more
  polysaccharides. Treat as a prior with unquantified composition bias.
- Validity box: X_w 0.49–0.90 (solids 10–51 % w/w), T 30–82 °C. Espresso-strength
  liquor (TDS 8–12 %, X_w 0.88–0.92) sits at the **upper edge** of the
  concentration range; brew-strength and weaker liquor is extrapolation toward
  water. Espresso brew temperatures (88–96 °C) are extrapolation above 82 °C —
  mild for the linear fits, unquantified.
- The direct linear fits do NOT extrapolate to pure-water values at X_w = 1:
  Eq. (4) gives k ≈ 0.56 W/(m·°C) at X_w = 1, 82 °C vs ≈ 0.67 for water (−16 %);
  Eq. (2) gives 0.98 ρ_w; Eq. (5) gives ≈ 0.85 k_w. Do not use below ~10 %
  solids. Eq. (3) is the best-behaved at the water limit (≈ 4133 vs 4178
  J/kg·°C at 30 °C).
- Single batch, single supplier, no composition characterization beyond
  moisture. No pressure dependence (espresso liquor sees up to ~9 bar; effect
  on liquid properties is genuinely negligible, but stated nowhere).
- Silent on: sub-30 °C behavior (cold-start transients), crema/foam, and any
  solid-phase (puck) thermal properties — this is the *liquor* only. Puck
  effective thermal properties would need a porous-medium mixing rule this
  paper does not provide.
- **Normalization hazard (for the roadmap P1 table):** X_w is a fraction here
  but a percentage in telisromero2001's Eqs. (10)/(12)/(13). Feeding
  fraction-form X_w into the 2001 closures (or vice versa) produces errors of
  10²·⁶–10⁶·⁰⁷ magnitude. Any shared TDS→X_w adapter must carry an explicit
  units field.

## Interface mapping
Inputs consumed: local liquor solids concentration from the extraction stage
(adapter: X_w = 1 − TDS/100, fraction form) and temperature T — T is still not
a contract field (observables backlog "temperature effects").
Outputs produced: ρ, C_p, k, α of the liquor phase. No current BedState /
MachineState / ShotResultState field carries any of these; all registered flow
components assume constant water properties.
Couplings: OFFLINE CALIBRATION provider only; no runtime coupling forced.
Consumers, in likely order of use: (i) any future thermal shot model under the
"temperature effects" backlog item (C_p and k of the liquor are its closure
terms); (ii) density consistency for Darcy chains and foster2025 mass budgets —
at shot TDS (X_w ≈ 0.90, 82 °C) Eq. (1) gives ρ ≈ 1003 kg/m³, a ≤1 % correction
over water, i.e. negligible for flow but relevant if a mass-budget gate (grudeva
Issue 4 class) converts beverage mass to volume at concentrated first-drip
conditions (X_w = 0.49 → ρ ≈ 1196 kg/m³, a 20 % effect); (iii) paired with
telisromero2001 μ(T, X_w) to give a complete, mutually consistent liquor
property set from the same material batch family.
Implementation note: pick ONE α path — either α ≡ k/(ρC_p) from Eqs. (1)/(3)/(4)
(self-consistent) or Eq. (6)/(7) (direct but convection-biased per the authors)
— never mix, given the documented −11.35 % systematic offset.

## Extractable data
- No tables — all 4 × 40 experimental values are published only as Figures 2–5.
  Digitization targets, in value order: Fig. 2 (ρ) and Fig. 3 (C_p) — clean,
  low-scatter, worth transcribing to data/telisromero2000_fig2_density.csv and
  _fig3_cp.csv if the correlations are ever re-fitted or gated; Fig. 4 (k) —
  moderate scatter; Fig. 5 (α) — contains BOTH measured and Eq.-(8)-calculated
  series (filled vs open symbols), which is the only quantitative record of the
  −11.35 % offset and the evidence base for the Eq. (6) typo diagnosis: highest
  diagnostic value despite the bias.
- The correlations themselves carry most of the paper's value; digitization is
  optional until a gate needs residuals.
- Raw data/code: not published, not offered. Companion rheology data: already
  carded (telisromero2001).

## Overlaps and conflicts
- COMPLEMENTS telisromero2001 (registered card, calibration-provider): together
  they give μ, ρ, C_p, k, α of coffee liquor as f(T, X_w) from one material
  system — the complete fluid-property closure set for gap G10 and the
  observables "temperature effects" backlog. This paper closes the acquisition
  target explicitly flagged in telisromero2001.md.
- Partially serves the observables backlog "temperature effects": provides the
  liquor-side property closures a thermal model needs, but no puck-side
  (solid/effective-medium) properties and no heat-transfer model — the backlog
  item is NOT closed by this card.
- COMPLEMENTS foster2025.infiltration and any mass-budget gate (ρ(TDS, T) for
  mass↔volume conversions at concentrated early-shot conditions).
- NO conflict with any registered component; nothing registered carries thermal
  properties. Singh et al. 1997 (coffee *powders*, cited in the intro) would be
  the complementary solid-phase acquisition target if a puck thermal model is
  ever pursued.
- Registry-side finding not stated in the source: the Eq. (6) temperature
  coefficient as printed is inconsistent with the paper's own Figure 5 by ~100×
  (exponent typo; corrected form given above).

## Implementation estimate
Effort S: seven one-line closures plus a TDS→X_w(fraction) adapter and external
water-property tables for Eqs. (2)/(5)/(7). No dependencies. Gate design:
(i) reproduce the Figure 2–5 endpoint values from the closures (using the
corrected Eq. 6 coefficient) within plotting accuracy; (ii) verify the
k/(ρC_p)-vs-Eq.(6/7) offset lands at ≈ −11 % as reported, confirming faithful
transcription; (iii) units gate on the shared adapter to prevent the
fraction-vs-percent hazard against telisromero2001.

VERDICT: calibration-provider — completes the liquor property set (ρ, C_p, k, α)
begun by telisromero2001 for G10 and the temperature-effects backlog, with a
documented Eq. (6) exponent typo, an ~11 % internal α inconsistency to route
around, and figure-only data — effort S.
