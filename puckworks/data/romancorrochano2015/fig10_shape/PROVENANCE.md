# Figure 10 mean-marker intake

Source: B. Roman Corrochano et al., *Journal of Food Engineering* 150 (2015),
106–116, [doi:10.1016/j.jfoodeng.2014.11.006](https://doi.org/10.1016/j.jfoodeng.2014.11.006),
**CC BY 3.0**. This transcription and its annotated source overlay are adaptations;
no endorsement is implied. Python analysis is Puckworks-authored software.

The configured local collection was mounted; the PDF bytes, native images and
methods were inspected, not merely catalog metadata. The file is
`pdf/06_other_papers/06_other_papers/20260717/Corrochano_et_al_New_methodology_estimate_Journal_Food_Engineering_2015.pdf`
relative to the configured collection root. `contract.json` binds the PDF and image
SHA256 identities, page and XObject. This copy has **12 PDF pages**, including a
cover; Figure 10 is PDF9/printed113. The 1839×1525 grayscale JPEG is the figure's
native raster; there are no vector marker coordinates to recover. `pdfimages`
and PyMuPDF extraction return the same image hash. No rendered-page rescaling
is used for coordinates. Raw PDFs/native image stay outside Git.

`coordinates.csv` records independently read glyph centres and visible SD caps,
in original pixels (origin top left). Circle/square centres and the centre of the
horizontal error bar through triangles/stars identify the marker anchor. Where
caps are hidden in a glyph or fitted line, the SD is **unresolved**, not zero.
Thin bars/lines are not extra mean observations. No published fitted-line pixels
enter any fit. `DIGITIZED.csv` applies the calibration in SI and keeps all pixel
provenance; asymmetric recovered SD endpoints are retained without forcing symmetry.
A mean-reading guard is ±3 px; the low, overlapping C/D glyphs in panels a/b use
±5 px. Each recoverable SD cap has a separate ±3 px reading guard. Guards enclose
centre/cap reading ambiguity, not the entire glyph, experimental spread or meter
error. Axes use stroke centres with ±1 px shared anchor guards; interior 0.2×10⁻⁵
m³/s and 0.5×10⁵ Pa ticks agree at this resolution. The overlay was inspected
against every series before model evaluation, correcting transcription positions.

There are **108 retained means**: 9 each except C-360/D-360 (10 each) and A-480
(7). The methods describe nine tank steps; the two extra visible markers and the
missing low A-480 markers have no authenticated tank-step mapping. Point IDs order
visible Q positions only. No missing step, individual bed, cross-step covariance
or 10 Hz raw sample is reconstructed. The series each summarize three independent
beds; pressure steps are not independent beds.

Before evaluation, reading sensitivity was specified as 4096 scrambled Sobol
realizations (seed 20261104), uniform within the declared pixel enclosures. Four
axis anchors move **jointly for all four series of each panel**. Each mean's x/y
reading also moves within its guard. Calibration is shared, not independently
redrawn for each model/series. Unknown physical pressure–flow covariance from the
Q-dependent correction is not represented by independent pixel offsets. The
reported 2.5–97.5 percentile intervals describe this explicit graphical perturbation
measure, **not population confidence intervals**, complete enclosure extrema,
experimental SD or an instrument uncertainty budget. Sampled extrema are retained
separately. No beds/steps are bootstrapped. SD bars are plotted but never used as
weights or mixed into graphical perturbations.

Every realization refits all five models on identical retained points. Each FA
and L0 series has its own amplitude. The reporting normalizers S² come only from
the central Q readings and stay fixed. Pooled D and m−m_FA are computed **within**
each realization. Both the data power exponent and frozen-FA reference use the
same unweighted squared-Q objective with profiled amplitude and m≥0. The reference
is grid-specific, not an intrinsic exponent; 1 and m_FA are references, not bands.

Search details: amplitudes are positive analytic least-squares projections. L1
uses exact active-set affine solutions, every knot and its constant-function limit
(P0→−∞); negative P0 is allowed. L2 and FA-S use a deterministic profiled scalar
grid, refining every local bracket. Nonnegative exponents/inverse pressure scales
include zero and their infinite limits. The upper computational point expands to
40 log units of separation from the limiting single-support shape; it is a
numerical representation of an unbounded domain, not a new parameter restriction.
The central and realization results retain boundary status and competing local
minimum counts. No fit or residual threshold decides a physical claim.

Reproduction: `python -m puckworks.analysis.cor15_shape_001` regenerates tables,
reading realizations and the comparison figure from these committed inputs.
No source PDF is needed to repeat the calculation. To inspect the reading,
`python tools/cor15_shape_overlay.py --source-pdf PATH --output PATH` verifies the
hashes and regenerates the annotated native-image overlay.
