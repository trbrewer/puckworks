# Source qualification and observation contract

Moroney, Lee, O’Brien, Suijver and Marra, *Modelling of coffee extraction during
brewing using multiscale methods: An experimentally validated model*, Chemical
Engineering Science 137 (2015), 216–234, DOI [10.1016/j.ces.2015.06.003](https://doi.org/10.1016/j.ces.2015.06.003).
Dataset identity remains **moroney2015/data**; no new experimental family/campaign.

The owner-controlled publisher PDF was resolved through the configured external
collection and its known paper folder. Its SHA256 is
`896672a997e585a50d97f988caa66259a9a8ed0067300ea7d19725a13c01c4a8`,
19 pages, matching the accepted original exactly. Figure 12 is printed page 233 /
zero-based index 17. The implementer inspected native paths and full rendered
pages 219 and 233; the independent reviewer separately rendered/inspected them.
Section 2.3 (218), Figure 3 caption (219), section G.3 (232–233), §2 and G.1
were read. The prior audit qualified only selected Figures 3/11; sharing page 233
never authenticated Figure 12. Private PDF, extracted page text and page renders
remain outside Git. Existing Elsevier source rights are unchanged: numeric
extraction and attributable analytical redraw only, no blanket source licence.

## Statements and their scope

| Item | Authentication / interpretation |
|---|---|
| JK material | §2 opening text (217)/G.1 identify Jacobs Krönung standard drip-filter coffee, a relatively fine grind. The other Illy/Cimbali grinds are distinct materials; no source-lot/roast identity is recovered here. |
| Loading | Figure 12 legend: 60 g in both conditions. Figure 3 caption: 60 g including approximately 4% moisture. G.3 says experiments repeat at the same coffee bed mass/flow; this supports the same nominal as-received basis. No independent high-pressure moisture assay or dry-dose outcome is inferred. |
| Flow | Both Figure 12 legends/caption and G.3: 250 mL/min. This is reported imposed flow, not a recovered measured trajectory, throughput uncertainty or equality of all bed conditions. |
| Apparatus | §2.3: cylindrical flow-through cell, rotary vane pump, nominal 1 L water at 90 °C, constant-flow mode with adjusting differential pressure or constant-differential mode with adjusting flow. G.3 uses the same apparatus. Figure 3 gives 59 mm diameter/4.05 cm JK height; no high-pressure bed-height measurement or equal operating porosity follows. |
| Pressure | Figure 3 calls reused 2.3 bar a pressure differential. G.3 and Figure 12 use absolute-pressure terminology for 2.3 and 9.0 bar. No pressure sensor type/location/reference, downstream back-pressure arrangement or outlet pressure reconciles these. Mathematical model boundary pressures do not authenticate experimental sensor semantics. Preserve native labels; no gauge conversion, authenticated 6.7-bar bed-pressure difference, Darcy gradient or EWP inlet boundary. |
| Axes | Caption and labels: beverage mass Mbrew in grams; mg coffee solubles per gram beverage. y increases upward, PDF y increases downward. Frame extends below zero; calibration uses labelled ticks. |
| Panel a | Concentration of the beverage collected in the coffee pot, measured throughout extraction (§2.3); an accumulating receiver interpretation is supported. Source does not specify mixing, withdrawals, corrected accumulated mass, reconstructed runs or contemporaneous balance denominator for the high-pressure record. |
| Panel b | Concentration of beverage at filter exit, measured throughout extraction. No authenticated instantaneous sampling or finite-window operator, durations, aliquot sizes or precise clock/mass joins. |
| Lineage | G.3 repeats the JK baseline comparison; 44 low-pressure centers match Figure 3 a/b one-to-one after independent native calibration. The same observations occur in different renderings, not new physical extractions. Pot/exit run pairing and replicate counts are unknown. |
| Assay context | §2.2 describes batch PAL-3 refractometry and evaporative 1 °Brix→8.25 g/L calibration. §2.3 does not explicitly assign that assay/calibration or its precision to these flow-through curves. No imported assay error. |
| Authors’ interpretation | G.3 describes near-identical profiles and reproducibility within a few percent, interpreting substantial independence from absolute pressure in the tested range. This is attributed interpretation, not measured uncertainty, statistical significance, equivalence or a validated causal mechanism. |

Replicates, averaging/statistic, flow-through assay error, covariance, sampling
windows, pot mixing, withdrawals, run joins, wetting history, porosity and
residence-time distributions remain unknown. A marker is not an independent brew.
The inherited predecessor used M*c_pot for its qualified baseline mass constraint;
that interpretation is preserved there. We do not extend it to an unauthenticated
high-pressure cumulative record: optional ΔS is UNSUPPORTED at all seven pot
masses. Concentration comparison remains supported. No ratios, dry-dose EY,
permeability, kinetics, species prediction, origin integration or forced pot/exit
consistency are introduced.

## Complete relevant object accounting

`source_objects.json` records all 94 legacy rows, source drawing/sequence/subpath
IDs, native geometry, center candidates, color, fill/stroke, legacy values and
re-extraction differences. Every candidate matches exactly one legacy row; there
are no omitted/ambiguous/unsupported candidates or duplicate Figure 12 renderings.
Both panels retain 22 blue low-pressure and 23 red high-pressure data markers.
The four questioned rows are authenticated legend samples, not fitted outliers:

| Raw data row | Panel/label | Drawing/sequence/subpath | Reason |
|---:|---|---|---|
| 7 | a / 2.3 bar | 320 / 424 / 0 | Inside rounded legend, beside low-pressure label |
| 32 | a / 9.0 bar | 322 / 428 / 0 | Inside rounded legend, beside high-pressure label |
| 54 | b / 2.3 bar | 457 / 581 / 0 | Inside rounded legend, beside low-pressure label |
| 79 | b / 9.0 bar | 459 / 585 / 0 | Inside rounded legend, beside high-pressure label |

Circles split into four-Bezier subpaths; each rectangle is separate. In panel b,
drawing 437 contains two circles, 439 six circles, and 456 eight squares. Their
tails must not be counted as one drawing each. Circle nominal anchors are the
native bounding-box centers, with opposite cardinal-anchor midpoints also admitted
as candidates. Squares use native rectangle centers. Markers are fill-only:
applicable stroke width is zero. No colored connecting paths add observations.
All 44 Figure 3 lineage links bind accepted original row and native object IDs;
recalibration differences are retained. Primary results use only Figure 12 centers.

Raw row numbers count data after comments/header; PDF page, drawing, sequence and
subpath indices are zero-based. Coordinates are PDF points with top-left origin.
Unrelated Figure 11 objects, bibliography glyphs and decorations are outside this
accounting. Calibration/legend objects and tick-label bounding boxes are included.

## Calibration and graphical convention

| Panel | x at 0 g (pt) | x at 1000 g (pt) | y at 0 mg/g (pt) | y at 200 mg/g (pt) |
|---|---:|---:|---:|---:|
| a | 154.73899841308594 | 292.5360107421875 | 317.05096435546875 | 248.91995239257812 |
| b | 335.302001953125 | 473.1000061035156 | 317.05096435546875 | 248.91995239257812 |

One shared affine x/y calibration per panel uses endpoint labelled ticks; all six
labelled x ticks/five labelled y ticks corroborate it. The 94 minor/major/mirrored
tick paths per panel are also retained and checked, including frame-padding ticks.
Minor/mirrored ticks are consistency checks, not extra fitted anchors. Maximum
absolute residuals: x a 0.010040283203125 pt, x b 0.00696563720703125 pt, y both
approximately 0.01043548584 pt. All are included conservatively, not fitted away.

The declared Cameron-plan convention is 0.25 pt + half applicable stroke width.
For markers, enclose all source-supported center candidates before the 0.25 pt
padding. Calibration tick width is 0.30000001192092896 pt; add maximum axis
residual to the endpoint tick padding (about 0.410040/0.406966 pt in x and
0.410435 pt in y). The module recomputes residuals with exact rational arithmetic
on serialized native decimals. JSON floating residuals are descriptive receipts.
This allowance is researcher-defined graphical sensitivity, not instrument
precision, experimental SD, confidence region or probability distribution.

Transform each marker's x enclosure over both uncertain endpoint ticks; these
marginal rectangular mass bounds relax shared x-calibration and marker-coordinate
dependencies. Require unambiguous interval ordering and universal component
coverage before enumerating all possibly active neighboring brackets. Native
ordinate bounds use -PDF_y, so the vertical offset cancels in a same-panel H−L
contrast. Apply one common positive vertical scale interval after subtraction.
The concentration marginals in the sidecar already contain full y calibration;
they are **not** reused/added in the contrast calculation. This avoids double
counting. The relaxation permits marginal extremes that may not coexist; bounds
are conservative, not sharp or claimed attaining geometries. Sensitivity is only
at the seven fixed masses per panel, never a continuous uncertainty ribbon.

Exact rational arithmetic protects order, zero inclusion, convex interpolation
weights and signs. No arithmetic epsilon is used. Central numeric CSV/JSON fields
are nearest binary64 displays; `*_exact` strings preserve rationals. Bounds shown
in RESULT round outward to .001 mg/g. Physical between-marker behavior is unknown.

PHYSICAL_VALIDATION=NOT_ESTABLISHED.
