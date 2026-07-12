# Data card: khomyakov2020 — coffee-extract kinematic viscosity (G10)

**Paper:** Khomyakov, Mordanov & Khomyakova (2020), "The experimental data on the
density, viscosity, and boiling temperature of the coffee extract," IOP Conf. Ser.:
Earth Environ. Sci. 548, 022040. DOI 10.1088/1755-1315/548/2/022040. **CC BY 3.0.**
**Stage(s):** flow (fluid properties) · **Kind:** calibration (data source)
**Status:** PARTIALLY SOURCED for G10 — the MEASURED kinematic-viscosity table is
usable at reference strength; the printed density + dynamic-viscosity regressions
are QUARANTINED (unresolved source conflicts). Does NOT resolve G10.

## What it supplies (and its limits)
Measured **kinematic viscosity** ν [mm²/s] of industrial soluble-coffee extract
over **dry-solids 15–70 wt%** and **T 20–80 °C** (Table 1; 60 points, on disk as
`data/g10_liquor_rheology/khomyakov2020_kinematic_viscosity.csv`, loader
`khomyakov_kinematic_viscosity`). A second measured coffee-extract source for G10
alongside the Telis-Romero reference envelope (`g10_liquor_rheology`), with the
advantage that it is a full measured grid, not a snippet-derived envelope.

**Load-bearing domain guard (why it does NOT close G10):**
- Lowest measured solids is **15 wt%**, ABOVE espresso TDS (~4–12 wt%) → espresso
  use is an **extrapolation toward the dilute end**; do NOT extrapolate below
  15 wt% silently.
- Industrial soluble-coffee extract, not a fraction-resolved espresso series.
- Kinematic (not dynamic) viscosity; converting ν→μ needs a density, and the
  source's density equation is quarantined (below), so no clean μ here.
- Physical consistency verified (smoke test): ν decreases monotonically with T and
  increases with solids — consistent with the Telis-Romero envelope direction and
  the G10 μ-bias picture (`gate_g10_mu_bias_directional`).

## QUARANTINED — do NOT promote to a production closure
Preserved as source transcriptions in the same directory, **not loaded**:
- `khomyakov2020_density_equation_FLAGGED.csv` — printed `ρ = 932 + 0.8·T + 509·f`;
  the **+0.8·T** term makes ρ RISE with T, contradicting the paper's own prose
  (ρ decreases with T). Sign likely a typo; needs author clarification / cross-check
  vs Telis-Romero 2000.
- `khomyakov2020_dynamic_viscosity_regression_QUARANTINED.csv` — Table 2 power-law
  coefficients μ = a·(T/100)^b. Literal evaluation with T in °C does NOT reproduce
  the measured Table 1 (off by 5.8×–1194×, see the FLAGGED consistency diagnostic);
  the convention/typesetting needs clarification. No f=0.25 row published; authors
  call the regressions approximate (4.0–16.2 % error).
- `khomyakov2020_regression_consistency_FLAGGED.csv` — the diagnostic that shows
  the above mismatch. A DIAGNOSTIC, not a corrected model.

An author-clarification email draft is in `docs/sourcing/` (G10 clarification).

## Overlaps
Complements `g10_liquor_rheology` (Telis-Romero envelope): khomyakov is measured
but ≥15 wt% (farther from espresso); Telis-Romero extends to 10 wt% but is
snippet-derived. Neither reaches espresso TDS — both are reference/qualitative for
espresso. Stronger acquisition targets remain the full Telis-Romero 2000/2001
tables (Tim institutional drop).

## Access
Open CC BY 3.0 (IOP). Tables transcribed with attribution; no PDF redistributed.

VERDICT: reference/qualitative measured kinematic-viscosity grid for G10; a real
measured second source, but its 15 wt% floor keeps espresso an extrapolation and
both printed closure equations are quarantined pending author clarification. G10
stays PARTIAL — effort to intake the measured table S (done); a production espresso
μ(T,c) closure still needs a sub-15 wt% measured source. — effort S.
