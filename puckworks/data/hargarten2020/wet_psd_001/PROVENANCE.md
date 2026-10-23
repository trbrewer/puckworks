# Retained Hargarten graphical readings

Hargarten, Kuhn & Briesen, *Swelling properties of roasted coffee particles*,
J Sci Food Agric **100(10)** (2020), 3960–3970, DOI
[10.1002/jsfa.10440](https://doi.org/10.1002/jsfa.10440).
Source copyright 2020 The Authors, published by Wiley for SCI, CC BY-NC.
Source-derived readings keep that provenance/rights posture; source artwork is
external, not redistributed or relicensed under the repository software license.
The old card/manifest issue-number `(11)` is a bibliographic error; the article
and publisher identify issue 10. Accepted scalar CSVs remain unchanged.

Acquisition on 2026-10-23: publisher HTML and PDF text accessible through web
reader, but direct byte request 403. TUM's published article copy downloaded from
<https://mediatum.ub.tum.de/doc/1580140/document.pdf>; exact identity in contract.
The PDF contains raster, not vector, figure artwork. PyMuPDF extracted xref 62
(Figure2, 1008x647), xref73 (Figure3, 1006x1419), xref72 (Figure5, 1010x1433).
The embedded-image hashes and original pixel calibrations are in contract.json.
These are graphical coordinates, never underlying raw instrument records.

The figure marker convention is white dry, gray wet25 (Figure2 only), black wet90;
triangles cumulative Q3 on the right, circles density q3 on the left. Figure3b
left-to-right S/M/L pairs; Figure5b only S/M pairs. Its caption's L is not
supported by the artwork, p3964 prose or Figure6. No light L is constructed.
Only b panels are read for prepared fractions. The source calls points interval
midpoints and states that intervals differ between measuring ranges. No bin edges
are inferred from midpoint spacing. No density integration is performed.

coordinates.csv retains selected identifiable CDF markers spanning the requested
support and the identifiable cumulative CI endpoints. Coordinates were read against
the original raster and enlarged crops; a ±3 pixel point/endpoint allowance covers
centre/stroke reading. Blank endpoints denote missing or visually inseparable
intervals, including marker-covered intervals; no zero-width CI is assumed.
At the upper axis several markers overlap, so the common top location is retained
as a graphical centre with its full allowance, not an exact F=1 constraint.
No first/last values are forced to 0/1. Axis uncertainty is shared within panels.

The file is a bounded marker intake, not a transcription of every plotted point.
All requested cutoffs/quantiles remain in outputs. Between retained anchors only
monotonicity is used; the denser connecting lines supply no extra measurements.
Results apply to nondecreasing representations on the displayed midpoint coordinate,
not exact physical fractions below each diameter. A valid graphical result does
not resolve that observation mapping or prove binning commutes with dilation.

Original methods and Table1 were read on p3962–3963. Source sample-count ranges
and repeated scans are provenance, not reconstructed replicates: three dry samples
per fraction; four/five wet samples per sieved fraction; three/five samples from
three ground batches for non-sieved. The source's t-based 95% intervals have no
authenticated simultaneous coverage. Microscopy and fine F intake are excluded.
Figures4/6 and scalar anchors are descriptive checks only; their outlier exclusions
are not inherited (q=.99 stays). No headline swelling spread is an interval input.

The source protocol, including cooling, dry-air dispersion, wet ultrasound for
non-sieved material, and washed/no-ultrasound retained coarse fractions, is recorded
in contract.json. These are selected preparations, not matched particle trajectories.
