# SCI-MD-HARGARTEN-WET-PSD-001

G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Actual base: `853cc0b609e0abaf9713579f7c0237a859692400`, current main on
2026-10-23, containing #354. No intervening main changes or Hargarten PR found.
EWP read-only context: `f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`.
Read AGENTS, CLAUDE, onboarding, minimum-necessary governance, data policy,
source cards, data register/guide, development guide and the specified predecessor
and EWP assessments. No runtime, gate, EWP or accepted-input change is intended.

## Source inspection and fixed reading contract

Publisher HTML/PDF text authenticated methods, Table 1 and captions. Direct
publisher byte download returned HTTP 403; the TUM repository's published article
copy downloaded successfully: DOI 10.1002/jsfa.10440, 11 pages, printed 3960–3970,
SHA256 `4a41545954e6748a33ec1d956fd690bea58aba9c2e38955dfbb3ae9f5bffbfb0`.
Original embedded raster artwork inspected: Figure 2 (p3964), Figures 3/5 (p3965).
Figure 2 triangles are CDFs (right axis); circles are densities (left axis).
All three retained panels use log diameter and linear cumulative percent axes.
Figure 3b has medium S/M/L; Figure 5b has light S/M only, despite its caption's L.
Figures 4/6 and prose are consistency context, never numerical inputs.

Points are displayed size-interval midpoints (source p3964). Instrument bin edges
and a binning/scaling commutation map are unavailable. Analyze nondecreasing CDF
representations through retained midpoint markers; use monotonicity through gaps,
not the connecting dashed lines. Physical fractions at exact cutoffs and physical
quantiles remain unresolved. Source artwork is external CC BY-NC, not MIT.

Retain integer pixel coordinates in original embedded images, top-left origin;
point centres and identifiable CDF CI endpoints get ±3 px reading allowances.
Each panel shares independent ±1 px axis-anchor allowances (two x and two y).
These allowances cover marker-centre/stroke placement and raster reading, not
experimental error. Freeze them before formal outputs; do not tune for outcomes.
Use every retained, authenticated marker; missing/obscured CI endpoints are null,
not zero-width. G uses centre bounds; P uses only identifiable CDF interval endpoints.
The source calls displayed intervals 95% CIs; joint coverage/covariance unavailable.
No density intervals, source-summary spreads or inferred replicates enter P.

## Fixed decisions and implementation

A/B: retain cutoffs 10,25,40,50,100,250 µm; 40 primary. Three conditions dry,
wetted at 25°C, wetted at 90°C. Per layer retain 18 readings and 18 contrasts
(two wet-minus-dry and hot-minus-cool per cutoff), including unsupported rows.
Outer subtraction is conservative, with shared calibration provenance; endpoints
need not be jointly attainable. Any supported strictly positive wet-minus-dry
lower bound excludes that condition's entire family Fwet(d)=Fdry(d/lambda),
lambda>=1: monotonicity gives Fdry(d/lambda)<=Fdry(d). B=max(0,max lower) is
only a certified maximum-discrepancy lower bound, not optimal fit or fines mass.
Any witness takes precedence over unrelated missing rows; otherwise complete
non-excluding coverage is NOT_EXCLUDED, incomplete coverage UNRESOLVED.

C: q=.10,.16,.50,.84,.90,.99 for medium S/M/L and light S/M (60 diameter and
30 ratio requests per layer). Q=inf{d:F(d)>=q}; below anchors require Fupper<q,
above anchors Flower>=q. Preserve one-sided tails, plateaus and gaps; never force
endpoints to 0/1 or extrapolate. Ratio [wet lower/dry upper,wet upper/dry lower]
requires finite positive bounds. Intersect with [1,infinity) within each fraction
and within each roast, retaining operands and every empty witness. Nonempty
complete/partial outer ranges are necessary only, not simultaneous compatibility.

Use exact fractions for ordinate calibration/subtraction/classification and
outward-enclosed decimal transcendental evaluation for log-axis diameter bounds.
Strict positive certificates must survive outward display rounding. First exhibit
one shared nominal calibration and nondecreasing [0,1] CDF assignment per retained
series/layer; inconsistency blocks affected decisions, never supplies vacuous exclusion.
No multiplier grid, fit, optimizer, raw-bin inference or scientific epsilon.

## Bounded delivery and review

Retain source/holdings records and original-coordinate table; deterministic offline
producer, CSV/JSON tables, local VizSpec comparison, independent checker, RESULT,
one independent scientific review checking actual artwork, and ordinary checks.
Preserve old CSV identities and predecessor results. Update only affected card,
capability/manifest owners and generated projections. One draft PR, open/unmerged,
auto-merge disabled. Public source exposure makes this no protected validation set.
The decision constrains a source-specific measured PSD representation; it identifies
no erosion inventory/rate, packing or hydraulic map, nor rejects all swelling or Mo.
