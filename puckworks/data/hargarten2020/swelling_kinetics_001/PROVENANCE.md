# Individual-particle graphical readings

Hargarten, Kuhn & Briesen, *Swelling properties of roasted coffee particles*,
J Sci Food Agric100(10),3960–3970 (2020), DOI
[10.1002/jsfa.10440](https://doi.org/10.1002/jsfa.10440).
Copyright2020 The Authors; CC BY-NC. Retained source-derived coordinates and plots
retain that attribution/rights posture; they are not relicensed MIT. No original
artwork is included. Numerical software is repository-authored.

The existing authenticated published article was inspected directly, without
substituting the dissertation. SHA256:
`4a41545954e6748a33ec1d956fd690bea58aba9c2e38955dfbb3ae9f5bffbfb0`.
TUM locator: https://mediatum.ub.tum.de/doc/1580140/document.pdf.
The attempted web-reader refresh returned429; the previously held bytes hash
exactly to the predecessor authentication. Original methods, Eq. 2/Eq. 4, captions,
Table 2 and original embedded rasters were read. Figure 7:xref96,PDFpage7,
printed3966; Figure 10:xref193,PDFpage9,printed3968. Artwork hashes and native
resolution are in contract.json. Independent review reopened these same images.

`coordinates.csv` is a **partial marker/cluster intake**, not original microscopy
measurements. It records all detected isolated components and unresolved connected
clusters, plus manually read frame-edge markers and dry-origin provenance. No
numerical coordinate is inferred inside an occluded cluster. A cluster can contain
multiple particles and cannot be counted as one or several measured observations.
Shape and interior gray establish identity only when distinguishable; the caption
assigns circles to80°C, triangles to25°C and increasing fill darkness to the
ordered diameters in traces.json. Two partly overlapping traces are not silently
merged. Initial proposed edge assignments and their review corrections are saved
in source_corrections.json. IDs remain stable across corrections; the diameter
in an old edge-ID token is not authoritative—use trace_id/diameter_um fields.

Coordinates are original-image pixels, top-left origin. For each linear panel,
`t=(x-x0)*tmax/(x1-x0)` and `p=(y-y0)*ymax/(y1-y0)/100`.
Both axes have separate panel calibrations. Figure 7 ticks are200s and5 diameter
percentage points; Figure 10 ticks are50s and50 progress percentage points.
Half-pixel bounding-box centers are retained exactly. Numerical output ordinates
are fractions; percent/percentage-point fields are explicitly labelled.
The fixed layer uses nominal common axes and±3 px marker-center bounds. The outer
layer encloses all±1 px shared axis-anchor changes plus±3 px marker-center changes.
Those outer marginal extremes generally do not coexist under one calibration.
They are not experimental uncertainty or probabilistic error bars.

Figure 10 is the primary normalized graphical representation. The source methods
say the first analyzed frame is10s, followed by20,30,40,50,60,90,120s and later
specified intervals. Some actual markers map to6.9–8.0s, and medium hot later
markers map to101/135/195/255s. No explanation for those discrepancies was found.
These are **graphical coordinates**, not proof of measurements before10s. Nothing
is snapped to the methods grid. Early graphical time uncertainty and rounded
diameter±0.5 µm are analyzed only as a necessary outer relaxation. There is no
source-authenticated timing error or true-radius error distribution.

Figure 7 extends1200s; Figure 10 only 300 s. Both use the same17 particles. Fig7 medium
hot circles end near 1154 s; light hot circles near1196s are partly clipped/overlapped
at the frame. Neither is silently declared an independently authenticated1200s
reference. Supported room-temperature frame markers at1200 can conditionally
supply graphical growth denominators for the separate Fig7 conversion file.
A reference divided by itself is exactly1, with correlated errors; other converted
intervals share the same uncertain reference. They are never independent residuals.

The same-frame transformation check exposes large Fig7/Fig10 discrepancies,
including medium543 µm near 120 s: Fig7≈4.54% versus final≈5.02% gives≈90%, whereas
Fig10≈139%. Even outer graphical allowances do not reconcile them. Full source
histories are unresolved. Do not average the figures or claim17+17 particles.
No negative marker was authenticated; observed decreases and>100% values are kept.
Negative retention is tested synthetically rather than manufactured in source data.

Microscopy used glued coarse particles400–1000µm, binary projected area and
area-equivalent circular diameter. It does not authenticate spherical3D radii.
Flow-cell hot water was measured at approximately 80 °C; a preheated reservoir
cooled to about60°C. The90→60°C protocol describes the separate diffraction
preparation. Constant t/R² under hot conditions is a conditional approximation;
a conflict cannot reject temperature-dependent diffusion. Room 25 °C is the cleaner
approximate constant-temperature comparison. No temperature trajectory was fitted.

The source documents bubbles obscuring boundaries, image-processing subtraction,
loosening fragments and noisy20-minute reference growth. It supplies no quantitative
segmentation-error law, imaging-plane-error distribution or joint measurement-error
bound. Table 2 calls its 8 entries averages but does not resolve the weighting and
trace-specific graphical clocks. Its accepted CSV stays separate and unchanged.
No full-espresso, pressure, fines or pore-scale-diffusivity inference follows.
Statistical nonsignificance of a size regression is not proof of no kinetic effect.
The prior wet-PSD uniform-dilation exclusion does not exclude native size-dependentMo.

`holdings_checked.json` records one bounded query of the configured inventory for
Hargarten/microscopy/swelling filenames and Hargarten family. The two matching
CSV files were reopened and rehashed: scalar anchors and Table 2 aggregates only.
No original per-particle microscopy file was authenticated **in those checked
holdings**. Other originals may exist elsewhere; this is not an exhaustion claim.
