# Cameron local computational audit, 2026-09-30

This owner-authorized retrospective audit starts from Puckworks
`713c3c229568bb189c548f4c8a490b69a6319bef`. The interpolation correction is
`NUMERICAL_METHOD_CHANGE`: it restores Supplemental Equation 3 without changing
C_S0, the printed bed-depth rule, kinetics, fitting data, or physical EY. Basis,
DOI and display corrections are `NO_GOVERNING_PHYSICS_CHANGE`. No physical
validation, merge, publishing, or new protected-target scoring is claimed.

## Executed correction

The source's Supplemental Information, Table S2 and Eq. 3, makes phase fractions
and radius the measured primitives and infers spherical area from them. The old
implementation interpolated the area independently of the radius, so its implied
particle volume differed from the phase fractions away from knots. Deriving
`b_i = 3*phi_i/a_i` after primitive interpolation preserves those fractions in the
release source, initial inventory, final inventory and retained liquid calculation.
The original knot values are unchanged (up to floating-point arithmetic). The
boulder source table is rounded, not exact; the fines table is inconsistent with
its stated 12 µm radius and implies approximately 49.7 µm. The existing choice of
measured fractions plus stated 12 µm radius is retained. These are geometric areas;
Table S2 describes them as inferred, not separately measured effective surface areas.

At 20 g in, 40 g out, 5 bar overpressure, N=40/M=24:

| GS | Old EY, % | Corrected EY, % | Old EY−EY_solid, pp |
|---|---:|---:|---:|
| 1.1 | 16.897824 | 16.864639 | 0.098443 |
| 1.3 | 16.427339 | 16.376745 | 0.147664 |
| 1.5 | 15.865497 | 15.865497 | <1e-12 |
| 1.7 | 15.589551 | 15.589551 | <1e-12 |
| 1.9 | 15.390531 | 15.390531 | <1e-12 |
| 2.1 | 14.965492 | 14.929997 | 0.101551 |
| 2.3 | 14.150135 | 14.097263 | 0.152326 |

Both seven-grind sweeps (C_S0=118 and 118/0.8272) and the six-resolution GS2.1
study were executed before and after the correction. The largest change in default
EY is −0.052872 pp; under the caller's alternate inventory it is −0.063907 pp.
Across these 19 cases, corrected cup/solid/retained-liquid balance closes within
3.2e-17 kg and EY−EY_solid within 1.7e-13 pp. The independent accounting regressions
fail 24/48 before and pass 48/48 after. The 320×48 corrected GS2.1 EY is 15.066680%,
versus 14.929997% at 40×24; spatial error remains separate from mass conservation.

## Source and basis limits

The final publisher main text plus complete SI was inspected visually alongside
the accepted manuscript and article-in-press version: *Matter* 2, 631–648,
DOI [10.1016/j.matt.2019.12.019](https://doi.org/10.1016/j.matt.2019.12.019).
Final Fig. 5 is journal p. 642; Eqs. 24–26 are p. 638; SI Table S1/S2 is SI p. 3.
Independent figure readings agree with Reviewer 2 within 0.02 EY pp. Visible error
bars are **one standard deviation**, not standard error; reading allowance is
separate. Corrected default homogeneous-curve RMSE is 7.1024 EY pp, versus 7.0781
before, on those readings. The accounting repair does not cure source reproduction.

The initial grain concentration is 118 kg/m³. With retained printed Eq. 25,
`V = dose*phi_s/rho_grounds`, its initial inventory is
`100*V*phi_s*C_S0/dose = 24.467473%` of dose. The streamtube explicitly requests
118/phi_s and therefore 29.578667%; this is a distinct caller input. Runtime product
inventory numbers now come from `inventory_ceiling_percent()` rather than 29.6%.
The legacy `reference_basis` bed-volume classification describes the aggregated
inventory `c_bed=phi_s*c_s`, not the underlying grain field and not the denominator
of physical EY, which remains dry dose.

Table S1 calls 330 kg/m³ a bulk density. Its normal mass/volume identity would give
22.625620 mm bed depth; printed Eq. 25 instead gives 18.715912 mm and implies bulk
density 398.936170 kg/m³. Treating 330 as intrinsic particle density would instead
give 27.352055 mm. None is silently substituted into production. Relative to the
printed geometry, the released MATLAB EY factor differs by phi_s^-2=1.461433;
that algebra is an internal inconsistency, not proof of author intent or the exact
configuration generating Fig. 5.

Authors' code at `79ebefb72446eb706084e2392cab64bf0fad93a2` was read, not executed:
MATLAB and Octave were unavailable in the inspected local installation locations.
It integrates to dimensionless T_end=10, so its full-horizon EY is distinct from a
one-shot integral; its a1=80 µm, a2=300 µm, k=1e-9 and Deff=1e-6 differ from the
paper/Puckworks configuration. No Python execution is represented as MATLAB.

## Claim propagation and historical records

The registry/card, common product inventory strings, live cross-card comparisons,
source DOI metadata and current roadmap now distinguish the operative inventory.
Generated discovery/data-register views were regenerated from their existing
commands; their commit fingerprints account for most of the generated diff. No
new identity, status, schema, assurance machinery or evidence-strength promotion
was introduced. Historical I-076 protocols/results, earlier roadmap log entries,
source-intake audit records and frozen experiment receipts remain unchanged; their
29.6% descriptions are historical, not authority for the current default. The
Paper A/B/3 surfaces were searched; no literal inventory substitution was needed.
Their broader scientific claims require their own retained comparisons.

Focused after-change tests: 248 passed (accounting, basis, quantity semantics,
product report, product execution, I-076 and discovery staleness), plus all 8 slow import-order cases (148.71 s). The integrated normal lane is
recorded separately in the private audit.
A pre-change run preserved five matplotlib/NumPy ABI failures before the isolated
audit environment was corrected; these were environment failures, not F13 failures.
The complete private audit retains source hashes, rendered pages, independent pixel
coordinates, CSVs, commands and before/after failures; rights-restricted source
pages and local source paths are not copied into this repository.
