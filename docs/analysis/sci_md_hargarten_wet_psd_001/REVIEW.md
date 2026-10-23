# Independent scientific review

**PASS — no unresolved material scientific findings in the bounded analysis.**
The G exclusions concern the declared graphical midpoint observable. P remains
unresolved for wet/dry dilation, and exact physical-cutoff mapping remains
unresolved in both layers. Prepared-fraction G ranges are necessary outer
candidates only. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

This is the single independent AI scientific review by Codex agent
`/root/scientific_review`, separate from the implementation author. It includes
bounded corrections in this task, not a new source campaign, human GitHub approval,
software-check receipt or independent validation cohort. The scope remains G1 /
NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED /
SOURCE_INTERNAL / NONSCORING. Reviewed bytes are bound in
[review_receipt.json](review_receipt.json); later verification and PR handoff are
separate.

## Actual source inspection and corrections

I inspected the accessible published article PDF, methods, Table 1, captions and
surrounding prose, and the actual original embedded rasters for Figures 2, 3(b)
and 5(b). PDF and all three raster hashes match the contract. I compared retained
marker centres and admitted cumulative interval endpoints to the artwork using
per-series overlays at original coordinates and enlarged crops. This is fresh
source inspection, not reliance on the prompt, scalar CSV, text extraction or
source hash alone. Figures 4/6 were used only to check identities and descriptive
consistency. I did not independently repeat the external corpus search; the
author's holdings receipt distinguishes inspected workbook content from catalogued
files and makes no claim that unavailable data do not exist.

White/gray/black Figure 2 cumulative triangles correspond to dry/wet25/wet90.
Figure 3(b) supports medium S/M/L and Figure 5(b) supports light S/M. Figure 5's
caption additionally names L, contrary to its artwork, adjacent prose and Figure 6;
the retained interpretation properly omits light L. Cumulative triangles use the
right ordinate, separately from density circles on the left. All three diameter
axes are logarithmic; calibrations are panel-specific. The article says plotted
points represent interval midpoints. Neither raw bin boundaries nor a physical
cutoff/scaling observation map is authenticated.

The initial proposed extraction had five material source-reading issues, corrected
before the first formal Part C outputs:

| Point ID | Source finding and bounded correction |
| --- | --- |
| medium_M_dry:p04 | At x=653, the triangle is near y=1074, not proposed y=1082. |
| medium_L_dry:p05 | At x=674, the L dry triangle is near y=1274, not proposed y=1239. |
| medium_L_dry:p02–p04 | Proposed centres are not securely identifiable as L cumulative markers amid overlapping density/other-series marks; retained coordinates are explicitly unsupported and excluded from numerical operands. |

The corrected centres and supported remaining points agree with the admitted
±3 px reading allowance. [source_corrections.json](source_corrections.json)
preserves the failed readings and their disposition. No cutoff, quantile or
uncertainty allowance was changed to improve a result. All requested quantiles
remain present despite these unsupported proposed points. A plot-label ambiguity
was also corrected: thin lines show individual quantile ratios, while thick
intersections impose λ≥1. That change has no numerical effect.

The dry Figure 2 cumulative CI endpoints cannot be reliably separated from the
markers. Their missing status is appropriate; no density interval or swelling
spread has been substituted. Source PSD intervals are identified as 95% CIs, with
no authenticated simultaneous coverage. G/P rectangles preserve their distinct
meanings and do not cover unquantified experimental/operator uncertainty. The
hot-labelled treatment's cooling from about 90 to 60 °C, dry-air dispersion,
non-sieved ultrasound and prepared washed/no-ultrasound differences are retained.
Prepared fractions are selected retained preparations, not particle trajectories.

## Independent arithmetic and classification

[review_check.py](review_check.py) imports no producer code and opens reported
results only after reconstructing the calculations from contract and original
coordinates. It uses standard-library `Fraction` arithmetic. Log-axis diameter
bounds use exact integer nth-root inequalities, independently of the producer's
Decimal exponential path: for exponent n/d, the integer k satisfies
k^d ≤ 10^(n+6d) < (k+1)^d. The resulting 10^-6 µm enclosure is rigorous, not a
floating-point approximation treated as exact. Calibration/reading rectangle
extrema, all CDF bounds, monotone brackets and ratios are independently derived.

The checker verifies all 352 marker/layer rows, 36 cutoff readings, 36 contrasts,
120 quantile requests, 60 ratio requests, 14 intersections and all ten decisive
CDF witnesses, including source operand IDs, exact signed bounds, percentage-point
rounding and limiting intersection operands. Duplicate result IDs are rejected.
It independently confirms common nominal calibration assignments that admit
nondecreasing supported CDF readings in [0,1]; thus exclusion is not vacuous.
An empty supported P series is missing evidence, not a zero-width observation.

Strictly positive wet-minus-dry excess gives the valid inequality
Fwet(d)−Fdry(d/λ) ≥ Fwet(d)−Fdry(d) ≥ L(d) for every λ≥1. Each condition has its
own multiplier. All ten certified lower bounds are positive as exact rationals;
the conservative printed lower bounds remain positive. Exact zero is non-excluding.
The maximum positive lower bound is a discrepancy lower bound, not a best-fit
error, mobile-fines inventory or erosion fraction. No multiplier search is needed.

Generalized-inverse bracketing uses Fupper<q below and Flower≥q above, retains
plateaus and one-sided tails, and divides only finite positive diameter bounds.
Marginal enclosures relax shared dependencies, so nonempty intersections are
necessary-only ranges and do not supply a simultaneous dilation witness.
Checker controls and reviewed producer tests cover exact zero, overlap, missing
rows, invalid CDFs, partial/empty intersections, plateaus, gaps, panel calibration,
unit conversion and a known uniform-scale synthetic case.

## Independently confirmed scientific outcomes

| Layer / condition | Primary 40 µm | Complete declared-set outcome | Largest certified discrepancy lower bound |
| --- | --- | --- | --- |
| G wet25 | Evaluated, non-excluding | Excluded; positive at 10,25,50,100 µm | 11/524, at least 2.099236 pp, at25 µm |
| G wet90 | Excluded: 43/524, at least 8.206106 pp | Excluded; positive at all six cutoffs | 57/524, at least 10.877862 pp, at50 µm |
| P wet25 | Unresolved | Unresolved: missing dry cumulative intervals | No nontrivial certificate |
| P wet90 | Unresolved | Unresolved: missing dry cumulative intervals | No nontrivial certificate |

Both G wet/dry sets have complete six-cutoff support. All five prepared-fraction
G intersections and both within-roast intersections are nonempty with complete
fixed-quantile coverage: medium common outer range [1.122018,1.281598], light
[1.125108,1.265870], rounded outward. All 30 G individual ratios are retained.
P has nine finite individual quantile brackets but no supported dry/wet ratio
pair; all its scale intersections are unresolved. No empty-intersection witness
exists in this retained dataset. These findings match RESULT.md and RESULT.json.

I inspected the measurement-derived comparison figure and the report's practical
interpretation. They preserve G/P and graphical/physical distinctions, source
rights, incomplete P support and necessary-only candidate ranges. Rejection of
uniform geometric enlargement does not reject every size-dependent swelling
process or the native Mo model. No mechanism, mass inventory, hydraulic mapping,
EWP calibration or physical validation follows.

Reproduce the independent check offline, with Python ≥3.10 and no PDF, network or
third-party package:

```sh
python docs/analysis/sci_md_hargarten_wet_psd_001/review_check.py
```

The final checker run passed. Ordinary local tests, required hosted CI and final
submitted head are reported separately in VERIFICATION.md and the draft PR.
