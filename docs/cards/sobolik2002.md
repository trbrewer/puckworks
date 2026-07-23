# Model card: Sobolík 2002 concentrated coffee-solution viscosity and electrical conductivity

**Paper/thesis:** Sobolík, V., Žitný, R., Tovcigrecko, V., Delgado, M., Allaf, K.
"Viscosity and electrical conductivity of concentrated solutions of soluble
coffee." *Journal of Food Engineering* 51 (2002) 93–98.
DOI: 10.1016/S0260-8774(01)00042-5.
**Stage(s):** flow (liquor viscosity/density closures) · observables
(conductivity and refractive-index measurement-kernel data) · **Kind:** calibration
**Status:** card-only

## Scope and mechanism

Property study on aqueous solutions of soluble (instant) coffee, in two parts.
(i) Viscosity of concentrated solutions (coffee mass fraction ω = 0.5–0.8,
T = 25–95 °C, Haake rotational viscometer): fresh solutions are slightly
pseudoplastic and thixotropic (flow index ≈ 0.9); after sustained shear and
passing 95 °C the behavior becomes Newtonian, and the reported limiting
viscosity μ is fitted by a five-parameter function of ω and T. A refit of
Weisser's (1972, Czech) data extends μ(ω, T) down to ω = 0–0.5. (ii) Specific
electrical conductivity κ of coffee in tap water (ω = 0–0.8, T = 25–72 °C,
four-electrode probe, 542 points): a seven-parameter "partially dissociated
species + water in parallel" empirical model, benchmarked against a modified
Casteel–Amis equation. The paper also reviews Weisser's refractive-index,
density, surface-tension, and thermal-conductivity correlations for ω = 0–0.5.
No mechanism beyond the parallel-resistor ansatz — property fits throughout.

## Governing equations

All fits: T in °C (viscosity fits convert internally via T + 273.15), ω =
**coffee (solids) mass fraction, 0–1**. Units hazard vs siblings (roadmap P1
class): ω solids-fraction here ≡ f in khomyakov2020_2, = 1 − X_w(fraction) in
telisromero2000, = 1 − X_w(%)/100 in telisromero2001. μ in Pa·s, κ in S/m.

Viscosity:
- (4) μ = exp[1.141 − 22.42 ω − 17.78 ω² − (973.1 − 17923 ω²)/(T + 273.15)]
  [Pa·s], own data, ω 0.5–0.8, T 25–95 °C, max error < 15 %.
- (5) μ = exp[−12.96 − 9.43 ω + 8.12 ω² + (1789 + 4382 ω)/(T + 273.15)]
  [Pa·s], authors' best fit to Weisser (1972) data, ω 0–0.5. (Transcription
  check at intake: ω = 0, 20 °C → 1.05 mPa·s ≈ water ✓; ω = 0.5, 60 °C →
  24.7 mPa·s ≈ Weisser's 24 ✓.)

Conductivity (model design Eqs. 6–8 lead to the implementable Eq. 9):
- (6) ω_diss = ω(1 − ω)^m — dissociated-species fraction ansatz, proportional
  to both coffee and water mass fractions.
- (7) κ = (κ_c0 + κ_c1 T) ω(1 − ω)^m + κ_w(1 − ω) — parallel-resistor
  combination (dissociated species, linear in T; non-dissociated species as
  insulator; tap water, T-dependence neglected). Constant m does not fit.
- (8) m = a + b·max(ω, ω_c) + c T — empirical exponent with a trend change at
  critical concentration ω_c.
- (9) κ(ω, T) = (κ_c0 + κ_c1 T) · ω · (1 − ω)^{a + b·max(ω, ω_c) + cT}
  + κ_w(1 − ω) — the recommended 7-parameter model.
- (10) Modified Casteel–Amis (De Diego et al. 1997, concentration replaced by
  ω): κ(ω, T) = (κ_max0 + κ_max1 T) · (ω/(ω_max0 + ω_max1 T))^x ·
  exp[y(ω − ω_max0 − ω_max1 T)² − x(ω/(ω_max0 + ω_max1 T) − 1)]. Six
  parameters; fits worse (σ = 0.0982 vs 0.0621 S/m); cannot describe κ(0) ≠ 0.
  Transcribed for completeness; not recommended for implementation.
- (11) κ_i(T) = p_0i + p_1i T + p_2i T² — per-concentration quadratic
  (11 concentrations, Table 1); reproduces primary data more closely than the
  global models (rel. std. dev. < 1.5 %).

Reviewed from Weisser 1972 (secondhand; original is Czech and likely
unobtainable):
- (1) n_D^20 = 1.333 + 0.1728 ω + 8.93×10⁻² ω² — refractive index at 20 °C,
  ω ≤ 0.5 (above that the dark color prevents scale reading).
- (2) 1/ρ(ω, T) = ω/ρ_C + (1 − ω)/ρ_W — ideal volume-additive mixing with
  ρ_W = 1000 − 0.036 T − 0.004 T² and ρ_C = 1654 − 1.79 T − 0.0063 T² [kg/m³,
  T °C]. By construction recovers pure water at ω = 0 (unlike telisromero2000
  Eq. 1) and gives ∂ρ/∂T < 0 throughout.
- (3) Thermal-conductivity correlation: **not reliably legible in our copy**
  (form approximately λ = 1.03·(0.565 + …T…)·(1 − 0.5ω); coefficients not
  transcribed — do not implement from this card; the registry's k(T, X_w)
  source remains telisromero2000 Eq. 4). Reacquire a clean scan if ever needed.
- Surface tension data points (ω = 0.1): 0.042 N/m at 20 °C, 0.037 N/m at
  40 °C. No correlation given.

## Parameters

Model (9) and (10), paper Table 2 (nonlinear least squares, N = 542,
T 25–72 °C, ω 0–0.8; confidence intervals as printed):

| symbol | value | units | source (measured/fitted/nominal) |
| --- | --- | --- | --- |
| Eq. 4 coefficients | 1.141, −22.42, −17.78, 973.1, −17923 | –, –, –, K, K | fitted (max error < 15 %) |
| Eq. 5 coefficients | −12.96, −9.43, +8.12, 1789, 4382 | –, –, –, K, K | fitted (to Weisser 1972 data) |
| κ_c0 | 5.833 ± 0.5 | S/m | fitted |
| κ_c1 | 0.2439 ± 0.01 | S/(m·°C) | fitted |
| a | 1.731 ± 0.11 | – | fitted |
| b | 2.648 ± 0.16 | – | fitted |
| c | −0.0111 ± 0.0012 | °C⁻¹ | fitted |
| κ_w | 0.0503 ± 0.0005 | S/m | fitted (≈ tap-water measurement 0.043 S/m at 50 °C) |
| ω_c | 0.454 ± 0.01 | – | fitted |
| κ_max0 (Eq. 10) | 0.3606 ± 0.140 | S/m | fitted |
| κ_max1 (Eq. 10) | 0.04198 ± 0.0028 | S/(m·°C) | fitted |
| ω_max0 (Eq. 10) | 0.2667 ± 0.020 | – | fitted |
| ω_max1 (Eq. 10) | 0.000678 ± 0.00034 | °C⁻¹ | fitted |
| x (Eq. 10) | 0.4055 ± 0.111 | – | fitted |
| y (Eq. 10) | −9.941 ± 1.06 | – | fitted |
| flow index, fresh solution | ≈ 0.9 | – | measured (ω = 0.7, 40 °C, before treatment) |
| max shear rate, S1 / S2 cylinder | 1574 / 455 | s⁻¹ | nominal (apparatus limits) |
| n_D^20, ρ_W, ρ_C coefficients (Eqs. 1–2) | as transcribed above | – | fitted (Weisser 1972, secondhand) |

Eq. (11) quadratic coefficients, paper Table 1 (κ_i in S/m, T in °C):

| ω | p_0 [S/m] | p_1 [S/(m·°C)] | p_2 [S/(m·°C²)] |
| --- | --- | --- | --- |
| 0 | 1.48E−5 † | 7.20E−7 † | 1.70E−10 † |
| 0.02 | 1.33E−1 | 5.25E−3 | 6.00E−6 |
| 0.05 | 3.07E−1 | 1.28E−2 | 1.40E−5 |
| 0.10 | 4.22E−1 | 1.90E−2 | 1.90E−5 |
| 0.20 | 5.88E−1 | 2.87E−2 | 4.70E−5 |
| 0.30 | 5.47E−1 | 3.13E−2 | 7.80E−5 |
| 0.40 | 4.81E−1 | 2.96E−2 | 1.21E−4 |
| 0.50 | 2.73E−1 | 1.92E−2 | 1.49E−4 |
| 0.60 | 9.02E−2 | 9.71E−3 | 1.47E−4 |
| 0.70 | 1.79E−2 | 1.20E−3 | 9.20E−5 |
| 0.80 | −4.10E−5 † | 9.39E−7 † | 1.18E−8 † |

**† Table 1 endpoint-row exponent anomaly, documented at intake (same failure
class as grudeva2025 Issue 2a, telisromero2000 Eq. 6, khomyakov2020_2 Eq. 2):**
the ω = 0 and ω = 0.80 rows as printed give κ ≈ 5×10⁻⁵ and ≈ 8×10⁻⁵ S/m at
50–70 °C, ~10³ below the same series in Fig. 5 (ω = 0: 0.03–0.07 S/m,
consistent with tap water; ω = 0.8: ~0.01 S/m at 38 °C rising to ~0.1 S/m at
72 °C). Shifting all three exponents by 10³ (1.48E−2, 7.20E−4, 1.70E−7 and
−4.10E−2, 9.39E−4, 1.18E−5) reproduces the Fig. 5 endpoints within reading
accuracy (ω = 0, 50 °C → 0.051 S/m; ω = 0.8, 72 °C → 0.088 S/m). The nine
interior rows check out against Figs. 5–6 as printed (e.g. ω = 0.3, 50 °C →
2.31 S/m ✓). Both variants carried; discriminating computation: digitize the
Fig. 5 ω = 0 and ω = 0.8 series and regress. Until then, prefer Eq. (9) for
the endpoints.

## Calibration and validation offered by the source

- All regressions are post-fit reconstruction on the authors' own data — the
  weakest rung. No held-out data, no replicate campaigns.
- Viscosity Eq. (4): max evaluation error < 15 % (authors' estimate), against
  a stated measurement error of ~15 % (concentrated solutions swell,
  caramelise, evaporate). Cross-check against Weisser (1972), ω = 0.5, 60 °C:
  0.019 Pa·s here vs 0.024 Pa·s Weisser — "quite good agreement", read by the
  authors as evidence viscosity is nearly independent of coffee type
  (freeze-dried Vox Mocca/Robusta vs spray-dried Nescafé Gold/Maxwell) and
  drying treatment. That is a genuine two-source concordance, at the ~25 %
  level.
- Conductivity: 542 (T, ω, κ) points. Per-concentration quadratics (11):
  rel. std. dev. < 1.5 %. Global model (9): σ = 0.0621 S/m, R = 0.9975.
  Modified Casteel–Amis (10): σ = 0.0982 S/m, R = 0.9936 — significantly
  worse; adding a κ_w(1 − ω) term to (10) did not help (σ = 0.099). Two
  plausibility spot-checks by the authors: fitted κ_w = 0.0503 S/m vs measured
  tap water ~0.043 S/m at 50 °C; fitted ω_c = 0.454 visually matches the
  trend change in Fig. 6. Parameter signs all physical; c < 0 reproduces the
  observed shift of the κ(ω) maximum (ω ≈ 0.35, κ_max ≈ 3.2 S/m at 70 °C,
  ~40× tap water) toward higher ω with rising T.
- Authors judge mild extrapolation of (9) to ~90 °C plausible on parameter-
  physicality grounds; that is an opinion, not a test.

## Assumptions and validity range

- Material: reconstituted instant coffee in water — same composition caveat as
  all three sibling cards (no emulsified oils, suspended fines, or dissolved
  CO₂; industrial extraction hydrolyzes more polysaccharides). Conductivity
  additionally in **tap water** of one site — κ_w and arguably the dissociation
  behavior are water-chemistry-specific; espresso brew water varies widely.
- Eq. (4) box: ω 0.5–0.8, T 25–95 °C — entirely above espresso beverage TDS;
  relevant only to in-pore/first-drip/film concentration bounds. **State
  caveat:** Eq. (4) is the limiting viscosity after sustained shear and a
  95 °C excursion; fresh solutions are pseudoplastic/thixotropic (flow index
  ≈ 0.9) and read higher. An irreversible viscosity increase was observed on
  prolonged holding near/above 95 °C (details partially illegible in our
  scan); do not use Eq. (4) above 95 °C.
- Eq. (5) box: ω 0–0.5, T ≈ 0–80 °C (Weisser's grid per Fig. 3). Covers
  espresso TDS; shot temperatures 88–96 °C are mild extrapolation.
- Conductivity box: ω 0–0.8, T 25–72 °C. Shot temperatures are extrapolation
  (authors: plausibly to ~90 °C). Below 25 °C untested.
- Shear-rate coverage: ≤ 1574 s⁻¹ (ω = 0.5), ≤ 455 s⁻¹ (ω > 0.5). In-pore
  espresso shear rates can exceed this; Newtonian claim untested beyond.
- Silent on: pressure dependence (shot sees ~9 bar), sub-25 °C conductivity,
  crema/foam and suspended-solids rheology, time-resolved thixotropy
  parameters (behavior described qualitatively only), and any thermal
  properties beyond the illegible reviewed Eq. (3).

## Interface mapping

Inputs consumed: local liquor solids concentration from the extraction stage
(adapter ω = TDS/100, solids-fraction form — note the now four-way ω/f/X_w
fraction-vs-percent, solids-vs-water hazard across sobolik2002 /
khomyakov2020_2 / telisromero2000 / telisromero2001; the shared adapter must
carry explicit units and basis fields) and temperature T (not a contract
field; observables "temperature effects" backlog).
Outputs produced: liquor μ(ω, T), ρ(ω, T), κ(ω, T), n_D^20(ω). No
BedState/MachineState/ShotResultState field carries any of these; all
registered flow components assume constant water properties.
Couplings: OFFLINE CALIBRATION provider only; no runtime coupling. Consumers:
(i) the G10 inter-source gate — Eqs. (4)/(5) are the third and fourth
independent μ(ω, T) sources, extending coverage to ω = 0.8 and 95 °C (past
khomyakov's 0.70/80 °C and telisromero2001's 51 % solids/365 K ceiling);
(ii) ρ via Eq. (2) as the only registry density closure that is exact at the
water limit — the right form for mass-budget gates spanning dilute beverage
to concentrated first-drip; (iii) κ and n_D^20 park under the observables
"scale/measurement kernels" backlog (refractometer- and conductivity-based
TDS sensing) with no active consumer today; (iv) the fresh-state
pseudoplastic/thixotropic observation is a qualitative prior for any G10
runtime hook: in-pore liquor during a 25–30 s shot never receives the
shear/thermal history that produces Eq. (4)'s Newtonian limit.

## Extractable data

- **Table 1 → data/sobolik2002_table1_kappa_quadratic.csv** (33 coefficients,
  11 concentrations; carry the † exponent flag on rows 1 and 11). Highest
  tabulated value — reproduces the 542-point primary dataset within 1.5 %.
- Table 2 → transcribed in full above (both conductivity models with
  confidence intervals).
- Fig. 5 (primary κ(T) data, every 2nd of ~542 points plotted, log scale):
  digitize ONLY the ω = 0 and ω = 0.8 series — that is the named
  discriminating computation for the Table 1 endpoint anomaly. Interior
  series are carried by Table 1.
- Fig. 2 (μ(T), ω 0.5–0.8, own data) and Fig. 3 (μ(T), ω 0–0.5, Weisser's
  data): moderate value. Fig. 3 is the only accessible quantitative record of
  Weisser 1972 (Czech, likely unobtainable) — digitize if a G10 gate ever
  needs residuals against Eq. (5) rather than the closure itself.
- Fig. 1 (fresh vs treated flow curves, ω = 0.7, 40 °C): the only
  quantitative record of the thixotropy claim; low priority.
- Raw data/code: not published, not offered (in-house program XREGA).

## Overlaps and conflicts

- COMPLEMENTS telisromero2001, telisromero2000, khomyakov2020_2 on gap G10:
  third independent laboratory/material/instrument set, extending the joint
  (ω, T) envelope to ω = 0.8 and 95 °C, plus the Weisser refit (a fourth
  source) covering ω 0–0.5.
- **Registry-side concordance (computed at intake, not in the source), and it
  moves the G10 spread question:** (a) at the khomyakov extremum f = 0.70,
  20 °C, Eq. (4) gives 29.2 Pa·s vs khomyakov's measured ≈ 27.5 Pa·s — +6 %;
  (b) at f = 0.15, 60 °C, Eq. (5) gives 1.06 mPa·s vs khomyakov 1.02 (+4 %)
  vs telisromero2001 Eq. (10) 0.73 (+45 %); (c) at f = 0.20, 20 °C, Eq. (5)
  gives 4.38 mPa·s vs khomyakov ≈ 3.31 vs telisromero2001 2.15. The
  khomyakov card carried a ~40–55 % TR-vs-Khomyakov offset as unadjudicated
  two-source spread; Weisser/Sobolík now side with khomyakov at the ~±10–30 %
  level, making telisromero2001 the probable low outlier (3-vs-1). Not merged
  — carried as an updated spread estimate for the G10 inter-source gate.
- Khomyakov Eq. (2) density sign anomaly: Weisser Eq. (2) here gives
  ∂ρ/∂T < 0 (e.g. ω = 0.5: 1226 → 1183 kg/m³ over 30 → 70 °C), agreeing in
  sign with telisromero2000 and physics against khomyakov's printed +0.8 —
  additional adjudication evidence (now 3-vs-1), though magnitudes still
  spread (≈ −1.1 here vs −0.16 kg/(m³·°C) in TR2000 at mid-range).
- Fixed-point density concordance: ω = 0.5, 30 °C → 1226 (here) vs 1192
  (TR2000 Eq. 1) vs 1211 kg/m³ (khomyakov at fixed t): ~3 % band.
- NOT a conflict with telisromero2001's power-law finding (n = 0.87–0.97 at
  36–51 % solids): Sobolík's FRESH solutions show flow index ≈ 0.9 —
  consistent — and the Newtonian claim applies only after shear + 95 °C
  history normalization. Reconciliation carried explicitly: the two sources
  describe different material states, and fresh-state (TR-like) rheology is
  the espresso-relevant one.
- n_D^20(ω) complements the mckeonaloe2022/2023 observables cards
  (refractometer TDS measurement); κ(ω, T) maps to the observables
  "scale/measurement kernels" backlog. Neither is consumed by anything
  registered.
- No overlap with any runtime component; nothing here touches
  cameron2020.extraction_bdf, brewer2026.*, wadsworth2026.*, or
  foster2025.infiltration beyond the constant-viscosity question already
  quantified in telisromero2001.md (registry-side: at ω = 0.10, 93 °C,
  Eq. (5) gives 0.43 mPa·s vs TR2001's 0.32 vs water's 0.31 — a ≤ 40 %
  relative disagreement that remains negligible for bulk Darcy flow).

## Implementation estimate

Effort S: Eqs. (4), (5), (9), (2), (1) are one-line closures plus the shared
TDS→ω adapter (with units/basis fields covering the four-way hazard); skip
Eq. (10). No dependencies. Gate design: (i) reproduce the authors' own
spot values (ω = 0.5, 60 °C → 0.019 Pa·s from Eq. 4; ω = 0, 20 °C → water
from Eq. 5; κ_max ≈ 3.2 S/m at ω ≈ 0.35, 70 °C from Eq. 9); (ii) the Table 1
endpoint-row discriminating computation (digitize Fig. 5 ω = 0 and ω = 0.8,
adjudicate the ×10³ exponent correction); (iii) extend the existing G10
inter-source gate to a four-source spread table (TR2001, khomyakov Table 1,
Eq. 4, Eq. 5) over the mutual overlap grid, recording the updated verdict
that TR2001 is the low outlier; (iv) units gate on the adapter.

VERDICT: calibration-provider — adds the third/fourth independent μ(ω, T)
sources that extend G10 coverage to ω = 0.8 / 95 °C and tip the unresolved
TR-vs-Khomyakov viscosity spread 3-vs-1 against telisromero2001, plus the only
water-limit-exact density closure and parked conductivity/refractive-index
measurement kernels, with one documented Table 1 exponent anomaly — effort S.
