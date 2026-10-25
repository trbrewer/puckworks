# SCI-MD-FOSTER-RADIAL-FRONT-001 — frozen reading and analysis plan

Frozen before new numerical interface readings/results, 2026-10-25 UTC
(local task date 2026-10-24). G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY /
RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. The figures and primary scans were inspected
before selection. This is an operational freeze, not prospective selection,
target blindness, protected scoring or independent physical validation.

Accepted Puckworks base: `236853feb4871dd57d0a6c1a269588db1a88e784`.
Remote EWP main: `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.
EWP dependency authority stays `fc61c4670ec7bf801e40bb391aab16048b8da26b`.
Neither main advanced from the reviewed references. Isolated Puckworks branch;
EWP is read-only. One draft PR; no merge, auto-merge, successor, physics adoption,
fit, execution in EWP, parameter/default/lock change or new laboratory work.

## Cohort, observable and source roles

Exactly 90 slots: ten annuli 0.0<r<0.1 through 0.9<r<1.0, displayed midpoints
0.05 through 0.95; printed scan labels 0–8 seconds. All ten at t=3,4,5 are the
fixed 30 primary slots; all 60 others are context, including rule zeros and
plateau values. No dropped difficult shell or substituted primary scan.
Observable: `published_fitted_infiltration_interface`, native fractional bed
depth, positive downward. Preserve values/extents outside [0,1]. Equal shell
widths are not equal areas; no area mean, wet volume or independent brew sample.
The one-second reconstruction duration is separate from graphical uncertainty;
no exact exposure-window convention, model t_shift, Figure 11 clock conversion,
time interpolation, speed or subsecond arrival inference.

Figure 9 is primary (native JPEG 1447×1070, SHA-256
`b626e8e851c67daac56452e8b57d8021bcd4b2819be4b9e54fe007b0f53ca613`).
Figure 8 is a duplicate depiction (native PNG 1447×1069, SHA-256
`a123b23236306844a0b480b1001302e3d621a01c3cc20324176902e76d2282b5`).
Methods II C and Figure 7 authenticate shell absorption-fit construction.
Figure 7's time text is cropped: map its nine colors by readable Figure 6
absorption legend and Figure 9 time legend, in order blue/orange/green/red/
purple/brown/pink/gray/olive = t=0/1/2/3/4/5/6/7/8.
Figure 8 colors instead encode shells; its negative headspace branch is not s.

Eligibility is assigned independently of the numerical result: authenticated
fit, authenticated source-rule zero, unresolved fit-versus-rule, or unsupported.
Use the stated scaled-absorption threshold 0.2 and visible Figure 7 profiles/fit
lines with the authenticated color map; a zero marker alone is insufficient.
Mixed/rule scans do not become ten-fitted-center results. Each slot retains
eligibility evidence and independent center/lower/upper support.

The bars are `published_front_position_extents`. Width parameters are discussed
as uncertainty, but no confidence level or unambiguous Figure 9 multiplier is
established. No SD/SEM/CI, repeatability or deterministic physical-bound label.
Figure 7 absorption-mean SEM is distinct. Preserve printed Equation (1)'s z2/z3
inconsistency relative to prose; no sigmoid refit or repair.

## Native pixel reading and support contract

Origin is native upper-left, x right and p=y down, integer coordinates identify
pixel centers. Extraction recovers embedded rasters, not vectors. Viewing crops
or enlargements add no precision. Each reading records nominal x/y and enclosure,
image/calibration ID, status, reason, discrete alternatives and duplicate links.
Independent endpoint reads are mandatory: no hidden cap from symmetry, w3,
connecting line, neighbor, smoothness or desired answer.

Rasters show circular markers about 17–19 pixels across, caps about 15 pixels
wide with 2–3-pixel ordinate thickness, and antialiased/JPEG fringes about 1 pixel.
Read a center from the visible disk's opposing contours, not its vertical span
as uncertainty. Freeze ordinate allowances: clear disk center ±2 native pixels;
clear cap centerline ±2 pixels (half thickness plus localization/fringe); tick
centerline ±1.5 pixels. X identity allowance ±2 pixels for clear shells/scans.
Under translucent legend or partial overlapping marker, ±4 pixels is allowed
only when distinct visible contours/cap pixels identify that feature. Use a
larger *explicit union of discrete feature branches*, not a silent widened
single read, if identity is ambiguous. If neither identified contours nor
endpoint pixels survive, mark that feature unsupported/null. Do not decode
opaque text by presumed smoothness. Preserve local crops/overlay evidence,
including translucent pixels and the legend's foreground contamination.

One shared affine ordinate calibration per depiction, z=alpha*p+beta,
alpha>0, for every scan/shell. Figure 9 uses ticks z=0,0.2,...,1.0;
Figure 8 uses z=-1,-0.5,0,0.5,1. Each printed tick supplies the two inequalities
alpha*(p-1.5)+beta <= z <= alpha*(p+1.5)+beta. Nominal calibration and its
feasibility are retained. Graphical enclosures are constraints, not statistical
errors. All endpoints obey a<=b; authenticated readable center/bar relationships
obey a<=s<=b. Never impose symmetry. Pixel endpoints of bars and center
localization uncertainty are different quantities.

A Figure 8 center can be linked only after shell, scan and s identity are
visible/authenticated. Preserve both records under the same observation ID;
never count/average duplicates. Borrow/equate endpoints only if extent/endpoint
construction is authenticated too. Otherwise Figure 8 is corroboration-only,
with no endpoint transfer or numerical constraint. Any authenticated duplicate
conflict must be investigated and retained if unresolved; no favorable-display
selection or manufactured agreement. A corroboration-only approximate visual
match is explicitly not a second measurement or shared latent constraint.

## Estimands, certification and stopping

Use a different c_t at each scan; no trajectory fitting.

* E=min_c max_i |s_i-c|=(max s-min s)/2: all ten fit-eligible centers required.
  Nominal c is midpoint of extremes. Enclose the per-reading optimum, not the
  cost of fixing c before uncertainty. Positive certified lower E resolves
  graphical center variation; nominal E>0 alone does not. Retain extremal IDs
  and certified invariant identities when available.
* D=s_outer-s_inner: only two authenticated fitted end-shell centers required.
  Strict direction needs lower>0 or upper<0; cannot establish monotonicity.
* G=max a-min b: all twenty endpoints of ten fitted observations required,
  independently of center readability. G<=0 includes touching. Optionally
  H=max(0,G)/2, symmetric graphical enlargement, not physical error.

First establish a nonempty joint graphical set by a feasible nominal witness
for every retained branch/calibration/linkage/ordering constraint. No vacuous
universal result from an empty set. A failed qualification is distinct from
unsupported source reading. Bound inf and sup over the full continuous set.
Use rational interval arithmetic and outward decimal reporting. For a shared
figure, beta cancels exactly from E/D/G; retain positive scale uncertainty.
Conservative marginal bounds for mixed figures retain each separate offset and
scale; never independently cancel origins. Correlations may make conservative
bounds wide; no unsupported sharpness claim or random-sampling certificate.

For genuinely independent pixel center intervals, inf range is
max(0,max l-min u); sup range is max(0,max_{i!=j}(u_i-l_j)). Scale with the shared
positive alpha bounds. General differences and G may use pairwise interval
bounds; endpoint ordering can only tighten this conservative outer enclosure.
Do not maximize an epigraph variable constrained only from below. No general
uncertainty framework is needed; stop when sound conservative bounds settle
the represented decision. If tightening uses LP, a floating optimum/primal
residual alone is not a strict certificate.

G classifications: lower>0 EXCLUDED_FOR_ALL_ADMISSIBLE_READINGS; upper<=0
COMPATIBLE_FOR_EVERY_ADMISSIBLE_READING; otherwise GRAPHICALLY_UNRESOLVED.
Missing eligibility/support: UNSUPPORTED_COMPLETE_COHORT. Empty set or failed
qualification: QUALIFICATION_FAILURE. Quantifier is for every u, exists c(u),
not exists c for every u. Label nominal vs feasible vs any fixed witness.
A straddling enclosure proves neither sign feasible; both-sign claims require
separate checked witnesses. A supported subset may supply a certified partial
obstruction even when complete G is unsupported, never complete compatibility
or range upper bound. E/D/G support and qualification remain separate for all
nine scan records. Null stays null.

## Delivery and interpretation

Canonical ID `foster2025_2/fig8_fig9_radial_front`; offline CLI reads committed
inputs only. Separate optional source extraction; auditable pixel overlays,
source/rights notes, nine-profile comparison, deterministic CSV/JSON summary,
RESULT, focused tests, independent substantive review and verification receipt.
Register through existing MANIFEST/capability/family/Insight producers. Preserve
historical data/results/parameters/evidence strengths. Correct active dependent
claims about uniformity, binary sharpness and model-form validation separately.

Retain separated / compatible / unresolved results at the published extent.
No arbitrary 5%/10% acceptance tolerance. Three outcomes stay separate: center
representation cost, displayed-extent compatibility, unknown physical wetting.
A nonzero E alone does not reject a useful approximate 1D model. Compatibility
does not establish uniformity, equivalence or a realizable trajectory; exclusion
does not establish whole-model failure or EWP capability failure. No inference
of binary saturation, azimuthal uniformity, channeling, permeability, physical
porosity, first liquid arrival, extraction onset or cup improvement. Spatial
wetting motivates future extraction representation; no successor is authorized.
