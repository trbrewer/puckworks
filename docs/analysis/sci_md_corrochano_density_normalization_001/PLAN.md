# SCI-MD-CORROCHANO-DENSITY-NORMALIZATION-001

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. One bounded research analysis, no component,
constitutive law, empirical calibration campaign or production adoption.

Actual base, refreshed 2026-10-23: Puckworks main
`81cfcebebf0625992fcbb60b93a9c6e965838b36`, merging #353, accepted head
`dd5375985a18ccf2af25bd3001d0f72ea71e1a38`, predecessor base / merged #352
`e21631e741ff739aaf4a6b9c58e5e11b161436cc`. No intervening main changes or existing
normalization implementation/PR found. EWP main read-only:
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Active ruleset 19053322 requires
quick (3.10), quick (3.12), verify-generated, paper3-scope-strict, all-scope-strict.

## Evidence and exposure

Reuse only `romancorrochano2017/fig6_2_dry_compaction`. Inspect retained
coordinates.csv, paths.json, contract.json, holdings_checked.json, PROVENANCE.md,
and both predecessor producers/tests, bundles and accepted source reconciliation.
Authenticate inputs against predecessor hashes; bind all retained source files,
both producers/tests and both historical bundles byte-for-byte in the contract.
No fresh PDF authentication, native-record search or external-holdings exhaustion
claim. Graphical B1–E3 IDs are not authenticated instrument-run IDs. Keep 76 unique
curve chunks, repeated-paint deduplication, four excluded legends, 64 approved tiny
joins and continuous paths beneath dash styling. No source artwork redistribution.

The primary interval 50→250 N and diagnostic B3 versus D2 were selected after
exploration. Proposal review also inspected all 990 determinants and the complete
72-reading affine witness. Exposed diagnostics: one pure-scaling separation,
B3−D2 at 50→250 N, approximately [-4997.520251613956,-244.350799199935] pt²;
D2−B3 conservative ratio margin approximately 0.002700564925783476; affine levels
approximately [0,0.242197557697501,0.522385383870927,0.713961790585087,
0.868671028138561,1]; no scaling separation on 25→250 N. These are exposure records,
not computational inputs, accepted repository results or regression-test oracles.
This plan is a fixed implementation contract, not a prospective holdout or statistical
preregistration. Reconstruct from original decimals; diagnose differences without tuning.

## Fixed sets and inherited reading contract

Samples B1,B2,B3,C1,C2,C3,D1,D2,D3,E1,E2,E3; forces 25,50,100,150,200,250 N;
all 15 unordered force intervals; pairs first minus second in canonical sample order,
including within-grind. A reports 72 coordinate readings, 180 within-sample ratios,
990 sample-pair contrasts, 60 grind envelopes and 90 cross-grind comparisons.

Use exact rational arithmetic from decimal strings for classifications and identities;
authoritative serialization is rational strings, displays round outward. Reconstruct
raw operands through recorded transforms, chunk order, deduplication and approved joins.
Set z=-y. For A use full inherited force strips from independently perturbed ±1 pt
shared axis anchors plus full ±1 pt horizontal trace allowance. Require entire-strip
support in the actual segment-projection union. Clip every segment; retain every
intersection, interior extremum, branch and ambiguity. Expand z by full ±1 pt vertical
trace allowance (already includes effective stroke). Maintain actual component unions
separately from hulls. Hulls are exclusion enclosures, not existence certificates.
No smoothing, extrapolation, unrecorded bridges, branch removal or extra stroke guard.
Replay all 72 accepted density marginals/statuses; predecessor tables are verification
only. Retain unsupported, incomplete, ambiguous and arithmetic-failure rows.

## A: pure positive scaling

Test rho_jk=s_j*h_k, s_j>0. Write rho=alpha+beta*z=beta*(z+tau).
For density anchors r0=300,r1=650 at downward p0,p1 and independent e0,e1∈[-1,1],
tau=[r1*(p0+e0)-r0*(p1+e1)]/(r1-r0). Enumerate anchor corners for exact tau bounds.
Show beta=(r1-r0)/(p0+e0-p1-e1)>0 throughout; never discard the physical intercept.
Use ONE shared tau in C=(z_ib+tau)*(z_ja+tau)-(z_jb+tau)*(z_ia+tau).
Expand C=z_ib*z_ja-z_jb*z_ia+tau*(z_ib+z_ja-z_jb-z_ia); tau² cancels.
This is separately affine in four endpoint coordinates and tau, so iteratively moving
each coordinate to an endpoint proves that all extrema over the relaxed rectangle occur
among 32 corners. Physical cross-product=beta²*C with positive beta²; beta/tau need
not be independent. Endpoint boxes relax shared force/path dependencies conservatively.

Require all z+tau denominator enclosures strictly positive. C.lower>0 or C.upper<0
means STRICTLY_SEPARATED; contact/zero-containing means NOT_EXCLUDED_BY_THIS_COMPARISON;
missing support, invalid positivity and arithmetic failures retain explicit reasons.
Any qualified separation excludes all-twelve A despite unrelated incomplete rows.
Otherwise complete declared comparisons mean NOT_EXCLUDED_BY_THE_DECLARED_COMPARISONS;
incomplete coverage means UNRESOLVED_DUE_TO_SUPPORT_OR_READING_LIMITS. Exclusion label:
EXCLUDED_BY_SAMPLE_RATIO_CONTRAST. Report primary and overall separately; non-exclusion
is not joint feasibility.

Ratio R=(z_b+tau)/(z_a+tau): for fixed tau, it increases with numerator z_b and
its derivative in denominator z_a has constant sign; for fixed endpoints its tau
derivative is (z_a-z_b)/(z_a+tau)^2, again constant sign. Thus corner extrema suffice
with positive denominators. Keep the same tau at both endpoints. Direct pair ratio
contrast=C/[(z_ia+tau)*(z_ja+tau)]; bound the positive denominator conservatively and
divide using all four signed endpoint quotients. Determinants are authoritative;
subtracting marginal ratio intervals is only a displayed diagnostic.
A complete grind envelope needs all three members. Whole-grind ordering requires all
nine cross-sample contrasts strict in the same direction. Keep direct classification
separate from marginal envelope overlap; one separated pair does not order grinds.

## B: fixed simultaneous affine witness

Test rho_jk=b_j+s_j*h_k, s_j>0. Fix BOTH axes at original nominal anchors, keeping
full horizontal/vertical ±1 pt TRACE allowances. At each force clip all admitted
segments against nominal x±1, project to z and expand ±1; retain components and hulls.
Set c_j=midpoint of 25 N hull; a_j=midpoint of 250 N hull minus c_j; require a_j>0.
Set h_25=0,h_250=1 (this gauge applies only to B). For each intermediate force,
intersect all twelve [(L_jk-c_j)/a_j,(U_jk-c_j)/a_j], require nonempty and take its
midpoint ONCE as the common h_k. Require strictly increasing h. Select z*=c_j+a_j*h_k.

For every point, scan segments in retained path order; select the FIRST with nonempty
t∈[0,1] satisfying |x_source-x_nominal|≤1 AND |z_source-z*|≤1; choose midpoint of that
feasible t interval. Handle reversed/constant coordinates exactly. Preserve stable
sample/grind/force/chunk/segment references, original versus approved join, ordered
position, exact endpoints/t/source x,z, nominal x, horizontal/vertical displacements,
z*, density, actual component/support references and shared parameter/level references.
Verify membership, both allowances, 0≤t≤1, component union (reject hull gaps), and
strict progression of ordered segment/parameter positions with increasing force.
This is graphical path order, not experimental chronology.

One nominal density calibration gives b_j=alpha+beta*c_j, s_j=beta*a_j. Verify all
72 identities rho*=alpha+beta*z*=b_j+s_j*h_k, positive s_j and densities; exactly twelve
parameter pairs, six common levels, four intersections, one common calibration.
Forbid per-force parameters/per-sample h. A separate checker independently reconstructs
raw source points, calibrations, hulls, midpoint construction and identities; it must
not call producer classification/success or trust producer bounds/success flags.
Any failed support, positivity, intersection, membership, ordering or certificate check:
NO_CERTIFICATE_FOUND_BY_DECLARED_CONSTRUCTION with exact row/reason; arithmetic failures
remain explicit. Success: FEASIBLE_AT_DECLARED_FORCE_LEVELS_BY_EXPLICIT_WITNESS.
No optimizer or replacement construction on failure; failure does not exclude B.

## Interpretation and completion

B includes both pure scaling and #353's offset-only family; exclusion of restricted
families does not exclude their combination. Under fixed sample mass, V_b/V_a=rho_a/rho_b;
constant area also gives relative height. Equal force is not authenticated equal stress;
no invented unloaded density. General strain histories, effective stresses and changing
mass/area remain outside this bridge. b_j is selected density at 25 N; s_j selected
25-to-250 N increase, not intrinsic parameters, unloaded density or unique mechanisms.
Finite compatibility does not establish identical actual material shapes, a continuous
law, constitutive validation or adoption. Preserve #352/#353 and their limits: separate
exclusions do not exclude unrestricted simultaneous force/density translations; inverse
connections require a common single-valued branch. Graphical displacements are admissible
reading choices, not instrument errors, probabilistic errors or measured preparation.
Instrument calibration/zero, compliance, initial states, preparation, population,
significance, independent replication, wet-bed/permeability/causality and EWP validation
remain unestablished. No 1320-comparison screen or alignment/calibration optimizer.

Commit plan/contract before formal production. Deliver exact tables, B witness/certificates,
RESULT.json/md, original local-VizSpec comparison (marginal A intervals, separate direct
contrast, six B points without continuous line/confidence bands), independent checker,
one independent scientific review, offline reproduction and normal checks. Update only
affected curated owners/projections; preserve unrelated manifest bytes and append-only
Insight IDs. Keep EWP, Smrke S1, defaults, equations, pins, source rights and campaign
unchanged. One OPEN/DRAFT/UNMERGED PR, auto-merge disabled, no successor.
