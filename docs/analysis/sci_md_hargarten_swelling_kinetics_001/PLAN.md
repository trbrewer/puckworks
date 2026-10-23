# SCI-MD-HARGARTEN-SWELLING-KINETICS-001

Frozen question: how much discrepancy do individual monotone finite-reference
histories require, what additional discrepancy does one radius-squared response
per source condition require, and how does unchanged Mo compare?

G1 / SOURCE_INTERNAL / RETROSPECTIVE / TARGET_EXPOSED / NONSCORING /
RESEARCH_ONLY / NO_GOVERNING_PHYSICS_CHANGE.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No fitted parameters or physical acceptance
threshold. This is an owner-authorized retrospective task, not protected scoring.

Remote main refreshed 2026-10-23: Puckworks
35cc43ae82909b4936e0d15edcc31e541f0c1283, EWP
f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516. Both match supplied references;
#355 is merged. EWP read-only; production physics unchanged.
Instructions read: AGENTS/CLAUDE/onboarding, current development guide at
`docs/research/ESPRESSO_DEVELOPMENT_GUIDE.md`, data guide/register, minimum
necessary governance, source cards, wet-PSD predecessor and its review/checker,
and EWP SCI-MD-002B. Preserve their campaign identity and claim ceilings.

Source: Hargarten, Kuhn, Briesen (2020), DOI10.1002/jsfa.10440, published TUM copy
https://mediatum.ub.tum.de/doc/1580140/document.pdf, SHA256
4a41545954e6748a33ec1d956fd690bea58aba9c2e38955dfbb3ae9f5bffbfb0.
Copyright2020 The Authors, CC BY-NC. No original artwork committed.
Figure7 native raster1016x1550, Figure10 native raster1018x1522.
Same17 particles, four independent roast/protocol groups; no independent replicates.
Figure7 extends1200s; Figure10 extends300s. Eq4 referenceT=1200s.
Microscopy hot is approximately80°C inside the cell, cooling reservoir to60°C;
90°C starting temperature describes separate PSD preparation, not the cell.

Read every separable native marker; retain overlapping/occluded clusters explicitly
as unsupported. Gray levels and circle/triangle shape authenticate trace identity.
Native component bounding-box centers are proposed readings, visually checked.
±3px center allowance, ±1px shared axis anchors; these are graphical allowances,
not measurement confidence intervals. Triangle centers are bounding-box centers.
Native times remain rational pixel mappings, never snapped to the methods grid.
Zero markers are dry-state definitions; no measured1200 point invented inFigure10.
Figure7 medium final circles are visibly near1155s; light final circles are near1196s and clipped/overlapping. Neither silently supplies an exact1200 reference.
Source transformation contradictions stay separate; Figure10 is the primary
normalized graphical layer, Figure7 is retained native growth and consistency
context. No pooled Fig7+10 residual. No clipped negative or>100% observations.

Metric: minimum maximum distance to fraction-valued graphical reading intervals;
report percentage points. Independent histories nondecreasing withp(0)=0,p(T)=1.
Boundedness[0,1] follows from these endpoints on[0,T]; this is a hypothesized true
response, not a restriction on noisy reported readings. Exact rational extrema
of endpoint violations and half ordered-interval gaps giveB_i and witnesses.
Missing support yields partial-coverage bounds, never a full-history verdict.

Shared familyP_i(t)=H(t/R_i²)/H(T/R_i²),H>=0 nondecreasing,H(0)=0,
R=d_proj/2 in metres (equivalent-sphere assumption). Scaled times are exact
rational numbers. No merging of near ties. Strict positive references are
handled by setting all referenceh>=1: every finite positive-reference solution
can be scaled to this convention, so no family-changing arbitrary cutoff.
At fixed rationalepsilon, inequalities become nonnegative multiplicative lower
bound edges. Exact longest-product relaxation either constructs a rational
witness or finds a reachable product>1 cycle/forced-zero contradiction.
Bisection brackets epsilon to<=0.01pp; retain exact certificates at bracket ends.
ReportDelta=epsilon-maxB with outward bounds. No ordinary unnormalized collapse.

Primary fixed coordinates use shared nominal calibration and±3px marker bounds.
Sensitivity expands ordinates over shared±1px calibration extremes and removes
scaled-order relations not forced by time/radius intervals (diameter rounding
±0.5µm only, not authenticated radius error). This is an outer relaxation,
necessary-only, never a simultaneously realized calibration/time/radius witness.
No incompatibility is a physical rejection without measurement-error authority.

Mo: call existing swelling_volume_ratio withD_W=1.25e-10,C_M=.1, individuald/2;
unique-sort exact source times for solver then restore ordering/repeats.
P=(cuberoot(V(t))-1)/(cuberoot(V(T))-1). No fitting, offsets or amplitude changes.
Check60/120 cells and240 if needed, plus tightened integration tolerances through
an analysis-only monitored solver call. Preserve native initial/quadrature defects
if found; no silent physics or numerical correction. Mesh/tolerance differences
are observed sensitivity, never universal error certificates. Table2 remains
separate; no forced agreement with a reconstructed average.

Deliver deterministic offline producer, raw readings, baseline/shared/Mo tables,
witnesses/certificates, plots, source record, one independent source/scientific
review and separately implemented offline verification, focused and ordinary
checks, complete commit and OPEN/DRAFT/UNMERGED PR with auto-merge disabled.
