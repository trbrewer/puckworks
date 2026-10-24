# SCI-MD-MO-WET-CT-PROFILES-001 — frozen retrospective plan

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

## Selection, scope and starting state

Question: which lower-versus-upper spatial contrasts are resolved by Mo's
published segmented-image profiles, and what do they establish about geometric
porosity? This is an analysis module, with no runtime model, physical fitting,
permeability conversion, solver run, production change or successor.

- New information: numerical spatial summaries absent from the current Mo intake.
- Resolved orderings: retain explicit, source-conditioned graphical constraints
  for a future comparison with a separately qualified observation operator.
- Contrary orderings: reject an overbroad displayed-signal claim on that support.
- Unresolved signs: withhold the ordering; overlap is not equality.
- Unsupported requests: identify the exact missing display support.
- Grinder-to-cup relevance: qualify structural evidence before using it to
  constrain an evolving-bed model. No result here establishes a mechanism.

Actual accepted Puckworks main: `13c750c7d08d1fc868e24ad500dced5fb34127e4`,
including merged Perticarini PR #360. Actual EWP remote main:
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`. Both match the reviewed heads;
no relevant intervening delta. The existing Puckworks worktree inspected first
was at `7bc013d4e00e416fb747d4c37e3cc514dc2e098d`; the new isolated branch
starts at accepted main. The EWP reference checkout is at
`7c025527da7e07982428d4c78a3e79bfa29a76ac`; accepted files were read with
`git show f44c33d:<path>`, without changing that checkout or its lock.

Read: AGENTS.md, CLAUDE.md, onboarding, development guide, available-data-first
policy, data guide, manifest/register, Mo card/provenance, minimum-necessary
governance; EWP's external-data use map and three-test task-selection guidance.
Scoped repository and live issue/PR searches found no equivalent Figure 14/16
intake. SCI-MD-MO-TRANSFER-001 / #273 / #274 concern `mo2023_2`, not this source.
The seven configured external `mo2023` files were resolved, rehashed against the
dated snapshot and read: **FILES_INSPECTED** (six CSVs and provenance; all match).
They contain granulometry, SPH sample tables and Figure 8a. Other families are
CATALOG_ONLY. This is not a new census or a corpus-exhaustion finding.

## Source and exposure freeze

Controlling text: Mo et al., Scientific Reports 13, 16374, published 29 September
2023, DOI `10.1038/s41598-023-42380-y`. Original lineage: arXiv v1 submitted
6 May 2023; v2 posted 8 October 2023, after the journal article. Method wording
is version-specific. All three supplied PDF SHA-256 identities were retrieved
and verified. The seven-page final supplement was inspected; it contains SPH
methods/parameters and enlarged E/H/M/F sections, not numerical 1/24-hour profiles.

Final PDF pages 12/13, Figures 14/16, correspond to arXiv v2 pages 14/15.
Four panels: 14a medium/pre, 14b medium/three-days-post; 16a dark/pre,
16b dark/immediate-post. Six printed radii in each: 0.92, 2.77, 4.61, 6.45,
8.30, 10.14 mm. These are 24 annular-region profiles from two capsule histories,
not 24 extractions or point measurements. No radial volume weights are inferred.
Figure 6 is context, not a paired baseline. Full paths, legends, ticks, clipping
and rendered panels have been inspected before this freeze. Patterns including
the delayed central rise are already exposed. This is neither prospective nor
blinded. No contrasts have yet been computed.

Canonical ordinate: `published_segmented_signal`; native epsilon / source
"porosity" are separate metadata. Spatial y increases bottom/outlet to top/inlet
although plotted horizontally. Vertices are rendering geometry, not CT samples.
Dry threshold matches reference porosity 0.17; wet threshold is manually selected
between histogram peaks. Wet imaging cannot adequately separate liquid and solid.
That observation limitation is distinct from graphical-reading uncertainty.

## Estimands and fixed support

For B=[u,v], M_B(s)=integral(s(y),u,v)/(v-u), using the entire declared width.
Freeze lower interior [12,14] mm, primary upper interior [17,19] mm,
later/top sensitivity [19,21] mm. The primary band was chosen for display support;
retain the late band and full profiles to preserve the central exception. No new
windows, subgroup search, smoothing or sign-driven calibration adjustment.

Exactly 48 dependent requests:

1. A=M_[12,14]-M_[17,19]: 12 post requests, primary, in two separate six-radius
   groups; 12 pre requests, descriptive context.
2. DeltaA=A_post-A_pre: 12 same-history/radius display-coordinate differences.
3. A_late=M_[12,14]-M_[19,21]: 12 post sensitivity requests.

Band means are diagnostics, not extra requests. DeltaA compares printed windows;
no material registration or unchanged observation operator is established.
Roast, capsule and delay are confounded; keep histories separate.

Retain path/segment/subpath topology and orientation. All inspected profile
operators are straight lines; integrate exact piecewise-linear polynomials,
including partial segments. Nonlinear operators must fail extraction, not be
replaced by endpoint chords. Finite source-membership alternatives qualify only
if every alternative completely supports every requested band. The six distinct
stroke colors and legend order authenticate membership; crossings alone do not
erase it. Never join disjoint paths or bridge opaque/clipped intervals.

The delayed central trace has an opaque legend, a PDF clipping rectangle and
three explicit subpath gaps beyond the top clipping. Preserve hidden coordinates
only as labelled audit rows. All means/bounds exclude hidden evidence. Other
legend/axis intersections are also masked geometrically, not guessed by radius.
Use the full legend bounding rectangle including border as a conservative mask
(its rounded corners do not license reading through it).

## Graphical contract and numerical enclosure

Nominal shared affine calibration per panel: y=alpha*x+beta,
s=gamma*z+delta, z=-PDF_page_y, alpha,gamma>0. Printed x ticks 12 and 22 mm
and ordinate ticks 0 and 0.40 anchor it. Retain all intermediate ticks as a
calibration check. PDF coordinates are exact rendering inputs as represented by
the parser; the following are declared graphical allowances, not measurement SDs.

Each endpoint tick-center anchor may move independently by half its actual stroke
width plus 0.003 PDF pt (allowing production/tick-rounding residuals); the same
resulting affine map applies to every band, vertex and radius in that panel.
No cross-panel calibration is shared. Parameterize inverse horizontal calibration
as x(y)=a+(b-a)*(y-12)/10 with a,b in those closed anchor boxes. Ordinate scale
gamma=0.4/(z_0.4-z_0) ranges over its positive anchor interval. Delta cancels
exactly in A, A_late and DeltaA. Positive gamma cannot reverse a fixed A sign;
different panels' scales affect DeltaA.

Local reading contract: a square containing the physical stroke cross-section,
horizontal half-width h_x=stroke_width/2 and vertical h_z=stroke_width/2, with
0.003 pt source-rounding allowance added to each. A locally read line may sample
the nominal continuous segment representation within h_x and have bounded
piecewise-linear vertex ordinate departures |e_i|<=h_z. This deliberately
conservative deterministic box is not independence of experimental samples.
The square is an outer relaxation of the ink, not an attainable reconstruction.
Membership is fixed by source strokes/legend even where ink overlaps.

At fixed calibration and no local displacement, retain the source coefficient
vector a_i from exact segment integration; combine reused quantities before
sum |a_i|h_i. Identical band terms cancel first. For moving calibration/local
horizontal readings, nonnegative interpolation weights sum to each band's
coefficient; hence the uniform-height box radius is bounded by h_z times the
sum of absolute retained band coefficients. No fixed nominal weight assumption
is used for horizontal propagation. Include the Jacobian alpha when integrating
in native coordinates: M=delta+gamma*alpha/(v-u)*integral f(x) dx.

Certify bounds by interval subdivision: a fixed 4x4 cover of the continuous a,b
box, and 256 equal y cells per band. For each calibration box and y cell,
enclose x(y) by its corner extrema, expand by h_x, and enclose the PL ordinate
by both endpoints and every enclosed source vertex. These are exact extrema
of a line-segment representation, not grid-point estimates of extrema.
Integrate cell range times its full y width and combine signed band terms;
enclose all parameter boxes, then multiply by the positive gamma interval.
This is an outer integral enclosure; refinement budget is fixed before signs.
Separately attained endpoints are never a joint reconstructed profile.

Check display support on the union of inverse bands over the ENTIRE calibration
box, expanded by h_x and h_z against opaque/clipped geometry. No calibration is
discarded to obtain support. Failure means UNSUPPORTED, with null qualified
bounds; retain a nominal estimate only if nominal centerline support is complete.
Bounds include a conservative 1e-7 signal arithmetic guard per within-panel
contrast (2e-7 inherited by DeltaA), with outward endpoint arithmetic/rounding.
Document the operation/coordinate/denominator bounds supporting that guard.

## Classification and physical ceiling

Keep coverage, membership and numerical qualification separate. Complete,
numerically qualified enclosures alone receive POSITIVE if lower>0, NEGATIVE
if upper<0, otherwise SIGN_UNRESOLVED, including zero touch. Missing support is
UNSUPPORTED, never an invented zero or overlap interval. For A/A_late the labels
are LOWER_INTERIOR_HIGHER / UPPER_INTERIOR_HIGHER; for DeltaA they are
CONTRAST_INCREASED / CONTRAST_DECREASED. Include all requests and adverse signs.
All-six statements require all six radii; neither monotonicity, whole-section
coverage nor population behavior follows. No p-values, bootstrap or sqrt(n).

Verify exactly the constructed observation-map witness g=phi*(1-S) at
g=(0.12,0.08): phi=(0.24,0.16),S=(1/2,1/2);
phi=(0.20,0.20),S=(2/5,3/5); phi=(0.16,0.24),S=(1/4,2/3).
Its porosity contrasts are +0.08,0,-0.08. This is not a fitted scanner model or
a claim that Mo's signal is gas volume. It establishes nonidentification even
under that favorable idealization. Numerical targets are displayed spatial
contrasts and differences of those contrasts, not geometric porosity or a
physical mechanism. Resolved signal signs neither establish nor exclude fines
migration, erosion, swelling or consolidation.

## Delivery and verification

Use stable dataset `mo2023/fig14_fig16_segmented_profiles`; preserve old IDs,
strengths, results and units caveat. Correct only directly affected Mo claims and
Protocol 4/dependent decision wording. Greater deposited solid occupancy within
a common bulk volume means less geometric void; it is not bottom-high porosity.
Regenerate discovery through existing producers, with dated census unchanged.

Commit canonical segments/metadata, all 48 CSV/JSON requests, supporting means,
result/summary, compact licensed crops, masks, geometry-comparison receipt,
four-panel/full-profile figure plus all-request summary and VIZ_SPEC. Offline
generation has no PDF/network requirement; a separate pinned parser command
extracts authenticated PDFs. Keep large raw PDFs external. Focused tests cover
the requested analytical/support/sign/identity risks and offline determinism;
reuse discovery tests and applicable ordinary checks in fresh final processes.
Obtain one independent substantive review of sources, masks/membership, bounds,
claims, protocol corrections and rendered figure; correct material findings
without relaxing allowances. Inspect live required checks. Leave one Puckworks
PR OPEN / DRAFT / UNMERGED, auto-merge disabled; EWP unchanged. Stop here.
