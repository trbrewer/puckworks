# Model card: Telis-Romero 2001 coffee-extract rheology

**Paper/thesis:** Telis-Romero, J., Cabral, R.A.F., Gabas, A.L., Telis, V.R.N.
"Rheological properties and fluid dynamics of coffee extract." *Journal of Food
Process Engineering* 24 (2001) 217–230. DOI: 10.1111/j.1745-4530.2001.tb00542.x.
**Stage(s):** flow (fluid-property closure for the liquor phase; secondary tag
observables via TDS→viscosity) · **Kind:** calibration
**Status:** implemented (2026-07-15) — Eqs (10)/(12)/(13) closures + 2 anchors in
`puckworks/data/g10_liquor_rheology/telisromero2001_{closures,anchors}.csv`,
loader `data.telisromero_viscosity_pas(T_K, Xw_pct)`, gate
`gate_g10_telisromero_closure` wired to `sourcing2026.g10_liquor_rheology`.
**Table 1/Table 2 per-cell digitization DONE (2026-07-15, Tim drop)** →
`telisromero2001_table{1_eta,2_Kn}.csv` (24 η + 27 K/n measured cells) + loaders
`data.telisromero_{table1_eta,table2_Kn,eta_measured}`; gate
`gate_g10_telisromero_full_table` shows the closures reproduce all 51 cells at the
authors' own fit quality. **Sensitivity study (§Impl-est ii) DONE** →
`analysis.g10_viscosity_sensitivity` + gate `gate_g10_viscosity_bulk_negligible`:
G10 closes as negligible-at-shot-TDS (constant-water-μ Darcy error ≤~3% shot-integrated;
liquor never reaches the power-law regime), NO runtime μ(c,T) hook warranted.

## Scope and mechanism
Empirical constitutive correlations for the viscosity of aqueous coffee extract as a
simultaneous function of temperature T (274–365 K) and water content X_w (49–90 % w/w,
i.e. 10–51 % solids), fitted to concentric-cylinder rheometry on one industrial
soluble-coffee extract batch (51 °Brix, COCAM, Brazil) diluted with distilled water.
Two regimes: a Newtonian domain (X_w 76–90 %, T 295–365 K) with η(T, X_w), and a
mildly shear-thinning Ostwald–De Waele (power-law) domain (X_w 49–64 %, T 274–353 K)
with K(T, X_w) and n(T, X_w), n = 0.87–0.97. A second part of the paper measures tube-flow
pressure drop and shows standard friction-factor correlations (Hagen–Poiseuille,
Colebrook, Dodge–Metzner) reproduce it using the fitted rheology — this is a consistency
check on the rheometry, not a separable model, so no second card.

## Governing equations
Power-law constitutive form (Eq. 1): σ = K γ̇ⁿ, with σ shear stress (Pa), γ̇ shear
rate (s⁻¹), K consistency index (Pa·sⁿ), n behavior index (–). Newtonian limit n = 1,
K = η.

Implementable closures (T in K, X_w in % w/w water, wet basis; R = 8.314 J mol⁻¹ K⁻¹):
- (10) η = 1.99×10⁶ · exp(E_a,η / RT) · X_w^(−6.07)   [Pa·s], Newtonian domain
- (12) n = 0.199 · exp(A / T) · X_w^(0.370)   [–], power-law domain
- (13) K = 1.46×10⁶ · exp(E_a,K / RT) · X_w^(−10.05)   [Pa·sⁿ], power-law domain

Unit sanity check performed at intake: Eq. (10) with X_w = 90, T = 295 K gives
η = 1.01×10⁻³ Pa·s vs Table 1 value 1.00×10⁻³ — confirms X_w enters as a percentage,
not a fraction. Eq. (13) at X_w = 49, T = 293 K gives 214×10⁻³ vs Table 2's 200×10⁻³
Pa·sⁿ (within the authors' stated ~7 % average error for K).

Not transcribed as implementables: Eq. (2) generic Arrhenius template (subsumed by
10/13); Eqs. (3)–(8) standard Fanning friction-factor / generalized-Reynolds tube-flow
relations (textbook, not coffee-specific); Eq. (9) Krieger–Elrod shear-rate series
(rheometer data reduction only); Eqs. (14)–(15) tube wall shear-rate estimates.

## Parameters
| symbol | value | units | source (measured/fitted/nominal) |
| --- | --- | --- | --- |
| pre-factor, Eq. 10 | 1.99×10⁶ | Pa·s (with X_w in %) | fitted (r² = 0.997) |
| E_a,η (viscosity) | 14 514 | J/mol | fitted |
| X_w exponent, Eq. 10 | −6.07 | – | fitted |
| pre-factor, Eq. 12 | 0.199 | – | fitted (r² > 0.998) |
| A (Eq. 12) | 13.46 | K | fitted |
| X_w exponent, Eq. 12 | 0.370 | – | fitted |
| pre-factor, Eq. 13 | 1.46×10⁶ | Pa·sⁿ | fitted (r² > 0.998) |
| E_a,K (consistency) | 56 924 | J/mol | fitted |
| X_w exponent, Eq. 13 | −10.05 | – | fitted |
| η range (Newtonian domain) | 0.32×10⁻³ – 2.81×10⁻³ | Pa·s | measured (Table 1) |
| K range (power-law domain) | 0.25×10⁻³ – 1062×10⁻³ | Pa·sⁿ | measured (Table 2) |
| n range | 0.87 – 0.97 | – | measured (Table 2) |
| ρ(T, X_w) | not provided here | kg/m³ | cites Telis-Romero et al. 2000 |

## Calibration and validation offered by the source
- Fit quality on the authors' own rheograms: Eq. (10) r² = 0.997, mean relative error
  2.34 %, max 10.17 %. Eq. (12) mean error 0.14 %, max 0.31 %. Eq. (13) mean error
  6.77 %, max 18.50 %.
- Independent-instrument cross-check: tube-flow pressure-drop experiments, friction
  factors from measured ΔP compared with correlations evaluated using Eqs. (10)/(12)/(13).
  Laminar Newtonian: mean error 3.62 % (max 6.29 %) vs f = 16/Re. Turbulent Newtonian
  vs Colebrook: mean 17.40 % (max 32.98 %). Laminar power-law vs f = 16/Re_g: mean
  9.56 % (max 12.96 %). Turbulent power-law vs Dodge–Metzner: mean 2.85 % (max 5.78 %).
  This is a genuine second experiment on the same material, but it validates the
  rheology only through widely accepted correlations — it is a consistency check,
  not independent validation of the (T, X_w) functional form.
- All data from ONE extract batch from one supplier; no replicate batches, no
  composition characterization beyond moisture content.

## Assumptions and validity range
- Material: industrially produced soluble-coffee extract (high-yield hot extraction
  for spray-drying feedstock), reconstituted by dilution. NOT fresh espresso liquor:
  solids composition differs (industrial extraction hydrolyzes more polysaccharides;
  espresso liquor additionally carries emulsified oils, suspended fines, and dissolved
  CO₂, none present here). Treat as a prior with unquantified composition bias.
- Validity box: Newtonian domain X_w 76–90 % (solids 10–24 %), T 295–365 K; power-law
  domain X_w 49–64 % (solids 36–51 %), T 274–353 K. NO data in the X_w 64–76 % gap
  between domains, and nothing more dilute than 10 % solids — the paper's most dilute
  point sits at the TOP of the espresso TDS range (~8–12 %); normal-strength espresso
  and anything weaker is (mild) extrapolation toward water.
- Rheometry shear rates 0.4–480 s⁻¹; tube experiments show the correlations still
  reproduce friction at 700–1482 s⁻¹. In-pore espresso shear rates can exceed this;
  with n ≈ 0.87–0.97 the extrapolation risk is mild but real.
- Silent on: time dependence/thixotropy, yield stress (σ₀ listed in nomenclature but
  never used), pressure dependence of viscosity (espresso liquor sees up to ~9 bar),
  and any suspended-solids or foam/crema rheology.
- Practical simplification licensed by the authors: since n ≈ 0.87–0.97, they state
  the extract may be treated as Newtonian across the whole studied range, with K
  playing the role of η. For espresso-strength liquor (n → 0.97 side) this is safe.

## Interface mapping
Inputs consumed: local liquor solids concentration (from extraction stage; adapter
TDS % w/w → X_w = 100 − TDS, valid if solids are the only non-water component) and
temperature T (currently NOT a contract field — observables backlog "temperature
effects" applies).
Outputs produced: liquor dynamic viscosity μ (and K, n if power-law retained) for the
flow stage. No current BedState/MachineState field carries μ; registered flow models
(brewer2026.lb_*, streamtube; Darcy in cameron2020/grudeva2025 chains) assume constant
water viscosity, so consuming this requires a small flow-side extension (μ(c, T) hook)
or an offline sensitivity study.
Couplings: OFFLINE CALIBRATION provider only; no runtime coupling forced. Quantitative
implication worth recording: at typical shot TDS (solids ≈ 10 %, X_w = 90) and 365 K,
Eq. (10) gives η ≈ 0.32 mPa·s vs ≈ 0.31 mPa·s for pure water — bulk-liquor viscosity
correction to Darcy flow is negligible. But early-shot in-pore liquor near the
extraction front is far more concentrated; at X_w = 76, 295–365 K the extract is
~2–3× water, and at first-drip concentrations the power-law domain values (K up to
~1 Pa·sⁿ at 274 K) imply order-of-magnitude effects. The correlations bound how big
a concentrated-liquor viscosity transient could be.

## Extractable data
- Table 1 → data/telisromero2001_table1.csv: η at 4 water fractions (76–90 %) ×
  6 temperatures (295–365 K), Newtonian domain. 24 values. HIGH value — spans the
  espresso-TDS end.
- Table 2 → data/telisromero2001_table2.csv: K and n at 3 water fractions (49–64 %) ×
  9 temperatures (274–353 K). 54 values. Moderate value (in-pore/first-drip regime).
- Figs. 1–2 (Moody diagrams): LOW value — confirm textbook correlations; skip
  digitising.
- Raw rheograms/code: not published, not offered. Companion density/thermal-property
  correlations are in Telis-Romero et al. 2000 (Int. J. Food Properties 3(3)) —
  flag as an acquisition target if μ(c,T) is implemented, since Darcy needs ρ
  consistently too.

## Overlaps and conflicts
- Directly addresses roadmap gap G10 (coffee-liquor rheology): first registry source
  putting numbers on liquor viscosity vs concentration and temperature. Partial
  satisfaction only, given the composition caveat (soluble-coffee extract ≠ espresso
  liquor) and the dilute-end extrapolation.
- COMPLEMENTS cameron2020.extraction_bdf and grudeva2025 (both produce c(t) that could
  drive μ(c, T)); complements brewer2026.streamtube / lb_reference / lb_taichi and the
  DE1 fixture A kappa fit by quantifying when the constant-μ assumption fails (answer:
  essentially never in bulk at shot TDS; possibly early in-pore).
- COMPLEMENTS observables backlog "temperature effects" (explicit Arrhenius T
  dependence, E_a = 14.5 kJ/mol Newtonian domain).
- No registered component competes; no conflict. The friction-factor section is
  irrelevant to puck flow (tube flow, Re up to 10⁵ — puck flow is creeping/Forchheimer,
  handled by wadsworth2026_inertial).

## Implementation estimate
Effort S: Eqs. (10), (12), (13) are one-line closures plus a TDS→X_w adapter. No
dependencies. Gate design: (i) reproduce Table 1/Table 2 values from the closures
within the authors' stated errors (2.34 % / 0.14 % / 6.77 % mean); (ii) sensitivity
study — rerun a Darcy/streamtube shot with μ(c, T) from Eq. (10) vs constant water μ
and record the flow/EY delta, to decide whether G10 warrants a runtime hook or is
formally closed as negligible at shot TDS.

VERDICT: calibration-provider — one-line μ(T, X_w) closures with transcribable tables
that partially fill G10 and quantify (likely bound as small) the constant-viscosity
error in every registered flow model, with a composition caveat vs real espresso
liquor — effort S.
