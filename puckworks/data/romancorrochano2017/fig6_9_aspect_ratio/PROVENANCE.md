# Figure 6.9 steady permeability by chamber

Dataset `romancorrochano2017/fig6_9_aspect_ratio`; G1 / research only /
retrospective / target exposed / source internal. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Four means, eight displayed error endpoints; no individual-bed ratios or new
independent campaign. [Source reconciliation](../../../../docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001/SOURCE_RECONCILIATION.md)
and [plan](../../../../docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001/PLAN.md)
control the reading, input and aggregation limits.

`source_paths.json` binds the 359-page thesis hash, PDF page 261 / printed 236,
page 2817/content 2818 and decoded-stream hash. Coordinates are transformed PDF
page points, origin top left, y downward; not rendered-image pixels. PyMuPDF 2.0
enumeration indexes are zero-based and `seqno` is its page display sequence.
Quads preserve PDF path winding; “top” means minimum page y, not a Quad corner
name. The extractor checks duplicate outlines; the producer checks endpoint
ordering. Fill and outline tops agree within 0.001 pt.

| Condition | Fill drawing indices / sequence | Outline indices / sequence | Error drawing / sequence / cap items (upper, lower) |
|---|---|---|---|
| Psi_B 2:1 | 15,24 / 30,40 | 16,25 / 31,41 | 23,32 / 38,48 / 1,2 |
| Psi_B 6:1 | 17,26 / 32,42 | 18,27 / 33,43 | 23,32 / 38,48 / 4,5 |
| Psi_E 2:1 | 19,28 / 34,44 | 20,29 / 35,45 | 23,32 / 38,48 / 7,8 |
| Psi_E 6:1 | 21,30 / 36,46 | 22,31 / 37,47 | 23,32 / 38,48 / 10,11 |

Both error paths have identical twelve line items, verified by the extractor.
Coordinates retain drawing 32/sequence 48; drawing 23/sequence 38 is the same
graphic, not an additional variability observation. Both remain in source_paths.

`source_coordinates.csv` records original centres. Shared axis zero
y=312.3118896484375 and top y=104.43576049804688 correspond to 0 and
1×10⁻¹³ m². Drawings 4/14 (sequences 9/29) repeat the axis; drawings 8–13
give the ticks, cross-checked in RESULT.json. Maximum internal nominal linear
tick residual is below 0.061 pt, enclosed by the 0.61 pt anchor guard.

Stroke-based interpretation bounds: axes ±0.61 pt, mean tops ±0.16 pt,
error caps ±0.92 pt; these round the half-stroke widths outward. No raster
allowance is transferred. Exact coordinates do not mean exact experimental
measurements. `contract.json` retains these guards and the published multiplier;
`readings.csv` is the deterministic SI projection. Reading bounds, displayed
variability, printed table/input precision, and unquantified experimental/
calibration uncertainty remain distinct. No rounding allowance on the registered
material constants is inherited; the primary scenarios use fixed nominal inputs.

The ratio of condition means uses a shared zero/scale calibration. Its exact
rational bounds are retained alongside floating presentations. Scale cancels;
baseline uncertainty does not. The separately reported marginal outer ratio
enclosure permits combinations that need not be jointly admissible. Neither
enclosure is a physical confidence interval or a bed-level covariance model.

Rights: compact factual derived coordinates and readings only. Thesis access
does not grant redistribution rights or make it MIT licensed. PDFs, images,
rendered pages and source overlays remain outside Git. The original reconstructed
SVG is generated from the factual readings with a local VizSpec.

Offline reproduction needs no PDF or network:

```sh
python -m puckworks.analysis.corrochano2017_aspect_ratio --output /tmp/aspect-ratio --plot
```

Optional exact-copy source audit (requires PyMuPDF 2.0):

```sh
python tools/extract_corrochano2017_aspect_ratio.py /path/to/Roman-Corrochano17EngD.pdf --output /tmp/aspect-coordinates
```

Compare the emitted coordinates and paths to this directory. The numerical
producer uses the qualified local material input named in `contract.json`, not
the optional source library. `holdings_checked.json` is a bounded underlying-file
receipt, not a refreshed corpus census or raw-data absence claim.
