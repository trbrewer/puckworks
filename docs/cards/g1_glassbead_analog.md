# Data card: g1_glassbead_analog (REFERENCE-STRENGTH shape prior for G1)

**Paper:** H. Yasuda, H. Katsuragi, M. Katsura, "Liquid water transport model in
hydrophilic granular: Preliminary validation with drying rate of hierarchical
granular." arXiv:2501.13361 (2025). Appendix B compiles glass-bead retention /
permeability from Sweijen et al. (2017, Adv. Water Resour. 107, 22), Culligan et
al. (2004), Hilpert & Miller (2001), and Topp & Miller (1966, SSSAJ 30, 156).
**Stage(s):** infiltration (unsaturated flow) · **Kind:** calibration (data source)
**Status:** proposed — REFERENCE/QUALITATIVE strength only. Does NOT close G1.

## Why this exists and what it is (and is NOT)
This is the **analog fallback** explicitly sanctioned by
`g1_retention_search_target.md` ("retention/K_r for a particle-size-matched inert
powder or fine granular medium, used as a shape prior until a coffee-specific
measurement appears"). It supplies the two constitutive functions Richards' eq.
needs — a retention curve theta(psi) shape and a relative-permeability law
K_r(S) — for **spherical glass beads**, NOT coffee. Its role is to let the G1
Richards machinery (egidi2018 solver) *run* with a physically-sane closure so
P3 hypothesis #2 (incomplete wetting) becomes computable. It is a shape prior,
not a validated coffee law.

**It must be tagged `reference/qualitative` per ROADMAP §0** and must NOT be
upgraded to `independent` without a §7.1 entry backed by a coffee-specific
measurement. The search-target card stays OPEN.

## Governing forms provided
1. Relative permeability (Mualem-type cubic):
   K = K0 * ((S - S_r)/(1 - S_r))^3         [Eq. 41; n=3 confirmed by fit]
   with S_r = 0.07 (residual saturation, 180 um beads, Topp-Miller data).
2. Absolute permeability scale (Kozeny-Carman):
   K0 = eps^3 * d^2 / (180 * (1-eps)^2)     [Eq. 42]
3. Capillary pressure (linearized van-Genuchten over 0.2<S<0.8):
   dPc/dS = -Gamma / (alpha * d)             [Eq. 39]
   alpha ~ 0.36 (wide PSD, ~50% dispersion — the closer analog to a real grind).

## Parameters
| symbol | value | units | source |
| S_r | 0.07 | - | fitted (Topp-Miller 180um beads) |
| n_Kr | 3 | - | fitted (cubic K_r) |
| alpha | 0.36 | - | fitted (GB2 wide dist) |
| K0 (max meas.) | 3.0e-11 | m^2 | measured (180um beads) |
| eps | 0.49 | - | representative (wide-dist bed) |
| De0L | 6.9e-3 | - | derived (Eq. 45) |

## Calibration and validation offered by the source
Glass-bead retention (Pc-S) and permeability (K-S) are *measured* in the cited
soil-physics literature and here re-compiled and fit. The cubic K_r and
linearized VG are good over the intermediate saturation band (0.2-0.8); both
break near S_r and near full saturation (Pc rises sharply). Validation in the
paper is against *drying-rate* curves, not espresso infiltration.

## Assumptions and validity range
- Spherical, near-monodisperse to moderately-disperse glass beads. Coffee grinds
  are angular, deformable, dual-porosity, and hydrophilic-to-oily — so this
  transfers **shape, not magnitude**. Use it to get K_r(S) curvature and an S_r,
  NOT to predict a coffee bed's actual capillary entry pressure.
- Newtonian pure water, isothermal. No swelling, no fines migration.
- Intermediate-S band only; do not trust the closure below S_r or above ~0.9.

## Interface mapping
Inputs consumed: bed porosity eps, representative particle size d (from
grindmap / wadsworth2026), saturation S. Outputs produced: K_r(S), Pc(S) shape
for the Richards/egidi2018 solver. Adapter needed: map grind d -> K0 via
Kozeny-Carman; carry the reference-strength tag through any gate that uses it.

## Extractable data
`glassbead_retention_kr.csv` (this directory): the six closure parameters + two
capillary slopes + KC formula, with saturation ranges and source eq/fig cited.

## Overlaps and conflicts
Complements (does not compete with) foster2025_2 — foster is the sharp-front
infiltration runtime; this is the partial-saturation closure foster deliberately
collapses. It does NOT satisfy the G1 search target (which requires a coffee
measurement). Keep both: foster for the front, this for the (analog) profile
behind it.

## Access
arXiv:2501.13361 — OPEN, fetched cleanly in this environment (no Cloudflare
block). No Tim drop needed. Underlying bead data are from the cited 1966-2017
soil-physics papers.

## Implementation estimate
Low. CSV is ready. Gate would be: "does egidi2018 with this closure produce a
partial-saturation profile behind the wetting front that is qualitatively
consistent with foster's front position?" — a *consistency* check at
reference-strength, not a validation. Flag prominently that G1 remains OPEN for
an independent coffee retention curve.
