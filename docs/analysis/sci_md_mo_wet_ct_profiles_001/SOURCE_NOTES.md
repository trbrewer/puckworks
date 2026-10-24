# Source and observation record

Controlling publication: Chaojie Mo, Richard Johnston, Luciano Navarini,
Furio Suggi Liverani & Marco Ellero, *Exploring the link between coffee matrix
microstructure and flow properties using combined X-ray microtomography and
smoothed particle hydrodynamics simulations*, Scientific Reports 13, 16374 (2023).
[Final article](https://www.nature.com/articles/s41598-023-42380-y),
[PMC mirror](https://pmc.ncbi.nlm.nih.gov/articles/PMC10541431/),
DOI [10.1038/s41598-023-42380-y](https://doi.org/10.1038/s41598-023-42380-y).

## Authenticated identities and access

All three original PDFs were retrieved by HTTPS GET on 2026-10-24 (Python
requests, HTTP 200, application/pdf); all match the supplied review references.
Raw PDFs are external, not committed. SHA-256:

| Source | Bytes | SHA-256 |
|---|---:|---|
| [Final PDF](https://www.nature.com/articles/s41598-023-42380-y.pdf) | 3044052 | `101720c58cabd32ce2852025a3d61e2b41c3f4d315f32c853f303a929542ffb8` |
| [arXiv v2 PDF](https://arxiv.org/pdf/2305.03911v2) | 2024245 | `5cb62413c80f70916f4ccf6e2a432bffdc5def0cc817e5f0e1685502720ece0c` |
| [Final supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41598-023-42380-y/MediaObjects/41598_2023_42380_MOESM1_ESM.pdf) | 930477 | `9ba14a679900eb1f460c13ab164272d19b9ea896b88798a35a20d57f05cba464` |

The [arXiv record](https://arxiv.org/abs/2305.03911) dates v1 to **6 May 2023**
and v2 to **8 October 2023**. The journal appeared **29 September 2023**.
Thus v2 itself is later than the journal. The original arXiv intake is retained;
[version-specific HTML](https://arxiv.org/html/2305.03911v2) is a companion,
not authority to silently change final-text method wording.

The separate final supplement was actually inspected during implementation,
using PDF text and rendered pages: pp.1–2 SPH formalism/parameters, pp.3–6
four enlarged vertical sections E/H/M/F, p.7 references. It contains no numerical
1-hour/24-hour segmented profiles. Those two scan-delay statements remain
**author narrative only** (final p.12; arXiv v2 p.13). No extra intake was opened.

Configured external Mo subset: **FILES_INSPECTED**, not catalog-only. Existing
`tools/inventory_local_corpus.py query "$PRIVATE_MANIFEST" --family mo2023`
resolved/rehashed seven files, all matching the dated 2026-09-23 snapshot. The six
CSVs and provenance were then read: four-type granulometry; four six-row SPH
sample tables; 12 Figure 8a points. The public repository already holds the same
numerical files. No Figure 14/16 dataset was present. Other private material was
not searched or inferred absent; other families remain CATALOG_ONLY. The new
canonical intake is not a new external census. Existing dataset IDs, SPH results,
strength labels and Forchheimer units caveat remain. SCI-MD-MO-TRANSFER-001 is
about the separate `mo2023_2` extraction/swelling source and is unchanged.

## Panel, radius and observation-unit authentication

| Panel | Final PDF page | arXiv v2 page | Capsule history | Stage |
|---|---:|---:|---|---|
| 14a | 12 | 14 | type H, medium roast | before extraction |
| 14b | 12 | 14 | same displayed medium capsule | three days after extraction |
| 16a | 13 | 15 | type H, dark roast | before extraction |
| 16b | 13 | 15 | same displayed dark capsule | immediately after extraction |

Every panel legend prints radii **0.92, 2.77, 4.61, 6.45, 8.30, 10.14 mm**.
The six unique RGB strokes match the six corresponding legend samples, in order:
dark blue, blue, cyan, green, yellow, orange-red. Figure captions, article p.11
and retained panel crops authenticate stage/roast/timing. Colors crossing is not
an identity failure: the original strokes and connectivity remain recoverable.
No unresolved membership remains for this intake; tests separately enforce that
finite alternatives qualify only if every alternative has complete support.

Final p.5 describes annular sections of equal radial thickness and layer-wise
segmented volume fractions. These are spatial summaries of annular regions at
printed radial labels, not point measurements. No annular boundaries or whole-bed
volume weights are reconstructed from the labels. There are **24 profiles from
two capsule histories**, not 24 independent extractions. Figure 6 is context,
not another paired baseline. Vertices are rendering geometry, not CT slices or
independent observations. The canonical signal is `published_segmented_signal`;
native epsilon and the source's “porosity” are retained separately in metadata.
Spatial **y increases bottom/outlet toward top/inlet**, although plotted on the
horizontal page axis. Fixed bands are interior regions, not boundary faces.

## Geometry, masks and version comparison

Extraction uses **PyMuPDF 1.26.7 / MuPDF 1.26.12**, `Page.get_drawings()`;
`get_drawings(extended=True)` was also inspected for the central explicit clip.
Coordinates are page points (x right, page_y down), with z=-page_y for calibration.
All 12,494 profile segments use PDF `l` operators. There are no Bezier profile
segments and no flattening approximation. Source glyphs/rounded legend boxes
include curves but are not integrated as data.

Canonical CSV: one row per original line segment, with native endpoints,
transformed endpoints, panel/history/radius, page/path/paint-sequence/subpath/
segment IDs, stroke width and parameterized visibility pieces. Original path
orientation/topology is retained. The three gaps in the delayed central path
remain disjoint; no sorting/joining/clamping occurs. Hidden coordinates are
explicit **AUDIT_ONLY** through profile metadata and per-segment mask status.
They are used for transcription/version audit only, never a displayed-evidence
mean or bound. `visibility_parts` is a list of `[t_start,t_end,status]` on each
original segment. Native endpoints use full parsed float representation.

The final left-panel data paths are 87–92; right-panel data paths 220–225.
ArXiv corresponding paths are 71–76 and 208–213. Final panel axis paths are
93/226; opaque legend paths 94/227. Exact path/paint IDs and coordinates live in
canonical metadata. Each path is strictly increasing in native x inside its
original continuous subpaths (minimum segment dx >0.117 pt). The legend mask is
the full bounding rectangle, expanded by half the actual border width; rounded
corners are conservatively unavailable. For 14b r=0.92 the extra PDF clip is
intersected with the displayed axis box. Other profiles use their panel axis box.

The delayed central nominal display map, rounded here for orientation (exact
fractions in CSV):

| y interval (mm) | Evidence |
|---|---|
| 10.89470–19.86189 | visible |
| 19.86189–20.09685 | legend-occluded |
| 20.09685–20.11089 | tiny visible portion above legend, below axis limit |
| 20.11089 onward | axis-clipped, interrupted by original source subpath gaps |
| 20.63995–20.88531; 21.47171–21.55721; 21.60127–21.66423 | original path gaps in the clipped region |

Consequently the [19,21] central request has **legend occlusion, axis clipping
and a source subpath gap**. Its estimate and bounds are null. This is not a
zero-spanning computed interval. Its primary [17,19] window retains full support
throughout the declared calibration/local allowance union. All other requested
bands retain complete support. Full-profile rendering shows missing portions as
missing, including the small visible fragment; it does not connect across masks.

`source_geometry_comparison.json` compares every corresponding segment endpoint,
in original order, after per-panel tick calibration. It checks operators,
orientation, counts and the same subpath discontinuity pattern. Maximum difference
across all 24 profiles: **8.468e-5 mm** horizontally and **4.065e-6 signal units**
vertically (outward rounded). These are PDF-production differences, not physical
uncertainties or independent replication. Curves are counted once. Geometry
agreement does not prove that every sentence of the two versions is identical.

## Observation-method limits

Final pp.3–4 dry method: invert the image, segment with a global threshold,
identify connected and isolated voids, and choose the threshold to match typical
literature bed porosity. The example matches 0.17 at grayscale 200. Partial volume
from fines/intragranular pores and scan resolution constrain absolute meaning.
Final p.11 wet method: the wet porosity is not known a priori; threshold selection
instead uses the horizontal center between two grayscale histogram peaks. The
source acknowledges that microCT cannot properly distinguish liquid from solid.
The quoted method locations refer to the final publication. The arXiv v2 wet
paragraph inspected on p.12 also describes the peak-midpoint method, but no
blanket sentence-equivalence claim is made.

Segmentation sensitivity, scanner measurement error, repeatability, physical
variability and saturation remain unquantified. Graphical bounds cover reading a
printed representation only. Different roast, capsule and delay are confounded.
DeltaA compares displayed coordinate windows without material registration or
an established common observation operator. The analytical witness in RESULT.md
is constructed, not fitted, and does not equate Mo's signal with gas volume.

## Calibration, local contract and numerical qualification

PLAN.md freezes the shared per-panel affine map and allowances. Horizontal
anchors are printed 12/22-mm ticks; vertical anchors are 0/0.40 ticks. Actual
axis/tick strokes are 0.442 pt (Figure 14) and 0.446 pt (Figure 16). Each anchor
moves by half that width plus 0.003 pt; no parameters are shared across panels.
Intermediate tick residuals are at most 0.00219 pt horizontally and 0.00310 pt
vertically, well within the total 0.224/0.226-pt anchor allowances. This is
geometrical justification of a declared reading contract, not scanner calibration.

Data strokes are 0.829/0.837 pt; local horizontal and vertical allowances are
half those widths plus 0.003 pt: 0.4175/0.4215 pt (approximately; exact parsed
widths are retained). The square relaxes stroke geometry. Locally sampled
abscissae may vary by h_x, and vertex ordinate departures are bounded by h_z.
A shared affine calibration remains shared throughout the panel. A common
ordinate offset cancels in spatial contrasts and therefore DeltaA. Positive
scale affects magnitude, while horizontal calibration moves the band boundaries.

At fixed calibration, exact partial-segment integration is a linear functional
of source vertices; weights for reused source quantities are combined first.
For independent bounded ordinate departures the radius is sum |a_i|h_i. This is
a deterministic box, not statistical independence. For uncertain local x and
calibration the interpolation weights are not frozen: nonnegativity/unit sum
bounds their combined norm by the total absolute retained band coefficients.
For disjoint equal-width contrast bands the vertical radius is at most 2h_z in
native z, valid throughout calibration; identical/overlapping terms are combined
before relaxing. Common-coordinate cancellation is explicitly tested.

Nominal integration uses gamma*alpha/(v−u) times the native x integral; alpha is
the Jacobian. Qualified integration uses physical y cells directly, an equivalent
change of variables. A fixed 4×4 set of closed parameter boxes covers all a,b.
Every one of the 256 y cells per band maps to an interval bounded by multilinear
corner extrema, expanded by h_x. Both ends and all internal vertices supply the
PL range. The cell range times full cell width encloses its entire integral.
Summing signed enclosures and then taking the hull over parameter boxes encloses
the continuous allowed set. Ordinate scale is independently interval-multiplied;
DeltaA subtracts the independent panel enclosures. Relaxed endpoints are not
asserted attainable or jointly reconstructible. No optimizer or grid-only
extremum claim is used. Support is checked on the entire union before subdivision.

Floating-point audit bounds for these canonical inputs: |native coordinate|<600,
max absolute segment slope<24.601, segment dx>0.117, horizontal anchor separation
>164 pt, vertical separation>144 pt, gamma<0.0028. Each scalar partial integral
or cell-sum evaluation uses fewer than 10,000 floating operations; intermediates
are bounded by 1e6. A conservative binary64 forward-error allowance using
10,000*epsilon/(1−10,000*epsilon), with the above denominator/range bounds,
is below 1e-7 in signal units. Every inverse-cell interval is additionally expanded
outward by 1e-10 pt; final bounds expand by **1e-7 signal** and `nextafter`.
DeltaA inherits both guards and outward subtraction. This guard is much larger
than observed roundoff and is not an experimental allowance. Source PDF/parser
rounding is separately covered by the 0.003-pt graphical additions. Displayed
endpoints round outward; classification uses unrounded bounds.

## Rights, modifications and reproduction

The final article is © The Authors 2023, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The final p.15 credit notice includes images unless separately credited. Neither
Figure 14/16 nor their captions carry an exception. `figure14_source.png` and
`figure16_source.png` are cropped 144-dpi PDF renderings; the canonical CSV and
comparison plot are transcribed/redrawn derivatives. Attribute all retained
source-derived material to the five authors and DOI above, identify these
modifications and retain the license link. Repository software MIT terms are not
assigned to third-party article artwork. Raw PDF bytes are not committed.

Run extraction in a separate environment so ordinary analysis/tests do not
import or require the parser:

```sh
python3 -m venv /tmp/mo-pdf-extract
/tmp/mo-pdf-extract/bin/pip install PyMuPDF==1.26.7
# Download the three URLs above as final.pdf, arxiv-v2.pdf, supplement.pdf
# into an external SOURCE_DIR. Extraction verifies all three identities.
/tmp/mo-pdf-extract/bin/python docs/analysis/sci_md_mo_wet_ct_profiles_001/extract_profiles.py \
  --source-dir "$SOURCE_DIR" --data-dir /tmp/mo-extracted-data --evidence-dir /tmp/mo-extracted-evidence
```

For different mirror bytes, authenticate their contents explicitly before changing
this task's hash-pinned extraction route; do not force a supplied hash. These
actual originals matched, so no alternate-byte adjudication was needed.

After installing existing repository dependencies (`pip install -e '.[dev,figures]'`):

```sh
python -m puckworks.analysis.mo2023_wet_ct_profiles --output /tmp/mo-wet-ct-replay --plot
python -m pytest -q tests/test_mo2023_wet_ct_profiles.py
```

Offline regeneration consumes the committed CSV/JSON only. Tests deny network and
PDF-reader imports in a fresh process. All five numerical/report artifacts and
both figure formats are deterministically regenerated; the extraction route also
reproduces canonical CSV/metadata, source crops and geometry comparison separately.
