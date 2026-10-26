# Figure 12 fixed-flow pressure-labelled comparison

**Source-qualified observational comparison.** Native Figure 12 centers define two separate
piecewise-linear concentration profiles. All 14 central and graphical requests are
supported. Graphically resolved: a at 800 g (NEGATIVE).
The other 13 intervals include zero; this does not establish equality or equivalence.

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.

## Fixed beverage masses

Units: mg solubles/g beverage; Δc = 9.0-bar-labelled − 2.3-bar-labelled.
Central numbers round to .001; sensitivity endpoints round outward to .001.

| Panel | M (g) | c_L | c_H | Δc | Graphical enclosure | Sign |
|---|---:|---:|---:|---:|---|---|
| a | 50 | 182.218 | 172.605 | -9.613 | [-22.928, 4.137] | SIGN_UNRESOLVED |
| a | 100 | 123.362 | 118.949 | -4.413 | [-14.270, 5.328] | SIGN_UNRESOLVED |
| a | 200 | 72.262 | 69.595 | -2.666 | [-7.192, 1.800] | SIGN_UNRESOLVED |
| a | 400 | 37.726 | 36.845 | -0.880 | [-3.384, 1.605] | SIGN_UNRESOLVED |
| a | 600 | 25.850 | 24.054 | -1.797 | [-3.766, 0.130] | SIGN_UNRESOLVED |
| a | 800 | 19.285 | 17.317 | -1.968 | [-3.667, -0.308] | NEGATIVE |
| a | 900 | 16.816 | 15.806 | -1.010 | [-2.666, 0.623] | SIGN_UNRESOLVED |
| b | 50 | 157.938 | 147.044 | -10.894 | [-35.219, 15.878] | SIGN_UNRESOLVED |
| b | 100 | 45.628 | 47.622 | 1.993 | [-9.644, 13.047] | SIGN_UNRESOLVED |
| b | 200 | 13.582 | 11.639 | -1.944 | [-4.930, 0.999] | SIGN_UNRESOLVED |
| b | 400 | 2.789 | 1.815 | -0.973 | [-2.750, 0.780] | SIGN_UNRESOLVED |
| b | 600 | 0.412 | -0.639 | -1.051 | [-2.618, 0.490] | SIGN_UNRESOLVED |
| b | 800 | -0.493 | -0.639 | -0.145 | [-1.633, 1.339] | SIGN_UNRESOLVED |
| b | 900 | -0.493 | -0.639 | -0.145 | [-1.633, 1.339] | SIGN_UNRESOLVED |

## Central domains and extrema

All attaining locations are retained in results.json and linked to union_knots.csv.
These exact rational calculations concern the declared interpolants, not bounds on
unknown physical concentration curves. No extrapolation, clipping or smoothing.

Panel a common support: [22.014325634, 933.354631137] g; 42 union knots.
- minimum: -9.887383549 mg/g at 48.134218244 g.
- maximum: -0.385724194 mg/g at 413.713608023 g.
- maximum_absolute: 9.887383549 mg/g at 48.134218244 g.

Panel b common support: [22.554655050, 934.832178572] g; 43 union knots.
- minimum: -11.321757950 mg/g at 51.183569878 g.
- maximum: 2.803524281 mg/g at 101.115413704 g.
- maximum_absolute: 11.321757950 mg/g at 51.183569878 g.

There are no tied extremal knots or constant attaining intervals in these data.

## Qualification and limits

The accepted 19-page publisher PDF was inspected as native paths and rendered pages.
All 94 legacy rows match: 90 observations (22 low + 23 high per panel), four
confirmed legend samples (rows 7, 32, 54, 79), zero ambiguous/omitted markers.
All 44 low-pressure markers reuse Figure 3 observations; no additional campaign or
independent extraction count is inferred. Figure 12 coordinates are primary.

The graphical convention is 0.25 PDF point plus half applicable stroke width,
enclosing center candidates and including all tick residuals. Both axes vary.
Horizontal marginal rectangles drop shared-calibration dependencies; native ordinate
contrasts cancel the shared vertical offset and apply a shared scale once.
These conservative outer bounds are not sharp or jointly attaining source geometries.
Universal support and coordinate order are checked independently of possible brackets.

The source identifies JK standard drip-filter coffee, nominal 60 g (approximately
4% moisture in the reused baseline), and 250 mL/min. Pressure wording remains
unreconciled: Figure 3 calls the baseline differential pressure; G.3/Figure 12
call the comparison absolute pressure. No gauge conversion or bed-pressure change
is authenticated. Equal nominal flow/loading do not establish equal wetting, porosity,
residence-time distribution or all other conditions.

Pot and exit concentrations remain distinct. Replicates, averaging, flow-through
assay error, covariance, sampling windows, pot mixing/withdrawals and run joins
are unknown. Batch Brix calibration is contextual, not Figure 12 uncertainty.
Optional solute-mass differences are unsupported at all seven pot masses because
the high-pressure cumulative-denominator/withdrawal contract is not authenticated.
Relative contrasts are omitted; signed tail readings are retained.

The authors interpreted the curves as substantially pressure independent and
reproducible within a few percent. This task establishes only the displayed
source-conditioned differences and their declared graphical sensitivity.
Graphical separation is not statistical significance or a causal pressure effect.
Zero inclusion is not equality, common-curve compatibility or practical equivalence;
no adequacy margin is supplied. Nothing establishes universal pressure-independent
dissolution/diffusion or that pressure acts only through flow.

SCI-MD-MORONEY-TRANSFER-001 remains CALIBRATION_INADEQUATE. No model, production
default, solver, dependency pin/lock or EWP change; no successor authorized.

[Source contract](SOURCE_NOTES.md) · [Plan](PLAN.md) · [Reproduction and checks](VERIFICATION.md)
· [Independent review](review/REVIEW.md) · [Figure](COMPARISON.svg) · [VizSpec](VIZ_SPEC.json)

PHYSICAL_VALIDATION=NOT_ESTABLISHED.
