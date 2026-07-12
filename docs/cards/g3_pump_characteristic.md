# Data card: g3_pump_characteristic (vibration-pump P-Q envelope)

**Sources:** Ulka/Repa vibration-pump catalogue (EAX5/EAP5/EP5 datasheets,
distributor listings); Decent Espresso engineering blog ("Perfectly Calibrating
Decent Flow Measurements", decentespresso.com); community hydraulics
(espressoaf.com "Understanding Pressure and Flow", coffeeforums.co.uk).
**Stage(s):** flow / machine mode · **Kind:** calibration (boundary condition)
**Status:** proposed — MIXED strength (see below). Partially unblocks G3/RC-3.

## Scope and mechanism
RC-3 machine mode currently rests on a *nominal manufacturer quadratic*. G3 asks
for a real pump/flow-bench characteristic, DE1 preferred. This card supplies the
**physical envelope** of the Ulka vibration pump that sits under the DE1 (P500 /
EAX5-class): manufacturer-stated free-flow debit and deadhead pressure, plus the
qualitative shape of the P-Q curve, which for a vibration pump is a **monotone,
concave droop — not a clean quadratic**.

## The honest limitation (read before using)
The *exact* DE1 pump characteristic is a physics model living in the closed ESP32
firmware; Decent's own blog confirms it exists, is voltage/frequency dependent,
and is country-calibrated, but the coefficients are not published. The open
`de1app` (Tcl) only *receives* firmware flow estimates. So a DE1-specific
measured curve at `independent` strength is NOT obtainable from public sources
in this environment — it would require either bench measurement (a TB task) or a
data request to Decent.

What IS obtainable, and what this card provides:
- **Manufacturer endpoints (reference-strength):** free flow ~10.8 mL/s
  (650 cc/min, 120V/60Hz), max pressure 15 bar deadhead. Both are catalogue
  values with a stated +/-15% tolerance on Ulka performance tables.
- **Curve shape (qualitative):** flow falls with back-pressure; the physical
  reason (stroke shortens when the compression stroke can't finish before the
  next AC pulse) means the droop is concave and steepens toward stall. A
  quadratic DP = aQ^2+bQ+c is a *fitting* form, not the pump's physics.

## Parameters
| symbol | value | units | source |
| Q_free (EAX5, 120V) | 10.8 | mL/s | manufacturer (650 cc/min) |
| Q_free (community) | ~8 | mL/s | espressoaf (practical) |
| P_deadhead | 15 | bar | manufacturer |
| P_operating | 9 | bar | convention (OPV/DE1 target) |
| duty cycle | 1/1.5 | min on/off | manufacturer |

## Calibration and validation offered by the source
None at bench-measurement strength for the DE1. The Ulka endpoints are
type-test catalogue figures (+/-15%). Use for BOUNDS and SHAPE, not for a
calibrated Q(P) at a working point.

## Assumptions and validity range
- 120V/60Hz (US, Tim's Austin bench). EU 230V/50Hz shifts the curve — Decent
  recalibrates per country; do not port US coefficients to a 50Hz rig.
- Cold-coil, 20C water (catalogue condition). Hot brew water and a warm coil
  both reduce output; the operating curve sits below catalogue.
- Pure water. Coffee liquor (see G10) raises viscosity and shifts Q(P) further.

## Interface mapping
Inputs: system back-pressure P (bar). Outputs: available pump flow Q (mL/s) as a
bounded, concave-droop envelope. Couplings: sits upstream of the puck resistance;
in RC-3 machine mode it sets the flow boundary condition. Adapter: reconcile
with the already-on-disk `waszkiewicz2025/brewer_quadratic` (measured single-rig
DP=aQ^2+bQ+c) — that stays the operative measured quadratic; THIS card adds the
manufacturer envelope + DE1-shape context around it.

## Extractable data
`pump_characteristic_ulka.csv` (this directory).

## Overlaps and conflicts
Does not replace `waszkiewicz2025/brewer_quadratic` (the one measured machine
quadratic in the repo). Complements it by (a) bounding it against manufacturer
endpoints and (b) flagging that the true vibe-pump shape is concave, so a
quadratic fit outside the measured range will mislead.

## Access
All public, all fetched cleanly (Decent blog, Ulka distributor pages,
espressoaf). No Tim drop needed for THIS envelope. A true DE1 `independent`
curve would need a bench pull (TB) or a Decent data request (§5.8 correspondence).

## Implementation estimate
Low for the envelope. Recommend: keep RC-3 on the measured waszkiewicz quadratic;
use this card to (1) sanity-bound that quadratic, (2) document why G3 stays
partially open (no independent DE1 curve), (3) seed a §5.8 correspondence line to
Decent or a TB bench-pull task if an independent curve is wanted.
