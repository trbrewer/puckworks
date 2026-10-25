# Source qualification and recovery

Matias, A. F. V., Valente-Matias, D. F., Neng, N. R., Nogueira, J. M. F.,
Andrade Jr., J. S., Coelho, R. C. V., and Araújo, N. A. M. (2023),
“Continuum model for extraction and retention in porous media,” Physics of Fluids
35(12), 123611, [DOI](https://doi.org/10.1063/5.0176273).
Publisher-deposited [Crossref metadata](https://api.crossref.org/works/10.1063/5.0176273)
confirms the title, journal, volume, issue, article number and 1 December 2023
publication date. Publisher DOI/issue pages were unavailable to the web reader;
the author-institution record also agrees. Numerical source is pinned
[arXiv v2](https://arxiv.org/abs/2304.03161v2), revised 19 December 2023,
not a silently substituted journal rendering.

The [PDF](https://arxiv.org/pdf/2304.03161v2),
[source archive](https://arxiv.org/src/2304.03161v2), and member identities match
PLAN and figure_geometry.json exactly, including PDF/member byte sizes.
Archive inspection rejected absolute/traversal/link members and bounded sizes;
only selected bytes were read, no author code executed. body.tex includes
`experiment` under `graphicspath{{./img/}}`. The paper's printed page 4 Im3
stream equals the member page stream byte for byte; all 22 nested drawing-form
streams are also identical (one model curve, ten horizontal, ten vertical,
one marker form). The blue curve is excluded from the observation packet.
Native axis labels and all ten square positions agree in both rendered images.

The arXiv record's license link is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The compact geometry, derived observations and annotated source overlay credit
Matias et al. and retain that license. Changes: coordinate extraction, calibration,
annotations and replotting. This is distinct from MIT first-party analysis code.
Original PDFs/archive remain external, following repository practice; compact
literal drawing streams, exact tokens and hashes suffice for offline replay.

## Experimental contract

Section II and Figure 1 establish sequential 5 mL vials. Section III.A/Figure 3
(printed page 4) gives aggregate caffeine concentration and standard error across
four samples. Appendix A.1 (printed page 7) specifies four extractions with ten
sequential 5 mL samples each, Delta Q MilkQool Evolution long espresso program,
AromatiQ capsules and uncontrolled espresso temperature. Forty individual
concentrations were not provided in the inspected public paper/archive. The
published points are ten aggregate finite-vial means in mg/L, not instantaneous
outlet samples or cumulative cup averages. General 90 °C/9 bar/6.5 g/25–30 s
espresso context at the start of Section II does not authenticate these settings
for the four extractions. Table I/Soxhlet's one capsule (5.57943 g; 70 mg caffeine)
is separate inventory context; it supplies no common dose/normalization here.
HPLC calibration and analytical procedure are context, not graphical precision.

Repository tree/MANIFEST/capability register had no numerical Matias intake.
Existing configuration resolved the mounted external collection and historical
inventory. Matias-name metadata hits were analytical EWP references; bounded
current filename search also located a byte-identical pinned PDF. No qualified
Figure 3 numerical intake was found. Unrelated/protected observations were not
opened. The collection is neither absent nor exhausted. EWP's historical
WP_0_3B_MATIAS_VERIFICATION explicitly says NO_EXPERIMENTAL_VALIDATION and remains
unchanged, as do accepted Puckworks caffeine-predictor and Khamitova results.

## Native geometry and recovery enclosure (fixed before objective calculation)

The figure was exported through Inkscape 1.2.2 / Cairo 1.16.0, with Matplotlib
v3.5.1 author metadata. Preserve literal decimal tokens, including suppressed
zeros. The initial `1 0 0 -1 0 166.461365 cm` flips PDF y; use native x-right,
y-down figure points throughout. Forms have identity matrices. Article placement
adds scale 1.02646 and translation (54,569.06) in its bottom-up page system;
these cancel when calibrating in the original figure coordinates.

Square centers are exactly rectangle origins plus 3/2 pt, not inferred from
visible pixel edges. Each vertical segment gives its two endpoints directly;
the lower-concentration endpoint has larger y. Horizontal endpoints are retained
separately, with UNDOCUMENTED_SEMANTICS. They are not bin widths, SE, tolerances
or independent boundary errors. Nominal windows remain exactly [0,5],...,[45,50].
Actual unequal-volume robustness is NOT_ESTABLISHED.

Shared nominal calibration uses volume ticks (0,37.395), (50,227.113) and log
concentration ticks (2,113.984), (3,58.711):

- V = 50 (x_native − 37.395)/(227.113 − 37.395) mL.
- z = 2 + (113.984 − y_native)/(113.984 − 58.711), dimensionless log10(c/(1 mg/L)).

All six major volume ticks and all twenty minor logarithmic ticks are checked.
Their maximum departures from the shared nominal calibration are below 0.005 pt.
No per-point recalibration or spacing fit is used.

For G and endpoint readings, assign the SAME ±0.01 pt bound to every recovered
coordinate and each calibration-anchor coordinate. This is a declared conservative
figure-reading enclosure: it covers the observed <0.005 pt tick consistency
residual plus a uniform 0.0005 pt decimal-serialization allowance with remaining
slack. It is deliberately larger than these observed drawing discrepancies.
It is NOT half the last displayed place of each token, an HPLC error, a confidence
interval, or a guarantee about unknown pre-export experimental values. The
nominal result is exact for serialized geometry; enclosure claims are conditional
on this stated graphical contract. No optical marker half-width is used as SE.

Evaluate all eight corners of (feature coordinate, first anchor, second anchor)
for each calibrated log/volume quantity. The denominator stays positive; a
linear-fractional function attains extrema on box vertices. A common underlying
calibration is shared, but the resulting marginal bands are analyzed as a
CONSERVATIVE RECTANGULAR OUTER RELAXATION. Their favorable optimizer may not be
jointly realizable. Every admissible shared-calibration reading lies in the
rectangle, so positive relaxed optimum proves exclusion for the joint contract.

F01–F06 vertical endpoints lie within the filled/stroked marker footprints:
COVERED_BUT_RECOVERED, never absent. F07–F09 endpoints extend beyond the marker.
F10's center lies at the right spine; its marker and horizontal right end cross
the clip x=227.114. Stored horizontal right endpoint is recovered outside clipping;
vertical endpoint coordinates are retained although the stroke is clipped at the
boundary. Record all feature statuses separately. The overlay distinguishes
raw source appearance from recovered centerlines and geometry outside the clip.

Concentrations are approximate display conversions from authoritative rational
log values; do not round mg/L and reconstruct logs. 1 mg/L = 0.001 kg/m³,
1 mL = 10^-6 m³, but no SI runtime contract is added here.
