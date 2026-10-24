# Independent source and numerical review

**Disposition: accepted for the bounded descriptive result, after three small
source-record corrections in this same review. No outstanding scientific defect
was found.** This is one substantive independent AI review, performed by the
`independent_s2_review` agent on 2026-10-24. It is not a human review, blinded
assessment, experimental independence claim or physical validation. Hosted CI and
final publication identities are separate in the verification/PR record.

## Material reviewed

The reviewer opened the authenticated local SI PDF, its actual S2 page/crop, the
main paper's pressure/tamp discussion and methods, and the new numerical redraw.
The reviewer independently rehashed both PDFs: SI
`37530ec8c450c6fe5b231a7d4e3b65347555454b366ed4730ec106a4fb56775f` (8 pages) and main
`efd41bb44e2542fcee04498ebc61b5c84e337601a755156e9392d12fcc93d229` (19 pages).
S2 is standalone SI PDF page 7 / printed page 6. Publisher artwork and audit
renders remain external to Git. Applicable repository instructions, the current
data/development guidance and preserved Cameron audit were consulted.

Reviewed file SHA256 identities (before any later formatting-only edits):

| File | SHA256 |
|---|---|
| `PLAN.md` | `ffb419d51adb9d21fc6aa008951fb574c51f48d07f9603b03af2dfe25bd4f2d4` |
| `SOURCE_NOTES.md` | `30fd54f8f10409c5a4565f0c2c1cfcefed3aa71c5265205cc848bb8f3dfbf080` |
| `RESULT.md` | `80192a13ff0fc073c84070d7f148fd109ea7738b56a4fed633b738991e6df9b9` |
| `contrasts.json` | `1250487c66386855cf30b19c0ba789083dc224b9aad603ba0f6fb11d2e97c5c7` |
| `COMPARISON.svg` | `d0233a628e7d95827122014e89d5479b45369014810c3d7803be907a564cef4e` |
| `puckworks/data/cameron2020/s2/observations.json` | `77c8db91db260f6d4382e86835ff4ff9add90870303522644d298522c746f01d` |
| `puckworks/analysis/cameron2020_pressure_tamp.py` | `8c5aebcd609863f80b17accfd0cd8b26476f6ebbfe4ccd8b110827a2af88e881` |
| `tools/extract_cameron_s2.py` | `2e02baa9ea8e8a2ddb3674f5ae9e4cac375886a9b67df97ca40961b135d67e0e` |

## Source checks

- Direct figure labels agree with dark/light grind 1.3/1.5 and circle/triangle
  6/9-bar assignments. An independent scan of in-frame native objects finds
  **16 filled markers and 24 vertical segments forming 12 bars**. Every marker
  bounding box, connector candidate and bar endpoint in the records matches
  its actual native path. The four missing extents are 6-bar/grind-1.3/F2 and
  9-bar/grind-1.5/F2–F4; no hidden corresponding paths were found.
- Four recurrent x clusters occur across all series. Their reading intersections
  are nonempty and groups are widely separated. F1/F4 are the same extrema for
  every series. Individual native x values and their uncertainty remain retained;
  nominal round forces and identical applied forces are not inferred.
- S2's top/bottom labels are 55/25 s, so increasing PDF y means decreasing time.
  The signed common scale and interior ticks agree with the retained mapping.
  The 0.25-pt floor plus half-stroke allowance is a declared graphical assumption,
  not empirical or statistical measurement precision.
- Triangle centroids/bounding centres are not silently substituted for connector
  anchors. Candidate disagreements, including the roughly 1.7-pt spread of the
  first dark triangle's candidate y anchors, are enclosed. Short end-dash paths
  102/104 use the end nearest the marker symmetry axis; interior dash ends are
  not data anchors. Bar midpoints and connecting-line interpolants supply no
  new observations. All eight corrected triangle centroid xy values were checked
  directly against the three native vertices.
- The crowded first light circle/triangle has recoverable encoded bar endpoints.
  Its 9-bar upper endpoint at y587.1210 pt is painted over the neighbouring light
  circle; inner bar occlusion does not justify filling the four absent extents.
  The off-plot curve artwork is correctly excluded from S2 observations.
- Main-paper PDF pages 17–18 give the recipe, 92 °C, mass tolerance, ±3-N tamper
  accuracy and general sampling statements. They do not identify S2's per-point
  n, central statistic, bar meaning or clock origin. Those fields remain
  unresolved. Native pressure labels are retained; Table S5 and Figure 5 bar
  semantics are not substituted into this analysis.

## Independent arithmetic

A separate 55-digit Decimal calculation imported neither the producer nor its
contrast functions. It constructed the eight DP, four I, four DF and two J
coefficient maps independently. For each complete row it enumerated every corner
of the original observation ranges and both uncertain calibration-tick endpoints,
converted every point using the **same** affine map, then formed the signed sum.
This checks the producer's alternative implementation that cancels the common
offset first and applies the common negative scale once.

All **36 rows** match: nominal values and unrounded interval bounds agree within
1e-12 s; all outward 0.01-s endpoints and sign dispositions agree exactly. All
coefficients sum to zero; I/J use the original four observations. Missingness
propagates to precisely nine B rows, without invalidating A. Bar endpoint padding
is included once in B; marker uncertainty is not added again.

Representative independent results (bounds rounded outward):

| Contrast | Nominal (s) | A bounds (s) | B bounds (s) |
|---|---:|---|---|
| DP-G1.3-F1 | 10.8852918244 | [10.54, 11.36] | [5.21, 16.61] |
| I-F1 | 11.9807351485 | [11.34, 12.85] | [3.44, 20.64] |
| DF-P9-G1.3 | −4.6054916337 | [−5.17, −4.20] | [−10.69, 1.45] |
| J-G1.3 | −3.6601135554 | [−4.43, −3.06] | [−12.90, 5.55] |

For example the first pressure nominal is
`(473.9888916015625 − 550.5636596679688) × (−30 / 211.041015625)` s.
The independently counted dispositions are A: 9 positive, 9 negative;
B: 4 positive, 5 unresolved, 9 incomplete. No row was omitted to obtain them.

## Claims and figure

The result correctly separates pressure ordering, additive interaction, actual
opposite signs, endpoint tamp changes and the endpoint change of pressure contrast.
A supports opposite pressure signs at all four groups and negative J at both
grinds. B supports positive I-F1 despite unresolved grind-1.5/F1 DP, and therefore
does **not** establish a reversal. Its complete tamp endpoint rows remain
unresolved; missing extents are not zero variability or force independence.
No monotonicity, constant I, population significance, practical equivalence,
pressure-drop law, permeability, choking mechanism or physical validation is claimed.

The redraw visibly distinguishes central reading rectangles from displayed
extent bars and marks absent extents with crosses. Its contrast panels show A/B
separately. The machine-readable files supply the small reading bounds that are
necessarily difficult to see at the full figure scale.

## Corrections closed in this review

1. Corrected the pressure/tamp passage locator from main PDF 11 / journal 640 to
   **PDF 12 / journal 641**; confirmed against the actual passage.
2. Removed the unsupported **VST** basket-brand attribution. The inspected methods
   specify 20-g ridge-less baskets without that brand.
3. Computed triangle centroid x from actual vertices instead of the bbox midpoint,
   and retained those vertices. The correction is 0.00015–0.00031 pt in x, far below
   the reading allowance; y, all contrast values, bounds and signs are unchanged.
   A bounded source-coordinate check confirmed the corrected records. Prose spacing
   was also improved as an editorial correction.

These corrections change no question, allowance, contrast choice or scientific
conclusion. No further scientific review round or successor study is needed for
this bounded result. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

## Closure of a hosted-CI discovery defect

The same reviewer narrowly checked the subsequent S2 discovery correction.
The general alias matcher had incorrectly treated the nominal pressure label as
a measured-pressure observable and inferred calibration from a shared source
card. The dataset-specific correction retains S2's source lineage, suppresses
those unsupported edges, and uses the existing `NO_INTERFACE_MAPPING` warning
to identify the shot-duration vocabulary limitation. The reviewer confirmed all
342 unrelated relations are unchanged, all 90 active candidate IDs/memberships
match the base, and original registry mappings remain preserved. The focused
regression passed. **Correction accepted; no outstanding defect.** No scientific
artifact changed and no broader source review or successor study was performed.
