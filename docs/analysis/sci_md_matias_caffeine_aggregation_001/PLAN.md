# SCI-MD-MATIAS-CAFFEINE-AGGREGATION-001 — bounded plan

Recorded 25 October 2026 before implementation assessment. Actual live base:
`91a8d92a027ffde1c15a841d694b2c8a51f2e637`; #364 is merged, accepted head
`a777ce74573c2f0a302f310b79d3b0966f76b249`. Repository/PR search found no
existing aggregation task. Isolated branch; preserve other work and EWP.

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING. Selected after exploratory
calculations on exposed data; no preregistration, outcome blindness, untouched
holdout or independent predictive validation. The owner's reviewed brief
specifies this bounded retrospective procedure, with no protected scoring.

Fixed input: directly read `puckworks/data/matias2023/observations.csv`, dataset
`matias2023/fig3_caffeine_fractions`. Reuse accepted #364 source/helper qualification.
Authenticate CSV SHA256 `6f2f8a426159de950a518768a11b326376ead1f2a1de91f8ca6f0c77d5f6cd0a`
and geometry `6f56f7a6548d38df0db12602b6528768fb8eecafb15ae61ba59ead0af935928e`.
No recovery, recalibration, corpus census, new observations or source artwork.
The underlying committed observations are inspected; external raw traces are
not inspected and the external collection is not claimed exhausted.

Operator: four extractions, ten consecutive nominal 5 mL windows; retain F01–F10
and x=i−1. Constant extraction-specific A>0,k>=0 integrate to B*q^n, 0<q<=1.
Fixed positive weights over the same extractions give a positive, nonincreasing,
log-convex aggregate. Optimize its necessary nonincreasing convex log shape,
a strictly larger family; never fit components or claim the converse.

Read exact rational log10(c/(1 mg/L)) strings: N=[z,z], G=[G_lower,G_upper],
P_outer=[L_minus,U_plus], P_inner=[L_plus,U_minus] only when valid. Retain accepted
recovered/covered/clipped support, all ten slots, and original coordinates across
gaps. N/G need centers; P needs endpoints. Absent/invalid support and empty inner
must remain distinct from positive discrepancy; subsets yield lower bounds only.

Metric: exact minimum maximum log-interval distance over nonincrease and convexity.
Use prefix upper minima (earliest tied source), lower hull (remove collinear middle
anchors), piecewise interpolation h, epsilon=max(0,max_i(l_i−h_i)/2), witness h+epsilon.
Retain every tied controlling certificate; weights use hull-anchor coordinates,
with prefix sources justified by monotonicity. Check all original intervals and
secant slopes exactly. An independent reader/checker must verify primal cost and
dual lower bound without calling the hull producer. Separately cross-check all
source layers and focused fixtures by the epigraph LP with sign-unbounded y.
Reuse the qualified directed multiplicative enclosure helper; floats are display only.

Retain eight original consecutive-triple diagnostics per layer and all ten
witness/support slots. Local non-exclusion is not simultaneous feasibility.
G/P rectangles relax shared graphical calibration. For every endpoint realization,
e_outer <= e_realized <= e_inner for the relaxed family; mixture e >= e_realized
>= e_outer. The inner relaxed cost is not a mixture upper bound. SE is descriptive,
not a confidence region; no adequacy threshold or amount-explained interpretation.

Deliver offline CLI, deterministic JSON/CSVs, exact checker/receipt, proofs,
semilog comparison and VizSpec, tests, source reuse/result/review/verification notes.
Test geometric/positive-mixture limits, necessary-only counterexample, local/global
fixture, invariances, provenance/ties/nonuniform grids, support and invalid inner.
One same-session independent-method mathematical review, not an external/human audit.
Update only current Matias capability descriptions, narrow guide/planning pointers
and affected existing projections. Preserve accepted scientific/source/code bytes.

Any exclusion is conditional on nominal equal windows, fixed weights and qualified
bands. Unequal-volume robustness, individual shots, covariance, physical mechanism,
time/mass mapping and shared 70 mg inventory are not established. Temperature was
uncontrolled; separate one-capsule Soxhlet context remains separate. Source-derived
artifacts retain Matias et al. CC BY 4.0 attribution; first-party code is MIT.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. One OPEN/DRAFT/UNMERGED PR, auto-merge disabled;
no production change, EWP write, merge or successor.
