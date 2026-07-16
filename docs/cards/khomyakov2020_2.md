# Model card: Khomyakov 2020 coffee-extract density/viscosity/boiling data

**Paper/thesis:** Khomyakov, A.P., Mordanov, S.V., Khomyakova, T.V. "The
experimental data on the density, viscosity, and boiling temperature of the
coffee extract." *IOP Conf. Ser.: Earth Environ. Sci.* 548 (2020) 022040.
DOI: 10.1088/1755-1315/548/2/022040. Open access (CC-BY 3.0).
**Stage(s):** flow (liquor property closures/data) · **Kind:** calibration
**Status:** card-only (fuller re-card of an already-intaken paper — the Table-1
data lives on disk via [[khomyakov2020]]; this card adds Eq 1/2/3, the Table-2
μ-coefficients, and the inter-source concordance finding gated below)

## Scope and mechanism
Pure experimental property study — no mechanism, no model beyond least-squares
regressions. Measures density ρ(f, t), kinematic viscosity ν(f, t), and
atmospheric-pressure boiling temperature T_b(f) of industrial coffee extract at
dry-substances mass fraction f = 0.15–0.70 and t = 20–80 °C (density stated
20–70 °C), for evaporator/spray-dryer design in soluble-coffee production.
Instruments: Swietoslawsky ebulliometer (T_b, ≤0.5 % error); aerometers
(f < 0.50) and pycnometry (f > 0.50) for ρ (≤0.15 % / ≤0.5 %); capillary
viscometers (0.99 and 1.47 mm) for f < 0.50 and for f > 0.50 at t ≥ 50 °C, cup
viscometer (4 mm nozzle) for f > 0.50 at t < 50 °C (≤0.5 % / ≤2.5 %). This is
the same material class as the telisromero2000/2001 cards (soluble-production
extract, not espresso liquor) from an independent group, batch, and instrument
set.

## Governing equations
All fits: t in °C, f = dry-substances mass fraction (0–1). Note units differ
from both Telis-Romero cards (P1 normalization-hazard class): μ in **mPa·s**,
ν in **mm²/s**, f a fraction here vs X_w = water percentage in telisromero2001.

- (1) T_b = 4.9395·f² + 1.6099·f + 99.633  [°C], atmospheric pressure;
  approximation error 0.26 %. Registry-irrelevant (puck never boils at shot
  pressures); transcribed for completeness only.
- (2) ρ = 932 + 0.8·t + 509·f  [kg/m³]; approximation error 1.97 %.
  **Sign anomaly flagged below — do not consume the T-dependence.**
- (3) μ = a·(t/100)^b  [mPa·s], one (a, b) pair per f (Table 2); average
  approximation error 8.2 %, maximum 26.1 % — the authors themselves call the
  regression values "rough", for estimation only. The primary viscosity record
  is Table 1 (measured ν), not Eq. (3).

Dynamic viscosity is not measured directly: μ = ρ·ν from Eqs./data above,
authors' stated propagated error 3.0 %.

**Eq. (2) sign anomaly, documented at intake (same failure class as the
grudeva2025 Issue 2a unit typo and the telisromero2000 Eq. 6 exponent typo):**
the prose states density "decreases with the temperature rising", consistent
with thermal expansion, with telisromero2000 Eq. (1) (−0.16 kg/m³·°C), and
with the Burmester data the authors cite approvingly. But the printed
coefficient is **+0.8 kg/m³·°C**, and the printed equation is self-consistent
with the printed extrema only under *increasing* T-dependence: min 1030 kg/m³
≈ Eq. (2) at (f = 0.15, t = 20) → 1024; max 1350 ≈ (f = 0.70, t = 70) → 1344.
Flipping the sign misses both extrema by 6–8 %, far outside the stated 1.97 %.
So the equation, the quoted min/max, and (as best readable) Figure 2 all imply
ρ rising with T; only the prose sentence says otherwise. Unresolvable from the
paper; possible uncorrected instrument-temperature artifact. Consequence: use
Eq. (2) only as ρ(f) at fixed t if at all; prefer telisromero2000 Eq. (1) for
any T-dependent density.

## Parameters
Eq. (3) coefficients (paper Table 2; μ in mPa·s, t in °C). **Note: no row for
f = 0.25 is printed, although Table 1 has an f = 0.25 data column.**

| f | a | b | avg. approx. error | source |
| --- | --- | --- | --- | --- |
| 0.15 | 3.85 | −0.741 | 4.0 % | fitted |
| 0.20 | 6.50 | −0.851 | 4.8 % | fitted |
| 0.25 | not provided | not provided | — | (row absent from Table 2) |
| 0.30 | 12.10 | −0.984 | 4.6 % | fitted |
| 0.35 | 32.80 | −1.090 | 4.1 % | fitted |
| 0.40 | 84.79 | −1.084 | 8.6 % | fitted |
| 0.45 | 215.27 | −1.335 | 5.6 % | fitted |
| 0.50 | 363.86 | −1.590 | 13.8 % | fitted |
| 0.60 | 4931.00 | −1.637 | 9.2 % | fitted |
| 0.70 | 300557.00 | −2.004 | 16.2 % | fitted |

| symbol | value | units | source |
| --- | --- | --- | --- |
| T_b coefficients (Eq. 1) | 4.9395, 1.6099, 99.633 | °C | fitted (approx. error 0.26 %) |
| ρ coefficients (Eq. 2) | 932, +0.8 (sign flagged), 509 | kg/m³; kg/(m³·°C); kg/m³ | fitted (approx. error 1.97 %) |
| ρ range | 1030–1350 | kg/m³ | measured |
| μ range | 0.769–27 481 | mPa·s | measured (via ρ·ν) |
| max thermal depression | 3.2 (at f = 0.70) | °C | measured |
| foaming onset | ~80 °C at f = 0.70; ~90–95 °C at f = 0.60 | °C | measured (qualitative) |

## Calibration and validation offered by the source
- Regression quality is approximation error on the authors' own data only —
  post-fit reconstruction, the weakest rung. Viscosity regressions are poor by
  the authors' own account (avg 8.2 %, max 26.1 %).
- External concordance is asserted, not shown: "correspondent well" with
  Telis-Romero [6][7][9] and Burmester [8], with no quantitative comparison.
- **Registry-side concordance check (not in the source):** in the overlap box
  with telisromero2001 (solids 15–20 %, i.e. X_w 80–85 %, Newtonian domain),
  Khomyakov dynamic viscosities run systematically **~40–55 % above**
  telisromero2001 Eq. (10): e.g. f = 0.20, 20 °C → μ ≈ 3.31 mPa·s here vs
  2.15 mPa·s from TR Eq. (10); f = 0.15, 60 °C → 1.02 vs 0.73 mPa·s. Different
  material (Russian production extract vs Brazilian 51 °Brix batch) and
  instruments; the discrepancy is carried as an unresolved inter-source spread
  on G10, not adjudicated here.
- Measurement-method caveat: telisromero2001 showed the extract is
  non-Newtonian above ~36 % solids (n down to 0.87). Capillary/cup viscometry
  reports a single apparent viscosity at an uncontrolled, geometry-dependent
  shear rate, so the f ≥ 0.40 columns are apparent values at unknown γ̇ — fine
  as data, not a constitutive law.

## Assumptions and validity range
- Material: industrial soluble-production coffee extract — no emulsified oils,
  suspended fines, or dissolved CO₂; composition uncharacterized beyond solids
  fraction. Same composition-bias caveat as both Telis-Romero cards.
- Validity box: f 0.15–0.70, t 20–80 °C (ρ stated to 70 °C), atmospheric
  pressure. The **entire** concentration range sits above espresso beverage
  TDS (8–12 %); even the most dilute point is above it. Relevant only to
  concentrated in-pore/first-drip liquor and as cross-check data.
- Espresso brew temperatures 88–96 °C are extrapolation above the box.
- Eq. (3) T-dependence should not be extrapolated below 20 °C (power-law in
  t/100 diverges) or above 80 °C.
- Boiling/foaming results are at atmospheric pressure only — irrelevant under
  shot pressure; retained only in case a future steaming/flash context wants
  them.
- Silent on: shear-rate dependence, pressure dependence, thermal properties
  (C_p, k, α — see telisromero2000), sub-15 % solids (the whole
  beverage-strength regime).

## Interface mapping
Inputs consumed: local liquor solids concentration from the extraction stage
(adapter: f = TDS/100, fraction form — note the three-way units hazard: f
fraction here, X_w percentage in telisromero2001, X_w fraction in
telisromero2000) and temperature t (not a contract field; observables
"temperature effects" backlog).
Outputs produced: ρ and μ of concentrated liquor. No BedState/MachineState
field carries either; all registered flow components assume constant water
properties.
Couplings: OFFLINE CALIBRATION data only; no runtime coupling. Realistic
consumers: (i) a G10 gate that tests the telisromero2001 closures against an
independent dataset in the 15–51 % overlap (this is the card's main value);
(ii) upper-bound checks on concentrated first-drip in-pore viscosity (μ up to
~27 Pa·s at f = 0.70 — far beyond anything a shot reaches in bulk, but bounds
worst-case film concentrations); (iii) ρ(f) cross-check on telisromero2000
Eq. (1) at fixed t (they agree within ~2 % at f = 0.50, 30 °C).

## Extractable data
- **Table 1 → data/khomyakov2020_table1_kinematic_viscosity.csv:** 60 measured
  kinematic-viscosity values (10 mass fractions × 6 temperatures, mm²/s).
  HIGHEST value in the paper — the only independent tabulated liquor-viscosity
  dataset in the registry overlapping the telisromero2001 box and extending it
  to f = 0.70 and 80 °C. Transcription hazards: mixed decimal precision
  (3 d.p. below f = 0.50, 1 d.p. above); f = 0.70/20 °C entry is 20 417
  (2.04×10⁴ mm²/s).
- Table 2 → transcribed in full above; only needed if Eq. (3) is implemented.
- Figure 1 (T_b) and Figure 2 (ρ): Eq. (1)/(2) plus stated extrema carry the
  content; digitize Figure 2 only if the sign anomaly ever needs adjudication.
- Raw data/code: not published, not offered.

## Overlaps and conflicts
- COMPLEMENTS telisromero2001 (calibration-provider, G10): independent
  laboratory/batch/instrument viscosity dataset overlapping TR's box —
  upgrades what a G10 gate can test from consistency-check to inter-source
  comparison. CONFLICT carried: ~40–55 % systematic viscosity offset in the
  overlap (registry-side finding; unresolved, likely material difference).
- COMPLEMENTS telisromero2000 (ρ closure): fixed-t density agreement ~2 %;
  CONFLICT on the sign of ∂ρ/∂T (+0.8 here as printed vs −0.16 there; TR2000
  and physics favored — documented above, not silently merged).
- Does NOT satisfy G10 by itself: no shear-rate-resolved rheology, no
  beverage-strength coverage, weaker regressions than TR2001.
- No overlap with any runtime component; nothing here touches
  cameron2020.extraction_bdf, brewer2026.*, wadsworth2026.*, or
  foster2025.infiltration beyond the (already negligible-at-shot-TDS)
  constant-viscosity question quantified in telisromero2001.md.
- Boiling-point/foaming content maps to no registry stage or backlog item.

## Implementation estimate
Effort S: transcribe Table 1 (60 values) and Table 2 (27 values); no closures
worth implementing beyond what telisromero2001/2000 already provide. Gate
design if used: (i) reproduce Table 1 → dynamic μ via Eq. (2) at fixed t and
confirm the authors' 0.769/27 481 mPa·s extrema; (ii) inter-source gate —
evaluate telisromero2001 Eqs. (10)/(13) across the overlap grid and record the
offset distribution (expected ~+40–55 %), fixing the current best estimate of
G10 inter-source spread; (iii) units gate covering the three-way f/X_w
fraction-vs-percent hazard.

VERDICT: data-only — Table 1 is the registry's only independent tabulated
liquor-viscosity dataset for cross-checking the telisromero2001 G10 closures
(revealing a ~40–55 % inter-source offset), but the regressions are rough, the
density equation carries an unresolved T-sign anomaly, and the whole box sits
above espresso TDS — effort S.
