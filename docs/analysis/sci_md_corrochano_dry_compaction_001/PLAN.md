# SCI-MD-CORROCHANO-DRY-COMPACTION-001

G1 / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL /
NO_GOVERNING_PHYSICS_CHANGE / PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Question: how much force reaches a fixed absolute dry bulk density across grinds,
how much additional force produces fixed density increments, and can all twelve
represented samples share F_j(rho_k)=a_j+f_k with arbitrary constant force offsets?
New information is a dry mechanical observation constraint distinct from the
existing hydraulic studies. Its consequence is limited exclusion or non-exclusion
of that finite null, without fitting a material law or validating a solver.
This bounds the packing behavior a grinder-to-cup model would have to reproduce.

Actual Puckworks base: bf65fa3d9bd9664545bb3fb4e1e97fc1e0ebc94b (PR351 merged).
Read-only EWP main: f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516.
Both remote main refs reconfirmed at intake. Isolated Puckworks worktree only.

## Fixed reporting and arithmetic

Twelve graphical identities B1–B3, C1–C3, D1–D3, E1–E3, not instrument IDs.
Force at density 360,400,480,500,520 kg/m³: 60 requests.
Density at force 25,50,100,150,200,250 N: 72 requests.
Within-sample increments PRIMARY 480→500 and SECONDARY 500→520 kg/m³: 24 requests.
Retain all 156 with explicit SUPPORTED, UNSUPPORTED,
AMBIGUOUS / MULTIPLE_INTERSECTIONS, or NUMERICALLY_UNRESOLVED dispositions and reasons.

For each same-sample pair, D_j=[L_b-U_a,U_b-L_a]. No sign clamp. Only afterward
form each grind envelope [min_j D_j.lower,max_j D_j.upper]. COMPLETE requires
all three samples and both endpoints supported; conservative all-crossing hulls
qualify if their full support is established, but remain explicitly ambiguous.
Keep partial envelopes descriptive and mark INCOMPLETE. Retain all six unordered
grind pairs for each increment (12 comparisons). Difference sign is second-minus-first.
STRICTLY_SEPARATED requires both complete envelopes and strictly positive lower
or strictly negative upper difference. Zero/touch/overlap is
NOT_EXCLUDED_BY_THIS_COMPARISON. Incompleteness is UNSUPPORTED_OR_INCOMPLETE.
Keep pair-specific descriptive arithmetic separate from the complete-envelope rule.

A single complete separation is sufficient for
EXCLUDED_BY_COMPLETE_INCREMENT_SEPARATION. Otherwise use
NOT_EXCLUDED_BY_THE_DECLARED_COMPARISONS if all twelve comparisons qualify;
if any remain incomplete use UNRESOLVED_DUE_TO_SUPPORT_OR_READING_LIMITS.
No joint-feasibility claim follows from overlap: 500 kg/m³ and shared calibration
couple the two increments. No a_j or f_k fit. Exact rational arithmetic from retained
decimal coordinates decides signs; six-decimal displays round outward afterward.

## Fixed source-reading contract

Freeze after factual source inspection, before formal comparison. The thesis SHA256
is f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818.
Figure6.2 printed223 / one-based PDF248 / zero-based247. Dataset paths.json retains
page/content identities, original decimal path operands and their composed page
coordinates, all 152 paintings of 76 unique curve chunks, four excluded legend
strokes, source order, styles and 64 joins. Twelve independent sample measurements
are represented by the caption, not 24 observations. Raw paths have no internal
moves after their first point. Dash spaces are deliberate stroke styling over an
explicit recovered continuous source path, not missing data. Never bridge an
actual unrecorded path gap. The 64 joins are source-decimal rounding discrepancies
at most0.000607381 pt, below the predeclared0.001 pt join limit; retain both ends
and a bounded straight connector. No added terminal support.

Axes: affine0/300 N and300/650 kg/m³ using original endpoint ticks; retain all
interior ticks and residuals. Maximum tick residual <0.044 pt. Local3 pt stroke
transforms once by diag(0.6073214,0.6073809); maximum effective width1.8221427 pt,
half0.91107135 pt. Butt caps and round joins. The source-based adopted allowance is
**±1 pt per shared axis anchor and ±1 pt per trace coordinate, in both axes**.
Each1 pt covers half stroke plus0.08892865 pt additional graphical allowance,
including tick residual, <0.0002 pt API reconstruction check and <0.001 pt joins.
For in-range queries their sum is a total±2 pt rectangular allowance. This independently
constructed allocation adopts the exposed2 pt starting hypothesis; it is not a
2 pt trace guard plus another2 pt calibration guard. No force-dependent tuning.

For either query direction: enumerate all shared anchor corners, inverse map the
requested physical value, take the hull and expand±1 pt in the query coordinate.
The **entire** admissible interval must lie in the union of explicitly supported
segment projections. Never truncate to an endpoint or fill an unsupported gap.
Clip each original linear segment to the query strip, retain ALL intersections
including vertical/horizontal and reverse-going portions, and project onto the
other coordinate. Expand each output interval±1 pt and map every output-axis
anchor corner. Retain the union and conservative hull; label multiple centerline
crossings or admitted strip branches. Do not select an arbitrary inverse branch.
A fold remains source geometry, not a reason to impose monotonicity.

Bounds are graphical-reading outer enclosures. Marginal propagation relaxes
shared axes, calibration, geometry and the common500 reading; extrema need not be
jointly attainable. These are distinct from represented-curve variation, documented
instrument uncertainty (no quantified mechanical budget recovered), and unknown
physical variability. No confidence intervals, sampling population or significance.

## Non-blinded exposure

Selection followed exploratory graphical extraction. Supplied outward whole-N
bands below are motivation, never fitting targets or regression oracles:

| Grind | F480 (N) | D480→500 (N) | D500→520 (N) |
|---|---|---|---|
| B | [9,18] | [0,17] | [3,23] |
| C | [23,35] | [6,30] | [12,40] |
| D | [53,79] | [15,50] | [24,64] |
| E | [100,149] | [27,81] | [35,96] |

The proposed B/E separations are only motivation. Diagnose disagreements without
optimizing the allowance, calibration, assignment or support. No holdout claim.

## Delivery and boundaries

Commit this plan, reconciliation and machine-readable contract before scoring.
Provide compact factual input, optional exact-PDF audit, deterministic offline
producer, all request/support tables, original VizSpec figure, result, one independent
scientific review (including independent coordinate arithmetic and unsupported case),
and verification receipts. Run synthetic scientific failure-mode tests, affected
regressions, normal suite and required hosted checks. Register only appropriate
manifest/loader/card/index projections. No dependency pin/default/physics changes,
Smrke repair, EWP edit, stress/porosity/strain mapping, extrapolation to larger
hydrodynamic forces, or new campaign. Leave one OPEN/DRAFT/UNMERGED PR, auto-merge
disabled, then stop. Force-offset exclusion does not exclude F_j(rho)=G(rho-b_j),
initial-state-relative strain behavior, or establish a mechanism or physical validation.
