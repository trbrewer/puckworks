# Data card: g10_liquor_rheology (coffee-extract mu, rho vs TDS, T)

**Papers:**
- Telis-Romero, Cabral, Gabas, Telis (2001), "Rheological properties and fluid
  dynamics of coffee extract," J. Food Process Eng. 24, 217-230.
  DOI 10.1111/j.1745-4530.2001.tb00541.x  [PRIMARY: viscosity vs T, water content]
- Telis-Romero, Gabas, Polizelli, Telis (2000), "Temperature and water content
  influence on thermophysical properties of coffee extract," Int. J. Food Prop.
  3(3), 375-384. DOI 10.1080/10942910009524642  [density, thermophysical]
- (cross-check) Tandfonline 2013, DOI 10.1080/10942912.2013.833221, "Rheological
  Behaviour, Freezing Curve, and Density of Coffee Solutions..." [density, low-T]
**Stage(s):** flow (all flow-coupled models) · **Kind:** calibration (fluid props)
**Status:** proposed — REFERENCE-STRENGTH for espresso (see caveat). Addresses G10.

## Scope and mechanism
Every flow model on file (foster, moroney, waszkiewicz constants, mo) uses
pure-water mu, rho. G10 is the shared early-shot bias this causes. This card
supplies coffee-extract **viscosity and density as functions of temperature and
soluble-solids content**, measured (in the source) over water content 49-90% and
274-365 K.

## The espresso-regime caveat (load-bearing — read first)
The sources measured **instant-coffee-processing** concentrations: their DILUTE
end is 90% water (~10% solids), and they turn non-Newtonian only above ~36%
solids. Espresso is the OPPOSITE extreme: TDS ~4-12% solids (88-96% water).

Consequences, stated honestly:
1. **Good news:** espresso liquor is firmly in the Newtonian band. No power-law,
   no thixotropy correction is needed. The single-viscosity assumption in the
   flow models is *qualitatively right*; only the magnitude is wrong.
2. **Limitation:** NO source on file measures rheology AT espresso TDS. The
   espresso viscosity is an **extrapolation** of the Telis-Romero fit toward the
   pure-water limit. So mu_espresso is a `reference/qualitative` estimate
   (~1.3-2x pure water at brew temp), NOT an `independent` measurement.
3. Therefore this card **must be tagged reference-strength**; do not upgrade to
   independent without a coffee measurement at espresso TDS (an open sub-search,
   analogous to the G1 target). It still beats "pure water everywhere."

## Governing forms provided
- Viscosity: Arrhenius-type mu(T) = A(Xw) * exp(Ea(Xw)/RT), with A, Ea functions
  of water content (Telis-Romero 5-parameter simultaneous fit).
- Density: rho(T, Xs) rising with solids, falling with T; 1000-1200 kg/m^3 over
  their range (Telis-Romero 2000), cross-checked 1036-1277 near freezing (2013).
  Density depends more strongly on Xs than on T.
- Newtonian threshold: power-law onset only above ~36% solids (>64% water).

## Parameters (espresso-relevant subset)
| symbol | value | units | source |
| mu_water @90C | 3.15e-4 | Pa*s | reference (current repo baseline) |
| mu_espresso @90C | ~4-6e-4 | Pa*s | REFERENCE extrapolation (Telis-Romero) |
| rho @ low-TDS, brew T | ~960-1000 | kg/m^3 | extrapolation |
| non-Newtonian onset | >36% solids | - | Telis-Romero 2001 |

## Calibration and validation offered by the source
Telis-Romero validated their mu(T,Xw) fit against tube-flow pressure-loss /
friction-factor measurements (good agreement) — but at processing
concentrations, not espresso. Density fit R^2 ~0.989 (2013 cross-check).

## Assumptions and validity range
- Newtonian in the espresso band (verified by source's own transition threshold).
- Extrapolation toward pure water is smooth and monotone — plausible but
  unvalidated at espresso TDS.
- No account of espresso-specific colloids (emulsified oils, CO2, melanoidin
  foam) which the instant-coffee extract lacks; these could raise apparent
  viscosity beyond the smooth extrapolation. Flagged.

## Interface mapping
Inputs: local TDS (from extraction stage output), temperature. Outputs: mu, rho
for the flow closure. Couplings: replaces the pure-water constants in
waszkiewicz2025/constants and in any Darcy/Forchheimer flow gate. Adapter:
mu_local = mu(T, c_local) evaluated per cell where c_local is dissolved-solids
fraction; carry reference-strength tag.

## Extractable data
`liquor_rheology.csv` (this directory). Full T-Xw fit coefficients would need the
Telis-Romero 2001 tables — both papers are paywalled (Wiley/Tandfonline, bot-
blocked here). The CSV captures the espresso-relevant envelope + forms; the exact
5-parameter coefficients are a **Tim drop** if quantitative per-cell mu(T,c) is
wanted (see Access).

## Overlaps and conflicts
No conflict; fills a gap all flow components share. Note the RC-2/RC-3 shared
early-shot bias is the symptom G10 targets — but confirm the bias magnitude is
consistent with only a ~1.3-2x viscosity bump before attributing all of it here
(some may be the swelling/first-drop-offset effects already carded elsewhere).

## Access
Telis-Romero 2001 (Wiley) and 2000 (Tandfonline) are **paywalled and bot-blocked**
in this environment — the abstracts, ranges, and forms are captured above from
search snippets and the open 2013 cross-check, but the numeric fit tables need a
**Tim drop** (institutional access) into `puckworks/data/g10_liquor_rheology/`
if per-cell quantitative mu(T,c) is required. For a reference-strength envelope,
the CSV as-is suffices.

## Implementation estimate
Low-to-medium. Reference envelope ready now. Quantitative per-cell closure needs
the Telis-Romero tables (Tim drop). Gate: "does swapping pure-water mu for the
reference espresso mu reduce the RC-2/RC-3 early-shot bias without breaking
equilibrium agreement?" — a directional improvement check at reference-strength.
**IMPLEMENTED 2026-07-12** (`harness.g10_mu_bias_direction`,
`gate_g10_mu_bias_directional`): Darcy Q~1/mu with the 1.27-1.90x reference mu
suppresses EARLY-shot flow to ~0.53-0.79x the pure-water prediction while leaving
the dilute LATE/equilibrium flow unchanged (x1.0) — directionally correct + bounded
~1.3-2x. Consistency check only (no espresso-TDS flow measured); confirm the real
early-shot bias is not much larger before attributing all of it to viscosity.
