# SCI-MD-CAMERON-PRESSURE-TAMP-001 plan

Recorded 2026-10-24 before production extraction and contrast calculation.
G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
This is not blinded, held out or prospectively preregistered: the figure,
apparent ordering and preliminary vector-structure observations were exposed.

Base: Puckworks main `72769feddee3fc38a4f716643bca9c567a595919` (PR #358).
Live EWP main is `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`; read-only.
Live refs, local branches, manifest/register/cards, analysis records, local Cameron
CSV holdings and GitHub issue/PR searches were checked. No overlapping S2 dataset
was identified. Figure 2 and Figure 5 are distinct existing datasets. The current
development guide already rejects an automatic pressure-label conversion.

## Bounded question and decisions

Recover 4 common nominal force groups × 2 native grind settings (1.3, 1.5) ×
2 native pressure labels (6, 9 bar): 16 plotted central summaries, not 16 shots.
Authenticate groups before joining, use F1–F4 in increasing source x order,
and use the same F1/F4 extrema for every series. Keep actual plotted x readings;
round nominal force settings are not assumed. Matching nominal groups does not
establish identical applied forces. Never interpolate missing observations.

For T(P,G,F), retain all 18 dependent contrasts:

- DP-G-F: T(9,G,F) − T(6,G,F), eight pressure contrasts.
- I-F: DP(1.3,F) − DP(1.5,F), four additive interactions (seconds).
- DF-P-G: T(P,G,F4) − T(P,G,F1), four endpoint tamp contrasts.
- J-G: DP(G,F4) − DP(G,F1), two endpoint changes in pressure contrast.

Primary questions are DP and I; DF and J are secondary. Intermediate force
observations remain context without an assumed linear or monotone response.
A supported contrast becomes a qualified endpoint relationship for a future
source-matched model. Unresolved contrasts remain bounds, not equality.

## Sources and reading rules

Authenticate the official standalone SI (8 pages; S2 PDF p7 / printed p6), SHA256
`37530ec8c450c6fe5b231a7d4e3b65347555454b366ed4730ec106a4fb56775f`, and author-hosted
main paper (19 pages), SHA256
`efd41bb44e2542fcee04498ebc61b5c84e337601a755156e9392d12fcc93d229`.
Both downloads match. URLs and page-level provenance accompany the data.
Restricted PDFs/renders stay outside Git; commit numerical records and a new plot.
Table S5 is model-scaled flux and supplies no independent observations here.

Prefer native PDF paths, corroborated by a rendered image and native axis ticks.
Record source object IDs, coordinates, transforms and stroke widths. Associate
central anchors using marker, connector and bar junction evidence together.
A triangle's bounding-box centre, centroid or tip, and a bar's midpoint, are
candidate geometry only, never automatically the exact central summary.
Where associated objects disagree, retain their candidate-anchor enclosure;
use a documented connector/junction anchor as a nominal reference if supported,
without averaging conflicting candidates. If no anchor can be authenticated,
retain ambiguity or unsupported status. Connecting paths supply no new samples.

Use a uniform graphical floor of 0.25 PDF point plus half the applicable stroke
width around each admitted anchor candidate or bar endpoint. The floor accounts
for finite placement/readout beyond encoded path precision (about one pixel at
300 dpi); it is not an experimental error estimate. Enclose all admitted candidates
before applying this padding. Tick coordinates receive the same rule. Inspect
all ticks for affine calibration consistency; retain any residual in the axis
allowance rather than fitting away a discrepancy. No allowance is chosen to
recover a contrast sign. Record native x uncertainty separately from the general
method's tamper accuracy. Recover hidden encoded bar paths where attributable;
if no path/endpoints are recoverable, retain missing, never zero or symmetric fill.

## Two reporting layers

A: propagate central-anchor enclosures and common calibration. For all contrasts,
sum signed original source y coordinates first; coefficient sums are zero, so
shared vertical offset cancels. Apply the signed common time scale once, retaining
its uncertainty and downward PDF y direction. Use interval enclosure over all
coordinate and scale extrema. I/J use original observations, never rounded DP/DF.
Full internal precision; displayed lower/upper endpoints round outward to 0.01 s.
POSITIVE/NEGATIVE require the entire interval strictly above/below zero;
UNRESOLVED includes zero; missing required support is UNSUPPORTED/INCOMPLETE.

B: repeat all 18 IDs using recovered displayed bar extents plus their endpoint
reading allowances, with common calibration once. Do not add central reading
uncertainty again. Missing endpoints make that contrast incomplete, while A stays
valid. This is sensitivity to displayed extents, not a contrast confidence interval,
significance/equivalence test, individual-shot range or population guarantee.

Summary statistic, per-point n, bar semantics, clock origin and covariance remain
unresolved unless explicitly authenticated for S2. General recipe/temperature,
mass tolerance, tamper accuracy and sampling statements are context, not automatic
S2 metadata. Do not borrow Figure 5's bar definition.

## Interpretation and verification

Report pressure signs, interactions, actual opposite-sign reversals, DF, J, and
B-layer coverage separately. I alone does not establish reversal; resolved versus
unresolved DP alone does not establish force dependence. Unresolved J is not
force independence; endpoint comparisons cannot exclude intermediate nonmonotonicity.
No regression, all-pairs force search, physical mechanism fit, Darcy inversion,
flux reconstruction or solver run. No pressure-drop law, permeability, choking
mechanism, population or causal conclusion follows. No 40 g/time flow conversion,
cross-source force–porosity transfer or Figure 5 repair.

Focused checks cover series/group joins, axis sign, competing anchors, hidden and
missing bars, 16 observations, 18 IDs per layer, coefficient arithmetic, shared
calibration, missingness, outward rounding and claims. One independent reviewer
will inspect the actual figure/records, independently calculate representative
contrasts and review wording. Run affected generators/tests and required hosted CI.
Preserve accepted Smrke S1/Figure 3, Cameron Figure 5/audit, consolidated permeability
comparison and historical receipts. Deliver one OPEN/DRAFT/UNMERGED PR with
no auto-merge. No successor. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
