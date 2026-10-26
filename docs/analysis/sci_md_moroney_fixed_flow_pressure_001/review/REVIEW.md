# Independent review — Figure 12 fixed-flow comparison

**PASS_FOR_DECLARED_SOURCE_QUALIFICATION_AND_OBSERVATIONAL_COMPARISON.**
Reviewed 2026-10-26 by the separate nonhuman reviewer agent
`/root/independent_review`, which did not implement or edit the source extractor,
analysis, scientific records or authority updates. This is an independent check
within this task, not a blinded review, independent experiment or predictive
validation. The task/plan and predecessor context were available to the reviewer.

The actual reviewed file SHA256 identities, independent numerical results and
private check-script identities are in [REVIEW.json](REVIEW.json). This receipt
binds those contents, not a prospective commit hash. Subsequent unchanged-file
delivery/QA receipts do not require recomputing the science. Full local-suite and
hosted-CI dispositions remain separate in [VERIFICATION.md](../VERIFICATION.md).

## Actual source access and qualification

I opened the owner-controlled 19-page publisher PDF and independently verified
SHA256 `896672a997e585a50d97f988caa66259a9a8ed0067300ea7d19725a13c01c4a8`.
I separately rendered and visually inspected printed pages 219 and 233, including
the full Figure 12 panels/tails and Figure 3 baseline. I read the original text
of §2, §2.2, §2.3, G.1 and G.3 and both captions; private source renders/text stay
outside Git. I examined native drawing items independently, without calling the
candidate extractor for my first extraction.

All 94 legacy rows correspond one-to-one to colored marker subpaths. Each panel
contains 22 low-pressure and 23 high-pressure data markers plus one legend sample
for each condition. Rows 7/32/54/79 are the symbols inside the rounded, labelled
legend boxes: drawing/sequence pairs 320/424, 322/428, 457/581 and 459/585.
Thus 90 markers are retained and four legend samples excluded; no omitted,
ambiguous or duplicate Figure 12 candidates were found. Panel b drawing 437 has
two circles, 439 six circles, and 456 eight rectangles. Counting drawings alone
would miss tail observations. Filled marker paths have no applicable stroke.

Labelled ticks establish the coordinate transforms, including the downward PDF
y direction and frames extending below zero. I independently checked labelled
tick residuals and inspected the candidate's more conservative minor/mirrored-tick
checks. Circle bounding-box and opposite-anchor midpoint candidates are enclosed
before padding. All 44 low-pressure observations match Figure 3 a/b in ordered
one-to-one lineage. My independent native calibrations differ between renderings
by at most 0.061794 g and 0.056740 mg/g; this is rendering correspondence, not
experimental error. Figure 12 supplies the comparison coordinates throughout.
The candidate re-extractor subsequently reproduced `source_objects.json`
byte-for-byte from the accepted PDF.

The stated JK material, 60 g nominal loading, 250 mL/min, axes and separate pot/
exit observables are authenticated. Figure 3 states approximately 4% moisture;
G.3 repeats the same nominal coffee loading. No new high-pressure moisture assay
or exact dry-dose inference follows. The source calls Figure 3's baseline a
pressure differential while G.3/Figure 12 use absolute-pressure terminology.
The inspected apparatus description supplies no sensor/reference/outlet-pressure
reconciliation. The notes correctly preserve this unresolved distinction.

Flow-through replicate/statistic, assay error, covariance, sampling-window,
mixing, withdrawal and run-join metadata remain unknown. Batch refractometry
does not establish Figure 12 uncertainty. Pot collection supports an accumulating
receiver interpretation but does not authenticate the high-pressure cumulative
mass/withdrawal contract. Refusal of optional solute-mass differences is warranted;
it does not obstruct concentration comparison. No ratios are reported.

## Independent numerical checks

I independently extracted native centers and evaluated the two interpolants on
each complete union of knots using rational arithmetic. All extrema and their
attaining locations agree with the candidate:

| Panel | Common support (g) | Minimum Δc (mg/g) at M (g) | Maximum Δc (mg/g) at M (g) | Maximum absolute Δc (mg/g) |
|---|---|---|---|---:|
| Pot | 22.014325634–933.354631137 | −9.887383549 at 48.134218244 | −0.385724194 at 413.713608023 | 9.887383549 |
| Exit | 22.554655050–934.832178572 | −11.321757950 at 51.183569878 | 2.803524281 at 101.115413704 | 11.321757950 |

There are 42/43 union knots. Each absolute maximum occurs at its signed minimum;
there are no tied extremal knots or constant extremal intervals in these data.
Separate synthetic crossing/tied/constant examples check the general attainment
handling, including intervals and support gaps.

I independently recomputed every fixed-mass central value and graphical enclosure.
For graphical weights I enumerated corners of each valid endpoint-coordinate
rectangle, independently of the candidate's closed-form weight formula. Both
series satisfy universal support and separated coordinate ordering at all seven
masses. Alternate brackets near uncertain knots are included. Native y contrasts
cancel the common offset and receive one shared scale interval; concentration
marginals containing calibration are not added again. Horizontal calibration/
coordinate dependencies are deliberately relaxed and the bounds are not sharp.

All 14 statuses agree: only pot 800 g is NEGATIVE, with central −1.967626815 mg/g
and outer interval approximately [−3.666737253, −0.308422063] mg/g. The other
13 intervals include zero. For example, pot 600 g is approximately
[−3.765486697, 0.129623427] and exit 50 g is
[−35.218416975, 15.877762633] mg/g. The 186 value/bracket comparisons agree to
within 5.23e−13 in binary64 reporting; the 1e−9 comparison tolerance is only a
check of independently serialized arithmetic, not a graphical allowance or sign
tolerance. Candidate classifications use exact rational arithmetic.

Independent analytical checks passed for unequal grids, exact knots, no
extrapolation, crossings/ties, constant attaining intervals, gaps, horizontal-only
and vertical-only perturbations, alternate brackets, universal support distinct
from possible bracketing, ordering refusal, duplicate-coordinate refusal, exact
zero inclusion and outward rounding. The focused repository suite also passed:
`python -m pytest -q tests/test_moroney2015_fixed_flow_pressure.py` — **12 passed**.

## Claims, preservation and outcome

I reviewed the final result, source notes, VizSpec, rendered comparison, card,
MANIFEST/curation and directly affected development/planning wording. Initial
presentation defects were corrected within this task: a placeholder named the
wrong resolved slot, the contrast axis clipped two exit intervals, and footer
text overlapped axis labels. The final figure includes every interval, a signed
exit-tail inset and a separated explanation of the declared interpolation and
discrete sensitivity. The JK source-section citation was corrected. Numerical
evidence was unchanged by these bounded presentation corrections.

All 13 accepted Moroney source-file hashes match, including raw Figure 12 and
`README_manifest.csv` with original bytes/line endings. Independently compared
100 tracked scientific artifacts across accepted Moroney-transfer, Khamitova
chemistry/common-scaling and Matias fraction/aggregation bundles: byte-identical
to implementation base `0004749e4e72c9db9c34b653dd4e4f8a1fa128ee`.
The legacy loader diff is documentation only; its raw-loading behavior is intact.

No scientific review blocker remains for this bounded observational result.
Unknown experimental uncertainty and pressure semantics remain limitations, not
solved metadata. Graphical separation is neither statistical significance nor a
causal pressure effect; zero inclusion is neither equality nor practical
equivalence. No physical kinetics law, EWP adoption, new campaign or rescue of
the CALIBRATION_INADEQUATE transport result follows. This review does not assert
completed hosted CI, authorize merge, or substitute for the implementer's final
repository/head-preservation handoff.

## Bounded serialization addendum

2026-10-26: reviewed the two added post-save lines that strip trailing whitespace
from the SVG. Removing exactly those lines recovers the original reviewed module
SHA256. The saved original SVG matches its reviewed hash, and its linewise
trailing-whitespace normalization equals the new SVG byte-for-byte. Every other
reviewed-file hash is unchanged. `REVIEW.json` preserves the previous/current
module and SVG bindings and updates the current reviewed hashes. No plot geometry,
scientific value, support, classification or claim changed. Original scientific
evidence is reused; the review outcome remains PASS. Full local-suite and hosted
CI outcomes remain separate.

PHYSICAL_VALIDATION=NOT_ESTABLISHED.
