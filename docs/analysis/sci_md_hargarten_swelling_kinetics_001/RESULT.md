# Individual swelling histories and the radius-squared clock

**SCI-MD-HARGARTEN-SWELLING-KINETICS-001.** The retained Figure 10 graphical
histories require additional discrepancy from a shared radius-squared response
in three of four source groups, beyond their individual monotone discrepancies.
Medium/25°C needs no additional penalty on the supported subset. **These are
certified mathematical statements about a conditional graphical representation.**
Figure 7 and Figure 10 materially disagree under their stated transformation, and
some plotted times disagree with the methods. A jointly consistent original
measurement history and physical mechanism conclusions remain **UNRESOLVED**.
The unchanged Mo parameterization has larger supported graphical discrepancies
than each particle's monotone baseline; it also has a native finite-grid initial
endpoint defect. No diffusivity or other model parameter was fitted.

G1 / SOURCE_INTERNAL / RETROSPECTIVE / TARGET_EXPOSED / NONSCORING /
RESEARCH_ONLY / NO_GOVERNING_PHYSICS_CHANGE.
**PHYSICAL_VALIDATION=NOT_ESTABLISHED.** Same source campaign,17 particles;
Figure 7 and Figure 10 are not independent samples. EWP is unchanged.

## A. What the source measured

The source measured binary microscope projection areas of glued coarse particles
and reported area-equivalent circular diameters. Figure 7 shows relative diameter
growth through 1200 s; Figure 10 reports diameter growth normalized to the20-minute
growth difference, enlarged through 300 s. Eq. 4 is
`p(t)=(d(t)-d(0))/(d(1200)-d(0))`, not diameter divided by final diameter and not
volume uptake. Positive reference growth is the hypothesis behind the comparators.
Methods first analyze a10 s frame. Earlier-looking native graphical coordinates
below 10 s **do not authenticate earlier physical measurements**.

Circles represent hot microscopy (approximately 80 °C inside the cell), triangles
25°C. Hot reservoir water cools to about 60 °C. The separate PSD preparation starts
90°C; that temperature must not be assigned to microscopy. Room 25 °C is the cleaner
approximate constant-temperature structural comparison. Constant t/R² for hot
particles is deliberately conditional and cannot reject temperature-dependent
transport. R=d_proj/2 is an equivalent-sphere modeling assumption, not a measured
true 3-D radius. Pressure, fines, spherical geometry and espresso extraction behavior
are not validated.

The authenticated published PDF has SHA256
`4a41545954e6748a33ec1d956fd690bea58aba9c2e38955dfbb3ae9f5bffbfb0`.
Original figures, captions, methods and Table 2 were inspected directly; no reprint
substitution. Source-derived readings retain Hargarten et al.(2020),
[DOI10.1002/jsfa.10440](https://doi.org/10.1002/jsfa.10440), CC BY-NC attribution.
[Source record](../../../puckworks/data/hargarten2020/swelling_kinetics_001/PROVENANCE.md)
contains calibration, rights, protocol and bounded holdings-search details.
Only the two existing aggregate/scalar CSVs were found in the targeted configured
inventory search; no original per-particle files were authenticated there. This
says nothing about unsearched holdings.

There are **226 supported native markers**:110 in Figure 7
and116 in Figure 10, plus 64 unsupported/clipped/overlapping feature records and 4 dry-origin
definition rows. Those 64 are graphical features, not a count of missing particles
or missing measurements. Coverage is partial for every trajectory; only the 116
supported Figure 10points enter primary comparisons. Light 462 has only 2 supported
points: its forced discrepancy is informative for those readings, while a full
kinetic history is insufficiently supported.

A concrete conflict is medium543 µm near 120 s: Figure 7 gives approximately 4.54%
growth relative to approximately 5.02% at 1200 s (about 90% progress), while Figure 10
gives approximately 139%. The [consistency table](figure_consistency.json) retains
outer reading intervals and conditional same-frame joins; separation survives
those allowances. Source text supplies no reconciliation. Medium hot Figure 7
circles end near 1154 s; they are not silently treated as exact 1200 s references.
[Separate conditional Figure 7 conversions](figure7_converted.json) retain shared
reference dependence and missing references. They are never pooled withFigure 10.

## B. Individual monotone discrepancy

The metric is minimum maximum distance from a model value to the graphical
ordinate interval. Fixed-coordinate intervals use common nominal axis calibration
and±3 native pixels per marker. Fractions are internal; reported discrepancies below
are **percentage points(pp)**. A nondecreasing p with p(0)=0,p(T)=1 necessarily lies
in[0,1] before T. Observed >100% and decreasing readings are preserved as discrepancies.
No negative source marker was authenticated; negative handling is tested synthetically.
Graphical allowances andB_i are not laboratory uncertainty estimates.

For interior readings, the exact optimum is the maximum of0, eachL−1, each−U,
and every (L_earlier−U_later)/2. Equal times impose both orderings. Observations
exactly at0/T impose their full distance to0/1. Cumulative maxima of L−B, with
endpoints, construct the optimum witness. [Exact baselines](baselines.json) retain
decisive pairs/endpoints; [baseline table](monotone_baselines.csv) is convenient for
inspection. A zero B does not establish a complete monotone measured history.

| Particle / µm | Protocol | n | Native span / s | First graphical progress / % | B_i / pp | Mo N240 / pp | Mo−B_i / pp |
|---|---|---:|---|---:|---:|---:|---:|
| medium_608 | hot80 | 9 | 8.10–194.89 | 63.39 | 12.696 | 39.447 | 26.751 |
| medium_519 | hot80 | 10 | 8.10–254.93 | 74.61 | 7.739 | 37.778 | 30.038 |
| medium_675 | hot80 | 10 | 8.10–194.89 | 79.04 | 14.087 | 57.233 | 43.146 |
| medium_585 | room25 | 7 | 6.87–300.00 | 67.17 | 14.522 | 36.262 | 21.740 |
| medium_543 | room25 | 10 | 7.04–300.00 | 96.00 | 47.391 | 62.670 | 15.279 |
| medium_914 | room25 | 11 | 10.04–294.89 | 43.43 | 0.826 | 18.777 | 17.951 |
| light_652 | hot80 | 6 | 39.96–296.13 | 30.05 | 0.000 | 30.667 | 30.667 |
| light_626 | hot80 | 6 | 39.96–296.13 | 38.41 | 0.000 | 37.349 | 37.349 |
| light_462 | hot80 | 2 | 9.86–20.07 | 136.15 | 35.366 | 92.021 | 56.655 |
| light_665 | hot80 | 4 | 29.93–235.92 | 91.99 | 5.836 | 40.475 | 34.638 |
| light_653 | hot80 | 5 | 9.86–296.13 | 68.73 | 18.118 | 35.841 | 17.723 |
| light_547 | hot80 | 6 | 9.86–59.86 | 80.49 | 10.932 | 52.334 | 41.402 |
| light_472 | room25 | 4 | 13.03–300.00 | 77.61 | 12.108 | 30.151 | 18.043 |
| light_589 | room25 | 6 | 20.07–119.89 | 69.90 | 0.000 | 21.524 | 21.524 |
| light_520 | room25 | 5 | 20.07–300.00 | 65.72 | 14.983 | 15.405 | 0.422 |
| light_568 | room25 | 7 | 13.03–300.00 | 38.41 | 0.871 | 8.648 | 7.777 |
| light_592 | room25 | 8 | 13.03–300.00 | 29.27 | 5.836 | 17.480 | 11.643 |

Earliest ordinate bounds are in[particles.json](particles.json). Descriptive 30 s
and 240 s requests are in[progress_summary.csv](progress_summary.csv): exact native
coordinates only are called direct; otherwise an in-range estimate is explicitly
conditional linear interpolation between the listed two supported markers. Gaps
remain gaps, and no extrapolation occurs. These estimates are never fit operands.
The source's [Table 2 CSV](../../../puckworks/data/hargarten2020/hargarten2020_swelling_progress.csv)
remains unchanged:83/82/71/59%at 30 s and109/111/101/108%at 240 s for medium hot/room,
light hot/room. It calls these averages but does not fully specify weighting and
reconciliation of trace clocks. No equality to the partial reconstructed mean,
or aggregate Mo comparison, is asserted.

## C. Shared finite-reference response

The tested family is`P_i(t)=H_c(t/R_i²)/H_c(T/R_i²)`. Each group has its own H,
nonnegative and nondecreasing with H(0)=0 and positive references. Different
finite-reference denominators are essential: ordinary normalized curve collapse
is not this test. Exact rational scaled times share variables when equal and stay
separate when merely near. No diffusivity, analytic law or intergroup identity is fit.

| Group | Particles / supported points | maxB_i / pp | Shared epsilon infimum / pp | Additional Delta / pp | Fixed graphical disposition |
|---|---:|---:|---:|---:|---|
| light_hot80 | 6 / 29 | 35.366 | [52.262, 52.268] | [16.896, 16.902] | CERTIFIED_INCOMPATIBILITY below lower bound; constructed upper witness |
| light_room25 | 5 / 30 | 14.983 | [17.111, 17.117] | [2.128, 2.135] | CERTIFIED_INCOMPATIBILITY below lower bound; constructed upper witness |
| medium_hot80 | 3 / 29 | 14.087 | [20.866, 20.873] | [6.779, 6.786] | CERTIFIED_INCOMPATIBILITY below lower bound; constructed upper witness |
| medium_room25 | 3 / 28 | 47.391 | [47.391, 47.392] | [0.000, 0.000] | CONSTRUCTED_COMPATIBLE_WITNESS at B |

All numbers concern the declared supported subset. Each infimum is exactly bounded
to≤0.01 pp. Delta subtracts the **maximum of the individual optima in that group**,
not a pooled tolerance imposed on other particles. Each subset B and epsilon is
a lower bound for its corresponding full-history quantity, but their difference
Delta is **not** a lower bound for the full-history incremental penalty: missing
points can increase the baseline and shared discrepancy by different amounts. Medium room's large543 µm
overshoot already dominates 47.39 pp; zero incremental penalty is weak compatibility
at that tolerance, not evidence for a common mechanism or a common true history.

Scale/positivity is exact: any finite collection of strictly positive reference
values can be rescaled so all are ≥1; conversely this convention ensures positivity.
No bound on the maximum h is imposed. Constraints become lower bound edges
`h_v≥a*h_u` with exact nonnegative rational a. Longest-product relaxation starting
from positive references produces either a rational feasible vector, a reachable
cycle whose exact product exceeds 1, or a path forcing a designated zero node positive.
The latter two are independently checkable infeasibility certificates. A negative
upper progress bound is incompatible with a positive reference. Unreachable
zero-growth segments remain admissible; the all-zero-denominator solution does not.
This avoids floating-point LP feasibility/strict-positivity ambiguity altogether.
Piecewise monotone extension between finite nodes constructs H on the needed domain.
No claim of smoothness or uniqueness follows.

[Certificates](certificates.json) retain complete fixed/outer graphs, exact upper
witnesses and lower infeasibility certificates. Nominal calibration is shared;
marker rectangles can be chosen simultaneously for the **declared fixed graphical
layer**. It does not resolve the known original-source figure/frame conflicts.
[Group tables](groups.csv) and [numerical results](RESULT.json) preserve this distinction.

The explicit sensitivity expands ordinates over±1 px shared axis-anchor possibilities
and removes order constraints not forced by marker-time and rounded diameter±0.5 µm
intervals. Independent endpoint choices relax shared calibration and radius/time
correlations. This is an outer set, **NONEMPTY_OUTER_FEASIBLE_SET_ONLY**, never a
jointly realizable source assignment. The outer epsilon brackets are:

- light_hot80: [52.002, 52.008]pp.
- light_room25: [16.852, 16.859]pp.
- medium_hot80: [20.604, 20.610]pp.
- medium_room25: [47.130, 47.131]pp.

These sensitivities are coordinate/rounding assumptions, not true 3-D radius or
experimental error bounds. Their feasible solutions prove only necessary-set
nonemptiness. They do not justify subtracting the fixed-coordinate baseline as an
uncertainty-corrected kinetic penalty. Near ties are omitted from forced order,
not falsely merged or assigned independently realizable times.

## D. Unchanged Mo parameterization

The producer calls current `swelling_volume_ratio` with D_W=1.25e−10m²/s, C_M=.1 and
eachindividual d_proj/2. No 194 µm representative substitution, offset, amplitude,
temperature factor or parameter fit. It maps native volume using
`(cuberoot(V(t))−1)/(cuberoot(V(1200))−1)`, preserving full internal precision.
Unique sorted solver coordinates are restored to requested order/repeats. Solver
success, finite outputs, concentration range, monotonicity and the discrete
quadrature volume ceiling are checked. Prediction/residual rows are in
[mo_predictions.csv](mo_predictions.csv), per-particle discrepancies in
[mo_comparison.csv](mo_comparison.csv), and actual numerical checks in
[mo_numerics.json](mo_numerics.json).

On the retained positive-time support, the maximum 60→120cell change is
0.133435pp;
120→240 is0.033375pp. Tightening 240-cell BDF tolerances from
rtol 1e−7 / atol 1e−9 to1e−9/1e−11 changes at most0.00000854pp.
These are observed numerical sensitivities, **not a certified continuum error bound**.
All per-particle Mo increments overB are positive (minimumabout 0.422 pp).
Group worst residuals are92.021pp(lighthot462),57.233pp(mediumhot675),
30.151pp(lightroom472),62.670pp(mediumroom543); individual worse cases stay visible.

The native implementation's surface Dirichlet endpoint gets finite trapezoidal
weight, so raw P(0) is not zero: for 608 µm, about 2.714/1.327/0.655 pp at 60/120/240 cells.
The equilibrium integral also slightly exceeds the physical volume ceiling1/(1−C_M)
by its discrete quadrature bias. We retain these failures explicitly, check the
known discrete ceiling`(1+1/(2N²))/(1−C_M)`, and do not silently renormalize V(0),
clip volume, alterproduction physics or call endpoint qualification complete.
P(T)=1 is exact by the observation formula. No near-zero universal accuracy claim.

Any mismatch concerns this frozen parameterization and observation map. Hargarten
was part ofMo's diffusivity calibration lineage, so this is not independent external
validation or rejection of every diffusion model.

## E. Claim classification and evidence

- **Certified:** independent supported-subsetB_i; exact fixed-graph feasibility
  brackets and positive added penalties in three groups; nonnegative Delta; all rational
  certificates and witnesses under the declared coordinate/reading contracts.
- **Constructed, conditional:** finiteH witnesses at reported upper tolerances
  under one nominal panel calibration; supported-subset monotone witnesses.
- **Necessary-only:** outer calibration/time/diameter relaxation, and optional
  Figure 7 interval conversions sharing a reference. Feasibleouter sets are not
  jointly consistent source measurements.
- **Unresolved/insufficient:** obscured markers, full particle histories (especially
  light462), Figure 7/Figure 10 and methods/graphical-clock consistency, quantitative
  measurement error, true 3-D geometry, hot temperature histories, raw Mo initial
  endpoint/continuum accuracy, aggregate weighting and physical mechanism adequacy.

Bubbles, image processing and detached fragments are source-documented limitations;
no invented distribution or error bar is assigned. Imaging-plane effects are not
quantified by this source. A nonsignificant size regression does not establish no
kinetic size effect. Prior wet-PSD uniform-dilation exclusion does not exclude
native Mo's size-dependent swelling. No hydraulic/permeability or full espresso
prediction, production adoption or automatic successor follows.

[Figure 10 comparison](comparison.svg) shows reading bounds, monotone/shared witnesses
and Mo. Connecting lines are explicitly synthetic guides. [Figure 7 native plot](figure7_native.svg)
keeps original growth separately with gaps. [Review](REVIEW.md), [verification](VERIFICATION.md),
[plan](PLAN.md), [retained coordinates](../../../puckworks/data/hargarten2020/swelling_kinetics_001/coordinates.csv)
and [independent checker](review_check.py) make the bounded finding auditable.

Offline reproduction (Python ≥3.10 with repository dev/figure dependencies):

```sh
python -m puckworks.analysis.hargarten2020_swelling_kinetics --output /tmp/hargarten-kinetics-replay --plot
python docs/analysis/sci_md_hargarten_swelling_kinetics_001/review_check.py --output /tmp/hargarten-kinetics-replay
python -m pytest -q tests/test_hargarten2020_swelling_kinetics.py
```

No PDF, original artwork or network is required after retaining the authenticated
readings. Final exact base/head, hosted CI and OPEN/DRAFT/UNMERGED lifecycle are
recorded in the draft PR handoff; auto-merge remains disabled.
