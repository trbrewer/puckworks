# Source authentication and support audit

Foster, Lee, Moroney, Prjamkov, Salamon, Smith, Petrassem-de-Sousa and Vynnycky,
“Dynamics of liquid infiltration into an espresso bed using time-resolved
micro-computed tomography: Insights from experiment and modeling,” *Physics of
Fluids* 37, 013383 (2025), [article DOI](https://doi.org/10.1063/5.0245167).

## Actual source and rights

The actual [UL download](https://researchrepository.ul.ie/bitstreams/0e36d176-85df-4401-92e6-43ccc419c64d/download)
has 22 pages, 5,790,202 bytes, SHA-256
`a813c890e4a9ca66514896d9174d5c8d4ea9442678bc314a59b901fe0fe09d8b`.
Its cover is dated 2026-10-25 01:37:52. It differs from the reviewed
5,790,204-byte PDF (`a7a9256ea9b42ef37cc75d37eb4fd4105746feb1b6ec9e01463a25298be0daa6`).
The article title, authors, DOI, journal/page identifiers, methods and figures
were inspected independently of the wrapper. Figure 8 and Figure 9 extracted
bytes **match both reviewed native-image hashes exactly**. Therefore no changed
figure content is being authenticated merely by a matching DOI. The [Portsmouth
institutional copy](https://pure.port.ac.uk/ws/portalfiles/portal/107511955/Dynamics_of_liquid_infiltration_into_an_espresso_bed_using_time-resolved_micro-computed_tomography.pdf)
is a supplied alternate locator, not a second independently inspected source.
UL item DOI: [10.34961/researchrepository-ul.28322306](https://doi.org/10.34961/researchrepository-ul.28322306).

The article states **© 2025 Author(s), CC BY-NC 4.0**
([license](https://creativecommons.org/licenses/by-nc/4.0/)). The UL wrapper
separately states **CC BY-NC-SA 4.0**
([license](https://creativecommons.org/licenses/by-nc-sa/4.0/)). Preserve both
statements; the wrapper does not silently replace the article's notice. Native
article rasters, numerical digitizations, annotated audit crops and comparison
figure in this task are attributed source-derived material under CC BY-NC 4.0,
not relicensed under the repository's MIT software license. Changes: numerical
pixel transcription, graphical enclosures, annotation/cropping and replotting.
The full PDF, collection locators and private query receipts remain external.
No private source files, CT volumes or raw reconstruction data are redistributed.

[Extraction receipt](extraction_receipt.json) records native embedded-image
identities, dimensions, PDF pages and xrefs. Final reproducible extraction used
PyMuPDF 1.26.6 / MuPDF 1.26.11. Initial inspection also used PyMuPDF 2.0 /
MuPDF 1.28.5 and yielded the same four figure hashes. These are **raster** images,
not recovered vectors. No PNG serialization discrepancy occurred. A future
serialization mismatch must be resolved by decoded pixel/content comparison;
the extraction command fails closed on an unknown byte hash.

## Scoped available-data preflight and novelty

Inspected AGENTS/CLAUDE/onboarding, relevant ROADMAP/SPRINTS entries, minimum
necessary governance, espresso development/data guides and available-data-first
policy; MANIFEST/register/family records; active Foster card/provenance and
README; existing numerical files; completed post-saturation CONTRACT/RESULTS
and related records. The source-specific collection query was run **once**:
seven Foster files matched the existing snapshot. Their underlying files
were inspected/compared: the complete 19-row parameters and two nine-row
digitizations, plus headers and bounded rows of the two 461-row Figure 15 and
Figure 12–14 series. The query structurally parsed the complete CSV files; this
is not a claim of new semantic review of every cell.
No collection census was repeated; other external families are catalog context,
not inspected/exhausted underlying bytes. Raw CT is not in the inspected Foster
subset; this is no claim that it does not exist elsewhere.

The existing IDs `foster2025_2/params`, `/fig15_flow`, `/fig12_14_curves` retain
all bytes and roles. Figure 15 is equation-generated verification. Figure 6 is
the whole-bed fitted interface. `fig8_headspace.csv` aggregates the ten shells'
headspace estimates; it is not ten-shell s intake. Figure 12–14 uses five
vertical-line front estimates and their mean, with the center-line position
shown separately. It is not the annular observer in Figures 7–9.

GitHub Foster prior/open-task search and local prior/family records found no
completed intake equivalent to the present 90 slots. Foster post-saturation
work (#312) and I-045/I-090 are preserved, not reopened. EWP's current
`docs/analysis/sci_md_radial_obs_001/RESULT.md` was read at
`f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516`: that task concerns recoverable-solute
assay composites and retained-field diagnostics, not the Foster fitted fronts.
No EWP execution or write occurred. NEW_INFORMATION is shell-level fitted
position, displayed endpoint and finite-representation constraints that were
not previously qualified numerically.

## Observer, membership, eligibility and clock

Methods II B/C (article pp.3–4; PDF pp.5–6) state one-second reconstructions,
initial-background subtraction, slice-averaged/scaled absorption and the
three-interface sigmoid construction. Ten cylindrical shells repeat the
whole-bed analysis using whole-bed absorption scaling. Front is z3=s; positive
z points down and is scaled by bed depth. Printed Equation (1) uses z2 again
in its third exponential whereas prose calls that interface z3. This source
inconsistency is recorded, not repaired or refitted.

Figure 7 native JPEG (1013×2034) has **cropped time text**. The colored series
and their order are independently authenticated against readable Figure 6's
absorption legend and Figure 9's scan legend:

| scan (s) | color in Figures 6 absorption / 7 / 9 | fit eligibility |
|---:|---|---|
| 0 | blue | all ten source-rule zeros; blue absorption baseline <0.2 |
| 1 | orange | inner three fitted; remaining seven orange profiles below 0.2 |
| 2 | green | inner nine fitted; outer green absorption remains below 0.2 |
| 3 | red | all ten fitted |
| 4 | purple | all ten fitted |
| 5 | brown | all ten fitted |
| 6 | pink | all ten fitted |
| 7 | gray | all ten fitted |
| 8 | olive | all ten fitted |

Fit/rule decisions use Figure 7 absorption amplitude/fit lines plus methods,
not zero markers alone. The orange profile in shell 0.2<r<0.3 exceeds the
threshold, while the next shell does not. The green outermost profile stays
below it. Rule-zero values do **not** establish absent physical penetration.
Figure 7 absorption-mean SEM is not an interface-position uncertainty interval.
Methods associate w1/w3 with uncertainty/transition width, but establish neither
a confidence level nor a unique Figure 9 extent multiplier. Literal cap
coordinates are retained as `published_front_position_extents`; no symmetry or
+/-w3 reconstruction is used.

Figure 8 colors encode shells, from blue for r00 through orange, green, red,
purple, brown, pink, gray, olive to cyan for r09. Its negative branch is -H,
not s. Only three unoccluded cyan end-shell centers at t=3/4/5 are quantitatively
linked as duplicate s readings. Their local pixel nominals are 554/654/820;
the simultaneous shared-center witness uses pixels 553.63/653.29/820.13
(rounded here; exact fractions in results), all inside their +/-2 boxes.
Other primary Figure 8 positions were inspected but overlapping colors do not
supply an additional independent reading. Endpoint construction identity was
**not authenticated for transfer**, so no Figure 8 endpoints are borrowed or
equated. Three linked centers still represent three original slots, not extras.

Keep the printed 0–8 s clock. Neither exact start/end/midpoint of each one-second
reconstruction nor subsecond interface crossing is authenticated. Figure 11's
labels are relative to estimated first contact and are not substituted here;
model t_shift=0.796 s is not applied. The observed coarse/fine Figure 11 slices
and discussion were inspected qualitatively: the source declines to apply this
front extraction/model to coarse grind. There is no matched coarse radial cohort
and no causal grind comparison here. Figures 12–14 were inspected as a distinct
vertical-line observer with different uncertainty construction.

## Pixel and calibration audit

[Canonical JSON](../../../puckworks/data/foster2025_2/fig8_fig9_radial_front.json)
owns all 90 observation IDs, independent statuses, coordinates, enclosures,
reasons, eligibility evidence and duplicate records. The CSV is its flat reading
projection. Empty CSV fields correspond to JSON nulls. Rule values are separate
from unsupported pixel readings. One continuous branch was retained; no
unresolved *discrete identity* was silently collapsed. Obscured features remain
unsupported, not alternative invented coordinates.

Clear centers/caps receive +/-2 px; translucent/partially overlapping supported
features +/-4 px. Tick locations receive +/-1.5 px. These allowances encompass
the native marker/cap thickness and JPEG/antialias fringes described in PLAN;
they are a declared reading contract, not a calibrated probability statement.
The front source is not vector artwork. Pixel boxes, visible strokes and the
unmarked image remain inspectable in [overlays](overlays/).

| scan | fitted centers read | fitted lower endpoints | fitted upper endpoints | reason for missing support |
|---:|---:|---:|---:|---|
| 0 | 0 | 0 | 0 | source-rule cohort; some zero markers themselves overwritten |
| 1 | 3 | 2 | 3 | seven rule values; r00 lower cap obscured by blue disk |
| 2 | 9 | 8 | 8 | outer rule zero; r06 lower / r05 upper cap obscured |
| 3 | 10 | 9 | 10 | r04 lower cap hidden by green disk; r00 upper survives legend border |
| 4 | 10 | 10 | 10 | inner two recovered through translucent legend |
| 5 | 10 | 10 | 10 | clear brown primary profile |
| 6 | 1 | 9 | 8 | pink disks mostly occluded; r02 lower / r04,r05 upper cap unresolved |
| 7 | 9 | 6 | 7 | gray outer disk occluded; r06–r09 lower / r03,r04,r06 upper caps unresolved |
| 8 | 10 | 10 | 9 | inner olive upper-ordinate cap unresolved near gray cap |

At t=4, the actual pale purple disk and its two cap segments are visible at
x=159; x=294 lies on the legend border, with disk/cap pixels visible on its
right and through the translucent fill. These are not reads from the connecting
line or legend's sample symbol. The [paired legend crop](overlays/legend_audit.png)
keeps raw and annotated native-scale pixels adjacent. At the plateau, visible
opposing gray disk side contours support nine +/-4 center reads. Tiny pink arcs
insufficient for opposing-contour localization are deliberately left unread;
no full-disk position is reconstructed from assumed radius or neighboring lines.

Figure 9 nominal z=(p-180)/731; all six ticks are checked, and the exact shared
scale bounds are [1/734,1/728]. Figure 8 nominal z=2(p-525)/805; all five ticks
are checked. Full rational calibration polygons, shared-center feasible pixels
and nominal endpoint ordering are included in `scan_results.json`. No clipping
at z=0 or 1. Calibration vertices certify linear extrema; multiplying an outer
pixel-difference interval by the positive scale interval encloses every reading.
Offsets cancel only for operands sharing that depiction. The other depiction's
constraints can shrink the feasible set, so ignoring their tightening gives a
conservative enclosure, explicitly not a sharp correlated range.

The global nominal witness satisfies every retained calibration, pixel,
duplicate and ordering constraint. Unreadable features do not enter any complete
result. Partial constraints can be extended with unspecified latent coordinates
without creating observed values. No numerical failure or duplicate conflict
remains; missing primary/context cap and plateau support remains a source-visibility limitation.

Independent-review source correction: r04-t03's apparent lower-cap reading was
a red vertical stem below an overlying green disk, not a visible cap. It is now
null. The same audit removed five context cap readings listed in the table,
retained visible cap-end fragments under the predeclared +/-4 allowance and
corrected r02-t01 lower-cap nominal from189 to187 px. No feature is recovered
from symmetry, a line or an anticipated conclusion. Primary E/D are unchanged;
complete G3 is unsupported. The original apparent all-primary compatibility
result is explicitly withdrawn in RESULT and review history.
